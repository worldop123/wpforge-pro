"""
PEDL - Page Element Description Language
页面元素描述语言 - 统一抽象层

这是一个JSON中间格式，用于描述页面结构和样式，
可以转换为Elementor、Bricks等多种页面构建器格式。
"""
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json


class WidgetType(str, Enum):
    """小部件类型"""
    # 基础元素
    HEADING = "heading"
    TEXT_EDITOR = "text_editor"
    IMAGE = "image"
    BUTTON = "button"
    DIVIDER = "divider"
    SPACER = "spacer"
    ICON = "icon"
    ICON_BOX = "icon_box"
    ICON_LIST = "icon_list"
    
    # 布局元素
    SECTION = "section"
    COLUMN = "column"
    INNER_SECTION = "inner_section"
    
    # 媒体元素
    IMAGE_GALLERY = "image_gallery"
    IMAGE_CAROUSEL = "image_carousel"
    VIDEO = "video"
    
    # 内容元素
    POSTS = "posts"
    TESTIMONIAL = "testimonial"
    TESTIMONIAL_CAROUSEL = "testimonial_carousel"
    ACCORDION = "accordion"
    TABS = "tabs"
    TOGGLE = "toggle"
    
    # 表单元素
    FORM = "form"
    
    # WooCommerce元素
    PRODUCT = "product"
    PRODUCTS = "products"
    PRODUCT_CAROUSEL = "product_carousel"
    ADD_TO_CART = "add_to_cart"
    PRODUCT_PRICE = "product_price"
    PRODUCT_TITLE = "product_title"
    PRODUCT_IMAGE = "product_image"
    PRODUCT_DESCRIPTION = "product_description"
    PRODUCT_RATING = "product_rating"
    PRODUCT_META = "product_meta"
    PRODUCT_ADDITIONAL_INFORMATION = "product_additional_information"
    PRODUCT_DATA_TABS = "product_data_tabs"
    PRODUCT_RELATED = "product_related"
    PRODUCT_UPSELLS = "product_upsells"
    
    # 营销元素
    COUNTDOWN = "countdown"
    PROGRESS_BAR = "progress_bar"
    ALERT = "alert"
    CALLOUT = "callout"
    FLIP_BOX = "flip_box"
    HOVER_CARD = "hover_card"
    PRICING_TABLE = "pricing_table"
    TEAM_MEMBER = "team_member"
    
    # 导航元素
    NAV_MENU = "nav_menu"
    BREADCRUMBS = "breadcrumbs"
    PAGINATION = "pagination"
    
    # 其他
    SHORTCODE = "shortcode"
    HTML = "html"
    WORDPRESS = "wordpress"
    SITE_LOGO = "site_logo"
    SITE_TITLE = "site_title"
    SITE_TAGLINE = "site_tagline"
    POST_TITLE = "post_title"
    POST_EXCERPT = "post_excerpt"
    POST_CONTENT = "post_content"
    POST_FEATURED_IMAGE = "post_featured_image"
    POST_META = "post_meta"
    AUTHOR_BOX = "author_box"
    POST_COMMENTS = "post_comments"
    POST_NAVIGATION = "post_navigation"


class ResponsiveBreakpoint(str, Enum):
    """响应式断点"""
    DESKTOP = "desktop"
    TABLET = "tablet"
    MOBILE = "mobile"


class Alignment(str, Enum):
    """对齐方式"""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"


class BorderStyle(str, Enum):
    """边框样式"""
    NONE = "none"
    SOLID = "solid"
    DOUBLE = "double"
    DOTTED = "dotted"
    DASHED = "dashed"
    GROOVE = "groove"
    RIDGE = "ridge"
    INSET = "inset"
    OUTSET = "outset"


class BackgroundType(str, Enum):
    """背景类型"""
    NONE = "none"
    CLASSIC = "classic"
    GRADIENT = "gradient"
    SLIDESHOW = "slideshow"
    VIDEO = "video"


class AnimationType(str, Enum):
    """动画类型"""
    NONE = "none"
    FADE_IN = "fadeIn"
    FADE_IN_UP = "fadeInUp"
    FADE_IN_DOWN = "fadeInDown"
    FADE_IN_LEFT = "fadeInLeft"
    FADE_IN_RIGHT = "fadeInRight"
    ZOOM_IN = "zoomIn"
    ZOOM_IN_UP = "zoomInUp"
    ZOOM_IN_DOWN = "zoomInDown"
    BOUNCE_IN = "bounceIn"
    BOUNCE_IN_UP = "bounceInUp"
    SLIDE_IN_UP = "slideInUp"
    SLIDE_IN_DOWN = "slideInDown"
    SLIDE_IN_LEFT = "slideInLeft"
    SLIDE_IN_RIGHT = "slideInRight"


