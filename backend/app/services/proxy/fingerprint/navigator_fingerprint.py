"""
Navigator对象全面伪造
提供Navigator对象的完整属性伪造
"""
import random
import hashlib
from typing import Dict, Any, List, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class NavigatorFingerprint:
    """Navigator指纹伪造器"""
    
    # 常见插件配置
    CHROME_PLUGINS = [
        {
            "name": "Chrome PDF Plugin",
            "filename": "internal-pdf-viewer",
            "description": "Portable Document Format",
            "mimeTypes": [
                {"type": "application/x-google-chrome-pdf", "suffixes": "pdf", "description": "Portable Document Format"}
            ]
        },
        {
            "name": "Chrome PDF Viewer",
            "filename": "mhjfbmdgcfjbbpaeojofohoefgiehjai",
            "description": "",
            "mimeTypes": [
                {"type": "application/pdf", "suffixes": "pdf", "description": ""}
            ]
        },
        {
            "name": "Native Client",
            "filename": "internal-nacl-plugin",
            "description": "",
            "mimeTypes": [
                {"type": "application/x-nacl", "suffixes": "", "description": "Native Client Executable"},
                {"type": "application/x-pnacl", "suffixes": "", "description": "Portable Native Client Executable"}
            ]
        },
    ]
    
    def __init__(self):
        self._user_agent: str = ""
        self._platform: str = "Win32"
        self._vendor: str = "Google Inc."
        self._app_name: str = "Netscape"
        self._app_code_name: str = "Mozilla"
        self._app_version: str = ""
        self._product: str = "Gecko"
        self._product_sub: str = "20030107"
        self._language: str = "en-US"
        self._languages: List[str] = ["en-US", "en"]
        self._hardware_concurrency: int = 8
        self._device_memory: int = 8
        self._max_touch_points: int = 0
        self._cookie_enabled: bool = True
        self._do_not_track: Optional[str] = None
        self._on_line: bool = True
        self._webdriver: bool = False
        self._plugins: List[Dict[str, Any]] = []
        self._mime_types: List[Dict[str, Any]] = []
        self._permissions: Dict[str, str] = {}
    
    def set_config(self, **kwargs):
        """设置Navigator配置"""
        for key, value in kwargs.items():
            attr_name = f"_{key}"
            if hasattr(self, attr_name):
                setattr(self, attr_name, value)
    
    def generate_random_config(self, browser: str = "chrome", os: str = "windows", 
                                country: str = "US", seed: Optional[str] = None):
        """生成随机的Navigator配置"""
        if seed:
            random.seed(hashlib.md5(seed.encode()).hexdigest())
        
        # 平台
        platform_map = {
            "windows": "Win32",
            "macos": "MacIntel",
            "linux": "Linux x86_64",
            "android": "Linux armv8l",
            "ios": "iPhone",
        }
        self._platform = platform_map.get(os, "Win32")
        
        # 供应商
        if browser == "chrome":
            self._vendor = "Google Inc."
        elif browser == "safari":
            self._vendor = "Apple Computer, Inc."
        elif browser == "firefox":
            self._vendor = ""
        else:
            self._vendor = "Google Inc."
        
        # 硬件
        if os in ["windows", "macos", "linux"]:
            self._hardware_concurrency = random.choice([4, 6, 8, 12, 16])
            self._device_memory = self._match_device_memory(self._hardware_concurrency)
            self._max_touch_points = 0
        else:
            self._hardware_concurrency = random.choice([4, 6, 8])
            self._device_memory = random.choice([4, 6, 8])
            self._max_touch_points = random.choice([5, 10])
        
        # 语言
        lang_map = {
            "US": ("en-US", ["en-US", "en"]),
            "GB": ("en-GB", ["en-GB", "en"]),
            "DE": ("de-DE", ["de-DE", "de", "en-US", "en"]),
            "FR": ("fr-FR", ["fr-FR", "fr", "en-US", "en"]),
            "JP": ("ja-JP", ["ja-JP", "ja", "en-US", "en"]),
            "CN": ("zh-CN", ["zh-CN", "zh", "en-US", "en"]),
            "KR": ("ko-KR", ["ko-KR", "ko", "en-US", "en"]),
        }
        self._language, self._languages = lang_map.get(country, ("en-US", ["en-US", "en"]))
        
        # 插件
        if browser == "chrome":
            self._plugins = self.CHROME_PLUGINS.copy()
        else:
            self._plugins = []
        
        # MIME类型
        self._mime_types = []
        for plugin in self._plugins:
            for mime in plugin.get("mimeTypes", []):
                self._mime_types.append(mime)
        
        # 权限
        self._permissions = {
            "geolocation": "prompt",
            "notifications": "default",
            "push": "prompt",
            "midi": "prompt",
            "camera": "prompt",
            "microphone": "prompt",
            "background-sync": "prompt",
            "ambient-light-sensor": "prompt",
            "accelerometer": "prompt",
            "gyroscope": "prompt",
            "magnetometer": "prompt",
            "clipboard-read": "prompt",
            "clipboard-write": "granted",
            "payment-handler": "prompt",
            "persistent-storage": "prompt",
        }
        
        if seed:
            random.seed()
    
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
    
    def get_injection_script(self) -> str:
        """
        生成Navigator指纹伪造的JavaScript注入脚本
        
        Returns:
            JavaScript代码字符串
        """
        languages_json = str(self._languages).replace("'", '"')
        plugins_json = str(self._plugins).replace("'", '"')
        
        return f"""
        // Navigator对象全面伪造
        (function() {{
            'use strict';
            
            // 保存原始navigator
            const originalNavigator = navigator;
            
            // 创建代理对象来伪造navigator属性
            const navigatorProxy = new Proxy(originalNavigator, {{
                get: function(target, prop) {{
                    switch (prop) {{
                        case 'userAgent':
                            return "{self._user_agent}";
                        case 'platform':
                            return "{self._platform}";
                        case 'vendor':
                            return "{self._vendor}";
                        case 'appName':
                            return "{self._app_name}";
                        case 'appCodeName':
                            return "{self._app_code_name}";
                        case 'appVersion':
                            return "{self._app_version}";
                        case 'product':
                            return "{self._product}";
                        case 'productSub':
                            return "{self._product_sub}";
                        case 'language':
                            return "{self._language}";
                        case 'languages':
                            return {languages_json};
                        case 'hardwareConcurrency':
                            return {self._hardware_concurrency};
                        case 'deviceMemory':
                            return {self._device_memory};
                        case 'maxTouchPoints':
                            return {self._max_touch_points};
                        case 'cookieEnabled':
                            return {str(self._cookie_enabled).lower()};
                        case 'doNotTrack':
                            return {f'"{self._do_not_track}"' if self._do_not_track else 'null'};
                        case 'onLine':
                            return {str(self._on_line).lower()};
                        case 'webdriver':
                            return false;
                        case 'plugins':
                            return getFakePlugins();
                        case 'mimeTypes':
                            return getFakeMimeTypes();
                        case 'permissions':
                            return getFakePermissions();
                        case 'credentials':
                            return target.credentials;
                        case 'clipboard':
                            return target.clipboard;
                        case 'connection':
                        case 'networkInformation':
                            return getFakeNetworkInfo();
                        case 'keyboard':
                            return target.keyboard;
                        case 'locks':
                            return target.locks;
                        case 'mediaDevices':
                            return target.mediaDevices;
                        case 'serviceWorker':
                            return target.serviceWorker;
                        case 'storage':
                            return target.storage;
                        case 'wakeLock':
                            return target.wakeLock;
                        default:
                            return target[prop];
                    }}
                }}
            }});
            
            // 替换navigator
            Object.defineProperty(window, 'navigator', {{
                get: function() {{
                    return navigatorProxy;
                }}
            }});
            
            // 伪造plugins
            function getFakePlugins() {{
                const fakePlugins = {plugins_json};
                
                const pluginArray = [];
                for (let i = 0; i < fakePlugins.length; i++) {{
                    const plugin = fakePlugins[i];
                    
                    // 创建plugin对象
                    const pluginObj = {{
                        name: plugin.name,
                        filename: plugin.filename,
                        description: plugin.description,
                        length: plugin.mimeTypes.length,
                    }};
                    
                    // 添加mimeTypes
                    for (let j = 0; j < plugin.mimeTypes.length; j++) {{
                        pluginObj[j] = {{
                            type: plugin.mimeTypes[j].type,
                            suffixes: plugin.mimeTypes[j].suffixes,
                            description: plugin.mimeTypes[j].description,
                            enabledPlugin: pluginObj,
                        }};
                    }}
                    
                    // namedItem方法
                    pluginObj.namedItem = function(name) {{
                        for (let j = 0; j < plugin.mimeTypes.length; j++) {{
                            if (plugin.mimeTypes[j].type === name) {{
                                return pluginObj[j];
                            }}
                        }}
                        return null;
                    }};
                    
                    pluginArray.push(pluginObj);
                }}
                
                // 添加数组方法
                pluginArray.namedItem = function(name) {{
                    for (let i = 0; i < pluginArray.length; i++) {{
                        if (pluginArray[i].name === name) {{
                            return pluginArray[i];
                        }}
                    }}
                    return null;
                }};
                
                return pluginArray;
            }}
            
            // 伪造mimeTypes
            function getFakeMimeTypes() {{
                const fakePlugins = {plugins_json};
                const mimeTypeArray = [];
                
                for (let i = 0; i < fakePlugins.length; i++) {{
                    const plugin = fakePlugins[i];
                    for (let j = 0; j < plugin.mimeTypes.length; j++) {{
                        const mimeType = {{
                            type: plugin.mimeTypes[j].type,
                            suffixes: plugin.mimeTypes[j].suffixes,
                            description: plugin.mimeTypes[j].description,
                            enabledPlugin: null, // 稍后设置
                        }};
                        mimeTypeArray.push(mimeType);
                    }}
                }}
                
                // 添加namedItem方法
                mimeTypeArray.namedItem = function(name) {{
                    for (let i = 0; i < mimeTypeArray.length; i++) {{
                        if (mimeTypeArray[i].type === name) {{
                            return mimeTypeArray[i];
                        }}
                    }}
                    return null;
                }};
                
                return mimeTypeArray;
            }}
            
            // 伪造permissions
            function getFakePermissions() {{
                const originalPermissions = navigator.permissions;
                
                if (!originalPermissions) {{
                    return originalPermissions;
                }}
                
                const fakePermissions = {{
                    query: function(permissionDescriptor) {{
                        const name = permissionDescriptor.name;
                        
                        // 常见权限的默认值
                        const permissionDefaults = {{
                            'geolocation': 'prompt',
                            'notifications': 'default',
                            'push': 'prompt',
                            'midi': 'prompt',
                            'camera': 'prompt',
                            'microphone': 'prompt',
                            'background-sync': 'prompt',
                            'ambient-light-sensor': 'prompt',
                            'accelerometer': 'prompt',
                            'gyroscope': 'prompt',
                            'magnetometer': 'prompt',
                            'clipboard-read': 'prompt',
                            'clipboard-write': 'granted',
                            'payment-handler': 'prompt',
                            'persistent-storage': 'prompt',
                        }};
                        
                        const state = permissionDefaults[name] || 'prompt';
                        
                        return Promise.resolve({{
                            state: state,
                            onchange: null,
                        }});
                    }}
                }};
                
                return fakePermissions;
            }}
            
            // 伪造网络信息
            function getFakeNetworkInfo() {{
                return {{
                    downlink: 10,
                    effectiveType: '4g',
                    onchange: null,
                    rtt: 50,
                    saveData: false,
                }};
            }}
            
            // 移除webdriver标志
            delete navigator.__proto__.webdriver;
            
            // 移除automation相关属性
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_;
            delete window.cdc_asdjflasutopfhvcZLmcfl_;
            delete window.cdc_;
            
            // 添加chrome对象（如果是Chrome浏览器）
            if ("{self._vendor}".indexOf('Google') !== -1) {{
                window.chrome = {{
                    runtime: {{
                        onMessage: {{
                            addListener: function() {{}},
                        }},
                        sendMessage: function() {{}},
                    }},
                    loadTimes: function() {{ return {{}}; }},
                    csi: function() {{ return {{}}; }},
                }};
            }}
            
            console.log('Navigator fingerprint spoofing activated');
        }})();
        """
