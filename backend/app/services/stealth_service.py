"""
浏览器反检测与指纹管理服务
确保浏览器指纹与代理IP一致性，模拟真实用户行为
"""

from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, field
import random
import time
import hashlib
from fake_useragent import UserAgent
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class BrowserFingerprint:
    """浏览器指纹"""
    user_agent: str
    accept_language: str
    platform: str
    vendor: str
    webgl_vendor: str
    webgl_renderer: str
    screen_width: int
    screen_height: int
    color_depth: int
    pixel_ratio: float
    timezone: str
    timezone_offset: int
    languages: List[str]
    plugins: List[str]
    mime_types: List[str]
    canvas_fingerprint: str
    audio_fingerprint: str
    fonts: List[str]
    hardware_concurrency: int
    device_memory: int
    webdriver: bool = False
    chrome: bool = True
    permissions: bool = True
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "user_agent": self.user_agent,
            "accept_language": self.accept_language,
            "platform": self.platform,
            "vendor": self.vendor,
            "webgl_vendor": self.webgl_vendor,
            "webgl_renderer": self.webgl_renderer,
            "screen_width": self.screen_width,
            "screen_height": self.screen_height,
            "color_depth": self.color_depth,
            "pixel_ratio": self.pixel_ratio,
            "timezone": self.timezone,
            "timezone_offset": self.timezone_offset,
            "languages": self.languages,
            "plugins": self.plugins,
            "mime_types": self.mime_types,
            "canvas_fingerprint": self.canvas_fingerprint,
            "audio_fingerprint": self.audio_fingerprint,
            "fonts": self.fonts,
            "hardware_concurrency": self.hardware_concurrency,
            "device_memory": self.device_memory,
            "webdriver": self.webdriver,
            "chrome": self.chrome,
            "permissions": self.permissions,
        }


