"""
代理网络模块测试 - 请求头伪造、Cookie 处理、缓存模拟
"""
import time
import pytest

from app.services.proxy.network.request_headers import RequestHeaderGenerator
from app.services.proxy.network.cookie_handler import Cookie, CookieHandler
from app.services.proxy.network.cache_simulator import CacheEntry, CacheSimulator


# ==================== RequestHeaderGenerator 测试 ====================

class TestRequestHeaderGenerator:
    """请求头生成器测试"""

    def test_creation_defaults(self):
        gen = RequestHeaderGenerator()
        assert gen._browser == "chrome"
        assert gen._language == "en-US"

    def test_set_browser(self):
        gen = RequestHeaderGenerator()
        gen.set_browser("firefox")
        assert gen._browser == "firefox"

    def test_set_browser_uppercase(self):
        gen = RequestHeaderGenerator()
        gen.set_browser("SAFARI")
        assert gen._browser == "safari"

    def test_set_user_agent_chrome(self):
        gen = RequestHeaderGenerator()
        gen.set_user_agent("Mozilla/5.0 (Windows NT 10.0) Chrome/124.0.0.0")
        assert "Chrome" in gen._sec_ch_ua
        assert "124" in gen._sec_ch_ua

    def test_set_user_agent_non_chrome(self):
        gen = RequestHeaderGenerator()
        gen.set_user_agent("Mozilla/5.0 (Firefox)")
        # 非 Chrome UA 使用默认 sec-ch-ua
        assert gen._sec_ch_ua != ""

    def test_set_language_with_languages(self):
        gen = RequestHeaderGenerator()
        gen.set_language("zh-CN", ["zh-CN", "zh", "en"])
        assert gen._language == "zh-CN"
        assert gen._languages == ["zh-CN", "zh", "en"]

    def test_set_language_without_languages(self):
        gen = RequestHeaderGenerator()
        gen.set_language("fr-FR")
        assert gen._language == "fr-FR"
        assert gen._languages[0] == "fr-FR"
        assert gen._languages[1] == "fr"

    def test_generate_chrome_headers(self):
        gen = RequestHeaderGenerator()
        gen.set_user_agent("Mozilla/5.0 Chrome/124.0")
        headers = gen.generate_headers("https://example.com/page")
        assert headers["Host"] == "example.com"
        assert headers["User-Agent"] == "Mozilla/5.0 Chrome/124.0"
        assert "sec-ch-ua" in headers
        assert headers["Sec-Fetch-Site"] == "none"
        assert headers["Sec-Fetch-Mode"] == "navigate"
        assert headers["Sec-Fetch-Dest"] == "document"

    def test_generate_chrome_headers_with_referer_same_origin(self):
        gen = RequestHeaderGenerator()
        gen.set_user_agent("Mozilla/5.0 Chrome/124.0")
        headers = gen.generate_headers(
            "https://example.com/page",
            referer="https://example.com/home",
        )
        assert headers["Sec-Fetch-Site"] == "same-origin"
        assert headers["Referer"] == "https://example.com/home"

    def test_generate_chrome_headers_with_referer_cross_site(self):
        gen = RequestHeaderGenerator()
        gen.set_user_agent("Mozilla/5.0 Chrome/124.0")
        headers = gen.generate_headers(
            "https://example.com/page",
            referer="https://other.com/home",
        )
        assert headers["Sec-Fetch-Site"] == "cross-site"

    def test_generate_chrome_ajax_headers(self):
        gen = RequestHeaderGenerator()
        gen.set_user_agent("Mozilla/5.0 Chrome/124.0")
        headers = gen.generate_headers("https://example.com/api", is_ajax=True)
        assert "application/json" in headers["Accept"]
        assert headers["Sec-Fetch-Mode"] == "cors"
        assert headers["Sec-Fetch-Dest"] == "empty"
        assert "Sec-Fetch-User" not in headers

    def test_generate_firefox_headers(self):
        gen = RequestHeaderGenerator()
        gen.set_browser("firefox")
        gen.set_user_agent("Mozilla/5.0 Firefox/120.0")
        headers = gen.generate_headers("https://example.com/page")
        assert headers["Host"] == "example.com"
        assert headers["User-Agent"] == "Mozilla/5.0 Firefox/120.0"
        assert "Sec-Fetch-Mode" in headers

    def test_generate_firefox_ajax_headers(self):
        gen = RequestHeaderGenerator()
        gen.set_browser("firefox")
        gen.set_user_agent("Mozilla/5.0 Firefox/120.0")
        headers = gen.generate_headers("https://example.com/api", is_ajax=True)
        assert headers["Sec-Fetch-Dest"] == "empty"
        assert headers["Sec-Fetch-Mode"] == "cors"

    def test_generate_safari_headers(self):
        gen = RequestHeaderGenerator()
        gen.set_browser("safari")
        gen.set_user_agent("Mozilla/5.0 Safari/605.1")
        headers = gen.generate_headers("https://example.com/page")
        assert headers["Host"] == "example.com"
        assert headers["User-Agent"] == "Mozilla/5.0 Safari/605.1"
        assert "sec-ch-ua" not in headers

    def test_generate_safari_ajax_headers(self):
        gen = RequestHeaderGenerator()
        gen.set_browser("safari")
        gen.set_user_agent("Mozilla/5.0 Safari/605.1")
        headers = gen.generate_headers("https://example.com/api", is_ajax=True)
        assert "application/json" in headers["Accept"]

    def test_generate_headers_with_extra_headers(self):
        gen = RequestHeaderGenerator()
        gen.set_user_agent("Mozilla/5.0 Chrome/124.0")
        headers = gen.generate_headers(
            "https://example.com/page",
            extra_headers={"X-Custom": "value"},
        )
        assert headers["X-Custom"] == "value"

    def test_generate_headers_unknown_browser_defaults_chrome(self):
        gen = RequestHeaderGenerator()
        gen.set_browser("edge")
        gen.set_user_agent("Mozilla/5.0 Chrome/124.0")
        headers = gen.generate_headers("https://example.com/page")
        assert headers["Host"] == "example.com"

    def test_generate_ajax_headers_helper(self):
        gen = RequestHeaderGenerator()
        gen.set_user_agent("Mozilla/5.0 Chrome/124.0")
        headers = gen.generate_ajax_headers("https://example.com/api")
        assert headers["Sec-Fetch-Mode"] == "cors"

    def test_generate_image_headers(self):
        gen = RequestHeaderGenerator()
        gen.set_user_agent("Mozilla/5.0 Chrome/124.0")
        headers = gen.generate_image_headers("https://example.com/img.jpg")
        assert "image" in headers["Accept"]
        assert headers["Sec-Fetch-Dest"] == "image"
        assert headers["Sec-Fetch-Mode"] == "no-cors"

    def test_generate_script_headers(self):
        gen = RequestHeaderGenerator()
        gen.set_user_agent("Mozilla/5.0 Chrome/124.0")
        headers = gen.generate_script_headers("https://example.com/script.js")
        assert headers["Accept"] == "*/*"
        assert headers["Sec-Fetch-Dest"] == "script"

    def test_generate_stylesheet_headers(self):
        gen = RequestHeaderGenerator()
        gen.set_user_agent("Mozilla/5.0 Chrome/124.0")
        headers = gen.generate_stylesheet_headers("https://example.com/style.css")
        assert "text/css" in headers["Accept"]
        assert headers["Sec-Fetch-Dest"] == "style"

    def test_get_header_order_chrome(self):
        gen = RequestHeaderGenerator()
        order = gen.get_header_order()
        assert "Host" in order
        assert "User-Agent" in order

    def test_get_header_order_firefox(self):
        gen = RequestHeaderGenerator()
        gen.set_browser("firefox")
        order = gen.get_header_order()
        assert "Host" in order

    def test_get_header_order_safari(self):
        gen = RequestHeaderGenerator()
        gen.set_browser("safari")
        order = gen.get_header_order()
        assert "Host" in order

    def test_get_header_order_unknown_browser(self):
        gen = RequestHeaderGenerator()
        gen.set_browser("unknown")
        order = gen.get_header_order()
        assert "Host" in order

    def test_order_headers_preserves_unknown(self):
        gen = RequestHeaderGenerator()
        gen.set_user_agent("Mozilla/5.0 Chrome/124.0")
        headers = gen.generate_headers(
            "https://example.com/page",
            extra_headers={"X-Custom-Header": "val"},
        )
        # 未知头应出现在末尾
        assert "X-Custom-Header" in headers


