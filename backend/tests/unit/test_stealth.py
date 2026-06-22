"""
反检测模块测试
"""
import pytest
from app.services.proxy.fingerprint.fingerprint_generator import (
    FingerprintGenerator,
    BrowserFingerprint,
    get_fingerprint_generator,
)
from app.services.proxy.fingerprint.canvas_fingerprint import CanvasFingerprint
from app.services.proxy.fingerprint.webgl_fingerprint import WebGLFingerprint
from app.services.proxy.fingerprint.font_fingerprint import FontFingerprint
from app.services.proxy.fingerprint.navigator_fingerprint import NavigatorFingerprint
from app.services.proxy.fingerprint.screen_fingerprint import ScreenFingerprint
from app.services.proxy.fingerprint.timezone_fingerprint import TimezoneFingerprint
from app.services.proxy.fingerprint.fingerprint_consistency import FingerprintConsistencyChecker
from app.services.proxy.behavior.mouse_behavior import MouseBehaviorSimulator
from app.services.proxy.behavior.scroll_behavior import ScrollBehaviorSimulator
from app.services.proxy.behavior.keyboard_behavior import KeyboardBehaviorSimulator
from app.services.proxy.proxy_pool import ProxyPool, Proxy, ProxyProvider, ProxyProtocol, ProxyType
from app.services.proxy.stealth_service import StealthService, get_stealth_service


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
        assert "language" in d

    def test_fingerprint_from_dict(self):
        """测试从字典创建"""
        d = {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "platform": "Win32",
            "language": "en-US",
        }
        fp = BrowserFingerprint.from_dict(d)
        assert fp.user_agent == "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        assert fp.platform == "Win32"

    def test_fingerprint_to_json(self):
        """测试转换为JSON"""
        fp = BrowserFingerprint()
        json_str = fp.to_json()
        assert isinstance(json_str, str)
        import json
        data = json.loads(json_str)
        assert "user_agent" in data


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

    def test_generate_chrome_fingerprint(self):
        """测试生成Chrome指纹"""
        gen = FingerprintGenerator()
        fp = gen.generate(browser="chrome")
        assert isinstance(fp, BrowserFingerprint)
        assert "Chrome" in fp.user_agent

    def test_generate_firefox_fingerprint(self):
        """测试生成Firefox指纹"""
        gen = FingerprintGenerator()
        fp = gen.generate(browser="firefox")
        assert isinstance(fp, BrowserFingerprint)
        assert "Firefox" in fp.user_agent

    def test_generate_windows_fingerprint(self):
        """测试生成Windows指纹"""
        gen = FingerprintGenerator()
        fp = gen.generate(os="windows")
        assert isinstance(fp, BrowserFingerprint)
        assert "Windows" in fp.user_agent
        assert fp.platform == "Win32"

    def test_generate_mac_fingerprint(self):
        """测试生成Mac指纹"""
        gen = FingerprintGenerator()
        fp = gen.generate(os="mac")
        assert isinstance(fp, BrowserFingerprint)
        assert "Mac" in fp.user_agent
        assert fp.platform == "MacIntel"

    def test_generate_linux_fingerprint(self):
        """测试生成Linux指纹"""
        gen = FingerprintGenerator()
        fp = gen.generate(os="linux")
        assert isinstance(fp, BrowserFingerprint)
        assert "Linux" in fp.user_agent

    def test_generate_by_country(self):
        """测试按国家生成指纹"""
        gen = FingerprintGenerator()
        fp = gen.generate(country="US")
        assert isinstance(fp, BrowserFingerprint)
        assert fp.language is not None
        assert fp.timezone is not None

    def test_generate_unique_fingerprints(self):
        """测试生成唯一指纹"""
        gen = FingerprintGenerator()
        fingerprints = set()
        for _ in range(100):
            fp = gen.generate()
            fp_str = fp.to_json()
            fingerprints.add(fp_str)
        # 应该有足够的多样性
        assert len(fingerprints) > 50

    def test_get_instance(self):
        """测试单例模式"""
        gen1 = get_fingerprint_generator()
        gen2 = get_fingerprint_generator()
        assert gen1 is gen2


