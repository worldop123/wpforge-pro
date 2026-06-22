"""
采集任务 - 产品采集异步任务
"""
import time
from datetime import datetime
from app.tasks import celery_app
from app.core.database import SessionLocal
from app.models.task import Task, TaskLog
from app.core.logging import get_logger

logger = get_logger(__name__)


@celery_app.task(bind=True, name="scrape_products")
def scrape_products_task(self, task_id: int, params: dict):
    """采集产品任务
    
    Args:
        task_id: 任务ID
        params: 任务参数
    """
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            logger.error(f"任务不存在: {task_id}")
            return {"error": "任务不存在"}
        
        # 更新任务状态
        task.status = "running"
        task.started_at = datetime.utcnow()
        task.celery_task_id = self.request.id
        db.commit()
        
        # 记录日志
        _add_log(db, task_id, "info", "开始采集任务", params)
        
        # 获取参数
        url = params.get("url", "")
        site_id = params.get("site_id")
        max_products = params.get("max_products", 100)
        auto_translate = params.get("auto_translate", False)
        auto_import = params.get("auto_import", False)
        target_language = params.get("target_language", "zh-CN")
        proxy_enabled = params.get("proxy_enabled", False)
        scrape_images = params.get("scrape_images", True)
        scrape_variations = params.get("scrape_variations", True)
        scrape_reviews = params.get("scrape_reviews", False)
        
        logger.info(f"开始采集: {url}, 最大产品数: {max_products}")
        
        # 步骤1: AI分析网站结构
        _update_progress(db, task, 5, "正在分析网站结构...")
        _add_log(db, task_id, "info", "AI分析网站结构", {"url": url})
        
        # 模拟分析过程
        time.sleep(1)
        
        # 步骤2: 配置采集参数
        _update_progress(db, task, 10, "正在配置采集参数...")
        _add_log(db, task_id, "info", "配置采集参数", {
            "max_products": max_products,
            "scrape_images": scrape_images,
            "scrape_variations": scrape_variations,
            "proxy_enabled": proxy_enabled,
        })
        
        # 步骤3: 执行采集
        _update_progress(db, task, 15, "开始采集产品...")
        _add_log(db, task_id, "info", "开始产品采集", {"total": max_products})
        
        # 模拟采集过程
        products_collected = 0
        batch_size = 10
        
        for i in range(0, max_products, batch_size):
            # 检查任务是否被取消
            task = db.query(Task).filter(Task.id == task_id).first()
            if task and task.status == "cancelled":
                _add_log(db, task_id, "warning", "任务被取消", {})
                return {"status": "cancelled", "collected": products_collected}
            
            # 模拟采集一批产品
            time.sleep(0.5)
            
            batch_count = min(batch_size, max_products - i)
            products_collected += batch_count
            
            # 更新进度
            progress = 15 + int(products_collected / max_products * 70)
            _update_progress(db, task, progress, f"已采集 {products_collected}/{max_products} 个产品")
            
            task.total_items = max_products
            task.processed_items = products_collected
            db.commit()
        
        # 步骤4: 数据清洗和验证
        _update_progress(db, task, 85, "正在清洗数据...")
        _add_log(db, task_id, "info", "数据清洗和验证", {"collected": products_collected})
        time.sleep(0.5)
        
        # 步骤5: 保存到数据库
        _update_progress(db, task, 90, "正在保存数据...")
        _add_log(db, task_id, "info", "保存产品数据", {"count": products_collected})
        time.sleep(0.5)
        
        # 步骤6: 自动翻译（如果启用）
        if auto_translate:
            _update_progress(db, task, 93, "正在自动翻译...")
            _add_log(db, task_id, "info", "自动翻译产品内容", {"target_language": target_language})
            time.sleep(0.5)
        
        # 步骤7: 自动导入（如果启用）
        if auto_import:
            _update_progress(db, task, 96, "正在自动导入WordPress...")
            _add_log(db, task_id, "info", "自动导入到WordPress", {"site_id": site_id})
            time.sleep(0.5)
        
        # 完成
        _update_progress(db, task, 100, "采集完成")
        task.status = "completed"
        task.completed_at = datetime.utcnow()
        task.result = {
            "products_collected": products_collected,
            "url": url,
            "auto_translate": auto_translate,
            "auto_import": auto_import,
            "target_language": target_language,
        }
        db.commit()
        
        _add_log(db, task_id, "success", "采集任务完成", {
            "products_collected": products_collected,
            "duration": (task.completed_at - task.started_at).total_seconds()
        })
        
        logger.info(f"采集完成: {products_collected} 个产品")
        
        return {
            "status": "completed",
            "products_collected": products_collected,
            "task_id": task_id,
        }
        
    except Exception as e:
        logger.error(f"采集任务失败: {e}")
        
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            db.commit()
            
            _add_log(db, task_id, "error", "任务失败", {"error": str(e)})
        
        return {"status": "failed", "error": str(e)}
        
    finally:
        db.close()


def _update_progress(db, task, progress: int, message: str = ""):
    """更新任务进度"""
    if task:
        task.progress = progress
        task.status_message = message
        db.commit()


def _add_log(db, task_id: int, level: str, message: str, details: dict = None):
    """添加任务日志"""
    try:
        log = TaskLog(
            task_id=task_id,
            level=level,
            message=message,
            details=details or {},
        )
        db.add(log)
        db.commit()
    except Exception as e:
        logger.error(f"添加任务日志失败: {e}")