# ==================== Cookie 测试 ====================

class TestCookie:
    """Cookie 数据类测试"""

    def test_cookie_creation(self):
        cookie = Cookie(name="session", value="abc", domain="example.com")
        assert cookie.name == "session"
        assert cookie.value == "abc"
        assert cookie.domain == "example.com"
        assert cookie.path == "/"

    def test_cookie_is_expired_session(self):
        cookie = Cookie(name="session", value="abc", domain="example.com")
        # 会话 Cookie 不过期
        assert cookie.is_expired() is False

    def test_cookie_is_expired_max_age(self):
        cookie = Cookie(name="session", value="abc", domain="example.com", max_age=0)
        # max_age=0 立即过期
        time.sleep(0.01)
        assert cookie.is_expired() is True

    def test_cookie_is_expired_expires_past(self):
        cookie = Cookie(
            name="session", value="abc", domain="example.com",
            expires=time.time() - 100,
        )
        assert cookie.is_expired() is True

    def test_cookie_is_expired_expires_future(self):
        cookie = Cookie(
            name="session", value="abc", domain="example.com",
            expires=time.time() + 100,
        )
        assert cookie.is_expired() is False

    def test_cookie_matches_domain(self):
        cookie = Cookie(name="session", value="abc", domain="example.com")
        assert cookie.matches("https://example.com/page") is True
        assert cookie.matches("https://sub.example.com/page") is True

    def test_cookie_matches_path(self):
        cookie = Cookie(name="session", value="abc", domain="example.com", path="/api")
        assert cookie.matches("https://example.com/api/data") is True
        assert cookie.matches("https://example.com/page") is False

    def test_cookie_matches_secure(self):
        cookie = Cookie(name="session", value="abc", domain="example.com", secure=True)
        assert cookie.matches("https://example.com/page") is True
        assert cookie.matches("http://example.com/page") is False

    def test_cookie_to_header_string(self):
        cookie = Cookie(name="session", value="abc", domain="example.com")
        assert cookie.to_header_string() == "session=abc"


