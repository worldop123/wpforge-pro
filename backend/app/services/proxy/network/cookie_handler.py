"""
Cookie处理器
提供Cookie自动管理功能
"""
import time
import random
from typing import Dict, Any, List, Optional, Set
from urllib.parse import urlparse

from app.core.logging import get_logger

logger = get_logger(__name__)


class Cookie:
    """Cookie数据类"""
    
    def __init__(self, name: str, value: str, domain: str, path: str = "/",
                 expires: Optional[float] = None, max_age: Optional[int] = None,
                 secure: bool = False, httponly: bool = False,
                 samesite: str = "Lax"):
        self.name = name
        self.value = value
        self.domain = domain
        self.path = path
        self.expires = expires
        self.max_age = max_age
        self.secure = secure
        self.httponly = httponly
        self.samesite = samesite
        self.created_at = time.time()
    
    def is_expired(self) -> bool:
        """检查Cookie是否过期"""
        if self.max_age is not None:
            return time.time() - self.created_at > self.max_age
        if self.expires is not None:
            return time.time() > self.expires
        return False  # 会话Cookie
    
    def matches(self, url: str) -> bool:
        """检查Cookie是否匹配URL"""
        parsed = urlparse(url)
        
        # 检查域名
        if not parsed.netloc.endswith(self.domain) and parsed.netloc != self.domain:
            return False
        
        # 检查路径
        if not parsed.path.startswith(self.path):
            return False
        
        # 检查Secure标志
        if self.secure and parsed.scheme != "https":
            return False
        
        return True
    
    def to_header_string(self) -> str:
        """转换为Cookie头字符串"""
        return f"{self.name}={self.value}"


class CookieHandler:
    """Cookie处理器"""
    
    def __init__(self):
        self._cookies: Dict[str, Cookie] = {}
        self._third_party_enabled: bool = True
        self._max_cookies_per_domain: int = 180
        self._max_cookie_size: int = 4096
    
    def add_cookie(self, cookie: Cookie):
        """添加Cookie"""
        key = f"{cookie.domain}{cookie.path}{cookie.name}"
        self._cookies[key] = cookie
        self._clean_expired()
    
    def add_cookie_from_header(self, set_cookie_header: str, domain: str):
        """从Set-Cookie头添加Cookie"""
        parts = set_cookie_header.split(";")
        if not parts:
            return
        
        # 解析name=value
        name_value = parts[0].strip()
        if "=" not in name_value:
            return
        
        name, value = name_value.split("=", 1)
        name = name.strip()
        value = value.strip()
        
        # 解析属性
        path = "/"
        expires = None
        max_age = None
        secure = False
        httponly = False
        samesite = "Lax"
        cookie_domain = domain
        
        for part in parts[1:]:
            part = part.strip()
            part_lower = part.lower()
            
            if part_lower.startswith("path="):
                path = part.split("=", 1)[1].strip()
            elif part_lower.startswith("domain="):
                cookie_domain = part.split("=", 1)[1].strip()
            elif part_lower.startswith("expires="):
                try:
                    from email.utils import parsedate_to_datetime
                    expires_str = part.split("=", 1)[1].strip()
                    expires = parsedate_to_datetime(expires_str).timestamp()
                except:
                    pass
            elif part_lower.startswith("max-age="):
                try:
                    max_age = int(part.split("=", 1)[1].strip())
                except:
                    pass
            elif part_lower == "secure":
                secure = True
            elif part_lower == "httponly":
                httponly = True
            elif part_lower.startswith("samesite="):
                samesite = part.split("=", 1)[1].strip()
        
        cookie = Cookie(
            name=name,
            value=value,
            domain=cookie_domain,
            path=path,
            expires=expires,
            max_age=max_age,
            secure=secure,
            httponly=httponly,
            samesite=samesite,
        )
        
        self.add_cookie(cookie)
    
    def get_cookies_for_url(self, url: str) -> List[Cookie]:
        """获取匹配URL的Cookie"""
        self._clean_expired()
        
        matching = []
        for cookie in self._cookies.values():
            if cookie.matches(url):
                matching.append(cookie)
        
        return matching
    
    def get_cookie_header(self, url: str) -> str:
        """获取Cookie头字符串"""
        cookies = self.get_cookies_for_url(url)
        if not cookies:
            return ""
        
        # 按名称排序（模拟浏览器行为）
        cookies.sort(key=lambda c: c.name)
        
        return "; ".join(c.to_header_string() for c in cookies)
    
    def delete_cookie(self, name: str, domain: str, path: str = "/"):
        """删除Cookie"""
        key = f"{domain}{path}{name}"
        if key in self._cookies:
            del self._cookies[key]
    
    def clear_cookies(self, domain: Optional[str] = None):
        """清除Cookie"""
        if domain is None:
            self._cookies.clear()
        else:
            keys_to_delete = []
            for key, cookie in self._cookies.items():
                if cookie.domain == domain:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self._cookies[key]
    
    def _clean_expired(self):
        """清理过期的Cookie"""
        keys_to_delete = []
        for key, cookie in self._cookies.items():
            if cookie.is_expired():
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del self._cookies[key]
    
    def get_all_cookies(self) -> List[Cookie]:
        """获取所有Cookie"""
        self._clean_expired()
        return list(self._cookies.values())
    
    def get_cookie_count(self) -> int:
        """获取Cookie数量"""
        self._clean_expired()
        return len(self._cookies)
    
    def simulate_cookie_degradation(self):
        """模拟Cookie降级（随机删除一些Cookie）"""
        # 模拟浏览器偶尔会清理一些Cookie
        if len(self._cookies) > 50 and random.random() < 0.1:
            # 随机删除1-5个Cookie
            num_to_delete = random.randint(1, 5)
            keys = list(self._cookies.keys())
            keys_to_delete = random.sample(keys, min(num_to_delete, len(keys)))
            
            for key in keys_to_delete:
                del self._cookies[key]
    
    def set_third_party_enabled(self, enabled: bool):
        """设置是否启用第三方Cookie"""
        self._third_party_enabled = enabled
    
    def is_third_party_enabled(self) -> bool:
        """检查是否启用第三方Cookie"""
        return self._third_party_enabled
