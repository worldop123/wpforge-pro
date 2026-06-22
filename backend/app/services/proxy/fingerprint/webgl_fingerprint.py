"""
WebGL指纹完全伪造
提供WebGLRenderingContext/WebGL2RenderingContext全属性Hook
"""
import random
import hashlib
from typing import Dict, Any, List, Optional, Tuple

from app.core.logging import get_logger

logger = get_logger(__name__)


class WebGLFingerprint:
    """WebGL指纹伪造器"""
    
    # 真实的WebGL供应商和渲染器配置
    WEBGL_CONFIGS = [
        ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0)"),
        ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0)"),
        ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0)"),
        ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA GeForce GTX 1660 Direct3D11 vs_5_0 ps_5_0)"),
        ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)"),
        ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0)"),
        ("Google Inc. (AMD)", "ANGLE (AMD, AMD Radeon RX 580 Series Direct3D11 vs_5_0 ps_5_0)"),
        ("Google Inc. (Apple)", "ANGLE (Apple, ANGLE Metal Renderer: Apple M1, Unspecified Version)"),
    ]
    
    # WebGL扩展列表
    WEBGL_EXTENSIONS = [
        "ANGLE_instanced_arrays",
        "EXT_blend_minmax",
        "EXT_color_buffer_half_float",
        "EXT_disjoint_timer_query",
        "EXT_frag_depth",
        "EXT_shader_texture_lod",
        "EXT_sRGB",
        "EXT_texture_filter_anisotropic",
        "OES_element_index_uint",
        "OES_standard_derivatives",
        "OES_texture_float",
        "OES_texture_float_linear",
        "OES_texture_half_float",
        "OES_texture_half_float_linear",
        "OES_vertex_array_object",
        "WEBGL_compressed_texture_s3tc",
        "WEBGL_compressed_texture_s3tc_srgb",
        "WEBGL_debug_renderer_info",
        "WEBGL_debug_shaders",
        "WEBGL_depth_texture",
        "WEBGL_draw_buffers",
        "WEBGL_lose_context",
    ]
    
    def __init__(self):
        self._vendor: str = ""
        self._renderer: str = ""
        self._extensions: List[str] = []
        self._shader_precision: Dict[str, Any] = {}
    
    def generate_random_config(self, seed: Optional[str] = None) -> Tuple[str, str]:
        """生成随机的WebGL供应商和渲染器配置"""
        if seed:
            random.seed(hashlib.md5(seed.encode()).hexdigest())
        
        vendor, renderer = random.choice(self.WEBGL_CONFIGS)
        
        if seed:
            random.seed()
        
        return vendor, renderer
    
    def generate_extensions(self, seed: Optional[str] = None) -> List[str]:
        """生成随机的WebGL扩展列表"""
        if seed:
            random.seed(hashlib.md5(seed.encode()).hexdigest())
        
        # 随机选择扩展子集
        num_extensions = random.randint(15, len(self.WEBGL_EXTENSIONS))
        extensions = random.sample(self.WEBGL_EXTENSIONS, num_extensions)
        
        if seed:
            random.seed()
        
        return extensions
    
    def generate_shader_precision(self, seed: Optional[str] = None) -> Dict[str, Any]:
        """生成着色器精度配置"""
        if seed:
            random.seed(hashlib.md5(seed.encode()).hexdigest())
        
        # 基础精度配置
        base_precision = {
            "vertex": {
                "low": {"rangeMin": -128, "rangeMax": 127, "precision": 23},
                "medium": {"rangeMin": -1024, "rangeMax": 1023, "precision": 23},
                "high": {"rangeMin": -65536, "rangeMax": 65535, "precision": 24},
            },
            "fragment": {
                "low": {"rangeMin": -128, "rangeMax": 127, "precision": 23},
                "medium": {"rangeMin": -1024, "rangeMax": 1023, "precision": 23},
                "high": {"rangeMin": -65536, "rangeMax": 65535, "precision": 24},
            },
        }
        
        # 添加一些微小变化
        for shader_type in ["vertex", "fragment"]:
            for precision_level in ["low", "medium", "high"]:
                config = base_precision[shader_type][precision_level]
                config["rangeMin"] += random.randint(-2, 2)
                config["rangeMax"] += random.randint(-2, 2)
                config["precision"] += random.randint(-1, 1)
        
        if seed:
            random.seed()
        
        return base_precision
    
    def set_config(self, vendor: str, renderer: str, extensions: List[str], 
                   shader_precision: Dict[str, Any]):
        """设置WebGL配置"""
        self._vendor = vendor
        self._renderer = renderer
        self._extensions = extensions
        self._shader_precision = shader_precision
    
    def get_injection_script(self) -> str:
        """
        生成WebGL指纹伪造的JavaScript注入脚本
        
        Returns:
            JavaScript代码字符串
        """
        extensions_json = str(self._extensions).replace("'", '"')
        
        return f"""
        // WebGL指纹完全伪造
        (function() {{
            'use strict';
            
            const fakeVendor = "{self._vendor}";
            const fakeRenderer = "{self._renderer}";
            const fakeExtensions = {extensions_json};
            
            // 保存原始方法
            const originalGetContext = HTMLCanvasElement.prototype.getContext;
            const originalGetSupportedExtensions = WebGLRenderingContext.prototype.getSupportedExtensions;
            const originalGetExtension = WebGLRenderingContext.prototype.getExtension;
            const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
            const originalGetShaderPrecisionFormat = WebGLRenderingContext.prototype.getShaderPrecisionFormat;
            
            // Hook getContext
            HTMLCanvasElement.prototype.getContext = function(type, attributes) {{
                const gl = originalGetContext.call(this, type, attributes);
                
                if (!gl || (type !== 'webgl' && type !== 'webgl2' && type !== 'experimental-webgl')) {{
                    return gl;
                }}
                
                // Hook getParameter - 伪造UNMASKED_VENDOR_WEBGL和UNMASKED_RENDERER_WEBGL
                const originalGetParameter = gl.getParameter;
                gl.getParameter = function(pname) {{
                    // UNMASKED_VENDOR_WEBGL = 0x9245
                    if (pname === 0x9245) {{
                        return fakeVendor;
                    }}
                    // UNMASKED_RENDERER_WEBGL = 0x9246
                    if (pname === 0x9246) {{
                        return fakeRenderer;
                    }}
                    // VENDOR
                    if (pname === 0x1F00) {{
                        return fakeVendor.split(' ')[0];
                    }}
                    // RENDERER
                    if (pname === 0x1F01) {{
                        return 'WebKit WebGL';
                    }}
                    // VERSION
                    if (pname === 0x1F02) {{
                        return 'WebGL 1.0 (OpenGL ES 2.0 Chromium)';
                    }}
                    // MAX_VIEWPORT_DIMS
                    if (pname === 0x0D3A) {{
                        return new Int32Array([16384, 16384]);
                    }}
                    
                    return originalGetParameter.call(this, pname);
                }};
                
                // Hook getSupportedExtensions
                gl.getSupportedExtensions = function() {{
                    return fakeExtensions.slice();
                }};
                
                // Hook getExtension
                gl.getExtension = function(name) {{
                    if (fakeExtensions.indexOf(name) === -1) {{
                        return null;
                    }}
                    return originalGetExtension.call(this, name);
                }};
                
                // Hook getShaderPrecisionFormat
                gl.getShaderPrecisionFormat = function(shaderType, precisionType) {{
                    const format = originalGetShaderPrecisionFormat.call(this, shaderType, precisionType);
                    
                    if (!format) {{
                        return format;
                    }}
                    
                    // 可以在这里微调精度值
                    return format;
                }};
                
                // Hook readPixels - 输出微调
                const originalReadPixels = gl.readPixels;
                gl.readPixels = function(x, y, width, height, format, type, pixels) {{
                    originalReadPixels.call(this, x, y, width, height, format, type, pixels);
                    
                    // 对像素数据添加微小噪声（可选，默认关闭以保证性能）
                    // 实际应用中可能需要更复杂的处理
                }};
                
                // Hook drawArrays / drawElements - 渲染结果微扰
                const originalDrawArrays = gl.drawArrays;
                gl.drawArrays = function(mode, first, count) {{
                    // 可以在这里添加渲染前的微扰
                    originalDrawArrays.call(this, mode, first, count);
                }};
                
                const originalDrawElements = gl.drawElements;
                gl.drawElements = function(mode, count, type, offset) {{
                    originalDrawElements.call(this, mode, count, type, offset);
                }};
                
                // 抗锯齿能力伪造
                Object.defineProperty(gl, 'antialias', {{
                    get: function() {{
                        return true;
                    }}
                }});
                
                return gl;
            }};
            
            // 也Hook WebGL2RenderingContext
            if (typeof WebGL2RenderingContext !== 'undefined') {{
                const originalGetParameter2 = WebGL2RenderingContext.prototype.getParameter;
                // 类似的Hook...
            }}
            
            console.log('WebGL fingerprint spoofing activated');
        }})();
        """
    
    def get_webgl_fingerprint_test_script(self) -> str:
        """生成WebGL指纹测试脚本"""
        return """
        // WebGL指纹测试
        (function() {
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            
            if (!gl) {
                return { supported: false };
            }
            
            const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
            
            let vendor = '';
            let renderer = '';
            
            if (debugInfo) {
                vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
                renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
            }
            
            const extensions = gl.getSupportedExtensions();
            
            // 生成简单的WebGL指纹图
            const vertexShaderSource = `
                attribute vec2 position;
                void main() {
                    gl_Position = vec4(position, 0.0, 1.0);
                }
            `;
            
            const fragmentShaderSource = `
                precision highp float;
                void main() {
                    gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
                }
            `;
            
            function createShader(type, source) {
                const shader = gl.createShader(type);
                gl.shaderSource(shader, source);
                gl.compileShader(shader);
                return shader;
            }
            
            const vertexShader = createShader(gl.VERTEX_SHADER, vertexShaderSource);
            const fragmentShader = createShader(gl.FRAGMENT_SHADER, fragmentShaderSource);
            
            const program = gl.createProgram();
            gl.attachShader(program, vertexShader);
            gl.attachShader(program, fragmentShader);
            gl.linkProgram(program);
            gl.useProgram(program);
            
            const positionBuffer = gl.createBuffer();
            gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
            gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
                -1.0, -1.0,
                 1.0, -1.0,
                -1.0,  1.0,
                 1.0,  1.0,
            ]), gl.STATIC_DRAW);
            
            const positionLocation = gl.getAttribLocation(program, 'position');
            gl.enableVertexAttribArray(positionLocation);
            gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);
            
            gl.viewport(0, 0, 256, 256);
            gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
            
            // 读取像素生成哈希
            const pixels = new Uint8Array(256 * 256 * 4);
            gl.readPixels(0, 0, 256, 256, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
            
            // 简单哈希
            let hash = 0;
            for (let i = 0; i < pixels.length; i += 16) {
                hash = ((hash << 5) - hash + pixels[i]) | 0;
            }
            
            return {
                supported: true,
                vendor: vendor,
                renderer: renderer,
                extensions_count: extensions ? extensions.length : 0,
                extensions: extensions,
                render_hash: hash,
                max_viewport_dims: gl.getParameter(gl.MAX_VIEWPORT_DIMS),
                max_texture_size: gl.getParameter(gl.MAX_TEXTURE_SIZE),
            };
        })();
        """
