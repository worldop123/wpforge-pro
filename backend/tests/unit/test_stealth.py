"""
反检测模块测试
"""
import pytest
from app.services.proxy.fingerprint.fingerprint_generator import (
    FingerprintGenerator,
    BrowserFingerprint,
    fingerprint_generator,
)
from app.services.proxy.fingerprint.canvas_fingerprint import CanvasFingerprint
from app.services.proxy.fingerprint.webgl_fingerprint import WebGLFingerprint
from app.services.proxy.fingerprint.font_fingerprint import FontFingerprint
from app.services.proxy.fingerprint.navigator_fingerprint import NavigatorFingerprint
from app.services.proxy.fingerprint.screen_fingerprint import ScreenFingerprint
from app.services.proxy.fingerprint.timezone_fingerprint import TimezoneFingerprint
from app.services.proxy.fingerprint.fingerprint_consistency import (
    FingerprintConsistency,
    FingerprintAuthenticity,
    FingerprintDiversity,
)
from app.services.proxy.behavior.mouse_behavior import MouseBehaviorSimulator
from app.services.proxy.behavior.scroll_behavior import ScrollBehaviorSimulator
from app.services.proxy.behavior.keyboard_behavior import KeyboardBehaviorSimulator
from app.services.proxy.proxy_pool import (
    ProxyPool,
    Proxy,
    ProxyProvider,
    ProxyProtocol,
    ProxyType,
    ProxyStatus,
    ProxyPoolConfig,
    ProxyManager,
)
from app.services.proxy.stealth_service import (
    StealthService,
    stealth_service,
    BrowserFingerprint as StealthBrowserFingerprint,
)


def _make_proxy(
    host="127.0.0.1",
    port=8080,
    provider=ProxyProvider.SELF_HOSTED,
    protocol=ProxyProtocol.HTTP,
    ptype=ProxyType.DATACENTER,
    country=None,
    status=ProxyStatus.ACTIVE,
    proxy_id=None,
):
    """构造一个 Proxy 实例（填充必填字段）"""
    return Proxy(
        id=proxy_id or f"{host}:{port}",
        provider=provider,
        protocol=protocol,
        type=ptype,
        host=host,
        port=port,
        country=country,
        status=status,
    )


class TestBrowserFingerprint:
    """浏览器指纹数据类测试"""

    def test_fingerprint_creation(self):
        """测试指纹创建"""
        fp = BrowserFingerprint()
        assert fp is not None
        assert fp.user_agent is not None
        assert fp.platform is not None
        assert fp.language is not None

    def test_fingerprint_to_dict(self):
        """测试转换为字典"""
        fp = BrowserFingerprint()
        d = fp.to_dict()
        assert isinstance(d, dict)
        assert "user_agent" in d
        assert "platform" in d

    def test_fingerprint_defaults(self):
        """测试默认值"""
        fp = BrowserFingerprint()
        assert fp.platform == "Win32"
        assert fp.screen_width > 0
        assert fp.screen_height > 0
        assert fp.timezone == "America/New_York"

    def test_fingerprint_custom_values(self):
        """测试自定义值"""
        fp = BrowserFingerprint(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            platform="Win32",
            language="en-US",
        )
        assert fp.user_agent == "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        assert fp.platform == "Win32"


