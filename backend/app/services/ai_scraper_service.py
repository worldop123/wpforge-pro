"""
AI智能采集识别服务
自动识别网站结构、字段映射、分页方式、货币类型等
"""
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import re
from urllib.parse import urlparse
from app.core.logging import get_logger

logger = get_logger(__name__)


class SiteType(str, Enum):
    """网站类型"""
    WOOCOMMERCE = "woocommerce"
    SHOPIFY = "shopify"
    MAGENTO = "magento"
    CUSTOM_ECOMMERCE = "custom_ecommerce"
    BLOG = "blog"
    CORPORATE = "corporate"
    UNKNOWN = "unknown"


class PaginationType(str, Enum):
    """分页类型"""
    NEXT_BUTTON = "next_button"
    PAGE_NUMBERS = "page_numbers"
    INFINITE_SCROLL = "infinite_scroll"
    LOAD_MORE = "load_more"
    NONE = "none"


@dataclass
class DetectedField:
    """检测到的字段"""
    name: str
    selector: str
    attribute: Optional[str] = None
    multiple: bool = False
    required: bool = False
    confidence: float = 0.0
    needs_translation: bool = False
    description: str = ""


@dataclass
class SiteAnalysisResult:
    """网站分析结果"""
    site_type: SiteType
    confidence: float
    pagination_type: PaginationType
    pagination_selector: Optional[str] = None
    product_list_selector: Optional[str] = None
    product_detail_url_pattern: Optional[str] = None
    detected_fields: List[DetectedField] = field(default_factory=list)
    currency: Optional[str] = None
    language: Optional[str] = None
    has_anti_detection: bool = False
    recommendations: List[str] = field(default_factory=list)


