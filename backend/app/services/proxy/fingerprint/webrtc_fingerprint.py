"""
WebRTC防泄漏与伪造
提供RTCPeerConnection Hook和mediaDevices伪造
"""
import random
import hashlib
from typing import Dict, Any, List, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class WebRTCFingerprint:
    """WebRTC指纹伪造器"""
    
    def __init__(self):
        self._enabled: bool = True
        self._prevent_leak: bool = True  # 防止本地IP泄漏
        self._use_proxy_ip: bool = True  # 是否返回代理IP
        self._proxy_ip: str = ""
        
        # 媒体设备
        self._camera_count: int = 1
        self._microphone_count: int = 1
        self._speaker_count: int = 1
        self._device_id_prefix: str = ""
    
    def generate_random_config(self, device_type: str = "desktop",
                                seed: Optional[str] = None):
        """生成随机的WebRTC配置"""
        if seed:
            random.seed(hashlib.md5(seed.encode()).hexdigest())
        
        # 设备数量
        if device_type == "mobile":
            self._camera_count = random.choice([1, 2])
            self._microphone_count = random.choice([1, 2])
            self._speaker_count = random.choice([1, 2])
        else:
            self._camera_count = random.choice([0, 1, 2])
            self._microphone_count = random.choice([0, 1, 2])
            self._speaker_count = random.choice([1, 2, 3])
        
        # 设备ID前缀
        self._device_id_prefix = hashlib.md5(str(random.random()).encode()).hexdigest()[:8]
        
        if seed:
            random.seed()
    
    def set_config(self, **kwargs):
        """设置WebRTC配置"""
        for key, value in kwargs.items():
            attr_name = f"_{key}"
            if hasattr(self, attr_name):
                setattr(self, attr_name, value)
    
    def get_injection_script(self) -> str:
        """
        生成WebRTC指纹伪造的JavaScript注入脚本
        
        Returns:
            JavaScript代码字符串
        """
        return f"""
        // WebRTC防泄漏与伪造
        (function() {{
            'use strict';
            
            const preventLeak = {str(self._prevent_leak).lower()};
            const useProxyIp = {str(self._use_proxy_ip).lower()};
            const proxyIp = "{self._proxy_ip}";
            const cameraCount = {self._camera_count};
            const microphoneCount = {self._microphone_count};
            const speakerCount = {self._speaker_count};
            const deviceIdPrefix = "{self._device_id_prefix}";
            
            // Hook RTCPeerConnection - 防止本地IP泄漏
            if (window.RTCPeerConnection || window.webkitRTCPeerConnection || window.mozRTCPeerConnection) {{
                const OriginalPeerConnection = window.RTCPeerConnection || window.webkitRTCPeerConnection || window.mozRTCPeerConnection;
                
                // 创建代理构造函数
                function PatchedPeerConnection(config, constraints) {{
                    if (preventLeak && config) {{
                        // 修改ICE服务器配置，防止泄漏
                        if (!config.iceServers) {{
                            config.iceServers = [];
                        }}
                        
                        // 可以在这里添加更多的防泄漏配置
                    }}
                    
                    const pc = new OriginalPeerConnection(config, constraints);
                    
                    // Hook createOffer
                    const originalCreateOffer = pc.createOffer;
                    pc.createOffer = function(options) {{
                        return originalCreateOffer.call(this, options).then(function(offer) {{
                            if (preventLeak) {{
                                // 修改SDP，移除本地IP
                                offer.sdp = offer.sdp.replace(/a=candidate:.*\\r\\n/g, '');
                            }}
                            return offer;
                        }});
                    }};
                    
                    // Hook createAnswer
                    const originalCreateAnswer = pc.createAnswer;
                    pc.createAnswer = function(options) {{
                        return originalCreateAnswer.call(this, options).then(function(answer) {{
                            if (preventLeak) {{
                                answer.sdp = answer.sdp.replace(/a=candidate:.*\\r\\n/g, '');
                            }}
                            return answer;
                        }});
                    }};
                    
                    // Hook onicecandidate事件
                    // 这可以防止通过ICE候选者泄漏IP
                    
                    return pc;
                }}
                
                // 替换RTCPeerConnection
                if (window.RTCPeerConnection) {{
                    window.RTCPeerConnection = PatchedPeerConnection;
                }}
                if (window.webkitRTCPeerConnection) {{
                    window.webkitRTCPeerConnection = PatchedPeerConnection;
                }}
                if (window.mozRTCPeerConnection) {{
                    window.mozRTCPeerConnection = PatchedPeerConnection;
                }}
            }}
            
            // Hook mediaDevices.enumerateDevices - 伪造设备列表
            if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {{
                const originalEnumerateDevices = navigator.mediaDevices.enumerateDevices;
                
                navigator.mediaDevices.enumerateDevices = function() {{
                    return originalEnumerateDevices.call(this).then(function(devices) {{
                        // 如果需要伪造设备列表
                        if (cameraCount >= 0 || microphoneCount >= 0) {{
                            const fakeDevices = [];
                            let deviceIndex = 0;
                            
                            // 添加摄像头
                            for (let i = 0; i < cameraCount; i++) {{
                                fakeDevices.push({{
                                    deviceId: deviceIdPrefix + '_camera_' + i,
                                    kind: 'videoinput',
                                    label: i === 0 ? 'Default Camera' : 'Camera ' + (i + 1),
                                    groupId: deviceIdPrefix + '_group_' + i,
                                }});
                            }}
                            
                            // 添加麦克风
                            for (let i = 0; i < microphoneCount; i++) {{
                                fakeDevices.push({{
                                    deviceId: deviceIdPrefix + '_mic_' + i,
                                    kind: 'audioinput',
                                    label: i === 0 ? 'Default Microphone' : 'Microphone ' + (i + 1),
                                    groupId: deviceIdPrefix + '_group_' + i,
                                }});
                            }}
                            
                            // 添加扬声器
                            for (let i = 0; i < speakerCount; i++) {{
                                fakeDevices.push({{
                                    deviceId: deviceIdPrefix + '_speaker_' + i,
                                    kind: 'audiooutput',
                                    label: i === 0 ? 'Default Speaker' : 'Speaker ' + (i + 1),
                                    groupId: deviceIdPrefix + '_group_' + i,
                                }});
                            }}
                            
                            return fakeDevices;
                        }}
                        
                        return devices;
                    }});
                }};
            }}
            
            // Hook getUserMedia - 模拟行为
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {{
                const originalGetUserMedia = navigator.mediaDevices.getUserMedia;
                
                navigator.mediaDevices.getUserMedia = function(constraints) {{
                    // 可以在这里添加模拟逻辑
                    return originalGetUserMedia.call(this, constraints);
                }};
            }}
            
            console.log('WebRTC fingerprint spoofing activated');
        }})();
        """
    
    def get_webrtc_test_script(self) -> str:
        """生成WebRTC测试脚本"""
        return """
        // WebRTC指纹测试
        (function() {
            const result = {
                webrtc_supported: false,
                media_devices_supported: false,
                devices: [],
                local_ips: [],
            };
            
            // 检查RTCPeerConnection支持
            if (window.RTCPeerConnection || window.webkitRTCPeerConnection || window.mozRTCPeerConnection) {
                result.webrtc_supported = true;
            }
            
            // 检查mediaDevices支持
            if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
                result.media_devices_supported = true;
                
                // 获取设备列表
                return navigator.mediaDevices.enumerateDevices().then(function(devices) {
                    result.devices = devices.map(function(d) {
                        return {
                            deviceId: d.deviceId ? d.deviceId.substring(0, 8) + '...' : null,
                            kind: d.kind,
                            label: d.label,
                            groupId: d.groupId ? d.groupId.substring(0, 8) + '...' : null,
                        };
                    });
                    
                    return result;
                }).catch(function() {
                    return result;
                });
            }
            
            return Promise.resolve(result);
        })();
        """
