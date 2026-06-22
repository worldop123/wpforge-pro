"""
主题配置生成器测试

对应 app/services/theme_config_generator.py 的实际实现。
ThemeConfigGenerator 没有 generate() 方法，主要 API：
- get_preset(preset) / get_all_presets() / get_preset_names()
- generate_from_analysis(site_analysis, industry, uniqueness)
- export_for_wordpress(config)
- generate_css_variables(config)
- compare_configs(c1, c2) / merge_configs(base, override)
- _shift_hue / _adjust_colors / _adjust_fonts (私有)
"""
import pytest
import json
from colorsys import rgb_to_hls, hls_to_rgb
from app.services.theme_config_generator import (
    ThemeConfigGenerator,
    ThemePreset,
    IndustryType,
    ThemeColors,
    ThemeTypography,
    ThemeLayout,
    ThemeButtons,
    ThemeHeader,
    ThemeFooter,
    ThemeConfig,
    get_theme_config_generator,
)


class TestThemeColors:
    """主题颜色测试"""

    def test_theme_colors_default(self):
        """测试默认颜色"""
        colors = ThemeColors()
        assert colors.primary is not None
        assert colors.secondary is not None
        assert colors.accent is not None
        assert colors.text is not None
        assert colors.background is not None

    def test_theme_colors_custom(self):
        """测试自定义颜色"""
        colors = ThemeColors(
            primary="#ff0000",
            secondary="#00ff00",
            accent="#0000ff",
            text="#333333",
            background="#ffffff"
        )
        assert colors.primary == "#ff0000"
        assert colors.secondary == "#00ff00"
        assert colors.accent == "#0000ff"

    def test_theme_colors_to_dict(self):
        """测试转换为字典"""
        colors = ThemeColors()
        d = colors.to_dict()
        assert isinstance(d, dict)
        assert "primary" in d
        assert "secondary" in d
        assert "accent" in d
        assert "text" in d
        assert "background" in d

    def test_theme_colors_all_fields(self):
        """测试所有颜色字段"""
        colors = ThemeColors()
        d = colors.to_dict()
        expected_keys = {"primary", "secondary", "accent", "text", "text_light",
                         "background", "background_alt", "border",
                         "success", "warning", "error", "info"}
        assert set(d.keys()) == expected_keys


class TestThemeTypography:
    """主题排版测试"""

    def test_theme_typography_default(self):
        """测试默认排版"""
        typo = ThemeTypography()
        assert typo.body_font is not None
        assert typo.heading_font is not None
        assert typo.base_font_size is not None
        assert typo.base_line_height > 0

    def test_theme_typography_custom(self):
        """测试自定义排版"""
        typo = ThemeTypography(
            body_font="Arial, sans-serif",
            heading_font="Georgia, serif",
            base_font_size="16px",
            base_line_height=1.8
        )
        assert typo.body_font == "Arial, sans-serif"
        assert typo.base_line_height == 1.8

    def test_theme_typography_to_dict(self):
        """测试转换为字典"""
        typo = ThemeTypography()
        d = typo.to_dict()
        assert isinstance(d, dict)
        assert "body_font" in d
        assert "heading_font" in d
        assert "base_font_size" in d


class TestThemeLayout:
    """主题布局测试"""

    def test_theme_layout_default(self):
        """测试默认布局"""
        layout = ThemeLayout()
        assert layout.container_width is not None
        assert layout.layout_style is not None
        assert layout.sidebar_position is not None

    def test_theme_layout_custom(self):
        """测试自定义布局"""
        layout = ThemeLayout(
            container_width="1400px",
            layout_style="wide",
            sidebar_position="left",
            sidebar_width="300px"
        )
        assert layout.container_width == "1400px"
        assert layout.layout_style == "wide"
        assert layout.sidebar_position == "left"

    def test_theme_layout_to_dict(self):
        """测试转换为字典"""
        layout = ThemeLayout()
        d = layout.to_dict()
        assert isinstance(d, dict)
        assert "container_width" in d
        assert "layout_style" in d


