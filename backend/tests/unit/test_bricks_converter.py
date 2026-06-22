"""
Bricks Builder 转换器测试
"""
import pytest
from app.services.page_builder.pedl import (
    WidgetType,
    PEDLWidget,
    PEDLColumn,
    PEDLSection,
    PEDLDocument,
    PEDLSettings,
    PEDLStyle,
    PEDLTypography,
    Alignment,
)
from app.services.page_builder.bricks_converter import BricksConverter


def _make_style(**kwargs):
    """构造带样式的 PEDLStyle"""
    return PEDLStyle(**kwargs)


def _make_document_with_section(section=None):
    """构造包含一个 section 的文档"""
    doc = PEDLDocument(title="Test Page")
    doc.add_section(section or PEDLSection())
    return doc


class TestBricksConverterCreation:
    """转换器创建测试"""

    def test_converter_creation(self):
        converter = BricksConverter()
        assert converter is not None
        assert hasattr(converter, "widget_type_map")

    def test_widget_type_map_contains_basic_types(self):
        converter = BricksConverter()
        assert converter.widget_type_map[WidgetType.HEADING] == "heading"
        assert converter.widget_type_map[WidgetType.TEXT_EDITOR] == "text"
        assert converter.widget_type_map[WidgetType.IMAGE] == "image"
        assert converter.widget_type_map[WidgetType.BUTTON] == "button"

    def test_widget_type_map_contains_woocommerce_types(self):
        converter = BricksConverter()
        assert converter.widget_type_map[WidgetType.PRODUCT] == "product"
        assert converter.widget_type_map[WidgetType.PRODUCTS] == "products"
        assert converter.widget_type_map[WidgetType.ADD_TO_CART] == "add-to-cart"

    def test_generate_id_returns_string(self):
        converter = BricksConverter()
        new_id = converter._generate_id()
        assert isinstance(new_id, str)
        assert len(new_id) > 0


class TestBricksConvertDocument:
    """文档转换测试"""

    def test_convert_empty_document(self):
        converter = BricksConverter()
        doc = PEDLDocument(title="Empty")
        result = converter.convert(doc)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_convert_document_with_section(self):
        converter = BricksConverter()
        section = PEDLSection()
        section.columns.append(PEDLColumn(width="100%"))
        doc = _make_document_with_section(section)

        result = converter.convert(doc)
        assert len(result) == 1
        assert result[0]["name"] == "section"
        assert result[0]["parent"] == 0
        assert "children" in result[0]
        assert len(result[0]["children"]) == 1

    def test_convert_to_bricks_data(self):
        converter = BricksConverter()
        section = PEDLSection()
        section.columns.append(PEDLColumn(width="50%"))
        doc = _make_document_with_section(section)

        result = converter.convert_to_bricks_data(doc)
        assert isinstance(result, dict)
        assert "elements" in result
        assert "settings" in result
        assert result["version"] == "1.9.6"
        assert result["title"] == "Test Page"
        assert result["type"] == doc.document_type

    def test_create_bricks_post_meta(self):
        converter = BricksConverter()
        section = PEDLSection()
        section.columns.append(PEDLColumn(width="50%"))
        doc = _make_document_with_section(section)

        meta = converter.create_bricks_post_meta(doc, post_id=42)
        assert isinstance(meta, list)
        meta_keys = [m["meta_key"] for m in meta]
        assert "_bricks_page_content_2" in meta_keys
        assert "_bricks_page_settings" in meta_keys
        assert "_bricks_editor_mode" in meta_keys
        assert "_bricks_version" in meta_keys
        for record in meta:
            assert record["post_id"] == 42


