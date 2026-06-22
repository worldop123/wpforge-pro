"""
验证码求解器
提供各种类型验证码的自动识别功能
"""
import time
import random
from typing import Dict, Any, Optional, List
from enum import Enum

from app.core.logging import get_logger

logger = get_logger(__name__)


class CaptchaType(Enum):
    """验证码类型枚举"""
    RECAPTCHA_V2 = "recaptcha_v2"
    RECAPTCHA_V3 = "recaptcha_v3"
    HCAPTCHA = "hcaptcha"
    FUNCAPTCHA = "funcaptcha"
    GEETEST = "geetest"
    CLOUDFLARE_TURNSTILE = "cloudflare_turnstile"
    IMAGE_CAPTCHA = "image_captcha"
    SLIDER_CAPTCHA = "slider_captcha"
    CLICK_CAPTCHA = "click_captcha"
    SMS_CAPTCHA = "sms_captcha"
    EMAIL_CAPTCHA = "email_captcha"


class CaptchaSolver:
    """验证码求解器"""
    
    def __init__(self):
        self._providers = {}
        self._current_provider = None
        self._budget_limit = 0.0  # 预算限制（美元）
        self._total_spent = 0.0
        self._solved_count = 0
        self._failed_count = 0
    
    def register_provider(self, name: str, provider):
        """注册打码平台"""
        self._providers[name] = provider
        if self._current_provider is None:
            self._current_provider = name
    
    def set_current_provider(self, name: str):
        """设置当前使用的打码平台"""
        if name in self._providers:
            self._current_provider = name
        else:
            logger.warning(f"Provider {name} not found")
    
    def set_budget_limit(self, limit: float):
        """设置预算限制"""
        self._budget_limit = limit
    
    def get_budget_status(self) -> Dict[str, Any]:
        """获取预算状态"""
        return {
            "budget_limit": self._budget_limit,
            "total_spent": self._total_spent,
            "remaining": self._budget_limit - self._total_spent,
            "solved_count": self._solved_count,
            "failed_count": self._failed_count,
        }
    
    def solve_captcha(self, captcha_type: CaptchaType, 
                       site_url: str,
                       site_key: str = "",
                       image_data: Optional[bytes] = None,
                       **kwargs) -> Optional[str]:
        """
        求解验证码
        
        Args:
            captcha_type: 验证码类型
            site_url: 网站URL
            site_key: 网站密钥
            image_data: 图片数据（图片验证码）
            **kwargs: 其他参数
            
        Returns:
            验证码解决方案，如果失败则返回None
        """
        # 检查预算
        if self._budget_limit > 0 and self._total_spent >= self._budget_limit:
            logger.warning("Budget limit reached")
            return None
        
        if not self._current_provider or self._current_provider not in self._providers:
            logger.warning("No captcha provider available")
            return None
        
        provider = self._providers[self._current_provider]
        
        try:
            # 根据验证码类型调用不同的方法
            if captcha_type == CaptchaType.RECAPTCHA_V2:
                result = provider.solve_recaptcha_v2(site_url, site_key, **kwargs)
            elif captcha_type == CaptchaType.RECAPTCHA_V3:
                result = provider.solve_recaptcha_v3(site_url, site_key, **kwargs)
            elif captcha_type == CaptchaType.HCAPTCHA:
                result = provider.solve_hcaptcha(site_url, site_key, **kwargs)
            elif captcha_type == CaptchaType.FUNCAPTCHA:
                result = provider.solve_funcaptcha(site_url, site_key, **kwargs)
            elif captcha_type == CaptchaType.GEETEST:
                result = provider.solve_geetest(site_url, **kwargs)
            elif captcha_type == CaptchaType.CLOUDFLARE_TURNSTILE:
                result = provider.solve_turnstile(site_url, site_key, **kwargs)
            elif captcha_type == CaptchaType.IMAGE_CAPTCHA:
                result = provider.solve_image_captcha(image_data, **kwargs)
            elif captcha_type == CaptchaType.SLIDER_CAPTCHA:
                result = provider.solve_slider_captcha(image_data, **kwargs)
            elif captcha_type == CaptchaType.CLICK_CAPTCHA:
                result = provider.solve_click_captcha(image_data, **kwargs)
            else:
                logger.warning(f"Unsupported captcha type: {captcha_type}")
                return None
            
            if result:
                self._solved_count += 1
                # 更新花费（假设每个验证码0.002美元）
                self._total_spent += 0.002
                return result
            else:
                self._failed_count += 1
                return None
                
        except Exception as e:
            logger.error(f"Error solving captcha: {e}")
            self._failed_count += 1
            return None
    
    def report_bad_captcha(self, captcha_id: str):
        """报告错误的验证码（用于退款）"""
        if not self._current_provider or self._current_provider not in self._providers:
            return
        
        provider = self._providers[self._current_provider]
        if hasattr(provider, 'report_bad'):
            provider.report_bad(captcha_id)
    
    def get_supported_types(self) -> List[CaptchaType]:
        """获取支持的验证码类型"""
        return list(CaptchaType)
    
    def get_provider_list(self) -> List[str]:
        """获取可用的打码平台列表"""
        return list(self._providers.keys())
    
    def get_best_provider(self, captcha_type: CaptchaType) -> Optional[str]:
        """获取最适合某类验证码的平台"""
        # 简单实现：返回当前平台
        return self._current_provider
