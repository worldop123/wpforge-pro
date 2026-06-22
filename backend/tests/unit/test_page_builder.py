"""
页面构建器测试
"""
import pytest
import json
from app.services.page_builder.pedl import (
    WidgetType,
    PEDLWidget,
    PEDLColumn,
    PEDLSection,
    PEDLDocument,
    create_simple_section,
    create_hero_section,
    create_features_section,
    create_pricing_section,
    create_testimonials_section,
    create_faq_section,
    create_cta_section,
    create_footer_section,
)
from app.services.page_builder.elementor_converter import (
    ElementorConverter,
    create_elementor_post_meta,
)
from app.services.page_builder.ai_design import (
    AIDesignEngine,
    ColorScheme,
    FontScheme,
    DesignStyle,
    get_ai_design_engine,
)


class TestWidgetType:
    """Widget类型测试"""

    def test_widget_type_values(self):
        """测试Widget类型值"""
        assert hasattr(WidgetType, 'HEADING')
        assert hasattr(WidgetType, 'TEXT')
        assert hasattr(WidgetType, 'IMAGE')
        assert hasattr(WidgetType, 'BUTTON')
        assert hasattr(WidgetType, 'ICON')
        assert hasattr(WidgetType, 'DIVIDER')
        assert hasattr(WidgetType, 'SPACER')
        assert hasattr(WidgetType, 'LIST')
        assert hasattr(WidgetType, 'VIDEO')
        assert hasattr(WidgetType, 'FORM')

    def test_widget_type_count(self):
        """测试Widget类型数量"""
        assert len(WidgetType) >= 30


class TestPEDLWidget:
    """PEDL Widget测试"""

    def test_widget_creation(self):
        """测试Widget创建"""
        widget = PEDLWidget(
            type=WidgetType.HEADING,
            content={"text": "Hello World", "level": 1}
        )
        assert widget.type == WidgetType.HEADING
        assert widget.content["text"] == "Hello World"

    def test_widget_styles(self):
        """测试Widget样式"""
        widget = PEDLWidget(
            type=WidgetType.TEXT,
            content={"text": "Test"},
            styles={
                "color": "#333",
                "font_size": "16px",
                "margin": {"top": "10px", "bottom": "10px"}
            }
        )
        assert widget.styles["color"] == "#333"
        assert widget.styles["margin"]["top"] == "10px"

    def test_widget_to_dict(self):
        """测试转换为字典"""
        widget = PEDLWidget(
            type=WidgetType.BUTTON,
            content={"text": "Click Me", "url": "https://example.com"}
        )
        d = widget.to_dict()
        assert isinstance(d, dict)
        assert d["type"] == "button"
        assert "content" in d
        assert "styles" in d

    def test_widget_from_dict(self):
        """测试从字典创建"""
        d = {
            "type": "heading",
            "content": {"text": "Test", "level": 2},
            "styles": {"color": "#ff0000"}
        }
        widget = PEDLWidget.from_dict(d)
        assert widget.type == WidgetType.HEADING
        assert widget.content["text"] == "Test"


class TestPEDLColumn:
    """PEDL Column测试"""

    def test_column_creation(self):
        """测试Column创建"""
        col = PEDLColumn(width="50%")
        assert col.width == "50%"
        assert len(col.widgets) == 0

    def test_column_add_widget(self):
        """测试添加Widget"""
        col = PEDLColumn()
        widget = PEDLWidget(type=WidgetType.TEXT, content={"text": "Test"})
        col.add_widget(widget)
        assert len(col.widgets) == 1

    def test_column_to_dict(self):
        """测试转换为字典"""
        col = PEDLColumn(width="33.33%")
        d = col.to_dict()
        assert isinstance(d, dict)
        assert d["width"] == "33.33%"
        assert "widgets" in d


class TestPEDLSection:
    """PEDL Section测试"""

    def test_section_creation(self):
        """测试Section创建"""
        section = PEDLSection()
        assert len(section.columns) == 0

    def test_section_add_column(self):
        """测试添加Column"""
        section = PEDLSection()
        col = PEDLColumn(width="50%")
        section.add_column(col)
        assert len(section.columns) == 1

    def test_section_to_dict(self):
        """测试转换为字典"""
        section = PEDLSection()
        d = section.to_dict()
        assert isinstance(d, dict)
        assert "columns" in d
        assert "styles" in d


