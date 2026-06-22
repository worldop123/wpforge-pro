"""
采集服务测试 - 测试 ProductScraper、SelectorGenerator、配置数据类
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from app.services.scraper_service import (
    SelectorConfig,
    ScrapingConfig,
    ScrapedProduct,
    ProductScraper,
    SelectorGenerator,
    WOOCOMMERCE_SELECTORS,
    create_woocommerce_scraper,
)


class TestSelectorConfig:
    """SelectorConfig 数据类测试"""

    def test_defaults(self):
        cfg = SelectorConfig(name="title", selector=".title")
        assert cfg.name == "title"
        assert cfg.selector == ".title"
        assert cfg.attribute is None
        assert cfg.multiple is False
        assert cfg.required is False
        assert cfg.default is None
        assert cfg.regex is None
        assert cfg.transform is None

    def test_with_all_fields(self):
        cfg = SelectorConfig(
            name="price",
            selector=".price",
            attribute="data-amount",
            multiple=True,
            required=True,
            default="0",
            regex=r"(\d+)",
            transform="float",
        )
        assert cfg.attribute == "data-amount"
        assert cfg.multiple is True
        assert cfg.required is True
        assert cfg.default == "0"
        assert cfg.regex == r"(\d+)"
        assert cfg.transform == "float"


class TestScrapingConfig:
    """ScrapingConfig 数据类测试"""

    def test_defaults(self):
        cfg = ScrapingConfig(start_url="https://example.com")
        assert cfg.start_url == "https://example.com"
        assert cfg.max_pages == 10
        assert cfg.max_products == 100
        assert cfg.follow_pagination is True
        assert cfg.delay_between_requests == 2.0
        assert cfg.use_stealth is True
        assert cfg.use_proxy is True
        assert cfg.headless is True
        assert cfg.timeout == 30000
        assert cfg.max_retries == 3

    def test_custom_values(self):
        cfg = ScrapingConfig(
            start_url="https://example.com",
            max_pages=5,
            max_products=50,
            use_proxy=False,
            use_stealth=False,
        )
        assert cfg.max_pages == 5
        assert cfg.max_products == 50
        assert cfg.use_proxy is False
        assert cfg.use_stealth is False


class TestScrapedProduct:
    """ScrapedProduct 数据类测试"""

    def test_defaults(self):
        product = ScrapedProduct(url="https://example.com/p1")
        assert product.url == "https://example.com/p1"
        assert product.title is None
        assert product.in_stock is True
        assert product.categories == []
        assert product.tags == []
        assert product.images == []
        assert product.attributes == []
        assert product.variations == []
        assert product.meta_data == {}
        assert product.is_variable is False

    def test_with_values(self):
        product = ScrapedProduct(
            url="https://example.com/p1",
            title="Test Product",
            price=99.99,
            currency="USD",
            images=["https://example.com/1.jpg"],
            categories=["Electronics"],
        )
        assert product.title == "Test Product"
        assert product.price == 99.99
        assert product.currency == "USD"
        assert len(product.images) == 1
        assert product.categories == ["Electronics"]


class TestProductScraperParsePrice:
    """ProductScraper._parse_price 测试（无需浏览器）"""

    def setup_method(self):
        self.config = ScrapingConfig(start_url="https://example.com", use_proxy=False, use_stealth=False)
        self.scraper = ProductScraper(self.config)

    def test_parse_price_usd(self):
        price, currency = self.scraper._parse_price("$29.99")
        assert price == 29.99
        assert currency == "USD"

    def test_parse_price_eur(self):
        price, currency = self.scraper._parse_price("€19,90")
        assert price == 19.90
        assert currency == "EUR"

    def test_parse_price_gbp(self):
        price, currency = self.scraper._parse_price("£15.50")
        assert price == 15.50
        assert currency == "GBP"

    def test_parse_price_cny(self):
        price, currency = self.scraper._parse_price("¥199")
        assert price == 199.0
        assert currency == "JPY"

    def test_parse_price_none(self):
        price, currency = self.scraper._parse_price(None)
        assert price is None
        assert currency is None

    def test_parse_price_empty(self):
        price, currency = self.scraper._parse_price("")
        assert price is None

    def test_parse_price_no_digits(self):
        price, currency = self.scraper._parse_price("Free")
        assert price is None

    def test_parse_price_with_thousands(self):
        price, currency = self.scraper._parse_price("$1,299.99")
        assert price == 1299.99
        assert currency == "USD"

    def test_parse_price_european_format(self):
        # 欧洲格式：1.299,99
        price, currency = self.scraper._parse_price("€1.299,99")
        assert price == 1299.99
        assert currency == "EUR"

    def test_parse_srcset(self):
        srcset = "img1.jpg 300w, img2.jpg 600w, img3.jpg 900w"
        urls = self.scraper._parse_srcset(srcset)
        assert len(urls) == 3
        assert urls[0] == "img1.jpg"
        assert urls[-1] == "img3.jpg"

    def test_parse_srcset_single(self):
        urls = self.scraper._parse_srcset("img.jpg")
        assert urls == ["img.jpg"]


class TestProductScraperInit:
    """ProductScraper 初始化测试"""

    def test_init(self):
        config = ScrapingConfig(start_url="https://example.com")
        scraper = ProductScraper(config)
        assert scraper.config is config
        assert scraper.browser is None
        assert scraper.page is None
        assert scraper.scraped_urls == set()
        assert scraper.scraped_products == []

    def test_scraped_urls_tracking(self):
        config = ScrapingConfig(start_url="https://example.com")
        scraper = ProductScraper(config)
        scraper.scraped_urls.add("https://example.com/p1")
        assert "https://example.com/p1" in scraper.scraped_urls
        assert len(scraper.scraped_urls) == 1


class TestSelectorGenerator:
    """SelectorGenerator 测试"""

    def test_generate_with_id(self):
        gen = SelectorGenerator()
        selector = gen.generate_selector_from_element({
            "tag": "div",
            "id": "product-title",
            "classes": ["title"],
        })
        assert selector == "div#product-title"

    def test_generate_with_classes(self):
        gen = SelectorGenerator()
        selector = gen.generate_selector_from_element({
            "tag": "h2",
            "classes": ["product", "title", "main"],
        })
        assert selector.startswith("h2")
        assert ".product" in selector
        assert ".title" in selector

    def test_generate_skips_hover_active_classes(self):
        gen = SelectorGenerator()
        selector = gen.generate_selector_from_element({
            "tag": "a",
            "classes": ["link", "hover-state", "active-state"],
        })
        assert ".hover-state" not in selector
        assert ".active-state" not in selector
        assert ".link" in selector

    def test_generate_with_attributes(self):
        gen = SelectorGenerator()
        selector = gen.generate_selector_from_element({
            "tag": "div",
            "classes": ["product"],
            "attributes": {"data-product-id": "123"},
        })
        assert '[data-product-id="123"]' in selector

    def test_generate_with_nth_child(self):
        gen = SelectorGenerator()
        selector = gen.generate_selector_from_element({
            "tag": "li",
            "nth_child": 3,
        })
        assert ":nth-child(3)" in selector

    def test_generate_empty_element(self):
        gen = SelectorGenerator()
        selector = gen.generate_selector_from_element({})
        assert selector == ""

    def test_generate_hierarchy_returns_shortest(self):
        gen = SelectorGenerator()
        path = [
            {"tag": "div", "classes": ["container"]},
            {"tag": "ul", "classes": ["products"]},
            {"tag": "li", "classes": ["item"]},
        ]
        selector = gen.generate_selector_hierarchy(path)
        # 算法从后往前找最短且唯一的，li.item 已 > 3 字符所以直接返回
        assert selector == "li.item"

    def test_generate_hierarchy_joins_when_short(self):
        gen = SelectorGenerator()
        # 用很短的标签让最后选择器 <=3 字符，触发拼接
        path = [
            {"tag": "div", "classes": ["container"]},
            {"tag": "li"},  # "li" 只有 2 字符
        ]
        selector = gen.generate_selector_hierarchy(path)
        # li <=3，所以会拼接 div.container > li
        assert ">" in selector
        assert "li" in selector

    def test_generate_hierarchy_single(self):
        gen = SelectorGenerator()
        path = [{"tag": "div", "id": "main"}]
        selector = gen.generate_selector_hierarchy(path)
        assert selector == "div#main"

    def test_generate_hierarchy_empty(self):
        gen = SelectorGenerator()
        selector = gen.generate_selector_hierarchy([])
        assert selector == ""


class TestWoocommerceSelectors:
    """WOOCOMMERCE_SELECTORS 测试"""

    def test_has_required_selectors(self):
        assert "title" in WOOCOMMERCE_SELECTORS
        assert "price" in WOOCOMMERCE_SELECTORS
        assert "description" in WOOCOMMERCE_SELECTORS
        assert "sku" in WOOCOMMERCE_SELECTORS

    def test_title_is_required(self):
        assert WOOCOMMERCE_SELECTORS["title"].required is True

    def test_categories_is_multiple(self):
        assert WOOCOMMERCE_SELECTORS["categories"].multiple is True

    def test_tags_is_multiple(self):
        assert WOOCOMMERCE_SELECTORS["tags"].multiple is True


class TestCreateWoocommerceScraper:
    """create_woocommerce_scraper 工厂函数测试"""

    def test_creates_scraper(self):
        scraper = create_woocommerce_scraper("https://example.com/shop")
        assert isinstance(scraper, ProductScraper)
        assert scraper.config.start_url == "https://example.com/shop"

    def test_uses_woocommerce_selectors(self):
        scraper = create_woocommerce_scraper("https://example.com/shop")
        assert "title" in scraper.config.product_selectors
        assert scraper.config.product_selectors["title"].selector == ".product_title"

    def test_with_custom_kwargs(self):
        scraper = create_woocommerce_scraper(
            "https://example.com/shop",
            max_pages=5,
            use_proxy=False,
        )
        assert scraper.config.max_pages == 5
        assert scraper.config.use_proxy is False

    def test_has_pagination_selectors(self):
        scraper = create_woocommerce_scraper("https://example.com/shop")
        assert scraper.config.product_link_selector == ".woocommerce-LoopProduct-link"
        assert scraper.config.next_page_selector == ".next.page-numbers"


def _make_async_page(query_selector_result=None, query_selector_all_result=None):
    """构造一个支持 await 的 mock page"""
    page = MagicMock()
    page.query_selector = AsyncMock(return_value=query_selector_result)
    page.query_selector_all = AsyncMock(return_value=query_selector_all_result or [])
    return page


def _make_async_element(inner_text_value=None, attribute_value=None):
    """构造一个支持 await 的 mock element"""
    element = MagicMock()
    element.inner_text = AsyncMock(return_value=inner_text_value)
    element.get_attribute = AsyncMock(return_value=attribute_value)
    return element


class TestProductScraperExtractText:
    """ProductScraper._extract_text 测试（使用 mock page）"""

    @pytest.mark.asyncio
    async def test_extract_text_with_mock(self):
        config = ScrapingConfig(start_url="https://example.com", use_proxy=False, use_stealth=False)
        scraper = ProductScraper(config)
        element = _make_async_element(inner_text_value="  Hello World  ")
        scraper.page = _make_async_page(query_selector_result=element)

        result = await scraper._extract_text(".title")
        assert result == "Hello World"

    @pytest.mark.asyncio
    async def test_extract_text_no_element(self):
        config = ScrapingConfig(start_url="https://example.com", use_proxy=False, use_stealth=False)
        scraper = ProductScraper(config)
        scraper.page = _make_async_page(query_selector_result=None)

        result = await scraper._extract_text(".nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_extract_text_with_attribute(self):
        config = ScrapingConfig(start_url="https://example.com", use_proxy=False, use_stealth=False)
        scraper = ProductScraper(config)
        element = _make_async_element(attribute_value="12345")
        scraper.page = _make_async_page(query_selector_result=element)

        result = await scraper._extract_text(".sku", attribute="data-sku")
        assert result == "12345"

    @pytest.mark.asyncio
    async def test_extract_text_with_regex(self):
        config = ScrapingConfig(start_url="https://example.com", use_proxy=False, use_stealth=False)
        scraper = ProductScraper(config)
        element = _make_async_element(inner_text_value="Price: $29.99")
        scraper.page = _make_async_page(query_selector_result=element)

        result = await scraper._extract_text(".price", regex=r"\$(\d+\.\d+)")
        assert result == "29.99"

    @pytest.mark.asyncio
    async def test_extract_all_with_mock(self):
        config = ScrapingConfig(start_url="https://example.com", use_proxy=False, use_stealth=False)
        scraper = ProductScraper(config)
        elem1 = _make_async_element(inner_text_value="Cat 1")
        elem2 = _make_async_element(inner_text_value="Cat 2")
        scraper.page = _make_async_page(query_selector_all_result=[elem1, elem2])

        results = await scraper._extract_all(".categories a")
        assert results == ["Cat 1", "Cat 2"]

    @pytest.mark.asyncio
    async def test_extract_all_empty(self):
        config = ScrapingConfig(start_url="https://example.com", use_proxy=False, use_stealth=False)
        scraper = ProductScraper(config)
        scraper.page = _make_async_page(query_selector_all_result=[])

        results = await scraper._extract_all(".nonexistent")
        assert results == []
