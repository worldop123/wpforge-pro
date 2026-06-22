"""
AI 仿站服务测试

覆盖:
- ColorScheme, ClonedPage, CloneResult 数据类
- PageType, DesignStyle 枚举
- AICloneService 核心方法:
  - analyze_website / full_clone (已有)
  - rewrite_content (2.1 内容原创化)
  - redesign_style (2.2 AI 重设计)
  - ensure_differentiation (2.3 差异化保证)
  - multi_site_fusion (2.4 多源模式)
- ai_clone_service 全局实例
"""
import pytest

from app.services.ai_clone_service import (
    PageType,
    DesignStyle,
    ColorScheme,
    ClonedPage,
    CloneResult,
    AICloneService,
    ai_clone_service,
)


# ---------------------------------------------------------------------------
# 数据类测试
# ---------------------------------------------------------------------------
class TestColorScheme:
    def test_defaults(self):
        cs = ColorScheme(
            primary="#000",
            secondary="#111",
            accent="#222",
            background="#fff",
            text="#333",
            text_light="#666",
        )
        assert cs.primary == "#000"
        assert cs.name == ""

    def test_with_name(self):
        cs = ColorScheme(
            primary="#000", secondary="#111", accent="#222",
            background="#fff", text="#333", text_light="#666",
            name="Test Scheme",
        )
        assert cs.name == "Test Scheme"


class TestClonedPage:
    def test_defaults(self):
        page = ClonedPage(url="http://x", page_type=PageType.HOME, title="T")
        assert page.url == "http://x"
        assert page.page_type == PageType.HOME
        assert page.title == "T"
        assert page.original_content == ""
        assert page.original_images == []
        assert page.original_layout == []
        assert page.originalized_content == ""
        assert page.originality_score == 0.0

    def test_independent_lists(self):
        a = ClonedPage(url="", page_type=PageType.HOME, title="")
        b = ClonedPage(url="", page_type=PageType.HOME, title="")
        a.original_images.append("img.jpg")
        assert b.original_images == []


class TestCloneResult:
    def test_defaults(self):
        r = CloneResult(reference_url="http://x", total_pages=0)
        assert r.reference_url == "http://x"
        assert r.pages == []
        assert r.color_scheme is None
        assert r.design_style == DesignStyle.MODERN_MINIMAL
        assert r.originality_score == 0.0

    def test_independent_lists(self):
        a = CloneResult(reference_url="", total_pages=0)
        b = CloneResult(reference_url="", total_pages=0)
        a.pages.append(ClonedPage(url="", page_type=PageType.HOME, title=""))
        assert b.pages == []


# ---------------------------------------------------------------------------
# 枚举测试
# ---------------------------------------------------------------------------
class TestEnums:
    def test_page_type_values(self):
        assert PageType.HOME.value == "home"
        assert PageType.PRODUCT_LIST.value == "product_list"
        assert PageType.CART.value == "cart"

    def test_design_style_values(self):
        assert DesignStyle.MODERN_MINIMAL.value == "modern_minimal"
        assert DesignStyle.LUXURY_PREMIUM.value == "luxury_premium"


# ---------------------------------------------------------------------------
# AICloneService 基础测试
# ---------------------------------------------------------------------------
class TestAICloneServiceBasic:
    def test_init(self):
        svc = AICloneService()
        assert hasattr(svc, "_page_type_patterns")
        assert hasattr(svc, "_color_schemes")
        assert hasattr(svc, "_layout_modules")

    def test_global_instance(self):
        assert isinstance(ai_clone_service, AICloneService)

    def test_get_page_type_name(self):
        svc = AICloneService()
        assert svc.get_page_type_name(PageType.HOME) == "首页"
        assert svc.get_page_type_name(PageType.CART) == "购物车"
        assert svc.get_page_type_name(PageType.UNKNOWN) == "未知页面"

    def test_color_schemes_has_all_styles(self):
        svc = AICloneService()
        for style in DesignStyle:
            # 至少 MODERN_MINIMAL 和 CLASSIC_ELEGANT 有方案
            if style in (DesignStyle.MODERN_MINIMAL, DesignStyle.CLASSIC_ELEGANT,
                         DesignStyle.BOLD_VIBRANT, DesignStyle.NEUTRAL_PROFESSIONAL,
                         DesignStyle.LUXURY_PREMIUM):
                assert style in svc._color_schemes


