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
    PEDLSettings,
    PEDLStyle,
)
from app.services.page_builder.elementor_converter import ElementorConverter
from app.services.page_builder.ai_design import AIDesignEngine


class TestWidgetType:
    """Widget类型测试"""

    def test_widget_type_values(self):
        """测试Widget类型值"""
        assert WidgetType.HEADING.value == "heading"
        assert WidgetType.TEXT_EDITOR.value == "text_editor"
        assert WidgetType.IMAGE.value == "image"
        assert WidgetType.BUTTON.value == "button"
        assert WidgetType.ICON.value == "icon"
        assert WidgetType.DIVIDER.value == "divider"
        assert WidgetType.SPACER.value == "spacer"
        assert WidgetType.VIDEO.value == "video"
        assert WidgetType.FORM.value == "form"

    def test_widget_type_count(self):
        """测试Widget类型数量"""
        assert len(WidgetType) >= 30


class TestPEDLWidget:
    """PEDL Widget测试"""

    def test_widget_creation(self):
        """测试Widget创建"""
        widget = PEDLWidget(
            widget_type=WidgetType.HEADING,
            content={"text": "Hello World", "level": 1}
        )
        assert widget.widget_type == WidgetType.HEADING
        assert widget.content["text"] == "Hello World"

    def test_widget_settings(self):
        """测试Widget设置"""
        style = PEDLStyle(text_color="#333")
        settings = PEDLSettings(title="Test", style=style)
        widget = PEDLWidget(
            widget_type=WidgetType.TEXT_EDITOR,
            content={"text": "Test"},
            settings=settings,
        )
        assert widget.settings.style.text_color == "#333"

    def test_widget_to_dict(self):
        """测试转换为字典"""
        widget = PEDLWidget(
            widget_type=WidgetType.BUTTON,
            content={"text": "Click Me", "url": "https://example.com"}
        )
        d = widget.to_dict()
        assert isinstance(d, dict)
        assert d["widget_type"] == "button"
        assert "content" in d
        assert "settings" in d

    def test_widget_from_dict(self):
        """测试从字典创建"""
        d = {
            "widget_type": "heading",
            "content": {"text": "Test", "level": 2},
            "settings": {},
        }
        widget = PEDLWidget.from_dict(d)
        assert widget.widget_type == WidgetType.HEADING
        assert widget.content["text"] == "Test"

    def test_widget_with_children(self):
        """测试带子元素的Widget"""
        parent = PEDLWidget(widget_type=WidgetType.ACCORDION)
        child = PEDLWidget(
            widget_type=WidgetType.TOGGLE,
            content={"tab_title": "Q1", "tab_content": "A1"},
        )
        parent.children.append(child)
        assert len(parent.children) == 1

        d = parent.to_dict()
        assert "children" in d
        assert len(d["children"]) == 1


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
        widget = PEDLWidget(widget_type=WidgetType.TEXT_EDITOR, content={"text": "Test"})
        col.widgets.append(widget)
        assert len(col.widgets) == 1

    def test_column_to_dict(self):
        """测试转换为字典"""
        col = PEDLColumn(width="33.33%")
        d = col.to_dict()
        assert isinstance(d, dict)
        assert d["width"] == "33.33%"
        assert "widgets" in d

    def test_column_from_dict(self):
        """测试从字典创建"""
        d = {
            "width": "25%",
            "widgets": [
                {"widget_type": "heading", "content": {"text": "Hi"}, "settings": {}}
            ],
        }
        col = PEDLColumn.from_dict(d)
        assert col.width == "25%"
        assert len(col.widgets) == 1
        assert col.widgets[0].widget_type == WidgetType.HEADING


class TestPEDLSection:
    """PEDL Section测试"""

    def test_section_creation(self):
        """测试Section创建"""
        section = PEDLSection()
        assert len(section.columns) == 0
        assert section.layout == "boxed"

    def test_section_add_column(self):
        """测试添加Column"""
        section = PEDLSection()
        col = PEDLColumn(width="50%")
        section.columns.append(col)
        assert len(section.columns) == 1

    def test_section_to_dict(self):
        """测试转换为字典"""
        section = PEDLSection()
        d = section.to_dict()
        assert isinstance(d, dict)
        assert "columns" in d
        assert "layout" in d

    def test_section_from_dict(self):
        """测试从字典创建"""
        d = {
            "layout": "full_width",
            "columns_gap": "no",
            "columns": [],
        }
        section = PEDLSection.from_dict(d)
        assert section.layout == "full_width"
        assert section.columns_gap == "no"


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

    def test_document_from_dict(self):
        """测试从字典创建"""
        d = {
            "title": "From Dict",
            "document_type": "page",
            "sections": [],
        }
        doc = PEDLDocument.from_dict(d)
        assert doc.title == "From Dict"