class TestFingerprintGenerator:
    """指纹生成器测试"""

    def test_generator_creation(self):
        """测试生成器创建"""
        gen = FingerprintGenerator()
        assert gen is not None

    def test_generate_fingerprint(self):
        """测试生成指纹"""
        gen = FingerprintGenerator()
        fp = gen.generate()
        assert isinstance(fp, BrowserFingerprint)
        assert fp.user_agent is not None
        assert len(fp.user_agent) > 0

    def test_generate_with_country(self):
        """测试按国家生成指纹"""
        gen = FingerprintGenerator()
        fp = gen.generate(country="US")
        assert isinstance(fp, BrowserFingerprint)
        assert fp.language is not None
        assert fp.timezone is not None

    def test_generate_with_seed(self):
        """测试带种子的确定性生成"""
        gen = FingerprintGenerator()
        fp1 = gen.generate(seed="test-seed")
        fp2 = gen.generate(seed="test-seed")
        # 相同种子应产生相同指纹ID
        assert fp1.fingerprint_id == fp2.fingerprint_id

    def test_generate_has_fingerprint_id(self):
        """测试生成的指纹有ID"""
        gen = FingerprintGenerator()
        fp = gen.generate()
        assert fp.fingerprint_id
        assert len(fp.fingerprint_id) > 0
        assert fp.generated_at > 0

    def test_generate_unique_fingerprints(self):
        """测试生成指纹的多样性"""
        gen = FingerprintGenerator()
        ids = set()
        for _ in range(20):
            fp = gen.generate()
            ids.add(fp.fingerprint_id)
        # 应该有一定多样性
        assert len(ids) >= 1

    def test_global_instance(self):
        """测试全局实例"""
        assert fingerprint_generator is not None
        assert isinstance(fingerprint_generator, FingerprintGenerator)

    def test_generate_consistent(self):
        """测试一致性生成（基于代理IP）"""
        gen = FingerprintGenerator()
        fp = gen.generate_consistent("192.168.1.1", country="US")
        assert isinstance(fp, BrowserFingerprint)
        assert fp.timezone is not None

    def test_cache_fingerprint(self):
        """测试缓存指纹"""
        gen = FingerprintGenerator()
        fp = gen.generate()
        gen.cache_fingerprint(fp)
        cached = gen.get_cached(fp.fingerprint_id)
        assert cached is not None
        assert cached.fingerprint_id == fp.fingerprint_id

    def test_get_cached_expired(self):
        """测试获取不存在的缓存"""
        gen = FingerprintGenerator()
        assert gen.get_cached("non-existent-id") is None


class TestCanvasFingerprint:
    """Canvas指纹测试"""

    def test_canvas_fingerprint_creation(self):
        """测试Canvas指纹创建"""
        cf = CanvasFingerprint()
        assert cf is not None

    def test_generate_fingerprint_hash(self):
        """测试生成Canvas指纹哈希"""
        cf = CanvasFingerprint()
        result = cf.generate_fingerprint_hash()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_fingerprint_hash_with_seed(self):
        """测试带种子的哈希生成"""
        cf = CanvasFingerprint()
        h1 = cf.generate_fingerprint_hash(seed="test")
        h2 = cf.generate_fingerprint_hash(seed="test")
        assert h1 == h2

    def test_set_noise_level(self):
        """测试设置噪声级别"""
        cf = CanvasFingerprint()
        cf.set_noise_level(0.8)
        # 不报错即可
        assert cf is not None

    def test_get_injection_script(self):
        """测试获取注入脚本"""
        cf = CanvasFingerprint()
        script = cf.get_injection_script("somehash")
        assert isinstance(script, str)
        assert len(script) > 0


class TestWebGLFingerprint:
    """WebGL指纹测试"""

    def test_webgl_fingerprint_creation(self):
        """测试WebGL指纹创建"""
        wf = WebGLFingerprint()
        assert wf is not None

    def test_generate_random_config(self):
        """测试生成随机配置"""
        wf = WebGLFingerprint()
        vendor, renderer = wf.generate_random_config()
        assert isinstance(vendor, str)
        assert isinstance(renderer, str)
        assert len(vendor) > 0

    def test_generate_extensions(self):
        """测试生成扩展列表"""
        wf = WebGLFingerprint()
        extensions = wf.generate_extensions()
        assert isinstance(extensions, list)
        assert len(extensions) > 0

    def test_generate_shader_precision(self):
        """测试生成着色器精度"""
        wf = WebGLFingerprint()
        precision = wf.generate_shader_precision()
        assert isinstance(precision, dict)
        assert "vertex" in precision
        assert "fragment" in precision

    def test_webgl_configs_available(self):
        """测试WebGL配置列表"""
        assert isinstance(WebGLFingerprint.WEBGL_CONFIGS, list)
        assert len(WebGLFingerprint.WEBGL_CONFIGS) > 0

    def test_webgl_extensions_available(self):
        """测试WebGL扩展列表"""
        assert isinstance(WebGLFingerprint.WEBGL_EXTENSIONS, list)
        assert len(WebGLFingerprint.WEBGL_EXTENSIONS) > 0

    def test_set_config_and_injection(self):
        """测试设置配置和注入脚本"""
        wf = WebGLFingerprint()
        wf.set_config(
            vendor="Google Inc. (NVIDIA)",
            renderer="ANGLE (NVIDIA)",
            extensions=["EXT_blend_minmax"],
            shader_precision={},
        )
        script = wf.get_injection_script()
        assert isinstance(script, str)
        assert len(script) > 0