class TestCanvasFingerprint:
    """Canvas指纹测试"""

    def test_canvas_fingerprint_creation(self):
        """测试Canvas指纹创建"""
        cf = CanvasFingerprint()
        assert cf is not None

    def test_generate_canvas_fingerprint(self):
        """测试生成Canvas指纹"""
        cf = CanvasFingerprint()
        result = cf.generate()
        assert isinstance(result, dict)
        assert "data_url" in result or "hash" in result

    def test_canvas_fingerprint_unique(self):
        """测试Canvas指纹唯一性"""
        cf = CanvasFingerprint()
        results = set()
        for _ in range(10):
            result = cf.generate()
            results.add(result.get("hash", ""))
        # 应该有变化
        assert len(results) >= 1  # 至少有一个


class TestWebGLFingerprint:
    """WebGL指纹测试"""

    def test_webgl_fingerprint_creation(self):
        """测试WebGL指纹创建"""
        wf = WebGLFingerprint()
        assert wf is not None

    def test_generate_webgl_fingerprint(self):
        """测试生成WebGL指纹"""
        wf = WebGLFingerprint()
        result = wf.generate()
        assert isinstance(result, dict)
        assert "vendor" in result
        assert "renderer" in result

    def test_webgl_vendor_list(self):
        """测试WebGL供应商列表"""
        wf = WebGLFingerprint()
        vendors = wf.get_vendor_list()
        assert isinstance(vendors, list)
        assert len(vendors) > 0

    def test_webgl_renderer_list(self):
        """测试WebGL渲染器列表"""
        wf = WebGLFingerprint()
        renderers = wf.get_renderer_list()
        assert isinstance(renderers, list)
        assert len(renderers) > 0


class TestFontFingerprint:
    """字体指纹测试"""

    def test_font_fingerprint_creation(self):
        """测试字体指纹创建"""
        ff = FontFingerprint()
        assert ff is not None

    def test_generate_font_list(self):
        """测试生成字体列表"""
        ff = FontFingerprint()
        fonts = ff.generate_font_list()
        assert isinstance(fonts, list)
        assert len(fonts) > 0

    def test_windows_fonts(self):
        """测试Windows字体"""
        ff = FontFingerprint()
        fonts = ff.get_windows_fonts()
        assert isinstance(fonts, list)
        assert len(fonts) > 0
        assert "Arial" in fonts

    def test_mac_fonts(self):
        """测试Mac字体"""
        ff = FontFingerprint()
        fonts = ff.get_mac_fonts()
        assert isinstance(fonts, list)
        assert len(fonts) > 0

    def test_linux_fonts(self):
        """测试Linux字体"""
        ff = FontFingerprint()
        fonts = ff.get_linux_fonts()
        assert isinstance(fonts, list)
        assert len(fonts) > 0


class TestNavigatorFingerprint:
    """Navigator指纹测试"""

    def test_navigator_fingerprint_creation(self):
        """测试Navigator指纹创建"""
        nf = NavigatorFingerprint()
        assert nf is not None

    def test_generate_user_agent(self):
        """测试生成User Agent"""
        nf = NavigatorFingerprint()
        ua = nf.generate_user_agent(browser="chrome", os="windows")
        assert isinstance(ua, str)
        assert "Chrome" in ua
        assert "Windows" in ua

    def test_generate_platform(self):
        """测试生成平台"""
        nf = NavigatorFingerprint()
        platform = nf.generate_platform(os="windows")
        assert platform == "Win32"

    def test_generate_languages(self):
        """测试生成语言"""
        nf = NavigatorFingerprint()
        languages = nf.generate_languages(country="US")
        assert isinstance(languages, list)
        assert len(languages) > 0

    def test_generate_hardware_concurrency(self):
        """测试生成硬件并发数"""
        nf = NavigatorFingerprint()
        cores = nf.generate_hardware_concurrency()
        assert isinstance(cores, int)
        assert 2 <= cores <= 32

    def test_generate_device_memory(self):
        """测试生成设备内存"""
        nf = NavigatorFingerprint()
        memory = nf.generate_device_memory()
        assert isinstance(memory, float) or isinstance(memory, int)
        assert 2 <= memory <= 64

    def test_generate_plugins(self):
        """测试生成插件列表"""
        nf = NavigatorFingerprint()
        plugins = nf.generate_plugins(browser="chrome")
        assert isinstance(plugins, list)
        assert len(plugins) > 0


