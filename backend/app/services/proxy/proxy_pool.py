"""
动态代理系统
支持多供应商适配：BrightData / Oxylabs / Smartproxy / 自建代理池
"""
import random
import time
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
from app.core.logging import get_logger

# 用于代理健康检查，按需导入（缺失时降级为跳过健康检查）
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    httpx = None

logger = get_logger(__name__)


class ProxyProvider(str, Enum):
    """代理供应商"""
    BRIGHTDATA = "brightdata"
    OXYLABS = "oxylabs"
    SMARTPROXY = "smartproxy"
    WEBSHARE = "webshare"
    SELF_HOSTED = "self_hosted"
    FREE = "free"


class ProxyProtocol(str, Enum):
    """代理协议"""
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


class ProxyType(str, Enum):
    """代理类型"""
    DATACENTER = "datacenter"
    RESIDENTIAL = "residential"
    MOBILE = "mobile"
    ISP = "isp"


class ProxyStatus(str, Enum):
    """代理状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class Proxy:
    """代理数据类"""
    id: str
    provider: ProxyProvider
    protocol: ProxyProtocol
    type: ProxyType
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    asn: Optional[str] = None
    status: ProxyStatus = ProxyStatus.ACTIVE
    success_count: int = 0
    fail_count: int = 0
    total_requests: int = 0
    avg_response_time: float = 0.0
    last_used: Optional[float] = None
    last_checked: Optional[float] = None
    last_banned: Optional[float] = None
    banned_domains: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_requests == 0:
            return 1.0
        return self.success_count / self.total_requests
    
    @property
    def url(self) -> str:
        """获取代理URL"""
        if self.username and self.password:
            return f"{self.protocol.value}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol.value}://{self.host}:{self.port}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "provider": self.provider.value,
            "protocol": self.protocol.value,
            "type": self.type.value,
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "country": self.country,
            "city": self.city,
            "status": self.status.value,
            "success_rate": self.success_rate,
            "avg_response_time": self.avg_response_time,
        }


@dataclass
class ProxyPoolConfig:
    """代理池配置"""
    # 轮换策略
    rotation_strategy: str = "round_robin"  # round_robin, random, least_used, fastest
    
    # 健康检查
    health_check_enabled: bool = True
    health_check_interval: int = 300  # 秒
    health_check_timeout: int = 10  # 秒
    health_check_url: str = "https://httpbin.org/ip"
    
    # 失败处理
    max_failures: int = 5
    failure_cooldown: int = 300  # 秒
    auto_recover: bool = True
    
    # 限速
    rate_limit_per_proxy: int = 60  # 每分钟请求数
    request_delay_min: float = 1.0  # 秒
    request_delay_max: float = 3.0  # 秒
    
    # GEO匹配
    geo_match_enabled: bool = True
    prefer_same_country: bool = True
    
    # 会话持久化
    session_persistence: bool = False
    session_duration: int = 600  # 秒


class ProxyPool:
    """代理池"""
    
    def __init__(self, config: Optional[ProxyPoolConfig] = None):
        self.config = config or ProxyPoolConfig()
        self.proxies: Dict[str, Proxy] = {}
        self._round_robin_index = 0
        self._request_timestamps: Dict[str, List[float]] = {}
        self._sessions: Dict[str, str] = {}  # session_id -> proxy_id
    
    def add_proxy(self, proxy: Proxy) -> None:
        """添加代理"""
        self.proxies[proxy.id] = proxy
        logger.info(f"Added proxy: {proxy.id} ({proxy.provider.value})")
    
    def add_proxies(self, proxies: List[Proxy]) -> None:
        """批量添加代理"""
        for proxy in proxies:
            self.add_proxy(proxy)
    
    def remove_proxy(self, proxy_id: str) -> None:
        """移除代理"""
        if proxy_id in self.proxies:
            del self.proxies[proxy_id]
            logger.info(f"Removed proxy: {proxy_id}")
    
    def get_proxy(self, country: Optional[str] = None, 
                  proxy_type: Optional[ProxyType] = None,
                  session_id: Optional[str] = None) -> Optional[Proxy]:
        """
        获取一个可用代理
        
        Args:
            country: 目标国家
            proxy_type: 代理类型
            session_id: 会话ID（用于会话持久化）
            
        Returns:
            代理对象
        """
        # 会话持久化
        if session_id and self.config.session_persistence:
            if session_id in self._sessions:
                proxy_id = self._sessions[session_id]
                if proxy_id in self.proxies and self.proxies[proxy_id].status == ProxyStatus.ACTIVE:
                    return self.proxies[proxy_id]
        
        # 筛选可用代理
        available_proxies = [
            p for p in self.proxies.values()
            if p.status == ProxyStatus.ACTIVE
        ]
        
        if not available_proxies:
            logger.warning("No available proxies in pool")
            return None
        
        # 按国家筛选
        if country and self.config.geo_match_enabled:
            country_proxies = [p for p in available_proxies if p.country == country]
            if country_proxies:
                available_proxies = country_proxies
        
        # 按类型筛选
        if proxy_type:
            type_proxies = [p for p in available_proxies if p.type == proxy_type]
            if type_proxies:
                available_proxies = type_proxies
        
        if not available_proxies:
            logger.warning("No proxies match the criteria")
            return None
        
        # 按策略选择
        if self.config.rotation_strategy == "round_robin":
            proxy = self._round_robin(available_proxies)
        elif self.config.rotation_strategy == "random":
            proxy = random.choice(available_proxies)
        elif self.config.rotation_strategy == "least_used":
            proxy = min(available_proxies, key=lambda p: p.total_requests)
        elif self.config.rotation_strategy == "fastest":
            proxy = min(available_proxies, key=lambda p: p.avg_response_time)
        else:
            proxy = random.choice(available_proxies)
        
        # 会话持久化
        if session_id and self.config.session_persistence:
            self._sessions[session_id] = proxy.id
        
        # 记录使用时间
        proxy.last_used = time.time()
        proxy.total_requests += 1
        
        return proxy
    
    def _round_robin(self, proxies: List[Proxy]) -> Proxy:
        """轮询选择"""
        if not proxies:
            return None
        
        proxy = proxies[self._round_robin_index % len(proxies)]
        self._round_robin_index = (self._round_robin_index + 1) % len(proxies)
        return proxy
    
    def report_success(self, proxy_id: str, response_time: float) -> None:
        """报告成功"""
        if proxy_id not in self.proxies:
            return
        
        proxy = self.proxies[proxy_id]
        proxy.success_count += 1
        
        # 更新平均响应时间
        if proxy.avg_response_time == 0:
            proxy.avg_response_time = response_time
        else:
            proxy.avg_response_time = (proxy.avg_response_time * 0.9 + response_time * 0.1)
        
        proxy.status = ProxyStatus.ACTIVE
    
    def report_failure(self, proxy_id: str, reason: str = "unknown") -> None:
        """报告失败"""
        if proxy_id not in self.proxies:
            return
        
        proxy = self.proxies[proxy_id]
        proxy.fail_count += 1
        
        # 检查是否超过最大失败次数
        if proxy.fail_count >= self.config.max_failures:
            proxy.status = ProxyStatus.BANNED
            proxy.last_banned = time.time()
            logger.warning(f"Proxy {proxy_id} banned after {proxy.fail_count} failures: {reason}")
            
            # 自动恢复：尝试恢复其他已过冷却期的被禁代理
            if self.config.auto_recover:
                self.auto_recover()
    
    def check_proxy_health(self, proxy_id: str) -> bool:
        """检查单个代理的健康状态

        通过向配置的健康检查URL发送请求来验证代理是否可用。
        当httpx不可用或健康检查未启用时，直接返回代理当前状态。

        Args:
            proxy_id: 代理ID

        Returns:
            True表示代理健康可用，False表示不可用
        """
        if proxy_id not in self.proxies:
            return False

        proxy = self.proxies[proxy_id]

        # 如果健康检查未启用，直接根据当前状态判断
        if not self.config.health_check_enabled:
            return proxy.status == ProxyStatus.ACTIVE

        # httpx不可用时无法进行真实健康检查
        if not HTTPX_AVAILABLE:
            logger.warning("httpx未安装，无法执行代理健康检查")
            return proxy.status == ProxyStatus.ACTIVE

        proxy.last_checked = time.time()

        try:
            with httpx.Client(
                proxy=proxy.url,
                timeout=self.config.health_check_timeout,
                verify=False,
            ) as client:
                response = client.get(self.config.health_check_url)
                is_healthy = response.status_code < 400

            if is_healthy:
                logger.debug(f"Proxy {proxy_id} health check passed")
            else:
                logger.debug(
                    f"Proxy {proxy_id} health check failed: status {response.status_code}"
                )
            return is_healthy
        except Exception as e:
            logger.debug(f"Proxy {proxy_id} health check error: {e}")
            return False

    def auto_recover(self) -> int:
        """自动恢复被禁用的代理

        遍历所有处于 BANNED / ERROR / TIMEOUT 状态的代理，
        对冷却期（failure_cooldown）已过的代理执行健康检查：
          - 健康检查通过：重新启用代理，清零失败计数，状态置为 ACTIVE
          - 健康检查未通过：保持禁用状态，更新 last_checked 时间
          - 冷却期未到：跳过，等待下次恢复

        Returns:
            本次成功恢复的代理数量
        """
        if not self.config.auto_recover:
            return 0

        now = time.time()
        cooldown = self.config.failure_cooldown
        recovered_count = 0

        # 遍历所有非活跃代理（BANNED / ERROR / TIMEOUT / INACTIVE）
        disabled_statuses = {
            ProxyStatus.BANNED,
            ProxyStatus.ERROR,
            ProxyStatus.TIMEOUT,
            ProxyStatus.INACTIVE,
        }

        for proxy in self.proxies.values():
            if proxy.status not in disabled_statuses:
                continue

            # 判断冷却期是否已过
            banned_time = proxy.last_banned or proxy.last_checked or 0
            if banned_time and (now - banned_time) < cooldown:
                # 冷却期未到，跳过
                continue

            # 执行健康检查
            is_healthy = self.check_proxy_health(proxy.id)

            if is_healthy:
                # 恢复代理：清零失败计数，重新启用
                proxy.status = ProxyStatus.ACTIVE
                proxy.fail_count = 0
                proxy.last_checked = now
                recovered_count += 1
                logger.info(
                    f"Proxy {proxy.id} recovered: health check passed, "
                    f"fail count reset to 0"
                )
            else:
                # 健康检查未通过，更新检查时间，保持禁用
                proxy.last_checked = now
                logger.debug(
                    f"Proxy {proxy.id} still unhealthy, remains {proxy.status.value}"
                )

        if recovered_count > 0:
            logger.info(f"Auto recover: {recovered_count} proxy(s) re-enabled")

        return recovered_count

    def cleanup_failure_counts(self) -> int:
        """清理活跃代理的失败计数

        对于长期运行后累积了少量失败但未达到禁用阈值的活跃代理，
        定期清理其失败计数，避免历史失败累积导致误禁用。

        Returns:
            本次清理了失败计数的代理数量
        """
        cleaned_count = 0
        for proxy in self.proxies.values():
            # 仅清理活跃代理的非零失败计数
            if proxy.status == ProxyStatus.ACTIVE and proxy.fail_count > 0:
                # 如果最近有成功记录，清理失败计数
                if proxy.success_count > 0:
                    proxy.fail_count = 0
                    cleaned_count += 1

        if cleaned_count > 0:
            logger.debug(f"Cleaned failure counts for {cleaned_count} active proxy(s)")

        return cleaned_count
    
    def check_rate_limit(self, proxy_id: str) -> bool:
        """检查速率限制"""
        if self.config.rate_limit_per_proxy <= 0:
            return True
        
        now = time.time()
        window_start = now - 60  # 1分钟窗口
        
        if proxy_id not in self._request_timestamps:
            self._request_timestamps[proxy_id] = []
        
        # 清理过期时间戳
        self._request_timestamps[proxy_id] = [
            ts for ts in self._request_timestamps[proxy_id]
            if ts > window_start
        ]
        
        return len(self._request_timestamps[proxy_id]) < self.config.rate_limit_per_proxy
    
    def get_request_delay(self) -> float:
        """获取请求延迟（模拟真人）"""
        return random.uniform(
            self.config.request_delay_min,
            self.config.request_delay_max
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """获取代理池统计"""
        total = len(self.proxies)
        active = sum(1 for p in self.proxies.values() if p.status == ProxyStatus.ACTIVE)
        banned = sum(1 for p in self.proxies.values() if p.status == ProxyStatus.BANNED)
        
        avg_success_rate = 0.0
        avg_response_time = 0.0
        total_requests = 0
        
        if self.proxies:
            avg_success_rate = sum(p.success_rate for p in self.proxies.values()) / total
            avg_response_time = sum(p.avg_response_time for p in self.proxies.values()) / total
            total_requests = sum(p.total_requests for p in self.proxies.values())
        
        return {
            "total_proxies": total,
            "active_proxies": active,
            "banned_proxies": banned,
            "avg_success_rate": avg_success_rate,
            "avg_response_time": avg_response_time,
            "total_requests": total_requests,
        }
    
    def get_proxies_by_country(self) -> Dict[str, int]:
        """按国家统计代理数量"""
        countries = {}
        for proxy in self.proxies.values():
            country = proxy.country or "unknown"
            countries[country] = countries.get(country, 0) + 1
        return countries
    
    def get_proxies_by_provider(self) -> Dict[str, int]:
        """按供应商统计代理数量"""
        providers = {}
        for proxy in self.proxies.values():
            provider = proxy.provider.value
            providers[provider] = providers.get(provider, 0) + 1
        return providers


class ProxyManager:
    """代理管理器"""
    
    def __init__(self):
        self.pools: Dict[str, ProxyPool] = {}
        self._default_pool = "default"
        self._init_default_pool()
    
    def _init_default_pool(self) -> None:
        """初始化默认代理池"""
        config = ProxyPoolConfig()
        self.pools[self._default_pool] = ProxyPool(config)
    
    def create_pool(self, name: str, config: Optional[ProxyPoolConfig] = None) -> ProxyPool:
        """创建代理池"""
        if name in self.pools:
            logger.warning(f"Proxy pool {name} already exists")
            return self.pools[name]
        
        pool = ProxyPool(config)
        self.pools[name] = pool
        logger.info(f"Created proxy pool: {name}")
        return pool
    
    def get_pool(self, name: Optional[str] = None) -> ProxyPool:
        """获取代理池"""
        pool_name = name or self._default_pool
        if pool_name not in self.pools:
            return self.pools[self._default_pool]
        return self.pools[pool_name]
    
    def get_proxy(self, pool: Optional[str] = None, 
                  country: Optional[str] = None,
                  proxy_type: Optional[ProxyType] = None,
                  session_id: Optional[str] = None) -> Optional[Proxy]:
        """获取代理"""
        proxy_pool = self.get_pool(pool)
        return proxy_pool.get_proxy(country=country, proxy_type=proxy_type, session_id=session_id)
    
    def add_brightdata_proxies(self, username: str, password: str, 
                               zones: Optional[List[str]] = None,
                               pool: Optional[str] = None) -> int:
        """
        添加BrightData代理
        
        Args:
            username: BrightData用户名
            password: BrightData密码
            zones: 区域列表
            pool: 代理池名称
            
        Returns:
            添加的代理数量
        """
        proxy_pool = self.get_pool(pool)
        count = 0
        
        zones = zones or ["zone1"]
        
        for zone in zones:
            # BrightData使用不同的端口对应不同的国家
            base_port = 22225
            
            # 主要国家
            countries = ["us", "gb", "de", "fr", "jp", "au", "ca", "it", "es", "nl"]
            
            for i, country in enumerate(countries):
                proxy = Proxy(
                    id=f"brightdata-{zone}-{country}",
                    provider=ProxyProvider.BRIGHTDATA,
                    protocol=ProxyProtocol.HTTP,
                    type=ProxyType.RESIDENTIAL,
                    host="zproxy.lum-superproxy.io",
                    port=base_port + i,
                    username=f"{username}-zone-{zone}-country-{country}",
                    password=password,
                    country=country.upper(),
                )
                proxy_pool.add_proxy(proxy)
                count += 1
        
        logger.info(f"Added {count} BrightData proxies")
        return count
    
    def add_oxylabs_proxies(self, username: str, password: str,
                            pool: Optional[str] = None) -> int:
        """
        添加Oxylabs代理
        
        Args:
            username: Oxylabs用户名
            password: Oxylabs密码
            pool: 代理池名称
            
        Returns:
            添加的代理数量
        """
        proxy_pool = self.get_pool(pool)
        count = 0
        
        # 住宅代理入口
        countries = ["us", "gb", "de", "fr", "jp", "au", "ca"]
        
        for country in countries:
            proxy = Proxy(
                id=f"oxylabs-residential-{country}",
                provider=ProxyProvider.OXYLABS,
                protocol=ProxyProtocol.HTTP,
                type=ProxyType.RESIDENTIAL,
                host="pr.oxylabs.io",
                port=7777,
                username=f"user-{username}-cc-{country}",
                password=password,
                country=country.upper(),
            )
            proxy_pool.add_proxy(proxy)
            count += 1
        
        logger.info(f"Added {count} Oxylabs proxies")
        return count
    
    def add_smartproxy_proxies(self, username: str, password: str,
                               pool: Optional[str] = None) -> int:
        """
        添加Smartproxy代理
        
        Args:
            username: Smartproxy用户名
            password: Smartproxy密码
            pool: 代理池名称
            
        Returns:
            添加的代理数量
        """
        proxy_pool = self.get_pool(pool)
        count = 0
        
        # Smartproxy端点
        endpoints = [
            ("us.smartproxy.com", 10000, "US"),
            ("uk.smartproxy.com", 10001, "GB"),
            ("de.smartproxy.com", 10002, "DE"),
            ("fr.smartproxy.com", 10003, "FR"),
            ("jp.smartproxy.com", 10004, "JP"),
        ]
        
        for host, port, country in endpoints:
            proxy = Proxy(
                id=f"smartproxy-{country.lower()}",
                provider=ProxyProvider.SMARTPROXY,
                protocol=ProxyProtocol.HTTP,
                type=ProxyType.RESIDENTIAL,
                host=host,
                port=port,
                username=username,
                password=password,
                country=country,
            )
            proxy_pool.add_proxy(proxy)
            count += 1
        
        logger.info(f"Added {count} Smartproxy proxies")
        return count
    
    def add_webshare_proxies(self, api_key: str, 
                             pool: Optional[str] = None) -> int:
        """
        添加Webshare代理（需要API获取列表）
        
        Args:
            api_key: Webshare API密钥
            pool: 代理池名称
            
        Returns:
            添加的代理数量
        """
        # 这里应该调用Webshare API获取代理列表
        # 简化实现，添加示例代理
        proxy_pool = self.get_pool(pool)
        count = 0
        
        # 示例：添加10个数据中心代理
        for i in range(10):
            proxy = Proxy(
                id=f"webshare-dc-{i}",
                provider=ProxyProvider.WEBSHARE,
                protocol=ProxyProtocol.HTTP,
                type=ProxyType.DATACENTER,
                host=f"p.webshare.io",
                port=80 + i,
                username=f"user-{api_key[:8]}",
                password=api_key,
                country="US",
            )
            proxy_pool.add_proxy(proxy)
            count += 1
        
        logger.info(f"Added {count} Webshare proxies")
        return count
    
    def add_self_hosted_proxies(self, proxy_list: List[Dict[str, Any]],
                                 pool: Optional[str] = None) -> int:
        """
        添加自建代理
        
        Args:
            proxy_list: 代理列表，每个包含host, port, username, password等
            pool: 代理池名称
            
        Returns:
            添加的代理数量
        """
        proxy_pool = self.get_pool(pool)
        count = 0
        
        for i, proxy_data in enumerate(proxy_list):
            proxy = Proxy(
                id=f"self-hosted-{i}",
                provider=ProxyProvider.SELF_HOSTED,
                protocol=ProxyProtocol(proxy_data.get("protocol", "http")),
                type=ProxyType(proxy_data.get("type", "datacenter")),
                host=proxy_data["host"],
                port=proxy_data["port"],
                username=proxy_data.get("username"),
                password=proxy_data.get("password"),
                country=proxy_data.get("country"),
                city=proxy_data.get("city"),
            )
            proxy_pool.add_proxy(proxy)
            count += 1
        
        logger.info(f"Added {count} self-hosted proxies")
        return count
    
    def get_all_stats(self) -> Dict[str, Any]:
        """获取所有代理池统计"""
        stats = {}
        for name, pool in self.pools.items():
            stats[name] = pool.get_stats()
        return stats


# 全局代理管理器实例
proxy_manager = ProxyManager()
