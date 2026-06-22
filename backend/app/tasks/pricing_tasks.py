"""
价格计算任务
批量计算产品价格、汇率转换、智能定价
"""
from celery import shared_task
from typing import List, Dict, Optional
from decimal import Decimal
from app.core.database import SessionLocal
from app.core.logging import get_logger
from app.models.task import Task
from app.models.product import Product
from app.models.site import Site
from app.services.price_service import PriceEngine, ExchangeRateService

logger = get_logger(__name__)


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
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            logger.error(f"Task not found: {task_id}")
            return
        
        # 更新任务状态
        task.status = "running"
        task.started_at = db.func.now()
        db.commit()
        
        site_id = params.get("site_id")
        product_ids = params.get("product_ids")
        target_currency = params.get("target_currency", "USD")
        markup_percent = params.get("markup_percent", 30)
        include_sale_price = params.get("include_sale_price", True)
        price_ending = params.get("price_ending", ".99")
        
        # 获取站点信息
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
        
        # 初始化价格引擎
        price_engine = PriceEngine()
        exchange_service = ExchangeRateService()
        
        processed = 0
        failed = 0
        
        for i, product in enumerate(products):
            try:
                # 更新进度
                task.progress = int((i + 1) / total * 100)
                task.processed_items = i + 1
                
                # 获取原始价格
                original_price = product.regular_price or product.price
                original_currency = product.currency or "USD"
                
                if not original_price:
                    logger.warning(f"Product {product.id} has no price, skipping")
                    continue
                
                # 汇率转换
                if original_currency != target_currency:
                    converted_price = exchange_service.convert(
                        amount=float(original_price),
                        from_currency=original_currency,
                        to_currency=target_currency
                    )
                else:
                    converted_price = float(original_price)
                
                # 计算加价
                final_price = price_engine.calculate_markup(
                    base_price=converted_price,
                    markup_percent=markup_percent
                )
                
                # 价格尾数优化
                final_price = price_engine.optimize_price_ending(
                    price=final_price,
                    ending=price_ending
                )
                
                # 生成促销价
                sale_price = None
                if include_sale_price:
                    sale_price = price_engine.generate_sale_price(
                        regular_price=final_price,
                        discount_percent=15  # 默认15%折扣
                    )
                    sale_price = price_engine.optimize_price_ending(
                        price=sale_price,
                        ending=price_ending
                    )
                
                # 更新产品价格
                product.regular_price = Decimal(str(round(final_price, 2)))
                product.price = Decimal(str(round(final_price, 2)))
                product.currency = target_currency
                
                if sale_price:
                    product.sale_price = Decimal(str(round(sale_price, 2)))
                
                processed += 1
                
                # 每100个产品提交一次
                if (i + 1) % 100 == 0:
                    db.commit()
                    logger.info(f"Processed {i + 1}/{total} products")
                
            except Exception as e:
                logger.error(f"Error processing product {product.id}: {str(e)}")
                failed += 1
                continue
        
        # 最终提交
        db.commit()
        
        # 更新任务状态
        task.status = "completed"
        task.progress = 100
        task.processed_items = processed
        task.failed_items = failed
        task.completed_at = db.func.now()
        task.result = {
            "total": total,
            "processed": processed,
            "failed": failed,
            "target_currency": target_currency,
            "markup_percent": markup_percent,
        }
        db.commit()
        
        logger.info(f"Price calculation completed: {processed} success, {failed} failed")
        
    except Exception as e:
        logger.error(f"Price calculation task failed: {str(e)}", exc_info=True)
        if task:
            task.status = "failed"
            task.error_message = str(e)
            db.commit()
        raise
    finally:
        db.close()


@shared_task(name="update_exchange_rates_task")
def update_exchange_rates_task():
    """
    更新汇率缓存任务
    定时任务，定期更新汇率数据
    """
    try:
        logger.info("Starting exchange rate update")
        
        exchange_service = ExchangeRateService()
        result = exchange_service.update_rates()
        
        logger.info(f"Exchange rates updated: {result}")
        
        return {
            "success": True,
            "updated_at": result.get("updated_at"),
            "base_currency": result.get("base"),
            "rates_count": len(result.get("rates", {})),
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
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            logger.error(f"Task not found: {task_id}")
            return
        
        task.status = "running"
        task.started_at = db.func.now()
        db.commit()
        
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
        
        # 这里可以实现更复杂的AI定价逻辑
        # 包括竞品分析、需求弹性分析、价格敏感度分析等
        
        price_engine = PriceEngine()
        processed = 0
        
        for i, product in enumerate(products):
            try:
                task.progress = int((i + 1) / total * 100)
                task.processed_items = i + 1
                
                # 基于成本的定价
                cost_price = float(product.regular_price or 0) * 0.6  # 假设成本是售价的60%
                
                if pricing_strategy == "competitive":
                    # 竞争导向定价
                    target_price = price_engine.calculate_competitive_price(
                        cost_price=cost_price,
                        competitor_prices=[cost_price * 1.5],  # 模拟竞品价格
                        market_position="mid"
                    )
                elif pricing_strategy == "value":
                    # 价值导向定价
                    target_price = price_engine.calculate_value_based_price(
                        cost_price=cost_price,
                        perceived_value_multiplier=2.0
                    )
                else:
                    # 成本加成定价
                    target_price = price_engine.calculate_markup(
                        base_price=cost_price,
                        markup_percent=50
                    )
                
                # 价格尾数优化
                target_price = price_engine.optimize_price_ending(target_price, ".99")
                
                # 更新产品价格
                product.regular_price = Decimal(str(round(target_price, 2)))
                product.price = Decimal(str(round(target_price, 2)))
                
                processed += 1
                
                if (i + 1) % 50 == 0:
                    db.commit()
                
            except Exception as e:
                logger.error(f"Error pricing product {product.id}: {str(e)}")
                continue
        
        db.commit()
        
        task.status = "completed"
        task.progress = 100
        task.processed_items = processed
        task.completed_at = db.func.now()
        task.result = {
            "total": total,
            "processed": processed,
            "strategy": pricing_strategy,
        }
        db.commit()
        
        logger.info(f"AI pricing completed for {processed} products")
        
    except Exception as e:
        logger.error(f"AI pricing task failed: {str(e)}", exc_info=True)
        if task:
            task.status = "failed"
            task.error_message = str(e)
            db.commit()
        raise
    finally:
        db.close()