class TestCookieHandler:
    """Cookie 处理器测试"""

    def test_add_cookie(self):
        handler = CookieHandler()
        cookie = Cookie(name="session", value="abc", domain="example.com")
        handler.add_cookie(cookie)
        assert handler.get_cookie_count() == 1

    def test_add_cookie_from_header(self):
        handler = CookieHandler()
        handler.add_cookie_from_header(
            "sessionid=abc123; Path=/; Domain=example.com; HttpOnly",
            domain="example.com",
        )
        assert handler.get_cookie_count() == 1
        cookies = handler.get_cookies_for_url("https://example.com/")
        assert len(cookies) == 1
        assert cookies[0].name == "sessionid"
        assert cookies[0].value == "abc123"
        assert cookies[0].httponly is True

    def test_add_cookie_from_header_with_expires(self):
        handler = CookieHandler()
        handler.add_cookie_from_header(
            "token=xyz; Expires=Wed, 21 Oct 2099 07:28:00 GMT; Path=/",
            domain="example.com",
        )
        assert handler.get_cookie_count() == 1

    def test_add_cookie_from_header_with_max_age(self):
        handler = CookieHandler()
        handler.add_cookie_from_header(
            "token=xyz; Max-Age=3600; Path=/",
            domain="example.com",
        )
        assert handler.get_cookie_count() == 1

    def test_add_cookie_from_header_secure_samesite(self):
        handler = CookieHandler()
        handler.add_cookie_from_header(
            "token=xyz; Secure; SameSite=Strict; Path=/",
            domain="example.com",
        )
        cookies = handler.get_cookies_for_url("https://example.com/")
        assert len(cookies) == 1
        assert cookies[0].secure is True
        assert cookies[0].samesite == "Strict"

    def test_add_cookie_from_header_invalid(self):
        handler = CookieHandler()
        # 没有 = 的无效 cookie
        handler.add_cookie_from_header("invalidcookie", domain="example.com")
        assert handler.get_cookie_count() == 0

    def test_add_cookie_from_header_empty(self):
        handler = CookieHandler()
        handler.add_cookie_from_header("", domain="example.com")
        assert handler.get_cookie_count() == 0

    def test_get_cookie_header(self):
        handler = CookieHandler()
        handler.add_cookie(Cookie(name="a", value="1", domain="example.com"))
        handler.add_cookie(Cookie(name="b", value="2", domain="example.com"))
        header = handler.get_cookie_header("https://example.com/")
        assert "a=1" in header
        assert "b=2" in header

    def test_get_cookie_header_empty(self):
        handler = CookieHandler()
        assert handler.get_cookie_header("https://example.com/") == ""

    def test_delete_cookie(self):
        handler = CookieHandler()
        handler.add_cookie(Cookie(name="session", value="abc", domain="example.com"))
        handler.delete_cookie("session", "example.com")
        assert handler.get_cookie_count() == 0

    def test_clear_cookies_all(self):
        handler = CookieHandler()
        handler.add_cookie(Cookie(name="a", value="1", domain="example.com"))
        handler.add_cookie(Cookie(name="b", value="2", domain="other.com"))
        handler.clear_cookies()
        assert handler.get_cookie_count() == 0

    def test_clear_cookies_by_domain(self):
        handler = CookieHandler()
        handler.add_cookie(Cookie(name="a", value="1", domain="example.com"))
        handler.add_cookie(Cookie(name="b", value="2", domain="other.com"))
        handler.clear_cookies(domain="example.com")
        assert handler.get_cookie_count() == 1

    def test_get_all_cookies(self):
        handler = CookieHandler()
        handler.add_cookie(Cookie(name="a", value="1", domain="example.com"))
        handler.add_cookie(Cookie(name="b", value="2", domain="example.com"))
        all_cookies = handler.get_all_cookies()
        assert len(all_cookies) == 2

    def test_clean_expired(self):
        handler = CookieHandler()
        handler.add_cookie(Cookie(
            name="expired", value="x", domain="example.com", max_age=0,
        ))
        time.sleep(0.01)
        handler.add_cookie(Cookie(name="valid", value="y", domain="example.com"))
        # 添加新 cookie 时会触发清理
        assert handler.get_cookie_count() == 1

    def test_third_party_settings(self):
        handler = CookieHandler()
        assert handler.is_third_party_enabled() is True
        handler.set_third_party_enabled(False)
        assert handler.is_third_party_enabled() is False

    def test_simulate_cookie_degradation(self):
        handler = CookieHandler()
        # 添加少量 cookie，不应触发降级
        for i in range(10):
            handler.add_cookie(Cookie(name=f"c{i}", value="v", domain="example.com"))
        handler.simulate_cookie_degradation()
        assert handler.get_cookie_count() == 10


