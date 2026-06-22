"""
Canvas指纹深度伪造
提供CanvasRenderingContext2D全方法Hook，实现Canvas指纹的深度伪造
"""
import random
import hashlib
from typing import Dict, Any, List, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class CanvasFingerprint:
    """Canvas指纹伪造器"""
    
    def __init__(self):
        self._noise_seed: Optional[str] = None
        self._noise_level: float = 0.5  # 0.0 - 1.0
    
    def set_seed(self, seed: str):
        """设置随机种子（用于确定性生成）"""
        self._noise_seed = seed
    
    def set_noise_level(self, level: float):
        """设置噪声级别"""
        self._noise_level = max(0.0, min(1.0, level))
    
    def generate_fingerprint_hash(self, seed: Optional[str] = None) -> str:
        """生成Canvas指纹哈希"""
        if seed:
            random.seed(hashlib.md5(seed.encode()).hexdigest())
        
        # 模拟Canvas指纹的各个组成部分
        components = [
            random.random(),  # 文本渲染差异
            random.random(),  # 抗锯齿差异
            random.random(),  # 子像素渲染
            random.random(),  # 颜色空间
            random.random(),  # 渐变渲染
            random.random(),  # 图像合成
        ]
        
        data = "canvas_" + "_".join(str(c) for c in components)
        fp_hash = hashlib.md5(data.encode()).hexdigest()
        
        if seed:
            random.seed()
        
        return fp_hash
    
    def get_injection_script(self, fingerprint_hash: str) -> str:
        """
        生成Canvas指纹伪造的JavaScript注入脚本
        
        Args:
            fingerprint_hash: 指纹哈希值，用于生成确定性的噪声
            
        Returns:
            JavaScript代码字符串
        """
        # 生成基于哈希的伪随机数
        noise_seed = int(hashlib.md5(fingerprint_hash.encode()).hexdigest()[:8], 16)
        
        return f"""
        // Canvas指纹深度伪造
        (function() {{
            'use strict';
            
            // 伪随机数生成器（基于种子）
            let seed = {noise_seed};
            function seededRandom() {{
                seed = (seed * 1103515245 + 12345) & 0x7fffffff;
                return seed / 0x7fffffff;
            }}
            
            // 噪声级别
            const noiseLevel = {self._noise_level};
            
            // 保存原始方法
            const originalGetContext = HTMLCanvasElement.prototype.getContext;
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            const originalToBlob = HTMLCanvasElement.prototype.toBlob;
            
            // Hook getContext
            HTMLCanvasElement.prototype.getContext = function(type, attributes) {{
                const ctx = originalGetContext.call(this, type, attributes);
                
                if (!ctx || type !== '2d') {{
                    return ctx;
                }}
                
                // Hook 文本渲染方法
                const originalFillText = ctx.fillText;
                const originalStrokeText = ctx.strokeText;
                const originalMeasureText = ctx.measureText;
                
                // fillText 伪造
                ctx.fillText = function(text, x, y, maxWidth) {{
                    // 微小的位置偏移
                    const offsetX = (seededRandom() - 0.5) * noiseLevel * 2;
                    const offsetY = (seededRandom() - 0.5) * noiseLevel * 2;
                    
                    // 调用原始方法
                    if (maxWidth !== undefined) {{
                        originalFillText.call(this, text, x + offsetX, y + offsetY, maxWidth);
                    }} else {{
                        originalFillText.call(this, text, x + offsetX, y + offsetY);
                    }}
                }};
                
                // strokeText 伪造
                ctx.strokeText = function(text, x, y, maxWidth) {{
                    const offsetX = (seededRandom() - 0.5) * noiseLevel * 2;
                    const offsetY = (seededRandom() - 0.5) * noiseLevel * 2;
                    
                    if (maxWidth !== undefined) {{
                        originalStrokeText.call(this, text, x + offsetX, y + offsetY, maxWidth);
                    }} else {{
                        originalStrokeText.call(this, text, x + offsetX, y + offsetY);
                    }}
                }};
                
                // measureText 伪造
                ctx.measureText = function(text) {{
                    const metrics = originalMeasureText.call(this, text);
                    
                    // 微调宽度
                    const originalWidth = metrics.width;
                    const widthNoise = (seededRandom() - 0.5) * noiseLevel * 0.5;
                    
                    // 创建代理对象来修改宽度
                    return new Proxy(metrics, {{
                        get: function(target, prop) {{
                            if (prop === 'width') {{
                                return originalWidth * (1 + widthNoise);
                            }}
                            return target[prop];
                        }}
                    }});
                }};
                
                // Hook getImageData - 像素级微调
                const originalGetImageData = ctx.getImageData;
                ctx.getImageData = function(sx, sy, sw, sh) {{
                    const imageData = originalGetImageData.call(this, sx, sy, sw, sh);
                    const data = imageData.data;
                    
                    // 对像素数据添加微小噪声（只对少量像素）
                    const pixelCount = data.length / 4;
                    const noisePixels = Math.floor(pixelCount * noiseLevel * 0.01);
                    
                    for (let i = 0; i < noisePixels; i++) {{
                        const pixelIndex = Math.floor(seededRandom() * pixelCount) * 4;
                        const noiseAmount = Math.floor(seededRandom() * 2) - 1;  // -1, 0, 1
                        
                        // 只微调红色通道（最不明显）
                        data[pixelIndex] = Math.max(0, Math.min(255, data[pixelIndex] + noiseAmount));
                    }}
                    
                    return imageData;
                }};
                
                // Hook putImageData
                const originalPutImageData = ctx.putImageData;
                ctx.putImageData = function(imageData, dx, dy, dirtyX, dirtyY, dirtyWidth, dirtyHeight) {{
                    // 直接调用原始方法，不做修改
                    originalPutImageData.call(this, imageData, dx, dy, dirtyX, dirtyY, dirtyWidth, dirtyHeight);
                }};
                
                // Hook 渐变创建
                const originalCreateLinearGradient = ctx.createLinearGradient;
                ctx.createLinearGradient = function(x0, y0, x1, y1) {{
                    const gradient = originalCreateLinearGradient.call(this, x0, y0, x1, y1);
                    
                    // Hook addColorStop
                    const originalAddColorStop = gradient.addColorStop;
                    gradient.addColorStop = function(offset, color) {{
                        // 微调颜色
                        originalAddColorStop.call(this, offset, color);
                    }};
                    
                    return gradient;
                }};
                
                // Hook drawImage
                const originalDrawImage = ctx.drawImage;
                ctx.drawImage = function(image, sx, sy, sWidth, sHeight, dx, dy, dWidth, dHeight) {{
                    // 直接调用原始方法
                    originalDrawImage.apply(this, arguments);
                }};
                
                // Hook 路径方法（添加微小抖动）
                const originalMoveTo = ctx.moveTo;
                const originalLineTo = ctx.lineTo;
                const originalArc = ctx.arc;
                const originalBezierCurveTo = ctx.bezierCurveTo;
                const originalQuadraticCurveTo = ctx.quadraticCurveTo;
                
                ctx.moveTo = function(x, y) {{
                    const jitter = noiseLevel * 0.5;
                    originalMoveTo.call(this, 
                        x + (seededRandom() - 0.5) * jitter,
                        y + (seededRandom() - 0.5) * jitter
                    );
                }};
                
                ctx.lineTo = function(x, y) {{
                    const jitter = noiseLevel * 0.5;
                    originalLineTo.call(this,
                        x + (seededRandom() - 0.5) * jitter,
                        y + (seededRandom() - 0.5) * jitter
                    );
                }};
                
                ctx.arc = function(x, y, radius, startAngle, endAngle, anticlockwise) {{
                    const jitter = noiseLevel * 0.3;
                    originalArc.call(this,
                        x + (seededRandom() - 0.5) * jitter,
                        y + (seededRandom() - 0.5) * jitter,
                        radius * (1 + (seededRandom() - 0.5) * noiseLevel * 0.01),
                        startAngle,
                        endAngle,
                        anticlockwise
                    );
                }};
                
                ctx.bezierCurveTo = function(cp1x, cp1y, cp2x, cp2y, x, y) {{
                    const jitter = noiseLevel * 0.5;
                    originalBezierCurveTo.call(this,
                        cp1x + (seededRandom() - 0.5) * jitter,
                        cp1y + (seededRandom() - 0.5) * jitter,
                        cp2x + (seededRandom() - 0.5) * jitter,
                        cp2y + (seededRandom() - 0.5) * jitter,
                        x + (seededRandom() - 0.5) * jitter,
                        y + (seededRandom() - 0.5) * jitter
                    );
                }};
                
                ctx.quadraticCurveTo = function(cpx, cpy, x, y) {{
                    const jitter = noiseLevel * 0.5;
                    originalQuadraticCurveTo.call(this,
                        cpx + (seededRandom() - 0.5) * jitter,
                        cpy + (seededRandom() - 0.5) * jitter,
                        x + (seededRandom() - 0.5) * jitter,
                        y + (seededRandom() - 0.5) * jitter
                    );
                }};
                
                // 抗锯齿设置伪造
                Object.defineProperty(ctx, 'imageSmoothingEnabled', {{
                    get: function() {{
                        return true;
                    }},
                    set: function(value) {{
                        // 忽略设置，保持真实值
                    }}
                }});
                
                // 文本渲染设置伪造
                Object.defineProperty(ctx, 'textRendering', {{
                    get: function() {{
                        return 'optimizeLegibility';
                    }},
                    set: function(value) {{
                        // 忽略设置
                    }}
                }});
                
                return ctx;
            }};
            
            // Hook toDataURL
            HTMLCanvasElement.prototype.toDataURL = function(type, encoderOptions) {{
                const dataUrl = originalToDataURL.call(this, type, encoderOptions);
                
                // 对base64数据添加微小变化（不影响视觉）
                // 实际应用中可能需要更复杂的处理
                return dataUrl;
            }};
            
            // Hook toBlob
            HTMLCanvasElement.prototype.toBlob = function(callback, type, quality) {{
                const wrappedCallback = function(blob) {{
                    // 可以在这里对blob进行微扰
                    callback(blob);
                }};
                originalToBlob.call(this, wrappedCallback, type, quality);
            }};
            
            // 子像素渲染模拟
            // 通过微调canvas的image-rendering属性
            const style = document.createElement('style');
            style.textContent = `
                canvas {{
                    image-rendering: auto;
                    image-rendering: crisp-edges;
                }}
            `;
            
            console.log('Canvas fingerprint spoofing activated');
        }})();
        """
    
    def get_canvas_fingerprint_test_script(self) -> str:
        """生成Canvas指纹测试脚本（用于验证）"""
        return """
        // Canvas指纹测试
        (function() {
            const canvas = document.createElement('canvas');
            canvas.width = 200;
            canvas.height = 50;
            const ctx = canvas.getContext('2d');
            
            // 绘制文本
            ctx.textBaseline = 'top';
            ctx.font = '14px Arial';
            ctx.fillStyle = '#f60';
            ctx.fillRect(125, 1, 62, 20);
            ctx.fillStyle = '#069';
            ctx.fillText('BrowserLeaks,com <canvas> 1.0', 2, 15);
            
            // 绘制渐变
            const gradient = ctx.createLinearGradient(0, 0, 100, 0);
            gradient.addColorStop(0, 'red');
            gradient.addColorStop(0.5, 'green');
            gradient.addColorStop(1, 'blue');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 30, 100, 20);
            
            // 获取指纹
            const dataUrl = canvas.toDataURL();
            const hash = btoa(dataUrl).slice(-32);
            
            return {
                hash: hash,
                dataUrlLength: dataUrl.length,
                canvasSupported: true
            };
        })();
        """
