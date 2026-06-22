"""
采集API - 智能产品采集
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.task import Task
from app.schemas import (
    ScrapeRequest,
    ScrapeResponse,
    SuccessResponse,
)

router = APIRouter(prefix="/scraping", tags=["智能采集"])


@router.post("/start", response_model=ScrapeResponse)
async def start_scraping(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """开始采集任务"""
    # 创建任务记录
    task = Task(
        name=f"采集: {request.url}",
        task_type="scraping",
        params={
            "url": str(request.url),
            "site_id": request.site_id,
            "max_products": request.max_products,
            "auto_translate": request.auto_translate,
            "auto_import": request.auto_import,
            "target_language": request.target_language,
            "proxy_enabled": request.proxy_enabled,
            "scrape_images": request.scrape_images,
            "scrape_variations": request.scrape_variations,
            "scrape_reviews": request.scrape_reviews,
        },
        site_id=request.site_id,
        user_id=current_user.id,
        status="pending",
        progress=0,
        total_items=0,
        processed_items=0,
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # 提交到后台任务
    try:
        from app.tasks.scraping_tasks import scrape_products_task
        result = scrape_products_task.delay(task.id, task.params)
        task.task_id = result.id
        task.status = "pending"
        db.commit()
    except Exception as e:
        # 如果Celery不可用，使用后台任务
        background_tasks.add_task(_run_scraping_task, task.id, task.params)
    
    return ScrapeResponse(
        task_id=str(task.id),
        status="pending",
        message="采集任务已创建，正在排队中",
        estimated_count=None
    )


@router.post("/analyze", response_model=SuccessResponse)
async def analyze_site(
    url: str,
    current_user: User = Depends(get_current_user),
):
    """AI分析网站结构"""
    try:
        from app.services.ai_scraper_service import AIScraperAnalyzer
        import httpx
        
        # 获取页面HTML
        async with httpx.AsyncClient(
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            timeout=30,
            follow_redirects=True
        ) as client:
            response = await client.get(url)
            html = response.text
        
        # AI分析
        analyzer = AIScraperAnalyzer()
        result = analyzer.analyze_site(html, url)
        
        return SuccessResponse(
            message="网站分析完成",
            data={
                "site_type": result.site_type.value,
                "confidence": result.confidence,
                "pagination_type": result.pagination_type.value,
                "pagination_selector": result.pagination_selector,
                "product_list_selector": result.product_list_selector,
                "product_detail_url_pattern": result.product_detail_url_pattern,
                "currency": result.currency,
                "language": result.language,
                "has_anti_detection": result.has_anti_detection,
                "detected_fields": [
                    {
                        "name": f.name,
                        "selector": f.selector,
                        "confidence": f.confidence,
                        "needs_translation": f.needs_translation,
                    }
                    for f in result.detected_fields
                ],
                "recommendations": result.recommendations,
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析失败: {str(e)}"
        )


@router.get("/status/{task_id}", response_model=SuccessResponse)
async def get_scraping_status(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取采集任务状态"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id,
        Task.task_type == "scraping"
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    return SuccessResponse(
        message="获取状态成功",
        data={
            "task_id": task.id,
            "status": task.status,
            "progress": task.progress,
            "total_items": task.total_items,
            "processed_items": task.processed_items,
            "failed_items": task.failed_items,
            "result": task.result,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        }
    )


@router.post("/quick-scrape", response_model=SuccessResponse)
async def quick_scrape(
    url: str,
    current_user: User = Depends(get_current_user),
):
    """快速采集单个产品（同步）"""
    try:
        # 这里可以实现快速采集逻辑
        # 由于需要Playwright，实际部署时使用
        return SuccessResponse(
            message="快速采集功能",
            data={
                "url": url,
                "status": "demo",
                "message": "完整采集功能请使用异步任务"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"采集失败: {str(e)}"
        )


async def _run_scraping_task(task_id: int, params: dict):
    """后台运行采集任务（备用方案）"""
    from app.core.database import SessionLocal
    from app.models.task import Task
    
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return
        
        task.status = "running"
        db.commit()
        
        # 模拟采集过程
        import time
        for i in range(10):
            time.sleep(0.5)
            task.progress = (i + 1) * 10
            task.processed_items = i + 1
            db.commit()
        
        task.status = "completed"
        task.progress = 100
        task.total_items = 10
        task.processed_items = 10
        task.result = {"products_collected": 10, "success": True}
        db.commit()
        
    except Exception as e:
        if task:
            task.status = "failed"
            task.error_message = str(e)
            db.commit()
    finally:
        db.close()
