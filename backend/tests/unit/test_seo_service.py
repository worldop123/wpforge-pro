"""
SEO服务测试
"""
import pytest
from app.services.seo_service import SEOService, get_seo_service
from app.services.seo_enhanced import SEOEnhancedService, get_seo_enhanced_service


class TestSEOService:
    """SEO服务测试"""

    def test_seo_service_creation(self):
        """测试SEO服务创建"""
        service = SEOService()
        assert service is not None

    def test_generate_title(self):
        """测试生成标题"""
        service = SEOService()
        title = service.generate_title("Test Product", "Products")
        assert isinstance(title, str)
        assert len(title) > 0
        assert "Test Product" in title

    def test_generate_meta_description(self):
        """测试生成Meta描述"""
        service = SEOService()
        description = service.generate_meta_description("This is a test product description.")
        assert isinstance(description, str)
        assert len(description) > 0
        assert len(description) <= 160  # 建议长度

    def test_generate_keywords(self):
        """测试生成关键词"""
        service = SEOService()
        keywords = service.generate_keywords("This is a test product about electronics.")
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert all(isinstance(k, str) for k in keywords)

    def test_generate_slug(self):
        """测试生成Slug"""
        service = SEOService()
        slug = service.generate_slug("Hello World Test")
        assert isinstance(slug, str)
        assert " " not in slug  # 没有空格
        assert slug.islower()  # 全小写

    def test_generate_slug_special_chars(self):
        """测试特殊字符Slug"""
        service = SEOService()
        slug = service.generate_slug("Hello & World! @#$%")
        assert isinstance(slug, str)
        assert "&" not in slug
        assert "!" not in slug

    def test_analyze_seo_score(self):
        """测试分析SEO分数"""
        service = SEOService()
        content = {
            "title": "Test Product - Best Quality",
            "description": "This is a test product with high quality and great features.",
            "content": "This is the full product description with lots of details.",
            "keywords": ["test", "product", "quality"],
        }
        score = service.analyze_seo_score(content)
        assert isinstance(score, dict)
        assert "total" in score
        assert 0 <= score["total"] <= 100

    def test_analyze_keyword_density(self):
        """测试分析关键词密度"""
        service = SEOService()
        content = "test test test product product quality"
        density = service.analyze_keyword_density(content, "test")
        assert isinstance(density, float)
        assert 0 <= density <= 100

    def test_generate_lsi_keywords(self):
        """测试生成LSI关键词"""
        service = SEOService()
        lsi = service.generate_lsi_keywords("smartphone", "electronics")
        assert isinstance(lsi, list)
        assert len(lsi) > 0

    def test_generate_breadcrumb(self):
        """测试生成面包屑"""
        service = SEOService()
        breadcrumb = service.generate_breadcrumb(["Home", "Products", "Test Product"])
        assert isinstance(breadcrumb, list)
        assert len(breadcrumb) == 3
        assert breadcrumb[0]["name"] == "Home"

    def test_generate_schema_article(self):
        """测试生成Article Schema"""
        service = SEOService()
        schema = service.generate_schema("article", {
            "title": "Test Article",
            "author": "John Doe",
            "date_published": "2024-01-01",
        })
        assert isinstance(schema, dict)
        assert schema["@type"] == "Article"
        assert "headline" in schema

    def test_generate_schema_product(self):
        """测试生成Product Schema"""
        service = SEOService()
        schema = service.generate_schema("product", {
            "name": "Test Product",
            "price": "29.99",
            "currency": "USD",
            "image": "https://example.com/product.jpg",
        })
        assert isinstance(schema, dict)
        assert schema["@type"] == "Product"
        assert "name" in schema

    def test_generate_schema_faq(self):
        """测试生成FAQ Schema"""
        service = SEOService()
        faqs = [
            {"question": "What is this?", "answer": "It's a product."},
            {"question": "How much?", "answer": "$29.99"},
        ]
        schema = service.generate_schema("faq", {"faqs": faqs})
        assert isinstance(schema, dict)
        assert schema["@type"] == "FAQPage"
        assert "mainEntity" in schema

    def test_generate_schema_breadcrumb(self):
        """测试生成Breadcrumb Schema"""
        service = SEOService()
        items = [
            {"name": "Home", "url": "https://example.com"},
            {"name": "Products", "url": "https://example.com/products"},
        ]
        schema = service.generate_schema("breadcrumb", {"items": items})
        assert isinstance(schema, dict)
        assert schema["@type"] == "BreadcrumbList"
        assert "itemListElement" in schema

    def test_generate_schema_review(self):
        """测试生成Review Schema"""
        service = SEOService()
        schema = service.generate_schema("review", {
            "item_name": "Test Product",
            "rating": 4.5,
            "review_text": "Great product!",
            "author": "John",
        })
        assert isinstance(schema, dict)
        assert schema["@type"] == "Review"

    def test_generate_open_graph(self):
        """测试生成Open Graph标签"""
        service = SEOService()
        og = service.generate_open_graph({
            "title": "Test Page",
            "description": "Test description",
            "image": "https://example.com/image.jpg",
            "url": "https://example.com",
            "type": "website",
        })
        assert isinstance(og, dict)
        assert "og:title" in og
        assert "og:description" in og
        assert "og:image" in og

    def test_generate_twitter_cards(self):
        """测试生成Twitter Cards标签"""
        service = SEOService()
        tc = service.generate_twitter_cards({
            "title": "Test Page",
            "description": "Test description",
            "image": "https://example.com/image.jpg",
        })
        assert isinstance(tc, dict)
        assert "twitter:card" in tc
        assert "twitter:title" in tc

    def test_generate_canonical_url(self):
        """测试生成Canonical URL"""
        service = SEOService()
        canonical = service.generate_canonical_url("https://example.com/product/test")
        assert isinstance(canonical, str)
        assert canonical.startswith("http")

    def test_optimize_heading_structure(self):
        """测试优化标题结构"""
        service = SEOService()
        headings = [
            {"level": 1, "text": "Main Title"},
            {"level": 2, "text": "Section 1"},
            {"level": 2, "text": "Section 2"},
        ]
        optimized = service.optimize_heading_structure(headings)
        assert isinstance(optimized, list)
        assert len(optimized) > 0

    def test_generate_internal_links(self):
        """测试生成内部链接"""
        service = SEOService()
        content = "This is a test product with great features."
        links = service.generate_internal_links(content, ["product", "features"])
        assert isinstance(links, list)
        assert len(links) >= 0

    def test_get_instance(self):
        """测试单例模式"""
        s1 = get_seo_service()
        s2 = get_seo_service()
        assert s1 is s2