@dataclass
class PEDLDimension:
    """尺寸设置（支持响应式）"""
    top: Optional[str] = None
    right: Optional[str] = None
    bottom: Optional[str] = None
    left: Optional[str] = None
    unit: str = "px"
    
    def to_dict(self) -> dict:
        result = {}
        if self.top is not None:
            result['top'] = self.top
        if self.right is not None:
            result['right'] = self.right
        if self.bottom is not None:
            result['bottom'] = self.bottom
        if self.left is not None:
            result['left'] = self.left
        if self.unit != "px":
            result['unit'] = self.unit
        return result


@dataclass
class PEDLColor:
    """颜色设置"""
    color: Optional[str] = None
    color_type: str = "classic"  # classic, gradient
    
    def to_dict(self) -> dict:
        result = {}
        if self.color is not None:
            result['color'] = self.color
        if self.color_type != "classic":
            result['color_type'] = self.color_type
        return result


@dataclass
class PEDLBorder:
    """边框设置"""
    border_style: BorderStyle = BorderStyle.NONE
    border_width: Optional[PEDLDimension] = None
    border_color: Optional[str] = None
    border_radius: Optional[PEDLDimension] = None
    
    def to_dict(self) -> dict:
        result = {'border_style': self.border_style.value}
        if self.border_width:
            result['border_width'] = self.border_width.to_dict()
        if self.border_color:
            result['border_color'] = self.border_color
        if self.border_radius:
            result['border_radius'] = self.border_radius.to_dict()
        return result


@dataclass
class PEDLBoxShadow:
    """阴影设置"""
    horizontal: int = 0
    vertical: int = 0
    blur: int = 0
    spread: int = 0
    color: str = "rgba(0,0,0,0.3)"
    position: str = "outline"  # outline, inset
    
    def to_dict(self) -> dict:
        return {
            'horizontal': self.horizontal,
            'vertical': self.vertical,
            'blur': self.blur,
            'spread': self.spread,
            'color': self.color,
            'position': self.position,
        }


@dataclass
class PEDLBackground:
    """背景设置"""
    background_type: BackgroundType = BackgroundType.NONE
    background_color: Optional[str] = None
    background_image: Optional[str] = None
    background_position: str = "center center"
    background_size: str = "cover"
    background_repeat: str = "no-repeat"
    background_attachment: str = "scroll"
    background_overlay_color: Optional[str] = None
    gradient_color_a: Optional[str] = None
    gradient_color_b: Optional[str] = None
    gradient_type: str = "linear"
    gradient_angle: int = 180
    gradient_location_a: int = 0
    gradient_location_b: int = 100
    
    def to_dict(self) -> dict:
        result = {'background_type': self.background_type.value}
        if self.background_color:
            result['background_color'] = self.background_color
        if self.background_image:
            result['background_image'] = self.background_image
        if self.background_position != "center center":
            result['background_position'] = self.background_position
        if self.background_size != "cover":
            result['background_size'] = self.background_size
        if self.background_repeat != "no-repeat":
            result['background_repeat'] = self.background_repeat
        if self.background_overlay_color:
            result['background_overlay_color'] = self.background_overlay_color
        if self.gradient_color_a:
            result['gradient_color_a'] = self.gradient_color_a
        if self.gradient_color_b:
            result['gradient_color_b'] = self.gradient_color_b
        if self.gradient_type != "linear":
            result['gradient_type'] = self.gradient_type
        if self.gradient_angle != 180:
            result['gradient_angle'] = self.gradient_angle
        return result


@dataclass
class PEDLTypography:
    """排版设置"""
    font_family: Optional[str] = None
    font_size: Optional[str] = None
    font_weight: Optional[str] = None
    font_style: str = "normal"
    text_transform: str = "none"
    text_decoration: str = "none"
    line_height: Optional[str] = None
    letter_spacing: Optional[str] = None
    word_spacing: Optional[str] = None
    
    def to_dict(self) -> dict:
        result = {}
        if self.font_family:
            result['font_family'] = self.font_family
        if self.font_size:
            result['font_size'] = self.font_size
        if self.font_weight:
            result['font_weight'] = self.font_weight
        if self.font_style != "normal":
            result['font_style'] = self.font_style
        if self.text_transform != "none":
            result['text_transform'] = self.text_transform
        if self.text_decoration != "none":
            result['text_decoration'] = self.text_decoration
        if self.line_height:
            result['line_height'] = self.line_height
        if self.letter_spacing:
            result['letter_spacing'] = self.letter_spacing
        return result