# ==================== CacheSimulator 测试 ====================

class TestCacheEntry:
    """缓存条目测试"""

    def test_creation(self):
        entry = CacheEntry(
            url="https://example.com/page",
            headers={"Cache-Control": "max-age=3600", "ETag": "abc"},
        )
        assert entry.url == "https://example.com/page"
        assert entry.max_age == 3600
        assert entry.etag == "abc"

    def test_parse_max_age_none(self):
        entry = CacheEntry(
            url="https://example.com/page",
            headers={},
        )
        assert entry.max_age is None

    def test_parse_max_age_with_other_directives(self):
        entry = CacheEntry(
            url="https://example.com/page",
            headers={"Cache-Control": "public, max-age=600"},
        )
        assert entry.max_age == 600

    def test_is_expired_not_expired(self):
        entry = CacheEntry(
            url="https://example.com/page",
            headers={"Cache-Control": "max-age=3600"},
        )
        assert entry.is_expired() is False

    def test_is_expired_no_max_age(self):
        entry = CacheEntry(url="https://example.com/page", headers={})
        assert entry.is_expired() is False

    def test_is_expired_expired(self):
        entry = CacheEntry(
            url="https://example.com/page",
            headers={"Cache-Control": "max-age=0"},
        )
        time.sleep(0.01)
        assert entry.is_expired() is True

    def test_should_revalidate_no_cache(self):
        entry = CacheEntry(
            url="https://example.com/page",
            headers={"Cache-Control": "no-cache"},
        )
        assert entry.should_revalidate() is True

    def test_should_revalidate_expired_with_etag(self):
        entry = CacheEntry(
            url="https://example.com/page",
            headers={"Cache-Control": "max-age=0", "ETag": "abc"},
        )
        time.sleep(0.01)
        assert entry.should_revalidate() is True

    def test_should_revalidate_not_needed(self):
        entry = CacheEntry(
            url="https://example.com/page",
            headers={"Cache-Control": "max-age=3600"},
        )
        assert entry.should_revalidate() is False

    def test_touch(self):
        entry = CacheEntry(url="https://example.com/page", headers={})
        old_accessed = entry.last_accessed
        old_count = entry.access_count
        time.sleep(0.01)
        entry.touch()
        assert entry.last_accessed > old_accessed
        assert entry.access_count == old_count + 1


