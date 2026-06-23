"""
增强的SEO服务
页面SEO、技术SEO、Schema结构化数据、内部链接、图片SEO
"""
import re
import random
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class SEOScore:
    """SEO评分"""
    overall: float = 0.0
    title: float = 0.0
    description: float = 0.0
    headings: float = 0.0
    content: float = 0.0
    images: float = 0.0
    links: float = 0.0
    schema: float = 0.0
    speed: float = 0.0
    mobile: float = 0.0
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class SchemaData:
    """Schema结构化数据"""
    schema_type: str
    data: Dict[str, Any]
    
    def to_json_ld(self) -> Dict[str, Any]:
        """转换为JSON-LD格式"""
        return {
            "@context": "https://schema.org",
            "@type": self.schema_type,
            **self.data,
        }


class KeywordGenerator:
    """关键词生成器"""
    
    # LSI关键词模板
    LSI_TEMPLATES = {
        "product": [
            "best {keyword}",
            "{keyword} review",
            "{keyword} for sale",
            "{keyword} price",
            "buy {keyword}",
            "{keyword} near me",
            "{keyword} vs",
            "how to use {keyword}",
            "{keyword} benefits",
            "{keyword} features",
            "cheap {keyword}",
            "{keyword} discount",
            "{keyword} coupon",
            "{keyword} free shipping",
            "where to buy {keyword}",
        ],
        "service": [
            "best {keyword} service",
            "{keyword} company",
            "{keyword} near me",
            "professional {keyword}",
            "affordable {keyword}",
            "{keyword} cost",
            "{keyword} price",
            "{keyword} reviews",
            "top {keyword}",
            "{keyword} expert",
            "{keyword} consultant",
            "{keyword} agency",
            "{keyword} solution",
            "{keyword} provider",
            "hire {keyword}",
        ],
        "blog": [
            "what is {keyword}",
            "how to {keyword}",
            "{keyword} guide",
            "{keyword} tips",
            "{keyword} tutorial",
            "{keyword} examples",
            "{keyword} best practices",
            "{keyword} for beginners",
            "{keyword} step by step",
            "{keyword} checklist",
            "{keyword} template",
            "{keyword} tools",
            "{keyword} resources",
            "{keyword} ideas",
            "{keyword} trends",
        ],
    }
    
    def __init__(self):
        # 关键词缓存，避免对同一主关键词重复生成
        self._cache: Dict[str, List[str]] = {}
        # 独立的随机数生成器，避免影响全局random状态
        self._rng = random.Random()

    def generate_lsi_keywords(self,
                               primary_keyword: str,
                               keyword_type: str = "product",
                               count: int = 10) -> List[str]:
        """
        生成LSI关键词
        
        Args:
            primary_keyword: 主关键词
            keyword_type: 关键词类型 (product, service, blog)
            count: 生成数量
            
        Returns:
            LSI关键词列表
        """
        templates = self.LSI_TEMPLATES.get(keyword_type, self.LSI_TEMPLATES["product"])
        
        keywords = []
        for template in templates:
            keyword = template.format(keyword=primary_keyword)
            keywords.append(keyword)
        
        # 随机选择指定数量
        if len(keywords) > count:
            keywords = random.sample(keywords, count)
        
        return keywords
    
    def generate_long_tail_keywords(self, 
                                     primary_keyword: str,
                                     modifiers: Optional[List[str]] = None,
                                     count: int = 10) -> List[str]:
        """
        生成长尾关键词
        
        Args:
            primary_keyword: 主关键词
            modifiers: 修饰词列表
            count: 生成数量
            
        Returns:
            长尾关键词列表
        """
        default_modifiers = [
            "best", "cheap", "affordable", "professional", "top",
            "2024", "2025", "guide", "review", "tutorial",
            "for beginners", "step by step", "complete", "ultimate",
            "near me", "online", "free", "discount", "coupon",
        ]
        
        modifiers = modifiers or default_modifiers
        
        long_tails = []
        for modifier in modifiers:
            if random.random() < 0.5:
                keyword = f"{modifier} {primary_keyword}"
            else:
                keyword = f"{primary_keyword} {modifier}"
            long_tails.append(keyword)
        
        # 随机选择指定数量
        if len(long_tails) > count:
            long_tails = random.sample(long_tails, count)
        
        return long_tails
    
    def generate_question_keywords(self, primary_keyword: str) -> List[str]:
        """
        生成问题式关键词
        
        Args:
            primary_keyword: 主关键词
            
        Returns:
            问题式关键词列表
        """
        question_templates = [
            f"What is {primary_keyword}?",
            f"How does {primary_keyword} work?",
            f"Why is {primary_keyword} important?",
            f"Where can I buy {primary_keyword}?",
            f"When should I use {primary_keyword}?",
            f"Who needs {primary_keyword}?",
            f"Which {primary_keyword} is best?",
            f"How much does {primary_keyword} cost?",
            f"Is {primary_keyword} worth it?",
            f"Can {primary_keyword} help me?",
            f"What are the benefits of {primary_keyword}?",
            f"How to choose the right {primary_keyword}?",
        ]
        
        return question_templates


