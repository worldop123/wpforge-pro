"""
全自动SEO优化服务
包含页面SEO、Schema结构化数据、关键词策略、内部链接建设等
"""
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import json
import random
from urllib.parse import urlparse


class SchemaType(str, Enum):
    """Schema类型枚举"""
    ARTICLE = "Article"
    BLOG_POSTING = "BlogPosting"
    PRODUCT = "Product"
    REVIEW = "Review"
    AGGREGATE_RATING = "AggregateRating"
    BREADCRUMB_LIST = "BreadcrumbList"
    FAQ_PAGE = "FAQPage"
    HOW_TO = "HowTo"
    ORGANIZATION = "Organization"
    WEB_SITE = "WebSite"
    LOCAL_BUSINESS = "LocalBusiness"
    PERSON = "Person"
    OFFER = "Offer"


@dataclass
class SEOAnalysisResult:
    """SEO分析结果"""
    score: int  # 0-100
    title_score: int
    description_score: int
    heading_score: int
    content_score: int
    image_score: int
    links_score: int
    schema_score: int
    issues: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "title_score": self.title_score,
            "description_score": self.description_score,
            "heading_score": self.heading_score,
            "content_score": self.content_score,
            "image_score": self.image_score,
            "links_score": self.links_score,
            "schema_score": self.schema_score,
            "issues": self.issues,
            "suggestions": self.suggestions,
        }


@dataclass
class SEOSettings:
    """SEO设置"""
    # 基础设置
    site_title: str = ""
    site_description: str = ""
    title_separator: str = "|"
    homepage_title_format: str = "{site_title} {separator} {site_description}"
    post_title_format: str = "{post_title} {separator} {site_title}"
    page_title_format: str = "{page_title} {separator} {site_title}"
    category_title_format: str = "{category_name} {separator} {site_title}"

    # Meta设置
    auto_generate_description: bool = True
    auto_generate_keywords: bool = True
    description_length_min: int = 120
    description_length_max: int = 160
    title_length_min: int = 30
    title_length_max: int = 60

    # Schema设置
    schema_enabled: bool = True
    article_schema: bool = True
    product_schema: bool = True
    breadcrumb_schema: bool = True
    review_schema: bool = True
    faq_schema: bool = True
    organization_schema: bool = True
    website_schema: bool = True
    local_business_schema: bool = False

    # 面包屑
    breadcrumb_enabled: bool = True
    breadcrumb_separator: str = "»"
    breadcrumb_home_text: str = "Home"
    breadcrumb_show_home: bool = True

    # 社交
    open_graph_enabled: bool = True
    twitter_cards_enabled: bool = True
    og_image: str = ""
    twitter_image: str = ""

    # 高级
    canonical_auto: bool = True
    prev_next_links: bool = True
    noindex_categories: bool = False
    noindex_tags: bool = False
    noindex_author: bool = True
    noindex_date: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "site_title": self.site_title,
            "site_description": self.site_description,
            "title_separator": self.title_separator,
            "homepage_title_format": self.homepage_title_format,
            "post_title_format": self.post_title_format,
            "page_title_format": self.page_title_format,
            "category_title_format": self.category_title_format,
            "auto_generate_description": self.auto_generate_description,
            "auto_generate_keywords": self.auto_generate_keywords,
            "description_length_min": self.description_length_min,
            "description_length_max": self.description_length_max,
            "title_length_min": self.title_length_min,
            "title_length_max": self.title_length_max,
            "schema_enabled": self.schema_enabled,
            "article_schema": self.article_schema,
            "product_schema": self.product_schema,
            "breadcrumb_schema": self.breadcrumb_schema,
            "review_schema": self.review_schema,
            "faq_schema": self.faq_schema,
            "organization_schema": self.organization_schema,
            "website_schema": self.website_schema,
            "local_business_schema": self.local_business_schema,
            "breadcrumb_enabled": self.breadcrumb_enabled,
            "breadcrumb_separator": self.breadcrumb_separator,
            "breadcrumb_home_text": self.breadcrumb_home_text,
            "breadcrumb_show_home": self.breadcrumb_show_home,
            "open_graph_enabled": self.open_graph_enabled,
            "twitter_cards_enabled": self.twitter_cards_enabled,
            "og_image": self.og_image,
            "twitter_image": self.twitter_image,
            "canonical_auto": self.canonical_auto,
            "prev_next_links": self.prev_next_links,
            "noindex_categories": self.noindex_categories,
            "noindex_tags": self.noindex_tags,
            "noindex_author": self.noindex_author,
            "noindex_date": self.noindex_date,
        }