class TestCacheSimulator:
    """缓存模拟器测试"""

    def test_creation(self):
        sim = CacheSimulator()
        assert sim.get_cache_stats()["total_entries"] == 0

    def test_add_response(self):
        sim = CacheSimulator()
        sim.add_response("https://example.com/page", {"Cache-Control": "max-age=3600"})
        assert sim.get_cache_stats()["total_entries"] == 1

    def test_add_response_no_store(self):
        sim = CacheSimulator()
        sim.add_response("https://example.com/page", {"Cache-Control": "no-store"})
        assert sim.get_cache_stats()["total_entries"] == 0

    def test_get_cached_response_hit(self):
        sim = CacheSimulator()
        sim.add_response(
            "https://example.com/page",
            {"Cache-Control": "max-age=3600", "Content-Type": "text/html"},
            response_time=1.0,
        )
        result = sim.get_cached_response("https://example.com/page")
        assert result is not None
        assert result["status"] == "hit"
        assert "headers" in result
        assert result["response_time"] < 1.0

    def test_get_cached_response_miss(self):
        sim = CacheSimulator()
        result = sim.get_cached_response("https://example.com/page")
        assert result is None

    def test_get_cached_response_expired_with_revalidate(self):
        sim = CacheSimulator()
        sim.add_response(
            "https://example.com/page",
            {"Cache-Control": "max-age=0", "ETag": "abc"},
        )
        time.sleep(0.01)
        result = sim.get_cached_response("https://example.com/page")
        assert result["status"] == "revalidate"
        assert result["etag"] == "abc"

    def test_get_cached_response_expired_deleted(self):
        sim = CacheSimulator()
        sim.add_response(
            "https://example.com/page",
            {"Cache-Control": "max-age=0"},
        )
        time.sleep(0.01)
        result = sim.get_cached_response("https://example.com/page")
        assert result is None
        assert sim.get_cache_stats()["total_entries"] == 0

    def test_get_conditional_headers(self):
        sim = CacheSimulator()
        sim.add_response(
            "https://example.com/page",
            {"ETag": "abc", "Last-Modified": "Wed, 01 Jan 2024 00:00:00 GMT"},
        )
        headers = sim.get_conditional_headers("https://example.com/page")
        assert headers["If-None-Match"] == "abc"
        assert "If-Modified-Since" in headers

    def test_get_conditional_headers_no_cache(self):
        sim = CacheSimulator()
        headers = sim.get_conditional_headers("https://example.com/notcached")
        assert headers == {}

    def test_handle_304_response(self):
        sim = CacheSimulator()
        sim.add_response(
            "https://example.com/page",
            {"Cache-Control": "max-age=3600", "ETag": "abc"},
        )
        sim.handle_304_response("https://example.com/page", {"X-New": "header"})
        result = sim.get_cached_response("https://example.com/page")
        assert result["headers"]["X-New"] == "header"

    def test_invalidate(self):
        sim = CacheSimulator()
        sim.add_response("https://example.com/page", {"Cache-Control": "max-age=3600"})
        sim.invalidate("https://example.com/page")
        assert sim.get_cache_stats()["total_entries"] == 0

    def test_clear(self):
        sim = CacheSimulator()
        sim.add_response("https://example.com/a", {"Cache-Control": "max-age=3600"})
        sim.add_response("https://example.com/b", {"Cache-Control": "max-age=3600"})
        sim.clear()
        assert sim.get_cache_stats()["total_entries"] == 0

    def test_evict_oldest(self):
        sim = CacheSimulator()
        sim._max_entries = 2
        sim.add_response("https://example.com/a", {"Cache-Control": "max-age=3600"})
        time.sleep(0.01)
        sim.add_response("https://example.com/b", {"Cache-Control": "max-age=3600"})
        time.sleep(0.01)
        # 访问 a 使其更新
        sim.get_cached_response("https://example.com/a")
        time.sleep(0.01)
        # 添加第三个，应该淘汰最旧的 b
        sim.add_response("https://example.com/c", {"Cache-Control": "max-age=3600"})
        assert sim.get_cache_stats()["total_entries"] == 2
        assert sim.get_cached_response("https://example.com/a") is not None
        assert sim.get_cached_response("https://example.com/c") is not None

    def test_get_cache_stats(self):
        sim = CacheSimulator()
        sim.add_response("https://example.com/a", {"Cache-Control": "max-age=3600"})
        sim.add_response(
            "https://example.com/b",
            {"Cache-Control": "max-age=0", "ETag": "x"},
        )
        stats = sim.get_cache_stats()
        assert stats["total_entries"] == 2
        assert stats["max_entries"] == 1000

    def test_simulate_hard_refresh(self):
        sim = CacheSimulator()
        headers = sim.simulate_hard_refresh("https://example.com/page")
        assert headers["Cache-Control"] == "no-cache"
        assert headers["Pragma"] == "no-cache"

    def test_simulate_normal_refresh(self):
        sim = CacheSimulator()
        sim.add_response(
            "https://example.com/page",
            {"ETag": "abc", "Last-Modified": "Wed, 01 Jan 2024 00:00:00 GMT"},
        )
        headers = sim.simulate_normal_refresh("https://example.com/page")
        assert "If-None-Match" in headers
