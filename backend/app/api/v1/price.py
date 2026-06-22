"""
价格API - 智能价格引擎
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas import (
    PriceCalculateRequest,
    PriceCalculateResponse,
    SuccessResponse,
)

router = APIRouter(prefix="/price", tags=["智能价格"])


@router.post("/calculate", response_model=PriceCalculateResponse)
async def calculate_price(
    request: PriceCalculateRequest,
    current_user: User = Depends(get_current_user),
):
    """计算价格"""
    try:
        from app.services.price_service import price_calculator
        
        final_price = await price_calculator.calculate_price(
            base_price=request.base_price,
            base_currency=request.base_currency,
            target_currency=request.target_currency,
            strategy=request.strategy,
            markup_percentage=request.markup_percentage,
            markup_fixed=request.markup_fixed,
            psychological_pricing=request.psychological_pricing,
        )
        
        # 获取汇率信息
        from app.services.price_service import exchange_rate_service
        rate = await exchange_rate_service.get_rate(
            request.base_currency,
            request.target_currency
        )
        
        return PriceCalculateResponse(
            base_price=request.base_price,
            base_currency=request.base_currency,
            target_currency=request.target_currency,
            exchange_rate=rate.rate,
            final_price=final_price,
            strategy=request.strategy,
            markup_percentage=request.markup_percentage,
            psychological_pricing=request.psychological_pricing,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"价格计算失败: {str(e)}"
        )


@router.post("/batch-calculate", response_model=SuccessResponse)
async def batch_calculate_prices(
    products: List[dict],
    base_currency: str = "USD",
    target_currency: str = "EUR",
    markup_percentage: float = 30.0,
    psychological_pricing: bool = True,
    current_user: User = Depends(get_current_user),
):
    """批量计算产品价格"""
    try:
        from app.services.price_service import price_calculator
        
        results = []
        
        for product in products:
            result = await price_calculator.calculate_product_prices(
                product=product,
                base_currency=base_currency,
                target_currency=target_currency,
                markup_percentage=markup_percentage,
                psychological_pricing=psychological_pricing,
            )
            results.append(result)
        
        return SuccessResponse(
            message="批量价格计算完成",
            data={
                "total": len(results),
                "products": results,
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量计算失败: {str(e)}"
        )


@router.get("/exchange-rate", response_model=SuccessResponse)
async def get_exchange_rate(
    base_currency: str = "USD",
    target_currency: str = "EUR",
    current_user: User = Depends(get_current_user),
):
    """获取汇率"""
    try:
        from app.services.price_service import exchange_rate_service
        
        rate = await exchange_rate_service.get_rate(base_currency, target_currency)
        
        return SuccessResponse(
            message="获取汇率成功",
            data={
                "base_currency": rate.base_currency,
                "target_currency": rate.target_currency,
                "rate": rate.rate,
                "source": rate.source,
                "timestamp": rate.timestamp,
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取汇率失败: {str(e)}"
        )


@router.get("/exchange-rates", response_model=SuccessResponse)
async def get_exchange_rates(
    base_currency: str = "USD",
    current_user: User = Depends(get_current_user),
):
    """获取常用货币汇率"""
    try:
        from app.services.price_service import exchange_rate_service
        
        target_currencies = ["EUR", "GBP", "JPY", "CNY", "HKD", "AUD", "CAD", "CHF", "SGD", "KRW"]
        rates = {}
        
        for target in target_currencies:
            rate = await exchange_rate_service.get_rate(base_currency, target)
            rates[target] = {
                "rate": rate.rate,
                "source": rate.source,
            }
        
        return SuccessResponse(
            message="获取汇率成功",
            data={
                "base_currency": base_currency,
                "rates": rates,
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取汇率失败: {str(e)}"
        )


@router.get("/strategies", response_model=SuccessResponse)
async def get_pricing_strategies(
    current_user: User = Depends(get_current_user),
):
    """获取定价策略列表"""
    strategies = [
        {
            "id": "percentage_markup",
            "name": "百分比加价",
            "description": "按成本价的百分比加价，简单易用",
            "use_case": "大多数常规产品",
            "params": ["markup_percentage"],
        },
        {
            "id": "fixed_markup",
            "name": "固定加价",
            "description": "固定金额加价，适合低价产品",
            "use_case": "低价小商品",
            "params": ["markup_fixed"],
        },
        {
            "id": "tiered_pricing",
            "name": "阶梯定价",
            "description": "根据价格区间不同加价比例",
            "use_case": "价格区间大的产品",
            "params": ["tiers"],
        },
        {
            "id": "competitive_pricing",
            "name": "竞争定价",
            "description": "基于竞争对手价格定价",
            "use_case": "竞争激烈的市场",
            "params": ["competitor_prices"],
        },
        {
            "id": "psychological_pricing",
            "name": "心理定价",
            "description": "9.99、19.99等心理价位",
            "use_case": "零售产品",
            "params": [],
        },
    ]
    
    return SuccessResponse(
        message="获取成功",
        data={"strategies": strategies}
    )


@router.post("/optimize", response_model=SuccessResponse)
async def optimize_prices(
    products: List[dict],
    strategy: str = "balanced",
    target_margin: float = 30.0,
    min_margin: float = 15.0,
    max_margin: float = 50.0,
    current_user: User = Depends(get_current_user),
):
    """批量优化价格"""
    try:
        from app.services.price_service import price_optimizer
        
        optimized = price_optimizer.optimize_prices(
            products=products,
            strategy=strategy,
            target_margin=target_margin,
            min_margin=min_margin,
            max_margin=max_margin,
        )
        
        return SuccessResponse(
            message="价格优化完成",
            data={
                "total": len(optimized),
                "strategy": strategy,
                "products": optimized,
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"价格优化失败: {str(e)}"
        )


@router.post("/suggest", response_model=SuccessResponse)
async def suggest_price(
    cost_price: float,
    competitor_prices: List[float],
    market_demand: str = "medium",
    current_user: User = Depends(get_current_user),
):
    """建议价格"""
    try:
        from app.services.price_service import price_optimizer
        
        suggestion = price_optimizer.suggest_price(
            cost_price=cost_price,
            competitor_prices=competitor_prices,
            market_demand=market_demand,
        )
        
        return SuccessResponse(
            message="价格建议生成成功",
            data=suggestion
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成建议失败: {str(e)}"
        )


@router.get("/currencies", response_model=SuccessResponse)
async def get_supported_currencies(
    current_user: User = Depends(get_current_user),
):
    """获取支持的货币列表"""
    currencies = [
        {"code": "USD", "name": "美元", "symbol": "$", "country": "美国"},
        {"code": "EUR", "name": "欧元", "symbol": "€", "country": "欧盟"},
        {"code": "GBP", "name": "英镑", "symbol": "£", "country": "英国"},
        {"code": "JPY", "name": "日元", "symbol": "¥", "country": "日本"},
        {"code": "CNY", "name": "人民币", "symbol": "¥", "country": "中国"},
        {"code": "HKD", "name": "港币", "symbol": "HK$", "country": "香港"},
        {"code": "AUD", "name": "澳元", "symbol": "A$", "country": "澳大利亚"},
        {"code": "CAD", "name": "加元", "symbol": "C$", "country": "加拿大"},
        {"code": "CHF", "name": "瑞郎", "symbol": "CHF", "country": "瑞士"},
        {"code": "SGD", "name": "新加坡元", "symbol": "S$", "country": "新加坡"},
        {"code": "KRW", "name": "韩元", "symbol": "₩", "country": "韩国"},
        {"code": "INR", "name": "印度卢比", "symbol": "₹", "country": "印度"},
        {"code": "RUB", "name": "卢布", "symbol": "₽", "country": "俄罗斯"},
        {"code": "BRL", "name": "雷亚尔", "symbol": "R$", "country": "巴西"},
        {"code": "ZAR", "name": "兰特", "symbol": "R", "country": "南非"},
        {"code": "MXN", "name": "比索", "symbol": "$", "country": "墨西哥"},
        {"code": "PLN", "name": "兹罗提", "symbol": "zł", "country": "波兰"},
        {"code": "SEK", "name": "瑞典克朗", "symbol": "kr", "country": "瑞典"},
        {"code": "NOK", "name": "挪威克朗", "symbol": "kr", "country": "挪威"},
        {"code": "DKK", "name": "丹麦克朗", "symbol": "kr", "country": "丹麦"},
        {"code": "CZK", "name": "捷克克朗", "symbol": "Kč", "country": "捷克"},
        {"code": "HUF", "name": "福林", "symbol": "Ft", "country": "匈牙利"},
        {"code": "RON", "name": "列伊", "symbol": "lei", "country": "罗马尼亚"},
        {"code": "TRY", "name": "里拉", "symbol": "₺", "country": "土耳其"},
        {"code": "THB", "name": "泰铢", "symbol": "฿", "country": "泰国"},
        {"code": "MYR", "name": "林吉特", "symbol": "RM", "country": "马来西亚"},
        {"code": "IDR", "name": "印尼盾", "symbol": "Rp", "country": "印度尼西亚"},
        {"code": "PHP", "name": "比索", "symbol": "₱", "country": "菲律宾"},
        {"code": "VND", "name": "越南盾", "symbol": "₫", "country": "越南"},
    ]
    
    return SuccessResponse(
        message="获取成功",
        data={"currencies": currencies}
    )