@dataclass
class PEDLResponsive:
    """响应式设置容器"""
    desktop: Optional[Dict[str, Any]] = None
    tablet: Optional[Dict[str, Any]] = None
    mobile: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> dict:
        result = {}
        if self.desktop:
            result['desktop'] = self.desktop
        if self.tablet:
            result['tablet'] = self.tablet
        if self.mobile:
            result['mobile'] = self.mobile
        return result


@dataclass
class PEDLStyle:
    """样式设置"""
    # 布局
    width: Optional[str] = None
    height: Optional[str] = None
    min_height: Optional[str] = None
    max_width: Optional[str] = None
    max_height: Optional[str] = None
    
    # 间距
    margin: Optional[PEDLDimension] = None
    padding: Optional[PEDLDimension] = None
    
    # 对齐
    alignment: Optional[Alignment] = None
    vertical_align: str = "top"
    
    # 颜色
    text_color: Optional[str] = None
    background: Optional[PEDLBackground] = None
    
    # 边框
    border: Optional[PEDLBorder] = None
    
    # 阴影
    box_shadow: Optional[PEDLBoxShadow] = None
    
    # 排版
    typography: Optional[PEDLTypography] = None
    
    # 高级
    z_index: Optional[int] = None
    overflow: str = "visible"
    opacity: float = 1.0
    css_filter: Optional[str] = None
    mix_blend_mode: str = "normal"
    
    # 动画
    entrance_animation: AnimationType = AnimationType.NONE
    animation_duration: float = 1.0
    animation_delay: float = 0.0
    animation_offset: int = 50
    
    # 响应式
    responsive: Optional[PEDLResponsive] = None
    
    # 自定义CSS
    custom_css: Optional[str] = None
    custom_css_classes: Optional[str] = None
    
    def to_dict(self) -> dict:
        result = {}
        
        # 布局
        if self.width:
            result['width'] = self.width
        if self.height:
            result['height'] = self.height
        if self.min_height:
            result['min_height'] = self.min_height
        if self.max_width:
            result['max_width'] = self.max_width
        if self.max_height:
            result['max_height'] = self.max_height
        
        # 间距
        if self.margin:
            result['margin'] = self.margin.to_dict()
        if self.padding:
            result['padding'] = self.padding.to_dict()
        
        # 对齐
        if self.alignment:
            result['alignment'] = self.alignment.value
        if self.vertical_align != "top":
            result['vertical_align'] = self.vertical_align
        
        # 颜色
        if self.text_color:
            result['text_color'] = self.text_color
        if self.background:
            result['background'] = self.background.to_dict()
        
        # 边框
        if self.border:
            result['border'] = self.border.to_dict()
        
        # 阴影
        if self.box_shadow:
            result['box_shadow'] = self.box_shadow.to_dict()
        
        # 排版
        if self.typography:
            result['typography'] = self.typography.to_dict()
        
        # 高级
        if self.z_index is not None:
            result['z_index'] = self.z_index
        if self.overflow != "visible":
            result['overflow'] = self.overflow
        if self.opacity != 1.0:
            result['opacity'] = self.opacity
        if self.css_filter:
            result['css_filter'] = self.css_filter
        if self.mix_blend_mode != "normal":
            result['mix_blend_mode'] = self.mix_blend_mode
        
        # 动画
        if self.entrance_animation != AnimationType.NONE:
            result['entrance_animation'] = self.entrance_animation.value
            result['animation_duration'] = self.animation_duration
            result['animation_delay'] = self.animation_delay
            result['animation_offset'] = self.animation_offset
        
        # 响应式
        if self.responsive:
            result['responsive'] = self.responsive.to_dict()
        
        # 自定义CSS
        if self.custom_css:
            result['custom_css'] = self.custom_css
        if self.custom_css_classes:
            result['custom_css_classes'] = self.custom_css_classes
        
        return result


