"""
价格计算任务测试

pricing_tasks.py 已修复为使用真实的 PriceCalculator/PriceOptimizer/ExchangeRateService，
因此测试通过 mock.patch 模拟 service 类，验证任务逻辑正确调用 service 并更新 Task 状态。
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from decimal import Decimal

from app.tasks.pricing_tasks import (
    calculate_prices_task,
    update_exchange_rates_task,
    ai_pricing_task,
)


# ==================== 辅助函数 ====================

class FakeQuery:
    """模拟 SQLAlchemy query 链式调用"""

    def __init__(self, first_result=None, all_result=None):
        self._first_result = first_result
        self._all_result = all_result or []

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        return self._first_result

    def all(self):
        return self._all_result


class _BadProduct:
    """模拟一个 regular_price 访问会抛异常的产品（避免污染 MagicMock 类）"""

    def __init__(self, pid=1):
        self.id = pid
        self.currency = "USD"
        self.is_deleted = False
        self.price = Decimal("100.00")
        self.sale_price = None
        self.site_id = 1

    @property
    def regular_price(self):
        raise ValueError("bad")


def _make_task_mock(status="pending"):
    """构造一个 mock task 对象"""
    task = MagicMock()
    task.id = 1
    task.status = status
    task.progress = 0
    task.status_message = ""
    task.total_items = 0
    task.processed_items = 0
    task.failed_items = 0
    task.result = {}
    task.error_message = None
    task.started_at = None
    task.completed_at = None
    return task


def _make_product_mock(pid=1, regular_price="100.00", currency="USD", price="100.00"):
    """构造一个 mock product 对象"""
    product = MagicMock()
    product.id = pid
    product.regular_price = Decimal(regular_price) if regular_price else None
    product.price = Decimal(price) if price else None
    product.currency = currency
    product.sale_price = None
    product.is_deleted = False
    product.site_id = 1
    return product


def _make_site_mock(currency="USD", price_markup=30):
    """构造一个 mock site 对象"""
    site = MagicMock()
    site.currency = currency
    site.price_markup = price_markup
    return site


def _make_db_mock(task=None, site=None, products=None):
    """构造一个 mock db session，支持多次 query 调用返回不同结果"""
    db = MagicMock()

    def query_side_effect(model):
        if model.__name__ == "Task" and task is not None:
            return FakeQuery(first_result=task)
        if model.__name__ == "Site" and site is not None:
            return FakeQuery(first_result=site)
        if model.__name__ == "Product":
            return FakeQuery(all_result=products or [])
        return FakeQuery()

    db.query.side_effect = query_side_effect
    db.commit = MagicMock()
    db.close = MagicMock()
    db.add = MagicMock()
    return db


# ==================== calculate_prices_task 测试 ====================

class TestCalculatePricesTask:
    """calculate_prices_task 测试"""

    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_calculate_prices_task_not_found(self, mock_session_local):
        """任务不存在时返回 None"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_session_local.return_value = mock_db

        result = calculate_prices_task.run(task_id=999, params={})

        assert result is None
        mock_db.close.assert_called_once()

    @patch("app.tasks.pricing_tasks.PriceCalculator")
    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_calculate_prices_task_success(self, mock_session_local, mock_calc_cls):
        """任务正常执行：验证真实 PriceCalculator 被调用"""
        task = _make_task_mock()
        site = _make_site_mock()
        products = [
            _make_product_mock(pid=1, regular_price="100.00", currency="USD"),
            _make_product_mock(pid=2, regular_price="50.00", currency="USD"),
        ]
        mock_db = _make_db_mock(task=task, site=site, products=products)
        mock_session_local.return_value = mock_db

        # 模拟 PriceCalculator.calculate_price 返回价格
        mock_calc = mock_calc_cls.return_value
        mock_calc.calculate_price = AsyncMock(return_value=130.0)

        result = calculate_prices_task.run(
            task_id=1,
            params={
                "site_id": 1,
                "target_currency": "USD",
                "markup_percent": 30,
                "include_sale_price": True,
                "price_ending": ".99",
            },
        )

        assert task.status == "completed"
        assert task.progress == 100
        assert task.processed_items == 2
        assert task.failed_items == 0
        assert task.result["total"] == 2
        assert task.result["processed"] == 2
        assert task.result["target_currency"] == "USD"
        mock_db.close.assert_called_once()
        # 验证真实 PriceCalculator 被调用2次
        assert mock_calc.calculate_price.call_count == 2

    @patch("app.tasks.pricing_tasks.PriceCalculator")
    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_calculate_prices_task_with_currency_conversion(self, mock_session_local, mock_calc_cls):
        """测试汇率转换流程：验证 PriceCalculator 被调用"""
        task = _make_task_mock()
        site = _make_site_mock()
        products = [
            _make_product_mock(pid=1, regular_price="100.00", currency="EUR"),
        ]
        mock_db = _make_db_mock(task=task, site=site, products=products)
        mock_session_local.return_value = mock_db

        mock_calc = mock_calc_cls.return_value
        mock_calc.calculate_price = AsyncMock(return_value=911.0)

        calculate_prices_task.run(
            task_id=1,
            params={
                "site_id": 1,
                "target_currency": "CNY",
                "markup_percent": 30,
                "include_sale_price": False,
            },
        )

        # 产品货币应被更新为目标货币
        assert products[0].currency == "CNY"
        assert task.status == "completed"
        # 验证 PriceCalculator 被调用
        mock_calc.calculate_price.assert_called_once()

    @patch("app.tasks.pricing_tasks.PriceCalculator")
    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_calculate_prices_task_no_price_product(self, mock_session_local, mock_calc_cls):
        """产品没有价格时跳过"""
        task = _make_task_mock()
        site = _make_site_mock()
        products = [
            _make_product_mock(pid=1, regular_price=None, price=None, currency="USD"),
            _make_product_mock(pid=2, regular_price="100.00", currency="USD"),
        ]
        mock_db = _make_db_mock(task=task, site=site, products=products)
        mock_session_local.return_value = mock_db

        mock_calc = mock_calc_cls.return_value
        mock_calc.calculate_price = AsyncMock(return_value=130.0)

        calculate_prices_task.run(
            task_id=1,
            params={"site_id": 1, "include_sale_price": False},
        )

        # 只处理了一个有价格的产品
        assert task.processed_items == 1
        assert task.status == "completed"
        # 只调用了一次 calculate_price（跳过无价格产品）
        assert mock_calc.calculate_price.call_count == 1

    @patch("app.tasks.pricing_tasks.PriceCalculator")
    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_calculate_prices_task_no_site(self, mock_session_local, mock_calc_cls):
        """站点不存在时仍能执行"""
        task = _make_task_mock()
        products = [
            _make_product_mock(pid=1, regular_price="100.00", currency="USD"),
        ]
        mock_db = _make_db_mock(task=task, site=None, products=products)
        mock_session_local.return_value = mock_db

        mock_calc = mock_calc_cls.return_value
        mock_calc.calculate_price = AsyncMock(return_value=130.0)

        calculate_prices_task.run(
            task_id=1,
            params={"target_currency": "USD", "include_sale_price": False},
        )

        assert task.status == "completed"
        assert task.processed_items == 1

    @patch("app.tasks.pricing_tasks.PriceCalculator")
    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_calculate_prices_task_empty_products(self, mock_session_local, mock_calc_cls):
        """没有产品时正常完成"""
        task = _make_task_mock()
        site = _make_site_mock()
        mock_db = _make_db_mock(task=task, site=site, products=[])
        mock_session_local.return_value = mock_db

        mock_calc = mock_calc_cls.return_value
        mock_calc.calculate_price = AsyncMock(return_value=130.0)

        calculate_prices_task.run(
            task_id=1,
            params={"site_id": 1, "include_sale_price": True},
        )

        assert task.status == "completed"
        assert task.total_items == 0
        assert task.processed_items == 0
        # 没有产品时不应调用 calculate_price
        mock_calc.calculate_price.assert_not_called()

    @patch("app.tasks.pricing_tasks.PriceCalculator")
    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_calculate_prices_task_product_exception(self, mock_session_local, mock_calc_cls):
        """单个产品处理异常时继续处理其他产品"""
        task = _make_task_mock()
        site = _make_site_mock()

        bad_product = _BadProduct(pid=1)
        good_product = _make_product_mock(pid=2, regular_price="100.00", currency="USD")
        mock_db = _make_db_mock(task=task, site=site, products=[bad_product, good_product])
        mock_session_local.return_value = mock_db

        mock_calc = mock_calc_cls.return_value
        mock_calc.calculate_price = AsyncMock(return_value=130.0)

        calculate_prices_task.run(
            task_id=1,
            params={"site_id": 1, "include_sale_price": False},
        )

        # 异常产品被跳过，好产品被处理
        assert task.status == "completed"
        assert task.failed_items == 1
        assert task.processed_items == 1

    @patch("app.tasks.pricing_tasks.PriceCalculator")
    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_calculate_prices_task_with_product_ids(self, mock_session_local, mock_calc_cls):
        """指定产品ID列表"""
        task = _make_task_mock()
        site = _make_site_mock()
        products = [
            _make_product_mock(pid=1, regular_price="100.00", currency="USD"),
        ]
        mock_db = _make_db_mock(task=task, site=site, products=products)
        mock_session_local.return_value = mock_db

        mock_calc = mock_calc_cls.return_value
        mock_calc.calculate_price = AsyncMock(return_value=130.0)

        calculate_prices_task.run(
            task_id=1,
            params={
                "site_id": 1,
                "product_ids": [1, 2, 3],
                "include_sale_price": True,
            },
        )

        assert task.status == "completed"