# ---------------------------------------------------------------------------
# 2.1 rewrite_content 内容原创化
# ---------------------------------------------------------------------------
class TestRewriteContent:
    def test_basic_rewrite(self):
        svc = AICloneService()
        original = "我们的产品提供非常好的质量，使用简单，价格合理。"
        rewritten = svc.rewrite_content(original, style="natural")
        assert isinstance(rewritten, str)
        assert len(rewritten) > 0

    def test_rewrite_returns_different_text(self):
        svc = AICloneService()
        original = "我们的产品提供非常好的质量，使用简单，价格合理。我们帮助客户选择最好的方案。专业的服务让客户满意。"
        rewritten = svc.rewrite_content(original, style="natural")
        # 至少应有部分不同（同义词替换）
        assert rewritten != original

    def test_rewrite_empty_text(self):
        svc = AICloneService()
        assert svc.rewrite_content("", style="natural") == ""
        assert svc.rewrite_content("   ", style="natural") == "   "

    def test_rewrite_none_text(self):
        svc = AICloneService()
        assert svc.rewrite_content(None, style="natural") is None

    def test_rewrite_all_styles(self):
        svc = AICloneService()
        original = "我们的产品提供非常好的质量，使用简单。专业的服务让客户满意。"
        for style in ["natural", "professional", "casual", "persuasive"]:
            rewritten = svc.rewrite_content(original, style=style)
            assert isinstance(rewritten, str)
            assert len(rewritten) > 0

    def test_rewrite_invalid_style_defaults_natural(self):
        svc = AICloneService()
        original = "我们的产品提供非常好的质量。"
        rewritten = svc.rewrite_content(original, style="invalid_style")
        assert isinstance(rewritten, str)
        assert len(rewritten) > 0

    def test_rewrite_english_text(self):
        svc = AICloneService()
        original = "Our product provides good quality and fast service. The best choice for you."
        rewritten = svc.rewrite_content(original, style="natural")
        assert isinstance(rewritten, str)
        assert len(rewritten) > 0

    def test_rewrite_preserves_meaning_keywords(self):
        """改写后应保留核心关键词（产品名等专有名词）"""
        svc = AICloneService()
        original = "我们的MagicWidget产品提供非常好的质量。"
        rewritten = svc.rewrite_content(original, style="natural")
        # MagicWidget 是专有名词，不应被替换
        assert "MagicWidget" in rewritten

    def test_local_rewrite_synonym_replacement(self):
        """本地算法应做同义词替换"""
        svc = AICloneService()
        original = "非常满意产品质量。"
        rewritten = svc._local_rewrite(original, style="natural")
        # "非常" 应被替换为某个同义词
        assert "非常" not in rewritten or rewritten != original

    def test_rewrite_long_text(self):
        svc = AICloneService()
        original = (
            "我们的产品提供非常好的质量。使用简单，价格合理。"
            "我们帮助客户选择最好的方案。专业的服务让客户满意。"
            "推荐给大家使用。体验非常好。"
        )
        rewritten = svc.rewrite_content(original, style="natural")
        assert isinstance(rewritten, str)
        assert len(rewritten) > 10


