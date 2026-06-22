"""
价格服务测试 - 测试 PriceCalculator、PriceOptimizer、ExchangeRateService
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from app.services.price_service import (
    PriceStrategy,
    ExchangeRate,
    ExchangeRateProvider,
    DefaultExchangeRateProvider,
    ExchangeRateService,
    PriceCalculator,
    PriceOptimizer,
    exchange_rate_service,
    price_calculator,
    price_optimizer,
)


class TestPriceStrategy:
    """PriceStrategy 枚举测试"""

    def test_strategy_values(self):
        assert PriceStrategy.FIXED_MARKUP.value == "fixed_markup"
        assert PriceStrategy.PERCENTAGE_MARKUP.value == "percentage_markup"
        assert PriceStrategy.TIERED_PRICING.value == "tiered_pricing"
        assert PriceStrategy.COMPETITIVE_PRICING.value == "competitive_pricing"
        assert PriceStrategy.PSYCHOLOGICAL_PRICING.value == "psychological_pricing"

    def test_strategy_count(self):
        assert len(PriceStrategy) == 5


class TestExchangeRate:
    """ExchangeRate 数据类测试"""

    def test_defaults(self):
        rate = ExchangeRate(base_currency="USD", target_currency="CNY", rate=7.24)
        assert rate.base_currency == "USD"
        assert rate.target_currency == "CNY"
        assert rate.rate == 7.24
        assert rate.source == "default"

    def test_is_expired_false(self):
        rate = ExchangeRate(base_currency="USD", target_currency="CNY", rate=7.24)
        assert rate.is_expired(ttl=3600) is False

    def test_is_expired_true(self):
        import time
        rate = ExchangeRate(
            base_currency="USD",
            target_currency="CNY",
            rate=7.24,
            timestamp=time.time() - 7200,
        )
        assert rate.is_expired(ttl=3600) is True


class TestDefaultExchangeRateProvider:
    """DefaultExchangeRateProvider 测试"""

    @pytest.mark.asyncio
    async def test_get_rate_usd_to_cny(self):
        provider = DefaultExchangeRateProvider()
        rate = await provider.get_rate("USD", "CNY")
        assert rate.base_currency == "USD"
        assert rate.target_currency == "CNY"
        assert rate.rate == 7.24

    @pytest.mark.asyncio
    async def test_get_rate_same_currency(self):
        provider = DefaultExchangeRateProvider()
        rate = await provider.get_rate("USD", "USD")
        assert rate.rate == 1.0

    @pytest.mark.asyncio
    async def test_get_rate_case_insensitive(self):
        provider = DefaultExchangeRateProvider()
        rate = await provider.get_rate("usd", "cny")
        assert rate.base_currency == "USD"
        assert rate.target_currency == "CNY"

    @pytest.mark.asyncio
    async def test_get_rate_unknown_currency(self):
        provider = DefaultExchangeRateProvider()
        # 未知货币默认 1.0
        rate = await provider.get_rate("USD", "XXX")
        assert rate.rate == 1.0

    @pytest.mark.asyncio
    async def test_get_rates_batch(self):
        provider = DefaultExchangeRateProvider()
        rates = await provider.get_rates("USD", ["CNY", "EUR"])
        assert "CNY" in rates
        assert "EUR" in rates
        assert rates["CNY"].rate == 7.24
        assert rates["EUR"].rate == 0.92

    def test_is_available(self):
        provider = DefaultExchangeRateProvider()
        assert provider.is_available() is True


class TestExchangeRateService:
    """ExchangeRateService 测试"""

    def test_singleton(self):
        from app.services.price_service import exchange_rate_service as s1
        assert s1 is exchange_rate_service

    def test_init_providers(self):
        service = ExchangeRateService()
        assert len(service.providers) > 0

    @pytest.mark.asyncio
    async def test_get_rate_same_currency(self):
        service = ExchangeRateService()
        rate = await service.get_rate("USD", "USD")
        assert rate.rate == 1.0
        assert rate.source == "direct"

    @pytest.mark.asyncio
    async def test_get_rate_usd_cny(self):
        service = ExchangeRateService()
        rate = await service.get_rate("USD", "CNY", use_cache=False)
        assert rate.rate > 1

    @pytest.mark.asyncio
    async def test_get_rate_uses_cache(self):
        service = ExchangeRateService()
        # 第一次获取，调用 provider
        await service.get_rate("USD", "EUR", use_cache=True)
        # 替换 provider 为 mock，验证第二次走缓存
        mock_provider = MagicMock(spec=ExchangeRateProvider)
        mock_provider.get_rate = AsyncMock()
        service.providers = [mock_provider]
        await service.get_rate("USD", "EUR", use_cache=True)
        mock_provider.get_rate.assert_not_called()

    @pytest.mark.asyncio
    async def test_convert(self):
        service = ExchangeRateService()
        # USD -> USD 应该是原值
        result = await service.convert(100.0, "USD", "USD")
        assert result == 100.0

    @pytest.mark.asyncio
    async def test_convert_usd_to_cny(self):
        service = ExchangeRateService()
        result = await service.convert(100.0, "USD", "CNY", use_cache=False)
        assert result == pytest.approx(100.0 * 7.24)

    def test_clear_cache(self):
        service = ExchangeRateService()
        service.cache["test"] = "value"
        service.clear_cache()
        assert len(service.cache) == 0

    def test_get_cache_stats(self):
        service = ExchangeRateService()
        stats = service.get_cache_stats()
        assert "size" in stats
        assert "ttl" in stats


class TestPriceCalculator:
    """PriceCalculator 测试"""

    def test_format_price_usd(self):
        calc = PriceCalculator()
        formatted = calc.format_price(99.99, "USD")
        assert "$" in formatted
        assert "99.99" in formatted

    def test_format_price_cny(self):
        calc = PriceCalculator()
        formatted = calc.format_price(199.0, "CNY")
        assert "¥" in formatted

    def test_format_price_unknown_currency(self):
        calc = PriceCalculator()
        formatted = calc.format_price(99.99, "XXX")
        # 未知货币返回货币代码
        assert "XXX" in formatted

    def test_format_price_with_thousands(self):
        calc = PriceCalculator()
        formatted = calc.format_price(1299.99, "USD")
        assert "1,299.99" in formatted

    def test_apply_psychological_pricing_small(self):
        calc = PriceCalculator()
        # 小额：.95 或 .99
        result = calc._apply_psychological_pricing(5.0)
        assert result in [4.95, 5.95, 5.99]

    def test_apply_psychological_pricing_medium(self):
        calc = PriceCalculator()
        # 中额：.99 结尾
        result = calc._apply_psychological_pricing(25.0)
        assert result == 25.99

    def test_apply_psychological_pricing_large(self):
        calc = PriceCalculator()
        # 大额：取整减1
        result = calc._apply_psychological_pricing(100.0)
        assert result == 99.99

    def test_apply_psychological_pricing_less_than_one(self):
        calc = PriceCalculator()
        # 小于1不处理
        result = calc._apply_psychological_pricing(0.5)
        assert result == 0.5

    def test_apply_tiered_pricing_no_tiers(self):
        calc = PriceCalculator()
        result = calc._apply_tiered_pricing(100.0, [])
        # 没有阶梯时默认 30% 加价
        assert result == 130.0

    def test_apply_tiered_pricing_with_tiers(self):
        calc = PriceCalculator()
        tiers = [
            {"min_quantity": 1, "markup_percentage": 20},
            {"min_quantity": 10, "markup_percentage": 15},
        ]
        result = calc._apply_tiered_pricing(100.0, tiers)
        # 默认使用第一档
        assert result == 120.0

    def test_apply_competitive_pricing_no_competitors(self):
        calc = PriceCalculator()
        result = calc._apply_competitive_pricing(100.0, [])
        assert result == 130.0

    def test_apply_competitive_pricing_with_competitors(self):
        calc = PriceCalculator()
        result = calc._apply_competitive_pricing(100.0, [200.0, 300.0])
        # 平均 250 * 0.95 = 237.5
        assert result == 237.5

    @pytest.mark.asyncio
    async def test_calculate_price_percentage_markup(self):
        calc = PriceCalculator()
        result = await calc.calculate_price(
            base_price=100.0,
            base_currency="USD",
            target_currency="USD",
            strategy=PriceStrategy.PERCENTAGE_MARKUP,
            markup_percentage=30.0,
            psychological_pricing=False,
        )
        assert result == 130.0

    @pytest.mark.asyncio
    async def test_calculate_price_fixed_markup(self):
        calc = PriceCalculator()
        result = await calc.calculate_price(
            base_price=100.0,
            base_currency="USD",
            target_currency="USD",
            strategy=PriceStrategy.FIXED_MARKUP,
            markup_fixed=20.0,
            psychological_pricing=False,
        )
        assert result == 120.0

    @pytest.mark.asyncio
    async def test_calculate_price_with_currency_conversion(self):
        calc = PriceCalculator()
        result = await calc.calculate_price(
            base_price=100.0,
            base_currency="USD",
            target_currency="CNY",
            strategy=PriceStrategy.PERCENTAGE_MARKUP,
            markup_percentage=0.0,
            psychological_pricing=False,
            use_cache=False,
        )
        # 100 USD * 7.24 = 724 CNY
        assert result == pytest.approx(724.0)

    @pytest.mark.asyncio
    async def test_calculate_price_with_psychological(self):
        calc = PriceCalculator()
        result = await calc.calculate_price(
            base_price=100.0,
            base_currency="USD",
            target_currency="USD",
            strategy=PriceStrategy.PERCENTAGE_MARKUP,
            markup_percentage=30.0,
            psychological_pricing=True,
        )
        # 130 -> 心理定价 129.99
        assert result == 129.99

    @pytest.mark.asyncio
    async def test_calculate_product_prices(self):
        calc = PriceCalculator()
        product = {
            "regular_price": "100",
            "sale_price": "80",
            "price": "90",
        }
        result = await calc.calculate_product_prices(
            product,
            base_currency="USD",
            target_currency="USD",
            strategy=PriceStrategy.PERCENTAGE_MARKUP,
            markup_percentage=10.0,
            psychological_pricing=False,
        )
        assert result["regular_price"] == 110.0
        assert result["sale_price"] == 88.0
        assert result["price"] == 99.0
        assert result["currency"] == "USD"

    @pytest.mark.asyncio
    async def test_calculate_product_prices_empty(self):
        calc = PriceCalculator()
        result = await calc.calculate_product_prices(
            {},
            base_currency="USD",
            target_currency="USD",
        )
        assert result["currency"] == "USD"


class TestPriceOptimizer:
    """PriceOptimizer 测试"""

    def test_singleton(self):
        from app.services.price_service import price_optimizer as p1
        assert p1 is price_optimizer

    def test_optimize_prices_balanced(self):
        opt = PriceOptimizer()
        products = [{"cost_price": 100.0, "name": "p1"}, {"cost_price": 200.0, "name": "p2"}]
        result = opt.optimize_prices(products, strategy="balanced", target_margin=30.0)
        assert len(result) == 2
        assert result[0]["optimized_price"] == 130.0
        assert result[0]["margin"] == 30.0
        assert result[1]["optimized_price"] == 260.0

    def test_optimize_prices_max_profit(self):
        opt = PriceOptimizer()
        products = [{"cost_price": 100.0}]
        result = opt.optimize_prices(products, strategy="max_profit", max_margin=50.0)
        assert result[0]["optimized_price"] == 150.0
        assert result[0]["margin"] == 50.0

    def test_optimize_prices_max_volume(self):
        opt = PriceOptimizer()
        products = [{"cost_price": 100.0}]
        result = opt.optimize_prices(products, strategy="max_volume", min_margin=15.0)
        assert result[0]["optimized_price"] == pytest.approx(115.0)
        assert result[0]["margin"] == 15.0

    def test_optimize_prices_uses_price_when_no_cost(self):
        opt = PriceOptimizer()
        products = [{"price": 100.0}]
        result = opt.optimize_prices(products, strategy="balanced", target_margin=20.0)
        assert result[0]["optimized_price"] == 120.0

    def test_optimize_prices_unknown_strategy(self):
        opt = PriceOptimizer()
        products = [{"cost_price": 100.0}]
        result = opt.optimize_prices(products, strategy="unknown", target_margin=25.0)
        # 未知策略用 target_margin
        assert result[0]["optimized_price"] == 125.0

    def test_suggest_price_no_competitors(self):
        opt = PriceOptimizer()
        result = opt.suggest_price(100.0, [])
        assert result["suggested_price"] == 150.0
        assert result["min_price"] == 120.0
        assert result["max_price"] == 200.0
        assert result["strategy"] == "default"

    def test_suggest_price_medium_demand(self):
        opt = PriceOptimizer()
        result = opt.suggest_price(100.0, [200.0, 300.0], market_demand="medium")
        # 平均 250 * 0.95 = 237.5
        assert result["suggested_price"] == 237.5
        assert result["strategy"] == "competitive_based"

    def test_suggest_price_high_demand(self):
        opt = PriceOptimizer()
        result = opt.suggest_price(100.0, [200.0, 300.0], market_demand="high")
        # 平均 250 * 1.05 = 262.5
        assert result["suggested_price"] == 262.5

    def test_suggest_price_low_demand(self):
        opt = PriceOptimizer()
        result = opt.suggest_price(100.0, [200.0, 300.0], market_demand="low")
        # 最低 200 * 0.95 = 190
        assert result["suggested_price"] == 190.0

    def test_suggest_price_ensures_min_profit(self):
        opt = PriceOptimizer()
        # 竞争对手价格很低，确保最低利润
        result = opt.suggest_price(100.0, [50.0, 60.0], market_demand="low")
        # 最低价 50 * 0.95 = 47.5，但最低利润是 100*1.15=115
        assert result["suggested_price"] >= 115.0
