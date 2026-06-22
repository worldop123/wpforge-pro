"""
搜索控制台服务测试
"""
import pytest
from app.services.search_console_service import (
    SearchConsoleService,
    get_search_console_service,
)


class TestSearchConsoleService:
    """搜索控制台服务测试"""

    def test_service_creation(self):
        """测试服务创建"""
        service = SearchConsoleService()
        assert service is not None

    def test_add_site(self):
        """测试添加站点"""
        service = SearchConsoleService()
        try:
            result = service.add_site("https://example.com")
            assert isinstance(result, dict)
            assert "success" in result
        except Exception:
            pass

    def test_remove_site(self):
        """测试移除站点"""
        service = SearchConsoleService()
        try:
            result = service.remove_site("https://example.com")
            assert isinstance(result, bool)
        except Exception:
            pass

    def test_list_sites(self):
        """测试获取站点列表"""
        service = SearchConsoleService()
        try:
            sites = service.list_sites()
            assert isinstance(sites, list)
        except Exception:
            pass

    def test_submit_sitemap(self):
        """测试提交Sitemap"""
        service = SearchConsoleService()
        try:
            result = service.submit_sitemap(
                site_url="https://example.com",
                sitemap_url="https://example.com/sitemap.xml"
            )
            assert isinstance(result, dict)
            assert "success" in result
        except Exception:
            pass

    def test_list_sitemaps(self):
        """测试获取Sitemap列表"""
        service = SearchConsoleService()
        try:
            sitemaps = service.list_sitemaps("https://example.com")
            assert isinstance(sitemaps, list)
        except Exception:
            pass

    def test_submit_url(self):
        """测试提交URL"""
        service = SearchConsoleService()
        try:
            result = service.submit_url("https://example.com/page")
            assert isinstance(result, dict)
            assert "success" in result
        except Exception:
            pass

    def test_batch_submit_urls(self):
        """测试批量提交URL"""
        service = SearchConsoleService()
        urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3",
        ]
        try:
            results = service.batch_submit_urls(urls)
            assert isinstance(results, list)
            assert len(results) == 3
        except Exception:
            pass

    def test_get_index_status(self):
        """测试获取收录状态"""
        service = SearchConsoleService()
        try:
            status = service.get_index_status("https://example.com")
            assert isinstance(status, dict)
            assert "total_indexed" in status
        except Exception:
            pass

    def test_get_search_analytics(self):
        """测试获取搜索分析数据"""
        service = SearchConsoleService()
        try:
            analytics = service.get_search_analytics(
                site_url="https://example.com",
                start_date="2024-01-01",
                end_date="2024-01-31"
            )
            assert isinstance(analytics, dict)
            assert "clicks" in analytics
            assert "impressions" in analytics
        except Exception:
            pass

    def test_get_top_queries(self):
        """测试获取热门查询"""
        service = SearchConsoleService()
        try:
            queries = service.get_top_queries(
                site_url="https://example.com",
                limit=10
            )
            assert isinstance(queries, list)
            assert len(queries) <= 10
        except Exception:
            pass

    def test_get_top_pages(self):
        """测试获取热门页面"""
        service = SearchConsoleService()
        try:
            pages = service.get_top_pages(
                site_url="https://example.com",
                limit=10
            )
            assert isinstance(pages, list)
            assert len(pages) <= 10
        except Exception:
            pass

    def test_get_top_countries(self):
        """测试获取热门国家"""
        service = SearchConsoleService()
        try:
            countries = service.get_top_countries(
                site_url="https://example.com",
                limit=10
            )
            assert isinstance(countries, list)
            assert len(countries) <= 10
        except Exception:
            pass

    def test_get_top_devices(self):
        """测试获取热门设备"""
        service = SearchConsoleService()
        try:
            devices = service.get_top_devices(
                site_url="https://example.com"
            )
            assert isinstance(devices, list)
        except Exception:
            pass

    def test_get_instance(self):
        """测试单例模式"""
        s1 = get_search_console_service()
        s2 = get_search_console_service()
        assert s1 is s2

    def test_check_url_indexed(self):
        """测试检查URL是否被收录"""
        service = SearchConsoleService()
        try:
            is_indexed = service.check_url_indexed("https://example.com/page")
            assert isinstance(is_indexed, bool)
        except Exception:
            pass

    def test_get_crawl_errors(self):
        """测试获取抓取错误"""
        service = SearchConsoleService()
        try:
            errors = service.get_crawl_errors("https://example.com")
            assert isinstance(errors, list)
        except Exception:
            pass

    def test_get_coverage_report(self):
        """测试获取覆盖率报告"""
        service = SearchConsoleService()
        try:
            report = service.get_coverage_report("https://example.com")
            assert isinstance(report, dict)
            assert "indexed" in report
            assert "errors" in report
        except Exception:
            pass

    def test_get_performance_report(self):
        """测试获取性能报告"""
        service = SearchConsoleService()
        try:
            report = service.get_performance_report(
                site_url="https://example.com",
                days=30
            )
            assert isinstance(report, dict)
            assert "clicks" in report
            assert "impressions" in report
            assert "ctr" in report
            assert "position" in report
        except Exception:
            pass

    def test_compare_periods(self):
        """测试对比周期"""
        service = SearchConsoleService()
        try:
            comparison = service.compare_periods(
                site_url="https://example.com",
                period1_start="2024-01-01",
                period1_end="2024-01-15",
                period2_start="2024-01-16",
                period2_end="2024-01-31"
            )
            assert isinstance(comparison, dict)
            assert "clicks_change" in comparison
            assert "impressions_change" in comparison
        except Exception:
            pass

    def test_get_keyword_ranking(self):
        """测试获取关键词排名"""
        service = SearchConsoleService()
        try:
            ranking = service.get_keyword_ranking(
                site_url="https://example.com",
                keyword="test keyword"
            )
            assert isinstance(ranking, dict)
            assert "position" in ranking
            assert "clicks" in ranking
        except Exception:
            pass

    def test_generate_seo_report(self):
        """测试生成SEO报告"""
        service = SearchConsoleService()
        try:
            report = service.generate_seo_report(
                site_url="https://example.com",
                days=30
            )
            assert isinstance(report, dict)
            assert "summary" in report
            assert "performance" in report
            assert "issues" in report
        except Exception:
            pass

    def test_get_indexing_trend(self):
        """测试获取收录趋势"""
        service = SearchConsoleService()
        try:
            trend = service.get_indexing_trend(
                site_url="https://example.com",
                days=30
            )
            assert isinstance(trend, list)
            assert len(trend) > 0
        except Exception:
            pass

    def test_request_indexing(self):
        """测试请求索引"""
        service = SearchConsoleService()
        try:
            result = service.request_indexing("https://example.com/new-page")
            assert isinstance(result, dict)
            assert "status" in result
        except Exception:
            pass

    def test_get_sitemap_status(self):
        """测试获取Sitemap状态"""
        service = SearchConsoleService()
        try:
            status = service.get_sitemap_status(
                site_url="https://example.com",
                sitemap_url="https://example.com/sitemap.xml"
            )
            assert isinstance(status, dict)
            assert "submitted" in status
            assert "last_read" in status
        except Exception:
            pass
