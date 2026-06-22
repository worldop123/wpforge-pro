"""
反机器人绕过
提供各种反爬系统（PerimeterX、Akamai、Datadome等）的绕过策略
"""
import time
import random
from typing import Dict, Any, Optional, List

from app.core.logging import get_logger

logger = get_logger(__name__)


class AntiBotBypass:
    """反机器人绕过器"""
    
    # 已知的反爬系统
    KNOWN_SYSTEMS = [
        "perimeterx",
        "akamai",
        "datadome",
        "shape_security",
        "imperva",
        "cloudflare",
        "reCAPTCHA",
        "hcaptcha",
        "funcaptcha",
        "geetest",
    ]
    
    def __init__(self):
        self._detected_systems = {}
        self._bypass_strategies = {}
        self._success_rates = {}
    
    def detect_antibot_system(self, response_headers: Dict[str, str],
                               status_code: int = 200,
                               response_body: str = "") -> List[str]:
        """
        检测反爬系统
        
        Args:
            response_headers: 响应头
            status_code: 状态码
            response_body: 响应体
            
        Returns:
            检测到的反爬系统列表
        """
        detected = []
        
        # 检查响应头
        headers_lower = {k.lower(): v.lower() for k, v in response_headers.items()}
        
        # Cloudflare
        if "server" in headers_lower and "cloudflare" in headers_lower["server"]:
            detected.append("cloudflare")
        
        if "cf-ray" in headers_lower:
            if "cloudflare" not in detected:
                detected.append("cloudflare")
        
        # PerimeterX
        if "x-px" in str(headers_lower) or "perimeterx" in response_body.lower():
            detected.append("perimeterx")
        
        # Akamai
        if "x-akamai" in str(headers_lower) or "akamai" in response_body.lower():
            detected.append("akamai")
        
        # DataDome
        if "datadome" in str(headers_lower) or "datadome" in response_body.lower():
            detected.append("datadome")
        
        # Shape Security
        if "x-sf-request" in headers_lower or "shape security" in response_body.lower():
            detected.append("shape_security")
        
        # Imperva (Incapsula)
        if "x-iinfo" in headers_lower or "imperva" in response_body.lower():
            detected.append("imperva")
        
        # reCAPTCHA
        if "recaptcha" in response_body.lower() or "google.com/recaptcha" in response_body:
            detected.append("reCAPTCHA")
        
        # hCaptcha
        if "hcaptcha" in response_body.lower() or "hcaptcha.com" in response_body:
            detected.append("hcaptcha")
        
        # FunCAPTCHA
        if "funcaptcha" in response_body.lower() or "arkoselabs" in response_body.lower():
            detected.append("funcaptcha")
        
        # GeeTest
        if "geetest" in response_body.lower() or "gt.geetest.com" in response_body:
            detected.append("geetest")
        
        # 记录检测结果
        for system in detected:
            self._detected_systems[system] = self._detected_systems.get(system, 0) + 1
        
        return detected
    
    def get_bypass_strategy(self, system_name: str) -> Dict[str, Any]:
        """
        获取绕过策略
        
        Args:
            system_name: 反爬系统名称
            
        Returns:
            策略配置
        """
        strategies = {
            "perimeterx": {
                "name": "PerimeterX",
                "difficulty": "hard",
                "methods": [
                    "浏览器指纹伪造",
                    "TLS指纹伪造",
                    "行为模拟",
                    "Cookie处理",
                    "请求频率控制",
                ],
                "required_tools": [
                    "真实浏览器",
                    "住宅代理",
                    "指纹伪造",
                ],
                "success_rate": 0.7,
                "description": "需要完整的浏览器环境和真实的行为模拟",
            },
            "akamai": {
                "name": "Akamai Bot Manager",
                "difficulty": "very_hard",
                "methods": [
                    "传感器数据伪造",
                    "行为分析绕过",
                    "TLS指纹匹配",
                    "HTTP/2指纹匹配",
                ],
                "required_tools": [
                    "真实浏览器",
                    "高级指纹伪造",
                    "TLS指纹伪造",
                ],
                "success_rate": 0.5,
                "description": "Akamai是最难绕过的反爬系统之一",
            },
            "datadome": {
                "name": "DataDome",
                "difficulty": "hard",
                "methods": [
                    "设备指纹伪造",
                    "行为生物识别绕过",
                    "TLS指纹匹配",
                ],
                "required_tools": [
                    "真实浏览器",
                    "住宅代理",
                    "高级指纹伪造",
                ],
                "success_rate": 0.6,
                "description": "需要设备级别的指纹伪造",
            },
            "shape_security": {
                "name": "Shape Security",
                "difficulty": "hard",
                "methods": [
                    "客户端JavaScript分析",
                    "行为模拟",
                    "指纹伪造",
                ],
                "required_tools": [
                    "真实浏览器",
                    "行为模拟",
                ],
                "success_rate": 0.65,
                "description": "专注于客户端行为分析",
            },
            "cloudflare": {
                "name": "Cloudflare",
                "difficulty": "medium",
                "methods": [
                    "5秒盾等待",
                    "JavaScript执行",
                    "cf_clearance Cookie",
                    "Turnstile验证码",
                ],
                "required_tools": [
                    "浏览器环境",
                    "打码平台（可选）",
                ],
                "success_rate": 0.85,
                "description": "相对容易绕过，特别是使用真实浏览器",
            },
            "reCAPTCHA": {
                "name": "reCAPTCHA",
                "difficulty": "medium",
                "methods": [
                    "打码平台",
                    "行为模拟（v3）",
                ],
                "required_tools": [
                    "打码平台",
                ],
                "success_rate": 0.9,
                "description": "可以通过打码平台解决",
            },
            "hcaptcha": {
                "name": "hCaptcha",
                "difficulty": "medium",
                "methods": [
                    "打码平台",
                ],
                "required_tools": [
                    "打码平台",
                ],
                "success_rate": 0.85,
                "description": "可以通过打码平台解决",
            },
        }
        
        return strategies.get(system_name, {
            "name": system_name,
            "difficulty": "unknown",
            "methods": [],
            "required_tools": [],
            "success_rate": 0.5,
            "description": "未知的反爬系统",
        })
    
    def get_general_bypass_tips(self) -> List[str]:
        """获取通用的反爬绕过建议"""
        return [
            "使用真实的浏览器指纹，不要使用默认的无头浏览器指纹",
            "确保TLS指纹与浏览器UA匹配",
            "确保HTTP/2指纹与浏览器匹配",
            "模拟真实的人类行为，包括鼠标移动、滚动、打字等",
            "控制请求频率，不要太快",
            "使用住宅代理IP，避免数据中心IP",
            "正确处理Cookie，保持会话一致性",
            "正确处理重定向",
            "使用与IP匹配的时区和语言",
            "避免在短时间内发送太多请求",
            "随机化请求间隔",
            "模拟页面停留时间",
            "正确处理缓存",
            "模拟真实的浏览路径",
        ]
    
    def get_detected_systems(self) -> Dict[str, int]:
        """获取检测到的反爬系统统计"""
        return self._detected_systems.copy()
    
    def get_success_rate(self, system_name: str) -> float:
        """获取某个系统的绕过成功率"""
        return self._success_rates.get(system_name, 0.5)
    
    def set_success_rate(self, system_name: str, rate: float):
        """设置某个系统的绕过成功率"""
        self._success_rates[system_name] = rate
    
    def get_difficulty_level(self, system_name: str) -> str:
        """获取某个系统的难度级别"""
        strategy = self.get_bypass_strategy(system_name)
        return strategy.get("difficulty", "unknown")
    
    def get_all_systems(self) -> List[str]:
        """获取所有已知的反爬系统"""
        return self.KNOWN_SYSTEMS.copy()
