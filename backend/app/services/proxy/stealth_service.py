"""
反检测服务
完整的浏览器指纹随机化 + 真人行为模拟 + 网络层反检测
集成了指纹伪造、行为模拟、网络层反检测、验证码绕过等完整功能
"""
import random
import time
import math
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class BrowserFingerprint:
    """浏览器指纹数据类"""
    # User Agent
    user_agent: str
    accept_language: str = "en-US,en;q=0.9"
    
    # Navigator
    platform: str = "Win32"
    vendor: str = "Google Inc."
    product_sub: str = "20030107"
    cookie_enabled: bool = True
    do_not_track: Optional[str] = None
    hardware_concurrency: int = 8
    device_memory: int = 8
    max_touch_points: int = 0
    
    # Screen
    screen_width: int = 1920
    screen_height: int = 1080
    screen_color_depth: int = 24
    screen_pixel_depth: int = 24
    avail_width: int = 1920
    avail_height: int = 1040
    
    # Window
    inner_width: int = 1366
    inner_height: int = 768
    outer_width: int = 1366
    outer_height: int = 768
    
    # Timezone
    timezone: str = "America/New_York"
    timezone_offset: int = 300  # 分钟
    
    # WebGL
    webgl_vendor: str = "Google Inc. (NVIDIA)"
    webgl_renderer: str = "ANGLE (NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0)"
    webgl_version: str = "WebGL 1.0"
    
    # Canvas
    canvas_fp: str = ""
    
    # Audio
    audio_fp: str = ""
    
    # Fonts
    fonts: List[str] = field(default_factory=list)
    
    # Plugins
    plugins: List[str] = field(default_factory=list)
    
    # WebRTC
    webrtc_enabled: bool = True
    
    # 其他
    webdriver: bool = False
    languages: List[str] = field(default_factory=lambda: ["en-US", "en"])
    mime_types: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_agent": self.user_agent,
            "platform": self.platform,
            "screen": {
                "width": self.screen_width,
                "height": self.screen_height,
            },
            "timezone": self.timezone,
            "webgl": {
                "vendor": self.webgl_vendor,
                "renderer": self.webgl_renderer,
            },
        }


