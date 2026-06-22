"""
存储相关指纹伪造
提供localStorage、sessionStorage、IndexedDB、WebSQL等存储API的伪造
"""
import random
import hashlib
from typing import Dict, Any, List, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class StorageFingerprint:
    """存储指纹伪造器"""
    
    def __init__(self):
        self._local_storage_enabled: bool = True
        self._session_storage_enabled: bool = True
        self._indexed_db_enabled: bool = True
        self._websql_enabled: bool = False
        self._cookie_enabled: bool = True
        self._cache_storage_enabled: bool = True
        self._file_system_access_enabled: bool = False
        self._storage_quota: int = 5000000000  # 5GB
        
        # 模拟存储容量限制
        self._local_storage_limit: int = 5000000  # 5MB
        self._session_storage_limit: int = 5000000  # 5MB
    
    def generate_random_config(self, seed: Optional[str] = None):
        """生成随机的存储配置"""
        if seed:
            random.seed(hashlib.md5(seed.encode()).hexdigest())
        
        # 大多数浏览器都支持这些
        self._local_storage_enabled = True
        self._session_storage_enabled = True
        self._indexed_db_enabled = True
        self._cookie_enabled = True
        self._cache_storage_enabled = True
        
        # WebSQL主要在旧版Safari和Chrome中支持
        self._websql_enabled = random.choice([False, False, False, True])
        
        # File System Access API比较新
        self._file_system_access_enabled = random.choice([False, False, True])
        
        # 存储配额
        self._storage_quota = random.choice([
            2000000000,  # 2GB
            5000000000,  # 5GB
            10000000000,  # 10GB
        ])
        
        if seed:
            random.seed()
    
    def set_config(self, **kwargs):
        """设置存储配置"""
        for key, value in kwargs.items():
            attr_name = f"_{key}"
            if hasattr(self, attr_name):
                setattr(self, attr_name, value)
    
    def get_injection_script(self) -> str:
        """
        生成存储指纹伪造的JavaScript注入脚本
        
        Returns:
            JavaScript代码字符串
        """
        return f"""
        // 存储相关指纹伪造
        (function() {{
            'use strict';
            
            const localStorageEnabled = {str(self._local_storage_enabled).lower()};
            const sessionStorageEnabled = {str(self._session_storage_enabled).lower()};
            const indexedDBEnabled = {str(self._indexed_db_enabled).lower()};
            const websqlEnabled = {str(self._websql_enabled).lower()};
            const cookieEnabled = {str(self._cookie_enabled).lower()};
            const cacheStorageEnabled = {str(self._cache_storage_enabled).lower()};
            const fileSystemAccessEnabled = {str(self._file_system_access_enabled).lower()};
            const storageQuota = {self._storage_quota};
            
            // localStorage伪造
            if (!localStorageEnabled) {{
                try {{
                    Object.defineProperty(window, 'localStorage', {{
                        get: function() {{
                            throw new Error('Access denied');
                        }}
                    }});
                }} catch (e) {{
                    // 某些浏览器可能不允许修改
                }}
            }}
            
            // sessionStorage伪造
            if (!sessionStorageEnabled) {{
                try {{
                    Object.defineProperty(window, 'sessionStorage', {{
                        get: function() {{
                            throw new Error('Access denied');
                        }}
                    }});
                }} catch (e) {{
                    // 某些浏览器可能不允许修改
                }}
            }}
            
            // IndexedDB伪造
            if (!indexedDBEnabled) {{
                try {{
                    Object.defineProperty(window, 'indexedDB', {{
                        get: function() {{
                            return undefined;
                        }}
                    }});
                }} catch (e) {{
                    // 某些浏览器可能不允许修改
                }}
            }}
            
            // WebSQL伪造
            if (!websqlEnabled) {{
                try {{
                    delete window.openDatabase;
                }} catch (e) {{
                    // 某些浏览器可能不允许修改
                }}
            }}
            
            // Cookie伪造
            if (!cookieEnabled) {{
                try {{
                    Object.defineProperty(navigator, 'cookieEnabled', {{
                        get: function() {{
                            return false;
                        }}
                    }});
                }} catch (e) {{
                    // 某些浏览器可能不允许修改
                }}
            }}
            
            // Cache Storage伪造
            if (!cacheStorageEnabled) {{
                try {{
                    Object.defineProperty(window, 'caches', {{
                        get: function() {{
                            return undefined;
                        }}
                    }});
                }} catch (e) {{
                    // 某些浏览器可能不允许修改
                }}
            }}
            
            // File System Access API伪造
            if (!fileSystemAccessEnabled) {{
                try {{
                    delete window.showOpenFilePicker;
                    delete window.showSaveFilePicker;
                    delete window.showDirectoryPicker;
                }} catch (e) {{
                    // 某些浏览器可能不允许修改
                }}
            }}
            
            // 存储配额伪造
            if (navigator.storage && navigator.storage.estimate) {{
                const originalEstimate = navigator.storage.estimate;
                navigator.storage.estimate = function() {{
                    return originalEstimate.call(this).then(function(estimate) {{
                        // 修改配额
                        estimate.quota = storageQuota;
                        return estimate;
                    }});
                }};
            }}
            
            console.log('Storage fingerprint spoofing activated');
        }})();
        """
    
    def get_storage_test_script(self) -> str:
        """生成存储测试脚本"""
        return """
        // 存储指纹测试
        (function() {
            const result = {
                localStorage_supported: false,
                sessionStorage_supported: false,
                indexedDB_supported: false,
                websql_supported: false,
                cookie_enabled: false,
                cache_storage_supported: false,
                file_system_access_supported: false,
            };
            
            // 检测localStorage
            try {
                result.localStorage_supported = typeof localStorage !== 'undefined';
            } catch (e) {
                result.localStorage_supported = false;
            }
            
            // 检测sessionStorage
            try {
                result.sessionStorage_supported = typeof sessionStorage !== 'undefined';
            } catch (e) {
                result.sessionStorage_supported = false;
            }
            
            // 检测IndexedDB
            try {
                result.indexedDB_supported = typeof indexedDB !== 'undefined';
            } catch (e) {
                result.indexedDB_supported = false;
            }
            
            // 检测WebSQL
            try {
                result.websql_supported = typeof window.openDatabase !== 'undefined';
            } catch (e) {
                result.websql_supported = false;
            }
            
            // 检测Cookie
            try {
                result.cookie_enabled = navigator.cookieEnabled;
            } catch (e) {
                result.cookie_enabled = false;
            }
            
            // 检测Cache Storage
            try {
                result.cache_storage_supported = typeof caches !== 'undefined';
            } catch (e) {
                result.cache_storage_supported = false;
            }
            
            // 检测File System Access API
            try {
                result.file_system_access_supported = typeof window.showOpenFilePicker !== 'undefined';
            } catch (e) {
                result.file_system_access_supported = false;
            }
            
            return result;
        })();
        """
