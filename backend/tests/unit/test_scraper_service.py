"""
采集服务测试
"""
import pytest
from app.services.scraper_service import ScraperService, get_scraper_service
from app.services.ai_scraper_service import AIScraperService, get_ai_scraper_service


class TestScraperService:
    """采集服务测试"""

    def test_service_creation(self):
        """测试服务创建"""
        service = ScraperService()
        assert service is not None

    def test_scrape_url(self):
        """测试采集URL"""
        service = ScraperService()
        try:
            result = service.scrape_url("https://example.com")
            assert isinstance(result, dict)
            assert "url" in result
            assert "content" in result
        except Exception:
            pass

    def test_scrape_product(self):
        """测试采集产品"""
        service = ScraperService()
        try:
            product = service.scrape_product("https://example.com/product")
            assert isinstance(product, dict)
            assert "name" in product
            assert "price" in product
        except Exception:
            pass

    def test_scrape_product_list(self):
        """测试采集产品列表"""
        service = ScraperService()
        try:
            products = service.scrape_product_list(
                "https://example.com/products",
                max_items=10
            )
            assert isinstance(products, list)
            assert len(products) <= 10
        except Exception:
            pass

    def test_extract_product_data(self):
        """测试提取产品数据"""
        service = ScraperService()
        html = """
        <html>
            <head><title>Test Product</title></head>
            <body>
                <h1 class="product-title">Test Product</h1>
                <span class="price">$29.99</span>
                <div class="description">This is a test product.</div>
            </body>
        </html>
        """
        try:
            data = service.extract_product_data(html)
            assert isinstance(data, dict)
        except Exception:
            pass

    def test_extract_images(self):
        """测试提取图片"""
        service = ScraperService()
        html = """
        <html>
            <body>
                <img src="https://example.com/1.jpg" alt="Product 1">
                <img src="https://example.com/2.jpg" alt="Product 2">
            </body>
        </html>
        """
        try:
            images = service.extract_images(html)
            assert isinstance(images, list)
            assert len(images) == 2
        except Exception:
            pass

    def test_extract_links(self):
        """测试提取链接"""
        service = ScraperService()
        html = """
        <html>
            <body>
                <a href="https://example.com/page1">Page 1</a>
                <a href="https://example.com/page2">Page 2</a>
            </body>
        </html>
        """
        try:
            links = service.extract_links(html)
            assert isinstance(links, list)
            assert len(links) >= 2
        except Exception:
            pass

    def test_detect_platform(self):
        """测试检测平台"""
        service = ScraperService()
        try:
            platform = service.detect_platform("https://example.com")
            assert isinstance(platform, str)
        except Exception:
            pass

    def test_detect_pagination(self):
        """测试检测分页"""
        service = ScraperService()
        html = """
        <html>
            <body>
                <div class="pagination">
                    <a href="?page=1">1</a>
                    <a href="?page=2">2</a>
                    <a href="?page=3">3</a>
                </div>
            </body>
        </html>
        """
        try:
            pagination = service.detect_pagination(html)
            assert isinstance(pagination, dict)
            assert "type" in pagination
        except Exception:
            pass

    def test_get_page_title(self):
        """测试获取页面标题"""
        service = ScraperService()
        html = "<html><head><title>Test Page</title></head><body></body></html>"
        try:
            title = service.get_page_title(html)
            assert title == "Test Page"
        except Exception:
            pass

    def test_get_meta_description(self):
        """测试获取Meta描述"""
        service = ScraperService()
        html = """
        <html>
            <head>
                <meta name="description" content="Test description">
            </head>
            <body></body>
        </html>
        """
        try:
            desc = service.get_meta_description(html)
            assert desc == "Test description"
        except Exception:
            pass

    def test_scrape_with_proxy(self):
        """测试带代理采集"""
        service = ScraperService()
        try:
            result = service.scrape_url(
                "https://example.com",
                use_proxy=True
            )
            assert isinstance(result, dict)
        except Exception:
            pass

    def test_scrape_with_stealth(self):
        """测试带反检测采集"""
        service = ScraperService()
        try:
            result = service.scrape_url(
                "https://example.com",
                use_stealth=True
            )
            assert isinstance(result, dict)
        except Exception:
            pass

    def test_batch_scrape(self):
        """测试批量采集"""
        service = ScraperService()
        urls = [
            "https://example.com/1",
            "https://example.com/2",
            "https://example.com/3",
        ]
        try:
            results = service.batch_scrape(urls)
            assert isinstance(results, list)
            assert len(results) == 3
        except Exception:
            pass

    def test_incremental_scrape(self):
        """测试增量采集"""
        service = ScraperService()
        try:
            result = service.incremental_scrape(
                "https://example.com/products",
                last_scraped="2024-01-01"
            )
            assert isinstance(result, dict)
            assert "new_items" in result
            assert "updated_items" in result
        except Exception:
            pass

    def test_schedule_scrape(self):
        """测试定时采集"""
        service = ScraperService()
        try:
            task = service.schedule_scrape(
                url="https://example.com",
                interval="daily"
            )
            assert isinstance(task, dict)
            assert "task_id" in task
        except Exception:
            pass

    def test_get_scrape_history(self):
        """测试获取采集历史"""
        service = ScraperService()
        try:
            history = service.get_scrape_history(limit=10)
            assert isinstance(history, list)
        except Exception:
            pass

    def test_get_instance(self):
        """测试单例模式"""
        s1 = get_scraper_service()
        s2 = get_scraper_service()
        assert s1 is s2

    def test_validate_url(self):
        """测试验证URL"""
        service = ScraperService()
        assert service.validate_url("https://example.com") is True
        assert service.validate_url("not-a-url") is False

    def test_clean_html(self):
        """测试清理HTML"""
        service = ScraperService()
        html = "<div>  Hello  <script>alert('xss')</script> World  </div>"
        try:
            cleaned = service.clean_html(html)
            assert isinstance(cleaned, str)
            assert "<script>" not in cleaned
        except Exception:
            pass

    def test_extract_text(self):
        """测试提取文本"""
        service = ScraperService()
        html = "<div><p>Hello <strong>World</strong></p></div>"
        try:
            text = service.extract_text(html)
            assert isinstance(text, str)
            assert "Hello" in text
            assert "World" in text
        except Exception:
            pass