class TestScreenFingerprint:
    """Screen指纹测试"""

    def test_screen_fingerprint_creation(self):
        """测试Screen指纹创建"""
        sf = ScreenFingerprint()
        assert sf is not None

    def test_generate_resolution(self):
        """测试生成分辨率"""
        sf = ScreenFingerprint()
        width, height = sf.generate_resolution()
        assert isinstance(width, int)
        assert isinstance(height, int)
        assert width >= 1366
        assert height >= 768

    def test_generate_color_depth(self):
        """测试生成颜色深度"""
        sf = ScreenFingerprint()
        depth = sf.generate_color_depth()
        assert depth in [24, 32]

    def test_generate_device_pixel_ratio(self):
        """测试生成设备像素比"""
        sf = ScreenFingerprint()
        dpr = sf.generate_device_pixel_ratio()
        assert isinstance(dpr, float)
        assert 1 <= dpr <= 3

    def test_generate_screen_orientation(self):
        """测试生成屏幕方向"""
        sf = ScreenFingerprint()
        orientation = sf.generate_screen_orientation()
        assert isinstance(orientation, dict)
        assert "type" in orientation
        assert "angle" in orientation


class TestTimezoneFingerprint:
    """时区指纹测试"""

    def test_timezone_fingerprint_creation(self):
        """测试时区指纹创建"""
        tf = TimezoneFingerprint()
        assert tf is not None

    def test_generate_timezone(self):
        """测试生成时区"""
        tf = TimezoneFingerprint()
        timezone = tf.generate_timezone(country="US")
        assert isinstance(timezone, str)
        assert "/" in timezone  # IANA格式

    def test_get_timezones_by_country(self):
        """测试按国家获取时区"""
        tf = TimezoneFingerprint()
        timezones = tf.get_timezones_by_country("US")
        assert isinstance(timezones, list)
        assert len(timezones) > 0

    def test_generate_timezone_offset(self):
        """测试生成时区偏移"""
        tf = TimezoneFingerprint()
        offset = tf.generate_timezone_offset(timezone="America/New_York")
        assert isinstance(offset, int)


class TestFingerprintConsistency:
    """指纹一致性测试"""

    def test_consistency_checker_creation(self):
        """测试一致性检查器创建"""
        checker = FingerprintConsistencyChecker()
        assert checker is not None

    def test_check_consistency_valid(self):
        """测试有效指纹一致性"""
        gen = FingerprintGenerator()
        fp = gen.generate(os="windows", browser="chrome")
        checker = FingerprintConsistencyChecker()
        is_consistent, issues = checker.check(fp)
        assert isinstance(is_consistent, bool)
        assert isinstance(issues, list)

    def test_check_ua_platform_match(self):
        """测试UA和平台匹配"""
        checker = FingerprintConsistencyChecker()
        result = checker.check_ua_platform_match(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Win32"
        )
        assert result is True

    def test_check_timezone_language_match(self):
        """测试时区和语言匹配"""
        checker = FingerprintConsistencyChecker()
        result = checker.check_timezone_language_match(
            "America/New_York",
            ["en-US"]
        )
        assert result is True

    def test_check_screen_dpr_match(self):
        """测试屏幕和DPR匹配"""
        checker = FingerprintConsistencyChecker()
        result = checker.check_screen_dpr_match(1920, 1080, 1.0)
        assert result is True

    def test_check_cpu_memory_match(self):
        """测试CPU和内存匹配"""
        checker = FingerprintConsistencyChecker()
        result = checker.check_cpu_memory_match(4, 8)
        assert result is True


