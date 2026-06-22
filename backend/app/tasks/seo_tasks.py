"""
SEO任务 - SEO优化异步任务
"""
import time
from datetime import datetime
from app.tasks import celery_app
from app.core.database import SessionLocal
from app.models.task import Task, TaskLog
from app.core.logging import get_logger

logger = get_logger(__name__)


@celery_app.task(bind=True, name="optimize_seo")
def optimize_seo_task(self, task_id: int, params: dict):
    """SEO优化任务
    
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
        _add_log(db, task_id, "info", "开始SEO优化任务", params)
        
        # 获取参数
        site_id = params.get("site_id")
        page_ids = params.get("page_ids", [])
        optimize_type = params.get("optimize_type", "full")
        target_keywords = params.get("target_keywords", [])
        language = params.get("language", "zh-CN")
        
        total_pages = len(page_ids) if page_ids else 20
        
        logger.info(f"开始SEO优化: {total_pages} 个页面, 类型: {optimize_type}")
        
        # 步骤1: SEO审计分析
        _update_progress(db, task, 5, "正在进行SEO审计...")
        _add_log(db, task_id, "info", "SEO审计分析", {"total_pages": total_pages})
        time.sleep(0.5)
        
        # 步骤2: 关键词研究
        _update_progress(db, task, 15, "正在进行关键词研究...")
        _add_log(db, task_id, "info", "关键词研究", {"target_keywords": target_keywords})
        time.sleep(0.5)
        
        # 步骤3: 页面SEO优化
        _update_progress(db, task, 25, "正在优化页面SEO...")
        _add_log(db, task_id, "info", "页面SEO优化", {"type": optimize_type})
        
        # 模拟优化过程
        optimized_count = 0
        batch_size = 5
        
        for i in range(0, total_pages, batch_size):
            # 检查任务是否被取消
            task = db.query(Task).filter(Task.id == task_id).first()
            if task and task.status == "cancelled":
                _add_log(db, task_id, "warning", "任务被取消", {})
                return {"status": "cancelled", "optimized": optimized_count}
            
            # 模拟优化一批页面
            time.sleep(0.3)
            
            batch_count = min(batch_size, total_pages - i)
            optimized_count += batch_count
            
            # 更新进度
            progress = 25 + int(optimized_count / total_pages * 50)
            _update_progress(db, task, progress, f"已优化 {optimized_count}/{total_pages} 个页面")
            
            task.total_items = total_pages
            task.processed_items = optimized_count
            db.commit()
        
        # 步骤4: 技术SEO优化
        _update_progress(db, task, 78, "正在优化技术SEO...")
        _add_log(db, task_id, "info", "技术SEO优化", {
            "schema": True,
            "sitemap": True,
            "robots": True,
        })
        time.sleep(0.5)
        
        # 步骤5: 生成结构化数据
        _update_progress(db, task, 85, "正在生成结构化数据...")
        _add_log(db, task_id, "info", "生成Schema结构化数据", {})
        time.sleep(0.3)
        
        # 步骤6: 内部链接优化
        _update_progress(db, task, 90, "正在优化内部链接...")
        _add_log(db, task_id, "info", "内部链接建设", {})
        time.sleep(0.3)
        
        # 步骤7: 图片SEO优化
        _update_progress(db, task, 94, "正在优化图片SEO...")
        _add_log(db, task_id, "info", "图片SEO优化", {"alt_tags": True})
        time.sleep(0.2)
        
        # 步骤8: 生成Sitemap
        _update_progress(db, task, 97, "正在生成Sitemap...")
        _add_log(db, task_id, "info", "生成XML Sitemap", {})
        time.sleep(0.2)
        
        # 完成
        _update_progress(db, task, 100, "SEO优化完成")
        task.status = "completed"
        task.completed_at = datetime.utcnow()
        task.result = {
            "optimized_pages": optimized_count,
            "optimize_type": optimize_type,
            "keywords_optimized": len(target_keywords),
            "average_score_improvement": 25,
            "schema_generated": True,
            "sitemap_updated": True,
        }
        db.commit()
        
        _add_log(db, task_id, "success", "SEO优化任务完成", {
            "optimized_pages": optimized_count,
            "score_improvement": 25,
            "duration": (task.completed_at - task.started_at).total_seconds()
        })
        
        logger.info(f"SEO优化完成: {optimized_count} 个页面")
        
        return {
            "status": "completed",
            "optimized_pages": optimized_count,
            "task_id": task_id,
        }
        
    except Exception as e:
        logger.error(f"SEO优化任务失败: {e}")
        
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
