"""
导入任务 - WordPress导入异步任务
调用真实的 WooCommerceImporter 执行产品导入
"""
import asyncio
from datetime import datetime
from typing import List, Dict
from app.tasks import celery_app
from app.core.database import SessionLocal
from app.models.task import Task, TaskLog
from app.models.product import Product
from app.models.site import Site
from app.core.logging import get_logger
from app.services.wordpress_service import (
    WooCommerceImporter,
    WPConfig,
    ImportResult,
    ImportStatus,
    create_woocommerce_importer,
)

logger = get_logger(__name__)


class _TaskCancelled(Exception):
    """任务被取消异常"""
    pass


@celery_app.task(bind=True, name="import_to_wordpress")
def import_to_wordpress_task(self, task_id: int, params: dict):
    """导入到WordPress任务

    Args:
        task_id: 任务ID
        params: 任务参数
            - site_id: 站点ID
            - product_ids: 产品ID列表
            - import_method: 导入方式
            - update_if_exists: 已存在时是否更新
            - skip_images: 是否跳过图片
            - publish: 是否发布
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

        _add_log(db, task_id, "info", "开始WordPress导入任务", params)

        # 获取参数
        site_id = params.get("site_id")
        product_ids = params.get("product_ids", [])
        import_method = params.get("import_method", "rest_api")
        update_if_exists = params.get("update_if_exists", True)
        skip_images = params.get("skip_images", False)
        publish = params.get("publish", True)

        logger.info(f"开始导入: site_id={site_id}, 产品数={len(product_ids) if product_ids else 'all'}")

        # 步骤1: 获取站点配置
        _update_progress(db, task, 5, "正在检查WordPress连接...")
        _add_log(db, task_id, "info", "检查WordPress连接", {"site_id": site_id})

        site = None
        if site_id:
            site = db.query(Site).filter(Site.id == site_id).first()

        if not site:
            raise ValueError(f"站点不存在: {site_id}")

        # 步骤2: 创建导入器并检查连接
        _update_progress(db, task, 10, "正在配置导入方式...")
        _add_log(db, task_id, "info", "配置导入方式", {
            "method": import_method,
            "update_if_exists": update_if_exists,
            "skip_images": skip_images,
            "publish": publish,
        })

        importer = create_woocommerce_importer(
            url=site.wp_url,
            username=site.wp_username,
            app_password=site.wp_password,
            wc_consumer_key=site.wc_consumer_key,
            wc_consumer_secret=site.wc_consumer_secret,
        )

        # 检查连接（异步方法）
        connected = asyncio.run(importer.check_connection())
        if not connected:
            raise ConnectionError("无法连接到WordPress站点")

        # 步骤3: 准备产品数据
        _update_progress(db, task, 15, "正在准备产品数据...")
        _add_log(db, task_id, "info", "准备产品数据", {})

        # 查询需要导入的产品
        query = db.query(Product).filter(Product.is_deleted == False)
        if product_ids:
            query = query.filter(Product.id.in_(product_ids))
        elif site_id:
            query = query.filter(Product.site_id == site_id)

        products = query.all()
        total_products = len(products)

        if total_products == 0:
            _update_progress(db, task, 100, "无产品需要导入")
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            task.result = {
                "imported_products": 0,
                "failed_products": 0,
                "skipped_products": 0,
                "import_method": import_method,
                "update_if_exists": update_if_exists,
                "publish": publish,
                "success_rate": 0,
            }
            db.commit()
            return {
                "status": "completed",
                "imported_products": 0,
                "failed_products": 0,
                "task_id": task_id,
            }

        # 转换为导入所需的字典格式
        products_data = [_product_to_dict(p, publish) for p in products]

        task.total_items = total_products
        db.commit()

        # 步骤4: 执行批量导入
        _update_progress(db, task, 25, "开始导入产品...")
        _add_log(db, task_id, "info", "开始批量导入", {"total": total_products})

        # 进度回调
        def progress_callback(current, total):
            # 检查任务是否被取消
            current_task = db.query(Task).filter(Task.id == task_id).first()
            if current_task and current_task.status == "cancelled":
                raise _TaskCancelled()
            if task:
                progress = 25 + int(current / max(total, 1) * 65)
                task.progress = progress
                task.processed_items = current
                db.commit()

        # 调用真实导入服务（异步方法）
        import_result = asyncio.run(importer.import_products_batch(
            products=products_data,
            update_if_exists=update_if_exists,
            skip_images=skip_images,
            progress_callback=progress_callback,
        ))

        imported_count = import_result.imported
        failed_count = import_result.failed
        skipped_count = import_result.skipped

        # 步骤5: 更新产品的 wp_post_id
        _update_progress(db, task, 92, "正在更新产品状态...")
        _add_log(db, task_id, "info", "更新产品状态", {
            "imported": imported_count,
            "failed": failed_count,
        })

        for i, product in enumerate(products):
            if i < len(import_result.imported_ids) and import_result.imported_ids[i]:
                product.wp_post_id = import_result.imported_ids[i]
                product.wp_status = "publish" if publish else "draft"
                product.last_synced_at = datetime.utcnow()

        db.commit()

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
            "success_rate": import_result.success_rate,
        }
        db.commit()

        _add_log(db, task_id, "success", "导入任务完成", {
            "imported": imported_count,
            "failed": failed_count,
            "success_rate": import_result.success_rate,
            "duration": (task.completed_at - task.started_at).total_seconds()
        })

        logger.info(f"导入完成: {imported_count} 个产品成功, {failed_count} 个失败")

        return {
            "status": "completed",
            "imported_products": imported_count,
            "failed_products": failed_count,
            "task_id": task_id,
        }

    except _TaskCancelled:
        logger.info(f"导入任务被取消: {task_id}")
        imported = task.processed_items if task else 0
        return {"status": "cancelled", "imported": imported}

    except Exception as e:
        logger.error(f"导入任务失败: {e}")

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


def _product_to_dict(product: Product, publish: bool = True) -> Dict:
    """将 Product 模型转换为导入所需的字典格式"""
    return {
        "name": product.name,
        "description": product.description or "",
        "short_description": product.short_description or "",
        "sku": product.sku,
        "regular_price": str(product.regular_price) if product.regular_price is not None else None,
        "sale_price": str(product.sale_price) if product.sale_price is not None else None,
        "price": str(product.price) if product.price is not None else None,
        "stock_quantity": product.stock_quantity,
        "in_stock": product.in_stock,
        "status": "publish" if publish else "draft",
        "categories": product.categories or [],
        "tags": product.tags or [],
        "images": product.images or [],
        "attributes": product.attributes or [],
        "is_variable": product.is_variable,
        "meta_data": product.meta_data or {},
    }


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
