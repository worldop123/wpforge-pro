"""
站点管理API - WordPress站点的增删改查
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.site import Site
from app.schemas import (
    SiteCreate,
    SiteUpdate,
    SiteResponse,
    SiteListResponse,
    SuccessResponse,
)

router = APIRouter(prefix="/sites", tags=["站点管理"])


@router.get("", response_model=SiteListResponse)
async def list_sites(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="状态过滤"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取站点列表"""
    query = db.query(Site).filter(Site.user_id == current_user.id, Site.is_deleted == False)
    
    # 状态过滤
    if status:
        query = query.filter(Site.status == status)
    
    # 搜索
    if search:
        query = query.filter(
            Site.name.ilike(f"%{search}%") |
            Site.url.ilike(f"%{search}%")
        )
    
    # 总数
    total = query.count()
    
    # 分页
    sites = query.order_by(Site.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return SiteListResponse(
        items=[SiteResponse.model_validate(site) for site in sites],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=SiteResponse, status_code=status.HTTP_201_CREATED)
async def create_site(
    site_data: SiteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建站点"""
    # 检查URL是否已存在
    existing = db.query(Site).filter(
        Site.url == str(site_data.url),
        Site.user_id == current_user.id,
        Site.is_deleted == False
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该站点已添加"
        )
    
    site = Site(
        name=site_data.name,
        url=str(site_data.url),
        description=site_data.description,
        wp_url=str(site_data.wp_url),
        wp_username=site_data.wp_username,
        wp_password=site_data.wp_password,
        language=site_data.language,
        currency=site_data.currency,
        price_markup=site_data.price_markup,
        page_builder=site_data.page_builder,
        status="active",
        user_id=current_user.id,
    )
    
    db.add(site)
    db.commit()
    db.refresh(site)
    
    return SiteResponse.model_validate(site)


@router.get("/{site_id}", response_model=SiteResponse)
async def get_site(
    site_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取站点详情"""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.user_id == current_user.id,
        Site.is_deleted == False
    ).first()
    
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="站点不存在"
        )
    
    return SiteResponse.model_validate(site)


@router.put("/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: int,
    site_data: SiteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新站点"""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.user_id == current_user.id,
        Site.is_deleted == False
    ).first()
    
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="站点不存在"
        )
    
    # 更新字段
    update_data = site_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(site, key, value)
    
    db.commit()
    db.refresh(site)
    
    return SiteResponse.model_validate(site)


@router.delete("/{site_id}", response_model=SuccessResponse)
async def delete_site(
    site_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除站点（软删除）"""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.user_id == current_user.id,
        Site.is_deleted == False
    ).first()
    
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="站点不存在"
        )
    
    site.is_deleted = True
    site.status = "inactive"
    db.commit()
    
    return SuccessResponse(message="站点已删除")


@router.post("/{site_id}/test-connection", response_model=SuccessResponse)
async def test_site_connection(
    site_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """测试站点连接"""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.user_id == current_user.id,
        Site.is_deleted == False
    ).first()
    
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="站点不存在"
        )
    
    # 测试连接
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{site.wp_url}/wp-json/")
            if response.status_code == 200:
                return SuccessResponse(
                    message="连接成功",
                    data={"status": "connected", "wp_version": response.json().get("version")}
                )
            else:
                return SuccessResponse(
                    success=False,
                    message=f"连接失败: HTTP {response.status_code}"
                )
    except Exception as e:
        return SuccessResponse(
            success=False,
            message=f"连接失败: {str(e)}"
        )


@router.get("/{site_id}/stats", response_model=SuccessResponse)
async def get_site_stats(
    site_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取站点统计信息"""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.user_id == current_user.id,
        Site.is_deleted == False
    ).first()
    
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="站点不存在"
        )
    
    # 统计产品数量
    from app.models.product import Product
    product_count = db.query(Product).filter(
        Product.site_id == site_id,
        Product.is_deleted == False
    ).count()
    
    # 统计任务数量
    from app.models.task import Task
    task_count = db.query(Task).filter(
        Task.site_id == site_id
    ).count()
    
    return SuccessResponse(
        message="获取统计成功",
        data={
            "products": product_count,
            "tasks": task_count,
            "last_sync": site.last_sync_at.isoformat() if site.last_sync_at else None,
        }
    )
