"""
代理API - 动态代理系统管理
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas import SuccessResponse

router = APIRouter(prefix="/proxy", tags=["代理管理"])


@router.get("/providers", response_model=SuccessResponse)
async def get_proxy_providers(
    current_user: User = Depends(get_current_user),
):
    """获取代理服务商列表"""
    providers = [
        {
            "id": "brightdata",
            "name": "BrightData",
            "description": "全球最大的住宅代理网络",
            "types": ["residential", "datacenter", "mobile", "isp"],
            "countries": 195,
            "status": "supported",
        },
        {
            "id": "oxylabs",
            "name": "Oxylabs",
            "description": "企业级代理解决方案",
            "types": ["residential", "datacenter", "mobile"],
            "countries": 195,
            "status": "supported",
        },
        {
            "id": "smartproxy",
            "name": "Smartproxy",
            "description": "高性价比住宅代理",
            "types": ["residential", "datacenter"],
            "countries": 195,
            "status": "supported",
        },
        {
            "id": "iproyal",
            "name": "IPRoyal",
            "description": "多种代理类型选择",
            "types": ["residential", "datacenter", "sneaker"],
            "countries": 195,
            "status": "supported",
        },
        {
            "id": "netnut",
            "name": "NetNut",
            "description": "ISP代理专家",
            "types": ["residential", "isp", "datacenter"],
            "countries": 195,
            "status": "supported",
        },
        {
            "id": "custom",
            "name": "自定义代理",
            "description": "支持HTTP/HTTPS/SOCKS5代理",
            "types": ["http", "https", "socks4", "socks5"],
            "countries": 0,
            "status": "supported",
        },
    ]
    
    return SuccessResponse(
        message="获取成功",
        data={"providers": providers}
    )


@router.get("/pool/stats", response_model=SuccessResponse)
async def get_proxy_pool_stats(
    current_user: User = Depends(get_current_user),
):
    """获取代理池统计"""
    try:
        from app.services.proxy_service import proxy_pool
        
        stats = proxy_pool.get_stats()
        
        return SuccessResponse(
            message="获取成功",
            data=stats
        )
        
    except Exception as e:
        # 返回默认统计
        return SuccessResponse(
            message="获取成功",
            data={
                "total": 0,
                "alive": 0,
                "dead": 0,
                "by_country": {},
                "by_protocol": {},
                "by_quality": {},
            }
        )


@router.post("/add", response_model=SuccessResponse)
async def add_proxy(
    host: str,
    port: int,
    protocol: str = "http",
    username: str = None,
    password: str = None,
    country: str = None,
    provider: str = "custom",
    current_user: User = Depends(get_current_user),
):
    """添加代理"""
    try:
        from app.services.proxy_service import proxy_pool, Proxy, ProxyProtocol, ProxyQuality
        
        proxy = Proxy(
            host=host,
            port=port,
            protocol=ProxyProtocol(protocol),
            username=username,
            password=password,
            country=country,
            quality=ProxyQuality.UNKNOWN,
            provider=provider,
        )
        
        proxy_pool.add_proxy(proxy)
        
        return SuccessResponse(
            message="代理添加成功",
            data={"proxy": proxy.to_dict()}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加失败: {str(e)}"
        )


@router.post("/batch-add", response_model=SuccessResponse)
async def batch_add_proxies(
    proxies: List[dict],
    current_user: User = Depends(get_current_user),
):
    """批量添加代理"""
    try:
        from app.services.proxy_service import proxy_pool, Proxy, ProxyProtocol, ProxyQuality
        
        added = 0
        for p in proxies:
            proxy = Proxy(
                host=p["host"],
                port=p["port"],
                protocol=ProxyProtocol(p.get("protocol", "http")),
                username=p.get("username"),
                password=p.get("password"),
                country=p.get("country"),
                quality=ProxyQuality(p.get("quality", "unknown")),
                provider=p.get("provider", "custom"),
            )
            proxy_pool.add_proxy(proxy)
            added += 1
        
        return SuccessResponse(
            message=f"成功添加 {added} 个代理",
            data={"added": added}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量添加失败: {str(e)}"
        )


@router.post("/check", response_model=SuccessResponse)
async def check_proxies(
    current_user: User = Depends(get_current_user),
):
    """检测所有代理可用性"""
    try:
        from app.services.proxy_service import proxy_pool
        
        alive, dead = await proxy_pool.check_all_proxies()
        
        return SuccessResponse(
            message="代理检测完成",
            data={"alive": alive, "dead": dead}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"检测失败: {str(e)}"
        )


@router.get("/list", response_model=SuccessResponse)
async def list_proxies(
    country: str = None,
    protocol: str = None,
    status_filter: str = None,
    current_user: User = Depends(get_current_user),
):
    """获取代理列表"""
    try:
        from app.services.proxy_service import proxy_pool
        
        proxies = proxy_pool.proxies
        
        # 过滤
        if country:
            proxies = [p for p in proxies if p.country == country]
        
        if protocol:
            from app.services.proxy_service import ProxyProtocol
            proxies = [p for p in proxies if p.protocol == ProxyProtocol(protocol)]
        
        if status_filter == "alive":
            proxies = [p for p in proxies if p.is_alive]
        elif status_filter == "dead":
            proxies = [p for p in proxies if not p.is_alive]
        
        return SuccessResponse(
            message="获取成功",
            data={
                "total": len(proxies),
                "proxies": [p.to_dict() for p in proxies]
            }
        )
        
    except Exception as e:
        return SuccessResponse(
            message="获取成功",
            data={"total": 0, "proxies": []}
        )


@router.delete("/{proxy_id}", response_model=SuccessResponse)
async def remove_proxy(
    proxy_id: int,
    current_user: User = Depends(get_current_user),
):
    """移除代理"""
    try:
        from app.services.proxy_service import proxy_pool
        
        if 0 <= proxy_id < len(proxy_pool.proxies):
            proxy = proxy_pool.proxies.pop(proxy_id)
            return SuccessResponse(
                message="代理已移除",
                data={"host": proxy.host, "port": proxy.port}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="代理不存在"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"移除失败: {str(e)}"
        )


@router.get("/strategies", response_model=SuccessResponse)
async def get_proxy_strategies(
    current_user: User = Depends(get_current_user),
):
    """获取代理选择策略"""
    strategies = [
        {
            "id": "round_robin",
            "name": "轮询",
            "description": "按顺序轮流使用代理",
            "use_case": "通用场景",
        },
        {
            "id": "random",
            "name": "随机",
            "description": "随机选择代理",
            "use_case": "需要随机性的场景",
        },
        {
            "id": "best_score",
            "name": "最优评分",
            "description": "选择综合评分最高的代理",
            "use_case": "追求稳定性的场景",
        },
        {
            "id": "least_used",
            "name": "最少使用",
            "description": "选择使用次数最少的代理",
            "use_case": "均衡使用所有代理",
        },
    ]
    
    return SuccessResponse(
        message="获取成功",
        data={"strategies": strategies}
    )


@router.get("/countries", response_model=SuccessResponse)
async def get_supported_countries(
    current_user: User = Depends(get_current_user),
):
    """获取支持的国家列表"""
    countries = [
        {"code": "US", "name": "美国", "flag": "🇺🇸"},
        {"code": "GB", "name": "英国", "flag": "🇬🇧"},
        {"code": "DE", "name": "德国", "flag": "🇩🇪"},
        {"code": "FR", "name": "法国", "flag": "🇫🇷"},
        {"code": "JP", "name": "日本", "flag": "🇯🇵"},
        {"code": "KR", "name": "韩国", "flag": "🇰🇷"},
        {"code": "CN", "name": "中国", "flag": "🇨🇳"},
        {"code": "HK", "name": "香港", "flag": "🇭🇰"},
        {"code": "SG", "name": "新加坡", "flag": "🇸🇬"},
        {"code": "AU", "name": "澳大利亚", "flag": "🇦🇺"},
        {"code": "CA", "name": "加拿大", "flag": "🇨🇦"},
        {"code": "BR", "name": "巴西", "flag": "🇧🇷"},
        {"code": "IN", "name": "印度", "flag": "🇮🇳"},
        {"code": "RU", "name": "俄罗斯", "flag": "🇷🇺"},
        {"code": "IT", "name": "意大利", "flag": "🇮🇹"},
        {"code": "ES", "name": "西班牙", "flag": "🇪🇸"},
        {"code": "NL", "name": "荷兰", "flag": "🇳🇱"},
        {"code": "SE", "name": "瑞典", "flag": "🇸🇪"},
        {"code": "PL", "name": "波兰", "flag": "🇵🇱"},
        {"code": "CH", "name": "瑞士", "flag": "🇨🇭"},
    ]
    
    return SuccessResponse(
        message="获取成功",
        data={"countries": countries}
    )
