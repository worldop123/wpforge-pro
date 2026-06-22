"""
时间与时区指纹伪造
提供Date对象和Intl.DateTimeFormat的完整伪造
"""
import random
import hashlib
from typing import Dict, Any, List, Optional, Tuple

from app.core.logging import get_logger

logger = get_logger(__name__)


class TimezoneFingerprint:
    """时区指纹伪造器"""
    
    # 常见时区配置
    TIMEZONES = {
        "US": [
            ("America/New_York", 300, True),
            ("America/Chicago", 360, True),
            ("America/Denver", 420, True),
            ("America/Los_Angeles", 480, True),
            ("America/Phoenix", 420, False),
        ],
        "EU": [
            ("Europe/London", 0, True),
            ("Europe/Paris", -60, True),
            ("Europe/Berlin", -60, True),
            ("Europe/Madrid", -60, True),
            ("Europe/Rome", -60, True),
            ("Europe/Amsterdam", -60, True),
            ("Europe/Stockholm", -60, True),
        ],
        "ASIA": [
            ("Asia/Tokyo", -540, False),
            ("Asia/Shanghai", -480, False),
            ("Asia/Hong_Kong", -480, False),
            ("Asia/Singapore", -480, False),
            ("Asia/Seoul", -540, False),
            ("Asia/Bangkok", -420, False),
            ("Asia/Dubai", -240, False),
        ],
        "OCEANIA": [
            ("Australia/Sydney", -600, True),
            ("Australia/Melbourne", -600, True),
            ("Pacific/Auckland", -720, True),
        ],
    }
    
    def __init__(self):
        self._timezone: str = "America/New_York"
        self._timezone_offset: int = 300  # 分钟
        self._has_dst: bool = True  # 是否有夏令时
        self._clock_drift: float = 0.0  # 时钟漂移（毫秒）
        self._performance_precision: float = 0.1  # performance.now()精度
    
    def generate_random_config(self, country: str = "US", 
                                seed: Optional[str] = None):
        """生成随机的时区配置"""
        if seed:
            random.seed(hashlib.md5(seed.encode()).hexdigest())
        
        # 根据国家选择时区
        region = "US"
        if country in ["GB", "DE", "FR", "ES", "IT", "NL", "SE"]:
            region = "EU"
        elif country in ["JP", "CN", "HK", "SG", "KR", "TH", "AE"]:
            region = "ASIA"
        elif country in ["AU", "NZ"]:
            region = "OCEANIA"
        
        timezone_list = self.TIMEZONES.get(region, self.TIMEZONES["US"])
        self._timezone, self._timezone_offset, self._has_dst = random.choice(timezone_list)
        
        # 时钟漂移（很小）
        self._clock_drift = random.uniform(-100, 100)  # 毫秒
        
        # performance.now()精度
        self._performance_precision = random.choice([0.1, 0.1, 0.1, 1.0])
        
        if seed:
            random.seed()
    
    def set_config(self, timezone: str, timezone_offset: int, 
                   has_dst: bool = True):
        """设置时区配置"""
        self._timezone = timezone
        self._timezone_offset = timezone_offset
        self._has_dst = has_dst
    
    def get_injection_script(self) -> str:
        """
        生成时区指纹伪造的JavaScript注入脚本
        
        Returns:
            JavaScript代码字符串
        """
        return f"""
        // 时间与时区指纹伪造
        (function() {{
            'use strict';
            
            const fakeTimezone = "{self._timezone}";
            const fakeTimezoneOffset = {self._timezone_offset};
            const clockDrift = {self._clock_drift};
            const performancePrecision = {self._performance_precision};
            
            // Hook Date.prototype.getTimezoneOffset
            const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
            Date.prototype.getTimezoneOffset = function() {{
                return fakeTimezoneOffset;
            }};
            
            // Hook Intl.DateTimeFormat
            const originalDateTimeFormat = Intl.DateTimeFormat;
            Intl.DateTimeFormat = function(locales, options) {{
                if (!options) {{
                    options = {{}};
                }}
                
                // 强制使用我们的时区
                options.timeZone = fakeTimezone;
                
                return new originalDateTimeFormat(locales, options);
            }};
            Intl.DateTimeFormat.prototype = originalDateTimeFormat.prototype;
            
            // Hook Intl.DateTimeFormat.resolvedOptions
            const originalResolvedOptions = originalDateTimeFormat.prototype.resolvedOptions;
            originalDateTimeFormat.prototype.resolvedOptions = function() {{
                const options = originalResolvedOptions.call(this);
                options.timeZone = fakeTimezone;
                return options;
            }};
            
            // 时钟漂移模拟（可选，默认关闭以避免问题）
            // const originalDateNow = Date.now;
            // Date.now = function() {{
            //     return originalDateNow() + clockDrift;
            // }};
            // 
            // const originalDateConstructor = Date;
            // Date = function(...args) {{
            //     if (args.length === 0) {{
            //         return new originalDateConstructor(originalDateNow() + clockDrift);
            //     }}
            //     return new originalDateConstructor(...args);
            // }};
            // Date.prototype = originalDateConstructor.prototype;
            // Date.now = originalDateNow;
            // Date.parse = originalDateConstructor.parse;
            // Date.UTC = originalDateConstructor.UTC;
            
            // Hook performance.now() - 降低精度
            if (window.performance && window.performance.now) {{
                const originalPerformanceNow = window.performance.now;
                window.performance.now = function() {{
                    const now = originalPerformanceNow.call(this);
                    // 降低精度
                    return Math.round(now / performancePrecision) * performancePrecision;
                }};
            }}
            
            // Hook performance.timing（如果存在）
            if (window.performance && window.performance.timing) {{
                // 可以在这里微调timing属性
            }}
            
            // Hook performance.memory（Chrome特有）
            if (window.performance && window.performance.memory) {{
                // 可以在这里伪造内存信息
            }}
            
            console.log('Timezone fingerprint spoofing activated: ' + fakeTimezone);
        }})();
        """
    
    def get_timezone_test_script(self) -> str:
        """生成时区测试脚本"""
        return """
        // 时区指纹测试
        (function() {
            const now = new Date();
            const timezoneOffset = now.getTimezoneOffset();
            
            let timezone = null;
            try {
                timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            } catch (e) {
                timezone = null;
            }
            
            return {
                timezone_offset: timezoneOffset,
                timezone: timezone,
                date_string: now.toString(),
                is_dst: timezoneOffset < (new Date(now.getFullYear(), 0, 1).getTimezoneOffset()),
                performance_now_precision: window.performance ? 
                    (window.performance.now() % 1).toFixed(3) : null,
            };
        })();
        """
