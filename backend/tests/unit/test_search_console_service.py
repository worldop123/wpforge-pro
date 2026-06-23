"""
搜索控制台服务测试
"""
import asyncio
import pytest
from unittest.mock import patch
from app.services.search_console_service import (
    SearchEngine,
    IndexingStatus,
    SearchConsoleProperty,
    IndexingResult,
    RankingData,
    SearchAnalyticsData,
    GoogleSearchConsoleService,
    BingWebmasterService,
    SearchEngineSubmissionService,
    VerificationMethod,
    VerificationStatus,
    SiteVerificationInfo,
    CredentialManager,
    RateLimiter,
    retry_with_backoff,
    async_retry_with_backoff,
    BaiduWebmasterService,
    google_generate_verification,
    google_verify_site,
    google_get_index_coverage_report,
    bing_generate_verification,
    bing_verify_site,
    bing_get_keyword_ranking,
    async_submit_url_to_google,
    async_submit_url_to_bing,
    async_submit_url_to_baidu,
    async_submit_url_to_all_engines,
    async_batch_submit_urls,
    async_submit_sitemap_to_all_engines,
    async_check_indexing_status_all,
    async_get_index_coverage_report,
    credential_manager,
)


class TestEnums:
    """枚举测试"""

    def test_search_engine_values(self):
        assert SearchEngine.GOOGLE.value == "google"
        assert SearchEngine.BING.value == "bing"
        assert SearchEngine.DUCKDUCKGO.value == "duckduckgo"
        assert SearchEngine.BAIDU.value == "baidu"
        assert SearchEngine.YANDEX.value == "yandex"

    def test_indexing_status_values(self):
        assert IndexingStatus.INDEXED.value == "indexed"
        assert IndexingStatus.NOT_INDEXED.value == "not_indexed"
        assert IndexingStatus.PENDING.value == "pending"
        assert IndexingStatus.ERROR.value == "error"
        assert IndexingStatus.UNKNOWN.value == "unknown"


class TestDataclasses:
    """数据类测试"""

    def test_search_console_property(self):
        prop = SearchConsoleProperty(
            id="sc-domain:example.com",
            url="https://example.com/",
            search_engine=SearchEngine.GOOGLE,
        )
        assert prop.id == "sc-domain:example.com"
        assert prop.url == "https://example.com/"
        assert prop.search_engine == SearchEngine.GOOGLE
        assert prop.permission_level == "owner"
        assert prop.is_verified is False
        assert prop.total_clicks == 0

    def test_indexing_result(self):
        result = IndexingResult(
            url="https://example.com/page",
            search_engine=SearchEngine.GOOGLE,
            status=IndexingStatus.INDEXED,
        )
        assert result.url == "https://example.com/page"
        assert result.search_engine == SearchEngine.GOOGLE
        assert result.status == IndexingStatus.INDEXED
        assert result.indexed is False
        assert result.error_message == ""

    def test_ranking_data(self):
        ranking = RankingData(
            keyword="test",
            url="https://example.com",
            search_engine=SearchEngine.GOOGLE,
        )
        assert ranking.keyword == "test"
        assert ranking.url == "https://example.com"
        assert ranking.search_engine == SearchEngine.GOOGLE
        assert ranking.position == 0

    def test_search_analytics_data(self):
        data = SearchAnalyticsData(date="2024-01-01")
        assert data.date == "2024-01-01"
        assert data.clicks == 0
        assert data.impressions == 0


