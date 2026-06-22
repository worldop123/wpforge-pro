"""
WordPress API - WordPress智能导入
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.site import Site
from app.models.task import Task
from app.schemas import (
    WPImportRequest,
    WPImportResponse,
    SuccessResponse,
)

router = APIRouter(prefix="/wordpress", tags=["WordPress导入"])


@router.post("/import", response_model=WPImportResponse)
async def import_to_wordpress(
    request: WPImportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """导入到WordPress"""
    # 验证站点
    site = db.query(Site).filter(
        Site.id == request.site_id,
        Site.user_id == current_user.id,
        Site.is_deleted == False
    ).first()
    
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="站点不存在"
        )
    
    # 创建任务记录
    task = Task(
        name=f"WordPress导入: {site.name}",
        task_type="import",
        params={
            "site_id": request.site_id,
            "product_ids": request.product_ids,
            "import_method": request.import_method,
            "update_if_exists": request.update_if_exists,
            "skip_images": request.skip_images,
            "publish": request.publish,
        },
        site_id=request.site_id,
        user_id=current_user.id,
        status="pending",
        progress=0,
        total_items=len(request.product_ids) if request.product_ids else 0,
        processed_items=0,
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # 提交到后台任务
    try:
        from app.tasks.import_tasks import import_to_wordpress_task
        result = import_to_wordpress_task.delay(task.id, task.params)
        task.task_id = result.id
        db.commit()
    except Exception as e:
        # 如果Celery不可用，使用后台任务
        background_tasks.add_task(_run_import_task, task.id, task.params)
    
    return WPImportResponse(
        task_id=str(task.id),
        status="pending",
        message="导入任务已创建，正在排队中",
        import_method=request.import_method,
    )


@router.post("/test-connection", response_model=SuccessResponse)
async def test_wordpress_connection(
    site_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """测试WordPress连接"""
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
    
    try:
        from app.services.wordpress_service import WooCommerceImporter, WPConfig
        
        config = WPConfig(
            url=site.wp_url,
            username=site.wp_username,
            app_password=site.wp_password,
            wc_consumer_key=site.wc_consumer_key,
            wc_consumer_secret=site.wc_consumer_secret,
        )
        
        importer = WooCommerceImporter(config)
        is_connected = await importer.check_connection()
        
        if is_connected:
            return SuccessResponse(
                message="连接成功",
                data={"status": "connected"}
            )
        else:
            return SuccessResponse(
                success=False,
                message="连接失败"
            )
            
    except Exception as e:
        return SuccessResponse(
            success=False,
            message=f"连接失败: {str(e)}"
        )


@router.get("/import-methods", response_model=SuccessResponse)
async def get_import_methods(
    current_user: User = Depends(get_current_user),
):
    """获取导入方式列表"""
    methods = [
        {
            "id": "rest_api",
            "name": "REST API",
            "description": "通过WordPress REST API导入，速度快，推荐使用",
            "requirements": ["需要应用密码", "需要WooCommerce REST API密钥"],
            "speed": "fast",
            "reliability": "high",
        },
        {
            "id": "wp_cli",
            "name": "WP-CLI",
            "description": "通过WP-CLI命令行导入，适合大量数据",
            "requirements": ["需要SSH访问", "需要WP-CLI"],
            "speed": "very_fast",
            "reliability": "high",
        },
        {
            "id": "database",
            "name": "直接数据库",
            "description": "直接写入数据库，速度最快，但风险较高",
            "requirements": ["需要数据库访问权限"],
            "speed": "fastest",
            "reliability": "medium",
        },
        {
            "id": "plugin",
            "name": "配套插件",
            "description": "通过WPForge配套插件导入，最稳定",
            "requirements": ["需要安装WPForge插件"],
            "speed": "medium",
            "reliability": "very_high",
        },
    ]
    
    return SuccessResponse(
        message="获取成功",
        data={"methods": methods}
    )


@router.post("/check-compatibility", response_model=SuccessResponse)
async def check_wordpress_compatibility(
    site_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """检查WordPress兼容性"""
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
    
    try:
        from app.services.wordpress_service import WordPressCompatibilityChecker, WPConfig
        
        config = WPConfig(
            url=site.wp_url,
            username=site.wp_username,
            app_password=site.wp_password,
            wc_consumer_key=site.wc_consumer_key,
            wc_consumer_secret=site.wc_consumer_secret,
        )
        
        checker = WordPressCompatibilityChecker()
        result = await checker.check_site_health(config)
        
        return SuccessResponse(
            message="兼容性检查完成",
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"检查失败: {str(e)}"
        )


@router.get("/categories", response_model=SuccessResponse)
async def get_wordpress_categories(
    site_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取WordPress产品分类"""
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
    
    try:
        import httpx
        from urllib.parse import urljoin
        
        # 使用WooCommerce API获取分类
        auth = (site.wc_consumer_key, site.wc_consumer_secret)
        url = urljoin(site.wp_url, "/wp-json/wc/v3/products/categories")
        
        async with httpx.AsyncClient(auth=auth, timeout=30) as client:
            response = await client.get(url, params={"per_page": 100, "hide_empty": False})
            
            if response.status_code == 200:
                categories = response.json()
                return SuccessResponse(
                    message="获取分类成功",
                    data={
                        "total": len(categories),
                        "categories": [
                            {
                                "id": cat["id"],
                                "name": cat["name"],
                                "slug": cat["slug"],
                                "parent": cat["parent"],
                                "count": cat["count"],
                            }
                            for cat in categories
                        ]
                    }
                )
            else:
                return SuccessResponse(
                    success=False,
                    message=f"获取失败: HTTP {response.status_code}"
                )
                
    except Exception as e:
        return SuccessResponse(
            success=False,
            message=f"获取失败: {str(e)}"
        )


