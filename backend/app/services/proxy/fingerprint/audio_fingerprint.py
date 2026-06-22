"""
AudioContext指纹深度伪造
提供AudioContext/OfflineAudioContext Hook，实现音频指纹的深度伪造
"""
import random
import hashlib
from typing import Dict, Any, List, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class AudioFingerprint:
    """音频指纹伪造器"""
    
    # 常见采样率
    SAMPLE_RATES = [44100, 48000, 96000]
    
    # 常见延迟值（秒）
    BASE_LATENCIES = [0.005, 0.01, 0.015, 0.02, 0.025]
    OUTPUT_LATENCIES = [0.01, 0.02, 0.03, 0.04, 0.05]
    
    def __init__(self):
        self._sample_rate: int = 44100
        self._base_latency: float = 0.01
        self._output_latency: float = 0.02
        self._max_channels: int = 2
        self._noise_level: float = 0.1  # 噪声级别
    
    def generate_random_config(self, seed: Optional[str] = None):
        """生成随机的音频配置"""
        if seed:
            random.seed(hashlib.md5(seed.encode()).hexdigest())
        
        self._sample_rate = random.choice(self.SAMPLE_RATES)
        self._base_latency = random.choice(self.BASE_LATENCIES)
        self._output_latency = random.choice(self.OUTPUT_LATENCIES)
        self._max_channels = random.choice([2, 2, 2, 6, 8])  # 大多数是立体声
        
        if seed:
            random.seed()
    
    def set_config(self, sample_rate: int, base_latency: float, 
                   output_latency: float, max_channels: int = 2):
        """设置音频配置"""
        self._sample_rate = sample_rate
        self._base_latency = base_latency
        self._output_latency = output_latency
        self._max_channels = max_channels
    
    def generate_fingerprint_hash(self, seed: Optional[str] = None) -> str:
        """生成音频指纹哈希"""
        if seed:
            random.seed(hashlib.md5(seed.encode()).hexdigest())
        
        # 模拟音频指纹的各个组成部分
        components = [
            self._sample_rate,
            self._base_latency,
            self._output_latency,
            random.random(),  # 振荡器特征
            random.random(),  # 压缩器特征
            random.random(),  # 分析器特征
            random.random(),  # 音频缓冲特征
        ]
        
        data = "audio_" + "_".join(str(c) for c in components)
        fp_hash = hashlib.sha256(data.encode()).hexdigest()
        
        if seed:
            random.seed()
        
        return fp_hash
    
    def get_injection_script(self, fingerprint_hash: str) -> str:
        """
        生成音频指纹伪造的JavaScript注入脚本
        
        Args:
            fingerprint_hash: 指纹哈希值，用于生成确定性的噪声
            
        Returns:
            JavaScript代码字符串
        """
        # 生成基于哈希的伪随机数
        noise_seed = int(hashlib.md5(fingerprint_hash.encode()).hexdigest()[:8], 16)
        
        return f"""
        // AudioContext指纹深度伪造
        (function() {{
            'use strict';
            
            // 伪随机数生成器
            let seed = {noise_seed};
            function seededRandom() {{
                seed = (seed * 1103515245 + 12345) & 0x7fffffff;
                return seed / 0x7fffffff;
            }}
            
            const noiseLevel = {self._noise_level};
            const fakeSampleRate = {self._sample_rate};
            const fakeBaseLatency = {self._base_latency};
            const fakeOutputLatency = {self._output_latency};
            
            // 检查AudioContext是否存在
            if (typeof AudioContext === 'undefined' && typeof webkitAudioContext === 'undefined') {{
                return;
            }}
            
            const OriginalAudioContext = window.AudioContext || window.webkitAudioContext;
            const OriginalOfflineAudioContext = window.OfflineAudioContext;
            
            if (!OriginalAudioContext) {{
                return;
            }}
            
            // Hook AudioContext构造函数
            function PatchedAudioContext(options) {{
                // 修改options
                if (!options) {{
                    options = {{}};
                }}
                options.sampleRate = fakeSampleRate;
                
                const ctx = new OriginalAudioContext(options);
                
                // Hook baseLatency
                Object.defineProperty(ctx, 'baseLatency', {{
                    get: function() {{
                        return fakeBaseLatency;
                    }}
                }});
                
                // Hook outputLatency
                Object.defineProperty(ctx, 'outputLatency', {{
                    get: function() {{
                        return fakeOutputLatency;
                    }}
                }});
                
                // Hook sampleRate
                Object.defineProperty(ctx, 'sampleRate', {{
                    get: function() {{
                        return fakeSampleRate;
                    }}
                }});
                
                // Hook createOscillator - 振荡器指纹随机化
                const originalCreateOscillator = ctx.createOscillator;
                ctx.createOscillator = function() {{
                    const oscillator = originalCreateOscillator.call(this);
                    
                    // Hook频率设置（添加微小噪声）
                    const originalSetValueAtTime = oscillator.frequency.setValueAtTime;
                    oscillator.frequency.setValueAtTime = function(value, startTime) {{
                        const noise = (seededRandom() - 0.5) * noiseLevel * 0.01 * value;
                        return originalSetValueAtTime.call(this, value + noise, startTime);
                    }};
                    
                    return oscillator;
                }};
                
                // Hook createDynamicsCompressor - 压缩器指纹
                const originalCreateDynamicsCompressor = ctx.createDynamicsCompressor;
                ctx.createDynamicsCompressor = function() {{
                    const compressor = originalCreateDynamicsCompressor.call(this);
                    
                    // 微调压缩器参数
                    const originalThreshold = compressor.threshold;
                    Object.defineProperty(compressor, 'threshold', {{
                        get: function() {{
                            return originalThreshold;
                        }}
                    }});
                    
                    return compressor;
                }};
                
                // Hook createAnalyser - 分析器输出微调
                const originalCreateAnalyser = ctx.createAnalyser;
                ctx.createAnalyser = function() {{
                    const analyser = originalCreateAnalyser.call(this);
                    
                    // Hook getByteFrequencyData
                    const originalGetByteFrequencyData = analyser.getByteFrequencyData;
                    analyser.getByteFrequencyData = function(array) {{
                        originalGetByteFrequencyData.call(this, array);
                        
                        // 添加微小噪声
                        for (let i = 0; i < array.length; i++) {{
                            if (seededRandom() < noiseLevel * 0.1) {{
                                const noise = Math.floor((seededRandom() - 0.5) * 2);
                                array[i] = Math.max(0, Math.min(255, array[i] + noise));
                            }}
                        }}
                    }};
                    
                    // Hook getByteTimeDomainData
                    const originalGetByteTimeDomainData = analyser.getByteTimeDomainData;
                    analyser.getByteTimeDomainData = function(array) {{
                        originalGetByteTimeDomainData.call(this, array);
                        
                        // 添加微小噪声
                        for (let i = 0; i < array.length; i++) {{
                            if (seededRandom() < noiseLevel * 0.1) {{
                                const noise = Math.floor((seededRandom() - 0.5) * 2);
                                array[i] = Math.max(0, Math.min(255, array[i] + noise));
                            }}
                        }}
                    }};
                    
                    return analyser;
                }};
                
                // Hook createBuffer - AudioBuffer采样数据微调
                const originalCreateBuffer = ctx.createBuffer;
                ctx.createBuffer = function(numberOfChannels, length, sampleRate) {{
                    const buffer = originalCreateBuffer.call(this, numberOfChannels, length, sampleRate);
                    
                    // Hook getChannelData
                    const originalGetChannelData = buffer.getChannelData;
                    buffer.getChannelData = function(channel) {{
                        const data = originalGetChannelData.call(this, channel);
                        
                        // 可以在这里对数据添加微扰（可选）
                        return data;
                    }};
                    
                    return buffer;
                }};
                
                return ctx;
            }}
            
            // 替换AudioContext
            window.AudioContext = PatchedAudioContext;
            if (window.webkitAudioContext) {{
                window.webkitAudioContext = PatchedAudioContext;
            }}
            
            // Hook OfflineAudioContext
            if (OriginalOfflineAudioContext) {{
                function PatchedOfflineAudioContext(numberOfChannels, length, sampleRate) {{
                    const ctx = new OriginalOfflineAudioContext(numberOfChannels, length, fakeSampleRate);
                    return ctx;
                }}
                
                window.OfflineAudioContext = PatchedOfflineAudioContext;
            }}
            
            console.log('Audio fingerprint spoofing activated');
        }})();
        """
    
    def get_audio_fingerprint_test_script(self) -> str:
        """生成音频指纹测试脚本"""
        return """
        // AudioContext指纹测试
        (function() {
            if (typeof AudioContext === 'undefined' && typeof webkitAudioContext === 'undefined') {
                return { supported: false };
            }
            
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            const ctx = new AudioContext();
            
            // 创建振荡器
            const oscillator = ctx.createOscillator();
            const analyser = ctx.createAnalyser();
            const gainNode = ctx.createGain();
            
            oscillator.type = 'sine';
            oscillator.frequency.setValueAtTime(1000, ctx.currentTime);
            gainNode.gain.setValueAtTime(0.5, ctx.currentTime);
            
            oscillator.connect(analyser);
            analyser.connect(gainNode);
            gainNode.connect(ctx.destination);
            
            oscillator.start();
            
            // 获取频率数据
            const frequencyData = new Uint8Array(analyser.frequencyBinCount);
            analyser.getByteFrequencyData(frequencyData);
            
            // 生成简单哈希
            let hash = 0;
            for (let i = 0; i < frequencyData.length; i += 8) {
                hash = ((hash << 5) - hash + frequencyData[i]) | 0;
            }
            
            oscillator.stop();
            
            return {
                supported: true,
                sampleRate: ctx.sampleRate,
                baseLatency: ctx.baseLatency,
                outputLatency: ctx.outputLatency,
                frequency_hash: hash,
                frequency_bin_count: analyser.frequencyBinCount,
                max_channels: ctx.destination.maxChannelCount,
            };
        })();
        """