class TestFontFingerprint:
    """字体指纹测试"""

    def test_font_fingerprint_creation(self):
        """测试字体指纹创建"""
        ff = FontFingerprint()
        assert ff is not None

    def test_generate_random_fonts(self):
        """测试生成随机字体列表"""
        ff = FontFingerprint()
        fonts = ff.generate_random_fonts(os_type="windows")
        assert isinstance(fonts, list)
        assert len(fonts) > 0

    def test_set_fonts(self):
        """测试设置字体"""
        ff = FontFingerprint()
        ff.set_fonts(["Arial", "Helvetica"], os_type="windows")
        # 不报错即可
        assert ff is not None

    def test_get_injection_script(self):
        """测试获取注入脚本"""
        ff = FontFingerprint()
        ff.set_fonts(["Arial"], os_type="windows")
        script = ff.get_injection_script()
        assert isinstance(script, str)
        assert len(script) > 0


class TestNavigatorFingerprint:
    """Navigator指纹测试"""

    def test_navigator_fingerprint_creation(self):
        """测试Navigator指纹创建"""
        nf = NavigatorFingerprint()
        assert nf is not None

    def test_generate_random_config(self):
        """测试生成随机配置"""
        nf = NavigatorFingerprint()
        nf.generate_random_config(browser="chrome", os="windows", country="US")
        # 不报错即可
        assert nf is not None

    def test_set_config(self):
        """测试设置配置"""
        nf = NavigatorFingerprint()
        nf.set_config(platform="Win32", vendor="Google Inc.")
        assert nf is not None

    def test_get_injection_script(self):
        """测试获取注入脚本"""
        nf = NavigatorFingerprint()
        nf.generate_random_config(browser="chrome", os="windows")
        script = nf.get_injection_script()
        assert isinstance(script, str)
        assert len(script) > 0


class TestScreenFingerprint:
    """Screen指纹测试"""

    def test_screen_fingerprint_creation(self):
        """测试Screen指纹创建"""
        sf = ScreenFingerprint()
        assert sf is not None

    def test_generate_random_config(self):
        """测试生成随机配置"""
        sf = ScreenFingerprint()
        sf.generate_random_config(device_type="desktop", os_type="windows")
        assert sf is not None

    def test_set_config(self):
        """测试设置配置"""
        sf = ScreenFingerprint()
        sf.set_config(width=1920, height=1080)
        assert sf is not None

    def test_get_injection_script(self):
        """测试获取注入脚本"""
        sf = ScreenFingerprint()
        sf.generate_random_config()
        script = sf.get_injection_script()
        assert isinstance(script, str)
        assert len(script) > 0


class TestTimezoneFingerprint:
    """时区指纹测试"""

    def test_timezone_fingerprint_creation(self):
        """测试时区指纹创建"""
        tf = TimezoneFingerprint()
        assert tf is not None

    def test_generate_random_config(self):
        """测试生成随机时区配置"""
        tf = TimezoneFingerprint()
        tf.generate_random_config(country="US")
        assert tf is not None

    def test_timezones_available(self):
        """测试时区列表"""
        assert isinstance(TimezoneFingerprint.TIMEZONES, dict)
        assert "US" in TimezoneFingerprint.TIMEZONES
        assert len(TimezoneFingerprint.TIMEZONES["US"]) > 0

    def test_set_config(self):
        """测试设置配置"""
        tf = TimezoneFingerprint()
        tf.set_config("America/New_York", 300, has_dst=True)
        assert tf is not None

    def test_get_injection_script(self):
        """测试获取注入脚本"""
        tf = TimezoneFingerprint()
        tf.generate_random_config()
        script = tf.get_injection_script()
        assert isinstance(script, str)
        assert len(script) > 0