class TestBricksSectionConversion:
    """区块转换测试"""

    def test_convert_section_boxed_layout(self):
        converter = BricksConverter()
        section = PEDLSection(layout="boxed")
        result = converter._convert_section(section)
        assert result["settings"]["container"] == "boxed"

    def test_convert_section_full_width_layout(self):
        converter = BricksConverter()
        section = PEDLSection(layout="full_width")
        result = converter._convert_section(section)
        assert result["settings"]["container"] == "full"

    def test_convert_section_full_width_stretched_layout(self):
        converter = BricksConverter()
        section = PEDLSection(layout="full_width_stretched")
        result = converter._convert_section(section)
        assert result["settings"]["container"] == "full"
        assert result["settings"]["stretch"] is True

    def test_convert_section_with_columns_gap(self):
        converter = BricksConverter()
        section = PEDLSection(columns_gap="narrow")
        result = converter._convert_section(section)
        assert result["settings"]["gap"] == 10

    def test_convert_section_with_default_gap(self):
        converter = BricksConverter()
        section = PEDLSection(columns_gap="default")
        result = converter._convert_section(section)
        # default gap 不应被设置（因为条件是 != "default"）
        assert "gap" not in result["settings"]

    def test_convert_section_with_advanced_settings(self):
        converter = BricksConverter()
        section = PEDLSection()
        section.settings.element_id = "main-section"
        section.settings.css_classes = "custom-class"
        section.settings.custom_css = ".x { color: red; }"
        section.settings.hide_on_desktop = True
        section.settings.hide_on_mobile = True

        result = converter._convert_section(section)
        assert result["settings"]["_cssId"] == "main-section"
        assert result["settings"]["_cssClasses"] == "custom-class"
        assert result["settings"]["_customCSS"] == ".x { color: red; }"
        assert result["settings"]["_visibility:hide_desktop"] is True
        assert result["settings"]["_visibility:hide_mobile"] is True


class TestBricksColumnConversion:
    """列转换测试"""

    def test_convert_column_with_width(self):
        converter = BricksConverter()
        column = PEDLColumn(width="50%")
        result = converter._convert_column(column, "parent123")
        assert result["name"] == "column"
        assert result["parent"] == "parent123"
        assert result["settings"]["width"] == "50%"

    def test_convert_column_invalid_width(self):
        converter = BricksConverter()
        column = PEDLColumn(width="invalid")
        result = converter._convert_column(column, "parent123")
        # 无效宽度回退到 50
        assert result["settings"]["width"] == "50%"

    def test_convert_column_with_advanced_settings(self):
        converter = BricksConverter()
        column = PEDLColumn(width="50%")
        column.settings.element_id = "col-1"
        column.settings.css_classes = "col-class"

        result = converter._convert_column(column, "parent123")
        assert result["settings"]["_cssId"] == "col-1"
        assert result["settings"]["_cssClasses"] == "col-class"

    def test_convert_column_with_widgets(self):
        converter = BricksConverter()
        column = PEDLColumn(width="50%")
        widget = PEDLWidget(
            widget_type=WidgetType.HEADING,
            content={"title": "Hello"},
        )
        column.widgets.append(widget)

        result = converter._convert_column(column, "parent123")
        assert len(result["children"]) == 1
        assert result["children"][0]["name"] == "heading"


