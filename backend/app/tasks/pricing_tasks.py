"""
价格计算任务
批量计算产品价格、汇率转换、智能定价
"""
import asyncio
from celery import shared_task
from typing import List, Dict, Optional
from decimal import Decimal
from datetime import datetime
from app.core.database import SessionLocal
from app.core.logging import get_logger
from app.models.task import Task, TaskLog
from app.models.product import Product
from app.models.site import Site
from app.services.price_service import (
    PriceCalculator,
    PriceOptimizer,
    ExchangeRateService,
    PriceStrategy,
)

logger = get_logger(__name__)


# ==================== 辅助函数 ====================

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


async def _calculate_product_prices(
    calculator: PriceCalculator,
    products: List[Product],
    target_currency: str,
    markup_percent: float,
    include_sale_price: bool,
):
    """异步批量计算产品价格

    返回结果列表，每项为 (product, final_price, sale_price) 或 (product, None, None) 表示跳过
    """
    results = []
    for product in products:
        try:
            # 获取原始价格
            original_price = product.regular_price
            if original_price is None:
                original_price = product.price
            if original_price is None:
                results.append((product, None, None))
                continue

            original_price = float(original_price)
            original_currency = product.currency or "USD"

            # 使用 PriceCalculator 计算价格（包含汇率转换、加价、心理定价）
            final_price = await calculator.calculate_price(
                base_price=original_price,
                base_currency=original_currency,
                target_currency=target_currency,
                strategy=PriceStrategy.PERCENTAGE_MARKUP,
                markup_percentage=markup_percent,
                psychological_pricing=True,
                round_decimals=2,
            )

            # 生成促销价
            sale_price = None
            if include_sale_price:
                sale_price = round(final_price * 0.85, 2)

            results.append((product, final_price, sale_price))
        except Exception as e:
            logger.error(f"产品 {getattr(product, 'id', '?')} 价格计算失败: {e}")
            results.append((product, "error", str(e)))
    return results


async def _ai_price_products(
    calculator: PriceCalculator,
    optimizer: PriceOptimizer,
    products: List[Product],
    pricing_strategy: str,
    competitor_urls: List[str],
):
    """异步 AI 智能定价

    返回结果列表，每项为 (product, target_price) 或 (product, "error", error_msg)
    """
    results = []
    for product in products:
        try:
            regular_price = product.regular_price
            if regular_price is None:
                regular_price = product.price
            if regular_price is None:
                results.append((product, None))
                continue

            # 假设成本是售价的60%
            cost_price = float(regular_price) * 0.6

            if pricing_strategy == "competitive":
                # 竞争导向定价：使用 PriceOptimizer.suggest_price
                # 基于成本估算竞品价格区间
                competitor_prices = [cost_price * 1.5, cost_price * 1.8, cost_price * 1.3]
                suggestion = optimizer.suggest_price(
                    cost_price=cost_price,
                    competitor_prices=competitor_prices,
                    market_demand="medium",
                )
                target_price = suggestion["suggested_price"]
            elif pricing_strategy == "value":
                # 价值导向定价：成本 * 价值倍数
                target_price = cost_price * 2.0
            else:
                # 成本加成定价：使用 PriceCalculator
                target_price = await calculator.calculate_price(
                    base_price=cost_price,
                    base_currency=product.currency or "USD",
                    target_currency=product.currency or "USD",
                    strategy=PriceStrategy.PERCENTAGE_MARKUP,
                    markup_percentage=50,
                    psychological_pricing=True,
                    round_decimals=2,
                )

            results.append((product, round(target_price, 2)))
        except Exception as e:
            logger.error(f"产品 {getattr(product, 'id', '?')} AI定价失败: {e}")
            results.append((product, "error", str(e)))
    return results


async def _fetch_exchange_rates(service: ExchangeRateService, base_currency: str = "USD"):
    """异步获取常用货币汇率并刷新缓存"""
    common_currencies = ["USD", "EUR", "GBP", "JPY", "CNY", "HKD", "AUD", "CAD"]
    rates = {}
    for target in common_currencies:
        try:
            rate = await service.get_rate(base_currency, target, use_cache=False)
            rates[target] = rate.rate
        except Exception as e:
            logger.warning(f"获取汇率 {base_currency}->{target} 失败: {e}")
    return rates


