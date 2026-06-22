"""
HTTP/2指纹伪造配置生成器
提供HTTP/2 SETTINGS帧、帧顺序、流优先级等指纹的配置生成功能

注意：这是一个配置生成器，实际的HTTP/2指纹伪造需要在底层网络库中实现
"""
import random
from typing import Dict, Any, List, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class HTTP2FingerprintGenerator:
    """HTTP/2指纹生成器"""
    
    # Chrome的SETTINGS参数
    CHROME_SETTINGS = {
        1: 65536,      # HEADER_TABLE_SIZE
        2: 0,          # ENABLE_PUSH
        3: 1000,       # MAX_CONCURRENT_STREAMS
        4: 6291456,    # INITIAL_WINDOW_SIZE
        5: 16384,      # MAX_FRAME_SIZE
        6: 262144,     # MAX_HEADER_LIST_SIZE
        7: 1,          # UNKNOWN_7
        9: 1,          # UNKNOWN_9
        10: 262144,    # UNKNOWN_10
    }
    
    # Firefox的SETTINGS参数
    FIREFOX_SETTINGS = {
        1: 65536,      # HEADER_TABLE_SIZE
        2: 0,          # ENABLE_PUSH
        3: 1000,       # MAX_CONCURRENT_STREAMS
        4: 131072,     # INITIAL_WINDOW_SIZE
        5: 16384,      # MAX_FRAME_SIZE
        6: 131072,     # MAX_HEADER_LIST_SIZE
    }
    
    # Safari的SETTINGS参数
    SAFARI_SETTINGS = {
        1: 131072,     # HEADER_TABLE_SIZE
        2: 0,          # ENABLE_PUSH
        3: 100,        # MAX_CONCURRENT_STREAMS
        4: 1048576,    # INITIAL_WINDOW_SIZE
        5: 16384,      # MAX_FRAME_SIZE
        6: 0,          # MAX_HEADER_LIST_SIZE
    }
    
    # Chrome的SETTINGS帧发送顺序
    CHROME_SETTINGS_ORDER = [1, 2, 3, 4, 5, 6, 7, 9, 10]
    
    # Firefox的SETTINGS帧发送顺序
    FIREFOX_SETTINGS_ORDER = [1, 2, 3, 4, 5, 6]
    
    # Chrome的WINDOW_UPDATE大小
    CHROME_WINDOW_UPDATE_SIZE = 15663105
    
    # Firefox的WINDOW_UPDATE大小
    FIREFOX_WINDOW_UPDATE_SIZE = 12517377
    
    # Chrome的伪头顺序
    CHROME_PSEUDO_HEADER_ORDER = [
        ":method",
        ":authority",
        ":scheme",
        ":path",
    ]
    
    # Firefox的伪头顺序
    FIREFOX_PSEUDO_HEADER_ORDER = [
        ":method",
        ":path",
        ":authority",
        ":scheme",
    ]
    
    # Chrome的流优先级
    CHROME_STREAM_PRIORITY = {
        0: {  # stream 0
            "weight": 256,
            "exclusive": False,
            "depends_on": 0,
        }
    }
    
    def __init__(self):
        self._browser: str = "chrome"
        self._browser_version: str = "124"
    
    def set_browser(self, browser: str, version: str = "124"):
        """设置浏览器类型和版本"""
        self._browser = browser.lower()
        self._browser_version = version
    
    def generate_http2_config(self) -> Dict[str, Any]:
        """
        生成HTTP/2配置
        
        Returns:
            HTTP/2配置字典
        """
        if self._browser == "chrome":
            return self._generate_chrome_config()
        elif self._browser == "firefox":
            return self._generate_firefox_config()
        elif self._browser == "safari":
            return self._generate_safari_config()
        else:
            return self._generate_chrome_config()
    
    def _generate_chrome_config(self) -> Dict[str, Any]:
        """生成Chrome风格的HTTP/2配置"""
        return {
            "browser": "chrome",
            "version": self._browser_version,
            "settings": self.CHROME_SETTINGS.copy(),
            "settings_order": self.CHROME_SETTINGS_ORDER.copy(),
            "window_update_size": self.CHROME_WINDOW_UPDATE_SIZE,
            "pseudo_header_order": self.CHROME_PSEUDO_HEADER_ORDER.copy(),
            "stream_priority": self.CHROME_STREAM_PRIORITY.copy(),
            "initial_frames": [
                "SETTINGS",
                "WINDOW_UPDATE",
                "PRIORITY",
            ],
            "frame_order": [
                "SETTINGS",
                "WINDOW_UPDATE",
                "HEADERS",
            ],
            "header_table_size": 65536,
            "enable_push": False,
            "max_concurrent_streams": 1000,
            "initial_window_size": 6291456,
            "max_frame_size": 16384,
            "max_header_list_size": 262144,
            "akamai_fingerprint": self._calculate_akamai_fingerprint(
                self.CHROME_SETTINGS,
                self.CHROME_SETTINGS_ORDER,
                self.CHROME_WINDOW_UPDATE_SIZE,
                self.CHROME_PSEUDO_HEADER_ORDER,
            ),
        }
    
    def _generate_firefox_config(self) -> Dict[str, Any]:
        """生成Firefox风格的HTTP/2配置"""
        return {
            "browser": "firefox",
            "version": self._browser_version,
            "settings": self.FIREFOX_SETTINGS.copy(),
            "settings_order": self.FIREFOX_SETTINGS_ORDER.copy(),
            "window_update_size": self.FIREFOX_WINDOW_UPDATE_SIZE,
            "pseudo_header_order": self.FIREFOX_PSEUDO_HEADER_ORDER.copy(),
            "stream_priority": {},
            "initial_frames": [
                "SETTINGS",
                "WINDOW_UPDATE",
            ],
            "frame_order": [
                "SETTINGS",
                "WINDOW_UPDATE",
                "HEADERS",
            ],
            "header_table_size": 65536,
            "enable_push": False,
            "max_concurrent_streams": 1000,
            "initial_window_size": 131072,
            "max_frame_size": 16384,
            "max_header_list_size": 131072,
            "akamai_fingerprint": "",
        }
    
    def _generate_safari_config(self) -> Dict[str, Any]:
        """生成Safari风格的HTTP/2配置"""
        return {
            "browser": "safari",
            "version": self._browser_version,
            "settings": self.SAFARI_SETTINGS.copy(),
            "settings_order": list(self.SAFARI_SETTINGS.keys()),
            "window_update_size": 1048576,
            "pseudo_header_order": [
                ":method",
                ":scheme",
                ":path",
                ":authority",
            ],
            "stream_priority": {},
            "initial_frames": [
                "SETTINGS",
                "WINDOW_UPDATE",
            ],
            "frame_order": [
                "SETTINGS",
                "WINDOW_UPDATE",
                "HEADERS",
            ],
            "header_table_size": 131072,
            "enable_push": False,
            "max_concurrent_streams": 100,
            "initial_window_size": 1048576,
            "max_frame_size": 16384,
            "max_header_list_size": 0,
            "akamai_fingerprint": "",
        }
    
    def _calculate_akamai_fingerprint(self, settings: Dict[int, int],
                                       settings_order: List[int],
                                       window_update: int,
                                       pseudo_headers: List[str]) -> str:
        """
        计算Akamai风格的HTTP/2指纹
        
        格式：
        SETTINGS值的顺序和值;WINDOW_UPDATE大小;伪头顺序
        """
        # SETTINGS部分
        settings_parts = []
        for key in settings_order:
            if key in settings:
                settings_parts.append(f"{key}:{settings[key]}")
        settings_str = ",".join(settings_parts)
        
        # WINDOW_UPDATE部分
        window_update_str = str(window_update)
        
        # 伪头部分
        pseudo_str = ",".join(pseudo_headers)
        
        # 组合
        fingerprint = f"{settings_str};{window_update_str};{pseudo_str}"
        
        return fingerprint
    
    def get_http2_fingerprint(self) -> str:
        """获取HTTP/2指纹"""
        config = self.generate_http2_config()
        return config.get("akamai_fingerprint", "")
    
    def get_pseudo_header_order(self) -> List[str]:
        """获取伪头顺序"""
        if self._browser == "chrome":
            return self.CHROME_PSEUDO_HEADER_ORDER.copy()
        elif self._browser == "firefox":
            return self.FIREFOX_PSEUDO_HEADER_ORDER.copy()
        else:
            return self.CHROME_PSEUDO_HEADER_ORDER.copy()
    
    def get_settings_order(self) -> List[int]:
        """获取SETTINGS参数顺序"""
        if self._browser == "chrome":
            return self.CHROME_SETTINGS_ORDER.copy()
        elif self._browser == "firefox":
            return self.FIREFOX_SETTINGS_ORDER.copy()
        else:
            return self.CHROME_SETTINGS_ORDER.copy()
    
    def get_http2_fingerprint_tips(self) -> List[str]:
        """获取HTTP/2指纹伪造的建议"""
        return [
            "保持SETTINGS参数顺序与真实浏览器一致",
            "保持SETTINGS参数值与真实浏览器一致",
            "保持WINDOW_UPDATE帧大小与真实浏览器一致",
            "保持伪头顺序与真实浏览器一致",
            "保持初始帧发送顺序一致",
            "注意流优先级的设置",
            "保持PUSH_PROMISE处理方式一致",
            "注意帧发送的时间间隔",
        ]
    
    def get_recommended_libraries(self) -> List[str]:
        """获取推荐的HTTP/2指纹伪造库"""
        return [
            "curl-impersonate",
            "requests-impersonate",
            "playwright-stealth",
            "puppeteer-extra-plugin-stealth",
            "undetected-chromedriver",
        ]
