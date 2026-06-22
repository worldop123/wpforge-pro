"""
采集器高级功能测试 - 变体采集、增量采集、定时采集、整站采集
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime

from app.services.scraper_service import (
    SelectorConfig,
    ScrapingConfig,
    ScrapedProduct,
    ProductScraper,
    WOOCOMMERCE_SELECTORS,
    create_woocommerce_scraper,
    build_celery_beat_schedule,
    parse_cron_expression,
    should_run_now,
    DEFAULT_SCHEDULED_SCRAPES,
)


def _make_async_page(query_selector_result=None, query_selector_all_result=None,
                     evaluate_result=None, content_result="<html></html>",
                     url="https://example.com/product"):
    """构造一个支持 await 的 mock page"""
    page = MagicMock()
    page.url = url
    page.query_selector = AsyncMock(return_value=query_selector_result)
    page.query_selector_all = AsyncMock(return_value=query_selector_all_result or [])
    page.evaluate = AsyncMock(return_value=evaluate_result)
    page.content = AsyncMock(return_value=content_result)
    page.set_default_timeout = MagicMock()
    return page


def _make_async_element(inner_text_value=None, attribute_value=None,
                        query_selector_all_result=None):
    """构造一个支持 await 的 mock element"""
    element = MagicMock()
    element.inner_text = AsyncMock(return_value=inner_text_value)
    element.get_attribute = AsyncMock(return_value=attribute_value)
    element.query_selector_all = AsyncMock(return_value=query_selector_all_result or [])
    return element


def _make_option_elements(values):
    """构造一组 option 元素"""
    options = []
    for v in values:
        opt = MagicMock()
        opt.get_attribute = AsyncMock(return_value=v)
        options.append(opt)
    return options


class TestScrapingConfigAdvanced:
    """ScrapingConfig 高级字段测试"""

    def test_advanced_defaults(self):
        cfg = ScrapingConfig(start_url="https://example.com")
        assert cfg.scrape_variations is True
        assert cfg.incremental is False
        assert cfg.full_site is False
        assert cfg.respect_robots_txt is True
        assert cfg.max_depth == 3
        assert cfg.incremental_hash_field == "raw_html"
        assert cfg.known_hashes == set()
        assert cfg.known_last_modified == {}
        assert cfg.cron_expression is None
        assert cfg.exclude_patterns == []

    def test_advanced_custom(self):
        cfg = ScrapingConfig(
            start_url="https://example.com",
            scrape_variations=False,
            incremental=True,
            full_site=True,
            max_depth=5,
            cron_expression="0 2 * * *",
            exclude_patterns=["/cart", "/checkout"],
            known_hashes={"abc"},
        )
        assert cfg.scrape_variations is False
        assert cfg.incremental is True
        assert cfg.full_site is True
        assert cfg.max_depth == 5
        assert cfg.cron_expression == "0 2 * * *"
        assert "/cart" in cfg.exclude_patterns
        assert "abc" in cfg.known_hashes


class TestContentHash:
    """增量采集：内容 hash 计算"""

    def test_compute_content_hash_uses_raw_html(self):
        cfg = ScrapingConfig(
            start_url="https://example.com",
            use_proxy=False,
            use_stealth=False,
            incremental=True,
        )
        scraper = ProductScraper(cfg)
        product = ScrapedProduct(url="https://example.com/p", raw_html="<html>hello</html>")
        h1 = scraper._compute_content_hash(product)
        h2 = scraper._compute_content_hash(product)
        assert h1 == h2
        assert len(h1) == 32  # md5 hex

    def test_compute_content_hash_differs_for_different_content(self):
        cfg = ScrapingConfig(start_url="https://example.com", use_proxy=False, use_stealth=False)
        scraper = ProductScraper(cfg)
        p1 = ScrapedProduct(url="u1", raw_html="<html>a</html>")
        p2 = ScrapedProduct(url="u2", raw_html="<html>b</html>")
        assert scraper._compute_content_hash(p1) != scraper._compute_content_hash(p2)

    def test_compute_content_hash_falls_back_to_empty(self):
        cfg = ScrapingConfig(start_url="https://example.com", use_proxy=False, use_stealth=False)
        scraper = ProductScraper(cfg)
        product = ScrapedProduct(url="u1")
        # raw_html is None
        h = scraper._compute_content_hash(product)
        assert isinstance(h, str)
        assert len(h) == 32

    def test_compute_content_hash_custom_field(self):
        cfg = ScrapingConfig(
            start_url="https://example.com",
            use_proxy=False,
            use_stealth=False,
            incremental_hash_field="title",
        )
        scraper = ProductScraper(cfg)
        product = ScrapedProduct(url="u1", title="Hello", raw_html="<x/>")
        h = scraper._compute_content_hash(product)
        assert isinstance(h, str)
        assert len(h) == 32


class TestIncrementalScraping:
    """增量采集：scrape_product_page 跳过未变化页面"""

    @pytest.mark.asyncio
    async def test_incremental_skips_unchanged_content(self):
        cfg = ScrapingConfig(
            start_url="https://example.com",
            use_proxy=False,
            use_stealth=False,
            incremental=True,
            scrape_variations=False,
            download_images=False,
        )
        # 预先放入 hash，模拟已采集过
        product = ScrapedProduct(url="https://example.com/p", raw_html="<html>same</html>")
        cfg.known_hashes.add(ProductScraper(cfg)._compute_content_hash(product))

        scraper = ProductScraper(cfg)
        scraper.page = _make_async_page(content_result="<html>same</html>")
        # _goto 返回 True
        with patch.object(scraper, "_goto", AsyncMock(return_value=True)):
            result = await scraper.scrape_product_page("https://example.com/p")

        assert result is not None
        assert result.meta_data.get("skipped_incremental") is True

    @pytest.mark.asyncio
    async def test_incremental_processes_new_content(self):
        cfg = ScrapingConfig(
            start_url="https://example.com",
            use_proxy=False,
            use_stealth=False,
            incremental=True,
            scrape_variations=False,
            download_images=False,
        )
        scraper = ProductScraper(cfg)
        scraper.page = _make_async_page(content_result="<html>brand new</html>")
        with patch.object(scraper, "_goto", AsyncMock(return_value=True)):
            result = await scraper.scrape_product_page("https://example.com/p")

        assert result is not None
        assert result.meta_data.get("skipped_incremental") is None
        assert "content_hash" in result.meta_data
        # hash 应该被加入到 known_hashes
        assert result.meta_data["content_hash"] in cfg.known_hashes


class TestVariationScraping:
    """变体采集测试"""

    @pytest.mark.asyncio
    async def test_extract_variations_from_json(self):
        cfg = ScrapingConfig(start_url="https://example.com", use_proxy=False, use_stealth=False)
        scraper = ProductScraper(cfg)
        json_data = '[{"variation_id": 1, "attributes": [{"attribute": "color", "value": "red"}], "display_price": "10.0", "display_regular_price": "12.0", "sku": "RED1", "is_in_stock": true, "image": {"src": "img.jpg"}}]'
        scraper.page = _make_async_page(evaluate_result=json_data)
        with patch.object(scraper, "_goto", AsyncMock(return_value=True)):
            variations = await scraper._extract_variations_from_json()
        assert len(variations) == 1
        assert variations[0]["variation_id"] == 1
        assert variations[0]["attributes"]["color"] == "red"
        assert variations[0]["price"] == "10.0"
        assert variations[0]["sku"] == "RED1"
        assert variations[0]["image"] == "img.jpg"

    @pytest.mark.asyncio
    async def test_extract_variations_from_json_empty(self):
        cfg = ScrapingConfig(start_url="https://example.com", use_proxy=False, use_stealth=False)
        scraper = ProductScraper(cfg)
        scraper.page = _make_async_page(evaluate_result=None)
        variations = await scraper._extract_variations_from_json()
        assert variations == []

    @pytest.mark.asyncio
    async def test_extract_variations_from_json_invalid(self):
        cfg = ScrapingConfig(start_url="https://example.com", use_proxy=False, use_stealth=False)
        scraper = ProductScraper(cfg)
        scraper.page = _make_async_page(evaluate_result="not json")
        variations = await scraper._extract_variations_from_json()
        assert variations == []

    @pytest.mark.asyncio
    async def test_extract_variations_from_dom(self):
        cfg = ScrapingConfig(start_url="https://example.com", use_proxy=False, use_stealth=False)
        scraper = ProductScraper(cfg)
        # 构造 select 元素
        select_elem = _make_async_element(
            attribute_value="attribute_color",
            query_selector_all_result=_make_option_elements(["red", "blue"]),
        )
        scraper.page = _make_async_page(query_selector_all_result=[select_elem])
        variations = await scraper._extract_variations_from_dom()
        assert len(variations) == 1
        assert "attribute_color" in variations[0]["attributes"]
        assert variations[0]["attributes"]["attribute_color"] == ["red", "blue"]

    @pytest.mark.asyncio
    async def test_extract_variations_from_dom_empty(self):
        cfg = ScrapingConfig(start_url="https://example.com", use_proxy=False, use_stealth=False)
        scraper = ProductScraper(cfg)
        scraper.page = _make_async_page(query_selector_all_result=[])
        variations = await scraper._extract_variations_from_dom()
        assert variations == []

    @pytest.mark.asyncio
    async def test_scrape_product_page_extracts_variations(self):
        cfg = ScrapingConfig(
            start_url="https://example.com",
            use_proxy=False,
            use_stealth=False,
            scrape_variations=True,
            download_images=False,
            incremental=False,
        )
        scraper = ProductScraper(cfg)
        scraper.page = _make_async_page(content_result="<html></html>")
        # mock _extract_variations 返回非空
        with patch.object(scraper, "_goto", AsyncMock(return_value=True)), \
             patch.object(scraper, "_extract_variations", AsyncMock(return_value=[{"attributes": {"color": "red"}}])):
            result = await scraper.scrape_product_page("https://example.com/p")
        assert result is not None
        assert result.is_variable is True
        assert len(result.variations) == 1

    @pytest.mark.asyncio
    async def test_scrape_product_page_no_variations_when_disabled(self):
        cfg = ScrapingConfig(
            start_url="https://example.com",
            use_proxy=False,
            use_stealth=False,
            scrape_variations=False,
            download_images=False,
            incremental=False,
        )
        scraper = ProductScraper(cfg)
        scraper.page = _make_async_page(content_result="<html></html>")
        with patch.object(scraper, "_goto", AsyncMock(return_value=True)):
            result = await scraper.scrape_product_page("https://example.com/p")
        assert result is not None
        assert result.is_variable is False
        assert result.variations == []


class TestFullSiteScraping:
    """整站采集测试"""

    def test_get_domain(self):
        cfg = ScrapingConfig(start_url="https://example.com", use_proxy=False, use_stealth=False)
        scraper = ProductScraper(cfg)
        assert scraper._get_domain("https://example.com/path") == "example.com"
        assert scraper._get_domain("https://sub.example.com") == "sub.example.com"
        assert scraper._get_domain("not a url") == ""

    def test_is_excluded_substring(self):
        cfg = ScrapingConfig(
            start_url="https://example.com",
            use_proxy=False,
            use_stealth=False,
            exclude_patterns=["/cart", "/checkout"],
        )
        scraper = ProductScraper(cfg)
        assert scraper._is_excluded("https://example.com/cart") is True
        assert scraper._is_excluded("https://example.com/checkout") is True
        assert scraper._is_excluded("https://example.com/product") is False

    def test_is_excluded_regex(self):
        cfg = ScrapingConfig(
            start_url="https://example.com",
            use_proxy=False,
            use_stealth=False,
            exclude_patterns=[r"/\d+/private"],
        )
        scraper = ProductScraper(cfg)
        assert scraper._is_excluded("https://example.com/123/private") is True
        assert scraper._is_excluded("https://example.com/product") is False

    @pytest.mark.asyncio
    async def test_is_product_page_with_selectors(self):
        cfg = ScrapingConfig(
            start_url="https://example.com",
            use_proxy=False,
            use_stealth=False,
            product_selectors=WOOCOMMERCE_SELECTORS,
        )
        scraper = ProductScraper(cfg)
        # 第一个 query_selector 返回非空
        elem = _make_async_element()
        scraper.page = _make_async_page(query_selector_result=elem)
        assert await scraper._is_product_page() is True

    @pytest.mark.asyncio
    async def test_is_product_page_without_match(self):
        cfg = ScrapingConfig(
            start_url="https://example.com",
            use_proxy=False,
            use_stealth=False,
            product_selectors=WOOCOMMERCE_SELECTORS,
        )
        scraper = ProductScraper(cfg)
        scraper.page = _make_async_page(query_selector_result=None)
        assert await scraper._is_product_page() is False

    @pytest.mark.asyncio
    async def test_extract_page_links_filters_external(self):
        cfg = ScrapingConfig(start_url="https://example.com", use_proxy=False, use_stealth=False)
        scraper = ProductScraper(cfg)
        # 构造 anchors
        a1 = MagicMock()
        a1.get_attribute = AsyncMock(return_value="/product/1")
        a2 = MagicMock()
        a2.get_attribute = AsyncMock(return_value="https://other.com/x")
        a3 = MagicMock()
        a3.get_attribute = AsyncMock(return_value="#anchor")
        a4 = MagicMock()
        a4.get_attribute = AsyncMock(return_value="javascript:void(0)")
        a5 = MagicMock()
        a5.get_attribute = AsyncMock(return_value="mailto:a@b.com")
        a6 = MagicMock()
        a6.get_attribute = AsyncMock(return_value="https://example.com/page2")
        scraper.page = _make_async_page(query_selector_all_result=[a1, a2, a3, a4, a5, a6])
        links = await scraper._extract_page_links("example.com")
        # 应该只保留同域的链接
        assert "https://example.com/product/1" in links
        assert "https://example.com/page2" in links
        assert all("other.com" not in l for l in links)
        assert all(not l.startswith("#") for l in links)
        assert all(not l.startswith("javascript") for l in links)
        assert all(not l.startswith("mailto") for l in links)

    @pytest.mark.asyncio
    async def test_scrape_full_site_falls_back_when_disabled(self):
        cfg = ScrapingConfig(
            start_url="https://example.com",
            use_proxy=False,
            use_stealth=False,
            full_site=False,
        )
        scraper = ProductScraper(cfg)
        # mock scrape 方法返回空列表
        with patch.object(scraper, "scrape", AsyncMock(return_value=[])):
            result = await scraper.scrape_full_site()
        assert result == []

    @pytest.mark.asyncio
    async def test_scrape_full_site_discovers_products(self):
        cfg = ScrapingConfig(
            start_url="https://example.com",
            use_proxy=False,
            use_stealth=False,
            full_site=True,
            max_depth=1,
            max_products=2,
            download_images=False,
            scrape_variations=False,
            incremental=False,
        )
        scraper = ProductScraper(cfg)

        # 模拟 _goto 返回 True
        async def fake_goto(url, retries=0):
            return True
        scraper._goto = fake_goto

        # 第一次访问是产品页，第二次不是
        call_count = {"n": 0}

        async def fake_is_product_page():
            call_count["n"] += 1
            return call_count["n"] == 1  # 只有第一次是产品页

        scraper._is_product_page = fake_is_product_page

        async def fake_extract_page_links(base_domain):
            return ["https://example.com/page2"]

        scraper._extract_page_links = fake_extract_page_links

        async def fake_scrape_product_page(url):
            return ScrapedProduct(url=url, title="P")

        scraper.scrape_product_page = fake_scrape_product_page

        # mock _init_browser 和 _close_browser
        scraper._init_browser = AsyncMock()
        scraper._close_browser = AsyncMock()

        result = await scraper.scrape_full_site()
        assert len(result) == 1
        assert result[0].title == "P"


class TestScheduledScraping:
    """定时采集调度测试"""

    def test_default_scheduled_scrapes(self):
        assert len(DEFAULT_SCHEDULED_SCRAPES) >= 2
        names = [s["name"] for s in DEFAULT_SCHEDULED_SCRAPES]
        assert "daily-product-scrape" in names
        assert "weekly-full-site-scrape" in names

    def test_build_celery_beat_schedule_default(self):
        schedule = build_celery_beat_schedule()
        assert "daily-product-scrape" in schedule
        assert "weekly-full-site-scrape" in schedule
        assert schedule["daily-product-scrape"]["task"] == "app.tasks.scraping_tasks.scrape_products_task"
        # schedule 字段应该是 crontab 对象
        from celery.schedules import crontab
        assert isinstance(schedule["daily-product-scrape"]["schedule"], crontab)

    def test_build_celery_beat_schedule_custom(self):
        custom = [
            {
                "name": "custom-scrape",
                "task": "app.tasks.scraping_tasks.scrape_products_task",
                "cron": "30 4 * * *",
                "args": [1, {"url": "https://x.com"}],
            }
        ]
        schedule = build_celery_beat_schedule(custom)
        assert "custom-scrape" in schedule
        assert schedule["custom-scrape"]["args"] == [1, {"url": "https://x.com"}]

    def test_build_celery_beat_schedule_skips_invalid(self):
        invalid = [
            {"name": "no-task", "cron": "0 2 * * *"},
            {"name": "no-cron", "task": "x"},
            {"name": "bad-cron", "task": "x", "cron": "not a cron"},
        ]
        schedule = build_celery_beat_schedule(invalid)
        assert schedule == {}

    def test_parse_cron_expression_valid(self):
        result = parse_cron_expression("0 2 * * *")
        assert result == {
            "minute": "0",
            "hour": "2",
            "day_of_month": "*",
            "month_of_year": "*",
            "day_of_week": "*",
        }

    def test_parse_cron_expression_invalid(self):
        assert parse_cron_expression("") is None
        assert parse_cron_expression("0 2 * *") is None  # 4 fields
        assert parse_cron_expression("0 2 * * * *") is None  # 6 fields
        assert parse_cron_expression(None) is None

    def test_should_run_now_wildcard(self):
        # "* * * * *" 任何时间都应触发
        now = datetime(2024, 6, 15, 10, 30)
        assert should_run_now("* * * * *", now=now) is True

    def test_should_run_now_specific_minute(self):
        now = datetime(2024, 6, 15, 10, 30)
        assert should_run_now("30 * * * *", now=now) is True
        assert should_run_now("31 * * * *", now=now) is False

    def test_should_run_now_specific_hour(self):
        now = datetime(2024, 6, 15, 10, 30)
        assert should_run_now("* 10 * * *", now=now) is True
        assert should_run_now("* 11 * * *", now=now) is False

    def test_should_run_now_step(self):
        # 每 15 分钟
        now = datetime(2024, 6, 15, 10, 30)
        assert should_run_now("*/15 * * * *", now=now) is True
        now2 = datetime(2024, 6, 15, 10, 17)
        assert should_run_now("*/15 * * * *", now=now2) is False

    def test_should_run_now_comma(self):
        now = datetime(2024, 6, 15, 10, 30)
        assert should_run_now("0,30 * * * *", now=now) is True
        now2 = datetime(2024, 6, 15, 10, 15)
        assert should_run_now("0,30 * * * *", now=now2) is False

    def test_should_run_now_invalid(self):
        assert should_run_now("not a cron") is False
        assert should_run_now("") is False


class TestWoocommerceScraperAdvanced:
    """WooCommerce 采集器高级配置测试"""

    def test_create_with_advanced_options(self):
        scraper = create_woocommerce_scraper(
            "https://example.com/shop",
            full_site=True,
            incremental=True,
            scrape_variations=True,
            max_depth=5,
            cron_expression="0 2 * * *",
        )
        assert scraper.config.full_site is True
        assert scraper.config.incremental is True
        assert scraper.config.scrape_variations is True
        assert scraper.config.max_depth == 5
        assert scraper.config.cron_expression == "0 2 * * *"
        # 仍然使用 WooCommerce 选择器
        assert "title" in scraper.config.product_selectors