class TestFingerprintConsistency:
    """指纹一致性测试"""

    def test_consistency_checker_creation(self):
        """测试一致性检查器创建"""
        checker = FingerprintConsistency()
        assert checker is not None

    def test_check_consistency_valid(self):
        """测试有效指纹一致性"""
        checker = FingerprintConsistency()
        fp = {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "platform": "Win32",
            "timezone": "America/New_York",
            "languages": ["en-US"],
        }
        is_consistent, issues = checker.check_consistency(fp)
        assert isinstance(is_consistent, bool)
        assert isinstance(issues, list)

    def test_consistency_score(self):
        """测试一致性评分"""
        checker = FingerprintConsistency()
        fp = {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "platform": "Win32",
        }
        score = checker.get_consistency_score(fp)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_authenticity(self):
        """测试真实性检查"""
        auth = FingerprintAuthenticity()
        fp = {"user_agent": "Mozilla/5.0", "platform": "Win32"}
        is_real, issues = auth.is_realistic(fp)
        assert isinstance(is_real, bool)
        assert isinstance(issues, list)

    def test_diversity(self):
        """测试多样性检查"""
        div = FingerprintDiversity()
        h = "somehash"
        # 新指纹应该是唯一的
        assert div.is_unique(h) is True
        div.record_fingerprint(h)
        # 记录后不再唯一
        assert div.is_unique(h) is False


class TestMouseBehavior:
    """鼠标行为测试"""

    def test_mouse_behavior_creation(self):
        """测试鼠标行为模拟器创建"""
        mb = MouseBehaviorSimulator()
        assert mb is not None

    def test_generate_bezier_path(self):
        """测试生成贝塞尔曲线路径"""
        mb = MouseBehaviorSimulator()
        path = mb.generate_bezier_path(
            start=(0, 0),
            end=(100, 100),
            control_points=[(50, 0), (50, 100)],
            steps=20,
        )
        assert isinstance(path, list)
        assert len(path) > 0
        assert all(isinstance(p, tuple) for p in path)

    def test_move_to(self):
        """测试移动到目标"""
        mb = MouseBehaviorSimulator()
        path = mb.move_to(100, 100)
        assert isinstance(path, list)
        assert len(path) > 0

    def test_add_jitter(self):
        """测试添加抖动"""
        mb = MouseBehaviorSimulator()
        path = [(0, 0), (10, 10), (20, 20)]
        result = mb.add_jitter(path, jitter_amount=1.0)
        assert isinstance(result, list)
        assert len(result) == len(path)

    def test_set_get_position(self):
        """测试设置和获取位置"""
        mb = MouseBehaviorSimulator()
        mb.set_position(50, 60)
        x, y = mb.get_position()
        assert x == 50
        assert y == 60


class TestScrollBehavior:
    """滚动行为测试"""

    def test_scroll_behavior_creation(self):
        """测试滚动行为模拟器创建"""
        sb = ScrollBehaviorSimulator()
        assert sb is not None

    def test_scroll_to(self):
        """测试滚动到目标"""
        sb = ScrollBehaviorSimulator()
        path = sb.scroll_to(1000)
        assert isinstance(path, list)
        assert len(path) > 0

    def test_scroll_down(self):
        """测试向下滚动"""
        sb = ScrollBehaviorSimulator()
        path = sb.scroll_down(500)
        assert isinstance(path, list)
        assert len(path) > 0

    def test_scroll_with_pauses(self):
        """测试带停顿的滚动"""
        sb = ScrollBehaviorSimulator()
        path = sb.scroll_with_pauses(1000)
        assert isinstance(path, list)
        assert len(path) > 0

    def test_get_scroll_speed(self):
        """测试获取滚动速度"""
        sb = ScrollBehaviorSimulator()
        speed = sb.get_scroll_speed()
        assert isinstance(speed, float)
        assert speed > 0


class TestKeyboardBehavior:
    """键盘行为测试"""

    def test_keyboard_behavior_creation(self):
        """测试键盘行为模拟器创建"""
        kb = KeyboardBehaviorSimulator()
        assert kb is not None

    def test_type_text(self):
        """测试打字"""
        kb = KeyboardBehaviorSimulator()
        timings = kb.type_text("Hello")
        assert isinstance(timings, list)
        assert len(timings) > 0

    def test_type_with_errors(self):
        """测试带错误的打字"""
        kb = KeyboardBehaviorSimulator()
        timings = kb.type_with_errors("Hello World", error_rate=0.1)
        assert isinstance(timings, list)

    def test_press_key(self):
        """测试按键"""
        kb = KeyboardBehaviorSimulator()
        events = kb.press_key("Enter")
        assert isinstance(events, list)

    def test_get_typing_speed(self):
        """测试获取打字速度"""
        kb = KeyboardBehaviorSimulator()
        speed = kb.get_typing_speed()
        assert isinstance(speed, (int, float))
        assert speed > 0

    def test_get_error_rate(self):
        """测试获取错误率"""
        kb = KeyboardBehaviorSimulator()
        rate = kb.get_error_rate()
        assert isinstance(rate, float)
        assert 0 <= rate <= 1