class TestGoogleSearchConsoleService:
    """Google Search Console服务测试"""

    def test_service_creation(self):
        service = GoogleSearchConsoleService()
        assert service is not None
        assert service._is_authorized is False

    def test_authorize(self):
        service = GoogleSearchConsoleService()
        result = service.authorize({"api_key": "test"})
        assert result is True
        assert service._is_authorized is True

    def test_list_sites(self):
        service = GoogleSearchConsoleService()
        sites = service.list_sites()
        assert isinstance(sites, list)
        assert len(sites) > 0
        assert isinstance(sites[0], SearchConsoleProperty)
        assert sites[0].search_engine == SearchEngine.GOOGLE

    def test_submit_url(self):
        service = GoogleSearchConsoleService()
        result = service.submit_url("https://example.com/page", "https://example.com")
        assert isinstance(result, dict)
        assert result["success"] is True
        assert result["url"] == "https://example.com/page"

    def test_get_indexing_status(self):
        service = GoogleSearchConsoleService()
        result = service.get_indexing_status("https://example.com/page")
        assert isinstance(result, IndexingResult)
        assert result.search_engine == SearchEngine.GOOGLE
        assert result.status == IndexingStatus.INDEXED

    def test_get_search_analytics(self):
        service = GoogleSearchConsoleService()
        analytics = service.get_search_analytics(
            site_url="https://example.com",
            start_date="2024-01-01",
            end_date="2024-01-03",
        )
        assert isinstance(analytics, list)
        assert len(analytics) > 0
        assert isinstance(analytics[0], SearchAnalyticsData)

    def test_get_top_queries(self):
        service = GoogleSearchConsoleService()
        queries = service.get_top_queries(
            site_url="https://example.com",
            start_date="2024-01-01",
            end_date="2024-01-31",
            limit=5,
        )
        assert isinstance(queries, list)
        assert len(queries) <= 5
        assert isinstance(queries[0], RankingData)

    def test_submit_sitemap(self):
        service = GoogleSearchConsoleService()
        result = service.submit_sitemap(
            site_url="https://example.com",
            sitemap_url="https://example.com/sitemap.xml",
        )
        assert isinstance(result, dict)
        assert result["success"] is True

    def test_get_sitemaps(self):
        service = GoogleSearchConsoleService()
        sitemaps = service.get_sitemaps("https://example.com")
        assert isinstance(sitemaps, list)
        assert len(sitemaps) > 0
        assert "path" in sitemaps[0]


class TestBingWebmasterService:
    """Bing Webmaster服务测试"""

    def test_service_creation(self):
        service = BingWebmasterService()
        assert service is not None
        assert service.api_key is None

    def test_set_api_key(self):
        service = BingWebmasterService()
        service.set_api_key("test-api-key")
        assert service.api_key == "test-api-key"

    def test_list_sites(self):
        service = BingWebmasterService()
        sites = service.list_sites()
        assert isinstance(sites, list)
        assert len(sites) > 0
        assert sites[0].search_engine == SearchEngine.BING

    def test_submit_url(self):
        service = BingWebmasterService()
        result = service.submit_url("https://example.com/page", "https://example.com")
        assert isinstance(result, dict)
        assert result["success"] is True

    def test_get_indexing_status(self):
        service = BingWebmasterService()
        result = service.get_indexing_status("https://example.com/page")
        assert isinstance(result, IndexingResult)
        assert result.search_engine == SearchEngine.BING

    def test_submit_sitemap(self):
        service = BingWebmasterService()
        result = service.submit_sitemap(
            site_url="https://example.com",
            sitemap_url="https://example.com/sitemap.xml",
        )
        assert isinstance(result, dict)
        assert result["success"] is True

    def test_get_keyword_stats(self):
        service = BingWebmasterService()
        stats = service.get_keyword_stats(
            site_url="https://example.com",
            keyword="test",
        )
        assert isinstance(stats, dict)
        assert "keyword" in stats
        assert "impressions" in stats
        assert "clicks" in stats


class TestSearchEngineSubmissionService:
    """搜索引擎提交服务测试"""

    def test_service_creation(self):
        service = SearchEngineSubmissionService()
        assert service is not None
        assert isinstance(service.gsc_service, GoogleSearchConsoleService)
        assert isinstance(service.bing_service, BingWebmasterService)

    def test_submit_url_to_all(self):
        service = SearchEngineSubmissionService()
        result = service.submit_url_to_all(
            url="https://example.com/page",
            site_url="https://example.com",
        )
        assert isinstance(result, dict)
        assert "results" in result
        assert "google" in result["results"]
        assert "bing" in result["results"]
        assert result["results"]["google"]["success"] is True
        assert result["results"]["bing"]["success"] is True


# ===========================================================================
# 以下为新增测试用例：站点验证、凭证加密、速率限制、重试机制、百度服务、异步方法
# ===========================================================================


class TestVerificationEnums:
    """验证相关枚举测试"""

    def test_verification_method_values(self):
        assert VerificationMethod.HTML_META.value == "html_meta"
        assert VerificationMethod.DNS_TXT.value == "dns_txt"
        assert VerificationMethod.HTML_FILE.value == "html_file"
        assert VerificationMethod.GOOGLE_ANALYTICS.value == "google_analytics"
        assert VerificationMethod.GOOGLE_TAG_MANAGER.value == "google_tag_manager"

    def test_verification_status_values(self):
        assert VerificationStatus.VERIFIED.value == "verified"
        assert VerificationStatus.PENDING.value == "pending"
        assert VerificationStatus.FAILED.value == "failed"
        assert VerificationStatus.NOT_STARTED.value == "not_started"

    def test_verification_method_is_str_enum(self):
        assert isinstance(VerificationMethod.HTML_META, str)

    def test_verification_status_is_str_enum(self):
        assert isinstance(VerificationStatus.VERIFIED, str)


