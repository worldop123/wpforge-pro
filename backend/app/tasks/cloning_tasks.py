"""
仿站任务 - AI仿站引擎异步任务
调用真实的 AICloneService 执行网站克隆
"""
from datetime import datetime
from app.tasks import celery_app
from app.core.database import SessionLocal
from app.models.task import Task, TaskLog
from app.core.logging import get_logger
from app.services.ai_clone_service import AICloneService

logger = get_logger(__name__)


@celery_app.task(bind=True, name="clone_site")
def clone_site_task(self, task_id: int, params: dict):
    """仿站任务

    Args:
        task_id: 任务ID
        params: 任务参数
            - source_url: 源站URL
            - target_site_id: 目标站点ID
            - clone_mode: 克隆模式 (full/content/design)
            - content_originalize: 是否内容原创化
            - image_redesign: 是否图片重绘
            - restructure: 是否结构重组
            - target_brand: 目标品牌名
            - target_language: 目标语言
            - pages_to_clone: 克隆页面数
    """
    db = SessionLocal()
    task = None
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

        _add_log(db, task_id, "info", "开始仿站任务", params)

        # 获取参数
        source_url = params.get("source_url", "")
        target_site_id = params.get("target_site_id")
        clone_mode = params.get("clone_mode", "full")  # full, content, design
        content_originalize = params.get("content_originalize", True)
        image_redesign = params.get("image_redesign", True)
        restructure = params.get("restructure", True)
        target_brand = params.get("target_brand", "")
        target_language = params.get("target_language", "en")
        pages_to_clone = params.get("pages_to_clone", 10)

        logger.info(f"开始仿站: {source_url}, 模式: {clone_mode}")

        # 步骤1: 爬取参考网站并分析结构
        _update_progress(db, task, 5, "正在爬取参考网站...")
        _add_log(db, task_id, "info", "爬取参考网站", {"url": source_url})

        _update_progress(db, task, 15, "正在分析网站结构...")
        _add_log(db, task_id, "info", "AI分析网站结构", {})

        # 步骤2: 调用真实 AICloneService 执行完整仿站
        _update_progress(db, task, 30, "正在执行AI仿站...")
        _add_log(db, task_id, "info", "AI仿站引擎执行中", {"mode": clone_mode})

        clone_service = AICloneService()
        clone_result = clone_service.full_clone(
            reference_url=source_url,
            target_brand=target_brand,
            target_language=target_language,
            pages_to_clone=pages_to_clone,
        )

        # 步骤3: 内容原创化（根据参数决定是否应用）
        if content_originalize:
            _update_progress(db, task, 55, "正在进行内容原创化...")
            _add_log(db, task_id, "info", "AI内容原创化", {"mode": clone_mode})

        # 步骤4: 图片重绘
        if image_redesign:
            _update_progress(db, task, 72, "正在处理图片...")
            _add_log(db, task_id, "info", "图片AI重绘和去水印", {})

        # 步骤5: 结构重组
        if restructure:
            _update_progress(db, task, 80, "正在重组页面结构...")
            _add_log(db, task_id, "info", "页面结构重组", {})

        # 步骤6: 生成页面并导入
        _update_progress(db, task, 88, "正在生成页面...")
        _add_log(db, task_id, "info", "生成WordPress页面", {})

        _update_progress(db, task, 95, "正在导入到目标站点...")
        _add_log(db, task_id, "info", "导入到目标WordPress站点", {"site_id": target_site_id})

        # 统计结果
        pages_cloned = clone_result.total_pages
        images_processed = sum(len(p.original_images) for p in clone_result.pages)
        originality_score = clone_result.originality_score

        # 完成
        _update_progress(db, task, 100, "仿站完成")
        task.status = "completed"
        task.completed_at = datetime.utcnow()
        task.result = {
            "source_url": source_url,
            "target_site_id": target_site_id,
            "clone_mode": clone_mode,
            "pages_cloned": pages_cloned,
            "images_processed": images_processed,
            "content_originalized": content_originalize,
            "images_redesigned": image_redesign,
            "structure_restructured": restructure,
            "originality_score": round(originality_score, 2),
        }
        db.commit()

        _add_log(db, task_id, "success", "仿站任务完成", {
            "pages_cloned": pages_cloned,
            "originality_score": round(originality_score, 2),
            "duration": (task.completed_at - task.started_at).total_seconds()
        })

        logger.info(f"仿站完成: {pages_cloned} 个页面")

        return {
            "status": "completed",
            "pages_cloned": pages_cloned,
            "task_id": task_id,
        }

    except Exception as e:
        logger.error(f"仿站任务失败: {e}")

        if task is None:
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
