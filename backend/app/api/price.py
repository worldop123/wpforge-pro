"""
API路由 - 价格与汇率相关接口
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.services.price_service import (
    exchange_rate_service,
    price_calculator,
    price_optimizer,
    PriceStrategy
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/price", tags=["价格管理"])


class PriceCalculateRequest(BaseModel):
    """价格计算请求"""
    base_price: float
    base_currency: str = "USD"
    target_currency: str = "CNY"
    strategy: str = "percentage_markup"
    markup_percentage: float = 30.0
    markup_fixed: float = 0.0
    psychological_pricing: bool = True
    round_decimals: int = 2


class ProductPriceRequest(BaseModel):
    """产品价格计算请求"""
    product: Dict
    base_currency: str = "USD"
    target_currency: str = "CNY"
    strategy: str = "percentage_markup"
    markup_percentage: float = 30.0
    psychological_pricing: bool = True


class PriceOptimizeRequest(BaseModel):
    """价格优化请求"""
    products: List[Dict]
    strategy: str = "balanced"
    target_margin: float = 30.0
    min_margin: float = 15.0
    max_margin: float = 50.0


@router.get("/exchange-rate")
async def get_exchange_rate(from_currency: str = "USD", to_currency: str = "CNY"):
    """获取汇率"""
    try:
        rate = await exchange_rate_service.get_rate(from_currency, to_currency)
        
        return {
            "base_currency": rate.base_currency,
            "target_currency": rate.target_currency,
            "rate": rate.rate,
            "timestamp": rate.timestamp,
            "source": rate.source
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取汇率失败: {str(e)}")


@router.get("/exchange-rates")
async def get_exchange_rates(base_currency: str = "USD", targets: str = "CNY,EUR,GBP,JPY"):
    """获取多个汇率"""
    try:
        target_currencies = targets.split(",")
        rates = {}
        
        for target in target_currencies:
            rate = await exchange_rate_service.get_rate(base_currency, target.strip())
            rates[target.strip()] = {
                "rate": rate.rate,
                "timestamp": rate.timestamp,
                "source": rate.source
            }
        
        return {
            "base_currency": base_currency,
            "rates": rates
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取汇率失败: {str(e)}")


@router.post("/calculate")
async def calculate_price(request: PriceCalculateRequest):
    """计算价格"""
    try:
        strategy = PriceStrategy(request.strategy)
        
        price = await price_calculator.calculate_price(
            base_price=request.base_price,
            base_currency=request.base_currency,
            target_currency=request.target_currency,
            strategy=strategy,
            markup_percentage=request.markup_percentage,
            markup_fixed=request.markup_fixed,
            psychological_pricing=request.psychological_pricing,
            round_decimals=request.round_decimals
        )
        
        # 获取汇率
        rate = await exchange_rate_service.get_rate(request.base_currency, request.target_currency)
        
        return {
            "base_price": request.base_price,
            "base_currency": request.base_currency,
            "target_price": price,
            "target_currency": request.target_currency,
            "exchange_rate": rate.rate,
            "strategy": request.strategy,
            "markup_percentage": request.markup_percentage,
            "psychological_pricing": request.psychological_pricing
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"价格计算失败: {str(e)}")


@router.post("/product")
async def calculate_product_prices(request: ProductPriceRequest):
    """计算产品价格"""
    try:
        strategy = PriceStrategy(request.strategy)
        
        result = await price_calculator.calculate_product_prices(
            product=request.product,
            base_currency=request.base_currency,
            target_currency=request.target_currency,
            strategy=strategy,
            markup_percentage=request.markup_percentage,
            psychological_pricing=request.psychological_pricing
        )
        
        return {
            "original": request.product,
            "calculated": result,
            "base_currency": request.base_currency,
            "target_currency": request.target_currency,
            "strategy": request.strategy
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"产品价格计算失败: {str(e)}")


@router.post("/optimize")
async def optimize_prices(request: PriceOptimizeRequest):
    """优化价格"""
    try:
        optimized = price_optimizer.optimize_prices(
            products=request.products,
            strategy=request.strategy,
            target_margin=request.target_margin,
            min_margin=request.min_margin,
            max_margin=request.max_margin
        )
        
        return {
            "total": len(optimized),
            "strategy": request.strategy,
            "target_margin": request.target_margin,
            "products": optimized
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"价格优化失败: {str(e)}")


@router.get("/strategies")
async def get_pricing_strategies():
    """获取定价策略"""
    strategies = [
        {
            "id": "percentage_markup",
            "name": "百分比加价",
            "description": "按成本价的百分比加价",
            "default_markup": 30
        },
        {
            "id": "fixed_markup",
            "name": "固定加价",
            "description": "按固定金额加价",
            "default_markup": 10
        },
        {
            "id": "tiered_pricing",
            "name": "阶梯定价",
            "description": "根据数量阶梯定价",
            "default_markup": 25
        },
        {
            "id": "competitive_pricing",
            "name": "竞争定价",
            "description": "基于竞争对手价格定价",
            "default_markup": 20
        },
        {
            "id": "psychological_pricing",
            "name": "心理定价",
            "description": "使用.99等心理价位",
            "default_markup": 30
        }
    ]
    
    return {
        "strategies": strategies,
        "default": "percentage_markup"
    }


@router.get("/currencies")
async def get_supported_currencies():
    """获取支持的货币"""
    currencies = [
        {"code": "USD", "name": "美元", "symbol": "$"},
        {"code": "EUR", "name": "欧元", "symbol": "€"},
        {"code": "GBP", "name": "英镑", "symbol": "£"},
        {"code": "JPY", "name": "日元", "symbol": "¥"},
        {"code": "CNY", "name": "人民币", "symbol": "¥"},
        {"code": "HKD", "name": "港币", "symbol": "HK$"},
        {"code": "AUD", "name": "澳元", "symbol": "A$"},
        {"code": "CAD", "name": "加元", "symbol": "C$"},
        {"code": "CHF", "name": "瑞士法郎", "symbol": "CHF"},
        {"code": "SGD", "name": "新加坡元", "symbol": "S$"},
        {"code": "KRW", "name": "韩元", "symbol": "₩"},
        {"code": "INR", "name": "印度卢比", "symbol": "₹"},
        {"code": "RUB", "name": "俄罗斯卢布", "symbol": "₽"},
        {"code": "BRL", "name": "巴西雷亚尔", "symbol": "R$"},
        {"code": "ZAR", "name": "南非兰特", "symbol": "R"},
        {"code": "MXN", "name": "墨西哥比索", "symbol": "Mex$"},
        {"code": "PLN", "name": "波兰兹罗提", "symbol": "zł"},
        {"code": "SEK", "name": "瑞典克朗", "symbol": "kr"},
        {"code": "NOK", "name": "挪威克朗", "symbol": "kr"},
        {"code": "DKK", "name": "丹麦克朗", "symbol": "kr"},
        {"code": "CZK", "name": "捷克克朗", "symbol": "Kč"},
        {"code": "HUF", "name": "匈牙利福林", "symbol": "Ft"},
        {"code": "RON", "name": "罗马尼亚列伊", "symbol": "lei"},
        {"code": "TRY", "name": "土耳其里拉", "symbol": "₺"},
        {"code": "THB", "name": "泰铢", "symbol": "฿"},
        {"code": "MYR", "name": "马来西亚林吉特", "symbol": "RM"},
        {"code": "IDR", "name": "印尼盾", "symbol": "Rp"},
        {"code": "PHP", "name": "菲律宾比索", "symbol": "₱"},
        {"code": "VND", "name": "越南盾", "symbol": "₫"},
    ]
    
    return {
        "total": len(currencies),
        "currencies": currencies
    }


@router.get("/cache/stats")
async def get_exchange_cache_stats():
    """获取汇率缓存统计"""
    stats = exchange_rate_service.get_cache_stats()
    return stats


@router.post("/cache/clear")
async def clear_exchange_cache():
    """清除汇率缓存"""
    exchange_rate_service.clear_cache()
    return {"success": True, "message": "汇率缓存已清除"}
