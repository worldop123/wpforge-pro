"""
浏览器指纹生成器
整合所有指纹模块，生成完整的浏览器指纹
"""
import random
import hashlib
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple

from app.core.logging import get_logger
from app.services.proxy.config.fingerprint_templates import (
    FingerprintTemplate,
    get_template,
    get_random_template,
)

logger = get_logger(__name__)


@dataclass
class BrowserFingerprint:
    """完整的浏览器指纹数据类"""
    # 基础信息
    fingerprint_id: str = ""
    generated_at: float = 0.0
    
    # User Agent
    user_agent: str = ""
    accept_language: str = "en-US,en;q=0.9"
    
    # Navigator
    platform: str = "Win32"
    vendor: str = "Google Inc."
    app_name: str = "Netscape"
    app_code_name: str = "Mozilla"
    app_version: str = ""
    product: str = "Gecko"
    product_sub: str = "20030107"
    cookie_enabled: bool = True
    do_not_track: Optional[str] = None
    hardware_concurrency: int = 8
    device_memory: int = 8
    max_touch_points: int = 0
    on_line: bool = True
    webdriver: bool = False
    
    # Screen
    screen_width: int = 1920
    screen_height: int = 1080
    screen_color_depth: int = 24
    screen_pixel_depth: int = 24
    screen_avail_width: int = 1920
    screen_avail_height: int = 1040
    screen_avail_left: int = 0
    screen_avail_top: int = 0
    screen_left: int = 0
    screen_top: int = 0
    device_pixel_ratio: float = 1.0
    screen_orientation_type: str = "landscape-primary"
    screen_orientation_angle: int = 0
    color_gamut: str = "srgb"
    
    # Window
    inner_width: int = 1366
    inner_height: int = 768
    outer_width: int = 1366
    outer_height: int = 768
    
    # Timezone
    timezone: str = "America/New_York"
    timezone_offset: int = 300  # 分钟
    timezone_dst: bool = False
    
    # WebGL
    webgl_vendor: str = "Google Inc. (NVIDIA)"
    webgl_renderer: str = "ANGLE (NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0)"
    webgl_version: str = "WebGL 1.0"
    webgl_extensions: List[str] = field(default_factory=list)
    webgl_shader_precision: Dict[str, Any] = field(default_factory=dict)
    webgl_antialias: bool = True
    webgl_max_viewport_dims: Tuple[int, int] = (16384, 16384)
    
    # Canvas
    canvas_fp: str = ""
    canvas_text_rendering: str = "optimizeLegibility"
    canvas_image_smoothing: bool = True
    canvas_subpixel_rendering: bool = True
    
    # Audio
    audio_fp: str = ""
    audio_sample_rate: int = 44100
    audio_base_latency: float = 0.01
    audio_output_latency: float = 0.02
    audio_max_channels: int = 2
    
    # Fonts
    fonts: List[str] = field(default_factory=list)
    font_count: int = 0
    
    # Plugins
    plugins: List[str] = field(default_factory=list)
    mime_types: List[str] = field(default_factory=list)
    
    # WebRTC
    webrtc_enabled: bool = True
    webrtc_media_devices: List[Dict[str, str]] = field(default_factory=list)
    webrtc_camera_count: int = 0
    webrtc_microphone_count: int = 0
    
    # Geolocation
    geolocation_enabled: bool = True
    geolocation_latitude: float = 40.7128
    geolocation_longitude: float = -74.0060
    geolocation_accuracy: float = 50.0
    geolocation_altitude: Optional[float] = None
    
    # Storage
    localStorage_enabled: bool = True
    sessionStorage_enabled: bool = True
    indexedDB_enabled: bool = True
    websql_enabled: bool = False
    cookie_enabled_storage: bool = True
    cache_storage_enabled: bool = True
    file_system_access_enabled: bool = False
    storage_quota: int = 5000000000  # 5GB
    
    # Performance
    performance_memory_total: int = 0
    performance_memory_used: int = 0
    performance_memory_limit: int = 0
    performance_now_precision: float = 0.1  # ms
    
    # Sensors
    battery_enabled: bool = False
    network_info_enabled: bool = True
    vibration_enabled: bool = False
    bluetooth_enabled: bool = False
    usb_enabled: bool = False
    gamepad_enabled: bool = False
    speech_synthesis_enabled: bool = True
    speech_recognition_enabled: bool = False
    ambient_light_sensor: bool = False
    proximity_sensor: bool = False
    magnetometer: bool = False
    accelerometer: bool = False
    gyroscope: bool = False
    barometer: bool = False
    
    # 语言
    language: str = "en-US"
    languages: List[str] = field(default_factory=lambda: ["en-US", "en"])
    
    # 权限
    permissions: Dict[str, str] = field(default_factory=dict)
    
    # 其他
    chrome_object: bool = True
    permissions_api: bool = True
    credentials_api: bool = True
    clipboard_api: bool = True
    connection_api: bool = True
    keyboard_api: bool = True
    locks_api: bool = True
    media_devices_api: bool = True
    service_worker_api: bool = True
    storage_api: bool = True
    wake_lock_api: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "fingerprint_id": self.fingerprint_id,
            "user_agent": self.user_agent,
            "platform": self.platform,
            "vendor": self.vendor,
            "hardware_concurrency": self.hardware_concurrency,
            "device_memory": self.device_memory,
            "screen": {
                "width": self.screen_width,
                "height": self.screen_height,
                "color_depth": self.screen_color_depth,
                "pixel_depth": self.screen_pixel_depth,
                "device_pixel_ratio": self.device_pixel_ratio,
            },
            "timezone": self.timezone,
            "timezone_offset": self.timezone_offset,
            "webgl": {
                "vendor": self.webgl_vendor,
                "renderer": self.webgl_renderer,
                "version": self.webgl_version,
            },
            "canvas_fp": self.canvas_fp,
            "audio_fp": self.audio_fp,
            "fonts_count": self.font_count,
            "plugins_count": len(self.plugins),
            "webdriver": self.webdriver,
            "languages": self.languages,
        }
    
    def to_stealth_script(self) -> str:
        """生成反检测JavaScript脚本"""
        # 这个方法会在各个子模块中实现
        return ""


