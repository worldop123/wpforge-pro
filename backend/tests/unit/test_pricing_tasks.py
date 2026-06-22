"""
价格计算任务测试

pricing_tasks.py 导入了 price_service 中不存在的 PriceEngine 类，
因此通过 sys.modules 注入伪造的 price_service 模块来测试任务逻辑。
"""
import sys
import types
from unittest.mock import MagicMock, patch
from decimal import Decimal

import pytest


# ==================== 构造伪造的 price_service 模块 ====================

class FakePriceEngine:
    """伪造的价格引擎，提供 pricing_tasks 用到的方法"""

    def calculate_markup(self, base_price: float, markup_percent: float) -> float:
        return base_price * (1 + markup_percent / 100)

    def optimize_price_ending(self, price: float, ending: str = ".99") -> float:
        # 简单实现：把小数部分替换为指定尾数
        try:
            ending_val = float(ending)
        except (ValueError, TypeError):
            ending_val = 0.99
        return float(int(price) + ending_val)

    def generate_sale_price(self, regular_price: float, discount_percent: float = 15) -> float:
        return regular_price * (1 - discount_percent / 100)

    def calculate_competitive_price(self, cost_price: float,
                                     competitor_prices: list,
                                     market_position: str = "mid") -> float:
        if not competitor_prices:
            return cost_price * 1.5
        avg = sum(competitor_prices) / len(competitor_prices)
        if market_position == "low":
            return avg * 0.9
        elif market_position == "high":
            return avg * 1.1
        return avg

    def calculate_value_based_price(self, cost_price: float,
                                     perceived_value_multiplier: float = 2.0) -> float:
        return cost_price * perceived_value_multiplier


class FakeExchangeRateService:
    """伪造的汇率服务，提供同步的 convert 和 update_rates 方法"""

    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        # 简单固定汇率用于测试
        rates = {"USD": 1.0, "CNY": 7.0, "EUR": 0.9}
        from_rate = rates.get(from_currency, 1.0)
        to_rate = rates.get(to_currency, 1.0)
        return amount * (to_rate / from_rate)

    def update_rates(self) -> dict:
        return {
            "updated_at": "2024-01-01T00:00:00Z",
            "base": "USD",
            "rates": {"CNY": 7.0, "EUR": 0.9, "USD": 1.0},
        }


def _install_fake_price_service():
    """向真实的 price_service 模块添加缺失的 PriceEngine 类。

    只补充缺失的 PriceEngine 类（pricing_tasks 模块导入需要），
    不修改 ExchangeRateService，以避免破坏 PriceCalculator 等使用
    异步 convert 方法的测试。ExchangeRateService 在各测试内通过
    @patch 替换为同步版本。
    """
    import app.services.price_service as real_module
    if not hasattr(real_module, "PriceEngine"):
        real_module.PriceEngine = FakePriceEngine


# 在导入 pricing_tasks 之前注入 PriceEngine
_install_fake_price_service()