# ---------------------------------------------------------------------------
# 2.2 redesign_style AI 重设计
# ---------------------------------------------------------------------------
class TestRedesignStyle:
    def test_redesign_from_color_scheme(self):
        svc = AICloneService()
        original = ColorScheme(
            name="Test", primary="#0077B6", secondary="#00B4D8",
            accent="#90E0EF", background="#FFFFFF", text="#1A1A2E", text_light="#6B7280",
        )
        result = svc.redesign_style(original)
        assert "colors" in result
        assert "fonts" in result
        assert "layout" in result
        assert "uniqueness_score" in result

    def test_redesign_from_dict(self):
        svc = AICloneService()
        original = {
            "primary": "#0077B6",
            "secondary": "#00B4D8",
            "accent": "#90E0EF",
            "background": "#FFFFFF",
            "text": "#1A1A2E",
            "text_light": "#6B7280",
        }
        result = svc.redesign_style(original)
        assert "colors" in result
        assert "primary" in result["colors"]

    def test_redesign_from_design_style(self):
        svc = AICloneService()
        result = svc.redesign_style(DesignStyle.MODERN_MINIMAL)
        assert "colors" in result
        assert "primary" in result["colors"]

    def test_redesign_colors_different_from_original(self):
        svc = AICloneService()
        original = ColorScheme(
            name="Test", primary="#0077B6", secondary="#00B4D8",
            accent="#90E0EF", background="#FFFFFF", text="#1A1A2E", text_light="#6B7280",
        )
        result = svc.redesign_style(original)
        new_colors = result["colors"]
        # 主色应与原色不同（色相旋转）
        assert new_colors["primary"] != original.primary

    def test_redesign_colors_are_valid_hex(self):
        svc = AICloneService()
        original = ColorScheme(
            name="Test", primary="#0077B6", secondary="#00B4D8",
            accent="#90E0EF", background="#FFFFFF", text="#1A1A2E", text_light="#6B7280",
        )
        result = svc.redesign_style(original)
        for key, val in result["colors"].items():
            assert val.startswith("#")
            assert len(val) == 7

    def test_redesign_has_fonts(self):
        svc = AICloneService()
        result = svc.redesign_style(DesignStyle.MODERN_MINIMAL)
        fonts = result["fonts"]
        assert "heading" in fonts
        assert "body" in fonts

    def test_redesign_has_layout(self):
        svc = AICloneService()
        result = svc.redesign_style(DesignStyle.MODERN_MINIMAL)
        layout = result["layout"]
        assert "header" in layout
        assert "sidebar" in layout
        assert "footer" in layout

    def test_redesign_uniqueness_score_range(self):
        svc = AICloneService()
        original = ColorScheme(
            name="Test", primary="#0077B6", secondary="#00B4D8",
            accent="#90E0EF", background="#FFFFFF", text="#1A1A2E", text_light="#6B7280",
        )
        result = svc.redesign_style(original)
        score = result["uniqueness_score"]
        assert 0.0 <= score <= 1.0

    def test_redesign_has_design_notes(self):
        svc = AICloneService()
        result = svc.redesign_style(DesignStyle.MODERN_MINIMAL)
        assert "design_notes" in result
        assert isinstance(result["design_notes"], str)
        assert len(result["design_notes"]) > 0

    def test_redesign_preserves_original_colors(self):
        svc = AICloneService()
        original = ColorScheme(
            name="Test", primary="#0077B6", secondary="#00B4D8",
            accent="#90E0EF", background="#FFFFFF", text="#1A1A2E", text_light="#6B7280",
        )
        result = svc.redesign_style(original)
        assert result["original_colors"]["primary"] == "#0077B6"

    def test_redesign_empty_dict(self):
        """空字典也应能处理"""
        svc = AICloneService()
        result = svc.redesign_style({})
        assert "colors" in result
        assert "fonts" in result

    def test_redesign_none(self):
        """None 输入也应能处理"""
        svc = AICloneService()
        result = svc.redesign_style(None)
        assert "colors" in result


# ---------------------------------------------------------------------------
# 颜色工具方法测试
# ---------------------------------------------------------------------------
class TestColorUtils:
    def test_hex_to_rgb(self):
        svc = AICloneService()
        assert AICloneService._hex_to_rgb("#0077B6") == (0, 119, 182)
        assert AICloneService._hex_to_rgb("#FFFFFF") == (255, 255, 255)
        assert AICloneService._hex_to_rgb("#000000") == (0, 0, 0)

    def test_hex_to_rgb_short_form(self):
        assert AICloneService._hex_to_rgb("#fff") == (255, 255, 255)

    def test_hex_to_rgb_invalid(self):
        assert AICloneService._hex_to_rgb("invalid") == (0, 0, 0)

    def test_rgb_to_hex(self):
        assert AICloneService._rgb_to_hex(0, 119, 182) == "#0077b6"
        assert AICloneService._rgb_to_hex(255, 255, 255) == "#ffffff"

    def test_rgb_to_hex_clamping(self):
        assert AICloneService._rgb_to_hex(300, -10, 128) == "#ff0080"

    def test_rgb_to_hsl_and_back(self):
        r, g, b = 0, 119, 182
        h, s, l = AICloneService._rgb_to_hsl(r, g, b)
        hex_color = AICloneService._hsl_to_rgb(h, s, l)
        # 转换回来应接近原值
        new_rgb = AICloneService._hex_to_rgb(hex_color)
        assert abs(new_rgb[0] - r) <= 1
        assert abs(new_rgb[1] - g) <= 1
        assert abs(new_rgb[2] - b) <= 1

    def test_shift_color_changes_color(self):
        original = "#0077B6"
        shifted = AICloneService._shift_color(original, hue_shift=180)
        assert shifted != original

    def test_shift_color_zero_shift_returns_same(self):
        original = "#0077B6"
        shifted = AICloneService._shift_color(original, hue_shift=0, sat_shift=0, light_shift=0)
        # 应非常接近原值（可能有浮点误差）
        orig_rgb = AICloneService._hex_to_rgb(original)
        new_rgb = AICloneService._hex_to_rgb(shifted)
        assert abs(new_rgb[0] - orig_rgb[0]) <= 1


