"""
主题配置生成器
根据目标网站分析结果自动生成WPForge Theme配置
"""
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import random
from urllib.parse import urlparse
from colorsys import rgb_to_hls, hls_to_rgb


class ThemePreset(str, Enum):
    """主题预设"""
    MODERN_BLUE = "modern_blue"
    ELEGANT_PURPLE = "elegant_purple"
    FRESH_GREEN = "fresh_green"
    WARM_ORANGE = "warm_orange"
    DARK_MODE = "dark_mode"
    MINIMAL_BLACK = "minimal_black"
    LUXURY_GOLD = "luxury_gold"
    TECH_NEON = "tech_neon"


class IndustryType(str, Enum):
    """行业类型"""
    TECH = "tech"
    FASHION = "fashion"
    HEALTH = "health"
    FOOD = "food"
    FINANCE = "finance"
    EDUCATION = "education"
    BEAUTY = "beauty"
    FITNESS = "fitness"
    ECOMMERCE = "ecommerce"
    VAPE = "vape"
    CANNABIS = "cannabis"
    CORPORATE = "corporate"


@dataclass
class ThemeColors:
    """主题颜色"""
    primary: str = "#2563eb"
    secondary: str = "#3b82f6"
    accent: str = "#06b6d4"
    text: str = "#1e293b"
    text_light: str = "#64748b"
    background: str = "#ffffff"
    background_alt: str = "#f8fafc"
    border: str = "#e2e8f0"
    success: str = "#10b981"
    warning: str = "#f59e0b"
    error: str = "#ef4444"
    info: str = "#3b82f6"

    def to_dict(self) -> Dict[str, str]:
        return {
            "primary": self.primary,
            "secondary": self.secondary,
            "accent": self.accent,
            "text": self.text,
            "text_light": self.text_light,
            "background": self.background,
            "background_alt": self.background_alt,
            "border": self.border,
            "success": self.success,
            "warning": self.warning,
            "error": self.error,
            "info": self.info,
        }


@dataclass
class ThemeTypography:
    """主题排版"""
    body_font: str = "Inter, system-ui, -apple-system, sans-serif"
    heading_font: str = "Inter, system-ui, -apple-system, sans-serif"
    base_font_size: str = "16px"
    base_line_height: float = 1.6
    heading_line_height: float = 1.2
    font_weight_normal: int = 400
    font_weight_medium: int = 500
    font_weight_bold: int = 700

    def to_dict(self) -> Dict[str, Any]:
        return {
            "body_font": self.body_font,
            "heading_font": self.heading_font,
            "base_font_size": self.base_font_size,
            "base_line_height": self.base_line_height,
            "heading_line_height": self.heading_line_height,
            "font_weight_normal": self.font_weight_normal,
            "font_weight_medium": self.font_weight_medium,
            "font_weight_bold": self.font_weight_bold,
        }


@dataclass
class ThemeLayout:
    """主题布局"""
    container_width: str = "1200px"
    content_width: str = "800px"
    sidebar_width: str = "300px"
    gutter: str = "30px"
    header_height: str = "80px"
    footer_height: str = "auto"
    layout_style: str = "boxed"  # boxed, full-width, contained
    sidebar_position: str = "right"  # left, right, none

    def to_dict(self) -> Dict[str, str]:
        return {
            "container_width": self.container_width,
            "content_width": self.content_width,
            "sidebar_width": self.sidebar_width,
            "gutter": self.gutter,
            "header_height": self.header_height,
            "footer_height": self.footer_height,
            "layout_style": self.layout_style,
            "sidebar_position": self.sidebar_position,
        }


@dataclass
class ThemeButtons:
    """主题按钮"""
    border_radius: str = "6px"
    padding: str = "12px 24px"
    font_size: str = "16px"
    font_weight: int = 500
    text_transform: str = "none"  # none, uppercase, lowercase, capitalize

    def to_dict(self) -> Dict[str, Any]:
        return {
            "border_radius": self.border_radius,
            "padding": self.padding,
            "font_size": self.font_size,
            "font_weight": self.font_weight,
            "text_transform": self.text_transform,
        }


@dataclass
class ThemeHeader:
    """主题头部"""
    layout: str = "default"  # default, centered, inline, stacked
    height: str = "80px"
    sticky: bool = True
    transparent: bool = False
    show_search: bool = True
    show_cart: bool = True
    show_account: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layout": self.layout,
            "height": self.height,
            "sticky": self.sticky,
            "transparent": self.transparent,
            "show_search": self.show_search,
            "show_cart": self.show_cart,
            "show_account": self.show_account,
        }


