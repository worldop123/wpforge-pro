"""
字体指纹完全随机化
提供已安装字体列表随机生成和字体渲染尺寸随机微调
"""
import random
import hashlib
from typing import Dict, Any, List, Optional, Set

from app.core.logging import get_logger

logger = get_logger(__name__)


class FontFingerprint:
    """字体指纹伪造器"""
    
    # Windows常见字体
    WINDOWS_FONTS = [
        "Arial", "Arial Black", "Arial Narrow",
        "Calibri", "Cambria", "Cambria Math",
        "Comic Sans MS", "Consolas", "Constantia", "Corbel",
        "Courier", "Courier New",
        "Georgia", "Helvetica", "Impact",
        "Lucida Console", "Lucida Sans Unicode",
        "Microsoft Sans Serif", "Palatino Linotype",
        "Segoe UI", "Segoe UI Light", "Segoe UI Semibold", "Segoe UI Symbol",
        "Tahoma", "Times", "Times New Roman",
        "Trebuchet MS", "Verdana", "Wingdings",
        "MS Gothic", "MS PGothic", "MS UI Gothic",
        "MS Mincho", "MS PMincho",
        "Meiryo", "Meiryo UI",
    ]
    
    # macOS常见字体
    MACOS_FONTS = [
        "Arial", "Arial Black", "Arial Narrow",
        "Helvetica", "Helvetica Neue",
        "Times", "Times New Roman",
        "Courier", "Courier New",
        "Verdana", "Georgia", "Tahoma",
        "Impact", "Comic Sans MS",
        "Trebuchet MS", "Palatino",
        "Optima", "Futura", "Gill Sans",
        "Hoefler Text", "Baskerville",
        "Didot", "American Typewriter",
        "Andale Mono", "Monaco", "Consolas",
        "Menlo", "SF Pro Display", "SF Pro Text",
        "SF Mono", "New York",
    ]
    
    # Linux常见字体
    LINUX_FONTS = [
        "Arial", "Helvetica",
        "Times New Roman", "Times",
        "Courier New", "Courier",
        "Verdana", "Georgia", "Tahoma",
        "DejaVu Sans", "DejaVu Serif", "DejaVu Sans Mono",
        "Liberation Sans", "Liberation Serif", "Liberation Mono",
        "Ubuntu", "Ubuntu Mono",
        "Cantarell", "Nimbus Sans",
        "FreeSans", "FreeSerif", "FreeMono",
        "Droid Sans", "Droid Serif", "Droid Sans Mono",
        "Noto Sans", "Noto Serif", "Noto Mono",
    ]
    
    def __init__(self):
        self._fonts: List[str] = []
        self._os_type: str = "windows"
        self._noise_level: float = 0.1  # 字体渲染噪声级别
    
    def generate_random_fonts(self, os_type: str = "windows", 
                               min_count: int = 20,
                               max_count: Optional[int] = None,
                               seed: Optional[str] = None) -> List[str]:
        """
        生成随机字体列表
        
        Args:
            os_type: 操作系统类型 (windows, macos, linux)
            min_count: 最少字体数量
            max_count: 最多字体数量
            seed: 随机种子
            
        Returns:
            字体列表
        """
        if seed:
            random.seed(hashlib.md5(seed.encode()).hexdigest())
        
        # 获取对应操作系统的字体列表
        if os_type == "windows":
            base_fonts = self.WINDOWS_FONTS.copy()
        elif os_type == "macos":
            base_fonts = self.MACOS_FONTS.copy()
        elif os_type == "linux":
            base_fonts = self.LINUX_FONTS.copy()
        else:
            base_fonts = self.WINDOWS_FONTS.copy()
        
        self._os_type = os_type
        
        # 确定字体数量
        if max_count is None:
            max_count = len(base_fonts)
        
        num_fonts = random.randint(min_count, min(max_count, len(base_fonts)))
        
        # 随机选择字体
        selected_fonts = random.sample(base_fonts, num_fonts)
        selected_fonts.sort()
        
        self._fonts = selected_fonts
        
        if seed:
            random.seed()
        
        return selected_fonts
    
    def set_fonts(self, fonts: List[str], os_type: str = "windows"):
        """设置字体列表"""
        self._fonts = fonts
        self._os_type = os_type
    
    def get_injection_script(self) -> str:
        """
        生成字体指纹伪造的JavaScript注入脚本
        
        Returns:
            JavaScript代码字符串
        """
        fonts_json = str(self._fonts).replace("'", '"')
        noise_level = self._noise_level
        
        return f"""
        // 字体指纹完全随机化
        (function() {{
            'use strict';
            
            const fakeFonts = {fonts_json};
            const noiseLevel = {noise_level};
            
            // 伪随机数生成器
            let seed = 12345;
            function seededRandom() {{
                seed = (seed * 1103515245 + 12345) & 0x7fffffff;
                return seed / 0x7fffffff;
            }}
            
            // Hook document.fonts API
            if (document.fonts) {{
                const originalCheck = document.fonts.check;
                const originalLoad = document.fonts.load;
                
                document.fonts.check = function(font, text) {{
                    // 检查字体是否在我们的伪造列表中
                    const fontName = font.split(' ').pop().replace(/["']/g, '');
                    
                    // 如果是我们伪造的字体，返回true
                    for (let i = 0; i < fakeFonts.length; i++) {{
                        if (fakeFonts[i].toLowerCase() === fontName.toLowerCase()) {{
                            return true;
                        }}
                    }}
                    
                    return originalCheck.call(this, font, text);
                }};
                
                document.fonts.load = function(font, text) {{
                    return originalLoad.call(this, font, text);
                }};
                
                // Hook ready属性
                Object.defineProperty(document.fonts, 'ready', {{
                    get: function() {{
                        return Promise.resolve();
                    }}
                }});
            }}
            
            // 字体检测伪造 - 通过创建canvas来检测字体
            // 这是最常见的字体检测方法
            const originalGetContext = HTMLCanvasElement.prototype.getContext;
            
            // 缓存字体检测结果
            const fontCache = {{}};
            
            function checkFont(fontName) {{
                if (fontCache[fontName] !== undefined) {{
                    return fontCache[fontName];
                }}
                
                // 检查是否在伪造列表中
                const isFake = fakeFonts.some(f => f.toLowerCase() === fontName.toLowerCase());
                fontCache[fontName] = isFake;
                
                return isFake;
            }}
            
            // Hook measureText来微调字体渲染尺寸
            // 这会影响字体指纹的精确性
            const originalGetContext2d = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function(type, attributes) {{
                const ctx = originalGetContext2d.call(this, type, attributes);
                
                if (!ctx || type !== '2d') {{
                    return ctx;
                }}
                
                const originalMeasureText = ctx.measureText;
                ctx.measureText = function(text) {{
                    const metrics = originalMeasureText.call(this, text);
                    
                    // 获取当前字体
                    const font = this.font || '';
                    const fontName = font.split(' ').pop().replace(/["']/g, '');
                    
                    // 检查是否是我们伪造的字体
                    if (checkFont(fontName)) {{
                        // 微调宽度
                        const originalWidth = metrics.width;
                        const widthNoise = (seededRandom() - 0.5) * noiseLevel * 0.02;
                        
                        return new Proxy(metrics, {{
                            get: function(target, prop) {{
                                if (prop === 'width') {{
                                    return originalWidth * (1 + widthNoise);
                                }}
                                return target[prop];
                            }}
                        }});
                    }}
                    
                    return metrics;
                }};
                
                return ctx;
            }};
            
            // 字体回退检测伪造
            // 某些检测会通过比较不同字体的渲染宽度来检测字体
            
            // @font-face加载行为模拟
            // 可以在这里添加更多的伪造逻辑
            
            // 字体抗锯齿差异模拟
            // 通过CSS来模拟不同的字体渲染效果
            
            console.log('Font fingerprint spoofing activated, ' + fakeFonts.length + ' fonts');
        }})();
        """
    
    def get_font_detection_test_script(self) -> str:
        """生成字体检测测试脚本"""
        return """
        // 字体指纹测试
        (function() {
            const testFonts = [
                "Arial", "Arial Black", "Arial Narrow",
                "Calibri", "Cambria",
                "Comic Sans MS", "Consolas", "Courier New",
                "Georgia", "Helvetica", "Impact",
                "Lucida Console",
                "Microsoft Sans Serif",
                "Segoe UI", "Tahoma", "Times New Roman",
                "Trebuchet MS", "Verdana", "Wingdings",
            ];
            
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            const baseFont = "monospace";
            const testString = "mmmmmmmmmmlli";
            
            function detectFont(fontName) {
                // 使用canvas测量字体宽度来检测
                ctx.font = `72px ${baseFont}`;
                const baseWidth = ctx.measureText(testString).width;
                
                ctx.font = `72px "${fontName}", ${baseFont}`;
                const testWidth = ctx.measureText(testString).width;
                
                return Math.abs(baseWidth - testWidth) > 0.5;
            }
            
            const detectedFonts = [];
            for (const font of testFonts) {
                if (detectFont(font)) {
                    detectedFonts.push(font);
                }
            }
            
            // 生成字体指纹哈希
            const hash = btoa(detectedFonts.join(','));
            
            return {
                total_tested: testFonts.length,
                detected_count: detectedFonts.length,
                detected_fonts: detectedFonts,
                fingerprint_hash: hash,
            };
        })();
        """
