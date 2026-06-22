"""
Bricks Builder转换器
将PEDL格式转换为Bricks Builder数据格式，支持直接写入WordPress数据库
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


class BricksConverter:
    """Bricks Builder转换器"""
    
    def __init__(self):
        self.widget_type_map = self._build_widget_type_map()
    
    def _build_widget_type_map(self) -> Dict[WidgetType, str]:
        """构建小部件类型映射"""
        return {
            # 基础元素
            WidgetType.HEADING: "heading",
            WidgetType.TEXT_EDITOR: "text",
            WidgetType.IMAGE: "image",
            WidgetType.BUTTON: "button",
            WidgetType.DIVIDER: "divider",
            WidgetType.SPACER: "spacer",
            WidgetType.ICON: "icon",
            WidgetType.ICON_BOX: "icon-box",
            WidgetType.ICON_LIST: "icon-list",
            
            # 布局元素
            WidgetType.SECTION: "section",
            WidgetType.COLUMN: "column",
            WidgetType.INNER_SECTION: "container",
            
            # 媒体元素
            WidgetType.IMAGE_GALLERY: "gallery",
            WidgetType.IMAGE_CAROUSEL: "carousel",
            WidgetType.VIDEO: "video",
            
            # 内容元素
            WidgetType.POSTS: "posts",
            WidgetType.TESTIMONIAL: "testimonial",
            WidgetType.TESTIMONIAL_CAROUSEL: "testimonial-carousel",
            WidgetType.ACCORDION: "accordion",
            WidgetType.TABS: "tabs",
            WidgetType.TOGGLE: "toggle",
            
            # WooCommerce元素
            WidgetType.PRODUCT: "product",
            WidgetType.PRODUCTS: "products",
            WidgetType.PRODUCT_CAROUSEL: "product-carousel",
            WidgetType.ADD_TO_CART: "add-to-cart",
            WidgetType.PRODUCT_PRICE: "product-price",
            WidgetType.PRODUCT_TITLE: "product-title",
            WidgetType.PRODUCT_IMAGE: "product-image",
            WidgetType.PRODUCT_DESCRIPTION: "product-description",
            WidgetType.PRODUCT_RATING: "product-rating",
            WidgetType.PRODUCT_META: "product-meta",
            WidgetType.PRODUCT_ADDITIONAL_INFORMATION: "product-additional-information",
            WidgetType.PRODUCT_DATA_TABS: "product-data-tabs",
            WidgetType.PRODUCT_RELATED: "related-products",
            WidgetType.PRODUCT_UPSELLS: "upsells",
            
            # 营销元素
            WidgetType.COUNTDOWN: "countdown",
            WidgetType.PROGRESS_BAR: "progress-bar",
            WidgetType.ALERT: "alert",
            WidgetType.CALLOUT: "callout",
            WidgetType.FLIP_BOX: "flip-box",
            WidgetType.HOVER_CARD: "hover-card",
            WidgetType.PRICING_TABLE: "pricing-table",
            WidgetType.TEAM_MEMBER: "team-member",
            
            # 导航元素
            WidgetType.NAV_MENU: "nav-menu",
            WidgetType.BREADCRUMBS: "breadcrumbs",
            WidgetType.PAGINATION: "pagination",
            
            # 其他
            WidgetType.SHORTCODE: "shortcode",
            WidgetType.HTML: "code",
            WidgetType.SITE_LOGO: "site-logo",
            WidgetType.SITE_TITLE: "site-title",
            WidgetType.SITE_TAGLINE: "site-tagline",
            WidgetType.POST_TITLE: "post-title",
            WidgetType.POST_EXCERPT: "post-excerpt",
            WidgetType.POST_CONTENT: "post-content",
            WidgetType.POST_FEATURED_IMAGE: "featured-image",
            WidgetType.POST_META: "post-meta",
            WidgetType.AUTHOR_BOX: "author-box",
            WidgetType.POST_COMMENTS: "comments",
            WidgetType.POST_NAVIGATION: "post-navigation",
        }
    
    def _generate_id(self) -> str:
        """生成Bricks元素ID"""
        return uuid.uuid4().hex[:10]
    
    def convert(self, pedl_document: PEDLDocument) -> List[Dict[str, Any]]:
        """
        将PEDL文档转换为Bricks Builder数据格式
        
        Args:
            pedl_document: PEDL文档
            
        Returns:
            Bricks数据列表（可直接写入_bricks_data）
        """
        bricks_data = []
        
        for section in pedl_document.sections:
            bricks_section = self._convert_section(section)
            bricks_data.append(bricks_section)
        
        return bricks_data
    
    def _convert_section(self, section: PEDLSection) -> Dict[str, Any]:
        """转换区块"""
        section_id = section.section_id or self._generate_id()
        
        bricks_section = {
            "id": section_id,
            "name": "section",
            "parent": 0,
            "children": [],
            "settings": self._convert_section_settings(section),
        }
        
        # 转换列
        for column in section.columns:
            bricks_column = self._convert_column(column, section_id)
            bricks_section["children"].append(bricks_column)
        
        return bricks_section
    
    def _convert_section_settings(self, section: PEDLSection) -> Dict[str, Any]:
        """转换区块设置"""
        settings = {}
        
        # 布局设置
        if section.layout == "full_width":
            settings["container"] = "full"
        elif section.layout == "full_width_stretched":
            settings["container"] = "full"
            settings["stretch"] = True
        else:
            settings["container"] = "boxed"
        
        # 列间距
        if section.columns_gap != "default":
            gap_map = {
                "no": 0,
                "narrow": 10,
                "default": 20,
                "extended": 40,
                "wide": 60,
            }
            settings["gap"] = gap_map.get(section.columns_gap, 20)
        
        # 样式设置
        style_settings = self._convert_style_settings(section.settings)
        settings.update(style_settings)
        
        # 高级设置
        if section.settings.element_id:
            settings["_cssId"] = section.settings.element_id
        
        if section.settings.css_classes:
            settings["_cssClasses"] = section.settings.css_classes
        
        if section.settings.custom_css:
            settings["_customCSS"] = section.settings.custom_css
        
        # 可见性
        if section.settings.hide_on_desktop:
            settings["_visibility:hide_desktop"] = True
        if section.settings.hide_on_tablet:
            settings["_visibility:hide_tablet"] = True
        if section.settings.hide_on_mobile:
            settings["_visibility:hide_mobile"] = True
        
        return settings
    
    def _convert_column(self, column: PEDLColumn, parent_id: str) -> Dict[str, Any]:
        """转换列"""
        column_id = column.column_id or self._generate_id()
        
        # 转换宽度百分比为Bricks格式
        width_percent = column.width.replace("%", "")
        try:
            width_int = int(float(width_percent))
        except (ValueError, TypeError):
            width_int = 50
        
        bricks_column = {
            "id": column_id,
            "name": "column",
            "parent": parent_id,
            "children": [],
            "settings": {
                "width": f"{width_int}%",
            },
        }
        
        # 样式设置
        style_settings = self._convert_style_settings(column.settings)
        bricks_column["settings"].update(style_settings)
        
        # 高级设置
        if column.settings.element_id:
            bricks_column["settings"]["_cssId"] = column.settings.element_id
        
        if column.settings.css_classes:
            bricks_column["settings"]["_cssClasses"] = column.settings.css_classes
        
        # 转换小部件
        for widget in column.widgets:
            bricks_widget = self._convert_widget(widget, column_id)
            bricks_column["children"].append(bricks_widget)
        
        return bricks_column
    
    def _convert_widget(self, widget: PEDLWidget, parent_id: str) -> Dict[str, Any]:
        """转换小部件"""
        widget_id = widget.widget_id or self._generate_id()
        widget_type = self.widget_type_map.get(widget.widget_type, "text")
        
        bricks_widget = {
            "id": widget_id,
            "name": widget_type,
            "parent": parent_id,
            "children": [],
            "settings": {},
        }
        
        # 转换内容设置
        content_settings = self._convert_widget_content(widget)
        bricks_widget["settings"].update(content_settings)
        
        # 转换样式设置
        style_settings = self._convert_style_settings(widget.settings)
        bricks_widget["settings"].update(style_settings)
        
        # 高级设置
        if widget.settings.element_id:
            bricks_widget["settings"]["_cssId"] = widget.settings.element_id
        
        if widget.settings.css_classes:
            bricks_widget["settings"]["_cssClasses"] = widget.settings.css_classes
        
        if widget.settings.custom_css:
            bricks_widget["settings"]["_customCSS"] = widget.settings.custom_css
        
        # 可见性
        if widget.settings.hide_on_desktop:
            bricks_widget["settings"]["_visibility:hide_desktop"] = True
        if widget.settings.hide_on_tablet:
            bricks_widget["settings"]["_visibility:hide_tablet"] = True
        if widget.settings.hide_on_mobile:
            bricks_widget["settings"]["_visibility:hide_mobile"] = True
        
        # 转换子元素
        if widget.children:
            bricks_widget["children"] = [
                self._convert_widget(child, widget_id) for child in widget.children
            ]
        
        return bricks_widget
    
    def _convert_widget_content(self, widget: PEDLWidget) -> Dict[str, Any]:
        """转换小部件内容设置"""
        content = widget.content
        settings = {}
        
        widget_type = widget.widget_type
        
        # 标题小部件
        if widget_type == WidgetType.HEADING:
            if "title" in content:
                settings["text"] = content["title"]
            if "size" in content:
                size_map = {
                    "h1": "h1",
                    "h2": "h2",
                    "h3": "h3",
                    "h4": "h4",
                    "h5": "h5",
                    "h6": "h6",
                }
                settings["tag"] = size_map.get(content["size"], "h2")
            if "align" in content:
                settings["align"] = content["align"]
        
        # 文本编辑器小部件
        elif widget_type == WidgetType.TEXT_EDITOR:
            if "editor" in content:
                settings["text"] = content["editor"]
        
        # 图片小部件
        elif widget_type == WidgetType.IMAGE:
            if "image" in content:
                image_data = content["image"]
                if isinstance(image_data, dict) and "url" in image_data:
                    settings["image"] = {
                        "url": image_data["url"],
                        "id": image_data.get("id", 0),
                    }
                elif isinstance(image_data, str):
                    settings["image"] = {"url": image_data, "id": 0}
            if "alt" in content:
                settings["alt"] = content["alt"]
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
                        "target": "_blank" if link_data.get("is_external", False) else "_self",
                        "nofollow": link_data.get("nofollow", False),
                    }
                elif isinstance(link_data, str):
                    settings["link"] = {"url": link_data, "target": "_self"}
            if "size" in content:
                size_map = {
                    "xs": "xs",
                    "sm": "sm",
                    "md": "md",
                    "lg": "lg",
                    "xl": "xl",
                }
                settings["size"] = size_map.get(content["size"], "md")
            if "icon" in content:
                settings["icon"] = {"library": "fontawesome", "icon": content["icon"]}
        
        # 图标框小部件
        elif widget_type == WidgetType.ICON_BOX:
            if "icon" in content:
                settings["icon"] = {"library": "fontawesome", "icon": content["icon"]}
            if "title_text" in content:
                settings["title"] = content["title_text"]
            if "description_text" in content:
                settings["description"] = content["description_text"]
            if "icon_position" in content:
                settings["iconPosition"] = content["icon_position"]
        
        # 手风琴小部件
        elif widget_type == WidgetType.ACCORDION:
            if "tabs" in content:
                settings["items"] = content["tabs"]
        
        # 标签页小部件
        elif widget_type == WidgetType.TABS:
            if "tabs" in content:
                settings["tabs"] = content["tabs"]
        
        # 评价小部件
        elif widget_type == WidgetType.TESTIMONIAL:
            if "content" in content:
                settings["content"] = content["content"]
            if "name" in content:
                settings["name"] = content["name"]
            if "title" in content:
                settings["role"] = content["title"]
            if "image" in content:
                settings["image"] = {"url": content["image"], "id": 0}
            if "rating" in content:
                settings["rating"] = content["rating"]
        
        # 倒计时小部件
        elif widget_type == WidgetType.COUNTDOWN:
            if "due_date" in content:
                settings["dueDate"] = content["due_date"]
            if "label_days" in content:
                settings["daysLabel"] = content["label_days"]
            if "label_hours" in content:
                settings["hoursLabel"] = content["label_hours"]
            if "label_minutes" in content:
                settings["minutesLabel"] = content["label_minutes"]
            if "label_seconds" in content:
                settings["secondsLabel"] = content["label_seconds"]
        
        # 进度条小部件
        elif widget_type == WidgetType.PROGRESS_BAR:
            if "title" in content:
                settings["label"] = content["title"]
            if "percentage" in content:
                settings["percentage"] = content["percentage"]
            if "display_percentage" in content:
                settings["showPercentage"] = content["display_percentage"]
        
        # 警告框小部件
        elif widget_type == WidgetType.ALERT:
            if "alert_title" in content:
                settings["title"] = content["alert_title"]
            if "alert_description" in content:
                settings["text"] = content["alert_description"]
            if "type" in content:
                settings["type"] = content["type"]
            if "show_dismiss" in content:
                settings["dismissible"] = content["show_dismiss"]
        
        # HTML/代码小部件
        elif widget_type == WidgetType.HTML:
            if "html" in content:
                settings["code"] = content["html"]
        
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
                settings["width"] = f"{content['width']}%"
            if "align" in content:
                settings["align"] = content["align"]
        
        # 间隔小部件
        elif widget_type == WidgetType.SPACER:
            if "space" in content:
                settings["height"] = f"{content['space']}px"
        
        # WooCommerce产品价格
        elif widget_type == WidgetType.PRODUCT_PRICE:
            if "product_id" in content:
                settings["productId"] = content["product_id"]
        
        # WooCommerce添加到购物车
        elif widget_type == WidgetType.ADD_TO_CART:
            if "product_id" in content:
                settings["productId"] = content["product_id"]
            if "quantity" in content:
                settings["quantity"] = content["quantity"]
            if "show_quantity" in content:
                settings["showQuantity"] = content["show_quantity"]
        
        # 产品列表
        elif widget_type == WidgetType.PRODUCTS:
            if "posts_per_page" in content:
                settings["postsPerPage"] = content["posts_per_page"]
            if "columns" in content:
                settings["columns"] = content["columns"]
            if "orderby" in content:
                settings["orderBy"] = content["orderby"]
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
            result["color"] = style.text_color
        
        # 背景
        if style.background:
            bg = style.background
            if bg.background_type.value == "classic":
                if bg.background_color:
                    result["backgroundColor"] = bg.background_color
                if bg.background_image:
                    result["backgroundImage"] = {"url": bg.background_image, "id": 0}
                if bg.background_position != "center center":
                    result["backgroundPosition"] = bg.background_position
                if bg.background_size != "cover":
                    result["backgroundSize"] = bg.background_size
                if bg.background_repeat != "no-repeat":
                    result["backgroundRepeat"] = bg.background_repeat
            elif bg.background_type.value == "gradient":
                if bg.gradient_color_a and bg.gradient_color_b:
                    result["backgroundGradient"] = {
                        "colorA": bg.gradient_color_a,
                        "colorB": bg.gradient_color_b,
                        "direction": f"{bg.gradient_angle}deg",
                    }
        
        # 边框
        if style.border:
            border = style.border
            if border.border_style.value != "none":
                result["borderStyle"] = border.border_style.value
                if border.border_width:
                    result["borderWidth"] = {
                        "top": f"{border.border_width.top or 0}{border.border_width.unit}",
                        "right": f"{border.border_width.right or 0}{border.border_width.unit}",
                        "bottom": f"{border.border_width.bottom or 0}{border.border_width.unit}",
                        "left": f"{border.border_width.left or 0}{border.border_width.unit}",
                    }
                if border.border_color:
                    result["borderColor"] = border.border_color
                if border.border_radius:
                    result["borderRadius"] = {
                        "top": f"{border.border_radius.top or 0}{border.border_radius.unit}",
                        "right": f"{border.border_radius.right or 0}{border.border_radius.unit}",
                        "bottom": f"{border.border_radius.bottom or 0}{border.border_radius.unit}",
                        "left": f"{border.border_radius.left or 0}{border.border_radius.unit}",
                    }
        
        # 阴影
        if style.box_shadow:
            shadow = style.box_shadow
            result["boxShadow"] = {
                "offsetX": f"{shadow.horizontal}px",
                "offsetY": f"{shadow.vertical}px",
                "blurRadius": f"{shadow.blur}px",
                "spreadRadius": f"{shadow.spread}px",
                "color": shadow.color,
                "inset": shadow.position == "inset",
            }
        
        # 排版
        if style.typography:
            typo = style.typography
            if typo.font_family:
                result["fontFamily"] = typo.font_family
            if typo.font_size:
                result["fontSize"] = f"{typo.font_size}px"
            if typo.font_weight:
                result["fontWeight"] = typo.font_weight
            if typo.font_style != "normal":
                result["fontStyle"] = typo.font_style
            if typo.text_transform != "none":
                result["textTransform"] = typo.text_transform
            if typo.line_height:
                result["lineHeight"] = f"{typo.line_height}em"
            if typo.letter_spacing:
                result["letterSpacing"] = f"{typo.letter_spacing}px"
        
        # 间距
        if style.margin:
            result["margin"] = {
                "top": f"{style.margin.top or 0}{style.margin.unit}",
                "right": f"{style.margin.right or 0}{style.margin.unit}",
                "bottom": f"{style.margin.bottom or 0}{style.margin.unit}",
                "left": f"{style.margin.left or 0}{style.margin.unit}",
            }
        
        if style.padding:
            result["padding"] = {
                "top": f"{style.padding.top or 0}{style.padding.unit}",
                "right": f"{style.padding.right or 0}{style.padding.unit}",
                "bottom": f"{style.padding.bottom or 0}{style.padding.unit}",
                "left": f"{style.padding.left or 0}{style.padding.unit}",
            }
        
        # 宽度
        if style.width:
            result["width"] = style.width
        
        # Z-index
        if style.z_index is not None:
            result["zIndex"] = style.z_index
        
        # 不透明度
        if style.opacity != 1.0:
            result["opacity"] = style.opacity
        
        # 动画
        if style.entrance_animation and style.entrance_animation.value != "none":
            result["animation"] = style.entrance_animation.value
            result["animationDuration"] = f"{style.animation_duration}s"
            result["animationDelay"] = f"{style.animation_delay}s"
        
        # 响应式设置
        if style.responsive:
            # 平板
            if style.responsive.tablet:
                tablet = style.responsive.tablet
                if "width" in tablet:
                    result["widthTablet"] = tablet["width"]
                if "alignment" in tablet:
                    result["alignTablet"] = tablet["alignment"]
            
            # 手机
            if style.responsive.mobile:
                mobile = style.responsive.mobile
                if "width" in mobile:
                    result["widthMobile"] = mobile["width"]
                if "alignment" in mobile:
                    result["alignMobile"] = mobile["alignment"]
        
        return result
    
    def convert_to_bricks_data(self, pedl_document: PEDLDocument) -> Dict[str, Any]:
        """
        转换为完整的Bricks数据格式
        
        Args:
            pedl_document: PEDL文档
            
        Returns:
            完整的Bricks数据
        """
        elements = self.convert(pedl_document)
        
        return {
            "elements": elements,
            "settings": {
                "title": pedl_document.title,
            },
            "version": "1.9.6",
            "title": pedl_document.title,
            "type": pedl_document.document_type,
        }
    
    def create_bricks_post_meta(self, pedl_document: PEDLDocument, post_id: int) -> List[Dict[str, Any]]:
        """
        创建Bricks postmeta记录（用于直接写入数据库）
        
        Args:
            pedl_document: PEDL文档
            post_id: WordPress文章ID
            
        Returns:
            postmeta记录列表
        """
        bricks_data = self.convert(pedl_document)
        
        meta_records = [
            {
                "post_id": post_id,
                "meta_key": "_bricks_page_content_2",
                "meta_value": bricks_data,
            },
            {
                "post_id": post_id,
                "meta_key": "_bricks_page_settings",
                "meta_value": {},
            },
            {
                "post_id": post_id,
                "meta_key": "_bricks_editor_mode",
                "meta_value": "bricks",
            },
            {
                "post_id": post_id,
                "meta_key": "_bricks_version",
                "meta_value": "1.9.6",
            },
        ]
        
        return meta_records