class FingerprintGenerator:
    """浏览器指纹生成器"""
    
    # 常见的屏幕分辨率
    SCREEN_RESOLUTIONS = [
        (1920, 1080),
        (2560, 1440),
        (1366, 768),
        (1536, 864),
        (1440, 900),
        (1600, 900),
        (1280, 720),
        (3840, 2160),
    ]
    
    # 常见的像素比
    PIXEL_RATIOS = [1.0, 1.25, 1.5, 2.0]
    
    # 常见的语言设置
    LANGUAGE_SETTINGS = [
        ("zh-CN", ["zh-CN", "zh", "en-US", "en"], "Asia/Shanghai", -480),
        ("en-US", ["en-US", "en"], "America/New_York", 300),
        ("en-GB", ["en-GB", "en"], "Europe/London", 0),
        ("de-DE", ["de-DE", "de", "en-US", "en"], "Europe/Berlin", -60),
        ("fr-FR", ["fr-FR", "fr", "en-US", "en"], "Europe/Paris", -60),
        ("es-ES", ["es-ES", "es", "en-US", "en"], "Europe/Madrid", -60),
        ("ja-JP", ["ja-JP", "ja", "en-US", "en"], "Asia/Tokyo", -540),
        ("ko-KR", ["ko-KR", "ko", "en-US", "en"], "Asia/Seoul", -540),
    ]
    
    # WebGL厂商和渲染器
    WEBGL_CONFIGS = [
        ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
        ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 6GB Direct3D11 vs_5_0 ps_5_0, D3D11)"),
        ("Google Inc. (AMD)", "ANGLE (AMD, AMD Radeon RX 580 Series Direct3D11 vs_5_0 ps_5_0, D3D11)"),
        ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ]
    
    # 常见字体
    COMMON_FONTS = [
        "Arial", "Arial Black", "Arial Narrow", "Calibri", "Cambria", "Cambria Math",
        "Comic Sans MS", "Consolas", "Constantia", "Corbel", "Courier", "Courier New",
        "Georgia", "Helvetica", "Impact", "Lucida Console", "Lucida Sans Unicode",
        "Microsoft Sans Serif", "Palatino Linotype", "Segoe UI", "Tahoma", "Times",
        "Times New Roman", "Trebuchet MS", "Verdana", "Wingdings"
    ]
    
    # 常见插件
    COMMON_PLUGINS = [
        "Chrome PDF Plugin",
        "Chrome PDF Viewer",
        "Native Client",
    ]
    
    def __init__(self):
        self.ua_generator = UserAgent()
    
    def generate_fingerprint(
        self,
        country: Optional[str] = None,
        browser_type: str = "chrome",
        os_type: Optional[str] = None
    ) -> BrowserFingerprint:
        """生成浏览器指纹
        
        Args:
            country: 国家代码，用于设置语言和时区
            browser_type: 浏览器类型: chrome, firefox, safari, edge
            os_type: 操作系统类型: windows, macos, linux
        """
        # 生成User Agent
        if browser_type == "chrome":
            user_agent = self.ua_generator.chrome
        elif browser_type == "firefox":
            user_agent = self.ua_generator.firefox
        elif browser_type == "safari":
            user_agent = self.ua_generator.safari
        else:
            user_agent = self.ua_generator.random
        
        # 根据国家选择语言设置
        lang_setting = self._get_language_by_country(country)
        accept_language = lang_setting[0]
        languages = lang_setting[1]
        timezone = lang_setting[2]
        timezone_offset = lang_setting[3]
        
        # 平台信息
        if os_type == "windows":
            platform = "Win32"
            vendor = "Google Inc."
        elif os_type == "macos":
            platform = "MacIntel"
            vendor = "Google Inc."
        elif os_type == "linux":
            platform = "Linux x86_64"
            vendor = "Google Inc."
        else:
            platform = random.choice(["Win32", "Win32", "Win32", "MacIntel", "Linux x86_64"])
            vendor = "Google Inc."
        
        # 屏幕分辨率
        screen_width, screen_height = random.choice(self.SCREEN_RESOLUTIONS)
        pixel_ratio = random.choice(self.PIXEL_RATIOS)
        color_depth = random.choice([24, 24, 24, 32])
        
        # WebGL信息
        webgl_vendor, webgl_renderer = random.choice(self.WEBGL_CONFIGS)
        
        # 硬件信息
        hardware_concurrency = random.choice([4, 6, 8, 12, 16])
        device_memory = random.choice([4, 8, 16, 32])
        
        # 生成canvas指纹
        canvas_fingerprint = self._generate_canvas_fingerprint()
        
        # 生成音频指纹
        audio_fingerprint = self._generate_audio_fingerprint()
        
        # 随机选择字体子集
        num_fonts = random.randint(20, len(self.COMMON_FONTS))
        fonts = random.sample(self.COMMON_FONTS, min(num_fonts, len(self.COMMON_FONTS)))
        
        return BrowserFingerprint(
            user_agent=user_agent,
            accept_language=accept_language,
            platform=platform,
            vendor=vendor,
            webgl_vendor=webgl_vendor,
            webgl_renderer=webgl_renderer,
            screen_width=screen_width,
            screen_height=screen_height,
            color_depth=color_depth,
            pixel_ratio=pixel_ratio,
            timezone=timezone,
            timezone_offset=timezone_offset,
            languages=languages,
            plugins=self.COMMON_PLUGINS.copy(),
            mime_types=[
                "application/pdf",
                "application/x-google-chrome-pdf",
                "application/x-nacl",
                "application/x-pnacl",
            ],
            canvas_fingerprint=canvas_fingerprint,
            audio_fingerprint=audio_fingerprint,
            fonts=fonts,
            hardware_concurrency=hardware_concurrency,
            device_memory=device_memory,
            webdriver=False,
            chrome=True,
            permissions=True,
        )
    
    def _get_language_by_country(self, country: Optional[str]) -> Tuple[str, List[str], str, int]:
        """根据国家获取语言设置"""
        country_lang_map = {
            "CN": self.LANGUAGE_SETTINGS[0],  # 中文
            "US": self.LANGUAGE_SETTINGS[1],  # 英语美国
            "GB": self.LANGUAGE_SETTINGS[2],  # 英语英国
            "DE": self.LANGUAGE_SETTINGS[3],  # 德语
            "FR": self.LANGUAGE_SETTINGS[4],  # 法语
            "ES": self.LANGUAGE_SETTINGS[5],  # 西班牙语
            "JP": self.LANGUAGE_SETTINGS[6],  # 日语
            "KR": self.LANGUAGE_SETTINGS[7],  # 韩语
        }
        
        if country and country.upper() in country_lang_map:
            return country_lang_map[country.upper()]
        
        return random.choice(self.LANGUAGE_SETTINGS)
    
    def _generate_canvas_fingerprint(self) -> str:
        """生成Canvas指纹"""
        # 模拟Canvas指纹生成
        seed = str(random.random())
        return hashlib.md5(seed.encode()).hexdigest()
    
    def _generate_audio_fingerprint(self) -> str:
        """生成音频指纹"""
        seed = str(random.random())
        return hashlib.sha256(seed.encode()).hexdigest()
    
    def generate_consistent_fingerprint(self, proxy_ip: str, country: Optional[str] = None) -> BrowserFingerprint:
        """生成与代理IP一致的指纹（基于IP哈希生成确定性指纹）"""
        # 使用IP作为种子，确保同一IP总是生成相同的指纹
        random.seed(hashlib.md5(proxy_ip.encode()).hexdigest())
        
        fingerprint = self.generate_fingerprint(country=country)
        
        # 恢复随机种子
        random.seed()
        
        return fingerprint


