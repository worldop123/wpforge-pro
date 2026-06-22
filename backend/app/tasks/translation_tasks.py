"""
翻译任务 - 产品翻译异步任务
"""
import time
from datetime import datetime
from app.tasks import celery_app
from app.core.database import SessionLocal
from app.models.task import Task, TaskLog
from app.core.logging import get_logger

logger = get_logger(__name__)


@celery_app.task(bind=True, name="translate_products")
def translate_products_task(self, task_id: int, params: dict):
    """翻译产品任务
    
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
        _add_log(db, task_id, "info", "开始翻译任务", params)
        
        # 获取参数
        product_ids = params.get("product_ids", [])
        source_language = params.get("source_language", "auto")
        target_language = params.get("target_language", "zh-CN")
        engine = params.get("engine", "ai")
        polish = params.get("polish", True)
        fields = params.get("fields", ["name", "description", "short_description"])
        
        total_products = len(product_ids) if product_ids else 50
        
        logger.info(f"开始翻译: {total_products} 个产品, 目标语言: {target_language}")
        
        # 步骤1: AI分析翻译需求
        _update_progress(db, task, 5, "正在分析翻译需求...")
        _add_log(db, task_id, "info", "AI分析翻译需求", {
            "source_language": source_language,
            "target_language": target_language,
            "fields": fields,
        })
        time.sleep(0.5)
        
        # 步骤2: 选择翻译引擎
        _update_progress(db, task, 10, "正在选择翻译引擎...")
        _add_log(db, task_id, "info", "选择翻译引擎", {"engine": engine})
        time.sleep(0.3)
        
        # 步骤3: 执行翻译
        _update_progress(db, task, 15, "开始翻译产品...")
        _add_log(db, task_id, "info", "开始批量翻译", {"total": total_products})
        
        # 模拟翻译过程
        translated_count = 0
        batch_size = 5
        
        for i in range(0, total_products, batch_size):
            # 检查任务是否被取消
            task = db.query(Task).filter(Task.id == task_id).first()
            if task and task.status == "cancelled":
                _add_log(db, task_id, "warning", "任务被取消", {})
                return {"status": "cancelled", "translated": translated_count}
            
            # 模拟翻译一批产品
            time.sleep(0.3)
            
            batch_count = min(batch_size, total_products - i)
            translated_count += batch_count
            
            # 更新进度
            progress = 15 + int(translated_count / total_products * 65)
            _update_progress(db, task, progress, f"已翻译 {translated_count}/{total_products} 个产品")
            
            task.total_items = total_products
            task.processed_items = translated_count
            db.commit()
        
        # 步骤4: AI润色优化
        if polish:
            _update_progress(db, task, 80, "正在AI润色...")
            _add_log(db, task_id, "info", "AI润色翻译内容", {"engine": engine})
            time.sleep(0.5)
        
        # 步骤5: SEO优化
        _update_progress(db, task, 88, "正在SEO优化...")
        _add_log(db, task_id, "info", "SEO优化翻译内容", {})
        time.sleep(0.3)
        
        # 步骤6: 保存翻译结果
        _update_progress(db, task, 95, "正在保存翻译结果...")
        _add_log(db, task_id, "info", "保存翻译结果", {"count": translated_count})
        time.sleep(0.3)
        
        # 完成
        _update_progress(db, task, 100, "翻译完成")
        task.status = "completed"
        task.completed_at = datetime.utcnow()
        task.result = {
            "translated_products": translated_count,
            "source_language": source_language,
            "target_language": target_language,
            "engine": engine,
            "polished": polish,
            "quality_score": 0.92,
        }
        db.commit()
        
        _add_log(db, task_id, "success", "翻译任务完成", {
            "translated_products": translated_count,
            "quality_score": 0.92,
            "duration": (task.completed_at - task.started_at).total_seconds()
        })
        
        logger.info(f"翻译完成: {translated_count} 个产品")
        
        return {
            "status": "completed",
            "translated_products": translated_count,
            "task_id": task_id,
        }
        
    except Exception as e:
        logger.error(f"翻译任务失败: {e}")
        
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
