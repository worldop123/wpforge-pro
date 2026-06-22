"""
翻译服务测试 - 测试 TranslationService、各引擎、术语库、缓存、记忆库
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from app.services.translation_service import (
    TranslationEngine,
    TranslationResult,
    TranslationTermManager,
    TranslationCache,
    TranslationEngineBase,
    AITranslationEngine,
    GoogleTranslationEngine,
    DeepLTranslationEngine,
    TranslationMemory,
    TranslationQualityEvaluator,
    TranslationService,
    translation_service,
)


class TestTranslationEngine:
    """TranslationEngine 枚举测试"""

    def test_engine_values(self):
        assert TranslationEngine.AI.value == "ai"
        assert TranslationEngine.GOOGLE.value == "google"
        assert TranslationEngine.DEEPL.value == "deepl"
        assert TranslationEngine.BAIDU.value == "baidu"
        assert TranslationEngine.YOUDAO.value == "youdao"

    def test_engine_count(self):
        assert len(TranslationEngine) >= 5

    def test_engine_is_string_enum(self):
        assert TranslationEngine.AI == "ai"


class TestTranslationResult:
    """TranslationResult 数据类测试"""

    def test_defaults(self):
        result = TranslationResult(
            source_text="hello",
            translated_text="你好",
            source_language="en",
            target_language="zh-CN",
            engine=TranslationEngine.AI,
        )
        assert result.model is None
        assert result.quality_score == 0.0
        assert result.is_polished is False
        assert result.used_terms == []
        assert result.translation_time == 0.0

    def test_with_all_fields(self):
        result = TranslationResult(
            source_text="hello",
            translated_text="你好",
            source_language="en",
            target_language="zh-CN",
            engine=TranslationEngine.DEEPL,
            model="gpt-4o",
            quality_score=0.95,
            is_polished=True,
            used_terms=["hello"],
            translation_time=1.5,
        )
        assert result.model == "gpt-4o"
        assert result.quality_score == 0.95
        assert result.is_polished is True
        assert result.used_terms == ["hello"]


class TestTranslationTermManager:
    """TranslationTermManager 测试"""

    def test_add_term(self):
        mgr = TranslationTermManager()
        mgr.add_term("hello", "你好")
        assert mgr.get_terms_count() == 1

    def test_add_term_case_insensitive(self):
        mgr = TranslationTermManager()
        mgr.add_term("Hello", "你好")
        # 术语以小写存储
        assert "hello" in mgr.terms["en_zh-CN"]

    def test_add_terms_batch(self):
        mgr = TranslationTermManager()
        mgr.add_terms_batch([("hello", "你好"), ("world", "世界")])
        assert mgr.get_terms_count() == 2

    def test_apply_terms(self):
        mgr = TranslationTermManager()
        mgr.add_term("hello", "你好")
        text, used = mgr.apply_terms("hello world")
        assert "你好" in text
        assert "hello" in used

    def test_apply_terms_no_terms(self):
        mgr = TranslationTermManager()
        text, used = mgr.apply_terms("hello world")
        assert text == "hello world"
        assert used == []

    def test_apply_terms_case_insensitive(self):
        mgr = TranslationTermManager()
        mgr.add_term("Hello", "你好")
        text, used = mgr.apply_terms("HELLO world")
        assert "你好" in text

    def test_apply_terms_longest_first(self):
        mgr = TranslationTermManager()
        mgr.add_term("smart", "智能")
        mgr.add_term("smart phone", "智能手机")
        text, used = mgr.apply_terms("smart phone case")
        # 长的先替换
        assert "智能手机" in text

    def test_get_terms_count_empty(self):
        mgr = TranslationTermManager()
        assert mgr.get_terms_count() == 0

    def test_get_terms_count_different_lang(self):
        mgr = TranslationTermManager()
        mgr.add_term("hello", "你好", "en", "zh-CN")
        mgr.add_term("hello", "bonjour", "en", "fr")
        assert mgr.get_terms_count("en", "zh-CN") == 1
        assert mgr.get_terms_count("en", "fr") == 1


class TestTranslationCache:
    """TranslationCache 测试"""

    def test_get_empty(self):
        cache = TranslationCache()
        result = cache.get("hello", "en", "zh-CN", "ai")
        assert result is None

    def test_set_and_get(self):
        cache = TranslationCache()
        result = TranslationResult(
            source_text="hello",
            translated_text="你好",
            source_language="en",
            target_language="zh-CN",
            engine=TranslationEngine.AI,
        )
        cache.set(result, "ai")
        cached = cache.get("hello", "en", "zh-CN", "ai")
        assert cached is not None
        assert cached.translated_text == "你好"

    def test_size(self):
        cache = TranslationCache()
        assert cache.size == 0
        result = TranslationResult(
            source_text="hello",
            translated_text="你好",
            source_language="en",
            target_language="zh-CN",
            engine=TranslationEngine.AI,
        )
        cache.set(result, "ai")
        assert cache.size == 1

    def test_clear(self):
        cache = TranslationCache()
        result = TranslationResult(
            source_text="hello",
            translated_text="你好",
            source_language="en",
            target_language="zh-CN",
            engine=TranslationEngine.AI,
        )
        cache.set(result, "ai")
        cache.clear()
        assert cache.size == 0

    def test_different_engine_different_cache(self):
        cache = TranslationCache()
        result = TranslationResult(
            source_text="hello",
            translated_text="你好",
            source_language="en",
            target_language="zh-CN",
            engine=TranslationEngine.AI,
        )
        cache.set(result, "ai")
        # 不同引擎应该 miss
        assert cache.get("hello", "en", "zh-CN", "google") is None

    def test_lru_eviction(self):
        cache = TranslationCache(max_size=2)
        for i in range(3):
            result = TranslationResult(
                source_text=f"text{i}",
                translated_text=f"翻译{i}",
                source_language="en",
                target_language="zh-CN",
                engine=TranslationEngine.AI,
            )
            cache.set(result, "ai")
        # 容量上限 2，应该驱逐一个
        assert cache.size == 2


class TestTranslationMemory:
    """TranslationMemory 测试"""

    def test_lookup_empty(self):
        memory = TranslationMemory()
        assert memory.lookup("hello", "en", "zh-CN") is None

    def test_add_and_lookup(self):
        memory = TranslationMemory()
        memory.add("hello", "你好", "en", "zh-CN")
        result = memory.lookup("hello", "en", "zh-CN")
        assert result == "你好"

    def test_lookup_case_insensitive(self):
        memory = TranslationMemory()
        memory.add("Hello", "你好", "en", "zh-CN")
        result = memory.lookup("hello", "en", "zh-CN")
        assert result == "你好"

    def test_add_increments_count(self):
        memory = TranslationMemory()
        memory.add("hello", "你好", "en", "zh-CN")
        memory.lookup("hello", "en", "zh-CN")
        memory.lookup("hello", "en", "zh-CN")
        # 找到 key 并检查 count
        key = memory._get_key("hello", "en", "zh-CN")
        assert memory.entries[key]["count"] == 3  # add(1) + lookup(2)

    def test_add_batch(self):
        memory = TranslationMemory()
        memory.add_batch([("hello", "你好"), ("world", "世界")], "en", "zh-CN")
        assert memory.lookup("hello", "en", "zh-CN") == "你好"
        assert memory.lookup("world", "en", "zh-CN") == "世界"

    def test_get_stats(self):
        memory = TranslationMemory()
        memory.add("hello", "你好", "en", "zh-CN")
        stats = memory.get_stats()
        assert stats["total_entries"] == 1
        assert stats["max_entries"] == 100000

    def test_different_language_pair(self):
        memory = TranslationMemory()
        memory.add("hello", "你好", "en", "zh-CN")
        # 不同语言对应该 miss
        assert memory.lookup("hello", "en", "ja") is None


class TestTranslationQualityEvaluator:
    """TranslationQualityEvaluator 测试"""

    def test_evaluate_basic(self):
        evaluator = TranslationQualityEvaluator()
        score = evaluator.evaluate("Hello world", "你好世界", "en", "zh-CN")
        assert 0.0 <= score <= 1.0

    def test_evaluate_empty_translation(self):
        evaluator = TranslationQualityEvaluator()
        score = evaluator.evaluate("Hello world", "", "en", "zh-CN")
        assert score < 1.0

    def test_evaluate_preserves_numbers(self):
        evaluator = TranslationQualityEvaluator()
        score = evaluator.evaluate("Price is 100", "价格是 100", "en", "zh-CN")
        assert score > 0.5

    def test_evaluate_garbled_text(self):
        evaluator = TranslationQualityEvaluator()
        score = evaluator.evaluate("Hello", "你好�", "en", "zh-CN")
        # 含乱码字符，分数应较低
        assert score < 1.0

    def test_has_garbled_chars(self):
        evaluator = TranslationQualityEvaluator()
        assert evaluator._has_garbled_chars("你好�") is True
        assert evaluator._has_garbled_chars("你好") is False


class TestAITranslationEngine:
    """AITranslationEngine 测试"""

    @pytest.mark.asyncio
    async def test_translate_with_mock(self):
        engine = AITranslationEngine()
        with patch("app.services.translation_service.ai_manager") as mock_ai:
            mock_resp = MagicMock()
            mock_resp.content = "  你好  "
            mock_ai.chat.return_value = mock_resp

            result = await engine.translate("hello", "en", "zh-CN")
            assert result.translated_text == "你好"
            assert result.source_text == "hello"
            assert result.engine == TranslationEngine.AI
            assert result.source_language == "en"
            assert result.target_language == "zh-CN"

    @pytest.mark.asyncio
    async def test_translate_raises_on_error(self):
        engine = AITranslationEngine()
        with patch("app.services.translation_service.ai_manager") as mock_ai:
            mock_ai.chat.side_effect = Exception("API error")
            with pytest.raises(Exception, match="API error"):
                await engine.translate("hello", "en", "zh-CN")


class TestGoogleTranslationEngine:
    """GoogleTranslationEngine 测试"""

    def test_is_available_without_key(self):
        engine = GoogleTranslationEngine(api_key=None)
        assert engine.is_available() is False

    def test_is_available_with_key(self):
        engine = GoogleTranslationEngine(api_key="test-key")
        assert engine.is_available() is True


class TestDeepLTranslationEngine:
    """DeepLTranslationEngine 测试"""

    def test_convert_lang_code_chinese(self):
        engine = DeepLTranslationEngine(api_key="test")
        assert engine._convert_lang_code("zh-CN") == "ZH"
        assert engine._convert_lang_code("en") == "EN"
        assert engine._convert_lang_code("de") == "DE"

    def test_convert_lang_code_unknown(self):
        engine = DeepLTranslationEngine(api_key="test")
        # 未知语言返回大写
        assert engine._convert_lang_code("xx") == "XX"

    def test_convert_lang_code_back(self):
        engine = DeepLTranslationEngine(api_key="test")
        assert engine._convert_lang_code_back("ZH") == "zh-CN"
        assert engine._convert_lang_code_back("EN") == "en"

    def test_is_available_with_key(self):
        engine = DeepLTranslationEngine(api_key="test-key")
        assert engine.is_available() is True


class TestTranslationService:
    """TranslationService 测试"""

    def test_singleton(self):
        from app.services.translation_service import translation_service as s1
        assert s1 is translation_service

    def test_init_engines(self):
        service = TranslationService()
        # AI 引擎总是可用
        assert "ai" in service.engines

    def test_get_engine(self):
        service = TranslationService()
        engine = service.get_engine("ai")
        assert engine is not None
        assert isinstance(engine, AITranslationEngine)

    def test_get_engine_unknown(self):
        service = TranslationService()
        assert service.get_engine("nonexistent") is None

    def test_get_available_engines(self):
        service = TranslationService()
        engines = service.get_available_engines()
        assert isinstance(engines, list)
        # AI 引擎可能可用（取决于配置）
        assert isinstance(engines, list)

    def test_add_term(self):
        service = TranslationService()
        service.add_term("hello", "你好")
        assert service.term_manager.get_terms_count() > 0

    def test_add_terms_batch(self):
        service = TranslationService()
        initial = service.term_manager.get_terms_count()
        service.add_terms_batch([("hello", "你好"), ("world", "世界")])
        assert service.term_manager.get_terms_count() >= initial + 2

    def test_get_stats(self):
        service = TranslationService()
        stats = service.get_stats()
        assert "engines" in stats
        assert "cache_size" in stats
        assert "terms_count" in stats
        assert "translation_memory" in stats

    @pytest.mark.asyncio
    async def test_translate_empty_text(self):
        service = TranslationService()
        result = await service.translate("", "en", "zh-CN")
        assert result.translated_text == ""
        assert result.quality_score == 1.0

    @pytest.mark.asyncio
    async def test_translate_with_mock_engine(self):
        service = TranslationService()
        mock_engine = MagicMock(spec=TranslationEngineBase)
        mock_engine.is_available.return_value = True
        mock_engine.translate = AsyncMock(return_value=TranslationResult(
            source_text="hello",
            translated_text="你好",
            source_language="en",
            target_language="zh-CN",
            engine=TranslationEngine.AI,
            quality_score=0.9,
        ))
        service.engines["ai"] = mock_engine

        result = await service.translate("hello", "en", "zh-CN", engine="ai", use_cache=False, use_memory=False, apply_terms=False)
        assert result.translated_text == "你好"
        mock_engine.translate.assert_called_once()

    @pytest.mark.asyncio
    async def test_translate_uses_cache(self):
        service = TranslationService()
        mock_engine = MagicMock(spec=TranslationEngineBase)
        mock_engine.is_available.return_value = True
        mock_engine.translate = AsyncMock(return_value=TranslationResult(
            source_text="hello",
            translated_text="你好",
            source_language="en",
            target_language="zh-CN",
            engine=TranslationEngine.AI,
            quality_score=0.9,
        ))
        service.engines["ai"] = mock_engine

        # 第一次翻译，调用引擎
        await service.translate("hello", "en", "zh-CN", engine="ai", use_memory=False, apply_terms=False)
        # 第二次应该命中缓存，不再调用引擎
        await service.translate("hello", "en", "zh-CN", engine="ai", use_memory=False, apply_terms=False)
        assert mock_engine.translate.call_count == 1

    @pytest.mark.asyncio
    async def test_translate_batch(self):
        service = TranslationService()
        mock_engine = MagicMock(spec=TranslationEngineBase)
        mock_engine.is_available.return_value = True

        async def mock_translate(text, source_lang, target_lang, **kwargs):
            return TranslationResult(
                source_text=text,
                translated_text=f"翻译:{text}",
                source_language=source_lang,
                target_language=target_lang,
                engine=TranslationEngine.AI,
                quality_score=0.9,
            )
        mock_engine.translate = mock_translate
        service.engines["ai"] = mock_engine

        results = await service.translate_batch(
            ["hello", "world"], "en", "zh-CN", engine="ai",
            use_cache=False, use_memory=False, apply_terms=False,
        )
        assert len(results) == 2
        assert results[0].translated_text == "翻译:hello"
        assert results[1].translated_text == "翻译:world"

    @pytest.mark.asyncio
    async def test_translate_product(self):
        service = TranslationService()
        mock_engine = MagicMock(spec=TranslationEngineBase)
        mock_engine.is_available.return_value = True

        async def mock_translate(text, source_lang, target_lang, **kwargs):
            return TranslationResult(
                source_text=text,
                translated_text=f"翻译:{text}",
                source_language=source_lang,
                target_language=target_lang,
                engine=TranslationEngine.AI,
                quality_score=0.9,
            )
        mock_engine.translate = mock_translate
        service.engines["ai"] = mock_engine

        product = {
            "name": "Test Product",
            "description": "A great product",
            "price": "99.99",
        }
        translated = await service.translate_product(
            product, "en", "zh-CN", engine="ai",
            use_cache=False, use_memory=False, apply_terms=False,
            fields=["name", "description"],
        )
        assert translated["name"] == "翻译:Test Product"
        assert translated["description"] == "翻译:A great product"
        # 未翻译字段保持不变
        assert translated["price"] == "99.99"

    @pytest.mark.asyncio
    async def test_translate_all_engines_fail_returns_fallback(self):
        service = TranslationService()
        mock_engine = MagicMock(spec=TranslationEngineBase)
        mock_engine.is_available.return_value = True
        mock_engine.translate = AsyncMock(side_effect=Exception("fail"))
        service.engines = {"ai": mock_engine}
        service._engine_priority = ["ai"]

        result = await service.translate(
            "hello", "en", "zh-CN", engine="ai",
            use_cache=False, use_memory=False, apply_terms=False,
            auto_fallback=True,
        )
        # 所有引擎失败时返回原文作为兜底
        assert result.translated_text == "hello"
        assert result.quality_score == 0.0