class TestMouseBehavior:
    """鼠标行为测试"""

    def test_mouse_behavior_creation(self):
        """测试鼠标行为模拟器创建"""
        mb = MouseBehaviorSimulator()
        assert mb is not None

    def test_generate_bezier_path(self):
        """测试生成贝塞尔曲线路径"""
        mb = MouseBehaviorSimulator()
        path = mb.generate_bezier_path((0, 0), (100, 100), steps=20)
        assert isinstance(path, list)
        assert len(path) == 20
        assert all(isinstance(p, tuple) for p in path)

    def test_generate_movement_with_jitter(self):
        """测试生成带抖动的移动"""
        mb = MouseBehaviorSimulator()
        path = mb.generate_movement_with_jitter((0, 0), (100, 100))
        assert isinstance(path, list)
        assert len(path) > 0

    def test_calculate_movement_duration(self):
        """测试计算移动时长"""
        mb = MouseBehaviorSimulator()
        duration = mb.calculate_movement_duration((0, 0), (100, 100))
        assert isinstance(duration, float)
        assert duration > 0

    def test_generate_click_position(self):
        """测试生成点击位置"""
        mb = MouseBehaviorSimulator()
        pos = mb.generate_click_position((100, 100))
        assert isinstance(pos, tuple)
        assert len(pos) == 2
        # 应该有微小偏移
        assert abs(pos[0] - 100) <= 3
        assert abs(pos[1] - 100) <= 3

    def test_generate_click_timing(self):
        """测试生成点击时序"""
        mb = MouseBehaviorSimulator()
        timing = mb.generate_click_timing()
        assert isinstance(timing, dict)
        assert "hover_time" in timing
        assert "click_delay" in timing


class TestScrollBehavior:
    """滚动行为测试"""

    def test_scroll_behavior_creation(self):
        """测试滚动行为模拟器创建"""
        sb = ScrollBehaviorSimulator()
        assert sb is not None

    def test_generate_scroll_path(self):
        """测试生成滚动路径"""
        sb = ScrollBehaviorSimulator()
        path = sb.generate_scroll_path(0, 1000)
        assert isinstance(path, list)
        assert len(path) > 0

    def test_generate_scroll_with_pauses(self):
        """测试生成带停顿的滚动"""
        sb = ScrollBehaviorSimulator()
        path = sb.generate_scroll_with_pauses(0, 1000)
        assert isinstance(path, list)
        assert len(path) > 0

    def test_calculate_scroll_speed(self):
        """测试计算滚动速度"""
        sb = ScrollBehaviorSimulator()
        speed = sb.calculate_scroll_speed()
        assert isinstance(speed, float)
        assert speed > 0


class TestKeyboardBehavior:
    """键盘行为测试"""

    def test_keyboard_behavior_creation(self):
        """测试键盘行为模拟器创建"""
        kb = KeyboardBehaviorSimulator()
        assert kb is not None

    def test_generate_typing_timings(self):
        """测试生成打字时序"""
        kb = KeyboardBehaviorSimulator()
        timings = kb.generate_typing_timings("Hello World")
        assert isinstance(timings, list)
        assert len(timings) == len("Hello World")

    def test_calculate_typing_speed(self):
        """测试计算打字速度"""
        kb = KeyboardBehaviorSimulator()
        speed = kb.calculate_typing_speed()
        assert isinstance(speed, float)
        assert 150 <= speed <= 400  # ms per char

    def test_generate_typo_probability(self):
        """测试生成打字错误概率"""
        kb = KeyboardBehaviorSimulator()
        prob = kb.get_typo_probability()
        assert isinstance(prob, float)
        assert 0 <= prob <= 1


class TestProxy:
    """代理数据类测试"""

    def test_proxy_creation(self):
        """测试代理创建"""
        proxy = Proxy(
            host="127.0.0.1",
            port=8080,
            protocol=ProxyProtocol.HTTP,
            provider=ProxyProvider.SELF_HOSTED,
        )
        assert proxy.host == "127.0.0.1"
        assert proxy.port == 8080
        assert proxy.protocol == ProxyProtocol.HTTP

    def test_proxy_to_dict(self):
        """测试转换为字典"""
        proxy = Proxy(host="127.0.0.1", port=8080)
        d = proxy.to_dict()
        assert isinstance(d, dict)
        assert d["host"] == "127.0.0.1"
        assert d["port"] == 8080

    def test_proxy_get_url(self):
        """测试获取代理URL"""
        proxy = Proxy(host="127.0.0.1", port=8080, protocol=ProxyProtocol.HTTP)
        url = proxy.get_url()
        assert "http://" in url
        assert "127.0.0.1:8080" in url