class FingerprintGenerator:
    """浏览器指纹生成器"""
    
    # 常见User-Agent列表
    USER_AGENTS = {
        "chrome_windows": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        ],
        "chrome_mac": [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        ],
        "chrome_linux": [
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ],
        "firefox_windows": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        ],
        "firefox_mac": [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
        ],
        "edge_windows": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        ],
        "safari_mac": [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        ],
    }
    
    # 常见屏幕分辨率
    SCREEN_RESOLUTIONS = [
        (1920, 1080),
        (2560, 1440),
        (1366, 768),
        (1536, 864),
        (1440, 900),
        (1280, 720),
        (1600, 900),
        (1680, 1050),
    ]
    
    # 常见时区
    TIMEZONES = {
        "US": [
            ("America/New_York", 300),
            ("America/Chicago", 360),
            ("America/Denver", 420),
            ("America/Los_Angeles", 480),
        ],
        "EU": [
            ("Europe/London", 0),
            ("Europe/Paris", -60),
            ("Europe/Berlin", -60),
            ("Europe/Madrid", -60),
            ("Europe/Rome", -60),
        ],
        "ASIA": [
            ("Asia/Tokyo", -540),
            ("Asia/Shanghai", -480),
            ("Asia/Hong_Kong", -480),
            ("Asia/Singapore", -480),
            ("Asia/Seoul", -540),
        ],
    }
    
    # WebGL供应商/渲染器
    WEBGL_CONFIGS = [
        ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0)"),
        ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0)"),
        ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0)"),
        ("Google Inc. (AMD)", "ANGLE (AMD Radeon RX 6800 XT Direct3D11 vs_5_0 ps_5_0)"),
        ("Google Inc. (Intel)", "ANGLE (Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)"),
        ("Google Inc. (Apple)", "ANGLE (Apple, ANGLE Metal Renderer: Apple M1, Unspecified Version)"),
    ]
    
    # 常见字体
    COMMON_FONTS = [
        "Arial", "Arial Black", "Arial Narrow",
        "Calibri", "Cambria", "Cambria Math",
        "Comic Sans MS", "Consolas", "Courier", "Courier New",
        "Georgia", "Helvetica", "Impact",
        "Lucida Console", "Lucida Sans Unicode",
        "Microsoft Sans Serif", "Palatino Linotype",
        "Segoe UI", "Tahoma", "Times", "Times New Roman",
        "Trebuchet MS", "Verdana", "Wingdings",
    ]
    
    # 常见插件
    COMMON_PLUGINS = [
        "Chrome PDF Plugin",
        "Chrome PDF Viewer",
        "Native Client",
        "Widevine Content Decryption Module",
    ]
    
    def __init__(self):
        pass
    
    def generate(self, 
                 browser: str = "chrome",
                 os: str = "windows",
                 country: str = "US",
                 mobile: bool = False) -> BrowserFingerprint:
        """
        生成随机浏览器指纹
        
        Args:
            browser: 浏览器类型 (chrome, firefox, edge, safari)
            os: 操作系统 (windows, mac, linux)
            country: 国家代码
            mobile: 是否移动端
            
        Returns:
            浏览器指纹
        """
        # 选择User-Agent
        ua_key = f"{browser}_{os}"
        ua_list = self.USER_AGENTS.get(ua_key, self.USER_AGENTS["chrome_windows"])
        user_agent = random.choice(ua_list)
        
        # 选择屏幕分辨率
        if mobile:
            screen_width, screen_height = random.choice([(375, 812), (414, 896), (360, 800)])
        else:
            screen_width, screen_height = random.choice(self.SCREEN_RESOLUTIONS)
        
        # 选择时区
        region = "US"
        if country in ["GB", "DE", "FR", "ES", "IT", "NL"]:
            region = "EU"
        elif country in ["JP", "CN", "HK", "SG", "KR"]:
            region = "ASIA"
        
        timezone_list = self.TIMEZONES.get(region, self.TIMEZONES["US"])
        timezone, timezone_offset = random.choice(timezone_list)
        
        # 选择WebGL配置
        webgl_vendor, webgl_renderer = random.choice(self.WEBGL_CONFIGS)
        
        # 平台
        platform_map = {
            "windows": "Win32",
            "mac": "MacIntel",
            "linux": "Linux x86_64",
        }
        platform = platform_map.get(os, "Win32")
        
        # 硬件配置
        hardware_concurrency = random.choice([4, 6, 8, 12, 16])
        device_memory = random.choice([4, 8, 16, 32])
        
        # 语言
        lang_map = {
            "US": "en-US,en;q=0.9",
            "GB": "en-GB,en;q=0.9",
            "DE": "de-DE,de;q=0.9,en;q=0.8",
            "FR": "fr-FR,fr;q=0.9,en;q=0.8",
            "JP": "ja-JP,ja;q=0.9,en;q=0.8",
            "CN": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        accept_language = lang_map.get(country, "en-US,en;q=0.9")
        
        # 随机选择一些字体
        num_fonts = random.randint(15, len(self.COMMON_FONTS))
        fonts = random.sample(self.COMMON_FONTS, num_fonts)
        
        # 插件
        plugins = self.COMMON_PLUGINS.copy()
        
        # 窗口大小（比屏幕小一些）
        inner_width = screen_width - random.randint(200, 400)
        inner_height = screen_height - random.randint(150, 300)
        
        fingerprint = BrowserFingerprint(
            user_agent=user_agent,
            accept_language=accept_language,
            platform=platform,
            hardware_concurrency=hardware_concurrency,
            device_memory=device_memory,
            screen_width=screen_width,
            screen_height=screen_height,
            inner_width=inner_width,
            inner_height=inner_height,
            outer_width=inner_width + 16,
            outer_height=inner_height + 86,
            timezone=timezone,
            timezone_offset=timezone_offset,
            webgl_vendor=webgl_vendor,
            webgl_renderer=webgl_renderer,
            fonts=fonts,
            plugins=plugins,
            languages=[accept_language.split(",")[0].split(";")[0], "en"],
        )
        
        return fingerprint
    
    def generate_canvas_fingerprint(self) -> str:
        """生成Canvas指纹（模拟）"""
        import hashlib
        random_data = str(random.random()).encode()
        return hashlib.md5(random_data).hexdigest()
    
    def generate_audio_fingerprint(self) -> str:
        """生成Audio指纹（模拟）"""
        import hashlib
        random_data = str(random.random()).encode()
        return hashlib.md5(random_data).hexdigest()


class HumanBehaviorSimulator:
    """真人行为模拟器"""
    
    def __init__(self):
        pass
    
    def generate_mouse_path(self, 
                            start_x: int, start_y: int,
                            end_x: int, end_y: int,
                            steps: Optional[int] = None) -> List[Tuple[int, int]]:
        """
        生成贝塞尔曲线鼠标路径
        
        Args:
            start_x: 起始X坐标
            start_y: 起始Y坐标
            end_x: 结束X坐标
            end_y: 结束Y坐标
            steps: 步数，自动计算
            
        Returns:
            坐标点列表
        """
        if steps is None:
            distance = math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)
            steps = max(int(distance / 10), 10)
            steps = min(steps, 100)
        
        # 生成控制点
        control_x = start_x + (end_x - start_x) * random.uniform(0.3, 0.7) + random.uniform(-50, 50)
        control_y = start_y + (end_y - start_y) * random.uniform(0.3, 0.7) + random.uniform(-50, 50)
        
        path = []
        for i in range(steps + 1):
            t = i / steps
            
            # 二次贝塞尔曲线
            x = (1 - t) ** 2 * start_x + 2 * (1 - t) * t * control_x + t ** 2 * end_x
            y = (1 - t) ** 2 * start_y + 2 * (1 - t) * t * control_y + t ** 2 * end_y
            
            # 添加一些随机抖动
            if i > 0 and i < steps:
                x += random.uniform(-2, 2)
                y += random.uniform(-2, 2)
            
            path.append((int(x), int(y)))
        
        return path
    
    def generate_scroll_path(self, 
                            start_y: int,
                            end_y: int,
                            duration: float = 2.0) -> List[Tuple[float, int]]:
        """
        生成滚动路径（模拟真人滚动）
        
        Args:
            start_y: 起始Y位置
            end_y: 结束Y位置
            duration: 持续时间（秒）
            
        Returns:
            (时间戳, Y位置) 列表
        """
        steps = int(duration * 10)  # 每100ms一个点
        path = []
        
        direction = 1 if end_y > start_y else -1
        distance = abs(end_y - start_y)
        
        for i in range(steps + 1):
            t = i / steps
            
            # 使用缓动函数模拟真人滚动（先快后慢）
            ease_t = 1 - (1 - t) ** 2
            
            current_y = start_y + direction * distance * ease_t
            
            # 添加一些随机波动
            if i > 0 and i < steps:
                current_y += random.uniform(-10, 10)
            
            path.append((i * 0.1, int(current_y)))
        
        return path
    
    def generate_typing_pattern(self, text: str, 
                                base_speed: float = 0.1) -> List[Tuple[float, str]]:
        """
        生成打字模式（模拟真人打字速度）
        
        Args:
            text: 要输入的文本
            base_speed: 基础速度（每个字符秒数）
            
        Returns:
            (时间戳, 字符) 列表
        """
        pattern = []
        current_time = 0.0
        
        for char in text:
            # 随机速度变化
            speed = base_speed * random.uniform(0.5, 2.0)
            
            # 空格和标点符号通常更慢
            if char in " .,!?;":
                speed *= 1.5
            
            # 大写字母需要Shift，更慢
            if char.isupper():
                speed *= 1.3
            
            current_time += speed
            pattern.append((current_time, char))
            
            # 偶尔的暂停
            if random.random() < 0.05:
                current_time += random.uniform(0.2, 0.8)
        
        return pattern
    
    def get_random_pause(self, min_pause: float = 0.5, max_pause: float = 3.0) -> float:
        """获取随机暂停时间（模拟真人思考）"""
        # 使用正态分布
        mean = (min_pause + max_pause) / 2
        std = (max_pause - min_pause) / 4
        pause = random.gauss(mean, std)
        
        # 限制在范围内
        return max(min_pause, min(max_pause, pause))
    
    def get_click_delay(self) -> float:
        """获取点击延迟（模拟鼠标移动到目标的时间）"""
        return random.uniform(0.3, 1.5)
    
    def get_page_stay_time(self, min_time: float = 10, max_time: float = 60) -> float:
        """获取页面停留时间"""
        return random.uniform(min_time, max_time)
    
    def generate_browsing_path(self, num_pages: int = 5) -> List[Dict[str, Any]]:
        """
        生成浏览路径（模拟用户在网站上的浏览行为）
        
        Args:
            num_pages: 浏览页面数
            
        Returns:
            浏览路径列表
        """
        actions = []
        
        for i in range(num_pages):
            action = {
                "action": random.choice(["scroll", "click", "hover", "read", "back"]),
                "duration": self.get_page_stay_time(5, 30),
                "scroll_depth": random.uniform(0.3, 1.0) if i > 0 else random.uniform(0.1, 0.5),
            }
            actions.append(action)
        
        return actions