# ==================== update_exchange_rates_task 测试 ====================

class TestUpdateExchangeRatesTask:
    """update_exchange_rates_task 测试"""

    @patch("app.tasks.pricing_tasks.ExchangeRateService")
    def test_update_exchange_rates_success(self, mock_service_cls):
        """更新汇率成功：验证真实 ExchangeRateService 被调用"""
        mock_service = mock_service_cls.return_value
        # 模拟 get_rate 返回带 rate 属性的对象
        mock_rate = MagicMock()
        mock_rate.rate = 7.0
        mock_service.get_rate = AsyncMock(return_value=mock_rate)
        mock_service.clear_cache = MagicMock()
        mock_service.get_cache_stats = MagicMock(return_value={"size": 8, "ttl": 3600})

        result = update_exchange_rates_task.run()

        assert result["success"] is True
        assert result["base_currency"] == "USD"
        # _fetch_exchange_rates 遍历 8 种常用货币
        assert result["rates_count"] == 8
        assert "updated_at" in result
        # 验证真实 ExchangeRateService 被调用
        mock_service.clear_cache.assert_called_once()
        assert mock_service.get_rate.call_count == 8

    @patch("app.tasks.pricing_tasks.ExchangeRateService")
    def test_update_exchange_rates_exception(self, mock_service_cls):
        """更新汇率异常时抛出"""
        mock_service = mock_service_cls.return_value
        mock_service.clear_cache.side_effect = Exception("API error")

        with pytest.raises(Exception):
            update_exchange_rates_task.run()