class TestSiteVerificationInfo:
    """站点验证信息数据类测试"""

    def test_default_values(self):
        info = SiteVerificationInfo(
            site_url="https://example.com",
            search_engine=SearchEngine.GOOGLE,
            method=VerificationMethod.HTML_META,
        )
        assert info.status == VerificationStatus.NOT_STARTED
        assert info.verification_token == ""
        assert info.verification_content == ""
        assert info.file_path == ""
        assert info.verified_at is None
        assert info.error_message == ""
        assert info.metadata == {}

    def test_full_values(self):
        info = SiteVerificationInfo(
            site_url="https://example.com",
            search_engine=SearchEngine.GOOGLE,
            method=VerificationMethod.HTML_FILE,
            status=VerificationStatus.VERIFIED,
            verification_token="abc123",
            verification_content="content",
            file_path="abc123.html",
            verified_at="2024-01-01",
        )
        assert info.status == VerificationStatus.VERIFIED
        assert info.verification_token == "abc123"
        assert info.file_path == "abc123.html"

    def test_metadata_independent(self):
        i1 = SiteVerificationInfo(
            site_url="u", search_engine=SearchEngine.GOOGLE, method=VerificationMethod.HTML_META
        )
        i2 = SiteVerificationInfo(
            site_url="u", search_engine=SearchEngine.GOOGLE, method=VerificationMethod.HTML_META
        )
        i1.metadata["k"] = "v"
        assert "k" not in i2.metadata


class TestCredentialManager:
    """凭证管理器测试"""

    def test_encrypt_decrypt_string(self):
        mgr = CredentialManager()
        plaintext = "my-secret-api-key"
        encrypted = mgr.encrypt(plaintext)
        assert encrypted != plaintext
        assert mgr.decrypt(encrypted) == plaintext

    def test_encrypt_empty_string(self):
        mgr = CredentialManager()
        assert mgr.encrypt("") == ""
        assert mgr.decrypt("") == ""

    def test_encrypt_credentials_dict(self):
        mgr = CredentialManager()
        creds = {"api_key": "secret", "client_id": "abc"}
        encrypted = mgr.encrypt_credentials(creds)
        assert isinstance(encrypted, str)
        decrypted = mgr.decrypt_credentials(encrypted)
        assert decrypted == creds

    def test_decrypt_credentials_empty(self):
        mgr = CredentialManager()
        assert mgr.decrypt_credentials("") == {}

    def test_decrypt_credentials_invalid_json(self):
        mgr = CredentialManager()
        encrypted = mgr.encrypt("not-json")
        result = mgr.decrypt_credentials(encrypted)
        assert result == {}

    def test_store_and_load_credentials(self):
        mgr = CredentialManager()
        creds = {"token": "abc", "site": "example.com"}
        encrypted = mgr.store_credentials("site-1", creds)
        loaded = mgr.load_credentials(encrypted)
        assert loaded == creds

    def test_decrypt_plaintext_passthrough(self):
        mgr = CredentialManager()
        # 未加密的明文应原样返回
        assert mgr.decrypt("plain-text") == "plain-text"

    def test_global_credential_manager(self):
        assert credential_manager is not None
        encrypted = credential_manager.encrypt("test")
        assert credential_manager.decrypt(encrypted) == "test"

    def test_custom_secret_key(self):
        mgr1 = CredentialManager(secret_key="key-A")
        mgr2 = CredentialManager(secret_key="key-A")
        encrypted = mgr1.encrypt("secret")
        # 相同密钥可以解密
        assert mgr2.decrypt(encrypted) == "secret"