class TestPEDLDocument:
    """PEDL Document测试"""

    def test_document_creation(self):
        """测试Document创建"""
        doc = PEDLDocument(title="Test Page")
        assert doc.title == "Test Page"
        assert len(doc.sections) == 0

    def test_document_add_section(self):
        """测试添加Section"""
        doc = PEDLDocument()
        section = PEDLSection()
        doc.add_section(section)
        assert len(doc.sections) == 1

    def test_document_to_json(self):
        """测试转换为JSON"""
        doc = PEDLDocument(title="Test")
        json_str = doc.to_json()
        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert data["title"] == "Test"
        assert "sections" in data

    def test_document_from_json(self):
        """测试从JSON创建"""
        doc = PEDLDocument(title="Test")
        json_str = doc.to_json()
        new_doc = PEDLDocument.from_json(json_str)
        assert new_doc.title == "Test"

    def test_document_to_dict(self):
        """测试转换为字典"""
        doc = PEDLDocument(title="Test")
        d = doc.to_dict()
        assert isinstance(d, dict)
        assert "title" in d
        assert "sections" in d


class TestHelperFunctions:
    """辅助函数测试"""

    def test_create_simple_section(self):
        """测试创建简单Section"""
        section = create_simple_section(
            title="Test Title",
            content="Test content text."
        )
        assert isinstance(section, PEDLSection)
        assert len(section.columns) >= 1

    def test_create_hero_section(self):
        """测试创建Hero Section"""
        section = create_hero_section(
            title="Welcome",
            subtitle="Subtitle text",
            button_text="Get Started",
            button_url="https://example.com"
        )
        assert isinstance(section, PEDLSection)
        assert len(section.columns) >= 1

    def test_create_features_section(self):
        """测试创建Features Section"""
        features = [
            {"title": "Feature 1", "description": "Desc 1", "icon": "star"},
            {"title": "Feature 2", "description": "Desc 2", "icon": "heart"},
            {"title": "Feature 3", "description": "Desc 3", "icon": "bolt"},
        ]
        section = create_features_section(features)
        assert isinstance(section, PEDLSection)
        assert len(section.columns) >= 3

    def test_create_pricing_section(self):
        """测试创建Pricing Section"""
        plans = [
            {"name": "Basic", "price": "$9", "features": ["Feature 1", "Feature 2"]},
            {"name": "Pro", "price": "$29", "features": ["All features"]},
        ]
        section = create_pricing_section(plans)
        assert isinstance(section, PEDLSection)
        assert len(section.columns) >= 2

    def test_create_testimonials_section(self):
        """测试创建Testimonials Section"""
        testimonials = [
            {"name": "User 1", "text": "Great product!", "avatar": "https://example.com/1.jpg"},
            {"name": "User 2", "text": "Love it!", "avatar": "https://example.com/2.jpg"},
        ]
        section = create_testimonials_section(testimonials)
        assert isinstance(section, PEDLSection)
        assert len(section.columns) >= 2

    def test_create_faq_section(self):
        """测试创建FAQ Section"""
        faqs = [
            {"question": "What is this?", "answer": "It's a product."},
            {"question": "How much?", "answer": "$29.99"},
        ]
        section = create_faq_section(faqs)
        assert isinstance(section, PEDLSection)

    def test_create_cta_section(self):
        """测试创建CTA Section"""
        section = create_cta_section(
            title="Ready to start?",
            button_text="Sign Up Now",
            button_url="https://example.com/signup"
        )
        assert isinstance(section, PEDLSection)

    def test_create_footer_section(self):
        """测试创建Footer Section"""
        section = create_footer_section(
            company_name="Test Company",
            copyright_text="© 2024 Test Company"
        )
        assert isinstance(section, PEDLSection)


class TestElementorConverter:
    """Elementor转换器测试"""

    def test_converter_creation(self):
        """测试转换器创建"""
        converter = ElementorConverter()
        assert converter is not None

    def test_convert_simple_widget(self):
        """测试转换简单Widget"""
        widget = PEDLWidget(
            type=WidgetType.HEADING,
            content={"text": "Hello", "level": 1}
        )
        result = ElementorConverter.convert_widget(widget)
        assert isinstance(result, dict)
        assert "widgetType" in result
        assert "settings" in result

    def test_convert_section(self):
        """测试转换Section"""
        section = create_simple_section(title="Test", content="Content")
        result = ElementorConverter.convert_section(section)
        assert isinstance(result, dict)
        assert "elType" in result

    def test_convert_document(self):
        """测试转换Document"""
        doc = PEDLDocument(title="Test Page")
        doc.add_section(create_simple_section(title="Test", content="Content"))
        result = ElementorConverter.convert(doc)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_create_elementor_post_meta(self):
        """测试创建Elementor post meta"""
        doc = PEDLDocument(title="Test")
        doc.add_section(create_simple_section(title="Test", content="Content"))
        meta = create_elementor_post_meta(doc)
        assert isinstance(meta, dict)
        assert "_elementor_data" in meta
        assert "_elementor_edit_mode" in meta
        assert "_elementor_template_type" in meta