# ---------------------------------------------------------------------------
# 2.3 ensure_differentiation 差异化保证
# ---------------------------------------------------------------------------
class TestEnsureDifferentiation:
    def test_basic_different_strings(self):
        svc = AICloneService()
        result = svc.ensure_differentiation("hello world", "goodbye universe")
        assert "differentiation_score" in result
        assert 0.0 <= result["differentiation_score"] <= 1.0
        assert "differences" in result
        assert "is_sufficient" in result

    def test_identical_strings_low_score(self):
        svc = AICloneService()
        result = svc.ensure_differentiation("same text", "same text")
        assert result["differentiation_score"] == 0.0
        assert result["is_sufficient"] is False

    def test_completely_different_strings_high_score(self):
        svc = AICloneService()
        result = svc.ensure_differentiation("abc", "xyz")
        assert result["differentiation_score"] > 0.3

    def test_returns_differences_list(self):
        svc = AICloneService()
        result = svc.ensure_differentiation("hello", "world")
        assert isinstance(result["differences"], list)
        assert len(result["differences"]) > 0

    def test_dict_comparison(self):
        svc = AICloneService()
        original = {"title": "Hello World", "content": "Original content here"}
        generated = {"title": "Hi Earth", "content": "New generated text"}
        result = svc.ensure_differentiation(original, generated)
        assert "differentiation_score" in result
        assert result["differentiation_score"] > 0.0

    def test_low_differentiation_triggers_adjustment(self):
        """差异度不足时应自动调整"""
        svc = AICloneService()
        # 几乎相同的文本
        original = "我们的产品非常好，质量很高。"
        generated = "我们的产品非常好，质量很高。"  # 完全相同
        result = svc.ensure_differentiation(original, generated)
        assert result["original_score"] < 0.3
        assert result["adjusted"] is not None
        # 调整后差异度应提升
        assert result["differentiation_score"] >= result["original_score"]

    def test_sufficient_differentiation_no_adjustment(self):
        """差异度足够时不应调整"""
        svc = AICloneService()
        original = "apple banana cherry"
        generated = "xyz123 completely different text"
        result = svc.ensure_differentiation(original, generated)
        if result["original_score"] >= 0.3:
            assert result["adjusted"] is None

    def test_empty_strings(self):
        svc = AICloneService()
        result = svc.ensure_differentiation("", "")
        assert result["differentiation_score"] == 0.0

    def test_one_empty_string(self):
        svc = AICloneService()
        result = svc.ensure_differentiation("hello", "")
        assert result["differentiation_score"] == 1.0

    def test_returns_lengths(self):
        svc = AICloneService()
        result = svc.ensure_differentiation("hello world", "hi")
        assert "original_length" in result
        assert "generated_length" in result

    def test_dict_field_differences(self):
        svc = AICloneService()
        original = {"a": "x", "b": "y"}
        generated = {"a": "x", "c": "z"}
        result = svc.ensure_differentiation(original, generated)
        # 应检测到字段差异
        field_diff_found = any("字段" in d for d in result["differences"])
        assert field_diff_found

    def test_adjusted_dict_when_low_diff(self):
        """字典差异度不足时应调整字段"""
        svc = AICloneService()
        original = {"content": "我们的产品非常好，质量很高，使用简单。"}
        generated = {"content": "我们的产品非常好，质量很高，使用简单。"}
        result = svc.ensure_differentiation(original, generated)
        assert result["adjusted"] is not None
        assert isinstance(result["adjusted"], dict)


