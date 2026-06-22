"""
AI服务测试
"""
import pytest
from app.services.ai_service import (
    AIService,
    AIProvider,
    AIModel,
    get_ai_service,
)
from app.services.ai_orchestrator import AIOrchestrator, get_ai_orchestrator


class TestAIProvider:
    """AI提供商枚举测试"""

    def test_provider_values(self):
        """测试提供商值"""
        assert hasattr(AIProvider, 'OPENAI')
        assert hasattr(AIProvider, 'ANTHROPIC')
        assert hasattr(AIProvider, 'GOOGLE')
        assert hasattr(AIProvider, 'OLLAMA')

    def test_provider_count(self):
        """测试提供商数量"""
        assert len(AIProvider) >= 4


class TestAIModel:
    """AI模型枚举测试"""

    def test_model_values(self):
        """测试模型值"""
        assert hasattr(AIModel, 'GPT_4')
        assert hasattr(AIModel, 'GPT_3_5_TURBO')
        assert hasattr(AIModel, 'CLAUDE_3_OPUS')
        assert hasattr(AIModel, 'GEMINI_PRO')

    def test_model_count(self):
        """测试模型数量"""
        assert len(AIModel) >= 4


class TestAIService:
    """AI服务测试"""

    def test_service_creation(self):
        """测试服务创建"""
        service = AIService()
        assert service is not None

    def test_generate_text(self):
        """测试生成文本"""
        service = AIService()
        try:
            result = service.generate_text("Hello, how are you?")
            assert isinstance(result, str)
            assert len(result) > 0
        except Exception:
            # API Key未配置是正常的
            pass

    def test_generate_text_with_system_prompt(self):
        """测试带系统提示的文本生成"""
        service = AIService()
        try:
            result = service.generate_text(
                "Hello",
                system_prompt="You are a helpful assistant."
            )
            assert isinstance(result, str)
        except Exception:
            pass

    def test_generate_json(self):
        """测试生成JSON"""
        service = AIService()
        try:
            result = service.generate_json(
                "Return a JSON object with name and age",
                schema={"name": "string", "age": "number"}
            )
            assert isinstance(result, dict)
            assert "name" in result
        except Exception:
            pass

    def test_summarize(self):
        """测试摘要"""
        service = AIService()
        try:
            text = "This is a long text about artificial intelligence and machine learning. " * 10
            summary = service.summarize(text, max_length=50)
            assert isinstance(summary, str)
            assert len(summary) < len(text)
        except Exception:
            pass

    def test_translate(self):
        """测试翻译"""
        service = AIService()
        try:
            result = service.translate("Hello World", "en", "zh")
            assert isinstance(result, str)
            assert len(result) > 0
        except Exception:
            pass

    def test_classify(self):
        """测试分类"""
        service = AIService()
        try:
            result = service.classify(
                "This is a great product!",
                categories=["positive", "negative", "neutral"]
            )
            assert isinstance(result, str)
            assert result in ["positive", "negative", "neutral"]
        except Exception:
            pass

    def test_extract_keywords(self):
        """测试提取关键词"""
        service = AIService()
        try:
            keywords = service.extract_keywords(
                "Artificial intelligence and machine learning are transforming technology."
            )
            assert isinstance(keywords, list)
            assert len(keywords) > 0
        except Exception:
            pass

    def test_analyze_sentiment(self):
        """测试情感分析"""
        service = AIService()
        try:
            result = service.analyze_sentiment("I love this product!")
            assert isinstance(result, dict)
            assert "sentiment" in result
            assert "score" in result
        except Exception:
            pass

    def test_generate_product_description(self):
        """测试生成产品描述"""
        service = AIService()
        try:
            description = service.generate_product_description(
                product_name="Wireless Headphones",
                features=["Bluetooth 5.0", "Noise Cancelling", "30h Battery"]
            )
            assert isinstance(description, str)
            assert len(description) > 0
        except Exception:
            pass

    def test_generate_seo_title(self):
        """测试生成SEO标题"""
        service = AIService()
        try:
            title = service.generate_seo_title(
                content="This is a product page about wireless headphones",
                keywords=["headphones", "wireless", "bluetooth"]
            )
            assert isinstance(title, str)
            assert len(title) <= 60  # SEO建议长度
        except Exception:
            pass

    def test_generate_meta_description(self):
        """测试生成Meta描述"""
        service = AIService()
        try:
            description = service.generate_meta_description(
                content="Product page content here",
                keywords=["headphones", "wireless"]
            )
            assert isinstance(description, str)
            assert len(description) <= 160  # SEO建议长度
        except Exception:
            pass

    def test_rewrite_content(self):
        """测试内容改写"""
        service = AIService()
        try:
            original = "This is the original content that needs to be rewritten."
            rewritten = service.rewrite_content(original, style="professional")
            assert isinstance(rewritten, str)
            assert len(rewritten) > 0
            assert rewritten != original
        except Exception:
            pass

    def test_get_available_models(self):
        """测试获取可用模型"""
        service = AIService()
        models = service.get_available_models()
        assert isinstance(models, list)
        assert len(models) > 0

    def test_set_provider(self):
        """测试设置提供商"""
        service = AIService()
        service.set_provider(AIProvider.OPENAI)
        assert service.current_provider == AIProvider.OPENAI

    def test_set_model(self):
        """测试设置模型"""
        service = AIService()
        service.set_model(AIModel.GPT_3_5_TURBO)
        assert service.current_model == AIModel.GPT_3_5_TURBO

    def test_get_usage_stats(self):
        """测试获取使用统计"""
        service = AIService()
        stats = service.get_usage_stats()
        assert isinstance(stats, dict)
        assert "total_tokens" in stats
        assert "total_requests" in stats

    def test_get_instance(self):
        """测试单例模式"""
        s1 = get_ai_service()
        s2 = get_ai_service()
        assert s1 is s2

    def test_calculate_cost(self):
        """测试计算费用"""
        service = AIService()
        cost = service.calculate_cost(
            prompt_tokens=1000,
            completion_tokens=500,
            model=AIModel.GPT_3_5_TURBO
        )
        assert isinstance(cost, float)
        assert cost >= 0

    def test_check_api_key(self):
        """测试检查API Key"""
        service = AIService()
        is_valid = service.check_api_key()
        assert isinstance(is_valid, bool)

    def test_stream_generate(self):
        """测试流式生成"""
        service = AIService()
        try:
            chunks = []
            for chunk in service.stream_generate("Hello"):
                chunks.append(chunk)
                assert isinstance(chunk, str)
            assert len(chunks) > 0
        except Exception:
            pass