class TestRateLimiter:
    """速率限制器测试"""

    def test_acquire_within_limit(self):
        limiter = RateLimiter(max_calls=5, period=1.0)
        for _ in range(5):
            assert limiter.acquire() is True

    def test_acquire_exceeds_limit(self):
        limiter = RateLimiter(max_calls=2, period=1.0)
        assert limiter.acquire() is True
        assert limiter.acquire() is True
        assert limiter.acquire() is False

    def test_reset(self):
        limiter = RateLimiter(max_calls=1, period=1.0)
        limiter.acquire()
        assert limiter.acquire() is False
        limiter.reset()
        assert limiter.acquire() is True

    def test_wait_returns_when_available(self):
        limiter = RateLimiter(max_calls=10, period=1.0)
        # 应立即返回，因为配额充足
        limiter.wait()
        assert len(limiter._timestamps) == 1

    def test_wait_async(self):
        limiter = RateLimiter(max_calls=10, period=1.0)
        asyncio.run(limiter.wait_async())
        assert len(limiter._timestamps) == 1


class TestRetryWithBackoff:
    """重试机制测试"""

    def test_retry_success_first_try(self):
        call_count = {"n": 0}

        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def func():
            call_count["n"] += 1
            return "ok"

        assert func() == "ok"
        assert call_count["n"] == 1

    def test_retry_success_after_failures(self):
        call_count = {"n": 0}

        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def func():
            call_count["n"] += 1
            if call_count["n"] < 3:
                raise ValueError("fail")
            return "ok"

        assert func() == "ok"
        assert call_count["n"] == 3

    def test_retry_exhausted_raises(self):
        call_count = {"n": 0}

        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def func():
            call_count["n"] += 1
            raise ValueError("always fail")

        with pytest.raises(ValueError):
            func()
        assert call_count["n"] == 3  # 1次初始 + 2次重试

    def test_retry_specific_exception_only(self):
        call_count = {"n": 0}

        @retry_with_backoff(max_retries=3, base_delay=0.01, exceptions=(ValueError,))
        def func():
            call_count["n"] += 1
            raise TypeError("not retried")

        with pytest.raises(TypeError):
            func()
        assert call_count["n"] == 1

    def test_async_retry_success(self):
        call_count = {"n": 0}

        def func():
            call_count["n"] += 1
            return "ok"

        result = asyncio.run(
            async_retry_with_backoff(func, max_retries=2, base_delay=0.01)
        )
        assert result == "ok"
        assert call_count["n"] == 1

    def test_async_retry_with_failures(self):
        call_count = {"n": 0}

        def func():
            call_count["n"] += 1
            if call_count["n"] < 2:
                raise ValueError("fail")
            return "recovered"

        result = asyncio.run(
            async_retry_with_backoff(func, max_retries=3, base_delay=0.01)
        )
        assert result == "recovered"
        assert call_count["n"] == 2

    def test_async_retry_exhausted(self):
        def func():
            raise ValueError("always")

        with pytest.raises(ValueError):
            asyncio.run(
                async_retry_with_backoff(func, max_retries=1, base_delay=0.01)
            )


class TestBaiduWebmasterService:
    """百度站长服务测试"""

    def test_service_creation_no_credentials(self):
        service = BaiduWebmasterService()
        assert service.site is None
        assert service.token is None
        assert service._check_credentials() is False

    def test_set_credentials(self):
        service = BaiduWebmasterService()
        service.set_credentials("example.com", "token123")
        assert service.site == "example.com"
        assert service.token == "token123"
        assert service._check_credentials() is True

    def test_submit_url_no_credentials(self):
        service = BaiduWebmasterService()
        result = service.submit_url("https://example.com/page")
        assert result["success"] is False
        assert result["error_code"] == "no_credentials"

    def test_submit_url_with_credentials(self):
        service = BaiduWebmasterService(site="example.com", token="tok")
        result = service.submit_url("https://example.com/page")
        assert result["success"] is True
        assert result["url"] == "https://example.com/page"
        assert "remain" in result

    def test_submit_urls_batch(self):
        service = BaiduWebmasterService(site="example.com", token="tok")
        urls = ["https://example.com/1", "https://example.com/2"]
        result = service.submit_urls_batch(urls)
        assert result["success"] is True
        assert result["total"] == 2

    def test_submit_url_fast(self):
        service = BaiduWebmasterService(site="example.com", token="tok")
        result = service.submit_url_fast("https://example.com/page")
        assert result["success"] is True
        assert result["type"] == "fast"

    def test_submit_sitemap(self):
        service = BaiduWebmasterService(site="example.com", token="tok")
        result = service.submit_sitemap("https://example.com", "https://example.com/sitemap.xml")
        assert result["success"] is True

    def test_get_indexed_count(self):
        service = BaiduWebmasterService(site="example.com", token="tok")
        with patch.object(service, "_fetch_indexed_count", return_value=1234):
            result = service.get_indexed_count("https://example.com")
        assert result["success"] is True
        assert "indexed_count" in result

    def test_get_indexed_count_no_credentials(self):
        service = BaiduWebmasterService()
        result = service.get_indexed_count("https://example.com")
        assert result["success"] is False
        assert result["indexed_count"] == 0

    def test_get_indexing_status(self):
        service = BaiduWebmasterService()
        result = service.get_indexing_status("https://example.com/page")
        assert isinstance(result, IndexingResult)
        assert result.search_engine == SearchEngine.BAIDU
        assert result.status == IndexingStatus.INDEXED

    def test_generate_verification_meta(self):
        service = BaiduWebmasterService()
        info = service.generate_verification_meta("https://example.com")
        assert info.search_engine == SearchEngine.BAIDU
        assert info.method == VerificationMethod.HTML_META
        assert "baidu-site-verification" in info.verification_content

    def test_verify_site_no_credentials(self):
        service = BaiduWebmasterService()
        result = service.verify_site("https://example.com")
        assert result["success"] is False

    def test_verify_site_with_credentials(self):
        service = BaiduWebmasterService(site="example.com", token="tok")
        result = service.verify_site("https://example.com")
        assert result["success"] is True
        assert result["status"] == VerificationStatus.VERIFIED.value


