"""
验证码模块测试 - 打码平台管理器和验证码求解器
"""
import pytest
from unittest.mock import MagicMock

from app.services.proxy.captcha.captcha_providers import (
    BaseCaptchaProvider,
    TwoCaptchaProvider,
    AntiCaptchaProvider,
    CapMonsterProvider,
    CaptchaProviderManager,
)
from app.services.proxy.captcha.captcha_solver import (
    CaptchaType,
    CaptchaSolver,
)


# ==================== 打码平台测试 ====================

class TestTwoCaptchaProvider:
    """2Captcha 平台测试"""

    def test_creation(self):
        provider = TwoCaptchaProvider(api_key="test-key")
        assert provider.name == "2captcha"
        assert provider.api_key == "test-key"
        assert provider.base_url == "https://api.2captcha.com"

    def test_solve_recaptcha_v2(self):
        provider = TwoCaptchaProvider(api_key="test-key")
        result = provider.solve_recaptcha_v2("https://example.com", "site_key")
        assert result is None

    def test_solve_recaptcha_v3(self):
        provider = TwoCaptchaProvider(api_key="test-key")
        result = provider.solve_recaptcha_v3("https://example.com", "site_key")
        assert result is None

    def test_solve_hcaptcha(self):
        provider = TwoCaptchaProvider(api_key="test-key")
        result = provider.solve_hcaptcha("https://example.com", "site_key")
        assert result is None

    def test_solve_image_captcha(self):
        provider = TwoCaptchaProvider(api_key="test-key")
        result = provider.solve_image_captcha(b"image_data")
        assert result is None

    def test_get_balance(self):
        provider = TwoCaptchaProvider(api_key="test-key")
        assert provider.get_balance() == 0.0

    def test_get_stats(self):
        provider = TwoCaptchaProvider(api_key="test-key")
        stats = provider.get_stats()
        assert "balance" in stats
        assert "solved_count" in stats
        assert "failed_count" in stats

    def test_report_bad(self):
        provider = TwoCaptchaProvider(api_key="test-key")
        assert provider.report_bad("captcha_id") is False


class TestAntiCaptchaProvider:
    """Anti-Captcha 平台测试"""

    def test_creation(self):
        provider = AntiCaptchaProvider(api_key="test-key")
        assert provider.name == "anti-captcha"
        assert provider.base_url == "https://api.anti-captcha.com"

    def test_solve_recaptcha_v2(self):
        provider = AntiCaptchaProvider()
        assert provider.solve_recaptcha_v2("https://example.com", "key") is None

    def test_solve_hcaptcha(self):
        provider = AntiCaptchaProvider()
        assert provider.solve_hcaptcha("https://example.com", "key") is None

    def test_solve_image_captcha(self):
        provider = AntiCaptchaProvider()
        assert provider.solve_image_captcha(b"data") is None


class TestCapMonsterProvider:
    """CapMonster 平台测试"""

    def test_creation(self):
        provider = CapMonsterProvider(api_key="test-key")
        assert provider.name == "capmonster"
        assert provider.base_url == "https://api.capmonster.cloud"

    def test_solve_recaptcha_v2(self):
        provider = CapMonsterProvider()
        assert provider.solve_recaptcha_v2("https://example.com", "key") is None

    def test_solve_recaptcha_v3(self):
        provider = CapMonsterProvider()
        assert provider.solve_recaptcha_v3("https://example.com", "key") is None

    def test_solve_image_captcha(self):
        provider = CapMonsterProvider()
        assert provider.solve_image_captcha(b"data") is None


