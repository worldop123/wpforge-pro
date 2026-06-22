"""
SEO服务测试

覆盖:
- app.services.seo_service: SEOAnalyzer, SEOGenerator, SiteSpeedOptimizer
- app.services.seo_enhanced: KeywordGenerator, SchemaGenerator, InternalLinkBuilder,
  ImageSEO, SEOService
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.services.seo_service import (
    SEOAnalysisResult,
    SEOAnalyzer,
    SEOGenerator,
    SiteSpeedOptimizer,
    seo_analyzer,
    seo_generator,
    site_speed_optimizer,
)
from app.services.seo_enhanced import (
    SEOScore,
    SchemaData,
    KeywordGenerator,
    SchemaGenerator,
    InternalLinkBuilder,
    ImageSEO,
    SEOService,
    seo_service,
)
from app.services.ai_service import ChatMessage, ChatResponse


# ---------------------------------------------------------------------------
# SEOAnalysisResult 数据类
# ---------------------------------------------------------------------------
class TestSEOAnalysisResult:
    def test_defaults(self):
        result = SEOAnalysisResult(url="https://example.com")
        assert result.url == "https://example.com"
        assert result.overall_score == 0
        assert result.content_score == 0
        assert result.technical_score == 0
        assert result.performance_score == 0
        assert result.title is None
        assert result.description is None
        assert result.keywords is None
        assert result.issues == []
        assert result.recommendations == []
        assert result.headings == []
        assert result.images == []
        assert result.links == []
        assert result.word_count == 0
        assert result.keyword_density == {}

    def test_custom_values(self):
        result = SEOAnalysisResult(
            url="https://example.com/page",
            overall_score=85,
            title="Test Title",
            word_count=500,
        )
        assert result.url == "https://example.com/page"
        assert result.overall_score == 85
        assert result.title == "Test Title"
        assert result.word_count == 500

    def test_independent_lists(self):
        """两个实例的列表字段应当相互独立"""
        a = SEOAnalysisResult(url="a")
        b = SEOAnalysisResult(url="b")
        a.issues.append({"type": "x"})
        assert b.issues == []


# ---------------------------------------------------------------------------
# SEOAnalyzer
# ---------------------------------------------------------------------------
class TestSEOAnalyzer:
    def test_analyze_html_complete_page(self):
        html = """
        <html>
        <head>
            <title>Test Product - Best Quality Electronics Online Store</title>
            <meta name="description" content="This is a test product with high quality and great features for everyday use.">
            <meta name="keywords" content="test, product, electronics">
            <link rel="canonical" href="https://example.com/product" />
            <meta property="og:title" content="Test Product" />
            <meta property="og:image" content="https://example.com/img.jpg" />
        </head>
        <body>
            <h1>Test Product</h1>
            <h2>Features</h2>
            <p>This is a long product description with enough words to pass the content threshold.
            It contains many words about the test product and its features. The product is great
            and has many use cases. Customers love it because it works well and lasts long.</p>
            <img src="https://example.com/img.jpg" alt="Product image" />
            <a href="/related">Related product</a>
        </body>
        </html>
        """
        result = seo_analyzer.analyze_html(html, "https://example.com/product")
        assert result.url == "https://example.com/product"
        assert result.title is not None
        assert "Test Product" in result.title
        assert result.description is not None
        assert result.keywords is not None
        assert result.word_count > 0
        assert len(result.headings) >= 2
        assert any(h["level"] == 1 for h in result.headings)
        assert len(result.images) == 1
        assert result.images[0]["has_alt"] is True
        assert len(result.links) >= 1
        assert 0 <= result.overall_score <= 100
        assert 0 <= result.content_score <= 100
        assert 0 <= result.technical_score <= 100
        assert result.performance_score == 70

    def test_analyze_html_missing_title(self):
        html = "<html><body><h1>Only body</h1></body></html>"
        result = seo_analyzer.analyze_html(html, "https://example.com")
        assert result.title is None
        # 缺少 description 会产生 error
        assert any(i["type"] == "description" and i["severity"] == "error" for i in result.issues)

    def test_analyze_html_title_too_short(self):
        html = "<html><head><title>Hi</title></head><body></body></html>"
        result = seo_analyzer.analyze_html(html, "https://example.com")
        assert any(i["type"] == "title" and "过短" in i["message"] for i in result.issues)

    def test_analyze_html_title_too_long(self):
        long_title = "A" * 100
        html = f"<html><head><title>{long_title}</title></head><body></body></html>"
        result = seo_analyzer.analyze_html(html, "https://example.com")
        assert any(i["type"] == "title" and "过长" in i["message"] for i in result.issues)

    def test_analyze_html_description_too_short(self):
        html = (
            "<html><head>"
            "<title>Normal length title here</title>"
            "<meta name='description' content='short' />"
            "</head><body></body></html>"
        )
        result = seo_analyzer.analyze_html(html, "https://example.com")
        assert any(i["type"] == "description" and "过短" in i["message"] for i in result.issues)

    def test_analyze_html_missing_h1(self):
        html = (
            "<html><head>"
            "<title>Normal length title here</title>"
            "<meta name='description' content='A description that is long enough to pass validation.' />"
            "</head><body><h2>Sub</h2></body></html>"
        )
        result = seo_analyzer.analyze_html(html, "https://example.com")
        assert any(i["type"] == "headings" and i["severity"] == "error" for i in result.issues)

    def test_analyze_html_multiple_h1(self):
        html = (
            "<html><head>"
            "<title>Normal length title here</title>"
            "<meta name='description' content='A description that is long enough to pass validation.' />"
            "</head><body><h1>One</h1><h1>Two</h1></body></html>"
        )
        result = seo_analyzer.analyze_html(html, "https://example.com")
        assert any(i["type"] == "headings" and "H1" in i["message"] for i in result.issues)

    def test_analyze_html_missing_alt(self):
        html = (
            "<html><head>"
            "<title>Normal length title here</title>"
            "<meta name='description' content='A description that is long enough to pass validation.' />"
            "</head><body><h1>Title</h1><img src='x.jpg' /></body></html>"
        )
        result = seo_analyzer.analyze_html(html, "https://example.com")
        assert any(i["type"] == "images" for i in result.issues)

    def test_analyze_html_missing_canonical(self):
        html = (
            "<html><head>"
            "<title>Normal length title here</title>"
            "<meta name='description' content='A description that is long enough to pass validation.' />"
            "</head><body><h1>Title</h1></body></html>"
        )
        result = seo_analyzer.analyze_html(html, "https://example.com")
        assert any(i["type"] == "canonical" for i in result.issues)

    def test_analyze_html_missing_og_tags(self):
        html = (
            "<html><head>"
            "<title>Normal length title here</title>"
            "<meta name='description' content='A description that is long enough to pass validation.' />"
            "<link rel='canonical' href='https://example.com' />"
            "</head><body><h1>Title</h1></body></html>"
        )
        result = seo_analyzer.analyze_html(html, "https://example.com")
        assert any(i["type"] == "og" for i in result.issues)

    def test_analyze_html_with_keywords(self):
        # 关键词密度过低
        html = (
            "<html><head>"
            "<title>Normal length title here</title>"
            "<meta name='description' content='A description that is long enough to pass validation.' />"
            "</head><body><h1>Title</h1>"
            "<p>" + " ".join(["word"] * 200) + "</p>"
            "</body></html>"
        )
        result = seo_analyzer.analyze_html(html, "https://example.com", target_keywords=["rareterm"])
        assert "rareterm" in result.keyword_density
        assert result.keyword_density["rareterm"] == 0.0
        assert any(i["type"] == "keyword" for i in result.issues)

    def test_analyze_html_keyword_high_density(self):
        # 关键词密度过高
        words = ["phone"] * 50 + ["other"] * 50
        html = (
            "<html><head>"
            "<title>Normal length title here</title>"
            "<meta name='description' content='A description that is long enough to pass validation.' />"
            "</head><body><h1>Title</h1>"
            "<p>" + " ".join(words) + "</p>"
            "</body></html>"
        )
        result = seo_analyzer.analyze_html(html, "https://example.com", target_keywords=["phone"])
        assert result.keyword_density["phone"] > 3.0
        assert any(i["type"] == "keyword" and "过高" in i["message"] for i in result.issues)

    def test_analyze_html_generates_recommendations(self):
        html = "<html><body></body></html>"
        result = seo_analyzer.analyze_html(html, "https://example.com")
        # 至少有 description 错误，应当生成对应建议
        assert len(result.recommendations) > 0
        assert all("suggestion" in r for r in result.recommendations)

    def test_analyze_html_internal_link(self):
        html = (
            "<html><head>"
            "<title>Title</title>"
            "<meta name='description' content='Description long enough for validation purposes here.' />"
            "</head><body><h1>Title</h1>"
            "<a href='/internal'>Internal</a>"
            "<a href='https://other.com'>External</a>"
            "</body></html>"
        )
        result = seo_analyzer.analyze_html(html, "https://example.com")
        internal = [l for l in result.links if l["is_internal"]]
        external = [l for l in result.links if not l["is_internal"]]
        assert len(internal) == 1
        assert len(external) == 1

    def test_analyze_html_empty_anchor_text(self):
        html = (
            "<html><head>"
            "<title>Title</title>"
            "<meta name='description' content='Description long enough for validation purposes here.' />"
            "</head><body><h1>Title</h1>"
            "<a href='/x'><img src='icon.png' /></a>"
            "</body></html>"
        )
        result = seo_analyzer.analyze_html(html, "https://example.com")
        assert any(i["type"] == "links" for i in result.issues)

    def test_analyze_html_score_calculation(self):
        """完整页面应当有较高分数"""
        html = """
        <html><head>
        <title>A Good Length Title For The Page</title>
        <meta name='description' content='A description that is long enough to pass validation purposes here.' />
        <link rel='canonical' href='https://example.com' />
        <meta property='og:title' content='T' />
        <meta property='og:image' content='i.jpg' />
        </head><body>
        <h1>Main</h1>
        <p>""" + " ".join(["content"] * 350) + """</p>
        <img src='i.jpg' alt='pic' />
        </body></html>
        """
        result = seo_analyzer.analyze_html(html, "https://example.com")
        assert result.overall_score > 0
        assert result.content_score > 0
        assert result.technical_score > 0


# ---------------------------------------------------------------------------
# SEOGenerator (async, uses ai_manager)
# ---------------------------------------------------------------------------
class TestSEOGenerator:
    @pytest.mark.asyncio
    async def test_generate_seo_title(self):
        generator = SEOGenerator()
        mock_response = ChatResponse(content="Best Test Product - Buy Now", model="test", provider="openai")
        with patch("app.services.seo_service.ai_manager") as mock_ai:
            mock_ai.chat.return_value = mock_response
            title = await generator.generate_seo_title("content", ["test", "product"])
            assert title == "Best Test Product - Buy Now"
            assert mock_ai.chat.called
            args, kwargs = mock_ai.chat.call_args
            assert len(kwargs["messages"]) == 2
            assert kwargs["messages"][0].role == "system"
            assert kwargs["messages"][1].role == "user"

    @pytest.mark.asyncio
    async def test_generate_seo_title_truncates(self):
        generator = SEOGenerator()
        long_title = "A" * 200
        mock_response = ChatResponse(content=long_title, model="test", provider="openai")
        with patch("app.services.seo_service.ai_manager") as mock_ai:
            mock_ai.chat.return_value = mock_response
            title = await generator.generate_seo_title("content", ["test"], max_length=60)
            assert len(title) <= 60
            assert title.endswith("...")

    @pytest.mark.asyncio
    async def test_generate_meta_description(self):
        generator = SEOGenerator()
        mock_response = ChatResponse(content="A great description for the product.", model="test", provider="openai")
        with patch("app.services.seo_service.ai_manager") as mock_ai:
            mock_ai.chat.return_value = mock_response
            desc = await generator.generate_meta_description("content", ["test"])
            assert desc == "A great description for the product."

    @pytest.mark.asyncio
    async def test_generate_meta_description_truncates(self):
        generator = SEOGenerator()
        long_desc = "B" * 300
        mock_response = ChatResponse(content=long_desc, model="test", provider="openai")
        with patch("app.services.seo_service.ai_manager") as mock_ai:
            mock_ai.chat.return_value = mock_response
            desc = await generator.generate_meta_description("content", ["test"], max_length=160)
            assert len(desc) <= 160
            assert desc.endswith("...")

    @pytest.mark.asyncio
    async def test_optimize_content(self):
        generator = SEOGenerator()
        mock_response = ChatResponse(content="optimized content", model="test", provider="openai")
        with patch("app.services.seo_service.ai_manager") as mock_ai:
            mock_ai.chat.return_value = mock_response
            result = await generator.optimize_content("original content", ["kw"])
            assert result == "optimized content"

    @pytest.mark.asyncio
    async def test_optimize_content_uses_optimization_type(self):
        generator = SEOGenerator()
        mock_response = ChatResponse(content="optimized", model="test", provider="openai")
        with patch("app.services.seo_service.ai_manager") as mock_ai:
            mock_ai.chat.return_value = mock_response
            await generator.optimize_content("c", ["kw"], optimization_type="max_seo")
            args, kwargs = mock_ai.chat.call_args
            assert "max_seo" in kwargs["messages"][0].content


# ---------------------------------------------------------------------------
# SiteSpeedOptimizer
# ---------------------------------------------------------------------------
class TestSiteSpeedOptimizer:
    def test_get_optimization_suggestions_returns_list(self):
        optimizer = SiteSpeedOptimizer()
        suggestions = optimizer.get_optimization_suggestions({})
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    def test_get_optimization_suggestions_structure(self):
        optimizer = SiteSpeedOptimizer()
        suggestions = optimizer.get_optimization_suggestions({})
        for s in suggestions:
            assert "category" in s
            assert "title" in s
            assert "description" in s
            assert "priority" in s
            assert "impact" in s
            assert "effort" in s
            assert "tools" in s
            assert isinstance(s["tools"], list)

    def test_get_optimization_suggestions_categories(self):
        optimizer = SiteSpeedOptimizer()
        suggestions = optimizer.get_optimization_suggestions({})
        categories = {s["category"] for s in suggestions}
        assert "images" in categories
        assert "caching" in categories
        assert "cdn" in categories

    def test_generate_htaccess_rules_empty(self):
        optimizer = SiteSpeedOptimizer()
        rules = optimizer.generate_htaccess_rules([])
        assert "BEGIN WPForge SEO Optimization" in rules
        assert "END WPForge SEO Optimization" in rules
        assert "GZIP" not in rules
        assert "Browser Caching" not in rules

    def test_generate_htaccess_rules_gzip(self):
        optimizer = SiteSpeedOptimizer()
        rules = optimizer.generate_htaccess_rules(["gzip"])
        assert "GZIP Compression" in rules
        assert "mod_deflate.c" in rules
        assert "Browser Caching" not in rules

    def test_generate_htaccess_rules_compression_alias(self):
        optimizer = SiteSpeedOptimizer()
        rules = optimizer.generate_htaccess_rules(["compression"])
        assert "GZIP Compression" in rules

    def test_generate_htaccess_rules_caching(self):
        optimizer = SiteSpeedOptimizer()
        rules = optimizer.generate_htaccess_rules(["caching"])
        assert "Browser Caching" in rules
        assert "mod_expires.c" in rules
        assert "ExpiresActive On" in rules

    def test_generate_htaccess_rules_all(self):
        optimizer = SiteSpeedOptimizer()
        rules = optimizer.generate_htaccess_rules(["gzip", "caching"])
        assert "GZIP Compression" in rules
        assert "Browser Caching" in rules


# ---------------------------------------------------------------------------
# KeywordGenerator
# ---------------------------------------------------------------------------
class TestKeywordGenerator:
    def test_generate_lsi_keywords_product(self):
        gen = KeywordGenerator()
        kws = gen.generate_lsi_keywords("phone", keyword_type="product", count=5)
        assert isinstance(kws, list)
        assert len(kws) == 5
        assert all("phone" in k for k in kws)

    def test_generate_lsi_keywords_service(self):
        gen = KeywordGenerator()
        kws = gen.generate_lsi_keywords("cleaning", keyword_type="service", count=3)
        assert len(kws) == 3
        assert all("cleaning" in k for k in kws)

    def test_generate_lsi_keywords_blog(self):
        gen = KeywordGenerator()
        kws = gen.generate_lsi_keywords("marketing", keyword_type="blog", count=4)
        assert len(kws) == 4
        assert all("marketing" in k for k in kws)

    def test_generate_lsi_keywords_unknown_type_defaults_to_product(self):
        gen = KeywordGenerator()
        kws = gen.generate_lsi_keywords("phone", keyword_type="unknown", count=2)
        assert len(kws) == 2

    def test_generate_lsi_keywords_count_greater_than_available(self):
        gen = KeywordGenerator()
        # count 超过模板数量时返回全部
        kws = gen.generate_lsi_keywords("phone", count=100)
        assert len(kws) <= 15

    def test_generate_long_tail_keywords_default(self):
        gen = KeywordGenerator()
        kws = gen.generate_long_tail_keywords("phone", count=5)
        assert len(kws) == 5
        assert all("phone" in k for k in kws)

    def test_generate_long_tail_keywords_custom_modifiers(self):
        gen = KeywordGenerator()
        kws = gen.generate_long_tail_keywords(
            "phone", modifiers=["best", "cheap"], count=10
        )
        assert len(kws) == 2
        assert all("phone" in k for k in kws)

    def test_generate_question_keywords(self):
        gen = KeywordGenerator()
        kws = gen.generate_question_keywords("phone")
        assert isinstance(kws, list)
        assert len(kws) > 0
        assert all("phone" in k for k in kws)
        assert any(k.startswith("What") for k in kws)
        assert any(k.startswith("How") for k in kws)


# ---------------------------------------------------------------------------
# SchemaGenerator
# ---------------------------------------------------------------------------
class TestSchemaGenerator:
    def test_generate_product_schema(self):
        gen = SchemaGenerator()
        product = {
            "name": "Test Product",
            "description": "A test product",
            "price": "29.99",
            "currency": "USD",
            "image": "https://example.com/img.jpg",
            "sku": "TEST001",
            "brand": "TestBrand",
        }
        schema = gen.generate_product_schema(product)
        assert isinstance(schema, SchemaData)
        assert schema.schema_type == "Product"
        assert schema.data["name"] == "Test Product"
        assert schema.data["offers"]["price"] == "29.99"
        assert schema.data["offers"]["priceCurrency"] == "USD"
        assert schema.data["offers"]["availability"] == "https://schema.org/InStock"

    def test_generate_product_schema_out_of_stock(self):
        gen = SchemaGenerator()
        schema = gen.generate_product_schema({"name": "X", "in_stock": False})
        assert schema.data["offers"]["availability"] == "https://schema.org/OutOfStock"

    def test_generate_product_schema_with_rating(self):
        gen = SchemaGenerator()
        schema = gen.generate_product_schema({
            "name": "X",
            "rating": 4.5,
            "review_count": 10,
        })
        assert "aggregateRating" in schema.data
        assert schema.data["aggregateRating"]["ratingValue"] == 4.5

    def test_generate_product_schema_with_reviews(self):
        gen = SchemaGenerator()
        schema = gen.generate_product_schema({
            "name": "X",
            "reviews": [
                {"rating": 5, "author": "A", "content": "good"},
                {"rating": 4, "author": "B", "content": "ok"},
                {"rating": 3, "author": "C", "content": "meh"},
                {"rating": 2, "author": "D", "content": "bad"},
                {"rating": 1, "author": "E", "content": "terrible"},
                {"rating": 5, "author": "F", "content": "extra"},  # 应被截断到5条
            ],
        })
        assert len(schema.data["review"]) == 5

    def test_generate_article_schema(self):
        gen = SchemaGenerator()
        article = {
            "title": "Test Article",
            "description": "An article",
            "author": "John",
            "date_published": "2024-01-01",
            "url": "https://example.com/article",
        }
        schema = gen.generate_article_schema(article)
        assert schema.schema_type == "Article"
        assert schema.data["headline"] == "Test Article"
        assert schema.data["author"]["name"] == "John"
        assert schema.data["datePublished"] == "2024-01-01"

    def test_generate_faq_schema(self):
        gen = SchemaGenerator()
        faqs = [
            {"question": "What is this?", "answer": "A product."},
            {"question": "How much?", "answer": "$29.99"},
        ]
        schema = gen.generate_faq_schema(faqs)
        assert schema.schema_type == "FAQPage"
        assert len(schema.data["mainEntity"]) == 2
        assert schema.data["mainEntity"][0]["@type"] == "Question"
        assert schema.data["mainEntity"][0]["acceptedAnswer"]["@type"] == "Answer"

    def test_generate_breadcrumb_schema(self):
        gen = SchemaGenerator()
        items = [
            {"name": "Home", "url": "https://example.com"},
            {"name": "Products", "url": "https://example.com/products"},
        ]
        schema = gen.generate_breadcrumb_schema(items)
        assert schema.schema_type == "BreadcrumbList"
        assert len(schema.data["itemListElement"]) == 2
        assert schema.data["itemListElement"][0]["position"] == 1
        assert schema.data["itemListElement"][1]["position"] == 2

    def test_generate_review_schema(self):
        gen = SchemaGenerator()
        reviews = [{
            "product_name": "Test",
            "rating": 4.5,
            "author": "John",
            "content": "Great!",
            "date": "2024-01-01",
        }]
        schema = gen.generate_review_schema(reviews)
        assert schema.schema_type == "Review"
        assert schema.data["reviewRating"]["ratingValue"] == 4.5
        assert schema.data["author"]["name"] == "John"

    def test_generate_review_schema_empty(self):
        gen = SchemaGenerator()
        schema = gen.generate_review_schema([])
        assert schema.schema_type == "Review"
        assert schema.data == {}

    def test_generate_local_business_schema(self):
        gen = SchemaGenerator()
        business = {
            "name": "My Shop",
            "phone": "+1234567890",
            "city": "Test City",
        }
        schema = gen.generate_local_business_schema(business)
        assert schema.schema_type == "LocalBusiness"
        assert schema.data["name"] == "My Shop"
        assert schema.data["telephone"] == "+1234567890"
        assert schema.data["address"]["addressLocality"] == "Test City"

    def test_generate_organization_schema(self):
        gen = SchemaGenerator()
        org = {"name": "Org", "url": "https://example.com", "email": "a@b.com"}
        schema = gen.generate_organization_schema(org)
        assert schema.schema_type == "Organization"
        assert schema.data["name"] == "Org"
        assert schema.data["contactPoint"]["email"] == "a@b.com"

    def test_generate_website_schema(self):
        gen = SchemaGenerator()
        site = {"name": "MySite", "url": "https://example.com"}
        schema = gen.generate_website_schema(site)
        assert schema.schema_type == "WebSite"
        assert schema.data["name"] == "MySite"
        assert "potentialAction" in schema.data
        assert schema.data["potentialAction"]["@type"] == "SearchAction"

    def test_schema_to_json_ld(self):
        schema = SchemaData(schema_type="Product", data={"name": "X"})
        json_ld = schema.to_json_ld()
        assert json_ld["@context"] == "https://schema.org"
        assert json_ld["@type"] == "Product"
        assert json_ld["name"] == "X"


# ---------------------------------------------------------------------------
# InternalLinkBuilder
# ---------------------------------------------------------------------------
class TestInternalLinkBuilder:
    def test_build_internal_links_adds_link(self):
        builder = InternalLinkBuilder()
        content = "This is a test product with great features."
        keywords = [{"keyword": "product", "url": "/products"}]
        result = builder.build_internal_links(content, keywords)
        assert "<a href=\"/products\"" in result
        assert "product" in result

    def test_build_internal_links_respects_max(self):
        builder = InternalLinkBuilder()
        content = "apple banana cherry apple banana cherry apple banana cherry"
        keywords = [
            {"keyword": "apple", "url": "/a"},
            {"keyword": "banana", "url": "/b"},
            {"keyword": "cherry", "url": "/c"},
        ]
        result = builder.build_internal_links(content, keywords, max_links=2)
        assert result.count("<a href=") == 2

    def test_build_internal_links_skips_empty(self):
        builder = InternalLinkBuilder()
        content = "test content"
        keywords = [
            {"keyword": "", "url": "/x"},
            {"keyword": "test", "url": ""},
        ]
        result = builder.build_internal_links(content, keywords)
        assert "<a" not in result

    def test_build_internal_links_case_insensitive(self):
        builder = InternalLinkBuilder()
        content = "The Product is great."
        keywords = [{"keyword": "product", "url": "/p"}]
        result = builder.build_internal_links(content, keywords)
        assert "<a href=\"/p\"" in result

    def test_generate_related_posts(self):
        builder = InternalLinkBuilder()
        all_posts = [{"id": i} for i in range(10)]
        related = builder.generate_related_posts({"id": 0}, all_posts, count=3)
        assert len(related) == 3
        assert all(r in all_posts for r in related)

    def test_generate_related_posts_count_exceeds_available(self):
        builder = InternalLinkBuilder()
        all_posts = [{"id": 1}, {"id": 2}]
        related = builder.generate_related_posts({"id": 0}, all_posts, count=5)
        assert len(related) == 2

    def test_build_breadcrumbs(self):
        builder = InternalLinkBuilder()
        hierarchy = [
            {"name": "Products", "url": "/products"},
            {"name": "Electronics", "url": "/products/electronics"},
        ]
        crumbs = builder.build_breadcrumbs("Test Product", hierarchy)
        assert crumbs[0]["name"] == "Home"
        assert crumbs[0]["url"] == "/"
        assert crumbs[-1]["name"] == "Test Product"
        assert len(crumbs) == 4


# ---------------------------------------------------------------------------
# ImageSEO
# ---------------------------------------------------------------------------
class TestImageSEO:
    def test_generate_alt_text_simple(self):
        seo = ImageSEO()
        alt = seo.generate_alt_text("red-shoes.jpg")
        assert isinstance(alt, str)
        assert len(alt) > 0
        assert "Red Shoes" in alt

    def test_generate_alt_text_with_product_name(self):
        seo = ImageSEO()
        alt = seo.generate_alt_text("img.jpg", product_name="Nike Air")
        assert "Nike Air" in alt

    def test_generate_alt_text_with_context(self):
        seo = ImageSEO()
        alt = seo.generate_alt_text("img.jpg", product_name="Nike Air", context="front view")
        assert "Nike Air" in alt

    def test_generate_alt_text_truncates(self):
        seo = ImageSEO()
        long_name = "a" * 200 + ".jpg"
        alt = seo.generate_alt_text(long_name)
        assert len(alt) <= 125

    def test_optimize_image_filename(self):
        seo = ImageSEO()
        result = seo.optimize_image_filename("My Image.jpg", "red shoes")
        assert result.endswith(".jpg")
        assert "red-shoes" in result
        assert " " not in result

    def test_optimize_image_filename_no_extension(self):
        seo = ImageSEO()
        result = seo.optimize_image_filename("filename", "keyword")
        assert result.endswith(".jpg")
        assert "keyword" in result

    def test_optimize_image_filename_cleans_keyword(self):
        seo = ImageSEO()
        result = seo.optimize_image_filename("f.jpg", "Key Word!@#")
        assert " " not in result
        assert "!" not in result

    def test_generate_image_sitemap(self):
        seo = ImageSEO()
        images = [
            {
                "page_url": "https://example.com/page",
                "image_url": "https://example.com/img.jpg",
                "title": "Test",
                "caption": "Caption",
            }
        ]
        xml = seo.generate_image_sitemap(images)
        assert "<?xml" in xml
        assert "<urlset" in xml
        assert "image:image" in xml
        assert "https://example.com/img.jpg" in xml
        assert "https://example.com/page" in xml

    def test_generate_image_sitemap_empty(self):
        seo = ImageSEO()
        xml = seo.generate_image_sitemap([])
        assert "<?xml" in xml
        assert "<urlset" in xml
        assert "</urlset>" in xml


# ---------------------------------------------------------------------------
# SEOService (enhanced)
# ---------------------------------------------------------------------------
class TestSEOService:
    def test_init_creates_components(self):
        svc = SEOService()
        assert isinstance(svc.keyword_generator, KeywordGenerator)
        assert isinstance(svc.schema_generator, SchemaGenerator)
        assert isinstance(svc.internal_link_builder, InternalLinkBuilder)
        assert isinstance(svc.image_seo, ImageSEO)

    def test_optimize_page_seo(self):
        svc = SEOService()
        result = svc.optimize_page_seo(
            title="Test Product",
            description="A product description.",
            content="This is the product content with enough words.",
            primary_keyword="product",
        )
        assert "original" in result
        assert "optimized" in result
        assert "score" in result
        assert "lsi_keywords" in result
        assert "long_tail_keywords" in result
        assert result["original"]["title"] == "Test Product"
        assert "product" in result["optimized"]["title"].lower()

    def test_optimize_page_seo_adds_keyword_to_title(self):
        svc = SEOService()
        result = svc.optimize_page_seo(
            title="Some Random Title",
            description="Some description.",
            content="content",
            primary_keyword="widget",
        )
        assert "widget" in result["optimized"]["title"].lower()

    def test_optimize_page_seo_truncates_long_title(self):
        svc = SEOService()
        long_title = "A" * 100
        result = svc.optimize_page_seo(
            title=long_title,
            description="desc",
            content="content",
            primary_keyword="aaa",
        )
        assert len(result["optimized"]["title"]) <= 60

    def test_calculate_seo_score_good(self):
        svc = SEOService()
        content = "keyword " * 200  # ~2% density
        score = svc.calculate_seo_score(
            title="keyword in title with enough length",
            description="keyword in description with enough length to pass validation",
            content=content,
            keyword="keyword",
        )
        assert isinstance(score, SEOScore)
        assert 0 <= score.overall <= 100
        assert score.title > 0
        assert score.description > 0
        assert score.content > 0

    def test_calculate_seo_score_missing_keyword(self):
        svc = SEOService()
        score = svc.calculate_seo_score(
            title="A title without the target",
            description="A description without the target word",
            content="Some content here without the target.",
            keyword="missing",
        )
        assert score.overall < 100
        assert any("关键词" in i for i in score.issues)

    def test_calculate_seo_score_with_images(self):
        svc = SEOService()
        score = svc.calculate_seo_score(
            title="keyword title",
            description="keyword description",
            content="keyword content",
            keyword="keyword",
            images=[{"alt": "alt1"}, {"alt": "alt2"}],
        )
        assert score.images == 100

    def test_calculate_seo_score_images_missing_alt(self):
        svc = SEOService()
        score = svc.calculate_seo_score(
            title="keyword title",
            description="keyword description",
            content="keyword content",
            keyword="keyword",
            images=[{"alt": "alt1"}, {"alt": ""}],
        )
        assert score.images < 100

    def test_calculate_seo_score_with_links(self):
        svc = SEOService()
        score = svc.calculate_seo_score(
            title="keyword title",
            description="keyword description",
            content="keyword content",
            keyword="keyword",
            links=["/internal1", "/internal2", "https://external.com"],
        )
        assert score.links == 100

    def test_generate_all_schemas_product(self):
        svc = SEOService()
        data = {
            "product": {"name": "X", "price": "10"},
            "faqs": [{"question": "Q", "answer": "A"}],
            "breadcrumbs": [{"name": "Home", "url": "/"}],
            "website": {"name": "Site", "url": "https://example.com"},
        }
        schemas = svc.generate_all_schemas("product", data)
        assert len(schemas) == 4
        types = {s.schema_type for s in schemas}
        assert "Product" in types
        assert "FAQPage" in types
        assert "BreadcrumbList" in types
        assert "WebSite" in types

    def test_generate_all_schemas_article(self):
        svc = SEOService()
        data = {
            "article": {"title": "T"},
            "breadcrumbs": [{"name": "Home", "url": "/"}],
        }
        schemas = svc.generate_all_schemas("article", data)
        assert len(schemas) == 2
        types = {s.schema_type for s in schemas}
        assert "Article" in types
        assert "BreadcrumbList" in types

    def test_generate_all_schemas_about(self):
        svc = SEOService()
        data = {"organization": {"name": "Org"}}
        schemas = svc.generate_all_schemas("about", data)
        assert len(schemas) == 1
        assert schemas[0].schema_type == "Organization"

    def test_generate_all_schemas_contact(self):
        svc = SEOService()
        data = {"local_business": {"name": "Shop"}}
        schemas = svc.generate_all_schemas("contact", data)
        assert len(schemas) == 1
        assert schemas[0].schema_type == "LocalBusiness"

    def test_generate_all_schemas_empty(self):
        svc = SEOService()
        schemas = svc.generate_all_schemas("unknown", {})
        assert schemas == []

    def test_generate_seo_report(self):
        svc = SEOService()
        report = svc.generate_seo_report(
            url="https://example.com",
            title="keyword title",
            description="keyword description",
            content="keyword content",
            keyword="keyword",
        )
        assert report["url"] == "https://example.com"
        assert report["keyword"] == "keyword"
        assert "overall_score" in report
        assert "grade" in report
        assert "detailed_scores" in report
        assert "issues" in report
        assert "recommendations" in report
        assert "preview" in report
        assert "google" in report["preview"]

    def test_get_grade_a_plus(self):
        svc = SEOService()
        assert svc._get_grade(95) == "A+"
        assert svc._get_grade(85) == "A"
        assert svc._get_grade(75) == "B"
        assert svc._get_grade(65) == "C"
        assert svc._get_grade(55) == "D"
        assert svc._get_grade(30) == "F"

    def test_get_speed_optimization_tips(self):
        svc = SEOService()
        tips = svc.get_speed_optimization_tips()
        assert isinstance(tips, list)
        assert len(tips) > 0
        assert all(isinstance(t, str) for t in tips)

    def test_global_seo_service_instance(self):
        assert isinstance(seo_service, SEOService)