@dataclass
class PEDLSettings:
    """通用设置"""
    # 基础
    element_id: Optional[str] = None
    title: Optional[str] = None
    
    # 布局
    column_width: Optional[str] = None
    content_width: str = "boxed"  # boxed, full_width
    content_width_value: Optional[str] = None
    columns_gap: str = "default"  # default, no, narrow, extended, wide
    
    # 高级
    css_classes: Optional[str] = None
    custom_css: Optional[str] = None
    
    # 可见性
    hide_on_desktop: bool = False
    hide_on_tablet: bool = False
    hide_on_mobile: bool = False
    
    # 样式
    style: Optional[PEDLStyle] = None
    
    def to_dict(self) -> dict:
        result = {}
        
        if self.element_id:
            result['element_id'] = self.element_id
        if self.title:
            result['title'] = self.title
        if self.column_width:
            result['column_width'] = self.column_width
        if self.content_width != "boxed":
            result['content_width'] = self.content_width
        if self.content_width_value:
            result['content_width_value'] = self.content_width_value
        if self.columns_gap != "default":
            result['columns_gap'] = self.columns_gap
        if self.css_classes:
            result['css_classes'] = self.css_classes
        if self.custom_css:
            result['custom_css'] = self.custom_css
        if self.hide_on_desktop:
            result['hide_on_desktop'] = self.hide_on_desktop
        if self.hide_on_tablet:
            result['hide_on_tablet'] = self.hide_on_tablet
        if self.hide_on_mobile:
            result['hide_on_mobile'] = self.hide_on_mobile
        if self.style:
            result['style'] = self.style.to_dict()
        
        return result


@dataclass
class PEDLWidget:
    """小部件/元素"""
    widget_type: WidgetType
    widget_id: Optional[str] = None
    settings: PEDLSettings = field(default_factory=PEDLSettings)
    
    # 内容设置（根据widget_type不同而不同）
    content: Dict[str, Any] = field(default_factory=dict)
    
    # 子元素（用于嵌套元素如accordion, tabs等）
    children: List['PEDLWidget'] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        result = {
            'widget_type': self.widget_type.value,
            'settings': self.settings.to_dict(),
            'content': self.content,
        }
        
        if self.widget_id:
            result['widget_id'] = self.widget_id
        
        if self.children:
            result['children'] = [child.to_dict() for child in self.children]
        
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PEDLWidget':
        widget_type = WidgetType(data.get('widget_type', 'text_editor'))
        widget = cls(widget_type=widget_type)
        widget.widget_id = data.get('widget_id')
        widget.content = data.get('content', {})
        
        # 解析子元素
        for child_data in data.get('children', []):
            widget.children.append(cls.from_dict(child_data))
        
        return widget


@dataclass
class PEDLColumn:
    """列"""
    column_id: Optional[str] = None
    width: str = "50%"
    settings: PEDLSettings = field(default_factory=PEDLSettings)
    widgets: List[PEDLWidget] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        result = {
            'width': self.width,
            'settings': self.settings.to_dict(),
            'widgets': [widget.to_dict() for widget in self.widgets],
        }
        
        if self.column_id:
            result['column_id'] = self.column_id
        
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PEDLColumn':
        column = cls()
        column.column_id = data.get('column_id')
        column.width = data.get('width', '50%')
        
        # 解析小部件
        for widget_data in data.get('widgets', []):
            column.widgets.append(PEDLWidget.from_dict(widget_data))
        
        return column


@dataclass
class PEDLSection:
    """区块（行）"""
    section_id: Optional[str] = None
    settings: PEDLSettings = field(default_factory=PEDLSettings)
    columns: List[PEDLColumn] = field(default_factory=list)
    
    # 布局
    layout: str = "boxed"  # boxed, full_width, full_width_stretched
    columns_gap: str = "default"  # default, no, narrow, extended, wide
    
    def to_dict(self) -> dict:
        result = {
            'layout': self.layout,
            'columns_gap': self.columns_gap,
            'settings': self.settings.to_dict(),
            'columns': [column.to_dict() for column in self.columns],
        }
        
        if self.section_id:
            result['section_id'] = self.section_id
        
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PEDLSection':
        section = cls()
        section.section_id = data.get('section_id')
        section.layout = data.get('layout', 'boxed')
        section.columns_gap = data.get('columns_gap', 'default')
        
        # 解析列
        for column_data in data.get('columns', []):
            section.columns.append(PEDLColumn.from_dict(column_data))
        
        return section