class TestPEDLDocumentBuilders:
    """PEDL Document构建方法测试"""

    def test_create_simple_section(self):
        """测试创建简单Section"""
        doc = PEDLDocument(title="Test")
        section = doc.create_simple_section(
            content="Test content text.",
            title="Test Title",
        )
        assert isinstance(section, PEDLSection)
        assert len(section.columns) >= 1
        assert len(doc.sections) == 1

    def test_create_hero_section(self):
        """测试创建Hero Section"""
        doc = PEDLDocument()
        section = doc.create_hero_section(
            title="Welcome",
            subtitle="Subtitle text",
            button_text="Get Started",
            button_url="https://example.com",
        )
        assert isinstance(section, PEDLSection)
        assert len(section.columns) >= 1
        assert section.layout == "full_width"

    def test_create_features_section(self):
        """测试创建Features Section"""
        doc = PEDLDocument()
        features = [
            {"title": "Feature 1", "description": "Desc 1", "icon": "star"},
            {"title": "Feature 2", "description": "Desc 2", "icon": "heart"},
            {"title": "Feature 3", "description": "Desc 3", "icon": "bolt"},
        ]
        section = doc.create_features_section(features)
        assert isinstance(section, PEDLSection)
        assert len(section.columns) >= 3

    def test_create_products_section(self):
        """测试创建Products Section"""
        doc = PEDLDocument()
        products = [
            {"name": "Product 1", "price": "$9", "image": "https://example.com/1.jpg"},
            {"name": "Product 2", "price": "$29", "image": "https://example.com/2.jpg"},
        ]
        section = doc.create_products_section(products)
        assert isinstance(section, PEDLSection)
        assert len(section.columns) >= 2

    def test_create_testimonials_section(self):
        """测试创建Testimonials Section"""
        doc = PEDLDocument()
        testimonials = [
            {"name": "User 1", "text": "Great product!"},
            {"name": "User 2", "text": "Love it!"},
        ]
        section = doc.create_testimonials_section(testimonials)
        assert isinstance(section, PEDLSection)
        assert len(section.columns) >= 1

    def test_create_faq_section(self):
        """测试创建FAQ Section"""
        doc = PEDLDocument()
        faqs = [
            {"question": "What is this?", "answer": "It's a product."},
            {"question": "How much?", "answer": "$29.99"},
        ]
        section = doc.create_faq_section(faqs)
        assert isinstance(section, PEDLSection)

    def test_create_cta_section(self):
        """测试创建CTA Section"""
        doc = PEDLDocument()
        section = doc.create_cta_section(
            title="Ready to start?",
            button_text="Sign Up Now",
            button_url="https://example.com/signup",
        )
        assert isinstance(section, PEDLSection)


class TestElementorConverter:
    """Elementor转换器测试"""

    def test_converter_creation(self):
        """测试转换器创建"""
        converter = ElementorConverter()
        assert converter is not None
        assert hasattr(converter, "widget_type_map")

    def test_convert_document(self):
        """测试转换Document"""
        doc = PEDLDocument(title="Test Page")
        doc.create_simple_section(content="Content", title="Test")
        converter = ElementorConverter()
        result = converter.convert(doc)
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0]["elType"] == "section"

    def test_convert_to_elementor_data(self):
        """测试转换为完整Elementor数据"""
        doc = PEDLDocument(title="Test Page")
        doc.create_simple_section(content="Content", title="Test")
        converter = ElementorConverter()
        result = converter.convert_to_elementor_data(doc)
        assert isinstance(result, dict)
        assert "content" in result
        assert "version" in result
        assert result["title"] == "Test Page"

    def test_create_elementor_post_meta(self):
        """测试创建Elementor post meta"""
        doc = PEDLDocument(title="Test")
        doc.create_simple_section(content="Content", title="Test")
        converter = ElementorConverter()
        meta = converter.create_elementor_post_meta(doc, post_id=1)
        assert isinstance(meta, list)
        meta_keys = [m["meta_key"] for m in meta]
        assert "_elementor_data" in meta_keys
        assert "_elementor_edit_mode" in meta_keys
        assert "_elementor_template_type" in meta_keys

    def test_convert_empty_document(self):
        """测试转换空Document"""
        doc = PEDLDocument(title="Empty")
        converter = ElementorConverter()
        result = converter.convert(doc)
        assert isinstance(result, list)
        assert len(result) == 0