class TestThemeConfig:
    """主题配置测试"""

    def test_theme_config_default(self):
        """测试默认配置"""
        config = ThemeConfig()
        assert config.colors is not None
        assert config.typography is not None
        assert config.layout is not None
        assert config.header is not None
        assert config.footer is not None
        assert config.buttons is not None

    def test_theme_config_to_json(self):
        """测试转换为JSON"""
        config = ThemeConfig()
        json_str = config.to_json()
        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert "colors" in data
        assert "typography" in data
        assert "layout" in data

    def test_theme_config_from_json(self):
        """测试从JSON创建"""
        config = ThemeConfig()
        config.colors.primary = "#ff0000"
        json_str = config.to_json()
        new_config = ThemeConfig.from_json(json_str)
        assert new_config.colors.primary == "#ff0000"

    def test_theme_config_to_dict(self):
        """测试转换为字典"""
        config = ThemeConfig()
        d = config.to_dict()
        assert isinstance(d, dict)
        assert "colors" in d
        assert "typography" in d
        assert "layout" in d
        assert "header" in d
        assert "footer" in d

    def test_theme_config_from_json_roundtrip(self):
        """测试JSON往返转换"""
        config = ThemeConfig(name="Test Theme")
        config.colors.secondary = "#abcdef"
        json_str = config.to_json()
        new_config = ThemeConfig.from_json(json_str)
        assert new_config.name == "Test Theme"
        assert new_config.colors.secondary == "#abcdef"


class TestThemePreset:
    """主题预设测试"""

    def test_preset_values(self):
        """测试预设值"""
        assert hasattr(ThemePreset, 'MODERN_BLUE')
        assert hasattr(ThemePreset, 'ELEGANT_PURPLE')
        assert hasattr(ThemePreset, 'FRESH_GREEN')
        assert hasattr(ThemePreset, 'WARM_ORANGE')
        assert hasattr(ThemePreset, 'DARK_MODE')
        assert hasattr(ThemePreset, 'MINIMAL_BLACK')
        assert hasattr(ThemePreset, 'LUXURY_GOLD')
        assert hasattr(ThemePreset, 'TECH_NEON')

    def test_preset_count(self):
        """测试预设数量"""
        assert len(ThemePreset) >= 8

    def test_preset_is_string_enum(self):
        """测试预设是字符串枚举"""
        assert ThemePreset.MODERN_BLUE.value == "modern_blue"


class TestIndustryType:
    """行业类型测试"""

    def test_industry_values(self):
        """测试行业值"""
        assert hasattr(IndustryType, 'TECH')
        assert hasattr(IndustryType, 'FASHION')
        assert hasattr(IndustryType, 'HEALTH')
        assert hasattr(IndustryType, 'FOOD')
        assert hasattr(IndustryType, 'FINANCE')
        assert hasattr(IndustryType, 'EDUCATION')
        assert hasattr(IndustryType, 'BEAUTY')
        assert hasattr(IndustryType, 'FITNESS')
        assert hasattr(IndustryType, 'ECOMMERCE')
        assert hasattr(IndustryType, 'VAPE')
        assert hasattr(IndustryType, 'CANNABIS')
        assert hasattr(IndustryType, 'CORPORATE')

    def test_industry_count(self):
        """测试行业数量"""
        assert len(IndustryType) >= 12