@dataclass
class ThemeFooter:
    """主题底部"""
    widget_columns: int = 4
    show_footer_bar: bool = True
    show_back_to_top: bool = True
    copyright_text: str = ""
    show_social_icons: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "widget_columns": self.widget_columns,
            "show_footer_bar": self.show_footer_bar,
            "show_back_to_top": self.show_back_to_top,
            "copyright_text": self.copyright_text,
            "show_social_icons": self.show_social_icons,
        }


@dataclass
class ThemeBlog:
    """主题博客设置"""
    archive_layout: str = "grid"  # grid, list, masonry
    archive_columns: int = 3
    show_featured_image: bool = True
    show_date: bool = True
    show_author: bool = True
    show_categories: bool = True
    show_tags: bool = True
    show_comments: bool = True
    excerpt_length: int = 30

    def to_dict(self) -> Dict[str, Any]:
        return {
            "archive_layout": self.archive_layout,
            "archive_columns": self.archive_columns,
            "show_featured_image": self.show_featured_image,
            "show_date": self.show_date,
            "show_author": self.show_author,
            "show_categories": self.show_categories,
            "show_tags": self.show_tags,
            "show_comments": self.show_comments,
            "excerpt_length": self.excerpt_length,
        }


@dataclass
class ThemeWooCommerce:
    """主题WooCommerce设置"""
    product_columns: int = 4
    product_per_page: int = 12
    show_quick_view: bool = True
    show_wishlist: bool = True
    show_compare: bool = False
    ajax_add_to_cart: bool = True
    catalog_mode: bool = False
    show_sku: bool = False
    show_categories: bool = True
    show_tags: bool = True
    show_related_products: bool = True
    related_products_count: int = 4

    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_columns": self.product_columns,
            "product_per_page": self.product_per_page,
            "show_quick_view": self.show_quick_view,
            "show_wishlist": self.show_wishlist,
            "show_compare": self.show_compare,
            "ajax_add_to_cart": self.ajax_add_to_cart,
            "catalog_mode": self.catalog_mode,
            "show_sku": self.show_sku,
            "show_categories": self.show_categories,
            "show_tags": self.show_tags,
            "show_related_products": self.show_related_products,
            "related_products_count": self.related_products_count,
        }


@dataclass
class ThemeSEO:
    """主题SEO设置"""
    auto_title: bool = True
    auto_description: bool = True
    auto_keywords: bool = True
    schema_markup: bool = True
    open_graph: bool = True
    twitter_cards: bool = True
    breadcrumbs: bool = True
    canonical_urls: bool = True
    prev_next_links: bool = True

    def to_dict(self) -> Dict[str, bool]:
        return {
            "auto_title": self.auto_title,
            "auto_description": self.auto_description,
            "auto_keywords": self.auto_keywords,
            "schema_markup": self.schema_markup,
            "open_graph": self.open_graph,
            "twitter_cards": self.twitter_cards,
            "breadcrumbs": self.breadcrumbs,
            "canonical_urls": self.canonical_urls,
            "prev_next_links": self.prev_next_links,
        }


@dataclass
class ThemePerformance:
    """主题性能设置"""
    css_minify: bool = True
    css_combine: bool = True
    css_inline_critical: bool = True
    js_defer: bool = True
    js_delay: bool = False
    image_lazy_load: bool = True
    image_webp: bool = True
    font_display_swap: bool = True
    disable_emoji: bool = True
    disable_embeds: bool = True
    disable_xmlrpc: bool = True
    remove_wp_version: bool = True

    def to_dict(self) -> Dict[str, bool]:
        return {
            "css_minify": self.css_minify,
            "css_combine": self.css_combine,
            "css_inline_critical": self.css_inline_critical,
            "js_defer": self.js_defer,
            "js_delay": self.js_delay,
            "image_lazy_load": self.image_lazy_load,
            "image_webp": self.image_webp,
            "font_display_swap": self.font_display_swap,
            "disable_emoji": self.disable_emoji,
            "disable_embeds": self.disable_embeds,
            "disable_xmlrpc": self.disable_xmlrpc,
            "remove_wp_version": self.remove_wp_version,
        }


