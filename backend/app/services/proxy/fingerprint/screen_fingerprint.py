"""
Screen对象完全伪造
提供Screen对象的完整属性伪造
"""
import random
import hashlib
from typing import Dict, Any, List, Optional, Tuple

from app.core.logging import get_logger

logger = get_logger(__name__)


class ScreenFingerprint:
    """Screen指纹伪造器"""
    
    # 常见屏幕分辨率
    DESKTOP_RESOLUTIONS = [
        (1920, 1080),
        (2560, 1440),
        (1366, 768),
        (1536, 864),
        (1440, 900),
        (1600, 900),
        (1280, 720),
        (1680, 1050),
        (1920, 1200),
        (3840, 2160),
        (2560, 1080),
        (3440, 1440),
    ]
    
    MOBILE_RESOLUTIONS = [
        (375, 812),
        (390, 844),
        (414, 896),
        (428, 926),
        (360, 780),
        (412, 915),
        (393, 851),
        (360, 800),
    ]
    
    TABLET_RESOLUTIONS = [
        (768, 1024),
        (834, 1194),
        (1024, 1366),
        (820, 1180),
        (810, 1080),
    ]
    
    # 常见像素比
    PIXEL_RATIOS = [1.0, 1.25, 1.5, 2.0, 2.5, 3.0]
    
    # 颜色深度
    COLOR_DEPTHS = [24, 24, 24, 32]
    
    def __init__(self):
        self._width: int = 1920
        self._height: int = 1080
        self._avail_width: int = 1920
        self._avail_height: int = 1040
        self._avail_left: int = 0
        self._avail_top: int = 0
        self._left: int = 0
        self._top: int = 0
        self._color_depth: int = 24
        self._pixel_depth: int = 24
        self._device_pixel_ratio: float = 1.0
        self._orientation_type: str = "landscape-primary"
        self._orientation_angle: int = 0
        self._color_gamut: str = "srgb"
        self._os_type: str = "windows"
    
    def generate_random_config(self, device_type: str = "desktop", 
                                os_type: str = "windows",
                                seed: Optional[str] = None):
        """生成随机的Screen配置"""
        if seed:
            random.seed(hashlib.md5(seed.encode()).hexdigest())
        
        self._os_type = os_type
        
        # 选择分辨率
        if device_type == "mobile":
            self._width, self._height = random.choice(self.MOBILE_RESOLUTIONS)
        elif device_type == "tablet":
            self._width, self._height = random.choice(self.TABLET_RESOLUTIONS)
        else:
            self._width, self._height = random.choice(self.DESKTOP_RESOLUTIONS)
        
        # 像素比
        if device_type == "mobile":
            self._device_pixel_ratio = random.choice([2.0, 2.5, 3.0, 3.5])
        elif device_type == "tablet":
            self._device_pixel_ratio = random.choice([1.5, 2.0, 2.5])
        else:
            self._device_pixel_ratio = random.choice(self.PIXEL_RATIOS)
        
        # 颜色深度
        self._color_depth = random.choice(self.COLOR_DEPTHS)
        self._pixel_depth = self._color_depth
        
        # 可用屏幕尺寸（减去任务栏/Dock）
        if os_type == "macos":
            self._avail_height = self._height - 28  # macOS菜单栏
        elif os_type == "windows":
            self._avail_height = self._height - 40  # Windows任务栏
        elif os_type == "linux":
            self._avail_height = self._height - 32  # Linux任务栏
        else:
            self._avail_height = self._height
        
        self._avail_width = self._width
        self._avail_left = 0
        self._avail_top = 0
        
        # 屏幕位置（多显示器场景）
        self._left = 0
        self._top = 0
        
        # 屏幕方向
        if self._width > self._height:
            self._orientation_type = "landscape-primary"
            self._orientation_angle = 0
        else:
            self._orientation_type = "portrait-primary"
            self._orientation_angle = 0
        
        # 色彩空间
        self._color_gamut = random.choice(["srgb", "srgb", "srgb", "display-p3"])
        
        if seed:
            random.seed()
    
    def set_config(self, **kwargs):
        """设置Screen配置"""
        for key, value in kwargs.items():
            attr_name = f"_{key}"
            if hasattr(self, attr_name):
                setattr(self, attr_name, value)
    
    def get_injection_script(self) -> str:
        """
        生成Screen指纹伪造的JavaScript注入脚本
        
        Returns:
            JavaScript代码字符串
        """
        return f"""
        // Screen对象完全伪造
        (function() {{
            'use strict';
            
            // 保存原始screen
            const originalScreen = screen;
            
            // 创建代理对象来伪造screen属性
            const screenProxy = new Proxy(originalScreen, {{
                get: function(target, prop) {{
                    switch (prop) {{
                        case 'width':
                            return {self._width};
                        case 'height':
                            return {self._height};
                        case 'availWidth':
                            return {self._avail_width};
                        case 'availHeight':
                            return {self._avail_height};
                        case 'availLeft':
                            return {self._avail_left};
                        case 'availTop':
                            return {self._avail_top};
                        case 'left':
                            return {self._left};
                        case 'top':
                            return {self._top};
                        case 'colorDepth':
                            return {self._color_depth};
                        case 'pixelDepth':
                            return {self._pixel_depth};
                        case 'orientation':
                            return getFakeOrientation();
                        case 'colorGamut':
                            return "{self._color_gamut}";
                        case 'onchange':
                            return null;
                        default:
                            return target[prop];
                    }}
                }},
                set: function(target, prop, value) {{
                    // 阻止修改某些属性
                    if (['width', 'height', 'colorDepth', 'pixelDepth'].includes(prop)) {{
                        return false;
                    }}
                    target[prop] = value;
                    return true;
                }}
            }});
            
            // 替换screen
            Object.defineProperty(window, 'screen', {{
                get: function() {{
                    return screenProxy;
                }}
            }});
            
            // 伪造devicePixelRatio
            Object.defineProperty(window, 'devicePixelRatio', {{
                get: function() {{
                    return {self._device_pixel_ratio};
                }}
            }});
            
            // 伪造屏幕方向
            function getFakeOrientation() {{
                return {{
                    type: "{self._orientation_type}",
                    angle: {self._orientation_angle},
                    onchange: null,
                    addEventListener: function() {{}},
                    removeEventListener: function() {{}},
                    dispatchEvent: function() {{ return true; }},
                    lock: function() {{ return Promise.reject(new Error('Not implemented')); }},
                    unlock: function() {{}},
                }};
            }}
            
            // 伪造窗口大小（可选，影响视口）
            // 注意：这可能会影响页面布局，默认不启用
            
            console.log('Screen fingerprint spoofing activated');
        }})();
        """
    
    def get_screen_fingerprint_test_script(self) -> str:
        """生成Screen指纹测试脚本"""
        return """
        // Screen指纹测试
        (function() {
            return {
                width: screen.width,
                height: screen.height,
                availWidth: screen.availWidth,
                availHeight: screen.availHeight,
                availLeft: screen.availLeft,
                availTop: screen.availTop,
                colorDepth: screen.colorDepth,
                pixelDepth: screen.pixelDepth,
                devicePixelRatio: window.devicePixelRatio,
                orientation_type: screen.orientation ? screen.orientation.type : null,
                orientation_angle: screen.orientation ? screen.orientation.angle : null,
                innerWidth: window.innerWidth,
                innerHeight: window.innerHeight,
                outerWidth: window.outerWidth,
                outerHeight: window.outerHeight,
                colorGamut: screen.colorGamut || null,
            };
        })();
        """
