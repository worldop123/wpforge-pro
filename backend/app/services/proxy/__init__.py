"""
代理系统模块
支持多供应商代理池、动态轮换、健康检查、GEO匹配
以及完整的浏览器指纹、行为模拟、网络层反检测等功能
"""
from app.services.proxy.proxy_pool import (
    Proxy,
    ProxyProvider,
    ProxyProtocol,
    ProxyType,
    ProxyStatus,
    ProxyPoolConfig,
    ProxyPool,
    ProxyManager,
    proxy_manager,
)
from app.services.proxy.stealth_service import (
    BrowserFingerprint,
    FingerprintGenerator,
    HumanBehaviorSimulator,
    StealthService,
    stealth_service,
)

# 指纹模块
from app.services.proxy.fingerprint import (
    CanvasFingerprint,
    WebGLFingerprint,
    AudioFingerprint,
    FontFingerprint,
    NavigatorFingerprint,
    ScreenFingerprint,
    TimezoneFingerprint,
    GeolocationFingerprint,
    WebRTCFingerprint,
    StorageFingerprint,
    PerformanceFingerprint,
    SensorFingerprint,
    FingerprintConsistency,
    FingerprintAuthenticity,
    FingerprintDiversity,
)

# 行为模拟模块
from app.services.proxy.behavior import (
    MouseBehaviorSimulator,
    ClickBehaviorSimulator,
    ScrollBehaviorSimulator,
    KeyboardBehaviorSimulator,
    BrowsingBehaviorSimulator,
    InteractionBehaviorSimulator,
    WordPressBehaviorSimulator,
)

# 网络层反检测模块
from app.services.proxy.network import (
    RequestHeaderGenerator,
    CookieHandler,
    CacheSimulator,
    TLSFingerprintGenerator,
    HTTP2FingerprintGenerator,
)

# 验证码与反爬绕过模块
from app.services.proxy.captcha import (
    CaptchaSolver,
    CaptchaType,
    CaptchaProviderManager,
    CloudflareBypass,
    AntiBotBypass,
)

# 检测与验证模块
from app.services.proxy.verification import (
    FingerprintTester,
    AntiBotTester,
    UpdateManager,
)

# 配置与管理模块
from app.services.proxy.config import (
    StealthConfig,
    StealthIntensity,
)

__all__ = [
    # 代理池
    "Proxy",
    "ProxyProvider",
    "ProxyProtocol",
    "ProxyType",
    "ProxyStatus",
    "ProxyPoolConfig",
    "ProxyPool",
    "ProxyManager",
    "proxy_manager",
    
    # 核心反检测服务
    "BrowserFingerprint",
    "FingerprintGenerator",
    "HumanBehaviorSimulator",
    "StealthService",
    "stealth_service",
    
    # 指纹模块
    "CanvasFingerprint",
    "WebGLFingerprint",
    "AudioFingerprint",
    "FontFingerprint",
    "NavigatorFingerprint",
    "ScreenFingerprint",
    "TimezoneFingerprint",
    "GeolocationFingerprint",
    "WebRTCFingerprint",
    "StorageFingerprint",
    "PerformanceFingerprint",
    "SensorFingerprint",
    "FingerprintConsistency",
    "FingerprintAuthenticity",
    "FingerprintDiversity",
    
    # 行为模拟模块
    "MouseBehaviorSimulator",
    "ClickBehaviorSimulator",
    "ScrollBehaviorSimulator",
    "KeyboardBehaviorSimulator",
    "BrowsingBehaviorSimulator",
    "InteractionBehaviorSimulator",
    "WordPressBehaviorSimulator",
    
    # 网络层反检测模块
    "RequestHeaderGenerator",
    "CookieHandler",
    "CacheSimulator",
    "TLSFingerprintGenerator",
    "HTTP2FingerprintGenerator",
    
    # 验证码与反爬绕过模块
    "CaptchaSolver",
    "CaptchaType",
    "CaptchaProviderManager",
    "CloudflareBypass",
    "AntiBotBypass",
    
    # 检测与验证模块
    "FingerprintTester",
    "AntiBotTester",
    "UpdateManager",
    
    # 配置与管理模块
    "StealthConfig",
    "StealthIntensity",
]