class StealthService:
    """
    反检测服务
    
    提供完整的浏览器指纹伪造、行为模拟、网络层反检测、验证码绕过等功能
    集成了所有子模块，提供统一的接口
    """
    
    def __init__(self):
        # 核心组件
        self.fingerprint_generator = FingerprintGenerator()
        self.behavior_simulator = HumanBehaviorSimulator()
        
        # 指纹缓存
        self._fingerprints: Dict[str, BrowserFingerprint] = {}
        
        # 子模块（延迟导入，避免循环依赖）
        self._canvas_fp = None
        self._webgl_fp = None
        self._audio_fp = None
        self._font_fp = None
        self._navigator_fp = None
        self._screen_fp = None
        self._timezone_fp = None
        self._geolocation_fp = None
        self._webrtc_fp = None
        self._storage_fp = None
        self._performance_fp = None
        self._sensor_fp = None
        
        # 行为模拟子模块
        self._mouse_behavior = None
        self._click_behavior = None
        self._scroll_behavior = None
        self._keyboard_behavior = None
        self._browsing_behavior = None
        self._interaction_behavior = None
        self._wordpress_behavior = None
        
        # 网络层反检测子模块
        self._request_headers = None
        self._cookie_handler = None
        self._cache_simulator = None
        self._tls_fp = None
        self._http2_fp = None
        
        # 验证码与反爬绕过
        self._captcha_solver = None
        self._captcha_providers = None
        self._cloudflare_bypass = None
        self._antibot_bypass = None
        
        # 一致性校验
        self._fingerprint_consistency = None
        self._fingerprint_authenticity = None
        self._fingerprint_diversity = None
        
        # 检测与验证
        self._fingerprint_tester = None
        self._antibot_tester = None
        self._update_manager = None
        
        # 配置管理
        self._config = None
        self._intensity = "medium"
    
    def _lazy_init(self):
        """延迟初始化子模块"""
        if self._config is None:
            try:
                from app.services.proxy.config import StealthConfig, StealthIntensity
                self._config = StealthConfig()
            except ImportError:
                pass
    
    def generate_fingerprint(self, 
                             session_id: str,
                             browser: str = "chrome",
                             os: str = "windows",
                             country: str = "US") -> BrowserFingerprint:
        """
        为会话生成并缓存浏览器指纹
        
        Args:
            session_id: 会话ID
            browser: 浏览器类型
            os: 操作系统
            country: 国家
            
        Returns:
            浏览器指纹
        """
        if session_id in self._fingerprints:
            return self._fingerprints[session_id]
        
        fingerprint = self.fingerprint_generator.generate(
            browser=browser,
            os=os,
            country=country,
        )
        
        self._fingerprints[session_id] = fingerprint
        logger.info(f"Generated fingerprint for session {session_id}")
        
        return fingerprint
    
    def get_fingerprint(self, session_id: str) -> Optional[BrowserFingerprint]:
        """获取会话的指纹"""
        return self._fingerprints.get(session_id)
    
    def clear_fingerprint(self, session_id: str) -> None:
        """清除会话指纹"""
        if session_id in self._fingerprints:
            del self._fingerprints[session_id]
    
    def get_stealth_scripts(self, fingerprint: BrowserFingerprint) -> str:
        """
        生成反检测JavaScript脚本
        
        Args:
            fingerprint: 浏览器指纹
            
        Returns:
            JavaScript代码
        """
        # 这里生成用于注入浏览器的反检测脚本
        # 包括修改navigator、screen、WebGL等属性
        
        script = f"""
        // Stealth script - injected by WPForge
        (function() {{
            // Override navigator properties
            Object.defineProperty(navigator, 'userAgent', {{
                get: () => '{fingerprint.user_agent}'
            }});
            
            Object.defineProperty(navigator, 'platform', {{
                get: () => '{fingerprint.platform}'
            }});
            
            Object.defineProperty(navigator, 'vendor', {{
                get: () => '{fingerprint.vendor}'
            }});
            
            Object.defineProperty(navigator, 'hardwareConcurrency', {{
                get: () => {fingerprint.hardware_concurrency}
            }});
            
            Object.defineProperty(navigator, 'deviceMemory', {{
                get: () => {fingerprint.device_memory}
            }});
            
            Object.defineProperty(navigator, 'language', {{
                get: () => '{fingerprint.languages[0]}'
            }});
            
            Object.defineProperty(navigator, 'languages', {{
                get: () => {fingerprint.languages}
            }});
            
            // Override webdriver
            Object.defineProperty(navigator, 'webdriver', {{
                get: () => false
            }});
            
            // Override screen properties
            Object.defineProperty(screen, 'width', {{
                get: () => {fingerprint.screen_width}
            }});
            
            Object.defineProperty(screen, 'height', {{
                get: () => {fingerprint.screen_height}
            }});
            
            Object.defineProperty(screen, 'colorDepth', {{
                get: () => {fingerprint.screen_color_depth}
            }});
            
            Object.defineProperty(screen, 'pixelDepth', {{
                get: () => {fingerprint.screen_pixel_depth}
            }});
            
            // Override timezone
            const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
            Date.prototype.getTimezoneOffset = function() {{
                return {fingerprint.timezone_offset};
            }};
            
            // Remove webdriver flag
            delete window.navigator.__proto__.webdriver;
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({{ state: Notification.permission }}) :
                    originalQuery(parameters)
            );
            
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {{
                get: () => {{
                    return {{
                        length: {len(fingerprint.plugins)},
                        0: {{ name: 'Chrome PDF Plugin' }},
                        1: {{ name: 'Chrome PDF Viewer' }},
                        2: {{ name: 'Native Client' }},
                    }};
                }}
            }});
            
            console.log('Stealth mode activated');
        }})();
        """
        
        return script
    
    def get_human_behavior_config(self) -> Dict[str, Any]:
        """获取真人行为配置"""
        return {
            "mouse_movement": {
                "enabled": True,
                "bezier_curve": True,
                "random_jitter": True,
                "speed_variation": True,
            },
            "scrolling": {
                "enabled": True,
                "human_like": True,
                "random_pauses": True,
                "variable_speed": True,
            },
            "typing": {
                "enabled": True,
                "variable_speed": True,
                "random_pauses": True,
                "mistakes": True,
            },
            "delays": {
                "click_delay_min": 0.3,
                "click_delay_max": 1.5,
                "page_stay_min": 10,
                "page_stay_max": 60,
                "action_pause_min": 0.5,
                "action_pause_max": 3.0,
            },
        }
    
    def generate_stealth_headers(self, fingerprint: BrowserFingerprint, 
                                  referer: Optional[str] = None) -> Dict[str, str]:
        """
        生成反检测HTTP头
        
        Args:
            fingerprint: 浏览器指纹
            referer: 来源页面
            
        Returns:
            HTTP头字典
        """
        headers = {
            "User-Agent": fingerprint.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": fingerprint.accept_language,
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none" if not referer else "same-origin",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        
        if referer:
            headers["Referer"] = referer
        
        return headers
    
    def get_anti_detection_tips(self) -> List[str]:
        """获取反检测建议"""
        return [
            "使用住宅代理而非数据中心代理",
            "保持会话一致性（同一IP+同一指纹）",
            "模拟真实的浏览行为模式",
            "避免过于规律的请求间隔",
            "使用真实的浏览器指纹",
            "启用JavaScript和Cookie",
            "模拟鼠标移动和滚动",
            "避免在短时间内发送过多请求",
            "使用随机的User-Agent",
            "模拟真实的打字速度",
        ]
    
    # ===== 扩展功能接口 =====
    
    def set_intensity(self, intensity: str):
        """
        设置反检测强度
        
        Args:
            intensity: 强度级别 (low, medium, high, extreme)
        """
        self._lazy_init()
        if self._config:
            from app.services.proxy.config import StealthIntensity
            self._config.set_intensity(StealthIntensity(intensity))
        self._intensity = intensity
    
    def get_intensity(self) -> str:
        """获取当前反检测强度"""
        return self._intensity
    
    def get_config(self) -> Optional[Dict[str, Any]]:
        """获取当前配置"""
        self._lazy_init()
        if self._config:
            return self._config.get_config()
        return None
    
    def check_fingerprint_consistency(self, fingerprint: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        检查指纹一致性
        
        Args:
            fingerprint: 指纹数据
            
        Returns:
            (是否一致, 问题列表)
        """
        self._lazy_init()
        if self._fingerprint_consistency is None:
            try:
                from app.services.proxy.fingerprint import FingerprintConsistency
                self._fingerprint_consistency = FingerprintConsistency()
            except ImportError:
                return (True, [])
        
        return self._fingerprint_consistency.check_consistency(fingerprint)
    
    def get_consistency_score(self, fingerprint: Dict[str, Any]) -> float:
        """
        获取指纹一致性评分
        
        Args:
            fingerprint: 指纹数据
            
        Returns:
            0.0 - 1.0 的评分
        """
        self._lazy_init()
        if self._fingerprint_consistency is None:
            try:
                from app.services.proxy.fingerprint import FingerprintConsistency
                self._fingerprint_consistency = FingerprintConsistency()
            except ImportError:
                return 1.0
        
        return self._fingerprint_consistency.get_consistency_score(fingerprint)
    
    def get_request_headers(self, url: str, 
                             user_agent: str = "",
                             referer: str = "",
                             browser: str = "chrome") -> Dict[str, str]:
        """
        获取真实浏览器风格的请求头
        
        Args:
            url: 请求URL
            user_agent: User-Agent
            referer: Referer
            browser: 浏览器类型
            
        Returns:
            请求头字典
        """
        if self._request_headers is None:
            try:
                from app.services.proxy.network import RequestHeaderGenerator
                self._request_headers = RequestHeaderGenerator()
            except ImportError:
                # 降级到简单实现
                return self._generate_simple_headers(user_agent, referer)
        
        self._request_headers.set_browser(browser)
        if user_agent:
            self._request_headers.set_user_agent(user_agent)
        
        return self._request_headers.generate_headers(url, referer=referer if referer else None)
    
    def _generate_simple_headers(self, user_agent: str, referer: str) -> Dict[str, str]:
        """生成简单的请求头（降级方案）"""
        headers = {
            "User-Agent": user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        if referer:
            headers["Referer"] = referer
        return headers
    
    def get_cloudflare_bypass(self):
        """获取Cloudflare绕过器"""
        if self._cloudflare_bypass is None:
            try:
                from app.services.proxy.captcha import CloudflareBypass
                self._cloudflare_bypass = CloudflareBypass()
            except ImportError:
                return None
        return self._cloudflare_bypass
    
    def get_antibot_bypass(self):
        """获取反机器人绕过器"""
        if self._antibot_bypass is None:
            try:
                from app.services.proxy.captcha import AntiBotBypass
                self._antibot_bypass = AntiBotBypass()
            except ImportError:
                return None
        return self._antibot_bypass
    
    def get_wordpress_behavior(self):
        """获取WordPress行为模拟器"""
        if self._wordpress_behavior is None:
            try:
                from app.services.proxy.behavior import WordPressBehaviorSimulator
                self._wordpress_behavior = WordPressBehaviorSimulator()
            except ImportError:
                return None
        return self._wordpress_behavior
    
    def get_all_modules_info(self) -> Dict[str, Any]:
        """获取所有模块的信息"""
        return {
            "core": {
                "fingerprint_generator": True,
                "behavior_simulator": True,
            },
            "fingerprint": {
                "canvas": self._canvas_fp is not None,
                "webgl": self._webgl_fp is not None,
                "audio": self._audio_fp is not None,
                "fonts": self._font_fp is not None,
                "navigator": self._navigator_fp is not None,
                "screen": self._screen_fp is not None,
                "timezone": self._timezone_fp is not None,
                "geolocation": self._geolocation_fp is not None,
                "webrtc": self._webrtc_fp is not None,
                "storage": self._storage_fp is not None,
                "performance": self._performance_fp is not None,
                "sensors": self._sensor_fp is not None,
            },
            "behavior": {
                "mouse": self._mouse_behavior is not None,
                "click": self._click_behavior is not None,
                "scroll": self._scroll_behavior is not None,
                "keyboard": self._keyboard_behavior is not None,
                "browsing": self._browsing_behavior is not None,
                "interaction": self._interaction_behavior is not None,
                "wordpress": self._wordpress_behavior is not None,
            },
            "network": {
                "request_headers": self._request_headers is not None,
                "cookie_handler": self._cookie_handler is not None,
                "cache_simulator": self._cache_simulator is not None,
                "tls_fingerprint": self._tls_fp is not None,
                "http2_fingerprint": self._http2_fp is not None,
            },
            "captcha": {
                "captcha_solver": self._captcha_solver is not None,
                "captcha_providers": self._captcha_providers is not None,
                "cloudflare_bypass": self._cloudflare_bypass is not None,
                "antibot_bypass": self._antibot_bypass is not None,
            },
            "consistency": {
                "fingerprint_consistency": self._fingerprint_consistency is not None,
                "fingerprint_authenticity": self._fingerprint_authenticity is not None,
                "fingerprint_diversity": self._fingerprint_diversity is not None,
            },
            "verification": {
                "fingerprint_tester": self._fingerprint_tester is not None,
                "antibot_tester": self._antibot_tester is not None,
                "update_manager": self._update_manager is not None,
            },
            "config": {
                "stealth_config": self._config is not None,
                "current_intensity": self._intensity,
            },
        }


# 全局反检测服务实例
stealth_service = StealthService()