# ==================== 任务定义 ====================

@shared_task(bind=True, name="calculate_prices_task")
def calculate_prices_task(self, task_id: int, params: dict):
    """
    批量计算产品价格任务

    Args:
        task_id: 任务ID
        params: 任务参数
            - site_id: 站点ID
            - product_ids: 产品ID列表（可选，不填则处理站点所有产品）
            - target_currency: 目标货币
            - markup_percent: 加价百分比
            - include_sale_price: 是否生成促销价
            - price_ending: 价格尾数优化
    """
    db = SessionLocal()
    task = None
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            logger.error(f"Task not found: {task_id}")
            return

        # 更新任务状态
        task.status = "running"
        task.started_at = datetime.utcnow()
        task.celery_task_id = self.request.id
        db.commit()

        _add_log(db, task_id, "info", "开始价格计算任务", params)

        site_id = params.get("site_id")
        product_ids = params.get("product_ids")
        target_currency = params.get("target_currency", "USD")
        markup_percent = params.get("markup_percent", 30)
        include_sale_price = params.get("include_sale_price", True)
        price_ending = params.get("price_ending", ".99")

        # 获取站点信息
        site = None
        if site_id:
            site = db.query(Site).filter(Site.id == site_id).first()
        if site:
            target_currency = target_currency or site.currency
            markup_percent = markup_percent or site.price_markup

        # 获取产品列表
        query = db.query(Product).filter(Product.is_deleted == False)
        if site_id:
            query = query.filter(Product.site_id == site_id)
        if product_ids:
            query = query.filter(Product.id.in_(product_ids))

        products = query.all()
        total = len(products)
        task.total_items = total
        db.commit()

        logger.info(f"Starting price calculation for {total} products")

        if total == 0:
            _update_progress(db, task, 100, "无产品需要处理")
            task.status = "completed"
            task.progress = 100
            task.processed_items = 0
            task.failed_items = 0
            task.completed_at = datetime.utcnow()
            task.result = {
                "total": 0,
                "processed": 0,
                "failed": 0,
                "target_currency": target_currency,
                "markup_percent": markup_percent,
            }
            db.commit()
            return

        # 初始化价格计算器（内部包含 ExchangeRateService）
        price_calculator = PriceCalculator()

        _update_progress(db, task, 5, "正在计算产品价格...")

        # 异步批量计算价格
        results = asyncio.run(_calculate_product_prices(
            calculator=price_calculator,
            products=products,
            target_currency=target_currency,
            markup_percent=markup_percent,
            include_sale_price=include_sale_price,
        ))

        processed = 0
        failed = 0

        for i, result in enumerate(results):
            product = result[0]
            if result[1] is None:
                # 跳过无价格产品
                continue
            if result[1] == "error":
                failed += 1
                continue

            final_price = result[1]
            sale_price = result[2]

            # 更新产品价格
            product.regular_price = Decimal(str(round(final_price, 2)))
            product.price = Decimal(str(round(final_price, 2)))
            product.currency = target_currency

            if sale_price is not None:
                product.sale_price = Decimal(str(sale_price))

            processed += 1

            # 更新进度
            task.progress = int((i + 1) / total * 100)
            task.processed_items = processed
            task.failed_items = failed

            # 每100个产品提交一次
            if (i + 1) % 100 == 0:
                db.commit()
                logger.info(f"Processed {i + 1}/{total} products")

        # 最终提交
        db.commit()

        # 更新任务状态
        task.status = "completed"
        task.progress = 100
        task.processed_items = processed
        task.failed_items = failed
        task.completed_at = datetime.utcnow()
        task.result = {
            "total": total,
            "processed": processed,
            "failed": failed,
            "target_currency": target_currency,
            "markup_percent": markup_percent,
        }
        db.commit()

        _add_log(db, task_id, "success", "价格计算任务完成", task.result)

        logger.info(f"Price calculation completed: {processed} success, {failed} failed")

    except Exception as e:
        logger.error(f"Price calculation task failed: {str(e)}", exc_info=True)
        if task:
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            db.commit()
            _add_log(db, task_id, "error", "任务失败", {"error": str(e)})
    finally:
        db.close()