class HumanBehaviorSimulator:
    """人类行为模拟器"""
    
    def __init__(self):
        self.min_delay = settings.RANDOM_DELAY_MIN
        self.max_delay = settings.RANDOM_DELAY_MAX
    
    def random_delay(self, min_delay: Optional[float] = None, max_delay: Optional[float] = None) -> float:
        """随机延迟
        
        Returns:
            实际延迟时间（秒）
        """
        min_d = min_delay if min_delay is not None else self.min_delay
        max_d = max_delay if max_delay is not None else self.max_delay
        
        delay = random.uniform(min_d, max_d)
        time.sleep(delay)
        return delay
    
    def human_like_scroll(self, page, target_position: Optional[int] = None, steps: int = 10):
        """模拟人类滚动行为
        
        Args:
            page: Playwright页面对象
            target_position: 目标滚动位置，None表示随机
            steps: 滚动步数
        """
        # 获取页面高度
        page_height = page.evaluate("document.body.scrollHeight")
        viewport_height = page.evaluate("window.innerHeight")
        
        if target_position is None:
            target_position = random.randint(0, max(0, page_height - viewport_height))
        
        current_position = page.evaluate("window.scrollY")
        
        # 分多步滚动，每步有随机延迟
        for i in range(steps):
            progress = (i + 1) / steps
            # 使用缓动函数使滚动更自然
            eased_progress = 1 - (1 - progress) ** 2
            next_position = current_position + (target_position - current_position) * eased_progress
            
            page.evaluate(f"window.scrollTo(0, {int(next_position)})")
            
            # 随机延迟
            time.sleep(random.uniform(0.05, 0.2))
    
    def human_like_type(self, element, text: str, min_delay: float = 0.05, max_delay: float = 0.2):
        """模拟人类打字
        
        Args:
            element: Playwright元素对象
            text: 要输入的文本
            min_delay: 最小字符间隔
            max_delay: 最大字符间隔
        """
        for char in text:
            element.type(char, delay=0)
            time.sleep(random.uniform(min_delay, max_delay))
    
    def human_like_click(self, element, delay_before: float = 0.5):
        """模拟人类点击
        
        Args:
            element: Playwright元素对象
            delay_before: 点击前的随机延迟
        """
        # 点击前随机移动鼠标（Playwright会自动处理）
        time.sleep(random.uniform(delay_before * 0.5, delay_before * 1.5))
        element.click()
        # 点击后随机延迟
        time.sleep(random.uniform(0.1, 0.5))
    
    def random_mouse_movements(self, page, duration: float = 2.0):
        """随机鼠标移动
        
        Args:
            page: Playwright页面对象
            duration: 持续时间（秒）
        """
        start_time = time.time()
        viewport = page.viewport_size
        
        while time.time() - start_time < duration:
            x = random.randint(0, viewport["width"])
            y = random.randint(0, viewport["height"])
            page.mouse.move(x, y)
            time.sleep(random.uniform(0.1, 0.3))
    
    def simulate_reading(self, page, min_time: float = 2.0, max_time: float = 10.0):
        """模拟阅读页面
        
        Args:
            page: Playwright页面对象
            min_time: 最少阅读时间
            max_time: 最多阅读时间
        """
        reading_time = random.uniform(min_time, max_time)
        start_time = time.time()
        
        # 滚动浏览
        while time.time() - start_time < reading_time:
            # 随机滚动
            scroll_amount = random.randint(-100, 200)
            page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            time.sleep(random.uniform(0.5, 2.0))
    
    def random_tab_switch(self, context, probability: float = 0.1):
        """随机切换标签页
        
        Args:
            context: Playwright上下文对象
            probability: 切换概率
        """
        if random.random() < probability:
            pages = context.pages
            if len(pages) > 1:
                target_page = random.choice(pages)
                target_page.bring_to_front()
                time.sleep(random.uniform(0.5, 2.0))


