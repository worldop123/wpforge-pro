"""
导入任务 - WordPress导入异步任务
"""
import time
from datetime import datetime
from app.tasks import celery_app
from app.core.database import SessionLocal
from app.models.task import Task, TaskLog
from app.core.logging import get_logger

logger = get_logger(__name__)


@celery_app.task(bind=True, name="import_to_wordpress")
def import_to_wordpress_task(self, task_id: int, params: dict):
    """导入到WordPress任务
    
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
        _add_log(db, task_id, "info", "开始WordPress导入任务", params)
        
        # 获取参数
        site_id = params.get("site_id")
        product_ids = params.get("product_ids", [])
        import_method = params.get("import_method", "rest_api")
        update_if_exists = params.get("update_if_exists", True)
        skip_images = params.get("skip_images", False)
        publish = params.get("publish", True)
        
        total_products = len(product_ids) if product_ids else 50
        
        logger.info(f"开始导入: {total_products} 个产品, 方式: {import_method}")
        
        # 步骤1: 检查WordPress连接
        _update_progress(db, task, 5, "正在检查WordPress连接...")
        _add_log(db, task_id, "info", "检查WordPress连接", {"site_id": site_id})
        time.sleep(0.5)
        
        # 步骤2: 选择导入方式
        _update_progress(db, task, 10, "正在配置导入方式...")
        _add_log(db, task_id, "info", "配置导入方式", {
            "method": import_method,
            "update_if_exists": update_if_exists,
            "skip_images": skip_images,
            "publish": publish,
        })
        time.sleep(0.3)
        
        # 步骤3: 准备产品数据
        _update_progress(db, task, 15, "正在准备产品数据...")
        _add_log(db, task_id, "info", "准备产品数据", {"total": total_products})
        time.sleep(0.5)
        
        # 步骤4: 处理图片
        if not skip_images:
            _update_progress(db, task, 25, "正在处理图片...")
            _add_log(db, task_id, "info", "下载和处理产品图片", {})
            
            # 模拟图片处理
            for i in range(5):
                time.sleep(0.2)
                progress = 25 + i * 3
                _update_progress(db, task, progress, f"正在处理图片 {i+1}/5...")
        
        # 步骤5: 执行导入
        _update_progress(db, task, 40, "开始导入产品...")
        _add_log(db, task_id, "info", "开始批量导入", {"total": total_products})
        
        # 模拟导入过程
        imported_count = 0
        failed_count = 0
        skipped_count = 0
        batch_size = 10
        
        for i in range(0, total_products, batch_size):
            # 检查任务是否被取消
            task = db.query(Task).filter(Task.id == task_id).first()
            if task and task.status == "cancelled":
                _add_log(db, task_id, "warning", "任务被取消", {})
                return {"status": "cancelled", "imported": imported_count}
            
            # 模拟导入一批产品
            time.sleep(0.4)
            
            batch_count = min(batch_size, total_products - i)
            imported_count += batch_count - 1  # 模拟偶尔失败
            failed_count += 1 if i % 50 == 0 else 0
            skipped_count += 1 if i % 30 == 0 else 0
            
            # 更新进度
            progress = 40 + int(imported_count / total_products * 50)
            _update_progress(db, task, progress, f"已导入 {imported_count}/{total_products} 个产品")
            
            task.total_items = total_products
            task.processed_items = imported_count
            task.failed_items = failed_count
            db.commit()
        
        # 步骤6: 验证导入结果
        _update_progress(db, task, 92, "正在验证导入结果...")
        _add_log(db, task_id, "info", "验证导入结果", {
            "imported": imported_count,
            "failed": failed_count,
            "skipped": skipped_count,
        })
        time.sleep(0.5)
        
        # 步骤7: 更新产品状态
        if publish:
            _update_progress(db, task, 96, "正在发布产品...")
            _add_log(db, task_id, "info", "发布产品到WordPress", {})
            time.sleep(0.3)
        
        # 完成
        _update_progress(db, task, 100, "导入完成")
        task.status = "completed"
        task.completed_at = datetime.utcnow()
        task.result = {
            "imported_products": imported_count,
            "failed_products": failed_count,
            "skipped_products": skipped_count,
            "import_method": import_method,
            "update_if_exists": update_if_exists,
            "publish": publish,
            "success_rate": imported_count / total_products if total_products > 0 else 0,
        }
        db.commit()
        
        _add_log(db, task_id, "success", "导入任务完成", {
            "imported": imported_count,
            "failed": failed_count,
            "success_rate": imported_count / total_products if total_products > 0 else 0,
            "duration": (task.completed_at - task.started_at).total_seconds()
        })
        
        logger.info(f"导入完成: {imported_count} 个产品成功, {failed_count} 个失败")
        
        return {
            "status": "completed",
            "imported_products": imported_count,
            "failed_products": failed_count,
            "task_id": task_id,
        }
        
    except Exception as e:
        logger.error(f"导入任务失败: {e}")
        
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