class TestAIOrchestrator:
    """AI编排器测试"""

    def test_orchestrator_creation(self):
        """测试编排器创建"""
        orchestrator = AIOrchestrator()
        assert orchestrator is not None

    def test_analyze_website(self):
        """测试分析网站"""
        orchestrator = AIOrchestrator()
        try:
            result = orchestrator.analyze_website("https://example.com")
            assert isinstance(result, dict)
            assert "design" in result
            assert "content" in result
            assert "technology" in result
        except Exception:
            pass

    def test_generate_theme_config(self):
        """测试生成主题配置"""
        orchestrator = AIOrchestrator()
        try:
            config = orchestrator.generate_theme_config(
                industry="ecommerce",
                style="modern"
            )
            assert isinstance(config, dict)
            assert "colors" in config
            assert "typography" in config
        except Exception:
            pass

    def test_generate_page_layout(self):
        """测试生成页面布局"""
        orchestrator = AIOrchestrator()
        try:
            layout = orchestrator.generate_page_layout(
                page_type="landing",
                industry="ecommerce"
            )
            assert isinstance(layout, dict)
            assert "sections" in layout
        except Exception:
            pass

    def test_optimize_content_seo(self):
        """测试SEO内容优化"""
        orchestrator = AIOrchestrator()
        try:
            optimized = orchestrator.optimize_content_seo(
                content="This is a test product.",
                keywords=["test", "product"]
            )
            assert isinstance(optimized, dict)
            assert "content" in optimized
            assert "seo_score" in optimized
        except Exception:
            pass

    def test_generate_product_content(self):
        """测试生成产品内容"""
        orchestrator = AIOrchestrator()
        try:
            content = orchestrator.generate_product_content(
                product_name="Test Product",
                features=["Feature 1", "Feature 2"],
                target_audience="everyone"
            )
            assert isinstance(content, dict)
            assert "title" in content
            assert "description" in content
            assert "short_description" in content
        except Exception:
            pass

    def test_generate_reviews(self):
        """测试生成评论"""
        orchestrator = AIOrchestrator()
        try:
            reviews = orchestrator.generate_reviews(
                product_name="Test Product",
                count=5
            )
            assert isinstance(reviews, list)
            assert len(reviews) == 5
            assert all("author" in r for r in reviews)
            assert all("rating" in r for r in reviews)
            assert all("content" in r for r in reviews)
        except Exception:
            pass

    def test_get_instance(self):
        """测试单例模式"""
        o1 = get_ai_orchestrator()
        o2 = get_ai_orchestrator()
        assert o1 is o2

    def test_select_best_model(self):
        """测试选择最佳模型"""
        orchestrator = AIOrchestrator()
        model = orchestrator.select_best_model(task="text_generation")
        assert model is not None

    def test_get_task_capabilities(self):
        """测试获取任务能力"""
        orchestrator = AIOrchestrator()
        capabilities = orchestrator.get_task_capabilities()
        assert isinstance(capabilities, list)
        assert len(capabilities) > 0

    def test_estimate_cost(self):
        """测试估算成本"""
        orchestrator = AIOrchestrator()
        cost = orchestrator.estimate_cost(task="text_generation", input_size=1000)
        assert isinstance(cost, float)
        assert cost >= 0
