"""
任务管理API - 任务队列的查询和管理
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.task import Task, TaskLog
from app.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    SuccessResponse,
)

router = APIRouter(prefix="/tasks", tags=["任务管理"])


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    site_id: Optional[int] = Query(None, description="站点ID过滤"),
    task_type: Optional[str] = Query(None, description="任务类型过滤"),
    status: Optional[str] = Query(None, description="状态过滤"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取任务列表"""
    query = db.query(Task).filter(Task.user_id == current_user.id)
    
    # 站点过滤
    if site_id:
        query = query.filter(Task.site_id == site_id)
    
    # 类型过滤
    if task_type:
        query = query.filter(Task.task_type == task_type)
    
    # 状态过滤
    if status:
        query = query.filter(Task.status == status)
    
    # 总数
    total = query.count()
    
    # 分页
    tasks = query.order_by(Task.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return TaskListResponse(
        items=[TaskResponse.model_validate(t) for t in tasks],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建任务"""
    task = Task(
        name=task_data.name,
        task_type=task_data.task_type,
        params=task_data.params,
        priority=task_data.priority,
        site_id=task_data.site_id,
        user_id=current_user.id,
        status="pending",
        progress=0,
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # 提交到Celery队列（如果配置了）
    try:
        from app.tasks import get_task_function
        task_func = get_task_function(task_data.task_type)
        if task_func:
            result = task_func.delay(task.id, task_data.params)
            task.task_id = result.id
            db.commit()
    except Exception as e:
        # 如果Celery不可用，任务保持pending状态
        pass
    
    return TaskResponse.model_validate(task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取任务详情"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    return TaskResponse.model_validate(task)


@router.get("/{task_id}/logs", response_model=SuccessResponse)
async def get_task_logs(
    task_id: int,
    limit: int = Query(100, ge=1, le=1000, description="日志数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取任务日志"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    logs = db.query(TaskLog).filter(
        TaskLog.task_id == task_id
    ).order_by(TaskLog.created_at.desc()).limit(limit).all()
    
    return SuccessResponse(
        message="获取日志成功",
        data=[
            {
                "id": log.id,
                "level": log.level,
                "message": log.message,
                "details": log.details,
                "created_at": log.created_at.isoformat()
            }
            for log in reversed(logs)
        ]
    )


@router.post("/{task_id}/cancel", response_model=SuccessResponse)
async def cancel_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """取消任务"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    if task.status in ("completed", "failed", "cancelled"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"任务状态为 {task.status}，无法取消"
        )
    
    # 尝试取消Celery任务
    if task.task_id:
        try:
            from celery.result import AsyncResult
            from app.tasks import celery_app
            result = AsyncResult(task.task_id, app=celery_app)
            result.revoke(terminate=True)
        except Exception:
            pass
    
    task.status = "cancelled"
    db.commit()
    
    return SuccessResponse(message="任务已取消")


@router.delete("/{task_id}", response_model=SuccessResponse)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除任务记录"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 如果任务正在运行，不允许删除
    if task.status == "running":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="任务正在运行中，无法删除"
        )
    
    db.delete(task)
    db.commit()
    
    return SuccessResponse(message="任务已删除")


@router.get("/stats/summary", response_model=SuccessResponse)
async def get_task_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取任务统计"""
    from sqlalchemy import func
    
    stats = db.query(
        Task.status,
        func.count(Task.id)
    ).filter(
        Task.user_id == current_user.id
    ).group_by(Task.status).all()
    
    result = {
        "total": 0,
        "pending": 0,
        "running": 0,
        "completed": 0,
        "failed": 0,
        "cancelled": 0,
    }
    
    for status, count in stats:
        result[status] = count
        result["total"] += count
    
    return SuccessResponse(
        message="获取统计成功",
        data=result
    )