class TestAIDesignEngine:
    """AI设计引擎测试"""

    def test_get_instance(self):
        """测试单例模式"""
        engine1 = get_ai_design_engine()
        engine2 = get_ai_design_engine()
        assert engine1 is engine2

    def test_color_scheme_values(self):
        """测试配色方案"""
        assert hasattr(ColorScheme, 'MODERN_BLUE')
        assert hasattr(ColorScheme, 'ELEGANT_PURPLE')
        assert hasattr(ColorScheme, 'FRESH_GREEN')
        assert hasattr(ColorScheme, 'WARM_ORANGE')
        assert hasattr(ColorScheme, 'DARK_MODE')
        assert hasattr(ColorScheme, 'MINIMAL_BLACK')
        assert len(ColorScheme) >= 6

    def test_font_scheme_values(self):
        """测试字体方案"""
        assert hasattr(FontScheme, 'MODERN_SANS')
        assert hasattr(FontScheme, 'ELEGANT_SERIF')
        assert hasattr(FontScheme, 'TECH_GEOMETRIC')
        assert hasattr(FontScheme, 'CLASSIC_NEWS')
        assert len(FontScheme) >= 4

    def test_design_style_values(self):
        """测试设计风格"""
        assert hasattr(DesignStyle, 'MINIMAL')
        assert hasattr(DesignStyle, 'MODERN')
        assert hasattr(DesignStyle, 'ELEGANT')
        assert hasattr(DesignStyle, 'BOLD')
        assert hasattr(DesignStyle, 'PLAYFUL')
        assert hasattr(DesignStyle, 'PROFESSIONAL')
        assert hasattr(DesignStyle, 'LUXURY')
        assert hasattr(DesignStyle, 'TECH')
        assert len(DesignStyle) >= 8

    def test_generate_product_page(self):
        """测试生成产品页面"""
        engine = get_ai_design_engine()
        doc = engine.generate_product_page(
            product_name="Test Product",
            description="This is a test product.",
            price="$29.99",
            image_url="https://example.com/product.jpg"
        )
        assert isinstance(doc, PEDLDocument)
        assert len(doc.sections) > 0

    def test_generate_landing_page(self):
        """测试生成落地页"""
        engine = get_ai_design_engine()
        doc = engine.generate_landing_page(
            title="Test Landing Page",
            subtitle="Subtitle",
            features=[{"title": "F1", "description": "D1"}],
            cta_text="Get Started"
        )
        assert isinstance(doc, PEDLDocument)
        assert len(doc.sections) > 0

    def test_generate_about_page(self):
        """测试生成关于页面"""
        engine = get_ai_design_engine()
        doc = engine.generate_about_page(
            company_name="Test Company",
            description="Company description.",
            team_members=[{"name": "John", "role": "CEO"}]
        )
        assert isinstance(doc, PEDLDocument)
        assert len(doc.sections) > 0

    def test_generate_contact_page(self):
        """测试生成联系页面"""
        engine = get_ai_design_engine()
        doc = engine.generate_contact_page(
            company_name="Test Company",
            email="info@example.com",
            phone="+1234567890",
            address="123 Test St"
        )
        assert isinstance(doc, PEDLDocument)
        assert len(doc.sections) > 0

    def test_get_color_scheme(self):
        """测试获取配色方案"""
        engine = get_ai_design_engine()
        colors = engine.get_color_scheme(ColorScheme.MODERN_BLUE)
        assert isinstance(colors, dict)
        assert "primary" in colors
        assert "secondary" in colors

    def test_get_font_scheme(self):
        """测试获取字体方案"""
        engine = get_ai_design_engine()
        fonts = engine.get_font_scheme(FontScheme.MODERN_SANS)
        assert isinstance(fonts, dict)
        assert "body" in fonts
        assert "heading" in fonts

    def test_get_industry_recommendation(self):
        """测试获取行业推荐"""
        engine = get_ai_design_engine()
        rec = engine.get_industry_recommendation("ecommerce")
        assert isinstance(rec, dict)
        assert "color_scheme" in rec
        assert "design_style" in rec

    def test_get_all_color_schemes(self):
        """测试获取所有配色方案"""
        engine = get_ai_design_engine()
        schemes = engine.get_all_color_schemes()
        assert isinstance(schemes, list)
        assert len(schemes) == len(ColorScheme)

    def test_get_all_font_schemes(self):
        """测试获取所有字体方案"""
        engine = get_ai_design_engine()
        schemes = engine.get_all_font_schemes()
        assert isinstance(schemes, list)
        assert len(schemes) == len(FontScheme)

    def test_get_all_design_styles(self):
        """测试获取所有设计风格"""
        engine = get_ai_design_engine()
        styles = engine.get_all_design_styles()
        assert isinstance(styles, list)
        assert len(styles) == len(DesignStyle)