class AIScraperAnalyzer:
    """
    AI智能采集分析器
    自动识别网站结构，生成采集配置
    """
    
    def __init__(self):
        # 常见电商平台特征
        self._platform_signatures = {
            SiteType.WOOCOMMERCE: [
                'woocommerce',
                'wp-content',
                'wc-ajax',
                'product_cat',
                '?add-to-cart='
            ],
            SiteType.SHOPIFY: [
                'shopify',
                'cdn.shopify.com',
                '/products/',
                '/collections/',
                'shopify.com/cart'
            ],
            SiteType.MAGENTO: [
                'magento',
                'static/version',
                'checkout/cart',
                'catalog/product/view'
            ]
        }
        
        # 常见字段选择器模式
        self._field_patterns = {
            'title': [
                {'selector': 'h1.product_title', 'confidence': 0.95, 'platform': 'woocommerce'},
                {'selector': '.product_title', 'confidence': 0.9, 'platform': 'woocommerce'},
                {'selector': 'h1[itemprop="name"]', 'confidence': 0.85, 'platform': 'general'},
                {'selector': '.product-name h1', 'confidence': 0.8, 'platform': 'general'},
                {'selector': 'h1', 'confidence': 0.6, 'platform': 'general'}
            ],
            'price': [
                {'selector': '.price .amount', 'confidence': 0.95, 'platform': 'woocommerce'},
                {'selector': 'p.price .woocommerce-Price-amount', 'confidence': 0.9, 'platform': 'woocommerce'},
                {'selector': '[itemprop="price"]', 'confidence': 0.85, 'platform': 'general'},
                {'selector': '.product-price', 'confidence': 0.8, 'platform': 'general'},
                {'selector': '.price', 'confidence': 0.6, 'platform': 'general'}
            ],
            'description': [
                {'selector': '#tab-description', 'confidence': 0.95, 'platform': 'woocommerce'},
                {'selector': '.woocommerce-Tabs-panel--description', 'confidence': 0.9, 'platform': 'woocommerce'},
                {'selector': '[itemprop="description"]', 'confidence': 0.85, 'platform': 'general'},
                {'selector': '.product-description', 'confidence': 0.8, 'platform': 'general'},
                {'selector': '.description', 'confidence': 0.5, 'platform': 'general'}
            ],
            'short_description': [
                {'selector': '.woocommerce-product-details__short-description', 'confidence': 0.95, 'platform': 'woocommerce'},
                {'selector': '.short-description', 'confidence': 0.8, 'platform': 'general'}
            ],
            'sku': [
                {'selector': '.sku', 'confidence': 0.9, 'platform': 'woocommerce'},
                {'selector': '[itemprop="sku"]', 'confidence': 0.85, 'platform': 'general'},
                {'selector': '.product-sku', 'confidence': 0.7, 'platform': 'general'}
            ],
            'stock': [
                {'selector': '.stock', 'confidence': 0.9, 'platform': 'woocommerce'},
                {'selector': '[itemprop="availability"]', 'confidence': 0.85, 'platform': 'general'}
            ],
            'categories': [
                {'selector': '.product_meta .posted_in a', 'confidence': 0.9, 'platform': 'woocommerce', 'multiple': True},
                {'selector': '.product-categories a', 'confidence': 0.8, 'platform': 'general', 'multiple': True}
            ],
            'tags': [
                {'selector': '.product_meta .tagged_as a', 'confidence': 0.9, 'platform': 'woocommerce', 'multiple': True},
                {'selector': '.product-tags a', 'confidence': 0.8, 'platform': 'general', 'multiple': True}
            ],
            'images': [
                {'selector': '.woocommerce-product-gallery__image img', 'attribute': 'src', 'confidence': 0.95, 'platform': 'woocommerce', 'multiple': True},
                {'selector': '.flex-viewport img', 'attribute': 'src', 'confidence': 0.9, 'platform': 'woocommerce', 'multiple': True},
                {'selector': '.product-images img', 'attribute': 'src', 'confidence': 0.8, 'platform': 'general', 'multiple': True}
            ],
            'attributes': [
                {'selector': '.woocommerce-product-attributes-item', 'confidence': 0.9, 'platform': 'woocommerce', 'multiple': True},
                {'selector': '.product-attributes .attribute-item', 'confidence': 0.7, 'platform': 'general', 'multiple': True}
            ],
            'brand': [
                {'selector': '.product_brand a', 'confidence': 0.85, 'platform': 'woocommerce'},
                {'selector': '[itemprop="brand"]', 'confidence': 0.8, 'platform': 'general'},
                {'selector': '.product-brand', 'confidence': 0.7, 'platform': 'general'}
            ]
        }
        
        # 需要翻译的字段
        self._translatable_fields = {
            'title', 'description', 'short_description', 'categories', 'tags',
            'attributes', 'brand'
        }
        
        # 货币符号映射
        self._currency_symbols = {
            '$': 'USD',
            '€': 'EUR',
            '£': 'GBP',
            '¥': 'CNY',
            '₹': 'INR',
            '₩': 'KRW',
            '₽': 'RUB',
            '₺': 'TRY',
            'R$': 'BRL',
            '₴': 'UAH',
            'Ft': 'HUF',
            'lei': 'RON',
            'zł': 'PLN',
            'Kč': 'CZK'
        }
    
    def analyze_site(self, html_content: str, url: str = "") -> SiteAnalysisResult:
        """
        分析网站，自动识别结构和字段
        """
        result = SiteAnalysisResult(
            site_type=SiteType.UNKNOWN,
            confidence=0.0,
            pagination_type=PaginationType.NONE
        )
        
        # 1. 识别网站类型
        site_type, confidence = self._detect_site_type(html_content, url)
        result.site_type = site_type
        result.confidence = confidence
        
        # 2. 识别分页方式
        pagination_type, pagination_selector = self._detect_pagination(html_content)
        result.pagination_type = pagination_type
        result.pagination_selector = pagination_selector
        
        # 3. 识别产品列表选择器
        result.product_list_selector = self._detect_product_list(html_content, site_type)
        
        # 4. 识别产品详情页URL模式
        result.product_detail_url_pattern = self._detect_product_url_pattern(url, site_type)
        
        # 5. 检测产品字段
        result.detected_fields = self._detect_product_fields(html_content, site_type)
        
        # 6. 检测货币
        result.currency = self._detect_currency(html_content)
        
        # 7. 检测语言
        result.language = self._detect_language(html_content)
        
        # 8. 检测反检测机制
        result.has_anti_detection = self._detect_anti_detection(html_content)
        
        # 9. 生成建议
        result.recommendations = self._generate_recommendations(result)
        
        logger.info(f"网站分析完成: {site_type.value}, 置信度: {confidence:.2f}")
        return result
    
    def _detect_site_type(self, html: str, url: str) -> Tuple[SiteType, float]:
        """检测网站类型"""
        scores = {}
        
        for site_type, signatures in self._platform_signatures.items():
            score = 0
            for sig in signatures:
                if sig.lower() in html.lower():
                    score += 1
                if sig.lower() in url.lower():
                    score += 0.5
            
            if signatures:
                scores[site_type] = score / len(signatures)
        
        # 检查是否是电商网站
        ecommerce_signals = [
            'add to cart', 'add-to-cart', 'shopping cart', 'checkout',
            'product', 'price', 'sku', 'in stock', 'out of stock'
        ]
        ecommerce_score = sum(1 for sig in ecommerce_signals if sig.lower() in html.lower())
        
        if scores:
            best_type = max(scores, key=scores.get)
            best_score = scores[best_type]
            
            if best_score > 0.3:
                return best_type, min(best_score + ecommerce_score * 0.02, 1.0)
        
        # 如果没检测到特定平台，但是有电商特征
        if ecommerce_score > 3:
            return SiteType.CUSTOM_ECOMMERCE, 0.5 + ecommerce_score * 0.05
        
        return SiteType.UNKNOWN, 0.3
    
    def _detect_pagination(self, html: str) -> Tuple[PaginationType, Optional[str]]:
        """检测分页方式"""
        # 检查下一页按钮
        next_patterns = [
            r'<a[^>]*class="[^"]*next[^"]*"[^>]*>',
            r'<a[^>]*class="[^"]*next-page[^"]*"[^>]*>',
            r'<a[^>]*rel="next"[^>]*>',
            r'class="pagination[^"]*".*?下一页',
            r'class="pagination[^"]*".*?Next'
        ]
        
        for pattern in next_patterns:
            if re.search(pattern, html, re.IGNORECASE):
                return PaginationType.NEXT_BUTTON, '.next'
        
        # 检查页码导航
        page_patterns = [
            r'class="[^"]*pagination[^"]*"',
            r'class="[^"]*page-numbers[^"]*"',
            r'class="[^"]*pages[^"]*"'
        ]
        
        for pattern in page_patterns:
            if re.search(pattern, html, re.IGNORECASE):
                return PaginationType.PAGE_NUMBERS, '.pagination'
        
        # 检查加载更多
        load_more_patterns = [
            r'load more',
            r'load-more',
            r'infinite scroll',
            r'infinite-scroll'
        ]
        
        for pattern in load_more_patterns:
            if re.search(pattern, html, re.IGNORECASE):
                if 'infinite' in pattern:
                    return PaginationType.INFINITE_SCROLL, None
                return PaginationType.LOAD_MORE, '.load-more'
        
        return PaginationType.NONE, None
    
    def _detect_product_list(self, html: str, site_type: SiteType) -> Optional[str]:
        """检测产品列表选择器"""
        # WooCommerce 产品列表
        if site_type == SiteType.WOOCOMMERCE:
            if 'products' in html and 'ul' in html:
                return 'ul.products li.product'
        
        # Shopify 产品列表
        if site_type == SiteType.SHOPIFY:
            if 'grid-product' in html:
                return '.grid-product'
        
        # 通用产品列表检测
        common_selectors = [
            '.products .product',
            '.product-list .product-item',
            '.products-grid .product',
            '.shop-products .product-item',
            '.product-grid-item'
        ]
        
        for selector in common_selectors:
            # 简单检查类名是否存在
            class_name = selector.split('.')[-1]
            if class_name in html:
                return selector
        
        return None
    
    def _detect_product_url_pattern(self, url: str, site_type: SiteType) -> Optional[str]:
        """检测产品详情页URL模式"""
        if site_type == SiteType.WOOCOMMERCE:
            return '/product/'
        elif site_type == SiteType.SHOPIFY:
            return '/products/'
        elif site_type == SiteType.MAGENTO:
            return '/catalog/product/view/'
        
        # 从URL推断
        parsed = urlparse(url)
        path = parsed.path
        
        if '/product/' in path:
            return '/product/'
        elif '/products/' in path:
            return '/products/'
        elif '/item/' in path:
            return '/item/'
        
        return None
    
    def _detect_product_fields(self, html: str, site_type: SiteType) -> List[DetectedField]:
        """检测产品字段"""
        detected_fields = []
        
        for field_name, patterns in self._field_patterns.items():
            best_pattern = None
            best_confidence = 0
            
            for pattern in patterns:
                # 检查选择器是否在HTML中存在（简化检查）
                selector = pattern['selector']
                platform = pattern.get('platform', 'general')
                confidence = pattern.get('confidence', 0.5)
                
                # 如果是特定平台的模式，且网站类型匹配，提高置信度
                if platform != 'general' and site_type.value == platform:
                    confidence += 0.1
                
                # 简化检查：检查类名或标签是否存在
                class_match = re.search(r'\.([a-zA-Z0-9_-]+)', selector)
                if class_match:
                    class_name = class_match.group(1)
                    if class_name in html:
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_pattern = pattern
            
            if best_pattern and best_confidence > 0.5:
                field = DetectedField(
                    name=field_name,
                    selector=best_pattern['selector'],
                    attribute=best_pattern.get('attribute'),
                    multiple=best_pattern.get('multiple', False),
                    required=field_name in ['title', 'price'],
                    confidence=best_confidence,
                    needs_translation=field_name in self._translatable_fields,
                    description=f"自动检测的{field_name}字段"
                )
                detected_fields.append(field)
        
        # 按置信度排序
        detected_fields.sort(key=lambda f: f.confidence, reverse=True)
        
        return detected_fields
    
    def _detect_currency(self, html: str) -> Optional[str]:
        """检测货币类型"""
        # 检查常见货币符号
        for symbol, currency in self._currency_symbols.items():
            if symbol in html:
                # 检查是否在价格上下文中
                price_patterns = [
                    rf'{re.escape(symbol)}\s*\d',
                    rf'\d\s*{re.escape(symbol)}'
                ]
                for pattern in price_patterns:
                    if re.search(pattern, html):
                        return currency
        
        # 检查货币代码
        currency_codes = ['USD', 'EUR', 'GBP', 'CNY', 'JPY', 'CAD', 'AUD', 'HUF', 'RON']
        for code in currency_codes:
            if re.search(rf'\b{code}\b', html):
                return code
        
        return None
    
    def _detect_language(self, html: str) -> Optional[str]:
        """检测页面语言"""
        # 检查lang属性
        lang_match = re.search(r'<html[^>]*lang="([^"]+)"', html, re.IGNORECASE)
        if lang_match:
            return lang_match.group(1)
        
        # 检查meta标签
        meta_lang = re.search(r'<meta[^>]*http-equiv="content-language"[^>]*content="([^"]+)"', html, re.IGNORECASE)
        if meta_lang:
            return meta_lang.group(1)
        
        return None
    
    def _detect_anti_detection(self, html: str) -> bool:
        """检测反检测机制"""
        anti_detection_signals = [
            'cloudflare',
            'captcha',
            'recaptcha',
            'hcaptcha',
            'distil',
            'perimeterx',
            'akamai',
            'datadome',
            'bot detection',
            'access denied',
            'security check'
        ]
        
        for signal in anti_detection_signals:
            if signal.lower() in html.lower():
                return True
        
        return False
    
    def _generate_recommendations(self, result: SiteAnalysisResult) -> List[str]:
        """生成采集建议"""
        recommendations = []
        
        # 网站类型建议
        if result.site_type == SiteType.WOOCOMMERCE:
            recommendations.append("检测到WooCommerce网站，建议使用WooCommerce专用采集模板")
            recommendations.append("可以通过REST API获取更完整的数据")
        elif result.site_type == SiteType.SHOPIFY:
            recommendations.append("检测到Shopify网站，建议使用Shopify专用采集模板")
        elif result.site_type == SiteType.CUSTOM_ECOMMERCE:
            recommendations.append("检测到自定义电商网站，AI将自动识别字段")
        
        # 反检测建议
        if result.has_anti_detection:
            recommendations.append("检测到反检测机制，建议启用反检测模式和代理")
            recommendations.append("建议降低采集速度，增加随机延迟")
        
        # 分页建议
        if result.pagination_type == PaginationType.INFINITE_SCROLL:
            recommendations.append("检测到无限滚动，需要模拟滚动操作")
        elif result.pagination_type == PaginationType.LOAD_MORE:
            recommendations.append("检测到加载更多按钮，需要模拟点击")
        
        # 货币建议
        if result.currency:
            recommendations.append(f"检测到货币: {result.currency}，将自动进行汇率转换")
        
        # 语言建议
        if result.language:
            recommendations.append(f"检测到语言: {result.language}")
        
        # 字段建议
        translatable_count = sum(1 for f in result.detected_fields if f.needs_translation)
        if translatable_count > 0:
            recommendations.append(f"检测到{translatable_count}个需要翻译的字段")
        
        return recommendations
    
    def generate_scraping_config(self, analysis: SiteAnalysisResult, url: str) -> Dict:
        """
        基于分析结果生成采集配置
        """
        config = {
            'start_url': url,
            'site_type': analysis.site_type.value,
            'confidence': analysis.confidence,
            'pagination': {
                'type': analysis.pagination_type.value,
                'selector': analysis.pagination_selector
            },
            'product_list_selector': analysis.product_list_selector,
            'product_url_pattern': analysis.product_detail_url_pattern,
            'fields': [],
            'currency': analysis.currency,
            'language': analysis.language,
            'use_stealth': analysis.has_anti_detection,
            'use_proxy': analysis.has_anti_detection,
            'auto_translate': True,
            'translatable_fields': [f.name for f in analysis.detected_fields if f.needs_translation]
        }
        
        # 添加字段配置
        for field in analysis.detected_fields:
            field_config = {
                'name': field.name,
                'selector': field.selector,
                'attribute': field.attribute,
                'multiple': field.multiple,
                'required': field.required,
                'confidence': field.confidence,
                'needs_translation': field.needs_translation
            }
            config['fields'].append(field_config)
        
        return config
    
    def auto_map_fields(self, source_fields: List[str], target_fields: List[str]) -> Dict[str, str]:
        """
        AI自动字段映射
        """
        # 常见字段映射规则
        mapping_rules = {
            'title': ['name', 'product_name', 'product-title', '标题', '产品名称'],
            'price': ['regular_price', 'sale_price', 'product_price', '价格', '售价'],
            'description': ['content', 'body', '详细描述', '产品描述'],
            'short_description': ['excerpt', 'summary', '简介', '简短描述'],
            'sku': ['product_sku', 'item_code', '货号', '编号'],
            'stock': ['quantity', 'inventory', '库存', '数量'],
            'categories': ['category', 'product_category', '分类', '产品分类'],
            'tags': ['tag', 'product_tag', '标签'],
            'images': ['image', 'gallery', '图片', '图片集'],
            'attributes': ['attribute', 'specification', '属性', '规格'],
            'brand': ['manufacturer', '品牌', '厂商']
        }
        
        mapping = {}
        
        for target in target_fields:
            best_match = None
            best_score = 0
            
            target_lower = target.lower().replace('_', ' ').replace('-', ' ')
            
            for source in source_fields:
                source_lower = source.lower().replace('_', ' ').replace('-', ' ')
                
                # 直接匹配
                if source_lower == target_lower:
                    best_match = source
                    best_score = 1.0
                    break
                
                # 检查映射规则
                if target in mapping_rules:
                    for alias in mapping_rules[target]:
                        alias_lower = alias.lower().replace('_', ' ')
                        if alias_lower in source_lower or source_lower in alias_lower:
                            score = 0.7
                            if score > best_score:
                                best_score = score
                                best_match = source
                
                # 部分匹配
                if source_lower in target_lower or target_lower in source_lower:
                    score = 0.5
                    if score > best_score:
                        best_score = score
                        best_match = source
            
            if best_match and best_score > 0.4:
                mapping[target] = best_match
        
        return mapping


# 全局实例
ai_scraper_analyzer = AIScraperAnalyzer()