# ==================== ai_pricing_task 测试 ====================

class TestAIPricingTask:
    """ai_pricing_task 测试"""

    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_ai_pricing_task_not_found(self, mock_session_local):
        """任务不存在时返回 None"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_session_local.return_value = mock_db

        result = ai_pricing_task.run(task_id=999, params={})

        assert result is None
        mock_db.close.assert_called_once()

    @patch("app.tasks.pricing_tasks.PriceOptimizer")
    @patch("app.tasks.pricing_tasks.PriceCalculator")
    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_ai_pricing_task_competitive(self, mock_session_local, mock_calc_cls, mock_opt_cls):
        """竞争导向定价策略：验证 PriceOptimizer.suggest_price 被调用"""
        task = _make_task_mock()
        products = [
            _make_product_mock(pid=1, regular_price="100.00", currency="USD"),
            _make_product_mock(pid=2, regular_price="200.00", currency="USD"),
        ]
        mock_db = _make_db_mock(task=task, site=None, products=products)
        mock_session_local.return_value = mock_db

        # 模拟 PriceOptimizer.suggest_price
        mock_opt = mock_opt_cls.return_value
        mock_opt.suggest_price = MagicMock(return_value={
            "suggested_price": 150.0,
            "min_price": 120.0,
            "max_price": 200.0,
            "strategy": "competitive_based",
        })

        # 模拟 PriceCalculator.calculate_price（competitive 策略不会调用）
        mock_calc = mock_calc_cls.return_value
        mock_calc.calculate_price = AsyncMock(return_value=150.0)

        ai_pricing_task.run(
            task_id=1,
            params={
                "site_id": 1,
                "product_ids": [1, 2],
                "competitor_urls": ["https://comp1.com", "https://comp2.com"],
                "pricing_strategy": "competitive",
            },
        )

        assert task.status == "completed"
        assert task.progress == 100
        assert task.processed_items == 2
        assert task.result["strategy"] == "competitive"
        mock_db.close.assert_called_once()
        # 验证 PriceOptimizer.suggest_price 被调用2次
        assert mock_opt.suggest_price.call_count == 2

    @patch("app.tasks.pricing_tasks.PriceOptimizer")
    @patch("app.tasks.pricing_tasks.PriceCalculator")
    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_ai_pricing_task_value_strategy(self, mock_session_local, mock_calc_cls, mock_opt_cls):
        """价值导向定价策略：不调用 service，直接成本*2.0"""
        task = _make_task_mock()
        products = [
            _make_product_mock(pid=1, regular_price="100.00", currency="USD"),
        ]
        mock_db = _make_db_mock(task=task, site=None, products=products)
        mock_session_local.return_value = mock_db

        mock_opt = mock_opt_cls.return_value
        mock_opt.suggest_price = MagicMock(return_value={"suggested_price": 150.0})
        mock_calc = mock_calc_cls.return_value
        mock_calc.calculate_price = AsyncMock(return_value=150.0)

        ai_pricing_task.run(
            task_id=1,
            params={
                "pricing_strategy": "value",
                "product_ids": [1],
            },
        )

        assert task.status == "completed"
        assert task.result["strategy"] == "value"
        # value 策略不调用 service
        mock_opt.suggest_price.assert_not_called()
        mock_calc.calculate_price.assert_not_called()

    @patch("app.tasks.pricing_tasks.PriceOptimizer")
    @patch("app.tasks.pricing_tasks.PriceCalculator")
    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_ai_pricing_task_cost_plus_strategy(self, mock_session_local, mock_calc_cls, mock_opt_cls):
        """成本加成定价策略：验证 PriceCalculator.calculate_price 被调用"""
        task = _make_task_mock()
        products = [
            _make_product_mock(pid=1, regular_price="100.00", currency="USD"),
        ]
        mock_db = _make_db_mock(task=task, site=None, products=products)
        mock_session_local.return_value = mock_db

        mock_opt = mock_opt_cls.return_value
        mock_opt.suggest_price = MagicMock(return_value={"suggested_price": 150.0})
        mock_calc = mock_calc_cls.return_value
        mock_calc.calculate_price = AsyncMock(return_value=90.0)

        ai_pricing_task.run(
            task_id=1,
            params={
                "pricing_strategy": "cost_plus",
                "product_ids": [1],
            },
        )

        assert task.status == "completed"
        assert task.result["strategy"] == "cost_plus"
        # cost_plus 策略调用 PriceCalculator
        mock_calc.calculate_price.assert_called_once()
        mock_opt.suggest_price.assert_not_called()

    @patch("app.tasks.pricing_tasks.PriceOptimizer")
    @patch("app.tasks.pricing_tasks.PriceCalculator")
    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_ai_pricing_task_empty_products(self, mock_session_local, mock_calc_cls, mock_opt_cls):
        """没有产品时正常完成"""
        task = _make_task_mock()
        mock_db = _make_db_mock(task=task, site=None, products=[])
        mock_session_local.return_value = mock_db

        mock_opt = mock_opt_cls.return_value
        mock_opt.suggest_price = MagicMock()
        mock_calc = mock_calc_cls.return_value
        mock_calc.calculate_price = AsyncMock()

        ai_pricing_task.run(
            task_id=1,
            params={"pricing_strategy": "competitive"},
        )

        assert task.status == "completed"
        assert task.total_items == 0
        mock_opt.suggest_price.assert_not_called()
        mock_calc.calculate_price.assert_not_called()

    @patch("app.tasks.pricing_tasks.PriceOptimizer")
    @patch("app.tasks.pricing_tasks.PriceCalculator")
    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_ai_pricing_task_product_exception(self, mock_session_local, mock_calc_cls, mock_opt_cls):
        """单个产品异常时继续"""
        task = _make_task_mock()

        bad_product = _BadProduct(pid=1)
        good_product = _make_product_mock(pid=2, regular_price="100.00", currency="USD")
        mock_db = _make_db_mock(task=task, site=None, products=[bad_product, good_product])
        mock_session_local.return_value = mock_db

        mock_opt = mock_opt_cls.return_value
        mock_opt.suggest_price = MagicMock(return_value={"suggested_price": 150.0})
        mock_calc = mock_calc_cls.return_value
        mock_calc.calculate_price = AsyncMock(return_value=150.0)

        ai_pricing_task.run(
            task_id=1,
            params={"pricing_strategy": "competitive"},
        )

        assert task.status == "completed"
        assert task.failed_items == 1
        assert task.processed_items == 1