from app.tasks.pricing_tasks import (  # noqa: E402
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


def _make_task_mock(status="pending"):
    """构造一个 mock task 对象"""
    task = MagicMock()
    task.id = 1
    task.status = status
    task.progress = 0
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

    query_results = {}

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
    db.func = MagicMock()
    db.func.now = MagicMock(return_value="now")
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

    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_calculate_prices_task_success(self, mock_session_local):
        """任务正常执行"""
        task = _make_task_mock()
        site = _make_site_mock()
        products = [
            _make_product_mock(pid=1, regular_price="100.00", currency="USD"),
            _make_product_mock(pid=2, regular_price="50.00", currency="USD"),
        ]
        mock_db = _make_db_mock(task=task, site=site, products=products)
        mock_session_local.return_value = mock_db

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

    @patch("app.tasks.pricing_tasks.SessionLocal")
    @patch("app.tasks.pricing_tasks.ExchangeRateService", FakeExchangeRateService)
    def test_calculate_prices_task_with_currency_conversion(self, mock_session_local):
        """测试汇率转换流程"""
        task = _make_task_mock()
        site = _make_site_mock()
        products = [
            _make_product_mock(pid=1, regular_price="100.00", currency="EUR"),
        ]
        mock_db = _make_db_mock(task=task, site=site, products=products)
        mock_session_local.return_value = mock_db

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

    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_calculate_prices_task_no_price_product(self, mock_session_local):
        """产品没有价格时跳过"""
        task = _make_task_mock()
        site = _make_site_mock()
        products = [
            _make_product_mock(pid=1, regular_price=None, price=None, currency="USD"),
            _make_product_mock(pid=2, regular_price="100.00", currency="USD"),
        ]
        mock_db = _make_db_mock(task=task, site=site, products=products)
        mock_session_local.return_value = mock_db

        calculate_prices_task.run(
            task_id=1,
            params={"site_id": 1, "include_sale_price": False},
        )

        # 只处理了一个有价格的产品
        assert task.processed_items == 1
        assert task.status == "completed"

    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_calculate_prices_task_no_site(self, mock_session_local):
        """站点不存在时仍能执行"""
        task = _make_task_mock()
        products = [
            _make_product_mock(pid=1, regular_price="100.00", currency="USD"),
        ]
        mock_db = _make_db_mock(task=task, site=None, products=products)
        mock_session_local.return_value = mock_db

        calculate_prices_task.run(
            task_id=1,
            params={"target_currency": "USD", "include_sale_price": False},
        )

        assert task.status == "completed"
        assert task.processed_items == 1

    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_calculate_prices_task_empty_products(self, mock_session_local):
        """没有产品时正常完成"""
        task = _make_task_mock()
        site = _make_site_mock()
        mock_db = _make_db_mock(task=task, site=site, products=[])
        mock_session_local.return_value = mock_db

        calculate_prices_task.run(
            task_id=1,
            params={"site_id": 1, "include_sale_price": True},
        )

        assert task.status == "completed"
        assert task.total_items == 0
        assert task.processed_items == 0

    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_calculate_prices_task_product_exception(self, mock_session_local):
        """单个产品处理异常时继续处理其他产品"""
        task = _make_task_mock()
        site = _make_site_mock()

        bad_product = MagicMock()
        bad_product.id = 1
        bad_product.regular_price = Decimal("100.00")
        bad_product.price = Decimal("100.00")
        bad_product.currency = "USD"
        bad_product.is_deleted = False
        # 让 regular_price 的访问抛异常
        type(bad_product).regular_price = property(
            lambda self: (_ for _ in ()).throw(ValueError("bad"))
        )

        good_product = _make_product_mock(pid=2, regular_price="100.00", currency="USD")
        mock_db = _make_db_mock(task=task, site=site, products=[bad_product, good_product])
        mock_session_local.return_value = mock_db

        calculate_prices_task.run(
            task_id=1,
            params={"site_id": 1, "include_sale_price": False},
        )

        # 异常产品被跳过，好产品被处理
        assert task.status == "completed"
        assert task.failed_items == 1

    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_calculate_prices_task_with_product_ids(self, mock_session_local):
        """指定产品ID列表"""
        task = _make_task_mock()
        site = _make_site_mock()
        products = [
            _make_product_mock(pid=1, regular_price="100.00", currency="USD"),
        ]
        mock_db = _make_db_mock(task=task, site=site, products=products)
        mock_session_local.return_value = mock_db

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

    @patch("app.tasks.pricing_tasks.ExchangeRateService", FakeExchangeRateService)
    def test_update_exchange_rates_success(self):
        """更新汇率成功"""
        result = update_exchange_rates_task.run()

        assert result["success"] is True
        assert result["base_currency"] == "USD"
        assert result["rates_count"] == 3
        assert "updated_at" in result

    @patch("app.tasks.pricing_tasks.ExchangeRateService")
    def test_update_exchange_rates_exception(self, mock_service_cls):
        """更新汇率异常时抛出"""
        mock_service = MagicMock()
        mock_service.update_rates.side_effect = Exception("API error")
        mock_service_cls.return_value = mock_service

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

    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_ai_pricing_task_competitive(self, mock_session_local):
        """竞争导向定价策略"""
        task = _make_task_mock()
        products = [
            _make_product_mock(pid=1, regular_price="100.00", currency="USD"),
            _make_product_mock(pid=2, regular_price="200.00", currency="USD"),
        ]
        mock_db = _make_db_mock(task=task, site=None, products=products)
        mock_session_local.return_value = mock_db

        calculate_prices_task_run = ai_pricing_task.run(
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

    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_ai_pricing_task_value_strategy(self, mock_session_local):
        """价值导向定价策略"""
        task = _make_task_mock()
        products = [
            _make_product_mock(pid=1, regular_price="100.00", currency="USD"),
        ]
        mock_db = _make_db_mock(task=task, site=None, products=products)
        mock_session_local.return_value = mock_db

        ai_pricing_task.run(
            task_id=1,
            params={
                "pricing_strategy": "value",
                "product_ids": [1],
            },
        )

        assert task.status == "completed"
        assert task.result["strategy"] == "value"

    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_ai_pricing_task_cost_plus_strategy(self, mock_session_local):
        """成本加成定价策略"""
        task = _make_task_mock()
        products = [
            _make_product_mock(pid=1, regular_price="100.00", currency="USD"),
        ]
        mock_db = _make_db_mock(task=task, site=None, products=products)
        mock_session_local.return_value = mock_db

        ai_pricing_task.run(
            task_id=1,
            params={
                "pricing_strategy": "cost_plus",
                "product_ids": [1],
            },
        )

        assert task.status == "completed"
        assert task.result["strategy"] == "cost_plus"

    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_ai_pricing_task_empty_products(self, mock_session_local):
        """没有产品时正常完成"""
        task = _make_task_mock()
        mock_db = _make_db_mock(task=task, site=None, products=[])
        mock_session_local.return_value = mock_db

        ai_pricing_task.run(
            task_id=1,
            params={"pricing_strategy": "competitive"},
        )

        assert task.status == "completed"
        assert task.total_items == 0

    @patch("app.tasks.pricing_tasks.SessionLocal")
    def test_ai_pricing_task_product_exception(self, mock_session_local):
        """单个产品异常时继续"""
        task = _make_task_mock()

        bad_product = MagicMock()
        bad_product.id = 1
        bad_product.regular_price = Decimal("100.00")
        bad_product.currency = "USD"
        bad_product.is_deleted = False
        # 让属性访问抛异常
        type(bad_product).regular_price = property(
            lambda self: (_ for _ in ()).throw(ValueError("bad"))
        )

        good_product = _make_product_mock(pid=2, regular_price="100.00", currency="USD")
        mock_db = _make_db_mock(task=task, site=None, products=[bad_product, good_product])
        mock_session_local.return_value = mock_db

        ai_pricing_task.run(
            task_id=1,
            params={"pricing_strategy": "competitive"},
        )

        assert task.status == "completed"