class TestAIDesignEngine:
    """AI设计引擎测试"""

    def test_engine_creation(self):
        """测试引擎创建"""
        engine = AIDesignEngine()
        assert engine is not None
        assert engine.color_scheme is not None
        assert engine.font_scheme is not None

    def test_engine_creation_with_custom_schemes(self):
        """测试自定义方案创建"""
        engine = AIDesignEngine(
            color_scheme="elegant_purple",
            font_scheme="elegant_serif",
            style="elegant",
        )
        assert engine.color_scheme["primary"] == "#7c3aed"
        assert engine.font_scheme["heading"] == "Playfair Display"
        assert engine.style == "elegant"

    def test_color_schemes_available(self):
        """测试配色方案可用"""
        assert "modern_blue" in AIDesignEngine.COLOR_SCHEMES
        assert "elegant_purple" in AIDesignEngine.COLOR_SCHEMES
        assert "fresh_green" in AIDesignEngine.COLOR_SCHEMES
        assert "warm_orange" in AIDesignEngine.COLOR_SCHEMES
        assert "dark_mode" in AIDesignEngine.COLOR_SCHEMES
        assert "minimal_black" in AIDesignEngine.COLOR_SCHEMES
        assert len(AIDesignEngine.COLOR_SCHEMES) >= 6

    def test_font_schemes_available(self):
        """测试字体方案可用"""
        assert "modern_sans" in AIDesignEngine.FONT_SCHEMES
        assert "elegant_serif" in AIDesignEngine.FONT_SCHEMES
        assert "tech_geometric" in AIDesignEngine.FONT_SCHEMES
        assert "classic_news" in AIDesignEngine.FONT_SCHEMES
        assert len(AIDesignEngine.FONT_SCHEMES) >= 4

    def test_design_styles_available(self):
        """测试设计风格可用"""
        styles = AIDesignEngine.DESIGN_STYLES
        assert "minimal" in styles
        assert "modern" in styles
        assert "elegant" in styles
        assert "bold" in styles
        assert "playful" in styles
        assert "professional" in styles
        assert "luxury" in styles
        assert "tech" in styles
        assert len(styles) >= 8

    def test_generate_product_page(self):
        """测试生成产品页面"""
        engine = AIDesignEngine()
        product = {
            "name": "Test Product",
            "description": "This is a test product.",
            "price": "$29.99",
            "image": "https://example.com/product.jpg",
        }
        doc = engine.generate_product_page(product)
        assert isinstance(doc, PEDLDocument)
        assert len(doc.sections) > 0

    def test_generate_landing_page(self):
        """测试生成落地页"""
        engine = AIDesignEngine()
        content = {
            "hero": {
                "title": "Test Landing Page",
                "subtitle": "Subtitle",
            },
            "features": [{"title": "F1", "description": "D1"}],
            "cta": {
                "title": "Get Started",
                "button_text": "Sign Up",
                "button_url": "https://example.com",
            },
        }
        doc = engine.generate_landing_page(content)
        assert isinstance(doc, PEDLDocument)
        assert len(doc.sections) > 0

    def test_generate_about_page(self):
        """测试生成关于页面"""
        engine = AIDesignEngine()
        content = {
            "hero": {"title": "About Us"},
            "description": "Company description.",
            "team": [{"name": "John", "role": "CEO"}],
        }
        doc = engine.generate_about_page(content)
        assert isinstance(doc, PEDLDocument)
        assert len(doc.sections) > 0

    def test_generate_contact_page(self):
        """测试生成联系页面"""
        engine = AIDesignEngine()
        content = {
            "title": "Contact Us",
            "email": "info@example.com",
            "phone": "+1234567890",
            "address": "123 Test St",
        }
        doc = engine.generate_contact_page(content)
        assert isinstance(doc, PEDLDocument)
        assert len(doc.sections) > 0

    def test_get_random_design(self):
        """测试获取随机设计"""
        engine = AIDesignEngine.get_random_design()
        assert isinstance(engine, AIDesignEngine)

    def test_get_design_for_industry(self):
        """测试获取行业设计"""
        engine = AIDesignEngine.get_design_for_industry("ecommerce")
        assert isinstance(engine, AIDesignEngine)