@dataclass
class ThemeConfig:
    """完整主题配置"""
    name: str = "WPForge Theme"
    version: str = "1.0.0"
    
    colors: ThemeColors = field(default_factory=ThemeColors)
    typography: ThemeTypography = field(default_factory=ThemeTypography)
    layout: ThemeLayout = field(default_factory=ThemeLayout)
    buttons: ThemeButtons = field(default_factory=ThemeButtons)
    header: ThemeHeader = field(default_factory=ThemeHeader)
    footer: ThemeFooter = field(default_factory=ThemeFooter)
    blog: ThemeBlog = field(default_factory=ThemeBlog)
    woocommerce: ThemeWooCommerce = field(default_factory=ThemeWooCommerce)
    seo: ThemeSEO = field(default_factory=ThemeSEO)
    performance: ThemePerformance = field(default_factory=ThemePerformance)
    
    # 自定义CSS/JS
    custom_css: str = ""
    custom_js: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "colors": self.colors.to_dict(),
            "typography": self.typography.to_dict(),
            "layout": self.layout.to_dict(),
            "buttons": self.buttons.to_dict(),
            "header": self.header.to_dict(),
            "footer": self.footer.to_dict(),
            "blog": self.blog.to_dict(),
            "woocommerce": self.woocommerce.to_dict(),
            "seo": self.seo.to_dict(),
            "performance": self.performance.to_dict(),
            "custom_css": self.custom_css,
            "custom_js": self.custom_js,
        }
    
    def to_json(self) -> str:
        """导出为JSON"""
        import json
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> "ThemeConfig":
        """从JSON导入"""
        import json
        data = json.loads(json_str)
        config = cls()
        
        if "colors" in data:
            config.colors = ThemeColors(**data["colors"])
        if "typography" in data:
            config.typography = ThemeTypography(**data["typography"])
        if "layout" in data:
            config.layout = ThemeLayout(**data["layout"])
        if "buttons" in data:
            config.buttons = ThemeButtons(**data["buttons"])
        if "header" in data:
            config.header = ThemeHeader(**data["header"])
        if "footer" in data:
            config.footer = ThemeFooter(**data["footer"])
        if "blog" in data:
            config.blog = ThemeBlog(**data["blog"])
        if "woocommerce" in data:
            config.woocommerce = ThemeWooCommerce(**data["woocommerce"])
        if "seo" in data:
            config.seo = ThemeSEO(**data["seo"])
        if "performance" in data:
            config.performance = ThemePerformance(**data["performance"])
        if "name" in data:
            config.name = data["name"]
        if "custom_css" in data:
            config.custom_css = data["custom_css"]
        if "custom_js" in data:
            config.custom_js = data["custom_js"]
        
        return config


