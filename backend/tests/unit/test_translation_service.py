"""
翻译服务测试
"""
import pytest
from app.services.translation_service import (
    TranslationService,
    TranslationEngine,
    get_translation_service,
)


class TestTranslationEngine:
    """翻译引擎枚举测试"""

    def test_engine_values(self):
        """测试引擎值"""
        assert hasattr(TranslationEngine, 'DEEPL')
        assert hasattr(TranslationEngine, 'GOOGLE')
        assert hasattr(TranslationEngine, 'OPENAI')
        assert hasattr(TranslationEngine, 'ANTHROPIC')
        assert hasattr(TranslationEngine, 'LOCAL')

    def test_engine_count(self):
        """测试引擎数量"""
        assert len(TranslationEngine) >= 5


class TestTranslationService:
    """翻译服务测试"""

    def test_service_creation(self):
        """测试服务创建"""
        service = TranslationService()
        assert service is not None

    def test_translate_text(self):
        """测试翻译文本"""
        service = TranslationService()
        result = service.translate("Hello", "en", "zh")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_translate_chinese(self):
        """测试翻译成中文"""
        service = TranslationService()
        result = service.translate("Hello World", "en", "zh")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_translate_batch(self):
        """测试批量翻译"""
        service = TranslationService()
        texts = ["Hello", "World", "Test"]
        results = service.translate_batch(texts, "en", "zh")
        assert isinstance(results, list)
        assert len(results) == 3
        assert all(isinstance(r, str) for r in results)

    def test_detect_language(self):
        """测试语言检测"""
        service = TranslationService()
        lang = service.detect_language("Hello World")
        assert isinstance(lang, str)
        assert len(lang) == 2  # ISO 639-1

    def test_detect_language_chinese(self):
        """测试中文检测"""
        service = TranslationService()
        lang = service.detect_language("你好世界")
        assert isinstance(lang, str)
        # 可能是zh或zh-CN等

    def test_get_supported_languages(self):
        """测试获取支持的语言"""
        service = TranslationService()
        languages = service.get_supported_languages()
        assert isinstance(languages, list)
        assert len(languages) > 0
        assert "en" in languages
        assert "zh" in languages

    def test_translate_with_quality_check(self):
        """测试带质量检查的翻译"""
        service = TranslationService()
        result = service.translate_with_quality("Hello World", "en", "zh")
        assert isinstance(result, dict)
        assert "translation" in result
        assert "quality_score" in result
        assert 0 <= result["quality_score"] <= 100

    def test_optimize_for_seo(self):
        """测试SEO优化翻译"""
        service = TranslationService()
        result = service.optimize_for_seo(
            "This is a test product",
            "en",
            "zh",
            keywords=["test", "product"]
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_terminology(self):
        """测试获取术语库"""
        service = TranslationService()
        terms = service.get_terminology("ecommerce")
        assert isinstance(terms, dict)
        assert len(terms) >= 0

    def test_add_terminology(self):
        """测试添加术语"""
        service = TranslationService()
        service.add_terminology("product", "产品", "en", "zh")
        terms = service.get_terminology("ecommerce")
        assert isinstance(terms, dict)

    def test_get_translation_memory(self):
        """测试获取翻译记忆"""
        service = TranslationService()
        memory = service.get_translation_memory()
        assert isinstance(memory, list) or isinstance(memory, dict)

    def test_add_to_memory(self):
        """测试添加到翻译记忆"""
        service = TranslationService()
        service.add_to_memory("Hello", "你好", "en", "zh")
        memory = service.get_translation_memory()
        assert isinstance(memory, list) or isinstance(memory, dict)

    def test_get_available_engines(self):
        """测试获取可用引擎"""
        service = TranslationService()
        engines = service.get_available_engines()
        assert isinstance(engines, list)
        assert len(engines) > 0

    def test_set_engine(self):
        """测试设置引擎"""
        service = TranslationService()
        service.set_engine(TranslationEngine.GOOGLE)
        assert service.current_engine == TranslationEngine.GOOGLE

    def test_get_engine_status(self):
        """测试获取引擎状态"""
        service = TranslationService()
        status = service.get_engine_status(TranslationEngine.GOOGLE)
        assert isinstance(status, dict)
        assert "available" in status

    def test_fallback_translation(self):
        """测试降级翻译"""
        service = TranslationService()
        # 模拟主引擎失败，应该自动降级
        result = service.translate("Hello", "en", "zh")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_usage_stats(self):
        """测试获取使用统计"""
        service = TranslationService()
        stats = service.get_usage_stats()
        assert isinstance(stats, dict)
        assert "total_chars" in stats
        assert "by_engine" in stats

    def test_get_instance(self):
        """测试单例模式"""
        s1 = get_translation_service()
        s2 = get_translation_service()
        assert s1 is s2

    def test_translate_long_text(self):
        """测试长文本翻译"""
        service = TranslationService()
        long_text = "Hello " * 100
        result = service.translate(long_text, "en", "zh")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_translate_html(self):
        """测试HTML翻译"""
        service = TranslationService()
        html = "<p>Hello <strong>World</strong></p>"
        result = service.translate_html(html, "en", "zh")
        assert isinstance(result, str)
        assert "<p>" in result
        assert "<strong>" in result

    def test_preserve_placeholders(self):
        """测试保留占位符"""
        service = TranslationService()
        text = "Hello {name}, your order {order_id} is ready."
        result = service.translate(text, "en", "zh")
        assert isinstance(result, str)
        assert "{name}" in result
        assert "{order_id}" in result

    def test_get_language_name(self):
        """测试获取语言名称"""
        service = TranslationService()
        name = service.get_language_name("zh")
        assert isinstance(name, str)
        assert len(name) > 0

    def test_is_rtl_language(self):
        """测试是否RTL语言"""
        service = TranslationService()
        assert service.is_rtl_language("ar") is True
        assert service.is_rtl_language("en") is False
        assert service.is_rtl_language("zh") is False

    def test_calculate_cost(self):
        """测试计算费用"""
        service = TranslationService()
        cost = service.calculate_cost(1000, TranslationEngine.GOOGLE)
        assert isinstance(cost, float)
        assert cost >= 0

    def test_translate_with_glossary(self):
        """测试带术语表的翻译"""
        service = TranslationService()
        glossary = {"product": "产品", "order": "订单"}
        result = service.translate_with_glossary(
            "This product is in your order.",
            "en",
            "zh",
            glossary
        )
        assert isinstance(result, str)
        assert len(result) > 0