class TestSEOEnhancedService:
    """SEO增强服务测试"""

    def test_enhanced_service_creation(self):
        """测试增强服务创建"""
        service = SEOEnhancedService()
        assert service is not None

    def test_comprehensive_seo_audit(self):
        """测试综合SEO审计"""
        service = SEOEnhancedService()
        content = {
            "title": "Test Product",
            "description": "Product description",
            "content": "Full content here",
            "images": [{"src": "test.jpg", "alt": ""}],
            "headings": [{"level": 1, "text": "Title"}],
            "url": "https://example.com/test-product",
        }
        audit = service.comprehensive_seo_audit(content)
        assert isinstance(audit, dict)
        assert "score" in audit
        assert "issues" in audit
        assert "recommendations" in audit

    def test_analyze_page_speed_factors(self):
        """测试分析页面速度因素"""
        service = SEOEnhancedService()
        factors = service.analyze_page_speed_factors({
            "image_count": 10,
            "script_count": 5,
            "css_count": 3,
            "page_size": 1024,
        })
        assert isinstance(factors, dict)
        assert "score" in factors
        assert "issues" in factors

    def test_generate_seo_report(self):
        """测试生成SEO报告"""
        service = SEOEnhancedService()
        report = service.generate_seo_report({
            "url": "https://example.com",
            "title": "Test",
            "description": "Test",
        })
        assert isinstance(report, dict)
        assert "overall_score" in report
        assert "categories" in report

    def test_check_technical_seo(self):
        """测试检查技术SEO"""
        service = SEOEnhancedService()
        result = service.check_technical_seo({
            "has_ssl": True,
            "has_sitemap": True,
            "has_robots_txt": True,
            "page_speed": 90,
        })
        assert isinstance(result, dict)
        assert "score" in result
        assert "passed" in result

    def test_optimize_content(self):
        """测试优化内容"""
        service = SEOEnhancedService()
        content = "This is a test product."
        keyword = "test product"
        optimized = service.optimize_content(content, keyword)
        assert isinstance(optimized, str)
        assert len(optimized) > 0

    def test_get_instance(self):
        """测试单例模式"""
        s1 = get_seo_enhanced_service()
        s2 = get_seo_enhanced_service()
        assert s1 is s2
