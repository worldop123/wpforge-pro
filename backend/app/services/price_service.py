"""
汇率与价格处理服务 - 实时汇率、加价公式、价格优化
"""

from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, field
import time
import math
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class PriceStrategy(str, Enum):
    """价格策略"""
    FIXED_MARKUP = "fixed_markup"  # 固定加价
    PERCENTAGE_MARKUP = "percentage_markup"  # 百分比加价
    TIERED_PRICING = "tiered_pricing"  # 阶梯定价
    COMPETITIVE_PRICING = "competitive_pricing"  # 竞争定价
    PSYCHOLOGICAL_PRICING = "psychological_pricing"  # 心理定价


@dataclass
class ExchangeRate:
    """汇率信息"""
    base_currency: str
    target_currency: str
    rate: float
    timestamp: float = field(default_factory=time.time)
    source: str = "default"
    
    def is_expired(self, ttl: int = 3600) -> bool:
        """检查是否过期"""
        return time.time() - self.timestamp > ttl


class ExchangeRateProvider:
    """汇率提供者基类"""
    
    async def get_rate(self, base_currency: str, target_currency: str) -> ExchangeRate:
        """获取汇率"""
        raise NotImplementedError
    
    async def get_rates(self, base_currency: str, target_currencies: List[str]) -> Dict[str, ExchangeRate]:
        """批量获取汇率"""
        results = {}
        for target in target_currencies:
            results[target] = await self.get_rate(base_currency, target)
        return results
    
    def is_available(self) -> bool:
        return True


class DefaultExchangeRateProvider(ExchangeRateProvider):
    """默认汇率提供者（使用固定汇率作为fallback）"""
    
    # 常用货币对美元的汇率（2024年参考值）
    DEFAULT_RATES = {
        "USD": 1.0,
        "EUR": 0.92,
        "GBP": 0.79,
        "JPY": 149.50,
        "CNY": 7.24,
        "HKD": 7.82,
        "AUD": 1.53,
        "CAD": 1.36,
        "CHF": 0.88,
        "SGD": 1.34,
        "KRW": 1320.0,
        "INR": 83.30,
        "RUB": 92.50,
        "BRL": 4.97,
        "ZAR": 18.65,
        "MXN": 17.15,
        "PLN": 4.05,
        "SEK": 10.45,
        "NOK": 10.60,
        "DKK": 6.87,
        "CZK": 22.50,
        "HUF": 355.0,
        "RON": 4.57,
        "TRY": 28.80,
        "THB": 35.20,
        "MYR": 4.70,
        "IDR": 15650.0,
        "PHP": 55.80,
        "VND": 24500.0,
    }
    
    async def get_rate(self, base_currency: str, target_currency: str) -> ExchangeRate:
        base = base_currency.upper()
        target = target_currency.upper()
        
        base_rate = self.DEFAULT_RATES.get(base, 1.0)
        target_rate = self.DEFAULT_RATES.get(target, 1.0)
        
        # 计算交叉汇率
        rate = target_rate / base_rate
        
        return ExchangeRate(
            base_currency=base,
            target_currency=target,
            rate=rate,
            source="default"
        )


class ExchangeRateService:
    """汇率服务"""
    
    def __init__(self):
        self.providers: List[ExchangeRateProvider] = []
        self.cache: Dict[str, ExchangeRate] = {}
        self.cache_ttl = settings.EXCHANGE_RATE_CACHE_TTL
        self._init_providers()
    
    def _init_providers(self):
        """初始化汇率提供者"""
        # 默认提供者（固定汇率）
        self.providers.append(DefaultExchangeRateProvider())
    
    def _get_cache_key(self, base: str, target: str) -> str:
        return f"{base.upper()}_{target.upper()}"
    
    async def get_rate(self, base_currency: str, target_currency: str, use_cache: bool = True) -> ExchangeRate:
        """获取汇率
        
        Args:
            base_currency: 基础货币
            target_currency: 目标货币
            use_cache: 是否使用缓存
        """
        if base_currency.upper() == target_currency.upper():
            return ExchangeRate(
                base_currency=base_currency,
                target_currency=target_currency,
                rate=1.0,
                source="direct"
            )
        
        cache_key = self._get_cache_key(base_currency, target_currency)
        
        # 检查缓存
        if use_cache and cache_key in self.cache:
            cached = self.cache[cache_key]
            if not cached.is_expired(self.cache_ttl):
                return cached
        
        # 从提供者获取
        last_error = None
        for provider in self.providers:
            try:
                rate = await provider.get_rate(base_currency, target_currency)
                self.cache[cache_key] = rate
                return rate
            except Exception as e:
                last_error = e
                logger.warning(f"Exchange rate provider failed: {e}")
                continue
        
        raise Exception(f"Failed to get exchange rate. Last error: {last_error}")
    
    async def convert(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
        use_cache: bool = True
    ) -> float:
        """转换货币
        
        Args:
            amount: 金额
            from_currency: 源货币
            to_currency: 目标货币
            use_cache: 是否使用缓存
        """
        rate = await self.get_rate(from_currency, to_currency, use_cache)
        return amount * rate.rate
    
    def clear_cache(self):
        """清除缓存"""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict:
        """获取缓存统计"""
        return {
            "size": len(self.cache),
            "ttl": self.cache_ttl,
        }