class TestCaptchaProviderManager:
    """打码平台管理器测试"""

    def test_creation(self):
        manager = CaptchaProviderManager()
        assert manager.get_current_provider() is None
        assert manager.get_provider_names() == []

    def test_add_provider(self):
        manager = CaptchaProviderManager()
        provider = TwoCaptchaProvider(api_key="key")
        manager.add_provider("2captcha", provider)
        assert manager.get_current_provider() is provider
        assert "2captcha" in manager.get_provider_names()

    def test_add_multiple_providers(self):
        manager = CaptchaProviderManager()
        manager.add_provider("2captcha", TwoCaptchaProvider())
        manager.add_provider("anti-captcha", AntiCaptchaProvider())
        assert len(manager.get_provider_names()) == 2

    def test_remove_provider(self):
        manager = CaptchaProviderManager()
        manager.add_provider("2captcha", TwoCaptchaProvider())
        manager.add_provider("anti-captcha", AntiCaptchaProvider())
        manager.remove_provider("2captcha")
        assert "2captcha" not in manager.get_provider_names()
        # 当前平台应切换到剩余的
        assert manager.get_current_provider() is not None

    def test_remove_current_provider(self):
        manager = CaptchaProviderManager()
        manager.add_provider("2captcha", TwoCaptchaProvider())
        manager.remove_provider("2captcha")
        assert manager.get_current_provider() is None

    def test_remove_nonexistent_provider(self):
        manager = CaptchaProviderManager()
        # 不应抛异常
        manager.remove_provider("nonexistent")

    def test_set_priority_order(self):
        manager = CaptchaProviderManager()
        manager.add_provider("a", TwoCaptchaProvider())
        manager.add_provider("b", AntiCaptchaProvider())
        manager.set_priority_order(["b", "a"])
        best = manager.select_best_provider()
        assert best == "b"

    def test_set_auto_select(self):
        manager = CaptchaProviderManager()
        manager.set_auto_select(False)
        manager.add_provider("a", TwoCaptchaProvider())
        # 自动选择关闭时返回当前平台
        assert manager.select_best_provider() == "a"

    def test_select_best_provider_empty(self):
        manager = CaptchaProviderManager()
        assert manager.select_best_provider() is None

    def test_get_provider(self):
        manager = CaptchaProviderManager()
        provider = TwoCaptchaProvider()
        manager.add_provider("2captcha", provider)
        assert manager.get_provider("2captcha") is provider
        assert manager.get_provider("nonexistent") is None

    def test_get_all_providers(self):
        manager = CaptchaProviderManager()
        manager.add_provider("a", TwoCaptchaProvider())
        manager.add_provider("b", AntiCaptchaProvider())
        all_providers = manager.get_all_providers()
        assert len(all_providers) == 2

    def test_get_all_balances(self):
        manager = CaptchaProviderManager()
        manager.add_provider("a", TwoCaptchaProvider())
        manager.add_provider("b", AntiCaptchaProvider())
        balances = manager.get_all_balances()
        assert "a" in balances
        assert "b" in balances

    def test_get_total_balance(self):
        manager = CaptchaProviderManager()
        manager.add_provider("a", TwoCaptchaProvider())
        assert manager.get_total_balance() == 0.0

    def test_check_health(self):
        manager = CaptchaProviderManager()
        manager.add_provider("a", TwoCaptchaProvider())
        health = manager.check_health()
        assert health["a"] is True


# ==================== 验证码求解器测试 ====================

class TestCaptchaType:
    """验证码类型枚举测试"""

    def test_captcha_type_values(self):
        assert CaptchaType.RECAPTCHA_V2.value == "recaptcha_v2"
        assert CaptchaType.HCAPTCHA.value == "hcaptcha"
        assert CaptchaType.IMAGE_CAPTCHA.value == "image_captcha"