@dataclass
class PEDLDocument:
    """PEDL文档 - 整个页面"""
    document_id: Optional[str] = None
    title: str = ""
    document_type: str = "page"  # page, post, product, template, section
    settings: Dict[str, Any] = field(default_factory=dict)
    sections: List[PEDLSection] = field(default_factory=list)
    
    # 元数据
    meta: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            'document_id': self.document_id,
            'title': self.title,
            'document_type': self.document_type,
            'settings': self.settings,
            'sections': [section.to_dict() for section in self.sections],
            'meta': self.meta,
            'pedl_version': '1.0.0',
        }
    
    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PEDLDocument':
        """从字典创建"""
        doc = cls()
        doc.document_id = data.get('document_id')
        doc.title = data.get('title', '')
        doc.document_type = data.get('document_type', 'page')
        doc.settings = data.get('settings', {})
        doc.meta = data.get('meta', {})
        
        # 解析区块
        for section_data in data.get('sections', []):
            doc.sections.append(PEDLSection.from_dict(section_data))
        
        return doc
    
    @classmethod
    def from_json(cls, json_str: str) -> 'PEDLDocument':
        """从JSON字符串创建"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def add_section(self, section: PEDLSection) -> None:
        """添加区块"""
        self.sections.append(section)
    
    def create_simple_section(self, content: str, title: str = "") -> PEDLSection:
        """创建简单的文本区块"""
        section = PEDLSection()
        
        column = PEDLColumn(width="100%")
        
        if title:
            heading = PEDLWidget(
                widget_type=WidgetType.HEADING,
                content={'title': title, 'size': 'h2'}
            )
            column.widgets.append(heading)
        
        text = PEDLWidget(
            widget_type=WidgetType.TEXT_EDITOR,
            content={'editor': content}
        )
        column.widgets.append(text)
        
        section.columns.append(column)
        self.sections.append(section)
        
        return section
    
    def create_hero_section(self, title: str, subtitle: str = "", button_text: str = "", button_url: str = "", background_image: str = "") -> PEDLSection:
        """创建Hero区块"""
        section = PEDLSection(layout="full_width")
        
        # 设置背景
        if background_image:
            section.settings.style = PEDLStyle()
            section.settings.style.background = PEDLBackground(
                background_type=BackgroundType.CLASSIC,
                background_image=background_image,
                background_overlay_color="rgba(0,0,0,0.5)"
            )
            section.settings.style.padding = PEDLDimension(top="100px", bottom="100px")
        
        column = PEDLColumn(width="100%")
        column.settings.style = PEDLStyle(alignment=Alignment.CENTER)
        
        # 标题
        heading = PEDLWidget(
            widget_type=WidgetType.HEADING,
            content={'title': title, 'size': 'h1'}
        )
        heading.settings.style = PEDLStyle(text_color="#ffffff")
        column.widgets.append(heading)
        
        # 副标题
        if subtitle:
            text = PEDLWidget(
                widget_type=WidgetType.TEXT_EDITOR,
                content={'editor': subtitle}
            )
            text.settings.style = PEDLStyle(text_color="#ffffff")
            column.widgets.append(text)
        
        # 按钮
        if button_text:
            button = PEDLWidget(
                widget_type=WidgetType.BUTTON,
                content={
                    'text': button_text,
                    'link': {'url': button_url, 'is_external': False},
                }
            )
            column.widgets.append(button)
        
        section.columns.append(column)
        self.sections.append(section)
        
        return section
    
    def create_features_section(self, features: List[Dict[str, str]], title: str = "") -> PEDLSection:
        """创建特性/功能区块"""
        section = PEDLSection()
        
        # 标题
        if title:
            title_column = PEDLColumn(width="100%")
            heading = PEDLWidget(
                widget_type=WidgetType.HEADING,
                content={'title': title, 'size': 'h2', 'align': 'center'}
            )
            title_column.widgets.append(heading)
            section.columns.append(title_column)
        
        # 特性列
        columns_count = len(features)
        column_width = f"{100 // columns_count}%"
        
        for feature in features:
            column = PEDLColumn(width=column_width)
            
            icon_box = PEDLWidget(
                widget_type=WidgetType.ICON_BOX,
                content={
                    'icon': feature.get('icon', 'fas fa-star'),
                    'title_text': feature.get('title', ''),
                    'description_text': feature.get('description', ''),
                }
            )
            column.widgets.append(icon_box)
            
            section.columns.append(column)
        
        self.sections.append(section)
        
        return section
    
    def create_products_section(self, products: List[Dict[str, Any]], title: str = "", columns: int = 4) -> PEDLSection:
        """创建产品区块"""
        section = PEDLSection()
        
        # 标题
        if title:
            title_column = PEDLColumn(width="100%")
            heading = PEDLWidget(
                widget_type=WidgetType.HEADING,
                content={'title': title, 'size': 'h2', 'align': 'center'}
            )
            title_column.widgets.append(heading)
            section.columns.append(title_column)
        
        # 产品列
        column_width = f"{100 // columns}%"
        
        for product in products:
            column = PEDLColumn(width=column_width)
            
            # 产品图片
            if product.get('image'):
                image = PEDLWidget(
                    widget_type=WidgetType.IMAGE,
                    content={
                        'image': {'url': product['image']},
                        'title': product.get('name', ''),
                        'alt': product.get('name', ''),
                    }
                )
                column.widgets.append(image)
            
            # 产品标题
            name = PEDLWidget(
                widget_type=WidgetType.HEADING,
                content={'title': product.get('name', ''), 'size': 'h3'}
            )
            column.widgets.append(name)
            
            # 产品价格
            if product.get('price'):
                price = PEDLWidget(
                    widget_type=WidgetType.TEXT_EDITOR,
                    content={'editor': f'<p class="price">{product["price"]}</p>'}
                )
                column.widgets.append(price)
            
            # 按钮
            button = PEDLWidget(
                widget_type=WidgetType.BUTTON,
                content={
                    'text': '查看详情',
                    'link': {'url': product.get('url', '#'), 'is_external': False},
                }
            )
            column.widgets.append(button)
            
            section.columns.append(column)
        
        self.sections.append(section)
        
        return section
    
    def create_testimonials_section(self, testimonials: List[Dict[str, str]], title: str = "") -> PEDLSection:
        """创建评价区块"""
        section = PEDLSection()
        
        # 标题
        if title:
            title_column = PEDLColumn(width="100%")
            heading = PEDLWidget(
                widget_type=WidgetType.HEADING,
                content={'title': title, 'size': 'h2', 'align': 'center'}
            )
            title_column.widgets.append(heading)
            section.columns.append(title_column)
        
        # 评价轮播
        column = PEDLColumn(width="100%")
        
        testimonial_carousel = PEDLWidget(
            widget_type=WidgetType.TESTIMONIAL_CAROUSEL,
            content={'slides': testimonials}
        )
        column.widgets.append(testimonial_carousel)
        
        section.columns.append(column)
        self.sections.append(section)
        
        return section
    
    def create_faq_section(self, faqs: List[Dict[str, str]], title: str = "") -> PEDLSection:
        """创建FAQ区块"""
        section = PEDLSection()
        
        # 标题
        if title:
            title_column = PEDLColumn(width="100%")
            heading = PEDLWidget(
                widget_type=WidgetType.HEADING,
                content={'title': title, 'size': 'h2', 'align': 'center'}
            )
            title_column.widgets.append(heading)
            section.columns.append(title_column)
        
        # FAQ手风琴
        column = PEDLColumn(width="100%")
        
        accordion = PEDLWidget(widget_type=WidgetType.ACCORDION)
        
        for faq in faqs:
            tab = PEDLWidget(
                widget_type=WidgetType.TOGGLE,
                content={
                    'tab_title': faq.get('question', ''),
                    'tab_content': faq.get('answer', ''),
                }
            )
            accordion.children.append(tab)
        
        column.widgets.append(accordion)
        
        section.columns.append(column)
        self.sections.append(section)
        
        return section
    
    def create_cta_section(self, title: str, description: str = "", button_text: str = "", button_url: str = "") -> PEDLSection:
        """创建CTA区块"""
        section = PEDLSection()
        section.settings.style = PEDLStyle(
            background=PEDLBackground(
                background_type=BackgroundType.CLASSIC,
                background_color="#f8f9fa"
            ),
            padding=PEDLDimension(top="60px", bottom="60px")
        )
        
        column = PEDLColumn(width="100%")
        column.settings.style = PEDLStyle(alignment=Alignment.CENTER)
        
        # 标题
        heading = PEDLWidget(
            widget_type=WidgetType.HEADING,
            content={'title': title, 'size': 'h2'}
        )
        column.widgets.append(heading)
        
        # 描述
        if description:
            text = PEDLWidget(
                widget_type=WidgetType.TEXT_EDITOR,
                content={'editor': description}
            )
            column.widgets.append(text)
        
        # 按钮
        if button_text:
            button = PEDLWidget(
                widget_type=WidgetType.BUTTON,
                content={
                    'text': button_text,
                    'link': {'url': button_url, 'is_external': False},
                    'size': 'lg',
                }
            )
            column.widgets.append(button)
        
        section.columns.append(column)
        self.sections.append(section)
        
        return section