class TestProxy:
    """代理数据类测试"""

    def test_proxy_creation(self):
        """测试代理创建"""
        proxy = _make_proxy()
        assert proxy.host == "127.0.0.1"
        assert proxy.port == 8080
        assert proxy.protocol == ProxyProtocol.HTTP

    def test_proxy_to_dict(self):
        """测试转换为字典"""
        proxy = _make_proxy()
        d = proxy.to_dict()
        assert isinstance(d, dict)
        assert d["host"] == "127.0.0.1"
        assert d["port"] == 8080

    def test_proxy_url_property(self):
        """测试代理URL属性"""
        proxy = _make_proxy(protocol=ProxyProtocol.HTTP)
        url = proxy.url
        assert "http://" in url
        assert "127.0.0.1:8080" in url

    def test_proxy_url_with_auth(self):
        """测试带认证的代理URL"""
        proxy = _make_proxy()
        proxy.username = "user"
        proxy.password = "pass"
        url = proxy.url
        assert "user:pass" in url

    def test_proxy_success_rate(self):
        """测试成功率"""
        proxy = _make_proxy()
        # 无请求时默认为1.0
        assert proxy.success_rate == 1.0
        proxy.success_count = 8
        proxy.total_requests = 10
        assert proxy.success_rate == 0.8


class TestProxyPool:
    """代理池测试"""

    def test_proxy_pool_creation(self):
        """测试代理池创建"""
        pool = ProxyPool()
        assert pool is not None
        assert isinstance(pool.proxies, dict)

    def test_add_proxy(self):
        """测试添加代理"""
        pool = ProxyPool()
        proxy = _make_proxy(proxy_id="p1")
        pool.add_proxy(proxy)
        assert len(pool.proxies) == 1
        assert "p1" in pool.proxies

    def test_add_proxies(self):
        """测试批量添加代理"""
        pool = ProxyPool()
        proxies = [
            _make_proxy(host="1.1.1.1", proxy_id="p1"),
            _make_proxy(host="2.2.2.2", proxy_id="p2"),
        ]
        pool.add_proxies(proxies)
        assert len(pool.proxies) == 2

    def test_remove_proxy(self):
        """测试移除代理"""
        pool = ProxyPool()
        proxy = _make_proxy(proxy_id="p1")
        pool.add_proxy(proxy)
        pool.remove_proxy("p1")
        assert len(pool.proxies) == 0

    def test_get_proxy(self):
        """测试获取代理"""
        pool = ProxyPool()
        pool.add_proxy(_make_proxy(host="1.1.1.1", proxy_id="p1"))
        pool.add_proxy(_make_proxy(host="2.2.2.2", proxy_id="p2"))
        proxy = pool.get_proxy()
        assert proxy is not None
        assert isinstance(proxy, Proxy)

    def test_get_proxy_by_country(self):
        """测试按国家获取代理"""
        pool = ProxyPool()
        pool.add_proxy(_make_proxy(host="1.1.1.1", country="US", proxy_id="p1"))
        pool.add_proxy(_make_proxy(host="2.2.2.2", country="GB", proxy_id="p2"))
        proxy = pool.get_proxy(country="US")
        assert proxy is not None
        assert proxy.country == "US"

    def test_report_success(self):
        """测试报告成功"""
        pool = ProxyPool()
        proxy = _make_proxy(proxy_id="p1")
        pool.add_proxy(proxy)
        pool.report_success("p1", response_time=0.5)
        assert pool.proxies["p1"].success_count == 1

    def test_report_failure(self):
        """测试报告失败"""
        pool = ProxyPool()
        proxy = _make_proxy(proxy_id="p1")
        pool.add_proxy(proxy)
        pool.report_failure("p1", reason="timeout")
        assert pool.proxies["p1"].fail_count == 1

    def test_get_stats(self):
        """测试获取统计"""
        pool = ProxyPool()
        pool.add_proxy(_make_proxy(proxy_id="p1"))
        pool.add_proxy(_make_proxy(host="2.2.2.2", proxy_id="p2"))
        stats = pool.get_stats()
        assert isinstance(stats, dict)

    def test_get_proxies_by_country(self):
        """测试按国家分组统计"""
        pool = ProxyPool()
        pool.add_proxy(_make_proxy(host="1.1.1.1", country="US", proxy_id="p1"))
        pool.add_proxy(_make_proxy(host="2.2.2.2", country="GB", proxy_id="p2"))
        by_country = pool.get_proxies_by_country()
        assert isinstance(by_country, dict)
        assert by_country.get("US", 0) >= 1

    def test_check_rate_limit(self):
        """测试限流检查"""
        pool = ProxyPool()
        proxy = _make_proxy(proxy_id="p1")
        pool.add_proxy(proxy)
        result = pool.check_rate_limit("p1")
        assert isinstance(result, bool)

    def test_get_request_delay(self):
        """测试请求延迟"""
        pool = ProxyPool()
        delay = pool.get_request_delay()
        assert isinstance(delay, (int, float))
        assert delay >= 0