class TestGoogleVerification:
    """Google站点验证测试"""

    def test_generate_verification_html_meta(self):
        info = google_generate_verification("https://example.com", VerificationMethod.HTML_META)
        assert info.search_engine == SearchEngine.GOOGLE
        assert info.method == VerificationMethod.HTML_META
        assert "google-site-verification" in info.verification_content
        assert info.verification_token != ""

    def test_generate_verification_dns_txt(self):
        info = google_generate_verification("https://example.com", VerificationMethod.DNS_TXT)
        assert info.method == VerificationMethod.DNS_TXT
        assert "google-site-verification=" in info.verification_content

    def test_generate_verification_html_file(self):
        info = google_generate_verification("https://example.com", VerificationMethod.HTML_FILE)
        assert info.method == VerificationMethod.HTML_FILE
        assert info.file_path.endswith(".html")
        assert info.verification_token != ""

    def test_verify_site_success(self):
        result = google_verify_site("https://example.com", VerificationMethod.HTML_META)
        assert result["success"] is True
        assert result["status"] == VerificationStatus.VERIFIED.value

    def test_get_index_coverage_report(self):
        report = google_get_index_coverage_report("https://example.com")
        assert report["site_url"] == "https://example.com"
        assert "total_urls" in report
        assert "indexed" in report
        assert "index_rate" in report
        assert "coverage" in report
        assert report["index_rate"] >= 0
        assert report["indexed"] <= report["total_urls"]


class TestBingVerification:
    """Bing站点验证测试"""

    def test_generate_verification(self):
        info = bing_generate_verification("https://example.com")
        assert info.search_engine == SearchEngine.BING
        assert "msvalidate.01" in info.verification_content

    def test_verify_site_no_api_key(self):
        result = bing_verify_site("https://example.com")
        assert result["success"] is False
        assert result["error_code"] == "no_api_key"

    def test_verify_site_with_api_key(self):
        result = bing_verify_site("https://example.com", api_key="bing-key")
        assert result["success"] is True
        assert result["status"] == VerificationStatus.VERIFIED.value

    def test_get_keyword_ranking_no_api_key(self):
        result = bing_get_keyword_ranking("https://example.com", "test")
        assert result["success"] is False
        assert result["error_code"] == "no_api_key"

    def test_get_keyword_ranking_with_api_key(self):
        result = bing_get_keyword_ranking("https://example.com", "test", api_key="key")
        assert result["success"] is True
        assert result["keyword"] == "test"
        assert "position" in result
        assert "search_volume" in result


