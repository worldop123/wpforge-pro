"""
地理位置与IP匹配指纹伪造
提供navigator.geolocation的完整伪造
"""
import random
import hashlib
from typing import Dict, Any, List, Optional, Tuple

from app.core.logging import get_logger

logger = get_logger(__name__)


class GeolocationFingerprint:
    """地理位置指纹伪造器"""
    
    # 主要城市经纬度
    CITY_COORDS = {
        "US": [
            ("New York", 40.7128, -74.0060),
            ("Los Angeles", 34.0522, -118.2437),
            ("Chicago", 41.8781, -87.6298),
            ("Houston", 29.7604, -95.3698),
            ("Phoenix", 33.4484, -112.0740),
            ("Philadelphia", 39.9526, -75.1652),
            ("San Antonio", 29.4241, -98.4936),
            ("San Diego", 32.7157, -117.1611),
            ("Dallas", 32.7767, -96.7970),
            ("San Jose", 37.3382, -121.8863),
        ],
        "GB": [
            ("London", 51.5074, -0.1278),
            ("Manchester", 53.4808, -2.2426),
            ("Birmingham", 52.4862, -1.8904),
            ("Leeds", 53.8008, -1.5491),
            ("Glasgow", 55.8642, -4.2518),
        ],
        "DE": [
            ("Berlin", 52.5200, 13.4050),
            ("Hamburg", 53.5511, 9.9937),
            ("Munich", 48.1351, 11.5820),
            ("Cologne", 50.9375, 6.9603),
            ("Frankfurt", 50.1109, 8.6821),
        ],
        "FR": [
            ("Paris", 48.8566, 2.3522),
            ("Marseille", 43.2965, 5.3698),
            ("Lyon", 45.7640, 4.8357),
            ("Toulouse", 43.6047, 1.4442),
            ("Nice", 43.7102, 7.2620),
        ],
        "JP": [
            ("Tokyo", 35.6762, 139.6503),
            ("Yokohama", 35.4437, 139.6380),
            ("Osaka", 34.6937, 135.5023),
            ("Nagoya", 35.1815, 136.9066),
            ("Sapporo", 43.0618, 141.3545),
        ],
        "CN": [
            ("Shanghai", 31.2304, 121.4737),
            ("Beijing", 39.9042, 116.4074),
            ("Guangzhou", 23.1291, 113.2644),
            ("Shenzhen", 22.5431, 114.0579),
            ("Chengdu", 30.5728, 104.0668),
        ],
        "KR": [
            ("Seoul", 37.5665, 126.9780),
            ("Busan", 35.1796, 129.0756),
            ("Incheon", 37.4563, 126.7052),
            ("Daegu", 35.8714, 128.6014),
            ("Daejeon", 36.3504, 127.3845),
        ],
        "AU": [
            ("Sydney", -33.8688, 151.2093),
            ("Melbourne", -37.8136, 144.9631),
            ("Brisbane", -27.4698, 153.0251),
            ("Perth", -31.9505, 115.8605),
            ("Adelaide", -34.9285, 138.6007),
        ],
        "CA": [
            ("Toronto", 43.6532, -79.3832),
            ("Vancouver", 49.2827, -123.1207),
            ("Montreal", 45.5017, -73.5673),
            ("Calgary", 51.0447, -114.0719),
            ("Ottawa", 45.4215, -75.6972),
        ],
    }
    
    def __init__(self):
        self._enabled: bool = True
        self._latitude: float = 40.7128
        self._longitude: float = -74.0060
        self._accuracy: float = 50.0  # 米
        self._altitude: Optional[float] = None
        self._altitude_accuracy: Optional[float] = None
        self._heading: Optional[float] = None
        self._speed: Optional[float] = None
        self._city: str = "New York"
        self._country: str = "US"
    
    def generate_random_config(self, country: str = "US", 
                                seed: Optional[str] = None):
        """生成随机的地理位置配置"""
        if seed:
            random.seed(hashlib.md5(seed.encode()).hexdigest())
        
        self._country = country
        
        # 选择城市
        city_list = self.CITY_COORDS.get(country, self.CITY_COORDS["US"])
        city_name, lat, lon = random.choice(city_list)
        self._city = city_name
        
        # 添加随机偏移（模拟城市内不同位置）
        self._latitude = lat + random.uniform(-0.05, 0.05)
        self._longitude = lon + random.uniform(-0.05, 0.05)
        
        # 精度
        self._accuracy = random.uniform(10, 100)
        
        # 海拔（可选）
        if random.random() < 0.3:
            self._altitude = random.uniform(0, 500)
            self._altitude_accuracy = random.uniform(10, 50)
        else:
            self._altitude = None
            self._altitude_accuracy = None
        
        if seed:
            random.seed()
    
    def set_config(self, latitude: float, longitude: float, 
                   accuracy: float = 50.0, **kwargs):
        """设置地理位置配置"""
        self._latitude = latitude
        self._longitude = longitude
        self._accuracy = accuracy
        
        for key, value in kwargs.items():
            attr_name = f"_{key}"
            if hasattr(self, attr_name):
                setattr(self, attr_name, value)
    
    def get_injection_script(self) -> str:
        """
        生成地理位置指纹伪造的JavaScript注入脚本
        
        Returns:
            JavaScript代码字符串
        """
        altitude_str = f"{self._altitude}" if self._altitude is not None else "null"
        altitude_accuracy_str = f"{self._altitude_accuracy}" if self._altitude_accuracy is not None else "null"
        heading_str = f"{self._heading}" if self._heading is not None else "null"
        speed_str = f"{self._speed}" if self._speed is not None else "null"
        
        return f"""
        // 地理位置指纹伪造
        (function() {{
            'use strict';
            
            const fakeLatitude = {self._latitude};
            const fakeLongitude = {self._longitude};
            const fakeAccuracy = {self._accuracy};
            const fakeAltitude = {altitude_str};
            const fakeAltitudeAccuracy = {altitude_accuracy_str};
            const fakeHeading = {heading_str};
            const fakeSpeed = {speed_str};
            const geolocationEnabled = {str(self._enabled).lower()};
            
            // 检查geolocation是否存在
            if (!navigator.geolocation) {{
                return;
            }}
            
            const originalGeolocation = navigator.geolocation;
            
            // 创建伪造的Position对象
            function createFakePosition() {{
                return {{
                    coords: {{
                        latitude: fakeLatitude,
                        longitude: fakeLongitude,
                        accuracy: fakeAccuracy,
                        altitude: fakeAltitude,
                        altitudeAccuracy: fakeAltitudeAccuracy,
                        heading: fakeHeading,
                        speed: fakeSpeed,
                    }},
                    timestamp: Date.now(),
                }};
            }}
            
            // Hook getCurrentPosition
            const originalGetCurrentPosition = originalGeolocation.getCurrentPosition;
            originalGeolocation.getCurrentPosition = function(successCallback, errorCallback, options) {{
                if (!geolocationEnabled) {{
                    if (errorCallback) {{
                        errorCallback({{
                            code: 1, // PERMISSION_DENIED
                            message: "User denied Geolocation",
                        }});
                    }}
                    return;
                }}
                
                // 模拟延迟
                setTimeout(function() {{
                    if (successCallback) {{
                        successCallback(createFakePosition());
                    }}
                }}, 100 + Math.random() * 200);
            }};
            
            // Hook watchPosition
            const originalWatchPosition = originalGeolocation.watchPosition;
            originalGeolocation.watchPosition = function(successCallback, errorCallback, options) {{
                if (!geolocationEnabled) {{
                    if (errorCallback) {{
                        errorCallback({{
                            code: 1, // PERMISSION_DENIED
                            message: "User denied Geolocation",
                        }});
                    }}
                    return -1;
                }}
                
                // 立即返回一次位置
                setTimeout(function() {{
                    if (successCallback) {{
                        successCallback(createFakePosition());
                    }}
                }}, 100 + Math.random() * 200);
                
                // 返回一个假的watch ID
                return Math.floor(Math.random() * 10000);
            }};
            
            // Hook clearWatch
            const originalClearWatch = originalGeolocation.clearWatch;
            originalGeolocation.clearWatch = function(watchId) {{
                // 什么都不做
            }};
            
            console.log('Geolocation fingerprint spoofing activated: ' + fakeLatitude.toFixed(4) + ', ' + fakeLongitude.toFixed(4));
        }})();
        """
    
    def get_geolocation_test_script(self) -> str:
        """生成地理位置测试脚本"""
        return """
        // 地理位置指纹测试
        (function() {
            return new Promise(function(resolve, reject) {
                if (!navigator.geolocation) {
                    resolve({ supported: false });
                    return;
                }
                
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        resolve({
                            supported: true,
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude,
                            accuracy: position.coords.accuracy,
                            altitude: position.coords.altitude,
                            altitude_accuracy: position.coords.altitudeAccuracy,
                            heading: position.coords.heading,
                            speed: position.coords.speed,
                            timestamp: position.timestamp,
                        });
                    },
                    function(error) {
                        resolve({
                            supported: true,
                            error: {
                                code: error.code,
                                message: error.message,
                            }
                        });
                    },
                    { timeout: 5000 }
                );
            });
        })();
        """