class TestThemeConfigGenerator:
    """主题配置生成器测试"""

    def test_get_instance(self):
        """测试单例模式"""
        gen1 = get_theme_config_generator()
        gen2 = get_theme_config_generator()
        assert gen1 is gen2

    def test_generator_creation(self):
        """测试生成器创建"""
        gen = ThemeConfigGenerator()
        assert gen is not None

    def test_get_preset(self):
        """测试获取预设配置"""
        gen = get_theme_config_generator()
        config = gen.get_preset(ThemePreset.MODERN_BLUE)
        assert isinstance(config, ThemeConfig)
        assert config.colors.primary is not None

    def test_get_all_presets(self):
        """测试获取所有预设（返回字典）"""
        gen = get_theme_config_generator()
        presets = gen.get_all_presets()
        assert isinstance(presets, dict)
        assert len(presets) == len(ThemePreset)

    def test_get_preset_names(self):
        """测试获取所有预设名称"""
        gen = get_theme_config_generator()
        names = gen.get_preset_names()
        assert isinstance(names, list)
        assert len(names) == len(ThemePreset)
        assert "modern_blue" in names

    def test_get_preset_unknown(self):
        """测试获取未知预设返回默认配置"""
        gen = get_theme_config_generator()
        config = gen.get_preset(None)
        assert isinstance(config, ThemeConfig)

    def test_generate_from_analysis(self):
        """测试从分析结果生成配置"""
        gen = get_theme_config_generator()
        analysis = {
            "color_scheme": {
                "primary": "#2563eb",
                "secondary": "#3b82f6",
                "text": "#1e293b",
                "background": "#ffffff"
            },
            "font_scheme": {
                "body_font": "Inter, sans-serif",
                "heading_font": "Inter, sans-serif"
            },
            "layout_style": "boxed",
            "title": "Test Site"
        }
        config = gen.generate_from_analysis(analysis)
        assert isinstance(config, ThemeConfig)
        assert config.colors.primary is not None

    def test_generate_from_analysis_with_industry(self):
        """测试从分析结果生成配置（带行业）"""
        gen = get_theme_config_generator()
        analysis = {
            "color_scheme": {
                "primary": "#2563eb",
            },
        }
        config = gen.generate_from_analysis(analysis, industry=IndustryType.ECOMMERCE)
        assert isinstance(config, ThemeConfig)
        assert config.colors.primary is not None

    def test_generate_from_analysis_empty(self):
        """测试从空分析结果生成配置"""
        gen = get_theme_config_generator()
        config = gen.generate_from_analysis({})
        assert isinstance(config, ThemeConfig)

    def test_generate_css_variables(self):
        """测试生成CSS变量"""
        gen = get_theme_config_generator()
        config = gen.get_preset(ThemePreset.MODERN_BLUE)
        css = gen.generate_css_variables(config)
        assert isinstance(css, str)
        assert "--wpforge-color-primary" in css
        assert "--wpforge-color-secondary" in css

    def test_export_for_wordpress(self):
        """测试导出为WordPress格式"""
        gen = get_theme_config_generator()
        config = gen.get_preset(ThemePreset.MODERN_BLUE)
        wp_config = gen.export_for_wordpress(config)
        assert isinstance(wp_config, dict)
        assert "theme_mods" in wp_config
        assert "options" in wp_config
        assert "custom_css" in wp_config

    def test_compare_configs(self):
        """测试配置比较"""
        gen = get_theme_config_generator()
        config1 = gen.get_preset(ThemePreset.MODERN_BLUE)
        config2 = gen.get_preset(ThemePreset.WARM_ORANGE)
        diff = gen.compare_configs(config1, config2)
        assert isinstance(diff, dict)
        assert "colors" in diff
        assert len(diff["colors"]) > 0

    def test_compare_configs_same(self):
        """测试比较相同配置"""
        gen = get_theme_config_generator()
        config = gen.get_preset(ThemePreset.MODERN_BLUE)
        diff = gen.compare_configs(config, config)
        assert isinstance(diff, dict)
        assert len(diff["colors"]) == 0

    def test_merge_configs(self):
        """测试配置合并"""
        gen = get_theme_config_generator()
        base = gen.get_preset(ThemePreset.MODERN_BLUE)
        override = gen.get_preset(ThemePreset.WARM_ORANGE)
        merged = gen.merge_configs(base, override)
        assert isinstance(merged, ThemeConfig)

    def test_shift_hue(self):
        """测试色相调整（私有方法但可访问）"""
        gen = get_theme_config_generator()
        color = "#2563eb"
        adjusted = gen._shift_hue(color, 30)
        assert isinstance(adjusted, str)
        assert adjusted.startswith("#")
        assert len(adjusted) == 7

    def test_shift_hue_invalid(self):
        """测试无效颜色色相调整"""
        gen = get_theme_config_generator()
        adjusted = gen._shift_hue("invalid", 30)
        # 无效颜色应返回原值
        assert adjusted == "invalid"

    def test_all_presets_have_colors(self):
        """测试所有预设都有颜色配置"""
        gen = get_theme_config_generator()
        for preset in ThemePreset:
            config = gen.get_preset(preset)
            assert config.colors.primary is not None
            assert config.colors.secondary is not None