class SEOService:
    """
    全自动SEO优化服务
    """

    def __init__(self, settings: Optional[SEOSettings] = None):
        self.settings = settings or SEOSettings()
        self._stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will", "would",
            "could", "should", "may", "might", "can", "shall",
        }

    def generate_seo_title(self, title: str, page_type: str = "post") -> str:
        """
        生成SEO友好的标题

        Args:
            title: 原始标题
            page_type: 页面类型（home/post/page/category）

        Returns:
            优化后的标题
        """
        if not title:
            return self.settings.site_title

        # 根据页面类型格式化
        if page_type == "home":
            formatted = self.settings.homepage_title_format.format(
                site_title=self.settings.site_title,
                separator=self.settings.title_separator,
                site_description=self.settings.site_description,
            )
        elif page_type == "post":
            formatted = self.settings.post_title_format.format(
                post_title=title,
                separator=self.settings.title_separator,
                site_title=self.settings.site_title,
            )
        elif page_type == "page":
            formatted = self.settings.page_title_format.format(
                page_title=title,
                separator=self.settings.title_separator,
                site_title=self.settings.site_title,
            )
        elif page_type == "category":
            formatted = self.settings.category_title_format.format(
                category_name=title,
                separator=self.settings.title_separator,
                site_title=self.settings.site_title,
            )
        else:
            formatted = f"{title} {self.settings.title_separator} {self.settings.site_title}"

        # 检查长度并调整
        if len(formatted) > self.settings.title_length_max:
            # 截断标题，保留站点名
            max_title_len = self.settings.title_length_max - len(f" {self.settings.title_separator} {self.settings.site_title}")
            if max_title_len > 10:
                truncated_title = title[:max_title_len - 3] + "..."
                formatted = f"{truncated_title} {self.settings.title_separator} {self.settings.site_title}"

        return formatted

    def generate_meta_description(self, content: str, title: str = "") -> str:
        """
        自动生成Meta描述

        Args:
            content: 页面内容
            title: 页面标题

        Returns:
            Meta描述
        """
        if not content and not title:
            return self.settings.site_description

        # 从内容中提取摘要
        description = ""

        if content:
            # 移除HTML标签
            clean_content = re.sub(r'<[^>]+>', '', content)
            # 移除多余空白
            clean_content = re.sub(r'\s+', ' ', clean_content).strip()

            # 取前几句话
            sentences = re.split(r'[.!?]+', clean_content)
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    if len(description) + len(sentence) + 1 <= self.settings.description_length_max:
                        if description:
                            description += " " + sentence
                        else:
                            description = sentence
                    else:
                        break

        # 如果内容不够，用标题补充
        if len(description) < self.settings.description_length_min and title:
            if description:
                description = f"{title} - {description}"
            else:
                description = title

        # 确保长度在范围内
        if len(description) > self.settings.description_length_max:
            description = description[:self.settings.description_length_max - 3] + "..."

        if len(description) < self.settings.description_length_min:
            # 补充默认描述
            if self.settings.site_description:
                description = self.settings.site_description

        return description.strip()

    def generate_slug(self, title: str) -> str:
        """
        生成SEO友好的URL Slug

        Args:
            title: 标题

        Returns:
            Slug
        """
        if not title:
            return ""

        # 转为小写
        slug = title.lower()

        # 替换特殊字符
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)

        # 替换空白为连字符
        slug = re.sub(r'\s+', '-', slug)

        # 移除连续连字符
        slug = re.sub(r'-+', '-', slug)

        # 移除首尾连字符
        slug = slug.strip('-')

        # 限制长度
        if len(slug) > 100:
            slug = slug[:100].rstrip('-')

        return slug

    def extract_keywords(self, content: str, num_keywords: int = 10) -> List[str]:
        """
        从内容中提取关键词

        Args:
            content: 内容文本
            num_keywords: 关键词数量

        Returns:
            关键词列表
        """
        if not content:
            return []

        # 移除HTML标签
        clean_content = re.sub(r'<[^>]+>', '', content.lower())

        # 分词
        words = re.findall(r'\b[a-z]{3,}\b', clean_content)

        # 过滤停用词
        words = [w for w in words if w not in self._stop_words]

        # 统计词频
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # 按词频排序
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

        # 提取前N个关键词
        keywords = [word for word, freq in sorted_words[:num_keywords]]

        return keywords

    def generate_lsi_keywords(self, main_keyword: str, content: str = "") -> List[str]:
        """
        生成LSI关键词（潜在语义索引）

        Args:
            main_keyword: 主关键词
            content: 内容上下文

        Returns:
            LSI关键词列表
        """
        # 基础LSI关键词生成（实际项目中可以使用AI生成）
        base_lsi = {
            "vape": ["e-cigarette", "vaporizer", "e-liquid", "vape juice", "pod system", "mod", "tank", "coil", "nicotine", "thc"],
            "cannabis": ["marijuana", "weed", "thc", "cbd", "edibles", "concentrates", "flower", "strain", "dispensary", "delivery"],
            "fashion": ["clothing", "apparel", "style", "trend", "outfit", "accessories", "footwear", "designer", "collection", "look"],
            "electronics": ["gadget", "device", "tech", "smart", "wireless", "bluetooth", "charger", "battery", "screen", "camera"],
            "beauty": ["skincare", "makeup", "cosmetics", "cream", "serum", "moisturizer", "anti-aging", "organic", "natural", "glow"],
            "fitness": ["workout", "exercise", "gym", "training", "muscle", "protein", "supplement", "weight loss", "cardio", "yoga"],
        }

        # 查找匹配的主关键词类别
        lsi_keywords = []
        for category, keywords in base_lsi.items():
            if category in main_keyword.lower() or main_keyword.lower() in category:
                lsi_keywords = keywords.copy()
                break

        # 如果没有匹配，生成通用LSI
        if not lsi_keywords:
            words = main_keyword.split()
            lsi_keywords = [
                f"best {main_keyword}",
                f"{main_keyword} review",
                f"{main_keyword} for sale",
                f"cheap {main_keyword}",
                f"{main_keyword} near me",
                f"{main_keyword} online",
                f"top {main_keyword}",
                f"{main_keyword} guide",
                f"{main_keyword} tips",
                f"buy {main_keyword}",
            ]

        return lsi_keywords

    def generate_long_tail_keywords(self, main_keyword: str) -> List[str]:
        """
    生成长尾关键词

        Args:
            main_keyword: 主关键词

        Returns:
            长尾关键词列表
        """
        patterns = [
            "best {keyword} for {purpose}",
            "how to {action} with {keyword}",
            "{keyword} vs {alternative}",
            "where to buy {keyword}",
            "{keyword} review 2024",
            "top 10 {keyword} products",
            "{keyword} for beginners",
            "is {keyword} worth it",
            "{keyword} buying guide",
            "cheap {keyword} under ${price}",
        ]

        purposes = ["men", "women", "beginners", "professionals", "small business", "home use"]
        actions = ["use", "choose", "get started", "find", "select"]
        alternatives = ["alternative", "competitor", "other options", "similar products"]
        prices = ["50", "100", "200", "500", "1000"]

        long_tails = []
        for pattern in patterns:
            keyword = main_keyword

            if "{purpose}" in pattern:
                purpose = random.choice(purposes)
                keyword = pattern.format(keyword=keyword, purpose=purpose)
            elif "{action}" in pattern:
                action = random.choice(actions)
                keyword = pattern.format(keyword=keyword, action=action)
            elif "{alternative}" in pattern:
                alt = random.choice(alternatives)
                keyword = pattern.format(keyword=keyword, alternative=alt)
            elif "{price}" in pattern:
                price = random.choice(prices)
                keyword = pattern.format(keyword=keyword, price=price)
            else:
                keyword = pattern.format(keyword=keyword)

            long_tails.append(keyword)

        return long_tails

    def generate_schema_markup(self, schema_type: SchemaType, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成Schema结构化数据

        Args:
            schema_type: Schema类型
            data: 数据

        Returns:
            Schema JSON-LD数据
        """
        schema = {
            "@context": "https://schema.org",
            "@type": schema_type.value,
        }

        if schema_type == SchemaType.ARTICLE:
            schema.update({
                "headline": data.get("title", ""),
                "description": data.get("description", ""),
                "image": data.get("image", ""),
                "author": {
                    "@type": "Person",
                    "name": data.get("author", ""),
                },
                "publisher": {
                    "@type": "Organization",
                    "name": data.get("publisher", ""),
                    "logo": {
                        "@type": "ImageObject",
                        "url": data.get("publisher_logo", ""),
                    },
                },
                "datePublished": data.get("date_published", ""),
                "dateModified": data.get("date_modified", ""),
            })

        elif schema_type == SchemaType.PRODUCT:
            schema.update({
                "name": data.get("name", ""),
                "description": data.get("description", ""),
                "image": data.get("images", []),
                "sku": data.get("sku", ""),
                "brand": {
                    "@type": "Brand",
                    "name": data.get("brand", ""),
                },
                "offers": {
                    "@type": "Offer",
                    "price": data.get("price", ""),
                    "priceCurrency": data.get("currency", "USD"),
                    "availability": data.get("availability", "https://schema.org/InStock"),
                    "url": data.get("url", ""),
                },
                "aggregateRating": {
                    "@type": "AggregateRating",
                    "ratingValue": data.get("rating", "5"),
                    "reviewCount": data.get("review_count", "0"),
                },
            })

        elif schema_type == SchemaType.BREADCRUMB_LIST:
            items = []
            breadcrumbs = data.get("breadcrumbs", [])
            for i, crumb in enumerate(breadcrumbs):
                items.append({
                    "@type": "ListItem",
                    "position": i + 1,
                    "name": crumb.get("name", ""),
                    "item": crumb.get("url", ""),
                })
            schema["itemListElement"] = items

        elif schema_type == SchemaType.FAQ_PAGE:
            main_entity = []
            faqs = data.get("faqs", [])
            for faq in faqs:
                main_entity.append({
                    "@type": "Question",
                    "name": faq.get("question", ""),
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": faq.get("answer", ""),
                    },
                })
            schema["mainEntity"] = main_entity

        elif schema_type == SchemaType.REVIEW:
            schema.update({
                "itemReviewed": {
                    "@type": "Product",
                    "name": data.get("product_name", ""),
                },
                "author": {
                    "@type": "Person",
                    "name": data.get("author", ""),
                },
                "reviewRating": {
                    "@type": "Rating",
                    "ratingValue": data.get("rating", "5"),
                    "bestRating": "5",
                },
                "reviewBody": data.get("review_text", ""),
                "datePublished": data.get("date", ""),
            })

        elif schema_type == SchemaType.ORGANIZATION:
            schema.update({
                "name": data.get("name", ""),
                "url": data.get("url", ""),
                "logo": data.get("logo", ""),
                "description": data.get("description", ""),
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": data.get("street_address", ""),
                    "addressLocality": data.get("city", ""),
                    "addressRegion": data.get("state", ""),
                    "postalCode": data.get("zip", ""),
                    "addressCountry": data.get("country", ""),
                },
                "contactPoint": {
                    "@type": "ContactPoint",
                    "telephone": data.get("phone", ""),
                    "contactType": "customer service",
                },
                "sameAs": data.get("social_links", []),
            })

        elif schema_type == SchemaType.WEB_SITE:
            schema.update({
                "name": data.get("name", ""),
                "url": data.get("url", ""),
                "description": data.get("description", ""),
                "potentialAction": {
                    "@type": "SearchAction",
                    "target": f"{data.get('url', '')}/?s={{search_term_string}}",
                    "query-input": "required name=search_term_string",
                },
            })

        elif schema_type == SchemaType.LOCAL_BUSINESS:
            schema.update({
                "name": data.get("name", ""),
                "image": data.get("image", ""),
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": data.get("street_address", ""),
                    "addressLocality": data.get("city", ""),
                    "addressRegion": data.get("state", ""),
                    "postalCode": data.get("zip", ""),
                    "addressCountry": data.get("country", ""),
                },
                "geo": {
                    "@type": "GeoCoordinates",
                    "latitude": data.get("latitude", ""),
                    "longitude": data.get("longitude", ""),
                },
                "url": data.get("url", ""),
                "telephone": data.get("phone", ""),
                "openingHours": data.get("opening_hours", []),
                "priceRange": data.get("price_range", "$$"),
            })

        return schema

    def generate_breadcrumb(self, current_page: str, path: List[Tuple[str, str]]) -> List[Dict[str, str]]:
        """
        生成面包屑导航

        Args:
            current_page: 当前页面名称
            path: 路径列表 [(名称, URL), ...]

        Returns:
            面包屑列表
        """
        breadcrumbs = []

        # 首页
        if self.settings.breadcrumb_show_home:
            breadcrumbs.append({
                "name": self.settings.breadcrumb_home_text,
                "url": "/",
            })

        # 路径
        for name, url in path:
            breadcrumbs.append({
                "name": name,
                "url": url,
            })

        # 当前页
        breadcrumbs.append({
            "name": current_page,
            "url": "",
        })

        return breadcrumbs

    def optimize_content_keywords(self, content: str, keywords: List[str]) -> str:
        """
        优化内容中的关键词布局

        Args:
            content: 原始内容
            keywords: 关键词列表

        Returns:
            优化后的内容
        """
        if not content or not keywords:
            return content

        optimized = content

        # 确保主关键词在前100字出现
        first_paragraph_end = optimized.find("</p>")
        if first_paragraph_end == -1:
            first_paragraph_end = 100

        first_part = optimized[:first_paragraph_end]
        main_keyword = keywords[0] if keywords else ""

        if main_keyword and main_keyword.lower() not in first_part.lower():
            # 在第一段开头插入关键词
            if "<p>" in first_part:
                insert_pos = first_part.find("<p>") + 3
                optimized = optimized[:insert_pos] + main_keyword + " - " + optimized[insert_pos:]

        return optimized

    def generate_internal_links(self, content: str, related_posts: List[Dict[str, str]]) -> str:
        """
        自动生成内部链接

        Args:
            content: 内容
            related_posts: 相关文章列表 [{title, url}, ...]

        Returns:
            带内部链接的内容
        """
        if not content or not related_posts:
            return content

        linked_content = content

        # 为每个相关文章尝试添加链接
        for post in related_posts[:3]:  # 最多3个内链
            title = post.get("title", "")
            url = post.get("url", "")

            if title and url:
                # 查找内容中第一次出现的标题关键词
                words = title.lower().split()
                for word in words:
                    if len(word) > 3 and word in linked_content.lower():
                        # 替换第一个出现的词为链接
                        pattern = re.compile(re.escape(word), re.IGNORECASE)
                        linked_content = pattern.sub(
                            f'<a href="{url}">{word}</a>',
                            linked_content,
                            count=1,
                        )
                        break

        return linked_content

    def optimize_image_seo(self, images: List[Dict[str, Any]], content: str = "") -> List[Dict[str, Any]]:
        """
        优化图片SEO

        Args:
            images: 图片列表 [{url, alt, title, ...}, ...]
            content: 内容上下文

        Returns:
            优化后的图片列表
        """
        optimized_images = []
        keywords = self.extract_keywords(content, 5) if content else []

        for i, image in enumerate(images):
            optimized = image.copy()

            # 自动生成ALT文本
            if not optimized.get("alt"):
                if keywords:
                    keyword = keywords[i % len(keywords)]
                    optimized["alt"] = f"{keyword} - image {i + 1}"
                else:
                    optimized["alt"] = f"Image {i + 1}"

            # 自动生成Title
            if not optimized.get("title"):
                optimized["title"] = optimized["alt"]

            # 文件名优化（URL中包含关键词）
            url = optimized.get("url", "")
            if url:
                parsed = urlparse(url)
                filename = parsed.path.split("/")[-1]
                if keywords and not any(k in filename.lower() for k in keywords):
                    # 文件名中没有关键词，建议重命名
                    optimized["filename_suggestion"] = f"{keywords[0].replace(' ', '-')}-{i + 1}.jpg"

            optimized_images.append(optimized)

        return optimized_images

    def analyze_seo(self, content: str, title: str = "", description: str = "",
                    images: List[Dict] = None, headings: List[str] = None,
                    links: List[str] = None, schema_count: int = 0) -> SEOAnalysisResult:
        """
        分析页面SEO

        Args:
            content: 页面内容
            title: 页面标题
            description: Meta描述
            images: 图片列表
            headings: 标题列表
            links: 链接列表
            schema_count: Schema数量

        Returns:
            SEO分析结果
        """
        issues = []
        suggestions = []

        # 标题评分
        title_score = 50
        if title:
            title_len = len(title)
            if self.settings.title_length_min <= title_len <= self.settings.title_length_max:
                title_score = 100
            elif title_len < self.settings.title_length_min:
                title_score = 60
                issues.append({"type": "title", "message": "标题太短", "severity": "warning"})
                suggestions.append("建议增加标题长度到30-60字符")
            else:
                title_score = 70
                issues.append({"type": "title", "message": "标题太长", "severity": "warning"})
                suggestions.append("建议缩短标题到60字符以内")
        else:
            title_score = 0
            issues.append({"type": "title", "message": "缺少标题", "severity": "error"})
            suggestions.append("请添加页面标题")

        # 描述评分
        desc_score = 50
        if description:
            desc_len = len(description)
            if self.settings.description_length_min <= desc_len <= self.settings.description_length_max:
                desc_score = 100
            elif desc_len < self.settings.description_length_min:
                desc_score = 50
                issues.append({"type": "description", "message": "描述太短", "severity": "warning"})
                suggestions.append("建议增加Meta描述长度到120-160字符")
            else:
                desc_score = 70
                issues.append({"type": "description", "message": "描述太长", "severity": "warning"})
                suggestions.append("建议缩短Meta描述到160字符以内")
        else:
            desc_score = 0
            issues.append({"type": "description", "message": "缺少Meta描述", "severity": "error"})
            suggestions.append("请添加Meta描述")

        # 标题层级评分
        heading_score = 50
        if headings:
            h1_count = sum(1 for h in headings if h.lower() == "h1")
            if h1_count == 1:
                heading_score = 90
            elif h1_count == 0:
                heading_score = 40
                issues.append({"type": "headings", "message": "缺少H1标题", "severity": "error"})
                suggestions.append("请添加一个H1标题")
            else:
                heading_score = 60
                issues.append({"type": "headings", "message": "多个H1标题", "severity": "warning"})
                suggestions.append("建议只使用一个H1标题")
        else:
            heading_score = 30
            issues.append({"type": "headings", "message": "没有标题层级", "severity": "warning"})
            suggestions.append("建议添加H1-H6标题层级")

        # 内容评分
        content_score = 50
        if content:
            word_count = len(re.findall(r'\b\w+\b', content))
            if word_count >= 1000:
                content_score = 100
            elif word_count >= 500:
                content_score = 80
            elif word_count >= 300:
                content_score = 60
            else:
                content_score = 40
                issues.append({"type": "content", "message": "内容太少", "severity": "warning"})
                suggestions.append("建议增加内容到至少300字")

            # 关键词密度检查
            keywords = self.extract_keywords(content, 1)
            if keywords:
                main_keyword = keywords[0]
                keyword_count = content.lower().count(main_keyword.lower())
                density = (keyword_count * len(main_keyword) / len(content)) * 100
                if 1 <= density <= 3:
                    content_score = min(content_score + 10, 100)
                elif density > 5:
                    content_score -= 20
                    issues.append({"type": "content", "message": "关键词堆砌", "severity": "warning"})
                    suggestions.append("建议降低关键词密度到1-3%")
        else:
            content_score = 0
            issues.append({"type": "content", "message": "没有内容", "severity": "error"})
            suggestions.append("请添加页面内容")

        # 图片评分
        image_score = 50
        if images:
            alt_count = sum(1 for img in images if img.get("alt"))
            alt_ratio = alt_count / len(images)
            if alt_ratio == 1:
                image_score = 100
            elif alt_ratio >= 0.8:
                image_score = 80
            elif alt_ratio >= 0.5:
                image_score = 60
            else:
                image_score = 40
                issues.append({"type": "images", "message": "图片缺少ALT文本", "severity": "warning"})
                suggestions.append("建议为所有图片添加ALT文本")
        else:
            image_score = 50  # 没有图片不扣分

        # 链接评分
        links_score = 50
        if links:
            internal_links = sum(1 for link in links if link.startswith("/") or "localhost" in link)
            external_links = len(links) - internal_links

            if internal_links >= 2 and external_links >= 1:
                links_score = 90
            elif internal_links >= 1:
                links_score = 70
            else:
                links_score = 50
                issues.append({"type": "links", "message": "缺少内部链接", "severity": "info"})
                suggestions.append("建议添加2-3个内部链接")
        else:
            links_score = 40
            issues.append({"type": "links", "message": "没有链接", "severity": "info"})
            suggestions.append("建议添加内部和外部链接")

        # Schema评分
        schema_score = 50
        if schema_count > 0:
            schema_score = 100
        else:
            schema_score = 30
            issues.append({"type": "schema", "message": "缺少Schema标记", "severity": "warning"})
            suggestions.append("建议添加结构化数据（Schema）")

        # 计算总分
        total_score = int(
            title_score * 0.15 +
            desc_score * 0.15 +
            heading_score * 0.15 +
            content_score * 0.25 +
            image_score * 0.1 +
            links_score * 0.1 +
            schema_score * 0.1
        )

        return SEOAnalysisResult(
            score=total_score,
            title_score=title_score,
            description_score=desc_score,
            heading_score=heading_score,
            content_score=content_score,
            image_score=image_score,
            links_score=links_score,
            schema_score=schema_score,
            issues=issues,
            suggestions=suggestions,
        )

    def generate_speed_optimization_suggestions(self, site_url: str = "") -> List[Dict[str, Any]]:
        """
        生成速度优化建议

        Args:
            site_url: 站点URL

        Returns:
            优化建议列表
        """
        suggestions = [
            {
                "category": "caching",
                "title": "启用页面缓存",
                "description": "配置浏览器缓存和服务器端缓存，减少重复加载",
                "priority": "high",
                "impact": "high",
            },
            {
                "category": "images",
                "title": "优化图片",
                "description": "压缩图片、使用WebP格式、实现懒加载",
                "priority": "high",
                "impact": "high",
            },
            {
                "category": "css",
                "title": "优化CSS",
                "description": "合并压缩CSS、内联关键CSS、延迟加载非关键CSS",
                "priority": "medium",
                "impact": "medium",
            },
            {
                "category": "js",
                "title": "优化JavaScript",
                "description": "延迟加载JS、移除未使用的脚本、使用async/defer",
                "priority": "medium",
                "impact": "medium",
            },
            {
                "category": "cdn",
                "title": "使用CDN",
                "description": "使用内容分发网络加速静态资源加载",
                "priority": "medium",
                "impact": "high",
            },
            {
                "category": "database",
                "title": "数据库优化",
                "description": "清理数据库、优化查询、使用对象缓存",
                "priority": "low",
                "impact": "medium",
            },
            {
                "category": "fonts",
                "title": "字体优化",
                "description": "使用系统字体、预加载字体、font-display: swap",
                "priority": "low",
                "impact": "low",
            },
            {
                "category": "plugins",
                "title": "减少插件",
                "description": "禁用或删除不必要的插件，减少HTTP请求",
                "priority": "medium",
                "impact": "medium",
            },
        ]

        return suggestions


# 单例实例
_seo_service = None


def get_seo_service() -> SEOService:
    """获取SEO服务单例"""
    global _seo_service
    if _seo_service is None:
        _seo_service = SEOService()
    return _seo_service
