"""
代理管理服务 - 支持多种代理协议、代理池管理、自动轮换
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import random
import time
import httpx
from enum import Enum
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ProxyProtocol(str, Enum):
    """代理协议类型"""
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


class ProxyQuality(str, Enum):
    """代理质量等级"""
    PREMIUM = "premium"
    STANDARD = "standard"
    BASIC = "basic"
    UNKNOWN = "unknown"


@dataclass
class Proxy:
    """代理配置"""
    host: str
    port: int
    protocol: ProxyProtocol = ProxyProtocol.HTTP
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    isp: Optional[str] = None
    quality: ProxyQuality = ProxyQuality.UNKNOWN
    speed: float = 0.0  # 响应时间（秒）
    success_rate: float = 1.0  # 成功率
    last_used: float = 0.0
    total_uses: int = 0
    failed_uses: int = 0
    is_alive: bool = True
    provider: Optional[str] = None  # 代理服务商
    
    @property
    def url(self) -> str:
        """获取代理URL"""
        auth = ""
        if self.username and self.password:
            auth = f"{self.username}:{self.password}@"
        
        return f"{self.protocol.value}://{auth}{self.host}:{self.port}"
    
    @property
    def score(self) -> float:
        """计算代理综合评分"""
        speed_score = max(0, 1 - self.speed / 10)  # 速度评分，越慢分越低
        success_score = self.success_rate
        quality_score = {
            ProxyQuality.PREMIUM: 1.0,
            ProxyQuality.STANDARD: 0.7,
            ProxyQuality.BASIC: 0.4,
            ProxyQuality.UNKNOWN: 0.5,
        }.get(self.quality, 0.5)
        
        return (speed_score * 0.3 + success_score * 0.4 + quality_score * 0.3)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "host": self.host,
            "port": self.port,
            "protocol": self.protocol.value,
            "username": self.username,
            "password": self.password,
            "country": self.country,
            "city": self.city,
            "isp": self.isp,
            "quality": self.quality.value,
            "speed": self.speed,
            "success_rate": self.success_rate,
            "is_alive": self.is_alive,
            "provider": self.provider,
        }


class ProxyPool:
    """代理池管理器"""
    
    def __init__(self):
        self.proxies: List[Proxy] = []
        self.current_index: int = 0
        self._lock = False
    
    def add_proxy(self, proxy: Proxy) -> None:
        """添加代理"""
        self.proxies.append(proxy)
        logger.info(f"Added proxy: {proxy.host}:{proxy.port}")
    
    def add_proxies(self, proxies: List[Proxy]) -> None:
        """批量添加代理"""
        self.proxies.extend(proxies)
        logger.info(f"Added {len(proxies)} proxies, total: {len(self.proxies)}")
    
    def remove_proxy(self, host: str, port: int) -> bool:
        """移除代理"""
        for i, proxy in enumerate(self.proxies):
            if proxy.host == host and proxy.port == port:
                self.proxies.pop(i)
                return True
        return False
    
    def get_proxy(
        self,
        country: Optional[str] = None,
        protocol: Optional[ProxyProtocol] = None,
        min_quality: Optional[ProxyQuality] = None,
        strategy: str = "round_robin"
    ) -> Optional[Proxy]:
        """获取代理
        
        Args:
            country: 国家过滤
            protocol: 协议过滤
            min_quality: 最低质量要求
            strategy: 选择策略: round_robin, random, best_score, least_used
        """
        # 过滤可用代理
        available = [p for p in self.proxies if p.is_alive]
        
        if country:
            available = [p for p in available if p.country == country]
        
        if protocol:
            available = [p for p in available if p.protocol == protocol]
        
        if min_quality:
            quality_order = [ProxyQuality.PREMIUM, ProxyQuality.STANDARD, ProxyQuality.BASIC, ProxyQuality.UNKNOWN]
            min_idx = quality_order.index(min_quality)
            available = [p for p in available if quality_order.index(p.quality) <= min_idx]
        
        if not available:
            return None
        
        if strategy == "round_robin":
            proxy = available[self.current_index % len(available)]
            self.current_index = (self.current_index + 1) % len(available)
        elif strategy == "random":
            proxy = random.choice(available)
        elif strategy == "best_score":
            proxy = max(available, key=lambda p: p.score)
        elif strategy == "least_used":
            proxy = min(available, key=lambda p: p.total_uses)
        else:
            proxy = available[0]
        
        proxy.last_used = time.time()
        proxy.total_uses += 1
        
        return proxy
    
    def mark_failed(self, proxy: Proxy) -> None:
        """标记代理失败"""
        proxy.failed_uses += 1
        proxy.success_rate = 1 - (proxy.failed_uses / max(1, proxy.total_uses))
        
        # 连续失败太多次，标记为不可用
        if proxy.failed_uses >= 5 and proxy.success_rate < 0.3:
            proxy.is_alive = False
            logger.warning(f"Proxy {proxy.host}:{proxy.port} marked as dead")
    
    def mark_success(self, proxy: Proxy, response_time: float) -> None:
        """标记代理成功"""
        proxy.speed = (proxy.speed * 0.7 + response_time * 0.3)  # 平滑更新
        proxy.success_rate = 1 - (proxy.failed_uses / max(1, proxy.total_uses))
    
    async def check_proxy(self, proxy: Proxy, test_url: str = "https://httpbin.org/ip", timeout: float = 10.0) -> bool:
        """检测代理是否可用"""
        try:
            start = time.time()
            async with httpx.AsyncClient(
                proxy=proxy.url,
                timeout=timeout,
                follow_redirects=True
            ) as client:
                response = await client.get(test_url)
                if response.status_code == 200:
                    proxy.speed = time.time() - start
                    proxy.is_alive = True
                    return True
        except Exception as e:
            logger.debug(f"Proxy check failed for {proxy.host}:{proxy.port}: {e}")
        
        proxy.is_alive = False
        return False
    
    async def check_all_proxies(self) -> Tuple[int, int]:
        """检测所有代理可用性
        
        Returns:
            (alive_count, dead_count)
        """
        alive = 0
        dead = 0
        
        for proxy in self.proxies:
            if await self.check_proxy(proxy):
                alive += 1
            else:
                dead += 1
        
        logger.info(f"Proxy check complete: {alive} alive, {dead} dead")
        return alive, dead
    
    def get_stats(self) -> Dict:
        """获取代理池统计"""
        alive = sum(1 for p in self.proxies if p.is_alive)
        dead = len(self.proxies) - alive
        
        by_country = {}
        by_protocol = {}
        by_quality = {}
        
        for proxy in self.proxies:
            if proxy.country:
                by_country[proxy.country] = by_country.get(proxy.country, 0) + 1
            by_protocol[proxy.protocol.value] = by_protocol.get(proxy.protocol.value, 0) + 1
            by_quality[proxy.quality.value] = by_quality.get(proxy.quality.value, 0) + 1
        
        return {
            "total": len(self.proxies),
            "alive": alive,
            "dead": dead,
            "by_country": by_country,
            "by_protocol": by_protocol,
            "by_quality": by_quality,
        }


class BrightDataProvider:
    """BrightData 代理服务商对接"""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
    
    def get_residential_proxy(self, country: Optional[str] = None) -> Proxy:
        """获取住宅代理"""
        host = "zproxy.lum-superproxy.io"
        port = 22225
        
        username = self.username
        if country:
            username = f"{self.username}-country-{country.lower()}"
        
        return Proxy(
            host=host,
            port=port,
            protocol=ProxyProtocol.HTTP,
            username=username,
            password=self.password,
            country=country,
            quality=ProxyQuality.PREMIUM,
            provider="brightdata"
        )
    
    def get_datacenter_proxy(self, country: Optional[str] = None) -> Proxy:
        """获取数据中心代理"""
        host = "zproxy.lum-superproxy.io"
        port = 22225
        
        username = f"{self.username}-datacenter"
        if country:
            username = f"{username}-country-{country.lower()}"
        
        return Proxy(
            host=host,
            port=port,
            protocol=ProxyProtocol.HTTP,
            username=username,
            password=self.password,
            country=country,
            quality=ProxyQuality.STANDARD,
            provider="brightdata"
        )


class OxylabsProvider:
    """Oxylabs 代理服务商对接"""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
    
    def get_residential_proxy(self, country: Optional[str] = None) -> Proxy:
        """获取住宅代理"""
        host = "pr.oxylabs.io"
        port = 7777
        
        username = self.username
        if country:
            username = f"{self.username}-cc-{country.lower()}"
        
        return Proxy(
            host=host,
            port=port,
            protocol=ProxyProtocol.HTTP,
            username=username,
            password=self.password,
            country=country,
            quality=ProxyQuality.PREMIUM,
            provider="oxylabs"
        )


class SmartproxyProvider:
    """Smartproxy 代理服务商对接"""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
    
    def get_residential_proxy(self, country: Optional[str] = None) -> Proxy:
        """获取住宅代理"""
        if country:
            host = f"{country.lower()}.smartproxy.com"
        else:
            host = "gate.smartproxy.com"
        
        port = 10000
        
        return Proxy(
            host=host,
            port=port,
            protocol=ProxyProtocol.HTTP,
            username=self.username,
            password=self.password,
            country=country,
            quality=ProxyQuality.PREMIUM,
            provider="smartproxy"
        )


# 全局代理池实例
proxy_pool = ProxyPool()


def init_proxy_pool(proxies_config: Optional[List[Dict]] = None):
    """初始化代理池"""
    if proxies_config:
        for config in proxies_config:
            proxy = Proxy(
                host=config["host"],
                port=config["port"],
                protocol=ProxyProtocol(config.get("protocol", "http")),
                username=config.get("username"),
                password=config.get("password"),
                country=config.get("country"),
                quality=ProxyQuality(config.get("quality", "unknown")),
                provider=config.get("provider")
            )
            proxy_pool.add_proxy(proxy)
    
    logger.info(f"Proxy pool initialized with {len(proxy_pool.proxies)} proxies")
