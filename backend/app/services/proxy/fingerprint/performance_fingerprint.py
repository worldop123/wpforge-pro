"""
性能与硬件指纹伪造
提供performance API和硬件相关API的伪造
"""
import random
import hashlib
from typing import Dict, Any, List, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class PerformanceFingerprint:
    """性能指纹伪造器"""
    
    def __init__(self):
        # performance.memory（Chrome特有）
        self._memory_total: int = 0
        self._memory_used: int = 0
        self._memory_limit: int = 0
        
        # performance.now()精度
        self._now_precision: float = 0.1
        
        # 硬件并发数和内存
        self._hardware_concurrency: int = 8
        self._device_memory: int = 8
        
        # GPU信息（与WebGL匹配）
        self._gpu_vendor: str = ""
        self._gpu_renderer: str = ""
    
    def generate_random_config(self, seed: Optional[str] = None):
        """生成随机的性能配置"""
        if seed:
            random.seed(hashlib.md5(seed.encode()).hexdigest())
        
        # 内存配置（Chrome performance.memory）
        self._memory_total = random.randint(100000000, 500000000)
        self._memory_used = random.randint(50000000, int(self._memory_total * 0.8))
        self._memory_limit = random.randint(500000000, 2000000000)
        
        # performance.now()精度
        self._now_precision = random.choice([0.1, 0.1, 0.1, 1.0])
        
        # 硬件配置
        self._hardware_concurrency = random.choice([4, 6, 8, 12, 16])
        self._device_memory = self._match_device_memory(self._hardware_concurrency)
        
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
    
    def set_config(self, **kwargs):
        """设置性能配置"""
        for key, value in kwargs.items():
            attr_name = f"_{key}"
            if hasattr(self, attr_name):
                setattr(self, attr_name, value)
    
    def get_injection_script(self) -> str:
        """
        生成性能指纹伪造的JavaScript注入脚本
        
        Returns:
            JavaScript代码字符串
        """
        return f"""
        // 性能与硬件指纹伪造
        (function() {{
            'use strict';
            
            const memoryTotal = {self._memory_total};
            const memoryUsed = {self._memory_used};
            const memoryLimit = {self._memory_limit};
            const nowPrecision = {self._now_precision};
            const hardwareConcurrency = {self._hardware_concurrency};
            const deviceMemory = {self._device_memory};
            
            // Hook performance.memory（Chrome特有）
            if (window.performance && window.performance.memory) {{
                const originalMemory = window.performance.memory;
                
                // 创建代理对象来伪造内存信息
                const memoryProxy = new Proxy(originalMemory, {{
                    get: function(target, prop) {{
                        switch (prop) {{
                            case 'totalJSHeapSize':
                                return memoryTotal;
                            case 'usedJSHeapSize':
                                return memoryUsed;
                            case 'jsHeapSizeLimit':
                                return memoryLimit;
                            default:
                                return target[prop];
                        }}
                    }}
                }});
                
                Object.defineProperty(window.performance, 'memory', {{
                    get: function() {{
                        return memoryProxy;
                    }}
                }});
            }}
            
            // Hook performance.now() - 降低精度
            if (window.performance && window.performance.now) {{
                const originalNow = window.performance.now;
                window.performance.now = function() {{
                    const now = originalNow.call(this);
                    // 降低精度
                    return Math.round(now / nowPrecision) * nowPrecision;
                }};
            }}
            
            // Hook performance.timing（如果存在）
            if (window.performance && window.performance.timing) {{
                // 可以在这里微调timing属性
                // 注意：这可能会影响性能监控工具
            }}
            
            // Hook hardwareConcurrency
            if (navigator.hardwareConcurrency) {{
                Object.defineProperty(navigator, 'hardwareConcurrency', {{
                    get: function() {{
                        return hardwareConcurrency;
                    }}
                }});
            }}
            
            // Hook deviceMemory
            if (navigator.deviceMemory) {{
                Object.defineProperty(navigator, 'deviceMemory', {{
                    get: function() {{
                        return deviceMemory;
                    }}
                }});
            }}
            
            console.log('Performance fingerprint spoofing activated');
        }})();
        """
    
    def get_performance_test_script(self) -> str:
        """生成性能测试脚本"""
        return """
        // 性能指纹测试
        (function() {
            const result = {
                performance_supported: false,
                memory_supported: false,
                memory_total: 0,
                memory_used: 0,
                memory_limit: 0,
                now_precision: 0,
                hardware_concurrency: 0,
                device_memory: 0,
            };
            
            // 检测performance支持
            if (window.performance) {
                result.performance_supported = true;
                
                // 检测memory支持
                if (window.performance.memory) {
                    result.memory_supported = true;
                    result.memory_total = window.performance.memory.totalJSHeapSize;
                    result.memory_used = window.performance.memory.usedJSHeapSize;
                    result.memory_limit = window.performance.memory.jsHeapSizeLimit;
                }
                
                // 检测now()精度
                const now = window.performance.now();
                result.now_precision = (now % 1).toFixed(3);
            }
            
            // 检测hardwareConcurrency
            if (navigator.hardwareConcurrency) {
                result.hardware_concurrency = navigator.hardwareConcurrency;
            }
            
            // 检测deviceMemory
            if (navigator.deviceMemory) {
                result.device_memory = navigator.deviceMemory;
            }
            
            return result;
        })();
        """