class TestBricksWidgetContentConversion:
    """小部件内容转换测试"""

    def test_convert_heading_widget(self):
        converter = BricksConverter()
        widget = PEDLWidget(
            widget_type=WidgetType.HEADING,
            content={"title": "Hello World", "size": "h1", "align": "center"},
        )
        result = converter._convert_widget(widget, "parent1")
        assert result["name"] == "heading"
        assert result["settings"]["text"] == "Hello World"
        assert result["settings"]["tag"] == "h1"
        assert result["settings"]["align"] == "center"

    def test_convert_heading_widget_default_tag(self):
        converter = BricksConverter()
        widget = PEDLWidget(
            widget_type=WidgetType.HEADING,
            content={"title": "Hello", "size": "unknown"},
        )
        result = converter._convert_widget(widget, "parent1")
        assert result["settings"]["tag"] == "h2"

    def test_convert_text_editor_widget(self):
        converter = BricksConverter()
        widget = PEDLWidget(
            widget_type=WidgetType.TEXT_EDITOR,
            content={"editor": "<p>Some text</p>"},
        )
        result = converter._convert_widget(widget, "parent1")
        assert result["settings"]["text"] == "<p>Some text</p>"

    def test_convert_image_widget_dict(self):
        converter = BricksConverter()
        widget = PEDLWidget(
            widget_type=WidgetType.IMAGE,
            content={
                "image": {"url": "https://example.com/img.jpg", "id": 5},
                "alt": "Alt text",
                "caption": "Caption",
            },
        )
        result = converter._convert_widget(widget, "parent1")
        assert result["settings"]["image"]["url"] == "https://example.com/img.jpg"
        assert result["settings"]["image"]["id"] == 5
        assert result["settings"]["alt"] == "Alt text"
        assert result["settings"]["caption"] == "Caption"

    def test_convert_image_widget_string(self):
        converter = BricksConverter()
        widget = PEDLWidget(
            widget_type=WidgetType.IMAGE,
            content={"image": "https://example.com/img.jpg"},
        )
        result = converter._convert_widget(widget, "parent1")
        assert result["settings"]["image"]["url"] == "https://example.com/img.jpg"
        assert result["settings"]["image"]["id"] == 0

    def test_convert_button_widget_dict_link(self):
        converter = BricksConverter()
        widget = PEDLWidget(
            widget_type=WidgetType.BUTTON,
            content={
                "text": "Click",
                "link": {"url": "https://example.com", "is_external": True, "nofollow": True},
                "size": "lg",
                "icon": "fa-star",
            },
        )
        result = converter._convert_widget(widget, "parent1")
        assert result["settings"]["text"] == "Click"
        assert result["settings"]["link"]["url"] == "https://example.com"
        assert result["settings"]["link"]["target"] == "_blank"
        assert result["settings"]["link"]["nofollow"] is True
        assert result["settings"]["size"] == "lg"
        assert result["settings"]["icon"]["icon"] == "fa-star"

    def test_convert_button_widget_string_link(self):
        converter = BricksConverter()
        widget = PEDLWidget(
            widget_type=WidgetType.BUTTON,
            content={"text": "Click", "link": "https://example.com"},
        )
        result = converter._convert_widget(widget, "parent1")
        assert result["settings"]["link"]["url"] == "https://example.com"
        assert result["settings"]["link"]["target"] == "_self"

    def test_convert_button_widget_default_size(self):
        converter = BricksConverter()
        widget = PEDLWidget(
            widget_type=WidgetType.BUTTON,
            content={"text": "Click", "size": "unknown"},
        )
        result = converter._convert_widget(widget, "parent1")
        assert result["settings"]["size"] == "md"

    def test_convert_icon_box_widget(self):
        converter = BricksConverter()
        widget = PEDLWidget(
            widget_type=WidgetType.ICON_BOX,
            content={
                "icon": "fa-star",
                "title_text": "Title",
                "description_text": "Desc",
                "icon_position": "left",
            },
        )
        result = converter._convert_widget(widget, "parent1")
        assert result["settings"]["icon"]["icon"] == "fa-star"
        assert result["settings"]["title"] == "Title"
        assert result["settings"]["description"] == "Desc"
        assert result["settings"]["iconPosition"] == "left"

    def test_convert_accordion_widget(self):
        converter = BricksConverter()
        widget = PEDLWidget(
            widget_type=WidgetType.ACCORDION,
            content={"tabs": [{"title": "T1", "content": "C1"}]},
        )
        result = converter._convert_widget(widget, "parent1")
        assert result["settings"]["items"] == [{"title": "T1", "content": "C1"}]

    def test_convert_tabs_widget(self):
        converter = BricksConverter()
        widget = PEDLWidget(
            widget_type=WidgetType.TABS,
            content={"tabs": [{"title": "T1"}]},
        )
        result = converter._convert_widget(widget, "parent1")
        assert result["settings"]["tabs"] == [{"title": "T1"}]

    def test_convert_testimonial_widget(self):
        converter = BricksConverter()
        widget = PEDLWidget(
            widget_type=WidgetType.TESTIMONIAL,
            content={
                "content": "Great!",
                "name": "John",
                "title": "CEO",
                "image": "https://example.com/john.jpg",
                "rating": 5,
            },
        )
        result = converter._convert_widget(widget, "parent1")
        assert result["settings"]["content"] == "Great!"
        assert result["settings"]["name"] == "John"
        assert result["settings"]["role"] == "CEO"
        assert result["settings"]["image"]["url"] == "https://example.com/john.jpg"
        assert result["settings"]["rating"] == 5

    def test_convert_countdown_widget(self):
        converter = BricksConverter()
        widget = PEDLWidget(
            widget_type=WidgetType.COUNTDOWN,
            content={
                "due_date": "2024-12-31",
                "label_days": "Days",
                "label_hours": "Hours",
                "label_minutes": "Minutes",
                "label_seconds": "Seconds",
            },
        )
        result = converter._convert_widget(widget, "parent1")
        assert result["settings"]["dueDate"] == "2024-12-31"
        assert result["settings"]["daysLabel"] == "Days"
        assert result["settings"]["hoursLabel"] == "Hours"
        assert result["settings"]["minutesLabel"] == "Minutes"
        assert result["settings"]["secondsLabel"] == "Seconds"

    def test_convert_progress_bar_widget(self):
        converter = BricksConverter()
        widget = PEDLWidget(
            widget_type=WidgetType.PROGRESS_BAR,
            content={
                "title": "Progress",
                "percentage": 75,
                "display_percentage": True,
            },
        )
        result = converter._convert_widget(widget, "parent1")
        assert result["settings"]["label"] == "Progress"
        assert result["settings"]["percentage"] == 75
        assert result["settings"]["showPercentage"] is True

    def test_convert_alert_widget(self):
        converter = BricksConverter()
        widget = PEDLWidget(
            widget_type=WidgetType.ALERT,
            content={
                "alert_title": "Warning",
                "alert_description": "Be careful",
                "type": "warning",
                "show_dismiss": True,
            },
        )
        result = converter._convert_widget(widget, "parent1")
        assert result["settings"]["title"] == "Warning"
        assert result["settings"]["text"] == "Be careful"
        assert result["settings"]["type"] == "warning"
        assert result["settings"]["dismissible"] is True

    def test_convert_html_widget(self):
        converter = BricksConverter()
        widget = PEDLWidget(
            widget_type=WidgetType.HTML,
            content={"html": "<div>custom</div>"},
        )
        result = converter._convert_widget(widget, "parent1")
        assert result["settings"]["code"] == "<div>custom</div>"

    def test_convert_shortcode_widget(self):
        converter = BricksConverter()
        widget = PEDLWidget(
            widget_type=WidgetType.SHORTCODE,
            content={"shortcode": "[contact-form]"},
        )
        result = converter._convert_widget(widget, "parent1")
        assert result["settings"]["shortcode"] == "[contact-form]"

    def test_convert_divider_widget(self):
        converter = BricksConverter()
        widget = PEDLWidget(
            widget_type=WidgetType.DIVIDER,
            content={"style": "solid", "weight": "2", "width": "50", "align": "center"},
        )
        result = converter._convert_widget(widget, "parent1")
        assert result["settings"]["style"] == "solid"
        assert result["settings"]["weight"] == "2"
        assert result["settings"]["width"] == "50%"
        assert result["settings"]["align"] == "center"

    def test_convert_spacer_widget(self):
        converter = BricksConverter()
        widget = PEDLWidget(
            widget_type=WidgetType.SPACER,
            content={"space": 30},
        )
        result = converter._convert_widget(widget, "parent1")
        assert result["settings"]["height"] == "30px"

    def test_convert_product_price_widget(self):
        converter = BricksConverter()
        widget = PEDLWidget(
            widget_type=WidgetType.PRODUCT_PRICE,
            content={"product_id": 123},
        )
        result = converter._convert_widget(widget, "parent1")
        assert result["settings"]["productId"] == 123

    def test_convert_add_to_cart_widget(self):
        converter = BricksConverter()
        widget = PEDLWidget(
            widget_type=WidgetType.ADD_TO_CART,
            content={
                "product_id": 456,
                "quantity": 2,
                "show_quantity": True,
            },
        )
        result = converter._convert_widget(widget, "parent1")
        assert result["settings"]["productId"] == 456
        assert result["settings"]["quantity"] == 2
        assert result["settings"]["showQuantity"] is True

    def test_convert_products_widget(self):
        converter = BricksConverter()
        widget = PEDLWidget(
            widget_type=WidgetType.PRODUCTS,
            content={
                "posts_per_page": 12,
                "columns": 4,
                "orderby": "date",
                "order": "DESC",
                "categories": ["shoes", "shirts"],
            },
        )
        result = converter._convert_widget(widget, "parent1")
        assert result["settings"]["postsPerPage"] == 12
        assert result["settings"]["columns"] == 4
        assert result["settings"]["orderBy"] == "date"
        assert result["settings"]["order"] == "DESC"
        assert result["settings"]["categories"] == ["shoes", "shirts"]

    def test_convert_unknown_widget_type_falls_back_to_text(self):
        converter = BricksConverter()
        widget = PEDLWidget(
            widget_type=WidgetType.FORM,
            content={},
        )
        result = converter._convert_widget(widget, "parent1")
        # FORM 不在映射中，回退到 text
        assert result["name"] == "text"

    def test_convert_widget_with_children(self):
        converter = BricksConverter()
        parent = PEDLWidget(
            widget_type=WidgetType.ACCORDION,
            content={"tabs": []},
        )
        child = PEDLWidget(
            widget_type=WidgetType.HEADING,
            content={"title": "Child"},
        )
        parent.children.append(child)

        result = converter._convert_widget(parent, "parent1")
        assert len(result["children"]) == 1
        assert result["children"][0]["name"] == "heading"

    def test_convert_widget_with_advanced_settings(self):
        converter = BricksConverter()
        widget = PEDLWidget(
            widget_type=WidgetType.HEADING,
            content={"title": "Hi"},
        )
        widget.settings.element_id = "widget-1"
        widget.settings.css_classes = "widget-class"
        widget.settings.custom_css = ".w { color: blue; }"
        widget.settings.hide_on_tablet = True

        result = converter._convert_widget(widget, "parent1")
        assert result["settings"]["_cssId"] == "widget-1"
        assert result["settings"]["_cssClasses"] == "widget-class"
        assert result["settings"]["_customCSS"] == ".w { color: blue; }"
        assert result["settings"]["_visibility:hide_tablet"] is True


