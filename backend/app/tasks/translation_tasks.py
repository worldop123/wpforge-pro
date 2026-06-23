"""
翻译任务 - 产品翻译异步任务
调用真实的 TranslationService 执行产品翻译
"""
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from app.tasks import celery_app
from app.core.database import SessionLocal
from app.models.task import Task, TaskLog
from app.models.product import Product
from app.core.logging import get_logger
from app.services.translation_service import TranslationService, TranslationResult

logger = get_logger(__name__)


class _TaskCancelled(Exception):
    """任务被取消异常"""
    pass


@celery_app.task(bind=True, name="translate_products")
def translate_products_task(self, task_id: int, params: dict):
    """翻译产品任务

    Args:
        task_id: 任务ID
        params: 任务参数
            - product_ids: 产品ID列表
            - source_language: 源语言
            - target_language: 目标语言
            - engine: 翻译引擎
            - polish: 是否润色
            - fields: 要翻译的字段列表
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

        _add_log(db, task_id, "info", "开始翻译任务", params)

        # 获取参数
        product_ids = params.get("product_ids", [])
        source_language = params.get("source_language", "auto")
        target_language = params.get("target_language", "zh-CN")
        engine = params.get("engine", "ai")
        polish = params.get("polish", True)
        fields = params.get("fields", ["name", "description", "short_description"])

        logger.info(f"开始翻译: 目标语言={target_language}, 引擎={engine}")

        # 步骤1: 查询需要翻译的产品
        _update_progress(db, task, 5, "正在准备翻译...")
        _add_log(db, task_id, "info", "准备翻译任务", {
            "source_language": source_language,
            "target_language": target_language,
            "engine": engine,
            "fields": fields,
        })

        query = db.query(Product).filter(Product.is_deleted == False)
        if product_ids:
            query = query.filter(Product.id.in_(product_ids))

        products = query.all()
        total_products = len(products)

        if total_products == 0:
            _update_progress(db, task, 100, "无产品需要翻译")
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            task.result = {
                "translated_products": 0,
                "source_language": source_language,
                "target_language": target_language,
                "engine": engine,
                "polished": polish,
                "quality_score": 0.0,
            }
            db.commit()
            return {
                "status": "completed",
                "translated_products": 0,
                "task_id": task_id,
            }

        task.total_items = total_products
        db.commit()

        # 步骤2: 初始化翻译服务
        _update_progress(db, task, 10, "正在初始化翻译引擎...")
        _add_log(db, task_id, "info", "选择翻译引擎", {"engine": engine})

        translation_service = TranslationService()

        # 步骤3: 执行翻译
        _update_progress(db, task, 15, "开始翻译产品...")
        _add_log(db, task_id, "info", "开始批量翻译", {"total": total_products})

        translated_count = 0
        failed_count = 0
        quality_scores = []

        for i, product in enumerate(products):
            # 检查任务是否被取消
            if (i + 1) % 5 == 0 or i == 0:
                current_task = db.query(Task).filter(Task.id == task_id).first()
                if current_task and current_task.status == "cancelled":
                    raise _TaskCancelled()

            try:
                # 构建产品数据字典
                product_data = _product_to_translation_dict(product)

                # 调用真实翻译服务（异步方法）
                translated_data = asyncio.run(translation_service.translate_product(
                    product_data=product_data,
                    source_lang=source_language,
                    target_lang=target_language,
                    engine=engine,
                    fields=fields,
                    polish=polish,
                ))

                # 更新产品字段
                _apply_translation(product, translated_data, fields)
                product.translated = True
                product.translation_language = target_language

                translated_count += 1

                # 收集质量分数
                if hasattr(translated_data, "quality_score"):
                    quality_scores.append(translated_data.quality_score)

            except Exception as e:
                logger.error(f"产品 {product.id} 翻译失败: {e}")
                failed_count += 1

            # 更新进度
            progress = 15 + int((i + 1) / total_products * 75)
            task.progress = progress
            task.processed_items = translated_count
            task.failed_items = failed_count
            db.commit()

        # 步骤4: 保存翻译结果
        _update_progress(db, task, 95, "正在保存翻译结果...")
        _add_log(db, task_id, "info", "保存翻译结果", {"count": translated_count})

        db.commit()

        # 计算平均质量分数
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0

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
            "quality_score": round(avg_quality, 2),
        }
        db.commit()

        _add_log(db, task_id, "success", "翻译任务完成", {
            "translated_products": translated_count,
            "quality_score": round(avg_quality, 2),
            "duration": (task.completed_at - task.started_at).total_seconds()
        })

        logger.info(f"翻译完成: {translated_count} 个产品")

        return {
            "status": "completed",
            "translated_products": translated_count,
            "task_id": task_id,
        }

    except _TaskCancelled:
        logger.info(f"翻译任务被取消: {task_id}")
        translated = task.processed_items if task else 0
        return {"status": "cancelled", "translated": translated}

    except Exception as e:
        logger.error(f"翻译任务失败: {e}")

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


def _product_to_translation_dict(product: Product) -> Dict:
    """将 Product 模型转换为翻译所需的字典格式"""
    return {
        "name": product.name or "",
        "title": product.name or "",
        "description": product.description or "",
        "short_description": product.short_description or "",
        "seo_title": product.seo_title or "",
        "seo_description": product.seo_description or "",
    }


def _apply_translation(product: Product, translated_data: Dict, fields: List[str]):
    """将翻译结果应用到产品模型"""
    field_mapping = {
        "name": "name",
        "title": "name",
        "description": "description",
        "short_description": "short_description",
        "seo_title": "seo_title",
        "seo_description": "seo_description",
    }

    for field in fields:
        if field in translated_data and translated_data[field]:
            product_field = field_mapping.get(field, field)
            if hasattr(product, product_field):
                setattr(product, product_field, translated_data[field])


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