class PriceCalculator:
    """价格计算器"""
    
    def __init__(self):
        self.exchange_service = ExchangeRateService()
    
    async def calculate_price(
        self,
        base_price: float,
        base_currency: str,
        target_currency: str,
        strategy: PriceStrategy = PriceStrategy.PERCENTAGE_MARKUP,
        markup_percentage: float = 30.0,
        markup_fixed: float = 0.0,
        psychological_pricing: bool = True,
        round_decimals: int = 2,
        **kwargs
    ) -> float:
        """计算最终价格
        
        Args:
            base_price: 基础价格（成本价）
            base_currency: 基础货币
            target_currency: 目标货币
            strategy: 定价策略
            markup_percentage: 加价百分比
            markup_fixed: 固定加价金额
            psychological_pricing: 是否应用心理定价
            round_decimals: 小数位数
        """
        # 转换货币
        converted_price = await self.exchange_service.convert(
            base_price,
            base_currency,
            target_currency
        )
        
        # 应用定价策略
        if strategy == PriceStrategy.PERCENTAGE_MARKUP:
            price = converted_price * (1 + markup_percentage / 100)
        elif strategy == PriceStrategy.FIXED_MARKUP:
            price = converted_price + markup_fixed
        elif strategy == PriceStrategy.TIERED_PRICING:
            price = self._apply_tiered_pricing(converted_price, kwargs.get("tiers", []))
        elif strategy == PriceStrategy.COMPETITIVE_PRICING:
            price = self._apply_competitive_pricing(converted_price, kwargs.get("competitor_prices", []))
        else:
            price = converted_price * (1 + markup_percentage / 100)
        
        # 心理定价
        if psychological_pricing:
            price = self._apply_psychological_pricing(price)
        
        # 四舍五入
        price = round(price, round_decimals)
        
        return price
    
    def _apply_psychological_pricing(self, price: float) -> float:
        """应用心理定价（如9.99, 19.99等）"""
        if price < 1:
            return price
        
        # 获取整数部分和小数部分
        integer_part = int(price)
        decimal_part = price - integer_part
        
        # 心理定价规则
        if integer_part >= 100:
            # 大额：取整减1（如100->99, 200->199）
            if decimal_part < 0.5:
                return float(integer_part - 1 + 0.99)
            else:
                return float(integer_part + 0.99)
        elif integer_part >= 10:
            # 中额：.99结尾
            return float(integer_part + 0.99)
        else:
            # 小额：.95或.99
            if decimal_part < 0.5:
                return float(integer_part - 0.05) if integer_part > 0 else 0.95
            else:
                return float(integer_part + 0.95)
    
    def _apply_tiered_pricing(self, base_price: float, tiers: List[Dict]) -> float:
        """应用阶梯定价"""
        if not tiers:
            return base_price * 1.3
        
        # 按数量排序
        sorted_tiers = sorted(tiers, key=lambda t: t.get("min_quantity", 0))
        
        # 默认使用第一档
        markup = sorted_tiers[0].get("markup_percentage", 30)
        return base_price * (1 + markup / 100)
    
    def _apply_competitive_pricing(self, base_price: float, competitor_prices: List[float]) -> float:
        """应用竞争定价"""
        if not competitor_prices:
            return base_price * 1.3
        
        avg_competitor = sum(competitor_prices) / len(competitor_prices)
        # 比竞争对手略低5%
        return avg_competitor * 0.95
    
    async def calculate_product_prices(
        self,
        product: Dict,
        base_currency: str,
        target_currency: str,
        **kwargs
    ) -> Dict:
        """计算产品的所有价格
        
        Args:
            product: 产品数据
            base_currency: 基础货币
            target_currency: 目标货币
        """
        result = product.copy()
        
        # 计算常规价格
        if "regular_price" in product and product["regular_price"]:
            result["regular_price"] = await self.calculate_price(
                float(product["regular_price"]),
                base_currency,
                target_currency,
                **kwargs
            )
        
        # 计算促销价格
        if "sale_price" in product and product["sale_price"]:
            result["sale_price"] = await self.calculate_price(
                float(product["sale_price"]),
                base_currency,
                target_currency,
                **kwargs
            )
        
        # 计算当前价格
        if "price" in product and product["price"]:
            result["price"] = await self.calculate_price(
                float(product["price"]),
                base_currency,
                target_currency,
                **kwargs
            )
        
        # 更新货币
        result["currency"] = target_currency
        
        return result
    
    def format_price(self, price: float, currency: str, locale: str = "zh_CN") -> str:
        """格式化价格显示"""
        currency_symbols = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "JPY": "¥",
            "CNY": "¥",
            "HKD": "HK$",
            "AUD": "A$",
            "CAD": "C$",
            "CHF": "CHF",
            "SGD": "S$",
            "KRW": "₩",
            "INR": "₹",
            "RUB": "₽",
            "BRL": "R$",
        }
        
        symbol = currency_symbols.get(currency, currency)
        
        # 格式化数字
        if locale.startswith("zh"):
            formatted = f"{price:,.2f}"
        else:
            formatted = f"{price:,.2f}"
        
        return f"{symbol}{formatted}"


