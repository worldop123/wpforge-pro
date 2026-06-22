"""
价格引擎测试
"""
import pytest
from app.services.price_service import (
    PriceService,
    PricingStrategy,
    get_price_service,
)


class TestPricingStrategy:
    """定价策略枚举测试"""

    def test_strategy_values(self):
        """测试策略值"""
        assert hasattr(PricingStrategy, 'COST_PLUS')
        assert hasattr(PricingStrategy, 'COMPETITOR_BASED')
        assert hasattr(PricingStrategy, 'VALUE_BASED')
        assert hasattr(PricingStrategy, 'DYNAMIC')
        assert hasattr(PricingStrategy, 'PSYCHOLOGICAL')

    def test_strategy_count(self):
        """测试策略数量"""
        assert len(PricingStrategy) >= 5


class TestPriceService:
    """价格服务测试"""

    def test_service_creation(self):
        """测试服务创建"""
        service = PriceService()
        assert service is not None

    def test_calculate_price_cost_plus(self):
        """测试成本加成定价"""
        service = PriceService()
        price = service.calculate_price(
            cost=10.0,
            strategy=PricingStrategy.COST_PLUS,
            markup=0.5  # 50%
        )
        assert isinstance(price, float)
        assert price == 15.0  # 10 * 1.5

    def test_calculate_price_competitor_based(self):
        """测试竞品定价"""
        service = PriceService()
        price = service.calculate_price(
            cost=10.0,
            strategy=PricingStrategy.COMPETITOR_BASED,
            competitor_prices=[15.0, 18.0, 20.0]
        )
        assert isinstance(price, float)
        assert price > 0

    def test_calculate_price_psychological(self):
        """测试心理定价"""
        service = PriceService()
        price = service.calculate_price(
            cost=10.0,
            strategy=PricingStrategy.PSYCHOLOGICAL,
            markup=1.0
        )
        assert isinstance(price, float)
        # 应该以.99或.95结尾
        assert price > 0

    def test_apply_price_ending(self):
        """测试应用价格尾数"""
        service = PriceService()
        result = service.apply_price_ending(20.0, ending="99")
        assert isinstance(result, float)
        assert result == 19.99

    def test_apply_price_ending_95(self):
        """测试.95尾数"""
        service = PriceService()
        result = service.apply_price_ending(20.0, ending="95")
        assert isinstance(result, float)
        assert result == 19.95

    def test_calculate_sale_price(self):
        """测试计算促销价"""
        service = PriceService()
        sale_price = service.calculate_sale_price(100.0, discount=0.2)
        assert isinstance(sale_price, float)
        assert sale_price == 80.0  # 100 * 0.8

    def test_calculate_sale_price_percentage(self):
        """测试百分比折扣"""
        service = PriceService()
        sale_price = service.calculate_sale_price(100.0, discount_percent=20)
        assert isinstance(sale_price, float)
        assert sale_price == 80.0

    def test_calculate_discount_percentage(self):
        """测试计算折扣百分比"""
        service = PriceService()
        discount = service.calculate_discount_percentage(100.0, 80.0)
        assert isinstance(discount, float)
        assert discount == 20.0  # 20% off

    def test_convert_currency(self):
        """测试货币转换"""
        service = PriceService()
        result = service.convert_currency(100.0, "USD", "EUR")
        assert isinstance(result, float)
        assert result > 0

    def test_get_exchange_rate(self):
        """测试获取汇率"""
        service = PriceService()
        rate = service.get_exchange_rate("USD", "EUR")
        assert isinstance(rate, float)
        assert rate > 0

    def test_get_supported_currencies(self):
        """测试获取支持的货币"""
        service = PriceService()
        currencies = service.get_supported_currencies()
        assert isinstance(currencies, list)
        assert len(currencies) > 0
        assert "USD" in currencies
        assert "EUR" in currencies

    def test_format_price(self):
        """测试格式化价格"""
        service = PriceService()
        formatted = service.format_price(29.99, "USD")
        assert isinstance(formatted, str)
        assert "$" in formatted or "USD" in formatted

    def test_format_price_euro(self):
        """测试欧元格式化"""
        service = PriceService()
        formatted = service.format_price(29.99, "EUR")
        assert isinstance(formatted, str)
        assert "€" in formatted or "EUR" in formatted

    def test_calculate_profit_margin(self):
        """测试计算利润率"""
        service = PriceService()
        margin = service.calculate_profit_margin(cost=10.0, price=15.0)
        assert isinstance(margin, float)
        assert margin > 0

    def test_calculate_markup(self):
        """测试计算加成"""
        service = PriceService()
        markup = service.calculate_markup(cost=10.0, price=15.0)
        assert isinstance(markup, float)
        assert markup == 50.0  # 50% markup

    def test_suggest_price(self):
        """测试建议价格"""
        service = PriceService()
        suggestion = service.suggest_price(
            cost=10.0,
            category="electronics",
            competitor_prices=[15.0, 18.0, 20.0]
        )
        assert isinstance(suggestion, dict)
        assert "recommended_price" in suggestion
        assert "strategy" in suggestion
        assert "profit_margin" in suggestion

    def test_batch_price_calculation(self):
        """测试批量价格计算"""
        service = PriceService()
        products = [
            {"cost": 10.0, "name": "Product 1"},
            {"cost": 20.0, "name": "Product 2"},
            {"cost": 30.0, "name": "Product 3"},
        ]
        results = service.batch_calculate_prices(
            products,
            strategy=PricingStrategy.COST_PLUS,
            markup=0.5
        )
        assert isinstance(results, list)
        assert len(results) == 3
        assert all("price" in r for r in results)

    def test_generate_coupon_code(self):
        """测试生成优惠券代码"""
        service = PriceService()
        coupon = service.generate_coupon_code(
            discount_type="percent",
            discount_value=20,
            prefix="SAVE"
        )
        assert isinstance(coupon, dict)
        assert "code" in coupon
        assert "discount_type" in coupon
        assert "discount_value" in coupon

    def test_validate_coupon(self):
        """测试验证优惠券"""
        service = PriceService()
        is_valid = service.validate_coupon("SAVE20", subtotal=100.0)
        assert isinstance(is_valid, bool)

    def test_calculate_shipping(self):
        """测试计算运费"""
        service = PriceService()
        shipping = service.calculate_shipping(
            subtotal=100.0,
            weight=2.0,
            destination="US"
        )
        assert isinstance(shipping, float)
        assert shipping >= 0

    def test_calculate_tax(self):
        """测试计算税费"""
        service = PriceService()
        tax = service.calculate_tax(subtotal=100.0, region="US-CA")
        assert isinstance(tax, float)
        assert tax >= 0

    def test_get_pricing_tiers(self):
        """测试获取价格阶梯"""
        service = PriceService()
        tiers = service.get_pricing_tiers(base_price=100.0)
        assert isinstance(tiers, list)
        assert len(tiers) > 0
        assert all("quantity" in t and "price" in t for t in tiers)

    def test_dynamic_pricing(self):
        """测试动态定价"""
        service = PriceService()
        price = service.dynamic_pricing(
            base_price=100.0,
            demand_level="high",
            inventory_level=10
        )
        assert isinstance(price, float)
        assert price > 0

    def test_get_instance(self):
        """测试单例模式"""
        s1 = get_price_service()
        s2 = get_price_service()
        assert s1 is s2

    def test_round_price(self):
        """测试价格四舍五入"""
        service = PriceService()
        rounded = service.round_price(19.999)
        assert isinstance(rounded, float)
        assert rounded == 20.0 or rounded == 19.99

    def test_is_sale_price_better(self):
        """测试促销价是否更优"""
        service = PriceService()
        assert service.is_sale_price_better(100.0, 80.0) is True
        assert service.is_sale_price_better(100.0, 100.0) is False
        assert service.is_sale_price_better(100.0, 120.0) is False

    def test_calculate_lifetime_value(self):
        """测试计算客户终身价值"""
        service = PriceService()
        ltv = service.calculate_lifetime_value(
            avg_order_value=50.0,
            purchase_frequency=4,
            customer_lifespan=3
        )
        assert isinstance(ltv, float)
        assert ltv > 0

    def test_get_price_bracket(self):
        """测试获取价格区间"""
        service = PriceService()
        bracket = service.get_price_bracket(59.99)
        assert isinstance(bracket, str)
        assert len(bracket) > 0