class FingerprintGenerator:
    """浏览器指纹生成器"""
    
    def __init__(self):
        self._cache: Dict[str, BrowserFingerprint] = {}
        self._cache_ttl: int = 3600  # 1小时
        self._max_cache_size: int = 1000
    
    def generate(
        self,
        template_name: Optional[str] = None,
        country: Optional[str] = None,
        browser: Optional[str] = None,
        os: Optional[str] = None,
        mobile: bool = False,
        seed: Optional[str] = None,
    ) -> BrowserFingerprint:
        """
        生成浏览器指纹
        
        Args:
            template_name: 模板名称
            country: 国家代码
            browser: 浏览器类型
            os: 操作系统
            mobile: 是否移动端
            seed: 随机种子（用于确定性生成）
            
        Returns:
            浏览器指纹
        """
        # 设置随机种子
        if seed:
            random.seed(hashlib.md5(seed.encode()).hexdigest())
        
        try:
            # 获取模板
            if template_name:
                template = get_template(template_name)
                if not template:
                    template = get_random_template()
            else:
                # 根据参数选择模板
                template = self._select_template(browser, os, mobile)
            
            # 生成指纹
            fingerprint = self._generate_from_template(template, country)
            
            # 生成指纹ID
            fingerprint.fingerprint_id = self._generate_fingerprint_id(fingerprint)
            fingerprint.generated_at = time.time()
            
            logger.debug(f"Generated fingerprint: {fingerprint.fingerprint_id}")
            
            return fingerprint
        finally:
            # 恢复随机种子
            if seed:
                random.seed()
    
    def _select_template(
        self,
        browser: Optional[str] = None,
        os: Optional[str] = None,
        mobile: bool = False,
    ) -> FingerprintTemplate:
        """根据参数选择模板"""
        if mobile:
            if os == "ios" or browser == "safari":
                return get_template("ios_safari")
            else:
                return get_template("android_chrome")
        
        if browser == "safari" or os == "macos":
            return get_template("mac_safari")
        
        # 默认使用Windows Chrome
        return get_template("windows_chrome")
    
    def _generate_from_template(
        self,
        template: FingerprintTemplate,
        country: Optional[str] = None,
    ) -> BrowserFingerprint:
        """从模板生成指纹"""
        fp = BrowserFingerprint()
        
        # User Agent
        fp.user_agent = random.choice(template.user_agents)
        
        # Navigator
        fp.platform = template.platform
        fp.vendor = template.vendor
        fp.app_name = template.app_name
        fp.app_code_name = template.app_code_name
        fp.app_version = template.app_version
        fp.product_sub = template.product_sub
        fp.cookie_enabled = template.cookie_enabled
        fp.do_not_track = template.do_not_track
        fp.webdriver = template.webdriver
        
        # 硬件
        fp.hardware_concurrency = random.randint(
            template.min_hardware_concurrency,
            template.max_hardware_concurrency
        )
        fp.device_memory = self._match_device_memory(fp.hardware_concurrency)
        
        # 屏幕
        fp.screen_width, fp.screen_height = random.choice(template.screen_resolutions)
        fp.device_pixel_ratio = random.choice(template.pixel_ratios)
        fp.screen_color_depth = random.choice(template.color_depths)
        fp.screen_pixel_depth = fp.screen_color_depth
        
        # 计算可用屏幕尺寸（减去任务栏/Dock）
        if template.os == "macos":
            fp.screen_avail_height = fp.screen_height - 28  # macOS菜单栏
        elif template.os == "windows":
            fp.screen_avail_height = fp.screen_height - 40  # Windows任务栏
        else:
            fp.screen_avail_height = fp.screen_height
        
        fp.screen_avail_width = fp.screen_width
        fp.screen_avail_left = 0
        fp.screen_avail_top = 0
        
        # 窗口大小
        fp.inner_width = fp.screen_width - random.randint(200, 400)
        fp.inner_height = fp.screen_height - random.randint(150, 300)
        fp.outer_width = fp.inner_width + 16
        fp.outer_height = fp.inner_height + 86
        
        # 屏幕方向
        if fp.screen_width > fp.screen_height:
            fp.screen_orientation_type = "landscape-primary"
            fp.screen_orientation_angle = 0
        else:
            fp.screen_orientation_type = "portrait-primary"
            fp.screen_orientation_angle = 0
        
        # 时区
        if country:
            timezone, offset = self._get_timezone_by_country(country, template)
        else:
            timezone, offset = random.choice(template.timezones)
        
        fp.timezone = timezone
        fp.timezone_offset = offset
        
        # WebGL
        fp.webgl_vendor = random.choice(template.webgl_vendors)
        fp.webgl_renderer = random.choice(template.webgl_renderers)
        fp.webgl_extensions = self._generate_webgl_extensions()
        fp.webgl_shader_precision = self._generate_shader_precision()
        
        # 字体
        num_fonts = random.randint(int(len(template.fonts) * 0.7), len(template.fonts))
        fp.fonts = random.sample(template.fonts, min(num_fonts, len(template.fonts)))
        fp.font_count = len(fp.fonts)
        
        # 插件
        fp.plugins = template.plugins.copy()
        fp.mime_types = template.mime_types.copy()
        
        # 语言
        fp.languages = template.languages.copy()
        fp.language = fp.languages[0]
        fp.accept_language = template.accept_language
        
        # 触摸点
        fp.max_touch_points = template.max_touch_points
        
        # Canvas指纹
        fp.canvas_fp = self._generate_canvas_fingerprint_hash()
        
        # Audio指纹
        fp.audio_fp = self._generate_audio_fingerprint_hash()
        fp.audio_sample_rate = random.choice([44100, 48000, 96000])
        
        # 地理位置
        fp.geolocation_latitude, fp.geolocation_longitude = self._get_geolocation_by_country(
            country or "US"
        )
        fp.geolocation_accuracy = random.uniform(10, 100)
        
        # WebRTC
        fp.webrtc_camera_count = random.randint(0, 2)
        fp.webrtc_microphone_count = random.randint(0, 2)
        
        # 性能
        fp.performance_memory_total = random.randint(100000000, 500000000)
        fp.performance_memory_used = random.randint(50000000, 200000000)
        fp.performance_memory_limit = random.randint(500000000, 2000000000)
        
        # 传感器
        self._set_sensor_defaults(fp, template)
        
        # Chrome对象
        fp.chrome_object = template.browser == "chrome"
        
        return fp
    
    def _match_device_memory(self, cpu_cores: int) -> int:
        """根据CPU核心数匹配合适的内存大小"""
        if cpu_cores <= 4:
            return random.choice([4, 8])
        elif cpu_cores <= 8:
            return random.choice([8, 16])
        elif cpu_cores <= 16:
            return random.choice([16, 32])
        else:
            return random.choice([32, 64])
    
    def _get_timezone_by_country(
        self,
        country: str,
        template: FingerprintTemplate,
    ) -> Tuple[str, int]:
        """根据国家获取时区"""
        # 简化实现，实际应该有完整的国家-时区映射
        country_timezones = {
            "US": [("America/New_York", 300), ("America/Chicago", 360), 
                   ("America/Denver", 420), ("America/Los_Angeles", 480)],
            "GB": [("Europe/London", 0)],
            "DE": [("Europe/Berlin", -60)],
            "FR": [("Europe/Paris", -60)],
            "JP": [("Asia/Tokyo", -540)],
            "CN": [("Asia/Shanghai", -480)],
            "KR": [("Asia/Seoul", -540)],
            "AU": [("Australia/Sydney", -600)],
            "CA": [("America/Toronto", 300), ("America/Vancouver", 480)],
        }
        
        tz_list = country_timezones.get(country.upper(), template.timezones)
        return random.choice(tz_list)
    
    def _get_geolocation_by_country(self, country: str) -> Tuple[float, float]:
        """根据国家获取大致经纬度"""
        country_coords = {
            "US": (40.7128, -74.0060),    # 纽约
            "GB": (51.5074, -0.1278),      # 伦敦
            "DE": (52.5200, 13.4050),      # 柏林
            "FR": (48.8566, 2.3522),       # 巴黎
            "JP": (35.6762, 139.6503),     # 东京
            "CN": (31.2304, 121.4737),     # 上海
            "KR": (37.5665, 126.9780),     # 首尔
            "AU": (-33.8688, 151.2093),    # 悉尼
            "CA": (43.6532, -79.3832),     # 多伦多
        }
        
        lat, lon = country_coords.get(country.upper(), (40.7128, -74.0060))
        
        # 添加一些随机偏移（模拟城市内不同位置）
        lat += random.uniform(-0.1, 0.1)
        lon += random.uniform(-0.1, 0.1)
        
        return lat, lon
    
    def _generate_webgl_extensions(self) -> List[str]:
        """生成WebGL扩展列表"""
        all_extensions = [
            "ANGLE_instanced_arrays",
            "EXT_blend_minmax",
            "EXT_color_buffer_half_float",
            "EXT_disjoint_timer_query",
            "EXT_frag_depth",
            "EXT_shader_texture_lod",
            "EXT_sRGB",
            "EXT_texture_filter_anisotropic",
            "OES_element_index_uint",
            "OES_standard_derivatives",
            "OES_texture_float",
            "OES_texture_float_linear",
            "OES_texture_half_float",
            "OES_texture_half_float_linear",
            "OES_vertex_array_object",
            "WEBGL_compressed_texture_s3tc",
            "WEBGL_compressed_texture_s3tc_srgb",
            "WEBGL_debug_renderer_info",
            "WEBGL_debug_shaders",
            "WEBGL_depth_texture",
            "WEBGL_draw_buffers",
            "WEBGL_lose_context",
        ]
        
        # 随机选择子集
        num_extensions = random.randint(15, len(all_extensions))
        return random.sample(all_extensions, num_extensions)
    
    def _generate_shader_precision(self) -> Dict[str, Any]:
        """生成着色器精度配置"""
        return {
            "vertex": {
                "low": {"rangeMin": -128, "rangeMax": 127, "precision": 23},
                "medium": {"rangeMin": -1024, "rangeMax": 1023, "precision": 23},
                "high": {"rangeMin": -65536, "rangeMax": 65535, "precision": 24},
            },
            "fragment": {
                "low": {"rangeMin": -128, "rangeMax": 127, "precision": 23},
                "medium": {"rangeMin": -1024, "rangeMax": 1023, "precision": 23},
                "high": {"rangeMin": -65536, "rangeMax": 65535, "precision": 24},
            },
        }
    
    def _generate_canvas_fingerprint_hash(self) -> str:
        """生成Canvas指纹哈希"""
        # 真实的Canvas指纹需要在浏览器中生成
        # 这里生成一个模拟的哈希值
        random_data = f"canvas_{random.random()}_{time.time()}"
        return hashlib.md5(random_data.encode()).hexdigest()
    
    def _generate_audio_fingerprint_hash(self) -> str:
        """生成Audio指纹哈希"""
        random_data = f"audio_{random.random()}_{time.time()}"
        return hashlib.sha256(random_data.encode()).hexdigest()
    
    def _set_sensor_defaults(self, fp: BrowserFingerprint, template: FingerprintTemplate):
        """设置传感器默认值"""
        # 桌面端默认关闭大多数传感器
        if template.os in ["windows", "macos", "linux"]:
            fp.battery_enabled = False
            fp.vibration_enabled = False
            fp.bluetooth_enabled = False
            fp.usb_enabled = False
            fp.gamepad_enabled = False
            fp.ambient_light_sensor = False
            fp.proximity_sensor = False
            fp.magnetometer = False
            fp.accelerometer = False
            fp.gyroscope = False
            fp.barometer = False
        else:
            # 移动端默认开启更多传感器
            fp.battery_enabled = True
            fp.vibration_enabled = True
            fp.accelerometer = True
            fp.gyroscope = True
            fp.ambient_light_sensor = True
            fp.proximity_sensor = True
            fp.magnetometer = random.choice([True, False])
            fp.barometer = random.choice([True, False])
    
    def _generate_fingerprint_id(self, fp: BrowserFingerprint) -> str:
        """生成指纹ID"""
        data = f"{fp.user_agent}_{fp.platform}_{fp.screen_width}x{fp.screen_height}_{fp.timezone}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def generate_consistent(self, proxy_ip: str, country: Optional[str] = None) -> BrowserFingerprint:
        """生成与代理IP一致的确定性指纹"""
        return self.generate(
            country=country,
            seed=proxy_ip,
        )
    
    def get_cached(self, fingerprint_id: str) -> Optional[BrowserFingerprint]:
        """获取缓存的指纹"""
        fp = self._cache.get(fingerprint_id)
        if fp and time.time() - fp.generated_at < self._cache_ttl:
            return fp
        elif fp:
            # 过期了，删除
            del self._cache[fingerprint_id]
        return None
    
    def cache_fingerprint(self, fingerprint: BrowserFingerprint):
        """缓存指纹"""
        if len(self._cache) >= self._max_cache_size:
            # 清理最旧的
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].generated_at)
            del self._cache[oldest_key]
        
        self._cache[fingerprint.fingerprint_id] = fingerprint


# 全局实例
fingerprint_generator = FingerprintGenerator()
