"""
指纹一致性与真实性校验模块
提供指纹一致性检查、真实性验证和多样性保证功能
"""
import random
from typing import Dict, Any, List, Optional, Tuple

from app.core.logging import get_logger

logger = get_logger(__name__)


class FingerprintConsistency:
    """指纹一致性检查器"""
    
    def __init__(self):
        self._rules = []
        self._init_default_rules()
    
    def _init_default_rules(self):
        """初始化默认的一致性规则"""
        self._rules = [
            # UA与平台匹配
            self._check_ua_platform_match,
            # 时区与IP地理位置匹配
            self._check_timezone_geo_match,
            # 语言与时区匹配
            self._check_language_timezone_match,
            # 屏幕分辨率与devicePixelRatio匹配
            self._check_screen_dpr_match,
            # CPU核心数与内存大小匹配
            self._check_cpu_memory_match,
            # WebGL渲染器与GPU信息匹配
            self._check_webgl_gpu_match,
            # 字体列表与操作系统匹配
            self._check_fonts_os_match,
            # 传感器与设备类型匹配
            self._check_sensors_device_match,
        ]
    
    def check_consistency(self, fingerprint: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        检查指纹的一致性
        
        Args:
            fingerprint: 指纹数据
            
        Returns:
            (是否一致, 问题列表)
        """
        issues = []
        
        for rule in self._rules:
            try:
                result = rule(fingerprint)
                if result:
                    issues.append(result)
            except Exception as e:
                logger.warning(f"Error checking consistency rule: {e}")
        
        return (len(issues) == 0, issues)
    
    def _check_ua_platform_match(self, fp: Dict[str, Any]) -> Optional[str]:
        """检查UA与平台是否匹配"""
        user_agent = fp.get("user_agent", "").lower()
        platform = fp.get("platform", "").lower()
        
        if not user_agent or not platform:
            return None
        
        # Windows UA应该对应Win32平台
        if "windows" in user_agent and "win" not in platform:
            return "UserAgent显示Windows但platform不匹配"
        
        # Mac UA应该对应MacIntel平台
        if "mac os" in user_agent and "mac" not in platform:
            return "UserAgent显示macOS但platform不匹配"
        
        # Linux UA应该对应Linux平台
        if "linux" in user_agent and "linux" not in platform:
            return "UserAgent显示Linux但platform不匹配"
        
        return None
    
    def _check_timezone_geo_match(self, fp: Dict[str, Any]) -> Optional[str]:
        """检查时区与地理位置是否匹配"""
        timezone = fp.get("timezone", "")
        country = fp.get("country", "")
        
        if not timezone or not country:
            return None
        
        # 简单的时区-国家匹配检查
        timezone_country_map = {
            "America/New_York": "US",
            "America/Los_Angeles": "US",
            "America/Chicago": "US",
            "Europe/London": "GB",
            "Europe/Berlin": "DE",
            "Europe/Paris": "FR",
            "Asia/Tokyo": "JP",
            "Asia/Shanghai": "CN",
            "Asia/Singapore": "SG",
            "Australia/Sydney": "AU",
        }
        
        expected_country = timezone_country_map.get(timezone)
        if expected_country and expected_country != country:
            return f"时区{timezone}与国家{country}不匹配"
        
        return None
    
    def _check_language_timezone_match(self, fp: Dict[str, Any]) -> Optional[str]:
        """检查语言与时区是否匹配"""
        language = fp.get("language", "").lower()
        timezone = fp.get("timezone", "")
        
        if not language or not timezone:
            return None
        
        # 简单的语言-时区匹配检查
        lang_timezone_map = {
            "en": ["America/New_York", "America/Los_Angeles", "Europe/London", "Australia/Sydney"],
            "zh": ["Asia/Shanghai", "Asia/Hong_Kong", "Asia/Taipei"],
            "ja": ["Asia/Tokyo"],
            "de": ["Europe/Berlin"],
            "fr": ["Europe/Paris"],
            "es": ["Europe/Madrid", "America/Mexico_City", "America/Argentina/Buenos_Aires"],
        }
        
        lang_prefix = language.split("-")[0] if "-" in language else language
        expected_timezones = lang_timezone_map.get(lang_prefix, [])
        
        if expected_timezones and timezone not in expected_timezones:
            return f"语言{language}与时区{timezone}不匹配"
        
        return None
    
    def _check_screen_dpr_match(self, fp: Dict[str, Any]) -> Optional[str]:
        """检查屏幕分辨率与devicePixelRatio是否匹配"""
        screen_width = fp.get("screen_width", 0)
        screen_height = fp.get("screen_height", 0)
        dpr = fp.get("device_pixel_ratio", 1.0)
        
        if not screen_width or not screen_height:
            return None
        
        # 常见的分辨率与DPR组合
        # 1920x1080通常DPR=1
        # 3840x2160通常DPR=2 (4K)
        # 2560x1440通常DPR=1或2
        # Mac的Retina屏幕DPR=2
        
        # 简单检查：分辨率太高但DPR太低
        if screen_width >= 3000 and dpr < 1.5:
            return f"高分辨率({screen_width}x{screen_height})与低DPR({dpr})不匹配"
        
        return None
    
    def _check_cpu_memory_match(self, fp: Dict[str, Any]) -> Optional[str]:
        """检查CPU核心数与内存大小是否匹配"""
        cpu_cores = fp.get("hardware_concurrency", 0)
        memory = fp.get("device_memory", 0)
        
        if not cpu_cores or not memory:
            return None
        
        # CPU核心数与内存应该有一定的正相关
        # 2核通常2-4GB内存
        # 4核通常4-8GB内存
        # 8核通常8-16GB内存
        # 16核通常16-64GB内存
        
        expected_min_memory = cpu_cores  # 至少1GB/核
        expected_max_memory = cpu_cores * 4  # 最多4GB/核
        
        if memory < expected_min_memory:
            return f"CPU核心数({cpu_cores})与内存大小({memory}GB)不匹配（内存太小）"
        
        if memory > expected_max_memory * 2:
            return f"CPU核心数({cpu_cores})与内存大小({memory}GB)不匹配（内存太大）"
        
        return None
    
    def _check_webgl_gpu_match(self, fp: Dict[str, Any]) -> Optional[str]:
        """检查WebGL渲染器与GPU信息是否匹配"""
        webgl_vendor = fp.get("webgl_vendor", "").lower()
        webgl_renderer = fp.get("webgl_renderer", "").lower()
        
        if not webgl_vendor or not webgl_renderer:
            return None
        
        # 厂商与渲染器应该匹配
        if "nvidia" in webgl_vendor and "nvidia" not in webgl_renderer and "geforce" not in webgl_renderer:
            return "WebGL厂商是NVIDIA但渲染器不匹配"
        
        if "intel" in webgl_vendor and "intel" not in webgl_renderer:
            return "WebGL厂商是Intel但渲染器不匹配"
        
        if "amd" in webgl_vendor and "amd" not in webgl_renderer and "radeon" not in webgl_renderer:
            return "WebGL厂商是AMD但渲染器不匹配"
        
        return None
    
    def _check_fonts_os_match(self, fp: Dict[str, Any]) -> Optional[str]:
        """检查字体列表与操作系统是否匹配"""
        fonts = fp.get("fonts", [])
        platform = fp.get("platform", "").lower()
        
        if not fonts or not platform:
            return None
        
        # Windows特有字体
        windows_fonts = ["Arial", "Times New Roman", "Microsoft YaHei", "SimSun", "Tahoma", "Verdana"]
        
        # Mac特有字体
        mac_fonts = ["Helvetica", "Helvetica Neue", "San Francisco", "Menlo", "Monaco"]
        
        # Linux特有字体
        linux_fonts = ["DejaVu Sans", "Ubuntu", "Liberation Sans", "Noto Sans"]
        
        windows_count = sum(1 for f in fonts if f in windows_fonts)
        mac_count = sum(1 for f in fonts if f in mac_fonts)
        linux_count = sum(1 for f in fonts if f in linux_fonts)
        
        if "win" in platform and mac_count > windows_count:
            return "Windows平台但Mac字体更多"
        
        if "mac" in platform and windows_count > mac_count:
            return "Mac平台但Windows字体更多"
        
        if "linux" in platform and windows_count > linux_count:
            return "Linux平台但Windows字体更多"
        
        return None
    
    def _check_sensors_device_match(self, fp: Dict[str, Any]) -> Optional[str]:
        """检查传感器与设备类型是否匹配"""
        device_type = fp.get("device_type", "desktop")
        has_accelerometer = fp.get("accelerometer_supported", False)
        has_gyroscope = fp.get("gyroscope_supported", False)
        has_touch = fp.get("max_touch_points", 0) > 0
        
        if device_type == "desktop":
            # 桌面端通常没有加速度计和陀螺仪
            if has_accelerometer and has_gyroscope:
                return "桌面设备但有移动设备传感器"
        
        if device_type == "mobile":
            # 移动端通常有触摸和传感器
            if not has_touch:
                return "移动设备但不支持触摸"
        
        return None
    
    def add_custom_rule(self, rule_func):
        """添加自定义一致性规则"""
        self._rules.append(rule_func)
    
    def get_consistency_score(self, fingerprint: Dict[str, Any]) -> float:
        """
        获取一致性评分
        
        Args:
            fingerprint: 指纹数据
            
        Returns:
            0.0 - 1.0 的一致性评分
        """
        is_consistent, issues = self.check_consistency(fingerprint)
        
        if is_consistent:
            return 1.0
        
        # 根据问题数量计算评分
        total_rules = len(self._rules)
        passed_rules = total_rules - len(issues)
        
        return max(0.0, passed_rules / total_rules)


class FingerprintAuthenticity:
    """指纹真实性验证器"""
    
    def __init__(self):
        self._known_fingerprints = set()
        self._fingerprint_database = {}
    
    def is_realistic(self, fingerprint: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        检查指纹是否真实
        
        Args:
            fingerprint: 指纹数据
            
        Returns:
            (是否真实, 问题列表)
        """
        issues = []
        
        # 检查是否有明显的假指纹特征
        checks = [
            self._check_default_values,
            self._check_extreme_values,
            self._check_common_fake_patterns,
            self._check_browser_version_consistency,
        ]
        
        for check in checks:
            try:
                result = check(fingerprint)
                if result:
                    issues.append(result)
            except Exception as e:
                logger.warning(f"Error checking authenticity: {e}")
        
        return (len(issues) == 0, issues)
    
    def _check_default_values(self, fp: Dict[str, Any]) -> Optional[str]:
        """检查是否有默认值"""
        # 检查是否有常见的默认值
        user_agent = fp.get("user_agent", "")
        
        if "HeadlessChrome" in user_agent:
            return "UserAgent包含HeadlessChrome，可能是无头浏览器"
        
        if "PhantomJS" in user_agent:
            return "UserAgent包含PhantomJS"
        
        if "Selenium" in user_agent:
            return "UserAgent包含Selenium"
        
        return None
    
    def _check_extreme_values(self, fp: Dict[str, Any]) -> Optional[str]:
        """检查是否有极端值"""
        cpu_cores = fp.get("hardware_concurrency", 0)
        memory = fp.get("device_memory", 0)
        
        if cpu_cores > 64:
            return f"CPU核心数({cpu_cores})异常高"
        
        if memory > 128:
            return f"内存大小({memory}GB)异常高"
        
        if cpu_cores < 1 and cpu_cores != 0:
            return f"CPU核心数({cpu_cores})异常低"
        
        return None
    
    def _check_common_fake_patterns(self, fp: Dict[str, Any]) -> Optional[str]:
        """检查常见的假指纹模式"""
        # 检查是否所有值都是默认的
        plugins = fp.get("plugins", [])
        if len(plugins) == 0:
            return "插件列表为空，可能是假指纹"
        
        fonts = fp.get("fonts", [])
        if len(fonts) == 0:
            return "字体列表为空，可能是假指纹"
        
        return None
    
    def _check_browser_version_consistency(self, fp: Dict[str, Any]) -> Optional[str]:
        """检查浏览器版本是否一致"""
        user_agent = fp.get("user_agent", "")
        
        # 简单检查：UA中的浏览器版本是否合理
        if "Chrome/" in user_agent:
            version_str = user_agent.split("Chrome/")[1].split(" ")[0]
            try:
                major_version = int(version_str.split(".")[0])
                if major_version < 80 or major_version > 200:
                    return f"Chrome版本({major_version})不合理"
            except:
                pass
        
        return None
    
    def get_authenticity_score(self, fingerprint: Dict[str, Any]) -> float:
        """
        获取真实性评分
        
        Args:
            fingerprint: 指纹数据
            
        Returns:
            0.0 - 1.0 的真实性评分
        """
        is_realistic, issues = self.is_realistic(fingerprint)
        
        if is_realistic:
            return 1.0
        
        # 简单计算
        return max(0.0, 1.0 - len(issues) * 0.2)


class FingerprintDiversity:
    """指纹多样性保证器"""
    
    def __init__(self):
        self._used_fingerprints = set()
        self._max_history = 10000
    
    def is_unique(self, fingerprint_hash: str) -> bool:
        """
        检查指纹是否唯一
        
        Args:
            fingerprint_hash: 指纹哈希
            
        Returns:
            是否唯一
        """
        return fingerprint_hash not in self._used_fingerprints
    
    def record_fingerprint(self, fingerprint_hash: str):
        """
        记录已使用的指纹
        
        Args:
            fingerprint_hash: 指纹哈希
        """
        self._used_fingerprints.add(fingerprint_hash)
        
        # 限制历史记录大小
        if len(self._used_fingerprints) > self._max_history:
            # 随机删除一些旧的
            remove_count = len(self._used_fingerprints) - self._max_history
            items = list(self._used_fingerprints)
            for i in range(remove_count):
                self._used_fingerprints.discard(items[i])
    
    def get_diversity_stats(self) -> Dict[str, Any]:
        """获取多样性统计"""
        return {
            "total_used": len(self._used_fingerprints),
            "max_history": self._max_history,
        }
    
    def estimate_combinations(self, fingerprint_config: Dict[str, Any]) -> int:
        """
        估算可能的指纹组合数
        
        Args:
            fingerprint_config: 指纹配置
            
        Returns:
            估算的组合数
        """
        # 简单估算
        combinations = 1
        
        # UA组合
        ua_count = fingerprint_config.get("ua_count", 100)
        combinations *= ua_count
        
        # 屏幕分辨率
        resolutions = fingerprint_config.get("resolutions", 10)
        combinations *= resolutions
        
        # 时区
        timezones = fingerprint_config.get("timezones", 50)
        combinations *= timezones
        
        # 语言
        languages = fingerprint_config.get("languages", 30)
        combinations *= languages
        
        # WebGL配置
        webgl_configs = fingerprint_config.get("webgl_configs", 10)
        combinations *= webgl_configs
        
        # 字体
        font_combinations = fingerprint_config.get("font_combinations", 1000)
        combinations *= font_combinations
        
        return combinations