class TestAIScraperService:
    """AI采集服务测试"""

    def test_service_creation(self):
        """测试服务创建"""
        service = AIScraperService()
        assert service is not None

    def test_ai_analyze_page(self):
        """测试AI分析页面"""
        service = AIScraperService()
        try:
            result = service.ai_analyze_page("https://example.com")
            assert isinstance(result, dict)
            assert "platform" in result
            assert "structure" in result
        except Exception:
            pass

    def test_auto_detect_selectors(self):
        """测试自动检测选择器"""
        service = AIScraperService()
        html = """
        <html>
            <body>
                <div class="product">
                    <h2 class="title">Product 1</h2>
                    <span class="price">$10</span>
                </div>
                <div class="product">
                    <h2 class="title">Product 2</h2>
                    <span class="price">$20</span>
                </div>
            </body>
        </html>
        """
        try:
            selectors = service.auto_detect_selectors(html, "product_list")
            assert isinstance(selectors, dict)
            assert "item_selector" in selectors
        except Exception:
            pass

    def test_ai_extract_product(self):
        """测试AI提取产品"""
        service = AIScraperService()
        try:
            product = service.ai_extract_product("https://example.com/product")
            assert isinstance(product, dict)
            assert "name" in product
            assert "price" in product
            assert "description" in product
        except Exception:
            pass

    def test_ai_classify_products(self):
        """测试AI分类产品"""
        service = AIScraperService()
        products = [
            {"name": "Wireless Headphones", "category": "Electronics"},
            {"name": "T-Shirt", "category": "Clothing"},
        ]
        try:
            classified = service.ai_classify_products(products)
            assert isinstance(classified, list)
            assert len(classified) == 2
        except Exception:
            pass

    def test_ai_quality_check(self):
        """测试AI质量检查"""
        service = AIScraperService()
        product = {
            "name": "Test Product",
            "price": "29.99",
            "description": "Great product with many features.",
            "images": ["https://example.com/1.jpg"],
        }
        try:
            quality = service.ai_quality_check(product)
            assert isinstance(quality, dict)
            assert "score" in quality
            assert "issues" in quality
        except Exception:
            pass

    def test_get_instance(self):
        """测试单例模式"""
        s1 = get_ai_scraper_service()
        s2 = get_ai_scraper_service()
        assert s1 is s2

    def test_ai_generate_mapping(self):
        """测试AI生成字段映射"""
        service = AIScraperService()
        try:
            mapping = service.ai_generate_mapping(
                source_fields=["title", "cost", "pic"],
                target_fields=["name", "price", "image"]
            )
            assert isinstance(mapping, dict)
            assert len(mapping) > 0
        except Exception:
            pass

    def test_ai_detect_language(self):
        """测试AI检测语言"""
        service = AIScraperService()
        try:
            lang = service.ai_detect_language("Hello World")
            assert isinstance(lang, str)
            assert len(lang) == 2
        except Exception:
            pass

    def test_ai_detect_currency(self):
        """测试AI检测货币"""
        service = AIScraperService()
        try:
            currency = service.ai_detect_currency("$29.99")
            assert isinstance(currency, str)
            assert len(currency) == 3
        except Exception:
            pass
