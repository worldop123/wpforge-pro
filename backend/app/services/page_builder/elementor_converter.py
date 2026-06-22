"""
Elementor转换器
将PEDL格式转换为Elementor数据格式，支持直接写入WordPress数据库
"""
import uuid
from typing import Dict, Any, List, Optional
from app.core.logging import get_logger
from app.services.page_builder.pedl import (
    PEDLDocument,
    PEDLSection,
    PEDLColumn,
    PEDLWidget,
    WidgetType,
    Alignment,
)

logger = get_logger(__name__)


class ElementorConverter:
    """Elementor转换器"""
    
    def __init__(self):
        self.widget_type_map = self._build_widget_type_map()
    
    def _build_widget_type_map(self) -> Dict[WidgetType, str]:
        """构建小部件类型映射"""
        return {
            # 基础元素
            WidgetType.HEADING: "heading",
            WidgetType.TEXT_EDITOR: "text-editor",
            WidgetType.IMAGE: "image",
            WidgetType.BUTTON: "button",
            WidgetType.DIVIDER: "divider",
            WidgetType.SPACER: "spacer",
            WidgetType.ICON: "icon",
            WidgetType.ICON_BOX: "icon-box",
            WidgetType.ICON_LIST: "icon-list",
            
            # 媒体元素
            WidgetType.IMAGE_GALLERY: "gallery",
            WidgetType.IMAGE_CAROUSEL: "image-carousel",
            WidgetType.VIDEO: "video",
            
            # 内容元素
            WidgetType.POSTS: "posts",
            WidgetType.TESTIMONIAL: "testimonial",
            WidgetType.TESTIMONIAL_CAROUSEL: "testimonial-carousel",
            WidgetType.ACCORDION: "accordion",
            WidgetType.TABS: "tabs",
            WidgetType.TOGGLE: "toggle",
            
            # WooCommerce元素
            WidgetType.PRODUCT: "woocommerce-product",
            WidgetType.PRODUCTS: "woocommerce-products",
            WidgetType.PRODUCT_CAROUSEL: "woocommerce-product-carousel",
            WidgetType.ADD_TO_CART: "woocommerce-add-to-cart",
            WidgetType.PRODUCT_PRICE: "woocommerce-product-price",
            WidgetType.PRODUCT_TITLE: "woocommerce-product-title",
            WidgetType.PRODUCT_IMAGE: "woocommerce-product-image",
            WidgetType.PRODUCT_DESCRIPTION: "woocommerce-product-description",
            WidgetType.PRODUCT_RATING: "woocommerce-product-rating",
            WidgetType.PRODUCT_META: "woocommerce-product-meta",
            WidgetType.PRODUCT_ADDITIONAL_INFORMATION: "woocommerce-product-additional-information",
            WidgetType.PRODUCT_DATA_TABS: "woocommerce-product-data-tabs",
            WidgetType.PRODUCT_RELATED: "woocommerce-product-related",
            WidgetType.PRODUCT_UPSELLS: "woocommerce-product-upsells",
            
            # 营销元素
            WidgetType.COUNTDOWN: "countdown",
            WidgetType.PROGRESS_BAR: "progress-bar",
            WidgetType.ALERT: "alert",
            WidgetType.CALLOUT: "callout",
            WidgetType.FLIP_BOX: "flip-box",
            WidgetType.HOVER_CARD: "hover-card",
            WidgetType.PRICING_TABLE: "price-table",
            WidgetType.TEAM_MEMBER: "team-member",
            
            # 导航元素
            WidgetType.NAV_MENU: "nav-menu",
            WidgetType.BREADCRUMBS: "breadcrumbs",
            WidgetType.PAGINATION: "pagination",
            
            # 其他
            WidgetType.SHORTCODE: "shortcode",
            WidgetType.HTML: "html",
            WidgetType.SITE_LOGO: "site-logo",
            WidgetType.SITE_TITLE: "site-title",
            WidgetType.SITE_TAGLINE: "site-tagline",
            WidgetType.POST_TITLE: "post-title",
            WidgetType.POST_EXCERPT: "post-excerpt",
            WidgetType.POST_CONTENT: "post-content",
            WidgetType.POST_FEATURED_IMAGE: "post-featured-image",
            WidgetType.POST_META: "post-meta",
            WidgetType.AUTHOR_BOX: "author-box",
            WidgetType.POST_COMMENTS: "post-comments",
            WidgetType.POST_NAVIGATION: "post-navigation",
        }
    
    def _generate_id(self) -> str:
        """生成Elementor元素ID"""
        return uuid.uuid4().hex[:10]
    
    def convert(self, pedl_document: PEDLDocument) -> List[Dict[str, Any]]:
        """
        将PEDL文档转换为Elementor数据格式
        
        Args:
            pedl_document: PEDL文档
            
        Returns:
            Elementor数据列表（可直接写入_elementor_data）
        """
        elementor_data = []
        
        for section in pedl_document.sections:
            elementor_section = self._convert_section(section)
            elementor_data.append(elementor_section)
        
        return elementor_data
    
    def _convert_section(self, section: PEDLSection) -> Dict[str, Any]:
        """转换区块"""
        section_id = section.section_id or self._generate_id()
        
        elementor_section = {
            "id": section_id,
            "elType": "section",
            "settings": self._convert_section_settings(section),
            "elements": [],
        }
        
        # 转换列
        for column in section.columns:
            elementor_column = self._convert_column(column)
            elementor_section["elements"].append(elementor_column)
        
        return elementor_section
    
    def _convert_section_settings(self, section: PEDLSection) -> Dict[str, Any]:
        """转换区块设置"""
        settings = {}
        
        # 布局设置
        if section.layout == "full_width":
            settings["layout"] = "full_width"
        elif section.layout == "full_width_stretched":
            settings["layout"] = "full_width_stretched"
        else:
            settings["layout"] = "boxed"
        
        if section.columns_gap != "default":
            settings["gap"] = section.columns_gap
        
        # 样式设置
        style_settings = self._convert_style_settings(section.settings)
        settings.update(style_settings)
        
        # 高级设置
        if section.settings.element_id:
            settings["_element_id"] = section.settings.element_id
        
        if section.settings.css_classes:
            settings["css_classes"] = section.settings.css_classes
        
        if section.settings.custom_css:
            settings["custom_css"] = section.settings.custom_css
        
        # 可见性
        if section.settings.hide_on_desktop:
            settings["hide_desktop"] = "yes"
        if section.settings.hide_on_tablet:
            settings["hide_tablet"] = "yes"
        if section.settings.hide_on_mobile:
            settings["hide_mobile"] = "yes"
        
        return settings
    
    def _convert_column(self, column: PEDLColumn) -> Dict[str, Any]:
        """转换列"""
        column_id = column.column_id or self._generate_id()
        
        # 转换宽度百分比为Elementor格式
        width_percent = column.width.replace("%", "")
        try:
            width_int = int(float(width_percent))
        except (ValueError, TypeError):
            width_int = 50
        
        elementor_column = {
            "id": column_id,
            "elType": "column",
            "settings": {
                "_column_size": width_int,
            },
            "elements": [],
        }
        
        # 样式设置
        style_settings = self._convert_style_settings(column.settings)
        elementor_column["settings"].update(style_settings)
        
        # 高级设置
        if column.settings.element_id:
            elementor_column["settings"]["_element_id"] = column.settings.element_id
        
        if column.settings.css_classes:
            elementor_column["settings"]["css_classes"] = column.settings.css_classes
        
        # 转换小部件
        for widget in column.widgets:
            elementor_widget = self._convert_widget(widget)
            elementor_column["elements"].append(elementor_widget)
        
        return elementor_column
    
    def _convert_widget(self, widget: PEDLWidget) -> Dict[str, Any]:
        """转换小部件"""
        widget_id = widget.widget_id or self._generate_id()
        widget_type = self.widget_type_map.get(widget.widget_type, "text-editor")
        
        elementor_widget = {
            "id": widget_id,
            "elType": "widget",
            "widgetType": widget_type,
            "settings": {},
            "elements": [],
        }
        
        # 转换内容设置
        content_settings = self._convert_widget_content(widget)
        elementor_widget["settings"].update(content_settings)
        
        # 转换样式设置
        style_settings = self._convert_style_settings(widget.settings)
        elementor_widget["settings"].update(style_settings)
        
        # 高级设置
        if widget.settings.element_id:
            elementor_widget["settings"]["_element_id"] = widget.settings.element_id
        
        if widget.settings.css_classes:
            elementor_widget["settings"]["css_classes"] = widget.settings.css_classes
        
        if widget.settings.custom_css:
            elementor_widget["settings"]["custom_css"] = widget.settings.custom_css
        
        # 可见性
        if widget.settings.hide_on_desktop:
            elementor_widget["settings"]["hide_desktop"] = "yes"
        if widget.settings.hide_on_tablet:
            elementor_widget["settings"]["hide_tablet"] = "yes"
        if widget.settings.hide_on_mobile:
            elementor_widget["settings"]["hide_mobile"] = "yes"
        
        # 转换子元素
        if widget.children:
            elementor_widget["elements"] = [
                self._convert_widget(child) for child in widget.children
            ]
        
        return elementor_widget
    
    def _convert_widget_content(self, widget: PEDLWidget) -> Dict[str, Any]:
        """转换小部件内容设置"""
        content = widget.content
        settings = {}
        
        widget_type = widget.widget_type
        
        # 标题小部件
        if widget_type == WidgetType.HEADING:
            if "title" in content:
                settings["title"] = content["title"]
            if "size" in content:
                size_map = {
                    "h1": "h1",
                    "h2": "h2",
                    "h3": "h3",
                    "h4": "h4",
                    "h5": "h5",
                    "h6": "h6",
                }
                settings["size"] = size_map.get(content["size"], "h2")
            if "align" in content:
                settings["align"] = content["align"]
        
        # 文本编辑器小部件
        elif widget_type == WidgetType.TEXT_EDITOR:
            if "editor" in content:
                settings["editor"] = content["editor"]
        
        # 图片小部件
        elif widget_type == WidgetType.IMAGE:
            if "image" in content:
                image_data = content["image"]
                if isinstance(image_data, dict) and "url" in image_data:
                    settings["image"] = {
                        "url": image_data["url"],
                        "id": image_data.get("id", ""),
                    }
                elif isinstance(image_data, str):
                    settings["image"] = {"url": image_data, "id": ""}
            if "alt" in content:
                settings["image_alt"] = content["alt"]
            if "title" in content:
                settings["title"] = content["title"]
            if "caption" in content:
                settings["caption"] = content["caption"]
        
        # 按钮小部件
        elif widget_type == WidgetType.BUTTON:
            if "text" in content:
                settings["text"] = content["text"]
            if "link" in content:
                link_data = content["link"]
                if isinstance(link_data, dict):
                    settings["link"] = {
                        "url": link_data.get("url", ""),
                        "is_external": link_data.get("is_external", False),
                        "nofollow": link_data.get("nofollow", False),
                    }
                elif isinstance(link_data, str):
                    settings["link"] = {"url": link_data, "is_external": False}
            if "size" in content:
                settings["size"] = content["size"]
            if "icon" in content:
                settings["selected_icon"] = {"value": content["icon"], "library": "fa-solid"}
            if "icon_align" in content:
                settings["icon_align"] = content["icon_align"]
        
        # 图标框小部件
        elif widget_type == WidgetType.ICON_BOX:
            if "icon" in content:
                settings["selected_icon"] = {"value": content["icon"], "library": "fa-solid"}
            if "title_text" in content:
                settings["title_text"] = content["title_text"]
            if "description_text" in content:
                settings["description_text"] = content["description_text"]
            if "title_size" in content:
                settings["title_size"] = content["title_size"]
            if "icon_position" in content:
                settings["icon_position"] = content["icon_position"]
        
        # 手风琴小部件
        elif widget_type == WidgetType.ACCORDION:
            if "tabs" in content:
                settings["tabs"] = content["tabs"]
        
        # 标签页小部件
        elif widget_type == WidgetType.TABS:
            if "tabs" in content:
                settings["tabs"] = content["tabs"]
        
        # 评价小部件
        elif widget_type == WidgetType.TESTIMONIAL:
            if "content" in content:
                settings["testimonial_content"] = content["content"]
            if "name" in content:
                settings["testimonial_name"] = content["name"]
            if "title" in content:
                settings["testimonial_title"] = content["title"]
            if "image" in content:
                settings["testimonial_image"] = {"url": content["image"], "id": ""}
            if "rating" in content:
                settings["rating"] = content["rating"]
        
        # 评价轮播小部件
        elif widget_type == WidgetType.TESTIMONIAL_CAROUSEL:
            if "slides" in content:
                slides = []
                for slide in content["slides"]:
                    slide_data = {}
                    if "content" in slide:
                        slide_data["testimonial_content"] = slide["content"]
                    if "name" in slide:
                        slide_data["testimonial_name"] = slide["name"]
                    if "title" in slide:
                        slide_data["testimonial_title"] = slide["title"]
                    if "image" in slide:
                        slide_data["testimonial_image"] = {"url": slide["image"], "id": ""}
                    if "rating" in slide:
                        slide_data["rating"] = slide["rating"]
                    slides.append(slide_data)
                settings["slides"] = slides
        
        # 倒计时小部件
        elif widget_type == WidgetType.COUNTDOWN:
            if "due_date" in content:
                settings["due_date"] = content["due_date"]
            if "show_days" in content:
                settings["show_days"] = "yes" if content["show_days"] else "no"
            if "show_hours" in content:
                settings["show_hours"] = "yes" if content["show_hours"] else "no"
            if "show_minutes" in content:
                settings["show_minutes"] = "yes" if content["show_minutes"] else "no"
            if "show_seconds" in content:
                settings["show_seconds"] = "yes" if content["show_seconds"] else "no"
            if "label_days" in content:
                settings["label_days"] = content["label_days"]
            if "label_hours" in content:
                settings["label_hours"] = content["label_hours"]
            if "label_minutes" in content:
                settings["label_minutes"] = content["label_minutes"]
            if "label_seconds" in content:
                settings["label_seconds"] = content["label_seconds"]
        
        # 进度条小部件
        elif widget_type == WidgetType.PROGRESS_BAR:
            if "title" in content:
                settings["title"] = content["title"]
            if "percentage" in content:
                settings["percentage"] = content["percentage"]
            if "display_percentage" in content:
                settings["display_percentage"] = "yes" if content["display_percentage"] else "no"
            if "inner_text" in content:
                settings["inner_text"] = content["inner_text"]
        
        # 警告框小部件
        elif widget_type == WidgetType.ALERT:
            if "alert_title" in content:
                settings["alert_title"] = content["alert_title"]
            if "alert_description" in content:
                settings["alert_description"] = content["alert_description"]
            if "type" in content:
                settings["type"] = content["type"]
            if "show_dismiss" in content:
                settings["show_dismiss"] = "yes" if content["show_dismiss"] else "no"
        
        # HTML小部件
        elif widget_type == WidgetType.HTML:
            if "html" in content:
                settings["html"] = content["html"]
        
        # 简码小部件
        elif widget_type == WidgetType.SHORTCODE:
            if "shortcode" in content:
                settings["shortcode"] = content["shortcode"]
        
        # 分隔线小部件
        elif widget_type == WidgetType.DIVIDER:
            if "style" in content:
                settings["style"] = content["style"]
            if "weight" in content:
                settings["weight"] = content["weight"]
            if "width" in content:
                settings["width"] = {"unit": "%", "size": content["width"]}
            if "align" in content:
                settings["align"] = content["align"]
        
        # 间隔小部件
        elif widget_type == WidgetType.SPACER:
            if "space" in content:
                settings["space"] = {"unit": "px", "size": content["space"]}
        
        # WooCommerce产品价格
        elif widget_type == WidgetType.PRODUCT_PRICE:
            if "product_id" in content:
                settings["product_id"] = content["product_id"]
        
        # WooCommerce添加到购物车
        elif widget_type == WidgetType.ADD_TO_CART:
            if "product_id" in content:
                settings["product_id"] = content["product_id"]
            if "quantity" in content:
                settings["quantity"] = content["quantity"]
            if "show_quantity" in content:
                settings["show_quantity"] = "yes" if content["show_quantity"] else "no"
        
        # 产品列表
        elif widget_type == WidgetType.PRODUCTS:
            if "posts_per_page" in content:
                settings["posts_per_page"] = content["posts_per_page"]
            if "columns" in content:
                settings["columns"] = content["columns"]
            if "rows" in content:
                settings["rows"] = content["rows"]
            if "orderby" in content:
                settings["orderby"] = content["orderby"]
            if "order" in content:
                settings["order"] = content["order"]
            if "categories" in content:
                settings["categories"] = content["categories"]
        
        return settings
    
    def _convert_style_settings(self, settings) -> Dict[str, Any]:
        """转换样式设置"""
        style = settings.style
        if not style:
            return {}
        
        result = {}
        
        # 对齐
        if style.alignment:
            align_map = {
                Alignment.LEFT: "left",
                Alignment.CENTER: "center",
                Alignment.RIGHT: "right",
                Alignment.JUSTIFY: "justify",
            }
            result["align"] = align_map.get(style.alignment, "left")
        
        # 文本颜色
        if style.text_color:
            result["text_color"] = style.text_color
        
        # 背景
        if style.background:
            bg = style.background
            if bg.background_type.value == "classic":
                result["background_background"] = "classic"
                if bg.background_color:
                    result["background_color"] = bg.background_color
                if bg.background_image:
                    result["background_image"] = {"url": bg.background_image, "id": ""}
                if bg.background_position != "center center":
                    result["background_position"] = bg.background_position
                if bg.background_size != "cover":
                    result["background_size"] = bg.background_size
                if bg.background_repeat != "no-repeat":
                    result["background_repeat"] = bg.background_repeat
            elif bg.background_type.value == "gradient":
                result["background_background"] = "gradient"
                if bg.gradient_color_a:
                    result["background_color"] = bg.gradient_color_a
                if bg.gradient_color_b:
                    result["background_color_b"] = bg.gradient_color_b
                if bg.gradient_type != "linear":
                    result["background_gradient_type"] = bg.gradient_type
                if bg.gradient_angle != 180:
                    result["background_gradient_angle"] = {
                        "unit": "deg",
                        "size": bg.gradient_angle,
                    }
        
        # 边框
        if style.border:
            border = style.border
            if border.border_style.value != "none":
                result["border_border"] = border.border_style.value
                if border.border_width:
                    result["border_width"] = {
                        "unit": border.border_width.unit,
                        "top": border.border_width.top or 0,
                        "right": border.border_width.right or 0,
                        "bottom": border.border_width.bottom or 0,
                        "left": border.border_width.left or 0,
                    }
                if border.border_color:
                    result["border_color"] = border.border_color
                if border.border_radius:
                    result["border_radius"] = {
                        "unit": border.border_radius.unit,
                        "top": border.border_radius.top or 0,
                        "right": border.border_radius.right or 0,
                        "bottom": border.border_radius.bottom or 0,
                        "left": border.border_radius.left or 0,
                    }
        
        # 阴影
        if style.box_shadow:
            shadow = style.box_shadow
            result["box_shadow_box_shadow"] = {
                "horizontal": shadow.horizontal,
                "vertical": shadow.vertical,
                "blur": shadow.blur,
                "spread": shadow.spread,
                "color": shadow.color,
            }
            if shadow.position == "inset":
                result["box_shadow_box_shadow_position"] = "inset"
        
        # 排版
        if style.typography:
            typo = style.typography
            result["typography_typography"] = "custom"
            if typo.font_family:
                result["typography_font_family"] = typo.font_family
            if typo.font_size:
                result["typography_font_size"] = {"unit": "px", "size": typo.font_size}
            if typo.font_weight:
                result["typography_font_weight"] = typo.font_weight
            if typo.font_style != "normal":
                result["typography_font_style"] = typo.font_style
            if typo.text_transform != "none":
                result["typography_text_transform"] = typo.text_transform
            if typo.text_decoration != "none":
                result["typography_text_decoration"] = typo.text_decoration
            if typo.line_height:
                result["typography_line_height"] = {"unit": "em", "size": typo.line_height}
            if typo.letter_spacing:
                result["typography_letter_spacing"] = {"unit": "px", "size": typo.letter_spacing}
        
        # 间距
        if style.margin:
            result["margin"] = {
                "unit": style.margin.unit,
                "top": style.margin.top or 0,
                "right": style.margin.right or 0,
                "bottom": style.margin.bottom or 0,
                "left": style.margin.left or 0,
            }
        
        if style.padding:
            result["padding"] = {
                "unit": style.padding.unit,
                "top": style.padding.top or 0,
                "right": style.padding.right or 0,
                "bottom": style.padding.bottom or 0,
                "left": style.padding.left or 0,
            }
        
        # 宽度
        if style.width:
            result["width"] = {"unit": "%", "size": style.width.replace("%", "")}
        
        # Z-index
        if style.z_index is not None:
            result["_z_index"] = style.z_index
        
        # 不透明度
        if style.opacity != 1.0:
            result["_opacity"] = style.opacity
        
        # 动画
        if style.entrance_animation and style.entrance_animation.value != "none":
            result["_animation"] = style.entrance_animation.value
            result["animation_duration"] = style.animation_duration
            result["animation_delay"] = style.animation_delay
        
        # 响应式设置
        if style.responsive:
            # 平板
            if style.responsive.tablet:
                tablet = style.responsive.tablet
                if "width" in tablet:
                    result["width_tablet"] = {"unit": "%", "size": tablet["width"].replace("%", "")}
                if "alignment" in tablet:
                    result["align_tablet"] = tablet["alignment"]
            
            # 手机
            if style.responsive.mobile:
                mobile = style.responsive.mobile
                if "width" in mobile:
                    result["width_mobile"] = {"unit": "%", "size": mobile["width"].replace("%", "")}
                if "alignment" in mobile:
                    result["align_mobile"] = mobile["alignment"]
        
        return result
    
    def convert_to_elementor_data(self, pedl_document: PEDLDocument) -> Dict[str, Any]:
        """
        转换为完整的Elementor数据格式（包含版本信息等）
        
        Args:
            pedl_document: PEDL文档
            
        Returns:
            完整的Elementor数据
        """
        elements = self.convert(pedl_document)
        
        return {
            "content": elements,
            "settings": {
                "page_title": pedl_document.title,
            },
            "version": "3.18.0",
            "title": pedl_document.title,
            "type": pedl_document.document_type,
        }
    
    def create_elementor_post_meta(self, pedl_document: PEDLDocument, post_id: int) -> List[Dict[str, Any]]:
        """
        创建Elementor postmeta记录（用于直接写入数据库）
        
        Args:
            pedl_document: PEDL文档
            post_id: WordPress文章ID
            
        Returns:
            postmeta记录列表
        """
        elementor_data = self.convert(pedl_document)
        
        meta_records = [
            {
                "post_id": post_id,
                "meta_key": "_elementor_data",
                "meta_value": elementor_data,
            },
            {
                "post_id": post_id,
                "meta_key": "_elementor_edit_mode",
                "meta_value": "builder",
            },
            {
                "post_id": post_id,
                "meta_key": "_elementor_template_type",
                "meta_value": pedl_document.document_type,
            },
            {
                "post_id": post_id,
                "meta_key": "_elementor_version",
                "meta_value": "3.18.0",
            },
            {
                "post_id": post_id,
                "meta_key": "_elementor_page_settings",
                "meta_value": {},
            },
            {
                "post_id": post_id,
                "meta_key": "_elementor_css",
                "meta_value": "",
            },
        ]
        
        return meta_records