class PriceOptimizer:
    """价格优化器"""
    
    def __init__(self):
        pass
    
    def optimize_prices(
        self,
        products: List[Dict],
        strategy: str = "balanced",
        target_margin: float = 30.0,
        min_margin: float = 15.0,
        max_margin: float = 50.0
    ) -> List[Dict]:
        """批量优化价格
        
        Args:
            products: 产品列表
            strategy: 优化策略: balanced, max_profit, max_volume
            target_margin: 目标利润率
            min_margin: 最低利润率
            max_margin: 最高利润率
        """
        optimized = []
        
        for product in products:
            optimized_product = product.copy()
            
            base_price = float(product.get("cost_price", product.get("price", 0)))
            
            if strategy == "balanced":
                # 平衡策略：目标利润率
                markup = target_margin
            elif strategy == "max_profit":
                # 利润最大化：最高利润率
                markup = max_margin
            elif strategy == "max_volume":
                # 销量最大化：最低利润率
                markup = min_margin
            else:
                markup = target_margin
            
            optimized_product["optimized_price"] = base_price * (1 + markup / 100)
            optimized_product["margin"] = markup
            
            optimized.append(optimized_product)
        
        return optimized
    
    def suggest_price(
        self,
        cost_price: float,
        competitor_prices: List[float],
        market_demand: str = "medium"
    ) -> Dict:
        """建议价格
        
        Args:
            cost_price: 成本价
            competitor_prices: 竞争对手价格
            market_demand: 市场需求: low, medium, high
        """
        if not competitor_prices:
            return {
                "suggested_price": cost_price * 1.5,
                "min_price": cost_price * 1.2,
                "max_price": cost_price * 2.0,
                "strategy": "default"
            }
        
        avg_competitor = sum(competitor_prices) / len(competitor_prices)
        min_competitor = min(competitor_prices)
        max_competitor = max(competitor_prices)
        
        # 根据市场需求调整
        if market_demand == "high":
            # 需求高，可以定价高一些
            suggested = avg_competitor * 1.05
        elif market_demand == "low":
            # 需求低，需要更有竞争力
            suggested = min_competitor * 0.95
        else:
            # 中等需求，略低于平均
            suggested = avg_competitor * 0.95
        
        # 确保有最低利润
        min_price = cost_price * 1.15
        if suggested < min_price:
            suggested = min_price
        
        return {
            "suggested_price": round(suggested, 2),
            "min_price": round(max(min_price, cost_price * 1.1), 2),
            "max_price": round(max_competitor * 1.1, 2),
            "avg_competitor": round(avg_competitor, 2),
            "strategy": "competitive_based"
        }


# 全局实例
exchange_rate_service = ExchangeRateService()
price_calculator = PriceCalculator()
price_optimizer = PriceOptimizer()