class TestCaptchaSolver:
    """验证码求解器测试"""

    def test_creation(self):
        solver = CaptchaSolver()
        assert solver.get_provider_list() == []
        assert solver.get_budget_status()["budget_limit"] == 0.0

    def test_register_provider(self):
        solver = CaptchaSolver()
        solver.register_provider("2captcha", TwoCaptchaProvider())
        assert "2captcha" in solver.get_provider_list()

    def test_set_current_provider(self):
        solver = CaptchaSolver()
        solver.register_provider("2captcha", TwoCaptchaProvider())
        solver.set_current_provider("2captcha")
        assert solver.get_best_provider(CaptchaType.RECAPTCHA_V2) == "2captcha"

    def test_set_current_provider_nonexistent(self):
        solver = CaptchaSolver()
        # 不应抛异常
        solver.set_current_provider("nonexistent")

    def test_set_budget_limit(self):
        solver = CaptchaSolver()
        solver.set_budget_limit(10.0)
        assert solver.get_budget_status()["budget_limit"] == 10.0

    def test_solve_captcha_no_provider(self):
        solver = CaptchaSolver()
        result = solver.solve_captcha(
            CaptchaType.RECAPTCHA_V2,
            site_url="https://example.com",
            site_key="key",
        )
        assert result is None

    def test_solve_captcha_recaptcha_v2(self):
        solver = CaptchaSolver()
        mock_provider = MagicMock()
        mock_provider.solve_recaptcha_v2.return_value = "token123"
        solver.register_provider("mock", mock_provider)

        result = solver.solve_captcha(
            CaptchaType.RECAPTCHA_V2,
            site_url="https://example.com",
            site_key="key",
        )
        assert result == "token123"
        assert solver.get_budget_status()["solved_count"] == 1

    def test_solve_captcha_recaptcha_v3(self):
        solver = CaptchaSolver()
        mock_provider = MagicMock()
        mock_provider.solve_recaptcha_v3.return_value = "token"
        solver.register_provider("mock", mock_provider)

        result = solver.solve_captcha(
            CaptchaType.RECAPTCHA_V3,
            site_url="https://example.com",
            site_key="key",
        )
        assert result == "token"

    def test_solve_captcha_hcaptcha(self):
        solver = CaptchaSolver()
        mock_provider = MagicMock()
        mock_provider.solve_hcaptcha.return_value = "token"
        solver.register_provider("mock", mock_provider)

        result = solver.solve_captcha(
            CaptchaType.HCAPTCHA,
            site_url="https://example.com",
            site_key="key",
        )
        assert result == "token"

    def test_solve_captcha_image(self):
        solver = CaptchaSolver()
        mock_provider = MagicMock()
        mock_provider.solve_image_captcha.return_value = "text"
        solver.register_provider("mock", mock_provider)

        result = solver.solve_captcha(
            CaptchaType.IMAGE_CAPTCHA,
            site_url="https://example.com",
            image_data=b"img",
        )
        assert result == "text"

    def test_solve_captcha_funcaptcha(self):
        solver = CaptchaSolver()
        mock_provider = MagicMock()
        mock_provider.solve_funcaptcha.return_value = "token"
        solver.register_provider("mock", mock_provider)

        result = solver.solve_captcha(
            CaptchaType.FUNCAPTCHA,
            site_url="https://example.com",
            site_key="key",
        )
        assert result == "token"

    def test_solve_captcha_geetest(self):
        solver = CaptchaSolver()
        mock_provider = MagicMock()
        mock_provider.solve_geetest.return_value = "token"
        solver.register_provider("mock", mock_provider)

        result = solver.solve_captcha(
            CaptchaType.GEETEST,
            site_url="https://example.com",
        )
        assert result == "token"

    def test_solve_captcha_turnstile(self):
        solver = CaptchaSolver()
        mock_provider = MagicMock()
        mock_provider.solve_turnstile.return_value = "token"
        solver.register_provider("mock", mock_provider)

        result = solver.solve_captcha(
            CaptchaType.CLOUDFLARE_TURNSTILE,
            site_url="https://example.com",
            site_key="key",
        )
        assert result == "token"

    def test_solve_captcha_slider(self):
        solver = CaptchaSolver()
        mock_provider = MagicMock()
        mock_provider.solve_slider_captcha.return_value = "token"
        solver.register_provider("mock", mock_provider)

        result = solver.solve_captcha(
            CaptchaType.SLIDER_CAPTCHA,
            site_url="https://example.com",
            image_data=b"img",
        )
        assert result == "token"

    def test_solve_captcha_click(self):
        solver = CaptchaSolver()
        mock_provider = MagicMock()
        mock_provider.solve_click_captcha.return_value = "token"
        solver.register_provider("mock", mock_provider)

        result = solver.solve_captcha(
            CaptchaType.CLICK_CAPTCHA,
            site_url="https://example.com",
            image_data=b"img",
        )
        assert result == "token"

    def test_solve_captcha_failed(self):
        solver = CaptchaSolver()
        mock_provider = MagicMock()
        mock_provider.solve_recaptcha_v2.return_value = None
        solver.register_provider("mock", mock_provider)

        result = solver.solve_captcha(
            CaptchaType.RECAPTCHA_V2,
            site_url="https://example.com",
            site_key="key",
        )
        assert result is None
        assert solver.get_budget_status()["failed_count"] == 1

    def test_solve_captcha_exception(self):
        solver = CaptchaSolver()
        mock_provider = MagicMock()
        mock_provider.solve_recaptcha_v2.side_effect = Exception("API error")
        solver.register_provider("mock", mock_provider)

        result = solver.solve_captcha(
            CaptchaType.RECAPTCHA_V2,
            site_url="https://example.com",
            site_key="key",
        )
        assert result is None
        assert solver.get_budget_status()["failed_count"] == 1

    def test_solve_captcha_budget_exceeded(self):
        solver = CaptchaSolver()
        solver.set_budget_limit(0.001)
        mock_provider = MagicMock()
        mock_provider.solve_recaptcha_v2.return_value = "token"
        solver.register_provider("mock", mock_provider)

        # 第一次花费 0.002，超过预算
        solver.solve_captcha(
            CaptchaType.RECAPTCHA_V2,
            site_url="https://example.com",
            site_key="key",
        )
        # 第二次应因预算不足返回 None
        result = solver.solve_captcha(
            CaptchaType.RECAPTCHA_V2,
            site_url="https://example.com",
            site_key="key",
        )
        assert result is None

    def test_solve_captcha_unsupported_type(self):
        solver = CaptchaSolver()
        mock_provider = MagicMock()
        solver.register_provider("mock", mock_provider)

        # SMS_CAPTCHA 不在处理分支中
        result = solver.solve_captcha(
            CaptchaType.SMS_CAPTCHA,
            site_url="https://example.com",
        )
        assert result is None

    def test_report_bad_captcha(self):
        solver = CaptchaSolver()
        mock_provider = MagicMock()
        mock_provider.report_bad = MagicMock(return_value=True)
        solver.register_provider("mock", mock_provider)

        solver.report_bad_captcha("captcha_id")
        mock_provider.report_bad.assert_called_once_with("captcha_id")

    def test_report_bad_captcha_no_provider(self):
        solver = CaptchaSolver()
        # 不应抛异常
        solver.report_bad_captcha("captcha_id")

    def test_get_supported_types(self):
        solver = CaptchaSolver()
        types = solver.get_supported_types()
        assert CaptchaType.RECAPTCHA_V2 in types
        assert len(types) >= 8

    def test_get_provider_list(self):
        solver = CaptchaSolver()
        solver.register_provider("a", TwoCaptchaProvider())
        solver.register_provider("b", AntiCaptchaProvider())
        assert len(solver.get_provider_list()) == 2
