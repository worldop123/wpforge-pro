"""
Cloudflare绕过
提供Cloudflare 5秒盾、IUAM挑战、验证码等的绕过功能
"""
import time
import random
from typing import Dict, Any, Optional, List

from app.core.logging import get_logger

logger = get_logger(__name__)


class CloudflareBypass:
    """Cloudflare绕过器"""
    
    def __init__(self):
        self._wait_time = 5.0  # 默认等待时间
        self._max_retries = 3
        self._cookie_cache = {}
        self._user_agent = ""
    
    def set_user_agent(self, user_agent: str):
        """设置User-Agent"""
        self._user_agent = user_agent
    
    def set_wait_time(self, seconds: float):
        """设置等待时间"""
        self._wait_time = seconds
    
    def set_max_retries(self, retries: int):
        """设置最大重试次数"""
        self._max_retries = retries
    
    def is_cloudflare_challenge(self, response_headers: Dict[str, str], 
                                status_code: int = 200) -> bool:
        """
        检测是否是Cloudflare挑战页面
        
        Args:
            response_headers: 响应头
            status_code: 状态码
            
        Returns:
            是否是Cloudflare挑战
        """
        # 检查状态码
        if status_code == 403 or status_code == 503:
            return True
        
        # 检查Server头
        server = response_headers.get("Server", "").lower()
        if "cloudflare" in server:
            # 检查是否有挑战相关的头
            if "cf-ray" in response_headers:
                # 可能是正常的Cloudflare响应，需要进一步检查
                pass
        
        # 检查是否有cf-challenge相关的头
        if "cf-challenge" in str(response_headers).lower():
            return True
        
        return False
    
    def is_iuam_challenge(self, response_headers: Dict[str, str]) -> bool:
        """
        检测是否是IUAM（I'm Under Attack Mode）挑战
        
        Args:
            response_headers: 响应头
            
        Returns:
            是否是IUAM挑战
        """
        # IUAM通常返回503状态码
        return False  # 简化实现
    
    def is_turnstile_challenge(self, response_headers: Dict[str, str]) -> bool:
        """
        检测是否是Turnstile验证码挑战
        
        Args:
            response_headers: 响应头
            
        Returns:
            是否是Turnstile挑战
        """
        return False  # 简化实现
    
    def wait_for_challenge(self, duration: Optional[float] = None) -> float:
        """
        等待挑战完成
        
        Args:
            duration: 等待时间（秒），如果为None则使用默认值
            
        Returns:
            实际等待时间
        """
        wait_time = duration if duration is not None else self._wait_time
        
        # 添加一些随机变化
        jitter = random.uniform(-0.5, 0.5)
        actual_wait = max(2.0, wait_time + jitter)
        
        logger.info(f"Waiting {actual_wait:.2f}s for Cloudflare challenge")
        
        return actual_wait
    
    def extract_cf_cookies(self, response_headers: Dict[str, str],
                            set_cookie_header: str = "") -> Dict[str, str]:
        """
        提取Cloudflare Cookie
        
        Args:
            response_headers: 响应头
            set_cookie_header: Set-Cookie头内容
            
        Returns:
            Cookie字典
        """
        cookies = {}
        
        # 从Set-Cookie头中提取
        if set_cookie_header:
            # 解析Set-Cookie头
            parts = set_cookie_header.split(";")
            if parts:
                name_value = parts[0].strip()
                if "=" in name_value:
                    name, value = name_value.split("=", 1)
                    # 检查是否是Cloudflare的Cookie
                    if name.startswith("cf_") or name == "__cfduid" or name == "cf_clearance":
                        cookies[name] = value
        
        return cookies
    
    def get_cf_clearance_cookie(self, domain: str) -> Optional[str]:
        """
        获取cf_clearance Cookie
        
        Args:
            domain: 域名
            
        Returns:
            cf_clearance Cookie值
        """
        return self._cookie_cache.get(domain, {}).get("cf_clearance")
    
    def cache_cf_cookies(self, domain: str, cookies: Dict[str, str]):
        """
        缓存Cloudflare Cookie
        
        Args:
            domain: 域名
            cookies: Cookie字典
        """
        if domain not in self._cookie_cache:
            self._cookie_cache[domain] = {}
        
        self._cookie_cache[domain].update(cookies)
    
    def get_bypass_strategy(self, challenge_type: str) -> Dict[str, Any]:
        """
        获取绕过策略
        
        Args:
            challenge_type: 挑战类型
            
        Returns:
            策略配置
        """
        strategies = {
            "iuam": {
                "name": "IUAM Challenge",
                "method": "javascript_eval",
                "wait_time": 5.0,
                "requires_browser": True,
                "description": "需要执行JavaScript计算",
            },
            "turnstile": {
                "name": "Turnstile Captcha",
                "method": "captcha_solver",
                "requires_provider": True,
                "description": "需要打码平台解决",
            },
            "managed_challenge": {
                "name": "Managed Challenge",
                "method": "browser_simulation",
                "wait_time": 8.0,
                "requires_browser": True,
                "description": "需要完整的浏览器模拟",
            },
        }
        
        return strategies.get(challenge_type, {
            "name": "Unknown",
            "method": "wait",
            "wait_time": 5.0,
        })
    
    def get_cloudflare_bypass_tips(self) -> List[str]:
        """获取Cloudflare绕过建议"""
        return [
            "使用真实的浏览器指纹",
            "确保TLS指纹与浏览器匹配",
            "确保HTTP/2指纹与浏览器匹配",
            "等待足够的时间让JavaScript执行",
            "正确处理cf_clearance Cookie",
            "保持会话一致性",
            "使用住宅代理IP",
            "模拟真实的人类行为",
            "避免快速重复请求",
            "正确处理重定向",
        ]
    
    def get_required_tools(self) -> List[str]:
        """获取需要的工具"""
        return [
            "真实浏览器（Playwright/Puppeteer）",
            "浏览器指纹伪造",
            "TLS指纹伪造",
            "住宅代理",
            "打码平台（针对Turnstile）",
        ]
