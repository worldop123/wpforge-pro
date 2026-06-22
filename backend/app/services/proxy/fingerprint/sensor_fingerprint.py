"""
传感器与其他API指纹伪造
提供各种传感器API和其他现代浏览器API的伪造
"""
import random
import hashlib
from typing import Dict, Any, List, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class SensorFingerprint:
    """传感器指纹伪造器"""
    
    def __init__(self):
        # 电池API
        self._battery_enabled: bool = False
        self._battery_level: float = 1.0
        self._battery_charging: bool = True
        self._battery_charging_time: float = 0
        self._battery_discharging_time: float = float('inf')
        
        # 网络信息API
        self._network_info_enabled: bool = True
        self._network_type: str = "4g"
        self._network_downlink: float = 10.0
        self._network_rtt: int = 50
        self._network_save_data: bool = False
        
        # 振动API
        self._vibration_enabled: bool = False
        
        # 蓝牙API
        self._bluetooth_enabled: bool = False
        
        # USB API
        self._usb_enabled: bool = False
        
        # 游戏手柄API
        self._gamepad_enabled: bool = False
        
        # 语音合成
        self._speech_synthesis_enabled: bool = True
        self._speech_recognition_enabled: bool = False
        
        # 传感器API
        self._ambient_light_sensor: bool = False
        self._proximity_sensor: bool = False
        self._magnetometer: bool = False
        self._accelerometer: bool = False
        self._gyroscope: bool = False
        self._barometer: bool = False
    
    def generate_random_config(self, device_type: str = "desktop",
                                seed: Optional[str] = None):
        """生成随机的传感器配置"""
        if seed:
            random.seed(hashlib.md5(seed.encode()).hexdigest())
        
        if device_type == "mobile":
            # 移动端默认开启更多传感器
            self._battery_enabled = True
            self._vibration_enabled = True
            self._network_info_enabled = True
            self._speech_synthesis_enabled = True
            self._speech_recognition_enabled = random.choice([True, False])
            
            # 传感器
            self._accelerometer = True
            self._gyroscope = True
            self._ambient_light_sensor = True
            self._proximity_sensor = True
            self._magnetometer = random.choice([True, False])
            self._barometer = random.choice([True, False])
            
            # 蓝牙和USB
            self._bluetooth_enabled = random.choice([True, False])
            self._usb_enabled = False
            
            # 游戏手柄
            self._gamepad_enabled = random.choice([True, False])
            
            # 电池状态
            self._battery_level = random.uniform(0.2, 1.0)
            self._battery_charging = random.choice([True, False])
            if self._battery_charging:
                self._battery_charging_time = random.uniform(0, 3600)
                self._battery_discharging_time = float('inf')
            else:
                self._battery_charging_time = float('inf')
                self._battery_discharging_time = random.uniform(3600, 28800)
            
            # 网络类型
            self._network_type = random.choice(["4g", "4g", "4g", "3g", "5g", "wifi"])
            if self._network_type == "wifi":
                self._network_downlink = random.uniform(10, 100)
                self._network_rtt = random.randint(10, 50)
            elif self._network_type == "5g":
                self._network_downlink = random.uniform(50, 500)
                self._network_rtt = random.randint(5, 20)
            elif self._network_type == "4g":
                self._network_downlink = random.uniform(2, 50)
                self._network_rtt = random.randint(30, 100)
            else:  # 3g
                self._network_downlink = random.uniform(0.5, 5)
                self._network_rtt = random.randint(100, 300)
        else:
            # 桌面端默认关闭大多数传感器
            self._battery_enabled = False
            self._vibration_enabled = False
            self._network_info_enabled = True
            self._speech_synthesis_enabled = True
            self._speech_recognition_enabled = random.choice([True, False])
            
            # 传感器
            self._accelerometer = False
            self._gyroscope = False
            self._ambient_light_sensor = False
            self._proximity_sensor = False
            self._magnetometer = False
            self._barometer = False
            
            # 蓝牙和USB
            self._bluetooth_enabled = random.choice([True, False])
            self._usb_enabled = random.choice([True, False])
            
            # 游戏手柄
            self._gamepad_enabled = random.choice([True, False])
            
            # 网络类型（桌面端通常是wifi/有线）
            self._network_type = random.choice(["wifi", "wifi", "ethernet"])
            self._network_downlink = random.uniform(10, 100)
            self._network_rtt = random.randint(5, 50)
        
        self._network_save_data = False
        
        if seed:
            random.seed()
    
    def set_config(self, **kwargs):
        """设置传感器配置"""
        for key, value in kwargs.items():
            attr_name = f"_{key}"
            if hasattr(self, attr_name):
                setattr(self, attr_name, value)
    
    def get_injection_script(self) -> str:
        """
        生成传感器指纹伪造的JavaScript注入脚本
        
        Returns:
            JavaScript代码字符串
        """
        return f"""
        // 传感器与其他API指纹伪造
        (function() {{
            'use strict';
            
            // 电池API
            const batteryEnabled = {str(self._battery_enabled).lower()};
            const batteryLevel = {self._battery_level};
            const batteryCharging = {str(self._battery_charging).lower()};
            const batteryChargingTime = {self._battery_charging_time};
            const batteryDischargingTime = {self._battery_discharging_time};
            
            // 网络信息API
            const networkInfoEnabled = {str(self._network_info_enabled).lower()};
            const networkType = "{self._network_type}";
            const networkDownlink = {self._network_downlink};
            const networkRtt = {self._network_rtt};
            const networkSaveData = {str(self._network_save_data).lower()};
            
            // 振动API
            const vibrationEnabled = {str(self._vibration_enabled).lower()};
            
            // 蓝牙API
            const bluetoothEnabled = {str(self._bluetooth_enabled).lower()};
            
            // USB API
            const usbEnabled = {str(self._usb_enabled).lower()};
            
            // 游戏手柄API
            const gamepadEnabled = {str(self._gamepad_enabled).lower()};
            
            // 语音合成
            const speechSynthesisEnabled = {str(self._speech_synthesis_enabled).lower()};
            const speechRecognitionEnabled = {str(self._speech_recognition_enabled).lower()};
            
            // 传感器
            const ambientLightSensor = {str(self._ambient_light_sensor).lower()};
            const proximitySensor = {str(self._proximity_sensor).lower()};
            const magnetometer = {str(self._magnetometer).lower()};
            const accelerometer = {str(self._accelerometer).lower()};
            const gyroscope = {str(self._gyroscope).lower()};
            const barometer = {str(self._barometer).lower()};
            
            // 电池API伪造
            if (navigator.getBattery) {{
                if (!batteryEnabled) {{
                    // 移除电池API
                    delete navigator.getBattery;
                }} else {{
                    // 伪造电池状态
                    const originalGetBattery = navigator.getBattery;
                    navigator.getBattery = function() {{
                        return originalGetBattery.call(this).then(function(battery) {{
                            // 创建代理对象
                            return new Proxy(battery, {{
                                get: function(target, prop) {{
                                    switch (prop) {{
                                        case 'level':
                                            return batteryLevel;
                                        case 'charging':
                                            return batteryCharging;
                                        case 'chargingTime':
                                            return batteryChargingTime;
                                        case 'dischargingTime':
                                            return batteryDischargingTime;
                                        default:
                                            return target[prop];
                                    }}
                                }}
                            }});
                        }});
                    }};
                }}
            }}
            
            // 网络信息API伪造
            if (navigator.connection || navigator.networkInformation) {{
                const connection = navigator.connection || navigator.networkInformation;
                
                if (!networkInfoEnabled) {{
                    // 移除网络信息API
                    try {{
                        delete navigator.connection;
                        delete navigator.networkInformation;
                    }} catch (e) {{
                        // 某些浏览器可能不允许删除
                    }}
                }} else {{
                    // 伪造网络信息
                    Object.defineProperty(connection, 'effectiveType', {{
                        get: function() {{
                            return networkType;
                        }}
                    }});
                    
                    Object.defineProperty(connection, 'downlink', {{
                        get: function() {{
                            return networkDownlink;
                        }}
                    }});
                    
                    Object.defineProperty(connection, 'rtt', {{
                        get: function() {{
                            return networkRtt;
                        }}
                    }});
                    
                    Object.defineProperty(connection, 'saveData', {{
                        get: function() {{
                            return networkSaveData;
                        }}
                    }});
                }}
            }}
            
            // 振动API伪造
            if (!vibrationEnabled) {{
                try {{
                    delete navigator.vibrate;
                }} catch (e) {{
                    // 某些浏览器可能不允许删除
                }}
            }}
            
            // 蓝牙API伪造
            if (!bluetoothEnabled) {{
                try {{
                    delete navigator.bluetooth;
                }} catch (e) {{
                    // 某些浏览器可能不允许删除
                }}
            }}
            
            // USB API伪造
            if (!usbEnabled) {{
                try {{
                    delete navigator.usb;
                }} catch (e) {{
                    // 某些浏览器可能不允许删除
                }}
            }}
            
            // 游戏手柄API伪造
            if (!gamepadEnabled) {{
                try {{
                    delete navigator.getGamepads;
                    delete navigator.webkitGetGamepads;
                }} catch (e) {{
                    // 某些浏览器可能不允许删除
                }}
            }}
            
            // 语音合成伪造
            if (!speechSynthesisEnabled) {{
                try {{
                    delete window.speechSynthesis;
                }} catch (e) {{
                    // 某些浏览器可能不允许删除
                }}
            }}
            
            // 语音识别伪造
            if (!speechRecognitionEnabled) {{
                try {{
                    delete window.SpeechRecognition;
                    delete window.webkitSpeechRecognition;
                }} catch (e) {{
                    // 某些浏览器可能不允许删除
                }}
            }}
            
            // 传感器API伪造
            // 这些通常是构造函数，可以通过删除来禁用
            if (!ambientLightSensor) {{
                try {{
                    delete window.AmbientLightSensor;
                }} catch (e) {{}}
            }}
            
            if (!proximitySensor) {{
                try {{
                    delete window.ProximitySensor;
                }} catch (e) {{}}
            }}
            
            if (!magnetometer) {{
                try {{
                    delete window.Magnetometer;
                }} catch (e) {{}}
            }}
            
            if (!accelerometer) {{
                try {{
                    delete window.Accelerometer;
                    delete window.LinearAccelerationSensor;
                    delete window.GravitySensor;
                }} catch (e) {{}}
            }}
            
            if (!gyroscope) {{
                try {{
                    delete window.Gyroscope;
                }} catch (e) {{}}
            }}
            
            if (!barometer) {{
                try {{
                    delete window.Barometer;
                    delete window.AbsoluteOrientationSensor;
                    delete window.RelativeOrientationSensor;
                }} catch (e) {{}}
            }}
            
            console.log('Sensor fingerprint spoofing activated');
        }})();
        """
    
    def get_sensor_test_script(self) -> str:
        """生成传感器测试脚本"""
        return """
        // 传感器指纹测试
        (function() {
            const result = {
                battery_supported: false,
                network_info_supported: false,
                network_type: null,
                vibration_supported: false,
                bluetooth_supported: false,
                usb_supported: false,
                gamepad_supported: false,
                speech_synthesis_supported: false,
                speech_recognition_supported: false,
                ambient_light_sensor: false,
                proximity_sensor: false,
                magnetometer: false,
                accelerometer: false,
                gyroscope: false,
                barometer: false,
            };
            
            // 检测电池API
            result.battery_supported = typeof navigator.getBattery !== 'undefined';
            
            // 检测网络信息API
            result.network_info_supported = typeof navigator.connection !== 'undefined' || 
                                           typeof navigator.networkInformation !== 'undefined';
            if (result.network_info_supported) {
                const conn = navigator.connection || navigator.networkInformation;
                result.network_type = conn.effectiveType || null;
            }
            
            // 检测振动API
            result.vibration_supported = typeof navigator.vibrate !== 'undefined';
            
            // 检测蓝牙API
            result.bluetooth_supported = typeof navigator.bluetooth !== 'undefined';
            
            // 检测USB API
            result.usb_supported = typeof navigator.usb !== 'undefined';
            
            // 检测游戏手柄API
            result.gamepad_supported = typeof navigator.getGamepads !== 'undefined' ||
                                      typeof navigator.webkitGetGamepads !== 'undefined';
            
            // 检测语音合成
            result.speech_synthesis_supported = typeof window.speechSynthesis !== 'undefined';
            
            // 检测语音识别
            result.speech_recognition_supported = typeof window.SpeechRecognition !== 'undefined' ||
                                                  typeof window.webkitSpeechRecognition !== 'undefined';
            
            // 检测传感器
            result.ambient_light_sensor = typeof window.AmbientLightSensor !== 'undefined';
            result.proximity_sensor = typeof window.ProximitySensor !== 'undefined';
            result.magnetometer = typeof window.Magnetometer !== 'undefined';
            result.accelerometer = typeof window.Accelerometer !== 'undefined';
            result.gyroscope = typeof window.Gyroscope !== 'undefined';
            result.barometer = typeof window.Barometer !== 'undefined';
            
            return result;
        })();
        """
