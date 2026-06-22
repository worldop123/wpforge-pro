"""
配置与管理模块
提供反检测系统的配置和管理功能
"""
from typing import Dict, Any, Optional, List
from enum import Enum

from app.core.logging import get_logger

logger = get_logger(__name__)


class StealthIntensity(Enum):
    """反检测强度级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


class StealthConfig:
    """反检测配置"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        "intensity": "medium",
        "fingerprint": {
            "enabled": True,
            "canvas": True,
            "webgl": True,
            "audio": True,
            "fonts": True,
            "navigator": True,
            "screen": True,
            "timezone": True,
            "geolocation": True,
            "webrtc": True,
            "storage": True,
            "performance": True,
            "sensors": True,
            "randomization_level": 0.7,
        },
        "behavior": {
            "enabled": True,
            "mouse": True,
            "click": True,
            "scroll": True,
            "keyboard": True,
            "browsing": True,
            "interaction": True,
            "human_like": True,
            "intensity": 0.6,
        },
        "network": {
            "enabled": True,
            "tls_fingerprint": True,
            "http2_fingerprint": True,
            "request_headers": True,
            "cookie_handling": True,
            "cache_simulation": True,
        },
        "proxy": {
            "enabled": True,
            "auto_rotate": False,
            "rotation_strategy": "per_session",
            "geo_matching": True,
            "health_check": True,
        },
        "captcha": {
            "enabled": False,
            "auto_solve": False,
            "budget_limit": 0.0,
            "preferred_provider": "2captcha",
        },
        "wordpress": {
            "enabled": True,
            "login_simulation": True,
            "admin_behavior": True,
            "operation_pacing": True,
            "session_management": True,
        },
        "consistency": {
            "enabled": True,
            "check_consistency": True,
            "check_authenticity": True,
            "ensure_diversity": True,
        },
        "verification": {
            "enabled": False,
            "auto_test": False,
            "test_sites": ["sannysoft", "browserleaks"],
            "min_score": 0.8,
        },
    }
    
    def __init__(self):
        self._config = self.DEFAULT_CONFIG.copy()
        self._intensity = StealthIntensity.MEDIUM
        self._apply_intensity_preset()
    
    def set_intensity(self, intensity: StealthIntensity):
        """设置反检测强度"""
        self._intensity = intensity
        self._apply_intensity_preset()
    
    def get_intensity(self) -> StealthIntensity:
        """获取当前反检测强度"""
        return self._intensity
    
    def _apply_intensity_preset(self):
        """应用强度预设"""
        if self._intensity == StealthIntensity.LOW:
            self._apply_low_intensity()
        elif self._intensity == StealthIntensity.MEDIUM:
            self._apply_medium_intensity()
        elif self._intensity == StealthIntensity.HIGH:
            self._apply_high_intensity()
        elif self._intensity == StealthIntensity.EXTREME:
            self._apply_extreme_intensity()
    
    def _apply_low_intensity(self):
        """低强度配置"""
        self._config["fingerprint"]["randomization_level"] = 0.3
        self._config["behavior"]["intensity"] = 0.3
        self._config["behavior"]["enabled"] = False
        self._config["network"]["tls_fingerprint"] = False
        self._config["network"]["http2_fingerprint"] = False
        self._config["consistency"]["enabled"] = False
    
    def _apply_medium_intensity(self):
        """中等强度配置（默认）"""
        self._config["fingerprint"]["randomization_level"] = 0.7
        self._config["behavior"]["intensity"] = 0.6
        self._config["behavior"]["enabled"] = True
        self._config["network"]["tls_fingerprint"] = True
        self._config["network"]["http2_fingerprint"] = True
        self._config["consistency"]["enabled"] = True
    
    def _apply_high_intensity(self):
        """高强度配置"""
        self._config["fingerprint"]["randomization_level"] = 0.9
        self._config["behavior"]["intensity"] = 0.8
        self._config["behavior"]["enabled"] = True
        self._config["network"]["tls_fingerprint"] = True
        self._config["network"]["http2_fingerprint"] = True
        self._config["proxy"]["auto_rotate"] = True
        self._config["consistency"]["enabled"] = True
        self._config["wordpress"]["enabled"] = True
    
    def _apply_extreme_intensity(self):
        """极致强度配置"""
        self._config["fingerprint"]["randomization_level"] = 1.0
        self._config["behavior"]["intensity"] = 1.0
        self._config["behavior"]["enabled"] = True
        self._config["network"]["tls_fingerprint"] = True
        self._config["network"]["http2_fingerprint"] = True
        self._config["proxy"]["auto_rotate"] = True
        self._config["proxy"]["rotation_strategy"] = "per_request"
        self._config["captcha"]["enabled"] = True
        self._config["captcha"]["auto_solve"] = True
        self._config["consistency"]["enabled"] = True
        self._config["verification"]["enabled"] = True
        self._config["verification"]["auto_test"] = True
    
    def get_config(self) -> Dict[str, Any]:
        """获取完整配置"""
        return self._config.copy()
    
    def set_config(self, config: Dict[str, Any]):
        """设置配置"""
        self._config.update(config)
    
    def get_fingerprint_config(self) -> Dict[str, Any]:
        """获取指纹配置"""
        return self._config.get("fingerprint", {}).copy()
    
    def get_behavior_config(self) -> Dict[str, Any]:
        """获取行为配置"""
        return self._config.get("behavior", {}).copy()
    
    def get_network_config(self) -> Dict[str, Any]:
        """获取网络配置"""
        return self._config.get("network", {}).copy()
    
    def get_proxy_config(self) -> Dict[str, Any]:
        """获取代理配置"""
        return self._config.get("proxy", {}).copy()
    
    def get_captcha_config(self) -> Dict[str, Any]:
        """获取验证码配置"""
        return self._config.get("captcha", {}).copy()
    
    def get_wordpress_config(self) -> Dict[str, Any]:
        """获取WordPress配置"""
        return self._config.get("wordpress", {}).copy()
    
    def get_consistency_config(self) -> Dict[str, Any]:
        """获取一致性配置"""
        return self._config.get("consistency", {}).copy()
    
    def get_verification_config(self) -> Dict[str, Any]:
        """获取验证配置"""
        return self._config.get("verification", {}).copy()
    
    def is_feature_enabled(self, feature: str) -> bool:
        """检查某个功能是否启用"""
        parts = feature.split(".")
        current = self._config
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return False
        
        if isinstance(current, bool):
            return current
        return False
    
    def enable_feature(self, feature: str):
        """启用某个功能"""
        parts = feature.split(".")
        current = self._config
        
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        current[parts[-1]] = True
    
    def disable_feature(self, feature: str):
        """禁用某个功能"""
        parts = feature.split(".")
        current = self._config
        
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        current[parts[-1]] = False
    
    def export_config(self) -> Dict[str, Any]:
        """导出配置"""
        return {
            "intensity": self._intensity.value,
            "config": self._config.copy(),
        }
    
    def import_config(self, config_data: Dict[str, Any]):
        """导入配置"""
        if "intensity" in config_data:
            self._intensity = StealthIntensity(config_data["intensity"])
        
        if "config" in config_data:
            self._config.update(config_data["config"])
    
    def reset_to_default(self):
        """重置为默认配置"""
        self._config = self.DEFAULT_CONFIG.copy()
        self._intensity = StealthIntensity.MEDIUM
    
    def get_intensity_description(self) -> str:
        """获取强度级别描述"""
        descriptions = {
            StealthIntensity.LOW: "低强度：基础指纹伪造，速度最快，适合简单场景",
            StealthIntensity.MEDIUM: "中等强度：完整指纹伪造，正常速度，适合大多数场景",
            StealthIntensity.HIGH: "高强度：完整指纹+行为模拟，较慢，适合严格检测的网站",
            StealthIntensity.EXTREME: "极致强度：所有反检测全开，速度最慢但最安全，适合极端严格的场景",
        }
        return descriptions.get(self._intensity, "")
    
    def get_all_intensity_levels(self) -> List[Dict[str, Any]]:
        """获取所有强度级别"""
        return [
            {
                "level": StealthIntensity.LOW.value,
                "name": "低强度",
                "description": "基础指纹伪造，速度最快",
                "performance_impact": "低",
            },
            {
                "level": StealthIntensity.MEDIUM.value,
                "name": "中等强度",
                "description": "完整指纹伪造，正常速度",
                "performance_impact": "中",
            },
            {
                "level": StealthIntensity.HIGH.value,
                "name": "高强度",
                "description": "完整指纹+行为模拟，较慢",
                "performance_impact": "高",
            },
            {
                "level": StealthIntensity.EXTREME.value,
                "name": "极致强度",
                "description": "所有反检测全开，最安全",
                "performance_impact": "极高",
            },
        ]
