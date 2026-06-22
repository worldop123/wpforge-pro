"""
AI自动设计引擎
根据产品信息、参考页面等自动生成PEDL页面布局和设计
"""
import random
from typing import Dict, Any, List, Optional
from app.core.logging import get_logger
from app.services.page_builder.pedl import (
    PEDLDocument,
    PEDLSection,
    PEDLColumn,
    PEDLWidget,
    PEDLSettings,
    PEDLStyle,
    PEDLBackground,
    PEDLDimension,
    PEDLTypography,
    PEDLBoxShadow,
    PEDLBorder,
    WidgetType,
    Alignment,
    BackgroundType,
    BorderStyle,
    AnimationType,
)

logger = get_logger(__name__)


class AIDesignEngine:
    """AI自动设计引擎"""
    
    # 预设配色方案
    COLOR_SCHEMES = {
        "modern_blue": {
            "primary": "#2563eb",
            "secondary": "#1e40af",
            "accent": "#3b82f6",
            "background": "#ffffff",
            "surface": "#f8fafc",
            "text": "#1e293b",
            "text_light": "#64748b",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444",
        },
        "elegant_purple": {
            "primary": "#7c3aed",
            "secondary": "#5b21b6",
            "accent": "#8b5cf6",
            "background": "#ffffff",
            "surface": "#faf5ff",
            "text": "#1e1b4b",
            "text_light": "#6b7280",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444",
        },
        "fresh_green": {
            "primary": "#059669",
            "secondary": "#047857",
            "accent": "#10b981",
            "background": "#ffffff",
            "surface": "#f0fdf4",
            "text": "#064e3b",
            "text_light": "#6b7280",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444",
        },
        "warm_orange": {
            "primary": "#ea580c",
            "secondary": "#c2410c",
            "accent": "#f97316",
            "background": "#ffffff",
            "surface": "#fff7ed",
            "text": "#431407",
            "text_light": "#6b7280",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444",
        },
        "dark_mode": {
            "primary": "#3b82f6",
            "secondary": "#2563eb",
            "accent": "#60a5fa",
            "background": "#0f172a",
            "surface": "#1e293b",
            "text": "#f1f5f9",
            "text_light": "#94a3b8",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444",
        },
        "minimal_black": {
            "primary": "#000000",
            "secondary": "#1a1a1a",
            "accent": "#333333",
            "background": "#ffffff",
            "surface": "#f5f5f5",
            "text": "#000000",
            "text_light": "#666666",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444",
        },
    }
    
    # 预设字体方案
    FONT_SCHEMES = {
        "modern_sans": {
            "heading": "Inter",
            "body": "Inter",
            "weights": {
                "light": 300,
                "regular": 400,
                "medium": 500,
                "semibold": 600,
                "bold": 700,
            },
        },
        "elegant_serif": {
            "heading": "Playfair Display",
            "body": "Lora",
            "weights": {
                "regular": 400,
                "medium": 500,
                "semibold": 600,
                "bold": 700,
            },
        },
        "tech_geometric": {
            "heading": "Poppins",
            "body": "Open Sans",
            "weights": {
                "light": 300,
                "regular": 400,
                "medium": 500,
                "semibold": 600,
                "bold": 700,
            },
        },
        "classic_news": {
            "heading": "Merriweather",
            "body": "Roboto",
            "weights": {
                "regular": 400,
                "bold": 700,
            },
        },
    }
    
    # 设计风格
    DESIGN_STYLES = [
        "minimal",
        "modern",
        "elegant",
        "bold",
        "playful",
        "professional",
        "luxury",
        "tech",
    ]
    
    def __init__(self, color_scheme: str = "modern_blue", font_scheme: str = "modern_sans", style: str = "modern"):
        self.color_scheme = self.COLOR_SCHEMES.get(color_scheme, self.COLOR_SCHEMES["modern_blue"])
        self.font_scheme = self.FONT_SCHEMES.get(font_scheme, self.FONT_SCHEMES["modern_sans"])
        self.style = style
    
    def generate_product_page(self, product: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> PEDLDocument:
        """
        生成产品详情页
        
        Args:
            product: 产品信息字典
            options: 生成选项
            
        Returns:
            PEDL文档
        """
        options = options or {}
        doc = PEDLDocument(
            title=product.get("name", "Product"),
            document_type="product",
            meta={"product_id": product.get("id")},
        )
        
        # 1. Hero区域（产品主图 + 标题 + 价格）
        self._add_product_hero_section(doc, product)
        
        # 2. 产品特性区域
        if product.get("features"):
            self._add_features_section(doc, product["features"], "产品特性")
        
        # 3. 产品描述区域
        if product.get("description"):
            self._add_description_section(doc, product["description"], "产品描述")
        
        # 4. 规格参数区域
        if product.get("specifications"):
            self._add_specifications_section(doc, product["specifications"])
        
        # 5. FAQ区域
        if product.get("faqs"):
            self._add_faq_section(doc, product["faqs"])
        
        # 6. 评价区域
        if product.get("reviews"):
            self._add_reviews_section(doc, product["reviews"])
        
        # 7. 相关产品区域
        if product.get("related_products"):
            self._add_related_products_section(doc, product["related_products"])
        
        # 8. CTA区域
        self._add_cta_section(doc, product)
        
        return doc
    
    def generate_landing_page(self, content: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> PEDLDocument:
        """
        生成落地页
        
        Args:
            content: 页面内容
            options: 生成选项
            
        Returns:
            PEDL文档
        """
        options = options or {}
        doc = PEDLDocument(
            title=content.get("title", "Landing Page"),
            document_type="page",
        )
        
        # 1. Hero区域
        if content.get("hero"):
            self._add_hero_section(doc, content["hero"])
        
        # 2. 特性/优势区域
        if content.get("features"):
            self._add_features_section(doc, content["features"], content.get("features_title", "为什么选择我们"))
        
        # 3. 产品/服务展示区域
        if content.get("products"):
            self._add_products_section(doc, content["products"], content.get("products_title", "热门产品"))
        
        # 4. 工作流程/步骤区域
        if content.get("steps"):
            self._add_steps_section(doc, content["steps"], content.get("steps_title", "工作流程"))
        
        # 5. 评价/见证区域
        if content.get("testimonials"):
            self._add_testimonials_section(doc, content["testimonials"], content.get("testimonials_title", "客户评价"))
        
        # 6. FAQ区域
        if content.get("faqs"):
            self._add_faq_section(doc, content["faqs"], content.get("faqs_title", "常见问题"))
        
        # 7. 团队/关于我们区域
        if content.get("team"):
            self._add_team_section(doc, content["team"], content.get("team_title", "我们的团队"))
        
        # 8. CTA区域
        if content.get("cta"):
            self._add_cta_section(doc, content["cta"])
        
        return doc
    
    def generate_about_page(self, content: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> PEDLDocument:
        """
        生成关于我们页面
        
        Args:
            content: 页面内容
            options: 生成选项
            
        Returns:
            PEDL文档
        """
        options = options or {}
        doc = PEDLDocument(
            title=content.get("title", "关于我们"),
            document_type="page",
        )
        
        # 1. Hero区域
        self._add_hero_section(doc, {
            "title": content.get("title", "关于我们"),
            "subtitle": content.get("subtitle", ""),
        })
        
        # 2. 公司介绍区域
        if content.get("introduction"):
            self._add_description_section(doc, content["introduction"], "公司介绍")
        
        # 3. 使命愿景价值观区域
        if content.get("values"):
            self._add_values_section(doc, content["values"])
        
        # 4. 发展历程/时间线区域
        if content.get("timeline"):
            self._add_timeline_section(doc, content["timeline"])
        
        # 5. 团队区域
        if content.get("team"):
            self._add_team_section(doc, content["team"], "核心团队")
        
        # 6. 数据/成就区域
        if content.get("stats"):
            self._add_stats_section(doc, content["stats"])
        
        # 7. CTA区域
        if content.get("cta"):
            self._add_cta_section(doc, content["cta"])
        
        return doc
    
    def generate_contact_page(self, content: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> PEDLDocument:
        """
        生成联系我们页面
        
        Args:
            content: 页面内容
            options: 生成选项
            
        Returns:
            PEDL文档
        """
        options = options or {}
        doc = PEDLDocument(
            title=content.get("title", "联系我们"),
            document_type="page",
        )
        
        # 1. Hero区域
        self._add_hero_section(doc, {
            "title": content.get("title", "联系我们"),
            "subtitle": content.get("subtitle", "我们随时为您服务"),
        })
        
        # 2. 联系信息 + 表单区域
        self._add_contact_section(doc, content)
        
        # 3. FAQ区域
        if content.get("faqs"):
            self._add_faq_section(doc, content["faqs"], "常见问题")
        
        return doc
    
    def _add_product_hero_section(self, doc: PEDLDocument, product: Dict[str, Any]) -> None:
        """添加产品Hero区域"""
        section = PEDLSection(layout="boxed")
        section.settings.style = PEDLStyle(
            padding=PEDLDimension(top="60px", bottom="60px")
        )
        
        # 左列：产品图片
        image_column = PEDLColumn(width="50%")
        
        if product.get("image"):
            image_widget = PEDLWidget(
                widget_type=WidgetType.IMAGE,
                content={
                    "image": {"url": product["image"]},
                    "alt": product.get("name", ""),
                    "title": product.get("name", ""),
                }
            )
            image_widget.settings.style = PEDLStyle(
                border=PEDLBorder(
                    border_style=BorderStyle.SOLID,
                    border_width=PEDLDimension(top="1px", right="1px", bottom="1px", left="1px"),
                    border_color="#e5e7eb",
                    border_radius=PEDLDimension(top="12px", right="12px", bottom="12px", left="12px"),
                ),
                box_shadow=PEDLBoxShadow(
                    horizontal=0,
                    vertical=4,
                    blur=20,
                    spread=0,
                    color="rgba(0,0,0,0.1)",
                ),
            )
            image_column.widgets.append(image_widget)
        
        # 产品图库（缩略图）
        if product.get("gallery"):
            gallery_widget = PEDLWidget(
                widget_type=WidgetType.IMAGE_GALLERY,
                content={"images": product["gallery"]}
            )
            image_column.widgets.append(gallery_widget)
        
        # 右列：产品信息
        info_column = PEDLColumn(width="50%")
        
        # 产品标题
        title_widget = PEDLWidget(
            widget_type=WidgetType.HEADING,
            content={
                "title": product.get("name", ""),
                "size": "h1",
            }
        )
        title_widget.settings.style = PEDLStyle(
            typography=PEDLTypography(
                font_family=self.font_scheme["heading"],
                font_size="36px",
                font_weight="700",
                line_height="1.2",
            ),
            margin=PEDLDimension(bottom="16px"),
        )
        info_column.widgets.append(title_widget)
        
        # 产品评分
        if product.get("rating"):
            rating_widget = PEDLWidget(
                widget_type=WidgetType.TEXT_EDITOR,
                content={"editor": f'<div class="product-rating">⭐ {product["rating"]} ({product.get("review_count", 0)} 评价)</div>'}
            )
            info_column.widgets.append(rating_widget)
        
        # 产品价格
        if product.get("price"):
            price_html = f'<div class="product-price"><span class="regular-price">{product["price"]}</span>'
            if product.get("sale_price"):
                price_html += f' <span class="sale-price">{product["sale_price"]}</span>'
            price_html += "</div>"
            
            price_widget = PEDLWidget(
                widget_type=WidgetType.TEXT_EDITOR,
                content={"editor": price_html}
            )
            price_widget.settings.style = PEDLStyle(
                margin=PEDLDimension(top="20px", bottom="20px"),
            )
            info_column.widgets.append(price_widget)
        
        # 简短描述
        if product.get("short_description"):
            desc_widget = PEDLWidget(
                widget_type=WidgetType.TEXT_EDITOR,
                content={"editor": product["short_description"]}
            )
            desc_widget.settings.style = PEDLStyle(
                text_color=self.color_scheme["text_light"],
                margin=PEDLDimension(bottom="24px"),
            )
            info_column.widgets.append(desc_widget)
        
        # 添加到购物车按钮
        add_to_cart = PEDLWidget(
            widget_type=WidgetType.BUTTON,
            content={
                "text": "加入购物车",
                "link": {"url": "#", "is_external": False},
                "size": "lg",
            }
        )
        add_to_cart.settings.style = PEDLStyle(
            background=PEDLBackground(
                background_type=BackgroundType.CLASSIC,
                background_color=self.color_scheme["primary"],
            ),
            padding=PEDLDimension(top="16px", right="32px", bottom="16px", left="32px"),
            border=PEDLBorder(
                border_style=BorderStyle.SOLID,
                border_width=PEDLDimension(top="2px", right="2px", bottom="2px", left="2px"),
                border_color=self.color_scheme["primary"],
                border_radius=PEDLDimension(top="8px", right="8px", bottom="8px", left="8px"),
            ),
        )
        info_column.widgets.append(add_to_cart)
        
        # 立即购买按钮
        buy_now = PEDLWidget(
            widget_type=WidgetType.BUTTON,
            content={
                "text": "立即购买",
                "link": {"url": "#", "is_external": False},
                "size": "lg",
            }
        )
        buy_now.settings.style = PEDLStyle(
            margin=PEDLDimension(left="12px"),
            background=PEDLBackground(
                background_type=BackgroundType.CLASSIC,
                background_color="#ffffff",
            ),
            text_color=self.color_scheme["primary"],
            padding=PEDLDimension(top="16px", right="32px", bottom="16px", left="32px"),
            border=PEDLBorder(
                border_style=BorderStyle.SOLID,
                border_width=PEDLDimension(top="2px", right="2px", bottom="2px", left="2px"),
                border_color=self.color_scheme["primary"],
                border_radius=PEDLDimension(top="8px", right="8px", bottom="8px", left="8px"),
            ),
        )
        info_column.widgets.append(buy_now)
        
        section.columns.append(image_column)
        section.columns.append(info_column)
        doc.sections.append(section)
    
    def _add_hero_section(self, doc: PEDLDocument, hero: Dict[str, Any]) -> None:
        """添加Hero区域"""
        section = PEDLSection(layout="full_width")
        
        # 背景设置
        if hero.get("background_image"):
            section.settings.style = PEDLStyle(
                background=PEDLBackground(
                    background_type=BackgroundType.CLASSIC,
                    background_image=hero["background_image"],
                    background_overlay_color="rgba(0,0,0,0.5)",
                ),
                padding=PEDLDimension(top="120px", bottom="120px"),
                min_height="600px",
            )
        else:
            section.settings.style = PEDLStyle(
                background=PEDLBackground(
                    background_type=BackgroundType.CLASSIC,
                    background_color=self.color_scheme["surface"],
                ),
                padding=PEDLDimension(top="80px", bottom="80px"),
            )
        
        column = PEDLColumn(width="100%")
        column.settings.style = PEDLStyle(alignment=Alignment.CENTER)
        
        # 标题
        if hero.get("title"):
            title_widget = PEDLWidget(
                widget_type=WidgetType.HEADING,
                content={
                    "title": hero["title"],
                    "size": "h1",
                }
            )
            title_widget.settings.style = PEDLStyle(
                typography=PEDLTypography(
                    font_family=self.font_scheme["heading"],
                    font_size="48px",
                    font_weight="700",
                    line_height="1.2",
                ),
                text_color="#ffffff" if hero.get("background_image") else self.color_scheme["text"],
                margin=PEDLDimension(bottom="20px"),
                entrance_animation=AnimationType.FADE_IN_UP,
                animation_duration=0.8,
            )
            column.widgets.append(title_widget)
        
        # 副标题
        if hero.get("subtitle"):
            subtitle_widget = PEDLWidget(
                widget_type=WidgetType.TEXT_EDITOR,
                content={"editor": hero["subtitle"]}
            )
            subtitle_widget.settings.style = PEDLStyle(
                typography=PEDLTypography(
                    font_family=self.font_scheme["body"],
                    font_size="20px",
                    line_height="1.6",
                ),
                text_color="rgba(255,255,255,0.9)" if hero.get("background_image") else self.color_scheme["text_light"],
                max_width="700px",
                margin=PEDLDimension(bottom="32px"),
                entrance_animation=AnimationType.FADE_IN_UP,
                animation_duration=0.8,
                animation_delay=0.2,
            )
            column.widgets.append(subtitle_widget)
        
        # 按钮
        if hero.get("button_text"):
            button_widget = PEDLWidget(
                widget_type=WidgetType.BUTTON,
                content={
                    "text": hero["button_text"],
                    "link": {"url": hero.get("button_url", "#"), "is_external": False},
                    "size": "lg",
                }
            )
            button_widget.settings.style = PEDLStyle(
                background=PEDLBackground(
                    background_type=BackgroundType.CLASSIC,
                    background_color=self.color_scheme["primary"],
                ),
                padding=PEDLDimension(top="16px", right="40px", bottom="16px", left="40px"),
                border=PEDLBorder(
                    border_style=BorderStyle.SOLID,
                    border_width=PEDLDimension(top="2px", right="2px", bottom="2px", left="2px"),
                    border_color=self.color_scheme["primary"],
                    border_radius=PEDLDimension(top="50px", right="50px", bottom="50px", left="50px"),
                ),
                entrance_animation=AnimationType.FADE_IN_UP,
                animation_duration=0.8,
                animation_delay=0.4,
            )
            column.widgets.append(button_widget)
        
        section.columns.append(column)
        doc.sections.append(section)
    
    def _add_features_section(self, doc: PEDLDocument, features: List[Dict[str, str]], title: str = "") -> None:
        """添加特性区域"""
        section = PEDLSection()
        section.settings.style = PEDLStyle(
            padding=PEDLDimension(top="80px", bottom="80px"),
        )
        
        # 标题
        if title:
            title_column = PEDLColumn(width="100%")
            title_widget = PEDLWidget(
                widget_type=WidgetType.HEADING,
                content={
                    "title": title,
                    "size": "h2",
                    "align": "center",
                }
            )
            title_widget.settings.style = PEDLStyle(
                typography=PEDLTypography(
                    font_family=self.font_scheme["heading"],
                    font_size="36px",
                    font_weight="700",
                    line_height="1.3",
                ),
                margin=PEDLDimension(bottom="16px"),
            )
            title_column.widgets.append(title_widget)
            
            # 副标题/描述
            desc_widget = PEDLWidget(
                widget_type=WidgetType.TEXT_EDITOR,
                content={"editor": '<p style="text-align: center; color: #6b7280;">探索我们的核心优势，为您的业务赋能</p>'}
            )
            desc_widget.settings.style = PEDLStyle(
                margin=PEDLDimension(bottom="48px"),
            )
            title_column.widgets.append(desc_widget)
            
            section.columns.append(title_column)
        
        # 特性列
        columns_count = min(len(features), 4)
        column_width = f"{100 // columns_count}%"
        
        for i, feature in enumerate(features):
            column = PEDLColumn(width=column_width)
            
            icon_box = PEDLWidget(
                widget_type=WidgetType.ICON_BOX,
                content={
                    "icon": feature.get("icon", "fas fa-check-circle"),
                    "title_text": feature.get("title", ""),
                    "description_text": feature.get("description", ""),
                    "icon_position": "top",
                }
            )
            icon_box.settings.style = PEDLStyle(
                padding=PEDLDimension(top="32px", right="24px", bottom="32px", left="24px"),
                background=PEDLBackground(
                    background_type=BackgroundType.CLASSIC,
                    background_color="#ffffff",
                ),
                border=PEDLBorder(
                    border_style=BorderStyle.SOLID,
                    border_width=PEDLDimension(top="1px", right="1px", bottom="1px", left="1px"),
                    border_color="#e5e7eb",
                    border_radius=PEDLDimension(top="12px", right="12px", bottom="12px", left="12px"),
                ),
                entrance_animation=AnimationType.FADE_IN_UP,
                animation_duration=0.6,
                animation_delay=0.1 * i,
            )
            column.widgets.append(icon_box)
            
            section.columns.append(column)
        
        doc.sections.append(section)
    
    def _add_description_section(self, doc: PEDLDocument, content: str, title: str = "") -> None:
        """添加描述区域"""
        section = PEDLSection()
        section.settings.style = PEDLStyle(
            padding=PEDLDimension(top="60px", bottom="60px"),
            background=PEDLBackground(
                background_type=BackgroundType.CLASSIC,
                background_color=self.color_scheme["surface"],
            ),
        )
        
        column = PEDLColumn(width="100%")
        
        if title:
            title_widget = PEDLWidget(
                widget_type=WidgetType.HEADING,
                content={
                    "title": title,
                    "size": "h2",
                }
            )
            title_widget.settings.style = PEDLStyle(
                typography=PEDLTypography(
                    font_family=self.font_scheme["heading"],
                    font_size="32px",
                    font_weight="700",
                ),
                margin=PEDLDimension(bottom="24px"),
            )
            column.widgets.append(title_widget)
        
        content_widget = PEDLWidget(
            widget_type=WidgetType.TEXT_EDITOR,
            content={"editor": content}
        )
        content_widget.settings.style = PEDLStyle(
            typography=PEDLTypography(
                font_family=self.font_scheme["body"],
                font_size="16px",
                line_height="1.8",
            ),
            text_color=self.color_scheme["text"],
        )
        column.widgets.append(content_widget)
        
        section.columns.append(column)
        doc.sections.append(section)
    
    def _add_specifications_section(self, doc: PEDLDocument, specifications: List[Dict[str, str]]) -> None:
        """添加规格参数区域"""
        section = PEDLSection()
        section.settings.style = PEDLStyle(
            padding=PEDLDimension(top="60px", bottom="60px"),
        )
        
        column = PEDLColumn(width="100%")
        
        title_widget = PEDLWidget(
            widget_type=WidgetType.HEADING,
            content={
                "title": "规格参数",
                "size": "h2",
            }
        )
        title_widget.settings.style = PEDLStyle(
            typography=PEDLTypography(
                font_family=self.font_scheme["heading"],
                font_size="32px",
                font_weight="700",
            ),
            margin=PEDLDimension(bottom="24px"),
        )
        column.widgets.append(title_widget)
        
        # 生成规格表格HTML
        table_html = '<table class="spec-table" style="width: 100%; border-collapse: collapse;">'
        for spec in specifications:
            table_html += f'''
            <tr style="border-bottom: 1px solid #e5e7eb;">
                <td style="padding: 12px 16px; font-weight: 600; width: 30%; background-color: {self.color_scheme['surface']};">{spec.get("label", "")}</td>
                <td style="padding: 12px 16px;">{spec.get("value", "")}</td>
            </tr>
            '''
        table_html += "</table>"
        
        table_widget = PEDLWidget(
            widget_type=WidgetType.HTML,
            content={"html": table_html}
        )
        column.widgets.append(table_widget)
        
        section.columns.append(column)
        doc.sections.append(section)
    
    def _add_faq_section(self, doc: PEDLDocument, faqs: List[Dict[str, str]], title: str = "常见问题") -> None:
        """添加FAQ区域"""
        section = PEDLSection()
        section.settings.style = PEDLStyle(
            padding=PEDLDimension(top="80px", bottom="80px"),
            background=PEDLBackground(
                background_type=BackgroundType.CLASSIC,
                background_color=self.color_scheme["surface"],
            ),
        )
        
        # 标题
        title_column = PEDLColumn(width="100%")
        title_widget = PEDLWidget(
            widget_type=WidgetType.HEADING,
            content={
                "title": title,
                "size": "h2",
                "align": "center",
            }
        )
        title_widget.settings.style = PEDLStyle(
            typography=PEDLTypography(
                font_family=self.font_scheme["heading"],
                font_size="36px",
                font_weight="700",
            ),
            margin=PEDLDimension(bottom="48px"),
        )
        title_column.widgets.append(title_widget)
        section.columns.append(title_column)
        
        # FAQ手风琴
        faq_column = PEDLColumn(width="100%")
        
        accordion = PEDLWidget(widget_type=WidgetType.ACCORDION)
        
        for faq in faqs:
            tab = PEDLWidget(
                widget_type=WidgetType.TOGGLE,
                content={
                    "tab_title": faq.get("question", ""),
                    "tab_content": faq.get("answer", ""),
                }
            )
            accordion.children.append(tab)
        
        faq_column.widgets.append(accordion)
        section.columns.append(faq_column)
        
        doc.sections.append(section)
    
    def _add_reviews_section(self, doc: PEDLDocument, reviews: List[Dict[str, Any]]) -> None:
        """添加评价区域"""
        section = PEDLSection()
        section.settings.style = PEDLStyle(
            padding=PEDLDimension(top="80px", bottom="80px"),
        )
        
        # 标题
        title_column = PEDLColumn(width="100%")
        title_widget = PEDLWidget(
            widget_type=WidgetType.HEADING,
            content={
                "title": "用户评价",
                "size": "h2",
                "align": "center",
            }
        )
        title_widget.settings.style = PEDLStyle(
            typography=PEDLTypography(
                font_family=self.font_scheme["heading"],
                font_size="36px",
                font_weight="700",
            ),
            margin=PEDLDimension(bottom="48px"),
        )
        title_column.widgets.append(title_widget)
        section.columns.append(title_column)
        
        # 评价轮播
        review_column = PEDLColumn(width="100%")
        
        testimonial_carousel = PEDLWidget(
            widget_type=WidgetType.TESTIMONIAL_CAROUSEL,
            content={"slides": reviews}
        )
        review_column.widgets.append(testimonial_carousel)
        
        section.columns.append(review_column)
        doc.sections.append(section)
    
    def _add_related_products_section(self, doc: PEDLDocument, products: List[Dict[str, Any]]) -> None:
        """添加相关产品区域"""
        section = PEDLSection()
        section.settings.style = PEDLStyle(
            padding=PEDLDimension(top="80px", bottom="80px"),
            background=PEDLBackground(
                background_type=BackgroundType.CLASSIC,
                background_color=self.color_scheme["surface"],
            ),
        )
        
        # 标题
        title_column = PEDLColumn(width="100%")
        title_widget = PEDLWidget(
            widget_type=WidgetType.HEADING,
            content={
                "title": "相关产品",
                "size": "h2",
                "align": "center",
            }
        )
        title_widget.settings.style = PEDLStyle(
            typography=PEDLTypography(
                font_family=self.font_scheme["heading"],
                font_size="36px",
                font_weight="700",
            ),
            margin=PEDLDimension(bottom="48px"),
        )
        title_column.widgets.append(title_widget)
        section.columns.append(title_column)
        
        # 产品列
        columns_count = min(len(products), 4)
        column_width = f"{100 // columns_count}%"
        
        for product in products:
            column = PEDLColumn(width=column_width)
            
            # 产品卡片
            card_widget = PEDLWidget(
                widget_type=WidgetType.HTML,
                content={
                    "html": f'''
                    <div class="product-card" style="background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); transition: transform 0.3s ease;">
                        <div class="product-image" style="aspect-ratio: 1; overflow: hidden;">
                            <img src="{product.get("image", "")}" alt="{product.get("name", "")}" style="width: 100%; height: 100%; object-fit: cover;">
                        </div>
                        <div class="product-info" style="padding: 20px;">
                            <h3 style="font-size: 18px; font-weight: 600; margin: 0 0 8px 0;">{product.get("name", "")}</h3>
                            <div class="price" style="font-size: 20px; font-weight: 700; color: {self.color_scheme['primary']};">
                                {product.get("price", "")}
                            </div>
                        </div>
                    </div>
                    '''
                }
            )
            column.widgets.append(card_widget)
            
            section.columns.append(column)
        
        doc.sections.append(section)
    
    def _add_cta_section(self, doc: PEDLDocument, content: Any) -> None:
        """添加CTA区域"""
        section = PEDLSection()
        section.settings.style = PEDLStyle(
            padding=PEDLDimension(top="80px", bottom="80px"),
            background=PEDLBackground(
                background_type=BackgroundType.GRADIENT,
                gradient_color_a=self.color_scheme["primary"],
                gradient_color_b=self.color_scheme["secondary"],
                gradient_angle=135,
            ),
        )
        
        column = PEDLColumn(width="100%")
        column.settings.style = PEDLStyle(alignment=Alignment.CENTER)
        
        # 标题
        title_text = content.get("title", "准备好开始了吗？") if isinstance(content, dict) else "立即行动"
        title_widget = PEDLWidget(
            widget_type=WidgetType.HEADING,
            content={
                "title": title_text,
                "size": "h2",
            }
        )
        title_widget.settings.style = PEDLStyle(
            typography=PEDLTypography(
                font_family=self.font_scheme["heading"],
                font_size="36px",
                font_weight="700",
            ),
            text_color="#ffffff",
            margin=PEDLDimension(bottom="16px"),
        )
        column.widgets.append(title_widget)
        
        # 描述
        if isinstance(content, dict) and content.get("description"):
            desc_widget = PEDLWidget(
                widget_type=WidgetType.TEXT_EDITOR,
                content={"editor": content["description"]}
            )
            desc_widget.settings.style = PEDLStyle(
                typography=PEDLTypography(
                    font_family=self.font_scheme["body"],
                    font_size="18px",
                ),
                text_color="rgba(255,255,255,0.9)",
                max_width="600px",
                margin=PEDLDimension(bottom="32px"),
            )
            column.widgets.append(desc_widget)
        
        # 按钮
        button_text = content.get("button_text", "立即开始") if isinstance(content, dict) else "了解更多"
        button_url = content.get("button_url", "#") if isinstance(content, dict) else "#"
        
        button_widget = PEDLWidget(
            widget_type=WidgetType.BUTTON,
            content={
                "text": button_text,
                "link": {"url": button_url, "is_external": False},
                "size": "lg",
            }
        )
        button_widget.settings.style = PEDLStyle(
            background=PEDLBackground(
                background_type=BackgroundType.CLASSIC,
                background_color="#ffffff",
            ),
            text_color=self.color_scheme["primary"],
            padding=PEDLDimension(top="16px", right="40px", bottom="16px", left="40px"),
            border=PEDLBorder(
                border_style=BorderStyle.SOLID,
                border_width=PEDLDimension(top="2px", right="2px", bottom="2px", left="2px"),
                border_color="#ffffff",
                border_radius=PEDLDimension(top="50px", right="50px", bottom="50px", left="50px"),
            ),
        )
        column.widgets.append(button_widget)
        
        section.columns.append(column)
        doc.sections.append(section)
    
    def _add_products_section(self, doc: PEDLDocument, products: List[Dict[str, Any]], title: str = "") -> None:
        """添加产品展示区域"""
        section = PEDLSection()
        section.settings.style = PEDLStyle(
            padding=PEDLDimension(top="80px", bottom="80px"),
        )
        
        # 标题
        if title:
            title_column = PEDLColumn(width="100%")
            title_widget = PEDLWidget(
                widget_type=WidgetType.HEADING,
                content={
                    "title": title,
                    "size": "h2",
                    "align": "center",
                }
            )
            title_widget.settings.style = PEDLStyle(
                typography=PEDLTypography(
                    font_family=self.font_scheme["heading"],
                    font_size="36px",
                    font_weight="700",
                ),
                margin=PEDLDimension(bottom="48px"),
            )
            title_column.widgets.append(title_widget)
            section.columns.append(title_column)
        
        # 产品列
        columns_count = min(len(products), 4)
        column_width = f"{100 // columns_count}%"
        
        for product in products:
            column = PEDLColumn(width=column_width)
            
            # 产品卡片
            card_html = f'''
            <div class="product-card" style="background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); transition: all 0.3s ease;">
                <div class="product-image" style="aspect-ratio: 1; overflow: hidden; background: {self.color_scheme['surface']};">
                    <img src="{product.get("image", "")}" alt="{product.get("name", "")}" style="width: 100%; height: 100%; object-fit: cover;">
                </div>
                <div class="product-info" style="padding: 24px;">
                    <h3 style="font-size: 18px; font-weight: 600; margin: 0 0 12px 0; color: {self.color_scheme['text']};">{product.get("name", "")}</h3>
                    <p style="font-size: 14px; color: {self.color_scheme['text_light']}; margin: 0 0 16px 0; line-height: 1.6;">{product.get("description", "")}</p>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div class="price" style="font-size: 24px; font-weight: 700; color: {self.color_scheme['primary']};">
                            {product.get("price", "")}
                        </div>
                        <a href="{product.get("url", "#")}" style="display: inline-block; padding: 8px 20px; background: {self.color_scheme['primary']}; color: white; text-decoration: none; border-radius: 6px; font-size: 14px;">
                            查看详情
                        </a>
                    </div>
                </div>
            </div>
            '''
            
            card_widget = PEDLWidget(
                widget_type=WidgetType.HTML,
                content={"html": card_html}
            )
            column.widgets.append(card_widget)
            
            section.columns.append(column)
        
        doc.sections.append(section)
    
    def _add_steps_section(self, doc: PEDLDocument, steps: List[Dict[str, Any]], title: str = "") -> None:
        """添加步骤/流程区域"""
        section = PEDLSection()
        section.settings.style = PEDLStyle(
            padding=PEDLDimension(top="80px", bottom="80px"),
            background=PEDLBackground(
                background_type=BackgroundType.CLASSIC,
                background_color=self.color_scheme["surface"],
            ),
        )
        
        # 标题
        if title:
            title_column = PEDLColumn(width="100%")
            title_widget = PEDLWidget(
                widget_type=WidgetType.HEADING,
                content={
                    "title": title,
                    "size": "h2",
                    "align": "center",
                }
            )
            title_widget.settings.style = PEDLStyle(
                typography=PEDLTypography(
                    font_family=self.font_scheme["heading"],
                    font_size="36px",
                    font_weight="700",
                ),
                margin=PEDLDimension(bottom="48px"),
            )
            title_column.widgets.append(title_widget)
            section.columns.append(title_column)
        
        # 步骤列
        columns_count = min(len(steps), 4)
        column_width = f"{100 // columns_count}%"
        
        for i, step in enumerate(steps):
            column = PEDLColumn(width=column_width)
            
            step_html = f'''
            <div class="step-item" style="text-align: center; position: relative;">
                <div class="step-number" style="width: 60px; height: 60px; background: {self.color_scheme['primary']}; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 700; margin: 0 auto 20px;">
                    {i + 1}
                </div>
                <h3 style="font-size: 20px; font-weight: 600; margin: 0 0 12px 0; color: {self.color_scheme['text']};">{step.get("title", "")}</h3>
                <p style="font-size: 14px; color: {self.color_scheme['text_light']}; margin: 0; line-height: 1.6;">{step.get("description", "")}</p>
            </div>
            '''
            
            step_widget = PEDLWidget(
                widget_type=WidgetType.HTML,
                content={"html": step_html}
            )
            column.widgets.append(step_widget)
            
            section.columns.append(column)
        
        doc.sections.append(section)
    
    def _add_testimonials_section(self, doc: PEDLDocument, testimonials: List[Dict[str, Any]], title: str = "") -> None:
        """添加评价/见证区域"""
        section = PEDLSection()
        section.settings.style = PEDLStyle(
            padding=PEDLDimension(top="80px", bottom="80px"),
        )
        
        # 标题
        if title:
            title_column = PEDLColumn(width="100%")
            title_widget = PEDLWidget(
                widget_type=WidgetType.HEADING,
                content={
                    "title": title,
                    "size": "h2",
                    "align": "center",
                }
            )
            title_widget.settings.style = PEDLStyle(
                typography=PEDLTypography(
                    font_family=self.font_scheme["heading"],
                    font_size="36px",
                    font_weight="700",
                ),
                margin=PEDLDimension(bottom="48px"),
            )
            title_column.widgets.append(title_widget)
            section.columns.append(title_column)
        
        # 评价列
        columns_count = min(len(testimonials), 3)
        column_width = f"{100 // columns_count}%"
        
        for testimonial in testimonials:
            column = PEDLColumn(width=column_width)
            
            testimonial_html = f'''
            <div class="testimonial-card" style="background: white; padding: 32px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
                <div class="stars" style="color: #fbbf24; margin-bottom: 16px;">
                    {"⭐" * testimonial.get("rating", 5)}
                </div>
                <p style="font-size: 16px; line-height: 1.8; color: {self.color_scheme['text']}; margin: 0 0 24px 0;">"{testimonial.get("content", "")}"</p>
                <div class="author" style="display: flex; align-items: center;">
                    <img src="{testimonial.get("avatar", "")}" alt="{testimonial.get("name", "")}" style="width: 48px; height: 48px; border-radius: 50%; margin-right: 12px;">
                    <div>
                        <div style="font-weight: 600; color: {self.color_scheme['text']};">{testimonial.get("name", "")}</div>
                        <div style="font-size: 14px; color: {self.color_scheme['text_light']};">{testimonial.get("title", "")}</div>
                    </div>
                </div>
            </div>
            '''
            
            testimonial_widget = PEDLWidget(
                widget_type=WidgetType.HTML,
                content={"html": testimonial_html}
            )
            column.widgets.append(testimonial_widget)
            
            section.columns.append(column)
        
        doc.sections.append(section)
    
    def _add_team_section(self, doc: PEDLDocument, team: List[Dict[str, Any]], title: str = "") -> None:
        """添加团队区域"""
        section = PEDLSection()
        section.settings.style = PEDLStyle(
            padding=PEDLDimension(top="80px", bottom="80px"),
        )
        
        # 标题
        if title:
            title_column = PEDLColumn(width="100%")
            title_widget = PEDLWidget(
                widget_type=WidgetType.HEADING,
                content={
                    "title": title,
                    "size": "h2",
                    "align": "center",
                }
            )
            title_widget.settings.style = PEDLStyle(
                typography=PEDLTypography(
                    font_family=self.font_scheme["heading"],
                    font_size="36px",
                    font_weight="700",
                ),
                margin=PEDLDimension(bottom="48px"),
            )
            title_column.widgets.append(title_widget)
            section.columns.append(title_column)
        
        # 团队成员列
        columns_count = min(len(team), 4)
        column_width = f"{100 // columns_count}%"
        
        for member in team:
            column = PEDLColumn(width=column_width)
            
            member_html = f'''
            <div class="team-member" style="text-align: center;">
                <div class="avatar" style="width: 150px; height: 150px; border-radius: 50%; overflow: hidden; margin: 0 auto 20px; border: 4px solid {self.color_scheme['surface']};">
                    <img src="{member.get("avatar", "")}" alt="{member.get("name", "")}" style="width: 100%; height: 100%; object-fit: cover;">
                </div>
                <h3 style="font-size: 20px; font-weight: 600; margin: 0 0 8px 0; color: {self.color_scheme['text']};">{member.get("name", "")}</h3>
                <p style="font-size: 14px; color: {self.color_scheme['primary']}; margin: 0 0 12px 0; font-weight: 500;">{member.get("position", "")}</p>
                <p style="font-size: 14px; color: {self.color_scheme['text_light']}; margin: 0; line-height: 1.6;">{member.get("bio", "")}</p>
            </div>
            '''
            
            member_widget = PEDLWidget(
                widget_type=WidgetType.HTML,
                content={"html": member_html}
            )
            column.widgets.append(member_widget)
            
            section.columns.append(column)
        
        doc.sections.append(section)
    
    def _add_values_section(self, doc: PEDLDocument, values: List[Dict[str, str]]) -> None:
        """添加价值观区域"""
        section = PEDLSection()
        section.settings.style = PEDLStyle(
            padding=PEDLDimension(top="80px", bottom="80px"),
            background=PEDLBackground(
                background_type=BackgroundType.CLASSIC,
                background_color=self.color_scheme["surface"],
            ),
        )
        
        # 标题
        title_column = PEDLColumn(width="100%")
        title_widget = PEDLWidget(
            widget_type=WidgetType.HEADING,
            content={
                "title": "我们的价值观",
                "size": "h2",
                "align": "center",
            }
        )
        title_widget.settings.style = PEDLStyle(
            typography=PEDLTypography(
                font_family=self.font_scheme["heading"],
                font_size="36px",
                font_weight="700",
            ),
            margin=PEDLDimension(bottom="48px"),
        )
        title_column.widgets.append(title_widget)
        section.columns.append(title_column)
        
        # 价值观列
        columns_count = min(len(values), 3)
        column_width = f"{100 // columns_count}%"
        
        for value in values:
            column = PEDLColumn(width=column_width)
            
            value_widget = PEDLWidget(
                widget_type=WidgetType.ICON_BOX,
                content={
                    "icon": value.get("icon", "fas fa-heart"),
                    "title_text": value.get("title", ""),
                    "description_text": value.get("description", ""),
                    "icon_position": "top",
                }
            )
            value_widget.settings.style = PEDLStyle(
                padding=PEDLDimension(top="32px", right="24px", bottom="32px", left="24px"),
                background=PEDLBackground(
                    background_type=BackgroundType.CLASSIC,
                    background_color="#ffffff",
                ),
                border=PEDLBorder(
                    border_style=BorderStyle.SOLID,
                    border_width=PEDLDimension(top="1px", right="1px", bottom="1px", left="1px"),
                    border_color="#e5e7eb",
                    border_radius=PEDLDimension(top="12px", right="12px", bottom="12px", left="12px"),
                ),
            )
            column.widgets.append(value_widget)
            
            section.columns.append(column)
        
        doc.sections.append(section)
    
    def _add_timeline_section(self, doc: PEDLDocument, timeline: List[Dict[str, Any]]) -> None:
        """添加时间线区域"""
        section = PEDLSection()
        section.settings.style = PEDLStyle(
            padding=PEDLDimension(top="80px", bottom="80px"),
        )
        
        # 标题
        title_column = PEDLColumn(width="100%")
        title_widget = PEDLWidget(
            widget_type=WidgetType.HEADING,
            content={
                "title": "发展历程",
                "size": "h2",
                "align": "center",
            }
        )
        title_widget.settings.style = PEDLStyle(
            typography=PEDLTypography(
                font_family=self.font_scheme["heading"],
                font_size="36px",
                font_weight="700",
            ),
            margin=PEDLDimension(bottom="48px"),
        )
        title_column.widgets.append(title_widget)
        section.columns.append(title_column)
        
        # 时间线
        timeline_column = PEDLColumn(width="100%")
        
        timeline_html = '<div class="timeline" style="position: relative; max-width: 800px; margin: 0 auto;">'
        
        for i, item in enumerate(timeline):
            is_left = i % 2 == 0
            timeline_html += f'''
            <div class="timeline-item" style="display: flex; margin-bottom: 40px; {"flex-direction: row-reverse;" if not is_left else ""}">
                <div class="timeline-content" style="width: 45%; padding: 24px; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
                    <div class="year" style="font-size: 24px; font-weight: 700; color: {self.color_scheme['primary']}; margin-bottom: 8px;">{item.get("year", "")}</div>
                    <h3 style="font-size: 18px; font-weight: 600; margin: 0 0 8px 0; color: {self.color_scheme['text']};">{item.get("title", "")}</h3>
                    <p style="font-size: 14px; color: {self.color_scheme['text_light']}; margin: 0; line-height: 1.6;">{item.get("description", "")}</p>
                </div>
                <div class="timeline-dot" style="width: 20px; height: 20px; background: {self.color_scheme['primary']}; border-radius: 50%; margin: 24px 20px 0; z-index: 1;"></div>
                <div style="width: 45%;"></div>
            </div>
            '''
        
        timeline_html += '</div>'
        
        timeline_widget = PEDLWidget(
            widget_type=WidgetType.HTML,
            content={"html": timeline_html}
        )
        timeline_column.widgets.append(timeline_widget)
        
        section.columns.append(timeline_column)
        doc.sections.append(section)
    
    def _add_stats_section(self, doc: PEDLDocument, stats: List[Dict[str, Any]]) -> None:
        """添加数据统计区域"""
        section = PEDLSection()
        section.settings.style = PEDLStyle(
            padding=PEDLDimension(top="80px", bottom="80px"),
            background=PEDLBackground(
                background_type=BackgroundType.GRADIENT,
                gradient_color_a=self.color_scheme["primary"],
                gradient_color_b=self.color_scheme["secondary"],
                gradient_angle=135,
            ),
        )
        
        # 统计列
        columns_count = min(len(stats), 4)
        column_width = f"{100 // columns_count}%"
        
        for stat in stats:
            column = PEDLColumn(width=column_width)
            column.settings.style = PEDLStyle(alignment=Alignment.CENTER)
            
            stat_html = f'''
            <div class="stat-item" style="text-align: center;">
                <div class="stat-number" style="font-size: 48px; font-weight: 700; color: white; margin-bottom: 8px;">{stat.get("number", "")}</div>
                <div class="stat-label" style="font-size: 16px; color: rgba(255,255,255,0.9);">{stat.get("label", "")}</div>
            </div>
            '''
            
            stat_widget = PEDLWidget(
                widget_type=WidgetType.HTML,
                content={"html": stat_html}
            )
            column.widgets.append(stat_widget)
            
            section.columns.append(column)
        
        doc.sections.append(section)
    
    def _add_contact_section(self, doc: PEDLDocument, content: Dict[str, Any]) -> None:
        """添加联系信息区域"""
        section = PEDLSection()
        section.settings.style = PEDLStyle(
            padding=PEDLDimension(top="80px", bottom="80px"),
        )
        
        # 左列：联系信息
        info_column = PEDLColumn(width="40%")
        
        info_title = PEDLWidget(
            widget_type=WidgetType.HEADING,
            content={
                "title": "联系信息",
                "size": "h3",
            }
        )
        info_title.settings.style = PEDLStyle(
            typography=PEDLTypography(
                font_family=self.font_scheme["heading"],
                font_size="24px",
                font_weight="700",
            ),
            margin=PEDLDimension(bottom="24px"),
        )
        info_column.widgets.append(info_title)
        
        # 联系信息列表
        contact_items = []
        if content.get("address"):
            contact_items.append(("📍", "地址", content["address"]))
        if content.get("phone"):
            contact_items.append(("📞", "电话", content["phone"]))
        if content.get("email"):
            contact_items.append(("✉️", "邮箱", content["email"]))
        if content.get("working_hours"):
            contact_items.append(("🕐", "工作时间", content["working_hours"]))
        
        for icon, label, value in contact_items:
            item_html = f'''
            <div class="contact-item" style="display: flex; margin-bottom: 20px;">
                <div class="icon" style="font-size: 24px; margin-right: 16px;">{icon}</div>
                <div>
                    <div style="font-weight: 600; color: {self.color_scheme['text']}; margin-bottom: 4px;">{label}</div>
                    <div style="color: {self.color_scheme['text_light']};">{value}</div>
                </div>
            </div>
            '''
            item_widget = PEDLWidget(
                widget_type=WidgetType.HTML,
                content={"html": item_html}
            )
            info_column.widgets.append(item_widget)
        
        # 右列：联系表单
        form_column = PEDLColumn(width="60%")
        
        form_title = PEDLWidget(
            widget_type=WidgetType.HEADING,
            content={
                "title": "发送消息",
                "size": "h3",
            }
        )
        form_title.settings.style = PEDLStyle(
            typography=PEDLTypography(
                font_family=self.font_scheme["heading"],
                font_size="24px",
                font_weight="700",
            ),
            margin=PEDLDimension(bottom="24px"),
        )
        form_column.widgets.append(form_title)
        
        # 表单
        form_html = f'''
        <form class="contact-form" style="background: {self.color_scheme['surface']}; padding: 32px; border-radius: 12px;">
            <div style="display: flex; gap: 16px; margin-bottom: 16px;">
                <div style="flex: 1;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 500; color: {self.color_scheme['text']};">姓名</label>
                    <input type="text" style="width: 100%; padding: 12px 16px; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 14px;" placeholder="请输入您的姓名">
                </div>
                <div style="flex: 1;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 500; color: {self.color_scheme['text']};">邮箱</label>
                    <input type="email" style="width: 100%; padding: 12px 16px; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 14px;" placeholder="请输入您的邮箱">
                </div>
            </div>
            <div style="margin-bottom: 16px;">
                <label style="display: block; margin-bottom: 8px; font-weight: 500; color: {self.color_scheme['text']};">主题</label>
                <input type="text" style="width: 100%; padding: 12px 16px; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 14px;" placeholder="请输入消息主题">
            </div>
            <div style="margin-bottom: 24px;">
                <label style="display: block; margin-bottom: 8px; font-weight: 500; color: {self.color_scheme['text']};">消息内容</label>
                <textarea rows="5" style="width: 100%; padding: 12px 16px; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 14px; resize: vertical;" placeholder="请输入您的消息..."></textarea>
            </div>
            <button type="submit" style="width: 100%; padding: 14px 24px; background: {self.color_scheme['primary']}; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer;">
                发送消息
            </button>
        </form>
        '''
        
        form_widget = PEDLWidget(
            widget_type=WidgetType.HTML,
            content={"html": form_html}
        )
        form_column.widgets.append(form_widget)
        
        section.columns.append(info_column)
        section.columns.append(form_column)
        doc.sections.append(section)
    
    @classmethod
    def get_random_design(cls) -> "AIDesignEngine":
        """获取随机设计方案"""
        color_scheme = random.choice(list(cls.COLOR_SCHEMES.keys()))
        font_scheme = random.choice(list(cls.FONT_SCHEMES.keys()))
        style = random.choice(cls.DESIGN_STYLES)
        
        return cls(color_scheme=color_scheme, font_scheme=font_scheme, style=style)
    
    @classmethod
    def get_design_for_industry(cls, industry: str) -> "AIDesignEngine":
        """根据行业推荐设计方案"""
        industry_map = {
            "tech": ("modern_blue", "tech_geometric", "tech"),
            "fashion": ("elegant_purple", "elegant_serif", "elegant"),
            "health": ("fresh_green", "modern_sans", "professional"),
            "food": ("warm_orange", "modern_sans", "playful"),
            "finance": ("modern_blue", "classic_news", "professional"),
            "education": ("fresh_green", "modern_sans", "friendly"),
            "beauty": ("elegant_purple", "elegant_serif", "luxury"),
            "fitness": ("warm_orange", "tech_geometric", "bold"),
            "ecommerce": ("modern_blue", "modern_sans", "modern"),
            "vape": ("minimal_black", "modern_sans", "minimal"),
        }
        
        color_scheme, font_scheme, style = industry_map.get(industry.lower(), ("modern_blue", "modern_sans", "modern"))
        
        return cls(color_scheme=color_scheme, font_scheme=font_scheme, style=style)