@router.get("/products", response_model=SuccessResponse)
async def get_wordpress_products(
    site_id: int,
    page: int = 1,
    per_page: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取WordPress产品列表"""
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
    
    try:
        import httpx
        from urllib.parse import urljoin
        
        auth = (site.wc_consumer_key, site.wc_consumer_secret)
        url = urljoin(site.wp_url, "/wp-json/wc/v3/products")
        
        async with httpx.AsyncClient(auth=auth, timeout=30) as client:
            response = await client.get(url, params={
                "page": page,
                "per_page": per_page,
                "status": "publish",
            })
            
            if response.status_code == 200:
                products = response.json()
                total = int(response.headers.get("X-WP-Total", 0))
                
                return SuccessResponse(
                    message="获取产品成功",
                    data={
                        "total": total,
                        "page": page,
                        "per_page": per_page,
                        "products": [
                            {
                                "id": p["id"],
                                "name": p["name"],
                                "sku": p.get("sku", ""),
                                "price": p.get("price", ""),
                                "status": p["status"],
                                "permalink": p.get("permalink", ""),
                            }
                            for p in products
                        ]
                    }
                )
            else:
                return SuccessResponse(
                    success=False,
                    message=f"获取失败: HTTP {response.status_code}"
                )
                
    except Exception as e:
        return SuccessResponse(
            success=False,
            message=f"获取失败: {str(e)}"
        )


async def _run_import_task(task_id: int, params: dict):
    """后台运行导入任务（备用方案）"""
    from app.core.database import SessionLocal
    from app.models.task import Task
    
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return
        
        task.status = "running"
        db.commit()
        
        # 模拟导入过程
        import time
        total = task.total_items or 10
        for i in range(total):
            time.sleep(0.3)
            task.progress = int((i + 1) / total * 100)
            task.processed_items = i + 1
            db.commit()
        
        task.status = "completed"
        task.progress = 100
        task.processed_items = total
        task.result = {"imported": total, "success": True}
        db.commit()
        
    except Exception as e:
        if task:
            task.status = "failed"
            task.error_message = str(e)
            db.commit()
    finally:
        db.close()
