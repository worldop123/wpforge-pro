"""
请求头伪造
提供真实浏览器请求头的生成功能
"""
import random
import hashlib
from typing import Dict, Any, List, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class RequestHeaderGenerator:
    """请求头生成器"""
    
    # Chrome浏览器的请求头顺序（非常重要！）
    CHROME_HEADER_ORDER = [
        "Host",
        "Connection",
        "Cache-Control",
        "sec-ch-ua",
        "sec-ch-ua-mobile",
        "sec-ch-ua-platform",
        "Upgrade-Insecure-Requests",
        "User-Agent",
        "Accept",
        "Sec-Fetch-Site",
        "Sec-Fetch-Mode",
        "Sec-Fetch-User",
        "Sec-Fetch-Dest",
        "Accept-Encoding",
        "Accept-Language",
        "Cookie",
    ]
    
    # Firefox浏览器的请求头顺序
    FIREFOX_HEADER_ORDER = [
        "Host",
        "User-Agent",
        "Accept",
        "Accept-Language",
        "Accept-Encoding",
        "Connection",
        "Upgrade-Insecure-Requests",
        "Sec-Fetch-Dest",
        "Sec-Fetch-Mode",
        "Sec-Fetch-Site",
        "Sec-Fetch-User",
        "Cache-Control",
        "Cookie",
    ]
    
    # Safari浏览器的请求头顺序
    SAFARI_HEADER_ORDER = [
        "Host",
        "Accept",
        "Accept-Encoding",
        "Accept-Language",
        "Connection",
        "Cookie",
        "User-Agent",
    ]
    
    def __init__(self):
        self._browser: str = "chrome"
        self._user_agent: str = ""
        self._language: str = "en-US"
        self._languages: List[str] = ["en-US", "en"]
        self._accept_encoding: str = "gzip, deflate, br"
        self._accept: str = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
        self._sec_ch_ua: str = ""
        self._sec_ch_ua_mobile: str = "?0"
        self._sec_ch_ua_platform: str = "Windows"
    
    def set_browser(self, browser: str):
        """设置浏览器类型"""
        self._browser = browser.lower()
    
    def set_user_agent(self, user_agent: str):
        """设置User-Agent"""
        self._user_agent = user_agent
        self._update_sec_ch_ua()
    
    def set_language(self, language: str, languages: Optional[List[str]] = None):
        """设置语言"""
        self._language = language
        if languages:
            self._languages = languages
        else:
            self._languages = [language, language.split("-")[0]]
    
    def _update_sec_ch_ua(self):
        """更新sec-ch-ua头"""
        # 从UA中提取Chrome版本
        if "Chrome/" in self._user_agent:
            version = self._user_agent.split("Chrome/")[1].split(" ")[0]
            major_version = version.split(".")[0]
            
            self._sec_ch_ua = (
                f'"Chromium";v="{major_version}", '
                f'"Google Chrome";v="{major_version}", '
                f'"Not.A/Brand";v="24"'
            )
        else:
            self._sec_ch_ua = '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"'
    
    def generate_headers(self, url: str, method: str = "GET",
                          referer: Optional[str] = None,
                          is_ajax: bool = False,
                          extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        生成请求头
        
        Args:
            url: 请求URL
            method: HTTP方法
            referer: Referer
            is_ajax: 是否是AJAX请求
            extra_headers: 额外的请求头
            
        Returns:
            请求头字典
        """
        headers = {}
        
        # 基础请求头
        if self._browser == "chrome":
            headers = self._generate_chrome_headers(url, method, referer, is_ajax)
        elif self._browser == "firefox":
            headers = self._generate_firefox_headers(url, method, referer, is_ajax)
        elif self._browser == "safari":
            headers = self._generate_safari_headers(url, method, referer, is_ajax)
        else:
            headers = self._generate_chrome_headers(url, method, referer, is_ajax)
        
        # 添加额外的请求头
        if extra_headers:
            headers.update(extra_headers)
        
        # 按正确顺序排序
        ordered_headers = self._order_headers(headers)
        
        return ordered_headers
    
    def _generate_chrome_headers(self, url: str, method: str,
                                  referer: Optional[str],
                                  is_ajax: bool) -> Dict[str, str]:
        """生成Chrome风格的请求头"""
        headers = {}
        
        # Host
        from urllib.parse import urlparse
        parsed = urlparse(url)
        headers["Host"] = parsed.netloc
        
        # Connection
        headers["Connection"] = "keep-alive"
        
        # Cache-Control
        headers["Cache-Control"] = "max-age=0"
        
        # sec-ch-ua
        if self._sec_ch_ua:
            headers["sec-ch-ua"] = self._sec_ch_ua
        
        # sec-ch-ua-mobile
        headers["sec-ch-ua-mobile"] = self._sec_ch_ua_mobile
        
        # sec-ch-ua-platform
        headers["sec-ch-ua-platform"] = f'"{self._sec_ch_ua_platform}"'
        
        # Upgrade-Insecure-Requests
        headers["Upgrade-Insecure-Requests"] = "1"
        
        # User-Agent
        headers["User-Agent"] = self._user_agent
        
        # Accept
        if is_ajax:
            headers["Accept"] = "application/json, text/javascript, */*; q=0.01"
        else:
            headers["Accept"] = self._accept
        
        # Sec-Fetch-Site
        if referer:
            referer_parsed = urlparse(referer)
            if referer_parsed.netloc == parsed.netloc:
                headers["Sec-Fetch-Site"] = "same-origin"
            else:
                headers["Sec-Fetch-Site"] = "cross-site"
        else:
            headers["Sec-Fetch-Site"] = "none"
        
        # Sec-Fetch-Mode
        if is_ajax:
            headers["Sec-Fetch-Mode"] = "cors"
        else:
            headers["Sec-Fetch-Mode"] = "navigate"
        
        # Sec-Fetch-User
        if not is_ajax:
            headers["Sec-Fetch-User"] = "?1"
        
        # Sec-Fetch-Dest
        if is_ajax:
            headers["Sec-Fetch-Dest"] = "empty"
        else:
            headers["Sec-Fetch-Dest"] = "document"
        
        # Accept-Encoding
        headers["Accept-Encoding"] = self._accept_encoding
        
        # Accept-Language
        headers["Accept-Language"] = ", ".join(self._languages) + ";q=0.9"
        
        # Referer
        if referer:
            headers["Referer"] = referer
        
        return headers
    
    def _generate_firefox_headers(self, url: str, method: str,
                                   referer: Optional[str],
                                   is_ajax: bool) -> Dict[str, str]:
        """生成Firefox风格的请求头"""
        headers = {}
        
        from urllib.parse import urlparse
        parsed = urlparse(url)
        
        # Host
        headers["Host"] = parsed.netloc
        
        # User-Agent
        headers["User-Agent"] = self._user_agent
        
        # Accept
        if is_ajax:
            headers["Accept"] = "application/json, text/javascript, */*; q=0.01"
        else:
            headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        
        # Accept-Language
        headers["Accept-Language"] = ", ".join(self._languages) + ";q=0.8,en-US;q=0.5,en;q=0.3"
        
        # Accept-Encoding
        headers["Accept-Encoding"] = "gzip, deflate, br"
        
        # Connection
        headers["Connection"] = "keep-alive"
        
        # Upgrade-Insecure-Requests
        headers["Upgrade-Insecure-Requests"] = "1"
        
        # Sec-Fetch-Dest
        if is_ajax:
            headers["Sec-Fetch-Dest"] = "empty"
        else:
            headers["Sec-Fetch-Dest"] = "document"
        
        # Sec-Fetch-Mode
        if is_ajax:
            headers["Sec-Fetch-Mode"] = "cors"
        else:
            headers["Sec-Fetch-Mode"] = "navigate"
        
        # Sec-Fetch-Site
        if referer:
            referer_parsed = urlparse(referer)
            if referer_parsed.netloc == parsed.netloc:
                headers["Sec-Fetch-Site"] = "same-origin"
            else:
                headers["Sec-Fetch-Site"] = "cross-site"
        else:
            headers["Sec-Fetch-Site"] = "none"
        
        # Sec-Fetch-User
        if not is_ajax:
            headers["Sec-Fetch-User"] = "?1"
        
        # Referer
        if referer:
            headers["Referer"] = referer
        
        return headers
    
    def _generate_safari_headers(self, url: str, method: str,
                                  referer: Optional[str],
                                  is_ajax: bool) -> Dict[str, str]:
        """生成Safari风格的请求头"""
        headers = {}
        
        from urllib.parse import urlparse
        parsed = urlparse(url)
        
        # Host
        headers["Host"] = parsed.netloc
        
        # Accept
        if is_ajax:
            headers["Accept"] = "application/json, text/javascript, */*; q=0.01"
        else:
            headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        
        # Accept-Encoding
        headers["Accept-Encoding"] = "gzip, deflate, br"
        
        # Accept-Language
        headers["Accept-Language"] = ", ".join(self._languages)
        
        # Connection
        headers["Connection"] = "keep-alive"
        
        # User-Agent
        headers["User-Agent"] = self._user_agent
        
        # Referer
        if referer:
            headers["Referer"] = referer
        
        return headers
    
    def _order_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """按正确的顺序排列请求头"""
        if self._browser == "chrome":
            header_order = self.CHROME_HEADER_ORDER
        elif self._browser == "firefox":
            header_order = self.FIREFOX_HEADER_ORDER
        elif self._browser == "safari":
            header_order = self.SAFARI_HEADER_ORDER
        else:
            header_order = self.CHROME_HEADER_ORDER
        
        ordered = {}
        
        # 先按顺序添加已知的头
        for header_name in header_order:
            if header_name in headers:
                ordered[header_name] = headers[header_name]
        
        # 然后添加剩余的头
        for header_name, value in headers.items():
            if header_name not in ordered:
                ordered[header_name] = value
        
        return ordered
    
    def generate_ajax_headers(self, url: str, referer: Optional[str] = None) -> Dict[str, str]:
        """生成AJAX请求头"""
        return self.generate_headers(url, method="GET", referer=referer, is_ajax=True)
    
    def generate_image_headers(self, url: str, referer: Optional[str] = None) -> Dict[str, str]:
        """生成图片请求头"""
        headers = self.generate_headers(url, referer=referer)
        headers["Accept"] = "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
        headers["Sec-Fetch-Dest"] = "image"
        headers["Sec-Fetch-Mode"] = "no-cors"
        return headers
    
    def generate_script_headers(self, url: str, referer: Optional[str] = None) -> Dict[str, str]:
        """生成脚本请求头"""
        headers = self.generate_headers(url, referer=referer)
        headers["Accept"] = "*/*"
        headers["Sec-Fetch-Dest"] = "script"
        headers["Sec-Fetch-Mode"] = "no-cors"
        return headers
    
    def generate_stylesheet_headers(self, url: str, referer: Optional[str] = None) -> Dict[str, str]:
        """生成样式表请求头"""
        headers = self.generate_headers(url, referer=referer)
        headers["Accept"] = "text/css,*/*;q=0.1"
        headers["Sec-Fetch-Dest"] = "style"
        headers["Sec-Fetch-Mode"] = "no-cors"
        return headers
    
    def get_header_order(self) -> List[str]:
        """获取请求头顺序"""
        if self._browser == "chrome":
            return self.CHROME_HEADER_ORDER.copy()
        elif self._browser == "firefox":
            return self.FIREFOX_HEADER_ORDER.copy()
        elif self._browser == "safari":
            return self.SAFARI_HEADER_ORDER.copy()
        else:
            return self.CHROME_HEADER_ORDER.copy()