class TestAsyncMethods:
    """异步方法测试"""

    def test_async_submit_url_to_google(self):
        result = asyncio.run(
            async_submit_url_to_google("https://example.com/page", "https://example.com")
        )
        assert isinstance(result, dict)
        assert result["success"] is True

    def test_async_submit_url_to_bing(self):
        result = asyncio.run(
            async_submit_url_to_bing("https://example.com/page", "https://example.com", api_key="key")
        )
        assert isinstance(result, dict)
        assert result["success"] is True

    def test_async_submit_url_to_baidu(self):
        result = asyncio.run(
            async_submit_url_to_baidu(
                "https://example.com/page", "https://example.com", site="example.com", token="tok"
            )
        )
        assert isinstance(result, dict)
        assert result["success"] is True

    def test_async_submit_url_to_all_engines(self):
        result = asyncio.run(
            async_submit_url_to_all_engines(
                "https://example.com/page",
                "https://example.com",
                google_credentials={"api_key": "g"},
                bing_api_key="b",
                baidu_site="example.com",
                baidu_token="t",
            )
        )
        assert "results" in result
        assert "google" in result["results"]
        assert "bing" in result["results"]
        assert "baidu" in result["results"]
        assert result["total_success"] == 3

    def test_async_submit_url_to_all_engines_no_credentials(self):
        result = asyncio.run(
            async_submit_url_to_all_engines("https://example.com/page", "https://example.com")
        )
        assert result["results"] == {}
        assert result["total_success"] == 0

    def test_async_batch_submit_urls(self):
        urls = ["https://example.com/1", "https://example.com/2"]
        result = asyncio.run(
            async_batch_submit_urls(
                urls, "https://example.com",
                google_credentials={"api_key": "g"},
                delay=0,  # 测试中不延迟
            )
        )
        assert result["total_urls"] == 2
        assert result["success_count"] == 2
        assert len(result["results"]) == 2

    def test_async_submit_sitemap_to_all_engines(self):
        result = asyncio.run(
            async_submit_sitemap_to_all_engines(
                "https://example.com/sitemap.xml",
                "https://example.com",
                google_credentials={"api_key": "g"},
                bing_api_key="b",
                baidu_site="example.com",
                baidu_token="t",
            )
        )
        assert "results" in result
        assert result["total_success"] == 3

    def test_async_check_indexing_status_all(self):
        result = asyncio.run(
            async_check_indexing_status_all("https://example.com/page")
        )
        assert "google" in result
        assert "bing" in result
        assert "baidu" in result
        assert isinstance(result["google"], IndexingResult)

    def test_async_check_indexing_status_specific_engines(self):
        result = asyncio.run(
            async_check_indexing_status_all(
                "https://example.com/page", [SearchEngine.GOOGLE]
            )
        )
        assert "google" in result
        assert "bing" not in result
        assert "baidu" not in result

    def test_async_get_index_coverage_report(self):
        result = asyncio.run(
            async_get_index_coverage_report("https://example.com")
        )
        assert "total_urls" in result
        assert "indexed" in result


class TestSearchEngineSubmissionServiceExtended:
    """搜索引擎提交服务扩展测试"""

    def test_batch_submit_urls(self):
        service = SearchEngineSubmissionService()
        urls = ["https://example.com/1", "https://example.com/2"]
        result = service.batch_submit_urls(urls, "https://example.com", delay=0)
        assert result["total_urls"] == 2
        assert result["success_count"] == 2
        assert len(result["results"]) == 2

    def test_check_indexing_status(self):
        service = SearchEngineSubmissionService()
        result = service.check_indexing_status("https://example.com/page")
        assert "google" in result
        assert "bing" in result
        assert isinstance(result["google"], IndexingResult)

    def test_submit_sitemap_to_all(self):
        service = SearchEngineSubmissionService()
        result = service.submit_sitemap_to_all(
            "https://example.com/sitemap.xml", "https://example.com"
        )
        assert "google" in result
        assert "bing" in result

    def test_get_indexing_report(self):
        service = SearchEngineSubmissionService()
        urls = ["https://example.com/1", "https://example.com/2"]
        report = service.get_indexing_report("https://example.com", urls)
        assert report["site_url"] == "https://example.com"
        assert report["total_urls"] == 2
        assert "google" in report
        assert "bing" in report
        assert "url_statuses" in report

    def test_get_ranking_report(self):
        service = SearchEngineSubmissionService()
        keywords = ["wordpress", "hosting"]
        report = service.get_ranking_report(
            "https://example.com", keywords, "2024-01-01", "2024-01-31"
        )
        assert report["total_keywords"] == 2
        assert "rankings" in report
        assert len(report["rankings"]) == 2

    def test_get_submission_history(self):
        service = SearchEngineSubmissionService()
        service.submit_url_to_all("https://example.com/page", "https://example.com")
        history = service.get_submission_history()
        assert len(history) == 1
        assert history[0]["url"] == "https://example.com/page"

    def test_get_best_practices(self):
        service = SearchEngineSubmissionService()
        practices = service.get_best_practices()
        assert isinstance(practices, list)
        assert len(practices) > 0
