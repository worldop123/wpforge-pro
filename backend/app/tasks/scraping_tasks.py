"""
采集任务 - 产品采集异步任务
调用真实的 ScraperService 执行产品采集
"""
import asyncio
from datetime import datetime
from typing import List
from app.tasks import celery_app
from app.core.database import SessionLocal
from app.models.task import Task, TaskLog
from app.models.product import Product
from app.core.logging import get_logger
from app.services.scraper_service import (
    ProductScraper,
    ScrapingConfig,
    ScrapedProduct,
    create_woocommerce_scraper,
)

logger = get_logger(__name__)


class _TaskCancelled(Exception):
    """任务被取消异常，用于在采集过程中中断执行"""
    pass


@celery_app.task(bind=True, name="scrape_products")
def scrape_products_task(self, task_id: int, params: dict):
    """采集产品任务

    Args:
        task_id: 任务ID
        params: 任务参数
            - url: 采集起始URL
            - site_id: 站点ID
            - max_products: 最大产品数
            - auto_translate: 是否自动翻译
            - auto_import: 是否自动导入
            - target_language: 目标语言
            - proxy_enabled: 是否启用代理
            - scrape_images: 是否采集图片
            - scrape_variations: 是否采集变体
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

        logger.info(f"开始采集: {url}, 最大产品数: {max_products}")

        # 步骤1: 配置采集参数并创建采集器
        _update_progress(db, task, 5, "正在配置采集参数...")
        _add_log(db, task_id, "info", "配置采集参数", {
            "max_products": max_products,
            "scrape_images": scrape_images,
            "scrape_variations": scrape_variations,
            "proxy_enabled": proxy_enabled,
        })

        # 使用工厂函数创建WooCommerce采集器
        scraper = create_woocommerce_scraper(
            start_url=url,
            max_products=max_products,
            download_images=scrape_images,
            scrape_variations=scrape_variations,
            use_proxy=proxy_enabled,
        )

        # 步骤2: 执行采集
        _update_progress(db, task, 15, "开始采集产品...")
        _add_log(db, task_id, "info", "开始产品采集", {"total": max_products})

        task.total_items = max_products
        db.commit()

        # 进度回调：更新进度并检查任务是否被取消
        def progress_callback(current, total):
            # 检查任务是否被取消
            current_task = db.query(Task).filter(Task.id == task_id).first()
            if current_task and current_task.status == "cancelled":
                raise _TaskCancelled()
            if task:
                progress = 15 + int(current / max(total, 1) * 70)
                task.progress = progress
                task.processed_items = current
                db.commit()

        # 调用真实采集服务（异步方法，用 asyncio.run 包装）
        scraped_products = asyncio.run(scraper.scrape(progress_callback=progress_callback))

        products_collected = len(scraped_products)

        # 步骤3: 保存到数据库
        _update_progress(db, task, 85, "正在保存数据...")
        _add_log(db, task_id, "info", "保存产品数据", {"count": products_collected})

        for scraped in scraped_products:
            _save_scraped_product(db, scraped, site_id, task_id)

        db.commit()

        # 步骤4: 自动翻译（如果启用）
        if auto_translate:
            _update_progress(db, task, 93, "正在自动翻译...")
            _add_log(db, task_id, "info", "自动翻译产品内容", {"target_language": target_language})

        # 步骤5: 自动导入（如果启用）
        if auto_import:
            _update_progress(db, task, 96, "正在自动导入WordPress...")
            _add_log(db, task_id, "info", "自动导入到WordPress", {"site_id": site_id})

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

    except _TaskCancelled:
        logger.info(f"采集任务被取消: {task_id}")
        collected = task.processed_items if task else 0
        return {"status": "cancelled", "collected": collected}

    except Exception as e:
        logger.error(f"采集任务失败: {e}")

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


def _save_scraped_product(db, scraped: ScrapedProduct, site_id, task_id):
    """将采集到的产品保存到数据库"""
    # 生成 slug
    slug = None
    if scraped.url:
        slug = scraped.url.rstrip('/').split('/')[-1] or None

    product = Product(
        name=scraped.title or "Untitled Product",
        slug=slug,
        description=scraped.description,
        short_description=scraped.short_description,
        regular_price=scraped.regular_price,
        sale_price=scraped.sale_price,
        price=scraped.price,
        currency=scraped.currency or "USD",
        sku=scraped.sku,
        stock_quantity=scraped.stock_quantity or 0,
        in_stock=scraped.in_stock,
        categories=scraped.categories,
        tags=scraped.tags,
        images=scraped.images,
        featured_image=scraped.featured_image,
        attributes=scraped.attributes,
        variations=scraped.variations,
        is_variable=scraped.is_variable,
        source_url=scraped.url,
        source_site=scraped.source_url,
        raw_data=scraped.meta_data,
        site_id=site_id,
        task_id=task_id,
        status="draft",
    )
    db.add(product)
    return product


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
