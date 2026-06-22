"""
API路由 - WordPress导入相关接口
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import uuid
import time

from app.core.logging import get_logger
from app.services.wordpress_service import (
    WooCommerceImporter,
    WPConfig,
    WordPressCompatibilityChecker,
    ImportStatus
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/wordpress", tags=["WordPress管理"])

# 内存中的导入任务
import_tasks: Dict[str, Dict] = {}


class WordPressSiteConfig(BaseModel):
    """WordPress站点配置"""
    url: str
    username: str
    app_password: str
    wc_consumer_key: Optional[str] = None
    wc_consumer_secret: Optional[str] = None


class ImportTaskRequest(BaseModel):
    """导入任务请求"""
    site_config: WordPressSiteConfig
    products: List[Dict]
    update_if_exists: bool = True
    skip_images: bool = False
    delay_between: float = 0.5


class ImportTaskResponse(BaseModel):
    """导入任务响应"""
    task_id: str
    status: str
    total: int
    created_at: float


class ImportProgressResponse(BaseModel):
    """导入进度响应"""
    task_id: str
    status: str
    progress: float
    total: int
    imported: int
    failed: int
    skipped: int
    errors: List[str] = Field(default_factory=list)
    imported_ids: List[int] = Field(default_factory=list)


@router.post("/sites/test")
async def test_wordpress_connection(site_config: WordPressSiteConfig):
    """测试WordPress连接"""
    try:
        config = WPConfig(
            url=site_config.url,
            username=site_config.username,
            app_password=site_config.app_password,
            wc_consumer_key=site_config.wc_consumer_key,
            wc_consumer_secret=site_config.wc_consumer_secret
        )
        
        importer = WooCommerceImporter(config)
        connected = await importer.check_connection()
        
        await importer.close()
        
        return {
            "connected": connected,
            "url": site_config.url
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"连接失败: {str(e)}")


@router.post("/sites/health-check")
async def wordpress_health_check(site_config: WordPressSiteConfig):
    """WordPress站点健康检查"""
    try:
        config = WPConfig(
            url=site_config.url,
            username=site_config.username,
            app_password=site_config.app_password,
            wc_consumer_key=site_config.wc_consumer_key,
            wc_consumer_secret=site_config.wc_consumer_secret
        )
        
        checker = WordPressCompatibilityChecker()
        health = await checker.check_site_health(config)
        
        # 检查插件冲突
        plugin_warnings = await checker.check_plugin_conflicts(config)
        health["plugin_warnings"] = plugin_warnings
        
        return health
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"检查失败: {str(e)}")


@router.post("/import/tasks", response_model=ImportTaskResponse)
async def create_import_task(
    request: ImportTaskRequest,
    background_tasks: BackgroundTasks
):
    """创建导入任务"""
    task_id = str(uuid.uuid4())
    
    # 初始化任务状态
    import_tasks[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "total": len(request.products),
        "imported": 0,
        "failed": 0,
        "skipped": 0,
        "progress": 0,
        "errors": [],
        "imported_ids": [],
        "created_at": time.time()
    }
    
    # 后台执行导入
    background_tasks.add_task(
        run_import_task,
        task_id,
        request.site_config,
        request.products,
        request.update_if_exists,
        request.skip_images,
        request.delay_between
    )
    
    return ImportTaskResponse(
        task_id=task_id,
        status="pending",
        total=len(request.products),
        created_at=import_tasks[task_id]["created_at"]
    )


async def run_import_task(
    task_id: str,
    site_config: WordPressSiteConfig,
    products: List[Dict],
    update_if_exists: bool,
    skip_images: bool,
    delay_between: float
):
    """执行导入任务"""
    try:
        import_tasks[task_id]["status"] = "running"
        
        config = WPConfig(
            url=site_config.url,
            username=site_config.username,
            app_password=site_config.app_password,
            wc_consumer_key=site_config.wc_consumer_key,
            wc_consumer_secret=site_config.wc_consumer_secret
        )
        
        importer = WooCommerceImporter(config)
        
        def progress_callback(current, total):
            import_tasks[task_id]["progress"] = current / total if total > 0 else 0
        
        result = await importer.import_products_batch(
            products,
            update_if_exists=update_if_exists,
            skip_images=skip_images,
            delay_between=delay_between,
            progress_callback=progress_callback
        )
        
        await importer.close()
        
        import_tasks[task_id]["status"] = result.status.value
        import_tasks[task_id]["imported"] = result.imported
        import_tasks[task_id]["failed"] = result.failed
        import_tasks[task_id]["skipped"] = result.skipped
        import_tasks[task_id]["errors"] = result.errors
        import_tasks[task_id]["imported_ids"] = result.imported_ids
        import_tasks[task_id]["progress"] = 1.0
        
        logger.info(f"Import task {task_id} completed: {result.imported}/{result.total}")
        
    except Exception as e:
        import_tasks[task_id]["status"] = "failed"
        import_tasks[task_id]["errors"].append(str(e))
        logger.error(f"Import task {task_id} failed: {e}")


@router.get("/import/tasks/{task_id}", response_model=ImportProgressResponse)
async def get_import_task(task_id: str):
    """获取导入任务状态"""
    if task_id not in import_tasks:
        raise HTTPException(status_code=404, detail="导入任务不存在")
    
    task = import_tasks[task_id]
    
    return ImportProgressResponse(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        total=task["total"],
        imported=task["imported"],
        failed=task["failed"],
        skipped=task["skipped"],
        errors=task["errors"],
        imported_ids=task["imported_ids"][:20]  # 只返回前20个
    )


@router.get("/sites/categories")
async def get_categories(site_config: WordPressSiteConfig):
    """获取产品分类"""
    try:
        config = WPConfig(
            url=site_config.url,
            username=site_config.username,
            app_password=site_config.app_password,
            wc_consumer_key=site_config.wc_consumer_key,
            wc_consumer_secret=site_config.wc_consumer_secret
        )
        
        importer = WooCommerceImporter(config)
        categories = await importer.get_categories()
        await importer.close()
        
        return {
            "total": len(categories),
            "categories": categories
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取分类失败: {str(e)}")


@router.post("/sites/categories")
async def create_category(site_config: WordPressSiteConfig, name: str, parent_id: Optional[int] = None):
    """创建产品分类"""
    try:
        config = WPConfig(
            url=site_config.url,
            username=site_config.username,
            app_password=site_config.app_password,
            wc_consumer_key=site_config.wc_consumer_key,
            wc_consumer_secret=site_config.wc_consumer_secret
        )
        
        importer = WooCommerceImporter(config)
        category_id = await importer.create_category(name, parent_id)
        await importer.close()
        
        if category_id:
            return {
                "success": True,
                "category_id": category_id,
                "name": name
            }
        else:
            raise HTTPException(status_code=400, detail="创建分类失败")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建分类失败: {str(e)}")