class ThemeConfigGenerator:
    """
    主题配置生成器
    根据目标网站分析结果自动生成主题配置
    """
    
    def __init__(self):
        self._presets = self._init_presets()
        self._industry_defaults = self._init_industry_defaults()
    
    def _init_presets(self) -> Dict[ThemePreset, ThemeConfig]:
        """初始化预设配置"""
        presets = {}
        
        # 现代蓝色
        config = ThemeConfig(name="Modern Blue")
        config.colors = ThemeColors(
            primary="#2563eb",
            secondary="#3b82f6",
            accent="#06b6d4",
        )
        presets[ThemePreset.MODERN_BLUE] = config
        
        # 优雅紫色
        config = ThemeConfig(name="Elegant Purple")
        config.colors = ThemeColors(
            primary="#7c3aed",
            secondary="#8b5cf6",
            accent="#a855f7",
        )
        config.typography.heading_font = "Playfair Display, Georgia, serif"
        presets[ThemePreset.ELEGANT_PURPLE] = config
        
        # 清新绿色
        config = ThemeConfig(name="Fresh Green")
        config.colors = ThemeColors(
            primary="#059669",
            secondary="#10b981",
            accent="#34d399",
            background="#f0fdf4",
        )
        presets[ThemePreset.FRESH_GREEN] = config
        
        # 温暖橙色
        config = ThemeConfig(name="Warm Orange")
        config.colors = ThemeColors(
            primary="#ea580c",
            secondary="#f97316",
            accent="#fb923c",
            background="#fff7ed",
        )
        presets[ThemePreset.WARM_ORANGE] = config
        
        # 暗色模式
        config = ThemeConfig(name="Dark Mode")
        config.colors = ThemeColors(
            primary="#6366f1",
            secondary="#818cf8",
            accent="#a5b4fc",
            text="#f1f5f9",
            text_light="#94a3b8",
            background="#0f172a",
            background_alt="#1e293b",
            border="#334155",
        )
        presets[ThemePreset.DARK_MODE] = config
        
        # 极简黑色
        config = ThemeConfig(name="Minimal Black")
        config.colors = ThemeColors(
            primary="#000000",
            secondary="#333333",
            accent="#666666",
            text="#111111",
            background="#ffffff",
        )
        config.typography.body_font = "system-ui, -apple-system, sans-serif"
        config.typography.heading_font = "system-ui, -apple-system, sans-serif"
        presets[ThemePreset.MINIMAL_BLACK] = config
        
        # 奢华金色
        config = ThemeConfig(name="Luxury Gold")
        config.colors = ThemeColors(
            primary="#b8860b",
            secondary="#daa520",
            accent="#ffd700",
            text="#1a1a1a",
            background="#fdfbf7",
            background_alt="#f9f5eb",
        )
        config.typography.heading_font = "Playfair Display, Georgia, serif"
        config.buttons.border_radius = "0px"
        presets[ThemePreset.LUXURY_GOLD] = config
        
        # 科技霓虹
        config = ThemeConfig(name="Tech Neon")
        config.colors = ThemeColors(
            primary="#00ff88",
            secondary="#00cc6a",
            accent="#00ffaa",
            text="#ffffff",
            background="#0a0a0a",
            background_alt="#111111",
            border="#222222",
        )
        config.typography.body_font = "Poppins, system-ui, sans-serif"
        config.typography.heading_font = "Poppins, system-ui, sans-serif"
        presets[ThemePreset.TECH_NEON] = config
        
        return presets
    
    def _init_industry_defaults(self) -> Dict[IndustryType, Dict[str, Any]]:
        """初始化行业默认配置"""
        return {
            IndustryType.ECOMMERCE: {
                "preset": ThemePreset.MODERN_BLUE,
                "woocommerce": {
                    "product_columns": 4,
                    "product_per_page": 12,
                    "show_quick_view": True,
                    "ajax_add_to_cart": True,
                },
            },
            IndustryType.FASHION: {
                "preset": ThemePreset.ELEGANT_PURPLE,
                "woocommerce": {
                    "product_columns": 3,
                    "product_per_page": 12,
                    "show_quick_view": True,
                },
                "blog": {
                    "archive_layout": "grid",
                    "archive_columns": 3,
                },
            },
            IndustryType.BEAUTY: {
                "preset": ThemePreset.ELEGANT_PURPLE,
                "woocommerce": {
                    "product_columns": 4,
                    "product_per_page": 16,
                },
            },
            IndustryType.HEALTH: {
                "preset": ThemePreset.FRESH_GREEN,
                "blog": {
                    "show_featured_image": True,
                    "show_date": True,
                    "show_author": True,
                },
            },
            IndustryType.FITNESS: {
                "preset": ThemePreset.WARM_ORANGE,
                "blog": {
                    "archive_layout": "grid",
                    "archive_columns": 3,
                },
            },
            IndustryType.TECH: {
                "preset": ThemePreset.MODERN_BLUE,
                "blog": {
                    "archive_layout": "list",
                    "archive_columns": 1,
                },
            },
            IndustryType.VAPE: {
                "preset": ThemePreset.DARK_MODE,
                "woocommerce": {
                    "product_columns": 4,
                    "product_per_page": 16,
                    "show_quick_view": True,
                    "ajax_add_to_cart": True,
                },
            },
            IndustryType.CANNABIS: {
                "preset": ThemePreset.FRESH_GREEN,
                "woocommerce": {
                    "product_columns": 4,
                    "product_per_page": 12,
                },
            },
            IndustryType.FOOD: {
                "preset": ThemePreset.WARM_ORANGE,
                "blog": {
                    "archive_layout": "grid",
                    "archive_columns": 3,
                },
            },
            IndustryType.FINANCE: {
                "preset": ThemePreset.MINIMAL_BLACK,
                "blog": {
                    "archive_layout": "list",
                    "archive_columns": 1,
                },
            },
            IndustryType.CORPORATE: {
                "preset": ThemePreset.MINIMAL_BLACK,
                "blog": {
                    "archive_layout": "list",
                    "archive_columns": 1,
                },
            },
            IndustryType.EDUCATION: {
                "preset": ThemePreset.MODERN_BLUE,
                "blog": {
                    "archive_layout": "grid",
                    "archive_columns": 2,
                },
            },
        }
    
    # ==================== 预设管理 ====================
    
    def get_preset(self, preset: ThemePreset) -> ThemeConfig:
        """获取预设配置"""
        return self._presets.get(preset, ThemeConfig())
    
    def get_all_presets(self) -> Dict[ThemePreset, ThemeConfig]:
        """获取所有预设"""
        return self._presets.copy()
    
    def get_preset_names(self) -> List[str]:
        """获取所有预设名称"""
        return [p.value for p in ThemePreset]
    
    # ==================== 从网站分析生成配置 ====================
    
    def generate_from_analysis(self, site_analysis: Dict[str, Any], 
                                industry: Optional[IndustryType] = None,
                                uniqueness: float = 0.6) -> ThemeConfig:
        """
        根据网站分析结果生成主题配置
        
        Args:
            site_analysis: 网站分析结果
            industry: 行业类型（可选）
            uniqueness: 差异化比例 0-1
            
        Returns:
            主题配置
        """
        config = ThemeConfig()
        
        # 如果指定了行业，使用行业默认配置
        if industry and industry in self._industry_defaults:
            defaults = self._industry_defaults[industry]
            preset = defaults.get("preset", ThemePreset.MODERN_BLUE)
            config = self.get_preset(preset)
            
            # 应用行业特定设置
            if "woocommerce" in defaults:
                for key, value in defaults["woocommerce"].items():
                    setattr(config.woocommerce, key, value)
            if "blog" in defaults:
                for key, value in defaults["blog"].items():
                    setattr(config.blog, key, value)
        
        # 从分析结果提取配色
        if "color_scheme" in site_analysis:
            original_colors = site_analysis["color_scheme"]
            # 根据差异化比例调整颜色
            if uniqueness > 0.3:
                config.colors = self._adjust_colors(original_colors, uniqueness)
        
        # 从分析结果提取字体
        if "font_scheme" in site_analysis:
            original_fonts = site_analysis["font_scheme"]
            if uniqueness > 0.5:
                config.typography = self._adjust_fonts(original_fonts, uniqueness)
        
        # 从分析结果提取布局风格
        if "layout_style" in site_analysis:
            layout_style = site_analysis["layout_style"]
            config.layout.layout_style = layout_style
        
        # 设置站点名称
        if "title" in site_analysis:
            config.name = site_analysis["title"] + " Theme"
        
        # 设置版权信息
        if "title" in site_analysis:
            config.footer.copyright_text = f"© {datetime.now().year} {site_analysis['title']}. All rights reserved."
        
        return config
    
    def _adjust_colors(self, original_colors: Dict[str, str], 
                       uniqueness: float) -> ThemeColors:
        """
        调整颜色以增加差异化
        
        Args:
            original_colors: 原始颜色
            uniqueness: 差异化比例
            
        Returns:
            调整后的颜色
        """
        colors = ThemeColors()
        
        # 复制原始颜色
        for key in ["primary", "secondary", "accent", "text", "background"]:
            if key in original_colors:
                setattr(colors, key, original_colors[key])
        
        # 根据差异化比例调整色相
        if uniqueness > 0.3:
            hue_shift = uniqueness * 60  # 最多偏移60度
            colors.primary = self._shift_hue(colors.primary, hue_shift)
            colors.secondary = self._shift_hue(colors.secondary, hue_shift)
            colors.accent = self._shift_hue(colors.accent, hue_shift)
        
        return colors
    
    def _shift_hue(self, hex_color: str, degrees: float) -> str:
        """
        调整颜色色相
        
        Args:
            hex_color: 十六进制颜色
            degrees: 偏移度数
            
        Returns:
            调整后的颜色
        """
        try:
            # 转换为RGB
            hex_color = hex_color.lstrip('#')
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            
            # 转换为HLS
            h, l, s = rgb_to_hls(r, g, b)
            
            # 调整色相
            h = (h + degrees / 360.0) % 1.0
            
            # 转换回RGB
            r, g, b = hls_to_rgb(h, l, s)
            
            # 转换回十六进制
            return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        except:
            return hex_color
    
    def _adjust_fonts(self, original_fonts: Dict[str, str], 
                      uniqueness: float) -> ThemeTypography:
        """
        调整字体以增加差异化
        
        Args:
            original_fonts: 原始字体
            uniqueness: 差异化比例
            
        Returns:
            调整后的字体配置
        """
        typography = ThemeTypography()
        
        # 复制原始字体
        if "body_font" in original_fonts:
            typography.body_font = original_fonts["body_font"]
        if "heading_font" in original_fonts:
            typography.heading_font = original_fonts["heading_font"]
        
        # 如果差异化比例高，更换字体族
        if uniqueness > 0.7:
            font_options = [
                ("Inter, system-ui, sans-serif", "Inter, system-ui, sans-serif"),
                ("Poppins, system-ui, sans-serif", "Poppins, system-ui, sans-serif"),
                ("Roboto, system-ui, sans-serif", "Roboto, system-ui, sans-serif"),
                ("Open Sans, system-ui, sans-serif", "Open Sans, system-ui, sans-serif"),
            ]
            body_font, heading_font = random.choice(font_options)
            typography.body_font = body_font
            typography.heading_font = heading_font
        
        return typography
    
    # ==================== 配置导出 ====================
    
    def export_for_wordpress(self, config: ThemeConfig) -> Dict[str, Any]:
        """
        导出为WordPress主题可直接使用的配置格式
        
        Args:
            config: 主题配置
            
        Returns:
            WordPress格式的配置
        """
        wp_config = {
            "theme_mods": {},
            "options": {},
            "custom_css": config.custom_css,
        }
        
        # 颜色设置
        colors = config.colors.to_dict()
        for key, value in colors.items():
            wp_config["theme_mods"][f"color_{key}"] = value
        
        # 排版设置
        typography = config.typography.to_dict()
        for key, value in typography.items():
            wp_config["theme_mods"][f"typography_{key}"] = value
        
        # 布局设置
        layout = config.layout.to_dict()
        for key, value in layout.items():
            wp_config["theme_mods"][f"layout_{key}"] = value
        
        # 头部设置
        header = config.header.to_dict()
        for key, value in header.items():
            wp_config["theme_mods"][f"header_{key}"] = value
        
        # 底部设置
        footer = config.footer.to_dict()
        for key, value in footer.items():
            wp_config["theme_mods"][f"footer_{key}"] = value
        
        return wp_config
    
    def generate_css_variables(self, config: ThemeConfig) -> str:
        """
        生成CSS变量
        
        Args:
            config: 主题配置
            
        Returns:
            CSS变量字符串
        """
        colors = config.colors.to_dict()
        typography = config.typography.to_dict()
        
        css = ":root {\n"
        
        # 颜色变量
        for key, value in colors.items():
            css += f"  --wpforge-color-{key.replace('_', '-')}: {value};\n"
        
        # 字体变量
        css += f"  --wpforge-font-body: {typography['body_font']};\n"
        css += f"  --wpforge-font-heading: {typography['heading_font']};\n"
        css += f"  --wpforge-font-size-base: {typography['base_font_size']};\n"
        css += f"  --wpforge-line-height-base: {typography['base_line_height']};\n"
        
        # 布局变量
        layout = config.layout.to_dict()
        css += f"  --wpforge-container-width: {layout['container_width']};\n"
        css += f"  --wpforge-gutter: {layout['gutter']};\n"
        
        # 按钮变量
        buttons = config.buttons.to_dict()
        css += f"  --wpforge-button-radius: {buttons['border_radius']};\n"
        
        css += "}\n"
        
        return css
    
    # ==================== 配置管理 ====================
    
    def compare_configs(self, config1: ThemeConfig, config2: ThemeConfig) -> Dict[str, Any]:
        """
        比较两个配置的差异
        
        Args:
            config1: 配置1
            config2: 配置2
            
        Returns:
            差异信息
        """
        diff = {
            "colors": {},
            "typography": {},
            "layout": {},
            "buttons": {},
            "header": {},
            "footer": {},
            "blog": {},
            "woocommerce": {},
            "seo": {},
            "performance": {},
        }
        
        # 比较颜色
        c1 = config1.colors.to_dict()
        c2 = config2.colors.to_dict()
        for key in c1:
            if c1[key] != c2[key]:
                diff["colors"][key] = {"old": c1[key], "new": c2[key]}
        
        # 可以继续比较其他部分...
        
        return diff
    
    def merge_configs(self, base_config: ThemeConfig, 
                      override_config: ThemeConfig) -> ThemeConfig:
        """
        合并两个配置
        
        Args:
            base_config: 基础配置
            override_config: 覆盖配置
            
        Returns:
            合并后的配置
        """
        # 简单实现：使用覆盖配置的值
        # 实际可以更智能地合并
        return override_config


# 单例实例
_theme_config_generator = None


def get_theme_config_generator() -> ThemeConfigGenerator:
    """获取主题配置生成器单例"""
    global _theme_config_generator
    if _theme_config_generator is None:
        _theme_config_generator = ThemeConfigGenerator()
    return _theme_config_generator


# 导入datetime（放在后面避免影响类型注解）
from datetime import datetime
