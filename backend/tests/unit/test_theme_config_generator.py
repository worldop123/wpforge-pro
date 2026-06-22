"""
主题配置生成器测试
"""
import pytest
import json
from app.services.theme_config_generator import (
    ThemeConfigGenerator,
    ThemePreset,
    IndustryType,
    ThemeColors,
    ThemeTypography,
    ThemeLayout,
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

    def test_theme_colors_from_dict(self):
        """测试从字典创建"""
        d = {
            "primary": "#ff0000",
            "secondary": "#00ff00",
            "accent": "#0000ff",
            "text": "#333333",
            "background": "#ffffff"
        }
        colors = ThemeColors.from_dict(d)
        assert colors.primary == "#ff0000"
        assert colors.secondary == "#00ff00"


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
        json_str = config.to_json()
        new_config = ThemeConfig.from_json(json_str)
        assert new_config.colors.primary == config.colors.primary

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

    def test_theme_config_from_dict(self):
        """测试从字典创建"""
        d = {
            "colors": {
                "primary": "#ff0000",
                "secondary": "#00ff00"
            },
            "typography": {
                "body_font": "Arial, sans-serif"
            }
        }
        config = ThemeConfig.from_dict(d)
        assert config.colors.primary == "#ff0000"
        assert config.typography.body_font == "Arial, sans-serif"

    def test_theme_config_merge(self):
        """测试配置合并"""
        base = ThemeConfig()
        override = ThemeConfig()
        override.colors.primary = "#ff0000"
        merged = base.merge(override)
        assert merged.colors.primary == "#ff0000"


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

    def test_generate_default(self):
        """测试生成默认配置"""
        gen = get_theme_config_generator()
        config = gen.generate()
        assert isinstance(config, ThemeConfig)
        assert config.colors.primary is not None

    def test_generate_by_preset(self):
        """测试按预设生成"""
        gen = get_theme_config_generator()
        config = gen.generate(preset=ThemePreset.MODERN_BLUE)
        assert isinstance(config, ThemeConfig)
        assert config.colors.primary is not None

    def test_generate_by_industry(self):
        """测试按行业生成"""
        gen = get_theme_config_generator()
        config = gen.generate(industry=IndustryType.ECOMMERCE)
        assert isinstance(config, ThemeConfig)
        assert config.colors.primary is not None

    def test_generate_all_presets(self):
        """测试所有预设"""
        gen = get_theme_config_generator()
        for preset in ThemePreset:
            config = gen.generate(preset=preset)
            assert isinstance(config, ThemeConfig)
            assert config.colors.primary is not None

    def test_generate_all_industries(self):
        """测试所有行业"""
        gen = get_theme_config_generator()
        for industry in IndustryType:
            config = gen.generate(industry=industry)
            assert isinstance(config, ThemeConfig)
            assert config.colors.primary is not None

    def test_get_preset_config(self):
        """测试获取预设配置"""
        gen = get_theme_config_generator()
        config = gen.get_preset_config(ThemePreset.MODERN_BLUE)
        assert isinstance(config, ThemeConfig)

    def test_get_industry_config(self):
        """测试获取行业配置"""
        gen = get_theme_config_generator()
        config = gen.get_industry_config(IndustryType.ECOMMERCE)
        assert isinstance(config, ThemeConfig)

    def test_get_all_presets(self):
        """测试获取所有预设"""
        gen = get_theme_config_generator()
        presets = gen.get_all_presets()
        assert isinstance(presets, list)
        assert len(presets) == len(ThemePreset)

    def test_get_all_industries(self):
        """测试获取所有行业"""
        gen = get_theme_config_generator()
        industries = gen.get_all_industries()
        assert isinstance(industries, list)
        assert len(industries) == len(IndustryType)

    def test_analyze_website_colors(self):
        """测试分析网站颜色"""
        gen = get_theme_config_generator()
        # 模拟颜色分析
        colors = ["#2563eb", "#3b82f6", "#1e293b", "#ffffff"]
        result = gen.analyze_website_colors(colors)
        assert isinstance(result, ThemeColors)
        assert result.primary is not None

    def test_generate_from_analysis(self):
        """测试从分析结果生成"""
        gen = get_theme_config_generator()
        analysis = {
            "colors": {
                "primary": "#2563eb",
                "secondary": "#3b82f6",
                "text": "#1e293b",
                "background": "#ffffff"
            },
            "fonts": {
                "body": "Inter, sans-serif",
                "heading": "Inter, sans-serif"
            },
            "layout": {
                "style": "boxed",
                "sidebar": "right"
            }
        }
        config = gen.generate_from_analysis(analysis)
        assert isinstance(config, ThemeConfig)
        assert config.colors.primary == "#2563eb"

    def test_generate_css_variables(self):
        """测试生成CSS变量"""
        gen = get_theme_config_generator()
        config = gen.generate()
        css = gen.generate_css_variables(config)
        assert isinstance(css, str)
        assert "--wpforge-color-primary" in css
        assert "--wpforge-color-secondary" in css

    def test_generate_wordpress_options(self):
        """测试生成WordPress选项"""
        gen = get_theme_config_generator()
        config = gen.generate()
        options = gen.generate_wordpress_options(config)
        assert isinstance(options, dict)
        assert len(options) > 0

    def test_validate_config(self):
        """测试配置验证"""
        gen = get_theme_config_generator()
        config = gen.generate()
        is_valid, errors = gen.validate_config(config)
        assert is_valid
        assert len(errors) == 0

    def test_validate_config_invalid(self):
        """测试无效配置验证"""
        gen = get_theme_config_generator()
        config = ThemeConfig()
        config.colors.primary = "invalid"
        is_valid, errors = gen.validate_config(config)
        assert not is_valid or len(errors) > 0  # depends on validation strictness

    def test_compare_configs(self):
        """测试配置比较"""
        gen = get_theme_config_generator()
        config1 = gen.generate(preset=ThemePreset.MODERN_BLUE)
        config2 = gen.generate(preset=ThemePreset.WARM_ORANGE)
        diff = gen.compare_configs(config1, config2)
        assert isinstance(diff, dict)
        assert len(diff) > 0

    def test_adjust_hue(self):
        """测试色相调整"""
        gen = get_theme_config_generator()
        color = "#2563eb"
        adjusted = gen.adjust_hue(color, 30)
        assert isinstance(adjusted, str)
        assert adjusted.startswith("#")
        assert len(adjusted) == 7

    def test_adjust_lightness(self):
        """测试亮度调整"""
        gen = get_theme_config_generator()
        color = "#2563eb"
        adjusted = gen.adjust_lightness(color, 0.2)
        assert isinstance(adjusted, str)
        assert adjusted.startswith("#")

    def test_rgb_to_hls(self):
        """测试RGB转HLS"""
        gen = get_theme_config_generator()
        r, g, b = 37, 99, 235
        h, l, s = gen.rgb_to_hls(r, g, b)
        assert 0 <= h <= 360
        assert 0 <= l <= 1
        assert 0 <= s <= 1

    def test_hls_to_rgb(self):
        """测试HLS转RGB"""
        gen = get_theme_config_generator()
        h, l, s = 220, 0.5, 0.8
        r, g, b = gen.hls_to_rgb(h, l, s)
        assert 0 <= r <= 255
        assert 0 <= g <= 255
        assert 0 <= b <= 255

    def test_rgb_hls_roundtrip(self):
        """测试RGB-HLS往返转换"""
        gen = get_theme_config_generator()
        r, g, b = 37, 99, 235
        h, l, s = gen.rgb_to_hls(r, g, b)
        r2, g2, b2 = gen.hls_to_rgb(h, l, s)
        assert abs(r - r2) <= 1
        assert abs(g - g2) <= 1
        assert abs(b - b2) <= 1