class SchemaGenerator:
    """Schema结构化数据生成器"""

    def __init__(self):
        # 支持的Schema类型注册表
        self._supported_types = {
            "Product", "Article", "FAQPage", "Organization",
            "WebSite", "BreadcrumbList", "Review", "LocalBusiness",
            "Event", "Recipe", "VideoObject", "HowTo",
        }

    def generate_product_schema(self, product: Dict[str, Any]) -> SchemaData:
        """
        生成产品Schema
        
        Args:
            product: 产品信息
            
        Returns:
            Schema数据
        """
        data = {
            "name": product.get("name", ""),
            "description": product.get("description", ""),
            "image": product.get("image", ""),
            "sku": product.get("sku", ""),
            "brand": {
                "@type": "Brand",
                "name": product.get("brand", ""),
            },
            "offers": {
                "@type": "Offer",
                "price": product.get("price", "0"),
                "priceCurrency": product.get("currency", "USD"),
                "availability": "https://schema.org/InStock" if product.get("in_stock", True) else "https://schema.org/OutOfStock",
                "url": product.get("url", ""),
            },
        }
        
        # 添加评分
        if product.get("rating"):
            data["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": product["rating"],
                "reviewCount": product.get("review_count", 0),
            }
        
        # 添加评价
        if product.get("reviews"):
            reviews = []
            for review in product["reviews"][:5]:  # 最多5条
                reviews.append({
                    "@type": "Review",
                    "reviewRating": {
                        "@type": "Rating",
                        "ratingValue": review.get("rating", 5),
                    },
                    "author": {
                        "@type": "Person",
                        "name": review.get("author", ""),
                    },
                    "reviewBody": review.get("content", ""),
                })
            data["review"] = reviews
        
        return SchemaData(schema_type="Product", data=data)
    
    def generate_article_schema(self, article: Dict[str, Any]) -> SchemaData:
        """
        生成文章Schema
        
        Args:
            article: 文章信息
            
        Returns:
            Schema数据
        """
        data = {
            "headline": article.get("title", ""),
            "description": article.get("description", ""),
            "image": article.get("image", ""),
            "datePublished": article.get("date_published", ""),
            "dateModified": article.get("date_modified", ""),
            "author": {
                "@type": "Person",
                "name": article.get("author", ""),
            },
            "publisher": {
                "@type": "Organization",
                "name": article.get("publisher", ""),
                "logo": {
                    "@type": "ImageObject",
                    "url": article.get("logo", ""),
                },
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": article.get("url", ""),
            },
        }
        
        return SchemaData(schema_type="Article", data=data)
    
    def generate_faq_schema(self, faqs: List[Dict[str, str]]) -> SchemaData:
        """
        生成FAQ Schema
        
        Args:
            faqs: FAQ列表，每个包含question和answer
            
        Returns:
            Schema数据
        """
        main_entity = []
        for faq in faqs:
            main_entity.append({
                "@type": "Question",
                "name": faq.get("question", ""),
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq.get("answer", ""),
                },
            })
        
        data = {
            "mainEntity": main_entity,
        }
        
        return SchemaData(schema_type="FAQPage", data=data)
    
    def generate_breadcrumb_schema(self, items: List[Dict[str, str]]) -> SchemaData:
        """
        生成面包屑Schema
        
        Args:
            items: 面包屑项列表，每个包含name和url
            
        Returns:
            Schema数据
        """
        item_list_element = []
        for i, item in enumerate(items, 1):
            item_list_element.append({
                "@type": "ListItem",
                "position": i,
                "name": item.get("name", ""),
                "item": item.get("url", ""),
            })
        
        data = {
            "itemListElement": item_list_element,
        }
        
        return SchemaData(schema_type="BreadcrumbList", data=data)
    
    def generate_review_schema(self, reviews: List[Dict[str, Any]]) -> SchemaData:
        """
        生成评价Schema
        
        Args:
            reviews: 评价列表
            
        Returns:
            Schema数据
        """
        # 简化为单个评价
        if reviews:
            review = reviews[0]
            data = {
                "itemReviewed": {
                    "@type": "Product",
                    "name": review.get("product_name", ""),
                },
                "reviewRating": {
                    "@type": "Rating",
                    "ratingValue": review.get("rating", 5),
                    "bestRating": 5,
                    "worstRating": 1,
                },
                "author": {
                    "@type": "Person",
                    "name": review.get("author", ""),
                },
                "reviewBody": review.get("content", ""),
                "datePublished": review.get("date", ""),
            }
        else:
            data = {}
        
        return SchemaData(schema_type="Review", data=data)
    
    def generate_local_business_schema(self, business: Dict[str, Any]) -> SchemaData:
        """
        生成本地商家Schema
        
        Args:
            business: 商家信息
            
        Returns:
            Schema数据
        """
        data = {
            "name": business.get("name", ""),
            "description": business.get("description", ""),
            "url": business.get("url", ""),
            "telephone": business.get("phone", ""),
            "address": {
                "@type": "PostalAddress",
                "streetAddress": business.get("street_address", ""),
                "addressLocality": business.get("city", ""),
                "addressRegion": business.get("state", ""),
                "postalCode": business.get("postal_code", ""),
                "addressCountry": business.get("country", ""),
            },
            "openingHours": business.get("opening_hours", []),
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": business.get("latitude", ""),
                "longitude": business.get("longitude", ""),
            },
            "image": business.get("image", ""),
            "priceRange": business.get("price_range", "$$"),
        }
        
        return SchemaData(schema_type="LocalBusiness", data=data)
    
    def generate_organization_schema(self, org: Dict[str, Any]) -> SchemaData:
        """
        生成组织Schema
        
        Args:
            org: 组织信息
            
        Returns:
            Schema数据
        """
        data = {
            "name": org.get("name", ""),
            "description": org.get("description", ""),
            "url": org.get("url", ""),
            "logo": org.get("logo", ""),
            "contactPoint": {
                "@type": "ContactPoint",
                "telephone": org.get("phone", ""),
                "contactType": "customer service",
                "email": org.get("email", ""),
            },
            "sameAs": org.get("social_links", []),
        }
        
        return SchemaData(schema_type="Organization", data=data)
    
    def generate_website_schema(self, website: Dict[str, Any]) -> SchemaData:
        """
        生成网站Schema
        
        Args:
            website: 网站信息
            
        Returns:
            Schema数据
        """
        data = {
            "name": website.get("name", ""),
            "url": website.get("url", ""),
            "potentialAction": {
                "@type": "SearchAction",
                "target": f"{website.get('url', '')}?s={{search_term_string}}",
                "query-input": "required name=search_term_string",
            },
        }
        
        return SchemaData(schema_type="WebSite", data=data)