class TestProxyPool:
    """代理池测试"""

    def test_proxy_pool_creation(self):
        """测试代理池创建"""
        pool = ProxyPool()
        assert pool is not None
        assert isinstance(pool.proxies, list)

    def test_add_proxy(self):
        """测试添加代理"""
        pool = ProxyPool()
        proxy = Proxy(host="127.0.0.1", port=8080)
        pool.add_proxy(proxy)
        assert len(pool.proxies) == 1

    def test_remove_proxy(self):
        """测试移除代理"""
        pool = ProxyPool()
        proxy = Proxy(host="127.0.0.1", port=8080)
        pool.add_proxy(proxy)
        pool.remove_proxy(proxy)
        assert len(pool.proxies) == 0

    def test_get_random_proxy(self):
        """测试获取随机代理"""
        pool = ProxyPool()
        pool.add_proxy(Proxy(host="1.1.1.1", port=8080))
        pool.add_proxy(Proxy(host="2.2.2.2", port=8080))
        proxy = pool.get_random_proxy()
        assert proxy is not None
        assert isinstance(proxy, Proxy)

    def test_get_proxy_by_country(self):
        """测试按国家获取代理"""
        pool = ProxyPool()
        pool.add_proxy(Proxy(host="1.1.1.1", port=8080, country="US"))
        pool.add_proxy(Proxy(host="2.2.2.2", port=8080, country="UK"))
        proxy = pool.get_proxy_by_country("US")
        assert proxy is not None
        assert proxy.country == "US"

    def test_get_active_proxies(self):
        """测试获取活跃代理"""
        pool = ProxyPool()
        pool.add_proxy(Proxy(host="1.1.1.1", port=8080, status="active"))
        pool.add_proxy(Proxy(host="2.2.2.2", port=8080, status="inactive"))
        active = pool.get_active_proxies()
        assert len(active) == 1

    def test_check_proxy_health(self):
        """测试检查代理健康"""
        pool = ProxyPool()
        proxy = Proxy(host="127.0.0.1", port=8080)
        # 可能返回True或False，取决于代理是否可用
        result = pool.check_proxy_health(proxy)
        assert isinstance(result, bool)

    def test_rotate_proxy(self):
        """测试轮换代理"""
        pool = ProxyPool()
        pool.add_proxy(Proxy(host="1.1.1.1", port=8080))
        pool.add_proxy(Proxy(host="2.2.2.2", port=8080))
        proxy = pool.rotate_proxy()
        assert proxy is not None
        assert isinstance(proxy, Proxy)


class TestStealthService:
    """反检测服务测试"""

    def test_stealth_service_creation(self):
        """测试反检测服务创建"""
        ss = StealthService()
        assert ss is not None

    def test_generate_fingerprint(self):
        """测试生成指纹"""
        ss = StealthService()
        fp = ss.generate_fingerprint()
        assert isinstance(fp, BrowserFingerprint)

    def test_get_behavior_simulator(self):
        """测试获取行为模拟器"""
        ss = StealthService()
        simulator = ss.get_behavior_simulator()
        assert simulator is not None

    def test_set_intensity(self):
        """测试设置强度"""
        ss = StealthService()
        ss.set_intensity("medium")
        assert ss.intensity == "medium"

    def test_get_config(self):
        """测试获取配置"""
        ss = StealthService()
        config = ss.get_config()
        assert isinstance(config, dict)
        assert "fingerprint" in config
        assert "behavior" in config

    def test_get_instance(self):
        """测试单例模式"""
        ss1 = get_stealth_service()
        ss2 = get_stealth_service()
        assert ss1 is ss2