@shared_task(name="update_exchange_rates_task")
def update_exchange_rates_task():
    """
    更新汇率缓存任务
    定时任务，定期刷新汇率数据
    """
    try:
        logger.info("Starting exchange rate update")

        exchange_service = ExchangeRateService()
        # 清除旧缓存，强制刷新
        exchange_service.clear_cache()

        # 异步获取常用货币汇率
        rates = asyncio.run(_fetch_exchange_rates(exchange_service, "USD"))

        cache_stats = exchange_service.get_cache_stats()

        logger.info(f"Exchange rates updated: {len(rates)} rates cached")

        return {
            "success": True,
            "updated_at": datetime.utcnow().isoformat(),
            "base_currency": "USD",
            "rates_count": len(rates),
            "cache_size": cache_stats.get("size", 0),
        }

    except Exception as e:
        logger.error(f"Failed to update exchange rates: {str(e)}", exc_info=True)
        raise


@shared_task(bind=True, name="ai_pricing_task")
def ai_pricing_task(self, task_id: int, params: dict):
    """
    AI智能定价任务
    基于竞品分析和市场数据智能定价

    Args:
        task_id: 任务ID
        params: 任务参数
            - site_id: 站点ID
            - product_ids: 产品ID列表
            - competitor_urls: 竞品URL列表
            - pricing_strategy: 定价策略 (competitive/value/cost_plus)
    """
    db = SessionLocal()
    task = None
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            logger.error(f"Task not found: {task_id}")
            return

        task.status = "running"
        task.started_at = datetime.utcnow()
        task.celery_task_id = self.request.id
        db.commit()

        _add_log(db, task_id, "info", "开始AI智能定价任务", params)

        site_id = params.get("site_id")
        product_ids = params.get("product_ids", [])
        competitor_urls = params.get("competitor_urls", [])
        pricing_strategy = params.get("pricing_strategy", "competitive")

        # 获取产品
        query = db.query(Product).filter(Product.is_deleted == False)
        if site_id:
            query = query.filter(Product.site_id == site_id)
        if product_ids:
            query = query.filter(Product.id.in_(product_ids))

        products = query.all()
        total = len(products)
        task.total_items = total
        db.commit()

        logger.info(f"Starting AI pricing for {total} products, strategy: {pricing_strategy}")

        if total == 0:
            _update_progress(db, task, 100, "无产品需要定价")
            task.status = "completed"
            task.progress = 100
            task.processed_items = 0
            task.completed_at = datetime.utcnow()
            task.result = {
                "total": 0,
                "processed": 0,
                "strategy": pricing_strategy,
            }
            db.commit()
            return

        # 初始化价格计算器和优化器
        price_calculator = PriceCalculator()
        price_optimizer = PriceOptimizer()

        _update_progress(db, task, 5, "正在执行AI智能定价...")

        # 异步批量定价
        results = asyncio.run(_ai_price_products(
            calculator=price_calculator,
            optimizer=price_optimizer,
            products=products,
            pricing_strategy=pricing_strategy,
            competitor_urls=competitor_urls,
        ))

        processed = 0
        failed = 0

        for i, result in enumerate(results):
            product = result[0]
            if result[1] is None:
                # 跳过无价格产品
                continue
            if result[1] == "error":
                failed += 1
                continue

            target_price = result[1]

            # 更新产品价格
            product.regular_price = Decimal(str(round(target_price, 2)))
            product.price = Decimal(str(round(target_price, 2)))

            processed += 1

            # 更新进度
            task.progress = int((i + 1) / total * 100)
            task.processed_items = processed
            task.failed_items = failed

            if (i + 1) % 50 == 0:
                db.commit()

        db.commit()

        task.status = "completed"
        task.progress = 100
        task.processed_items = processed
        task.failed_items = failed
        task.completed_at = datetime.utcnow()
        task.result = {
            "total": total,
            "processed": processed,
            "failed": failed,
            "strategy": pricing_strategy,
        }
        db.commit()

        _add_log(db, task_id, "success", "AI智能定价任务完成", task.result)

        logger.info(f"AI pricing completed for {processed} products")

    except Exception as e:
        logger.error(f"AI pricing task failed: {str(e)}", exc_info=True)
        if task:
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            db.commit()
            _add_log(db, task_id, "error", "任务失败", {"error": str(e)})
    finally:
        db.close()