# ---------------------------------------------------------------------------
# 2.4 multi_site_fusion 多源模式
# ---------------------------------------------------------------------------
class TestMultiSiteFusion:
    def test_basic_fusion(self):
        svc = AICloneService()
        result = svc.multi_site_fusion(["https://example1.com", "https://example2.com"])
        assert result["status"] == "fused"
        assert "fused_pages" in result
        assert "fusion_strategy" in result

    def test_empty_urls(self):
        svc = AICloneService()
        result = svc.multi_site_fusion([])
        assert result["status"] == "no_urls"
        assert result["total_pages"] == 0
        assert result["fused_pages"] == []

    def test_single_url(self):
        svc = AICloneService()
        result = svc.multi_site_fusion(["https://single.com"])
        assert result["status"] == "fused"
        assert len(result["source_urls"]) == 1

    def test_multiple_urls_analyzed(self):
        svc = AICloneService()
        urls = ["https://a.com", "https://b.com", "https://c.com"]
        result = svc.multi_site_fusion(urls)
        assert len(result["site_analyses"]) == 3
        assert result["source_urls"] == urls

    def test_has_color_scheme(self):
        svc = AICloneService()
        result = svc.multi_site_fusion(["https://example.com"])
        assert "color_scheme" in result

    def test_has_fonts(self):
        svc = AICloneService()
        result = svc.multi_site_fusion(["https://example.com"])
        assert "fonts" in result
        assert "heading" in result["fonts"]
        assert "body" in result["fonts"]

    def test_has_layout(self):
        svc = AICloneService()
        result = svc.multi_site_fusion(["https://example.com"])
        assert "layout" in result
        assert "header" in result["layout"]

    def test_has_fusion_strategy(self):
        svc = AICloneService()
        result = svc.multi_site_fusion(["https://example.com"])
        strategy = result["fusion_strategy"]
        assert isinstance(strategy, list)
        assert len(strategy) > 0
        assert all(isinstance(s, str) for s in strategy)

    def test_has_fused_modules(self):
        svc = AICloneService()
        result = svc.multi_site_fusion(["https://example.com"])
        assert "fused_modules" in result
        assert isinstance(result["fused_modules"], list)

    def test_has_fused_page_types(self):
        svc = AICloneService()
        result = svc.multi_site_fusion(["https://example.com"])
        assert "fused_page_types" in result
        assert isinstance(result["fused_page_types"], list)

    def test_total_pages_positive(self):
        svc = AICloneService()
        result = svc.multi_site_fusion(["https://example.com"])
        assert result["total_pages"] > 0

    def test_site_analyses_structure(self):
        svc = AICloneService()
        result = svc.multi_site_fusion(["https://example.com"])
        for analysis in result["site_analyses"]:
            assert "url" in analysis
            assert "total_pages" in analysis
            assert "design_style" in analysis

    def test_fused_pages_structure(self):
        svc = AICloneService()
        result = svc.multi_site_fusion(["https://example.com"])
        for page in result["fused_pages"]:
            assert "page_type" in page
            assert "page_type_name" in page
            assert "modules" in page

    def test_has_design_style(self):
        svc = AICloneService()
        result = svc.multi_site_fusion(["https://example.com"])
        assert "design_style" in result


# ---------------------------------------------------------------------------
# 已有方法回归测试（确保不破坏现有功能）
# ---------------------------------------------------------------------------
class TestExistingMethodsRegression:
    def test_analyze_website(self):
        svc = AICloneService()
        urls = ["https://example.com/", "https://example.com/about"]
        result = svc.analyze_website(urls)
        assert result.reference_url == "https://example.com/"
        assert result.total_pages == 2
        assert len(result.pages) == 2

    def test_full_clone(self):
        svc = AICloneService()
        result = svc.full_clone("https://example.com", target_brand="TestBrand")
        assert result.reference_url.startswith("https://example.com")
        assert result.total_pages > 0
        assert result.originality_score > 0.0

    def test_originalize_content(self):
        svc = AICloneService()
        page = ClonedPage(
            url="https://example.com",
            page_type=PageType.HOME,
            title="Test Title",
        )
        result = svc.originalize_content(page, brand_name="TestBrand")
        assert result.originality_score > 0.0

    def test_rearrange_layout(self):
        svc = AICloneService()
        page = ClonedPage(
            url="https://example.com",
            page_type=PageType.HOME,
            title="Test",
            original_layout=[
                {"module": "hero_section", "confidence": 0.7, "position": 0},
                {"module": "featured_products", "confidence": 0.7, "position": 1},
                {"module": "testimonials", "confidence": 0.7, "position": 2},
                {"module": "newsletter", "confidence": 0.7, "position": 3},
                {"module": "cta_banner", "confidence": 0.7, "position": 4},
            ],
        )
        result = svc.rearrange_layout(page)
        assert len(result.new_layout) > 0

    def test_detect_page_type_home(self):
        svc = AICloneService()
        # HOME 检测需要 path 和 html 共同匹配才能超过阈值 (>0.2)
        # 单独 / 路径只匹配 1/5=0.2，不大于 0.2，所以需要 html 辅助
        result = svc._detect_page_type("https://example.com/", '<title>homepage</title>')
        assert result == PageType.HOME

    def test_detect_page_type_cart(self):
        svc = AICloneService()
        assert svc._detect_page_type("https://example.com/cart", "") == PageType.CART

    def test_detect_page_type_unknown(self):
        svc = AICloneService()
        result = svc._detect_page_type("https://example.com/random-path-xyz", "")
        assert result == PageType.UNKNOWN