class StealthManager:
    """反检测管理器"""
    
    def __init__(self):
        self.fingerprint_generator = FingerprintGenerator()
        self.behavior_simulator = HumanBehaviorSimulator()
    
    def get_stealth_script(self, fingerprint: BrowserFingerprint) -> str:
        """生成反检测脚本
        
        Args:
            fingerprint: 浏览器指纹
            
        Returns:
            JavaScript脚本字符串
        """
        return f"""
        // 移除webdriver标志
        Object.defineProperty(navigator, 'webdriver', {{
            get: () => {str(fingerprint.webdriver).lower()}
        }});
        
        // 覆盖chrome对象
        window.chrome = {{
            runtime: {{}}
        }};
        
        // 覆盖权限API
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({{ state: Notification.permission }}) :
                originalQuery(parameters)
        );
        
        // 覆盖plugins
        Object.defineProperty(navigator, 'plugins', {{
            get: () => [
                {{
                    0: {{type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"}},
                    description: "Portable Document Format",
                    filename: "internal-pdf-viewer",
                    length: 1,
                    name: "Chrome PDF Plugin"
                }},
                {{
                    0: {{type: "application/pdf", suffixes: "pdf", description: ""}},
                    description: "",
                    filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                    length: 1,
                    name: "Chrome PDF Viewer"
                }},
                {{
                    0: {{type: "application/x-nacl", suffixes: "", description: "Native Client Executable"}},
                    1: {{type: "application/x-pnacl", suffixes: "", description: "Portable Native Client Executable"}},
                    description: "",
                    filename: "internal-nacl-plugin",
                    length: 2,
                    name: "Native Client"
                }}
            ]
        }});
        
        // 覆盖languages
        Object.defineProperty(navigator, 'languages', {{
            get: () => {fingerprint.languages}
        }});
        
        // 覆盖language
        Object.defineProperty(navigator, 'language', {{
            get: () => '{fingerprint.accept_language}'
        }});
        
        // 覆盖platform
        Object.defineProperty(navigator, 'platform', {{
            get: () => '{fingerprint.platform}'
        }});
        
        // 覆盖hardwareConcurrency
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: () => {fingerprint.hardware_concurrency}
        }});
        
        // 覆盖deviceMemory
        Object.defineProperty(navigator, 'deviceMemory', {{
            get: () => {fingerprint.device_memory}
        }});
        
        // 覆盖屏幕信息
        Object.defineProperty(screen, 'width', {{
            get: () => {fingerprint.screen_width}
        }});
        Object.defineProperty(screen, 'height', {{
            get: () => {fingerprint.screen_height}
        }});
        Object.defineProperty(screen, 'colorDepth', {{
            get: () => {fingerprint.color_depth}
        }});
        Object.defineProperty(screen, 'pixelDepth', {{
            get: () => {fingerprint.color_depth}
        }});
        
        // 覆盖时区
        const getTimezoneOffset = Date.prototype.getTimezoneOffset;
        Date.prototype.getTimezoneOffset = function() {{
            return {fingerprint.timezone_offset};
        }};
        
        // 覆盖Intl.DateTimeFormat
        const originalDateTimeFormat = Intl.DateTimeFormat;
        Intl.DateTimeFormat = function(locales, options) {{
            if (!options || !options.timeZone) {{
                options = {{...options, timeZone: '{fingerprint.timezone}'}};
            }}
            return new originalDateTimeFormat(locales, options);
        }};
        Intl.DateTimeFormat.prototype = originalDateTimeFormat.prototype;
        
        // 移除automation相关
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_;
        delete window.cdc_asdjflasutopfhvcZLmcfl_;
        delete window.cdc_;
        
        // 覆盖console.debug
        const originalDebug = console.debug;
        console.debug = function(...args) {{
            if (args.length > 0 && typeof args[0] === 'string' && args[0].includes('debugger')) {{
                return;
            }}
            return originalDebug.apply(console, args);
        }};
        """
    
    def apply_stealth(self, page, fingerprint: BrowserFingerprint):
        """应用反检测到页面
        
        Args:
            page: Playwright页面对象
            fingerprint: 浏览器指纹
        """
        stealth_script = self.get_stealth_script(fingerprint)
        page.add_init_script(stealth_script)
        
        logger.debug("Stealth script applied to page")
    
    def create_browser_context(self, browser, fingerprint: BrowserFingerprint, proxy_url: Optional[str] = None):
        """创建带反检测的浏览器上下文
        
        Args:
            browser: Playwright浏览器对象
            fingerprint: 浏览器指纹
            proxy_url: 代理URL
            
        Returns:
            Playwright上下文对象
        """
        context_options = {
            "user_agent": fingerprint.user_agent,
            "viewport": {
                "width": fingerprint.screen_width,
                "height": fingerprint.screen_height,
            },
            "locale": fingerprint.accept_language,
            "timezone_id": fingerprint.timezone,
            "permissions": ["geolocation"],
            "geolocation": self._get_geolocation(fingerprint.timezone),
        }
        
        if proxy_url:
            context_options["proxy"] = {
                "server": proxy_url
            }
        
        context = browser.new_context(**context_options)
        
        # 应用反检测脚本
        stealth_script = self.get_stealth_script(fingerprint)
        context.add_init_script(stealth_script)
        
        logger.info(f"Created stealth browser context with {fingerprint.user_agent[:50]}...")
        
        return context
    
    def _get_geolocation(self, timezone: str) -> Dict[str, float]:
        """根据时区获取大致地理位置"""
        timezone_geo = {
            "Asia/Shanghai": {"latitude": 31.2304, "longitude": 121.4737},
            "America/New_York": {"latitude": 40.7128, "longitude": -74.0060},
            "Europe/London": {"latitude": 51.5074, "longitude": -0.1278},
            "Europe/Berlin": {"latitude": 52.5200, "longitude": 13.4050},
            "Europe/Paris": {"latitude": 48.8566, "longitude": 2.3522},
            "Asia/Tokyo": {"latitude": 35.6762, "longitude": 139.6503},
        }
        return timezone_geo.get(timezone, {"latitude": 0.0, "longitude": 0.0})


# 全局实例
fingerprint_generator = FingerprintGenerator()
behavior_simulator = HumanBehaviorSimulator()
stealth_manager = StealthManager()