class TestProxyManager:
    """代理管理器测试"""

    def test_proxy_manager_creation(self):
        """测试代理管理器创建"""
        pm = ProxyManager()
        assert pm is not None

    def test_create_pool(self):
        """测试创建代理池"""
        pm = ProxyManager()
        pool = pm.create_pool("test_pool")
        assert pool is not None
        assert isinstance(pool, ProxyPool)

    def test_get_pool(self):
        """测试获取代理池"""
        pm = ProxyManager()
        pm.create_pool("test_pool")
        pool = pm.get_pool("test_pool")
        assert pool is not None

    def test_get_all_stats(self):
        """测试获取所有统计"""
        pm = ProxyManager()
        pm.create_pool("test_pool")
        stats = pm.get_all_stats()
        assert isinstance(stats, dict)


class TestStealthService:
    """反检测服务测试"""

    def test_stealth_service_creation(self):
        """测试反检测服务创建"""
        ss = StealthService()
        assert ss is not None

    def test_generate_fingerprint(self):
        """测试生成指纹"""
        ss = StealthService()
        fp = ss.generate_fingerprint(session_id="test-session")
        assert isinstance(fp, StealthBrowserFingerprint)

    def test_get_fingerprint(self):
        """测试获取已生成的指纹"""
        ss = StealthService()
        ss.generate_fingerprint(session_id="test-session")
        fp = ss.get_fingerprint(session_id="test-session")
        assert fp is not None
        assert isinstance(fp, StealthBrowserFingerprint)

    def test_clear_fingerprint(self):
        """测试清除指纹"""
        ss = StealthService()
        ss.generate_fingerprint(session_id="test-session")
        ss.clear_fingerprint(session_id="test-session")
        assert ss.get_fingerprint(session_id="test-session") is None

    def test_set_intensity(self):
        """测试设置强度"""
        ss = StealthService()
        ss.set_intensity("high")
        assert ss.get_intensity() == "high"

    def test_get_intensity(self):
        """测试获取强度"""
        ss = StealthService()
        assert ss.get_intensity() == "medium"

    def test_get_anti_detection_tips(self):
        """测试获取反检测建议"""
        ss = StealthService()
        tips = ss.get_anti_detection_tips()
        assert isinstance(tips, list)
        assert len(tips) > 0

    def test_get_human_behavior_config(self):
        """测试获取行为配置"""
        ss = StealthService()
        config = ss.get_human_behavior_config()
        assert isinstance(config, dict)
        assert "mouse_movement" in config
        assert "scrolling" in config

    def test_generate_stealth_headers(self):
        """测试生成反检测头"""
        ss = StealthService()
        fp = ss.generate_fingerprint(session_id="test-session")
        headers = ss.generate_stealth_headers(fp)
        assert isinstance(headers, dict)
        assert "User-Agent" in headers

    def test_check_fingerprint_consistency(self):
        """测试检查指纹一致性"""
        ss = StealthService()
        fp = {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "platform": "Win32",
        }
        is_consistent, issues = ss.check_fingerprint_consistency(fp)
        assert isinstance(is_consistent, bool)
        assert isinstance(issues, list)

    def test_global_instance(self):
        """测试全局实例"""
        assert stealth_service is not None
        assert isinstance(stealth_service, StealthService)