class TestBricksStyleConversion:
    """样式转换测试"""

    def test_convert_style_empty(self):
        converter = BricksConverter()
        settings = PEDLSettings()
        result = converter._convert_style_settings(settings)
        assert result == {}

    def test_convert_style_alignment(self):
        converter = BricksConverter()
        style = PEDLStyle(alignment=Alignment.CENTER)
        settings = PEDLSettings(style=style)
        result = converter._convert_style_settings(settings)
        assert result["align"] == "center"

    def test_convert_style_text_color(self):
        converter = BricksConverter()
        style = PEDLStyle(text_color="#ff0000")
        settings = PEDLSettings(style=style)
        result = converter._convert_style_settings(settings)
        assert result["color"] == "#ff0000"

    def test_convert_style_with_typography(self):
        converter = BricksConverter()
        typo = PEDLTypography(
            font_family="Arial",
            font_size=16,
            font_weight="bold",
            line_height=1.5,
            letter_spacing=2,
        )
        style = PEDLStyle(typography=typo)
        settings = PEDLSettings(style=style)
        result = converter._convert_style_settings(settings)
        assert result["fontFamily"] == "Arial"
        assert result["fontSize"] == "16px"
        assert result["fontWeight"] == "bold"
        assert result["lineHeight"] == "1.5em"
        assert result["letterSpacing"] == "2px"

    def test_convert_style_opacity(self):
        converter = BricksConverter()
        style = PEDLStyle(opacity=0.5)
        settings = PEDLSettings(style=style)
        result = converter._convert_style_settings(settings)
        assert result["opacity"] == 0.5

    def test_convert_style_z_index(self):
        converter = BricksConverter()
        style = PEDLStyle(z_index=10)
        settings = PEDLSettings(style=style)
        result = converter._convert_style_settings(settings)
        assert result["zIndex"] == 10

    def test_convert_style_width(self):
        converter = BricksConverter()
        style = PEDLStyle(width="100%")
        settings = PEDLSettings(style=style)
        result = converter._convert_style_settings(settings)
        assert result["width"] == "100%"