class InternalLinkBuilder:
    """内部链接建设器"""

    def __init__(self):
        # 已插入链接的关键词集合，避免重复链接
        self._linked_keywords: set = set()
        # 累计插入的链接总数
        self._total_links_added: int = 0

    def build_internal_links(self,
                             content: str,
                             keywords: List[Dict[str, str]],
                             max_links: int = 5) -> str:
        """
        在内容中自动插入内部链接
        
        Args:
            content: 原始内容
            keywords: 关键词列表，每个包含keyword和url
            max_links: 最大链接数
            
        Returns:
            带内部链接的内容
        """
        linked_content = content
        links_added = 0
        
        for kw in keywords:
            if links_added >= max_links:
                break
            
            keyword = kw.get("keyword", "")
            url = kw.get("url", "")
            
            if not keyword or not url:
                continue
            
            # 只替换第一次出现，且不在已有的链接中
            pattern = re.compile(rf'{re.escape(keyword)}(?!</a>)', re.IGNORECASE)
            match = pattern.search(linked_content)
            
            if match:
                # 创建链接
                link_html = f'<a href="{url}" title="{keyword}">{keyword}</a>'
                linked_content = linked_content[:match.start()] + link_html + linked_content[match.end():]
                links_added += 1
        
        logger.info(f"Added {links_added} internal links")
        return linked_content
    
    def generate_related_posts(self, 
                                current_post: Dict[str, Any],
                                all_posts: List[Dict[str, Any]],
                                count: int = 3) -> List[Dict[str, Any]]:
        """
        生成相关文章推荐
        
        Args:
            current_post: 当前文章
            all_posts: 所有文章
            count: 推荐数量
            
        Returns:
            相关文章列表
        """
        # 简化实现：随机选择
        related = random.sample(all_posts, min(count, len(all_posts)))
        return related
    
    def build_breadcrumbs(self, 
                          current_page: str,
                          hierarchy: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        构建面包屑导航
        
        Args:
            current_page: 当前页面
            hierarchy: 层级结构
            
        Returns:
            面包屑列表
        """
        breadcrumbs = [
            {"name": "Home", "url": "/"},
        ]
        breadcrumbs.extend(hierarchy)
        breadcrumbs.append({"name": current_page, "url": ""})
        
        return breadcrumbs


class ImageSEO:
    """图片SEO优化器"""

    def __init__(self):
        # 支持的图片格式
        self._supported_formats = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"}
        # ALT文本最大长度（SEO最佳实践）
        self._max_alt_length: int = 125

    def generate_alt_text(self,
                          image_name: str,
                          product_name: Optional[str] = None,
                          context: Optional[str] = None) -> str:
        """
        自动生成图片ALT文本
        
        Args:
            image_name: 图片文件名
            product_name: 产品名称
            context: 上下文
            
        Returns:
            ALT文本
        """
        # 清理文件名
        alt = image_name.replace("-", " ").replace("_", " ").replace(".jpg", "").replace(".png", "")
        alt = alt.title()
        
        # 如果有产品名称，使用产品名称
        if product_name:
            alt = f"{product_name} - {alt}" if context else product_name
        
        # 限制长度
        if len(alt) > 125:
            alt = alt[:122] + "..."
        
        return alt
    
    def optimize_image_filename(self, 
                                 original_filename: str,
                                 keyword: str) -> str:
        """
        优化图片文件名（SEO友好）
        
        Args:
            original_filename: 原始文件名
            keyword: 关键词
            
        Returns:
            优化后的文件名
        """
        # 获取扩展名
        ext = original_filename.split(".")[-1].lower() if "." in original_filename else "jpg"
        
        # 清理关键词
        clean_keyword = keyword.lower().replace(" ", "-")
        clean_keyword = re.sub(r"[^a-z0-9-]", "", clean_keyword)
        
        # 添加随机后缀避免重复
        import hashlib
        hash_suffix = hashlib.md5(original_filename.encode()).hexdigest()[:6]
        
        optimized_filename = f"{clean_keyword}-{hash_suffix}.{ext}"
        
        return optimized_filename
    
    def generate_image_sitemap(self, images: List[Dict[str, Any]]) -> str:
        """
        生成图片Sitemap XML
        
        Args:
            images: 图片列表
            
        Returns:
            XML格式的图片Sitemap
        """
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        xml += 'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
        
        for image in images:
            xml += "  <url>\n"
            xml += f"    <loc>{image.get('page_url', '')}</loc>\n"
            xml += "    <image:image>\n"
            xml += f"      <image:loc>{image.get('image_url', '')}</image:loc>\n"
            xml += f"      <image:title><![CDATA[{image.get('title', '')}]]></image:title>\n"
            xml += f"      <image:caption><![CDATA[{image.get('caption', '')}]]></image:caption>\n"
            xml += "    </image:image>\n"
            xml += "  </url>\n"
        
        xml += "</urlset>"
        
        return xml


class SEOService:
    """增强的SEO服务"""
    
    def __init__(self):
        self.keyword_generator = KeywordGenerator()
        self.schema_generator = SchemaGenerator()
        self.internal_link_builder = InternalLinkBuilder()
        self.image_seo = ImageSEO()
    
    def optimize_page_seo(self, 
                          title: str,
                          description: str,
                          content: str,
                          primary_keyword: str,
                          options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        优化页面SEO
        
        Args:
            title: 页面标题
            description: 页面描述
            content: 页面内容
            primary_keyword: 主关键词
            options: 优化选项
            
        Returns:
            优化结果
        """
        options = options or {}
        
        result = {
            "original": {
                "title": title,
                "description": description,
            },
            "optimized": {},
            "score": {},
            "recommendations": [],
        }
        
        # 优化标题
        optimized_title = self._optimize_title(title, primary_keyword)
        result["optimized"]["title"] = optimized_title
        
        # 优化描述
        optimized_description = self._optimize_description(description, primary_keyword)
        result["optimized"]["description"] = optimized_description
        
        # 优化内容
        optimized_content = self._optimize_content(content, primary_keyword)
        result["optimized"]["content"] = optimized_content
        
        # 生成LSI关键词
        lsi_keywords = self.keyword_generator.generate_lsi_keywords(primary_keyword)
        result["lsi_keywords"] = lsi_keywords
        
        # 生成长尾关键词
        long_tail_keywords = self.keyword_generator.generate_long_tail_keywords(primary_keyword)
        result["long_tail_keywords"] = long_tail_keywords
        
        # 计算SEO评分
        score = self.calculate_seo_score(
            title=optimized_title,
            description=optimized_description,
            content=optimized_content,
            keyword=primary_keyword,
        )
        result["score"] = score
        
        return result
    
    def _optimize_title(self, title: str, keyword: str) -> str:
        """优化标题"""
        # 确保关键词在标题中
        if keyword.lower() not in title.lower():
            title = f"{keyword} - {title}"
        
        # 限制长度（50-60字符最佳）
        if len(title) > 60:
            title = title[:57] + "..."
        
        return title
    
    def _optimize_description(self, description: str, keyword: str) -> str:
        """优化描述"""
        # 确保关键词在描述中
        if keyword.lower() not in description.lower():
            description = f"{keyword}. {description}"
        
        # 限制长度（150-160字符最佳）
        if len(description) > 160:
            description = description[:157] + "..."
        
        return description
    
    def _optimize_content(self, content: str, keyword: str) -> str:
        """优化内容

        确保关键词密度在1-3%之间，密度过低时在合适位置自然插入关键词。
        """
        if not keyword or not content:
            return content

        # 确保关键词密度在1-3%之间
        word_count = len(content.split())
        keyword_count = content.lower().count(keyword.lower())

        if word_count > 0:
            density = keyword_count / word_count * 100

            # 如果密度太低，在合适的位置自然插入关键词
            if density < 1.0:
                # 计算需要插入的次数，使密度达到约1.5%
                target_count = max(1, int(word_count * 0.015))
                insertions_needed = target_count - keyword_count
                if insertions_needed > 0:
                    content = self._insert_keyword_naturally(content, keyword, insertions_needed)

        return content

    def _insert_keyword_naturally(self, content: str, keyword: str, count: int) -> str:
        """在内容的自然位置插入关键词

        优先在段落开头或句号后插入，避免破坏内容结构。

        Args:
            content: 原始内容
            keyword: 要插入的关键词
            count: 插入次数

        Returns:
            插入关键词后的内容
        """
        # 按段落分割
        paragraphs = content.split("\n")
        inserted = 0

        for i, para in enumerate(paragraphs):
            if inserted >= count:
                break
            if not para.strip():
                continue

            # 在段落首句后插入关键词（句号、问号、感叹号后）
            sentence_end = re.search(r'[.。!！?？]\s*', para)
            if sentence_end:
                pos = sentence_end.end()
                # 构造自然的插入语句
                insertion = f" {keyword} "
                paragraphs[i] = para[:pos] + insertion + para[pos:]
                inserted += 1
            elif inserted == 0 and len(para) > 20:
                # 第一个段落且无句号时，在开头插入
                paragraphs[i] = f"{keyword}. {para}"
                inserted += 1

        return "\n".join(paragraphs)
    
    def calculate_seo_score(self,
                            title: str,
                            description: str,
                            content: str,
                            keyword: str,
                            images: Optional[List[Dict[str, Any]]] = None,
                            links: Optional[List[str]] = None) -> SEOScore:
        """
        计算SEO评分
        
        Args:
            title: 页面标题
            description: 页面描述
            content: 页面内容
            keyword: 关键词
            images: 图片列表
            links: 链接列表
            
        Returns:
            SEO评分
        """
        score = SEOScore()
        issues = []
        recommendations = []
        
        # 标题评分
        title_score = 0
        if keyword.lower() in title.lower():
            title_score += 40
            if title.lower().startswith(keyword.lower()):
                title_score += 10
        else:
            issues.append("标题中未包含关键词")
            recommendations.append("在页面标题中添加目标关键词")
        
        if 50 <= len(title) <= 60:
            title_score += 30
        elif len(title) < 50:
            issues.append("标题过短")
            recommendations.append("建议标题长度在50-60字符之间")
            title_score += 15
        else:
            issues.append("标题过长")
            recommendations.append("建议标题长度不超过60字符")
            title_score += 20
        
        score.title = title_score / 80 * 100
        
        # 描述评分
        desc_score = 0
        if keyword.lower() in description.lower():
            desc_score += 40
        else:
            issues.append("描述中未包含关键词")
            recommendations.append("在Meta描述中添加目标关键词")
        
        if 150 <= len(description) <= 160:
            desc_score += 40
        elif len(description) < 150:
            desc_score += 20
            issues.append("描述过短")
            recommendations.append("建议Meta描述长度在150-160字符之间")
        else:
            desc_score += 25
            issues.append("描述过长")
            recommendations.append("建议Meta描述不超过160字符")
        
        score.description = desc_score / 80 * 100
        
        # 内容评分
        content_score = 0
        word_count = len(content.split())
        
        if word_count >= 300:
            content_score += 20
        elif word_count >= 100:
            content_score += 10
            issues.append("内容字数较少")
            recommendations.append("建议内容至少300字以上")
        else:
            issues.append("内容过短")
            recommendations.append("建议增加内容长度")
        
        # 关键词密度
        if word_count > 0:
            keyword_count = content.lower().count(keyword.lower())
            density = keyword_count / word_count * 100
            
            if 1 <= density <= 3:
                content_score += 30
            elif density < 1:
                content_score += 15
                issues.append("关键词密度过低")
                recommendations.append(f"建议关键词密度在1-3%之间，当前为{density:.1f}%")
            else:
                content_score += 10
                issues.append("关键词密度过高")
                recommendations.append("避免关键词堆砌，保持自然密度")
        
        # 标题层级
        h1_count = content.count("<h1")
        h2_count = content.count("<h2")
        
        if h1_count == 1:
            content_score += 15
        elif h1_count == 0:
            issues.append("缺少H1标题")
            recommendations.append("确保页面有且仅有一个H1标题")
        else:
            issues.append("多个H1标题")
            recommendations.append("一个页面应该只有一个H1标题")
        
        if h2_count >= 2:
            content_score += 15
        elif h2_count == 1:
            content_score += 8
        else:
            issues.append("缺少H2子标题")
            recommendations.append("使用H2标题组织内容结构")
        
        score.content = content_score / 80 * 100
        
        # 图片评分
        image_score = 0
        if images:
            images_with_alt = sum(1 for img in images if img.get("alt"))
            if images_with_alt == len(images):
                image_score = 100
            else:
                image_score = images_with_alt / len(images) * 100
                issues.append(f"{len(images) - images_with_alt}张图片缺少ALT属性")
                recommendations.append("为所有图片添加描述性的ALT文本")
        else:
            image_score = 50
            issues.append("页面缺少图片")
            recommendations.append("添加相关图片提升内容质量")
        
        score.images = image_score
        
        # 链接评分
        link_score = 0
        if links:
            internal_links = sum(1 for link in links if link.startswith("/"))
            external_links = len(links) - internal_links
            
            if internal_links >= 2:
                link_score += 50
            else:
                link_score += 25
                issues.append("内部链接较少")
                recommendations.append("添加更多相关的内部链接")
            
            if external_links >= 1:
                link_score += 50
            else:
                link_score += 25
                issues.append("缺少外部链接")
                recommendations.append("添加权威的外部链接")
        else:
            link_score = 30
            issues.append("页面缺少链接")
            recommendations.append("添加内部和外部链接")
        
        score.links = link_score
        
        # 总分
        score.overall = (
            score.title * 0.2 +
            score.description * 0.15 +
            score.content * 0.3 +
            score.images * 0.15 +
            score.links * 0.2
        )
        
        score.issues = issues
        score.recommendations = recommendations
        
        return score
    
    def generate_all_schemas(self, 
                             page_type: str,
                             data: Dict[str, Any]) -> List[SchemaData]:
        """
        生成所有适用的Schema
        
        Args:
            page_type: 页面类型
            data: 页面数据
            
        Returns:
            Schema数据列表
        """
        schemas = []
        
        if page_type == "product":
            # 产品页面
            if "product" in data:
                schemas.append(self.schema_generator.generate_product_schema(data["product"]))
            
            # FAQ
            if "faqs" in data:
                schemas.append(self.schema_generator.generate_faq_schema(data["faqs"]))
            
            # 面包屑
            if "breadcrumbs" in data:
                schemas.append(self.schema_generator.generate_breadcrumb_schema(data["breadcrumbs"]))
        
        elif page_type == "article":
            # 文章页面
            if "article" in data:
                schemas.append(self.schema_generator.generate_article_schema(data["article"]))
            
            # 面包屑
            if "breadcrumbs" in data:
                schemas.append(self.schema_generator.generate_breadcrumb_schema(data["breadcrumbs"]))
        
        elif page_type == "about":
            # 关于页面
            if "organization" in data:
                schemas.append(self.schema_generator.generate_organization_schema(data["organization"]))
        
        elif page_type == "contact":
            # 联系页面
            if "local_business" in data:
                schemas.append(self.schema_generator.generate_local_business_schema(data["local_business"]))
        
        # 网站Schema（所有页面都可以有）
        if "website" in data:
            schemas.append(self.schema_generator.generate_website_schema(data["website"]))
        
        return schemas
    
    def generate_seo_report(self, 
                            url: str,
                            title: str,
                            description: str,
                            content: str,
                            keyword: str) -> Dict[str, Any]:
        """
        生成SEO报告
        
        Args:
            url: 页面URL
            title: 页面标题
            description: 页面描述
            content: 页面内容
            keyword: 关键词
            
        Returns:
            SEO报告
        """
        score = self.calculate_seo_score(title, description, content, keyword)
        
        report = {
            "url": url,
            "keyword": keyword,
            "overall_score": score.overall,
            "grade": self._get_grade(score.overall),
            "detailed_scores": {
                "title": score.title,
                "description": score.description,
                "content": score.content,
                "images": score.images,
                "links": score.links,
            },
            "issues": score.issues,
            "recommendations": score.recommendations,
            "preview": {
                "google": self._generate_google_preview(title, description, url),
            },
        }
        
        return report
    
    def _get_grade(self, score: float) -> str:
        """根据分数获取等级"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    def _generate_google_preview(self, title: str, description: str, url: str) -> Dict[str, str]:
        """生成Google搜索预览"""
        return {
            "title": title[:60] + ("..." if len(title) > 60 else ""),
            "description": description[:160] + ("..." if len(description) > 160 else ""),
            "url": url,
        }
    
    def get_speed_optimization_tips(self) -> List[str]:
        """获取速度优化建议"""
        return [
            "启用Gzip/Brotli压缩",
            "启用浏览器缓存",
            "使用CDN加速静态资源",
            "优化图片（压缩、WebP格式）",
            "延迟加载图片和视频",
            "最小化CSS和JavaScript",
            "移除未使用的CSS和JS",
            "使用字体子集化",
            "优化数据库查询",
            "使用对象缓存（Redis/Memcached）",
            "启用HTTP/2",
            "预加载关键资源",
            "减少第三方脚本",
            "使用懒加载评论和社交媒体小部件",
            "优化Core Web Vitals（LCP、FID、CLS）",
        ]


# 全局SEO服务实例
seo_service = SEOService()
