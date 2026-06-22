"""
产品采集器服务 - 基于Playwright的可视化采集引擎
支持全量字段采集、反检测、代理池
"""

from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
import asyncio
import time
import random
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from decimal import Decimal

from app.core.config import settings
from app.core.logging import get_logger
from app.services.proxy_service import proxy_pool, Proxy, ProxyProtocol, ProxyQuality
from app.services.stealth_service import (
    stealth_manager,
    fingerprint_generator,
    behavior_simulator,
    BrowserFingerprint
)

logger = get_logger(__name__)


@dataclass
class SelectorConfig:
    """选择器配置"""
    name: str  # 字段名称
    selector: str  # CSS选择器
    attribute: Optional[str] = None  # 获取属性值，None表示获取文本
    multiple: bool = False  # 是否获取多个值
    required: bool = False  # 是否必填
    default: Optional[Any] = None  # 默认值
    regex: Optional[str] = None  # 正则提取
    transform: Optional[str] = None  # 转换函数名


@dataclass
class ScrapingConfig:
    """采集配置"""
    # 基础配置
    start_url: str
    max_pages: int = 10
    max_products: int = 100
    follow_pagination: bool = True
    
    # 列表页选择器
    product_link_selector: str = ""
    next_page_selector: str = ""
    
    # 详情页选择器
    product_selectors: Dict[str, SelectorConfig] = field(default_factory=dict)
    
    # 采集速度控制
    delay_between_requests: float = 2.0
    randomize_delay: bool = True
    
    # 反检测
    use_stealth: bool = True
    use_proxy: bool = True
    proxy_country: Optional[str] = None
    proxy_quality: Optional[ProxyQuality] = None
    
    # 重试配置
    max_retries: int = 3
    retry_delay: float = 5.0
    
    # 图片采集
    download_images: bool = True
    image_quality: str = "original"  # original, high, medium, low
    
    # 其他
    timeout: int = 30000
    headless: bool = True


@dataclass
class ScrapedProduct:
    """采集到的产品数据"""
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    sku: Optional[str] = None
    
    # 价格
    regular_price: Optional[float] = None
    sale_price: Optional[float] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    
    # 库存
    stock_quantity: Optional[int] = None
    in_stock: bool = True
    
    # 分类和标签
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    brand: Optional[str] = None
    
    # 图片
    images: List[str] = field(default_factory=list)
    featured_image: Optional[str] = None
    
    # 属性和变体
    attributes: List[Dict] = field(default_factory=list)
    variations: List[Dict] = field(default_factory=list)
    is_variable: bool = False
    
    # 元数据
    meta_data: Dict[str, Any] = field(default_factory=dict)
    raw_html: Optional[str] = None
    
    # 采集信息
    scraped_at: float = field(default_factory=time.time)
    source_url: Optional[str] = None


class ProductScraper:
    """产品采集器"""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.browser = None
        self.context = None
        self.page = None
        self.current_proxy: Optional[Proxy] = None
        self.fingerprint: Optional[BrowserFingerprint] = None
        self.scraped_urls: set = set()
        self.scraped_products: List[ScrapedProduct] = []
    
    async def _init_browser(self):
        """初始化浏览器"""
        from playwright.async_api import async_playwright
        
        self.playwright = await async_playwright().start()
        
        # 获取代理
        proxy_url = None
        if self.config.use_proxy:
            self.current_proxy = proxy_pool.get_proxy(
                country=self.config.proxy_country,
                min_quality=self.config.proxy_quality,
                strategy="best_score"
            )
            if self.current_proxy:
                proxy_url = self.current_proxy.url
                logger.info(f"Using proxy: {self.current_proxy.host}:{self.current_proxy.port}")
        
        # 生成指纹
        if self.config.use_stealth:
            country = self.config.proxy_country
            if self.current_proxy:
                country = self.current_proxy.country
            self.fingerprint = fingerprint_generator.generate_fingerprint(country=country)
        
        # 启动浏览器
        self.browser = await self.playwright.chromium.launch(
            headless=self.config.headless,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-gpu',
            ]
        )
        
        # 创建上下文
        if self.config.use_stealth and self.fingerprint:
            self.context = stealth_manager.create_browser_context(
                self.browser,
                self.fingerprint,
                proxy_url=proxy_url
            )
        else:
            context_options = {}
            if proxy_url:
                context_options["proxy"] = {"server": proxy_url}
            self.context = await self.browser.new_context(**context_options)
        
        # 创建页面
        self.page = await self.context.new_page()
        
        # 设置超时
        self.page.set_default_timeout(self.config.timeout)
        
        logger.info("Browser initialized")
    
    async def _close_browser(self):
        """关闭浏览器"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        
        logger.info("Browser closed")
    
    async def _goto(self, url: str, retries: int = 0) -> bool:
        """访问页面，带重试"""
        try:
            # 随机延迟
            if self.config.randomize_delay:
                delay = random.uniform(
                    self.config.delay_between_requests * 0.5,
                    self.config.delay_between_requests * 1.5
                )
            else:
                delay = self.config.delay_between_requests
            
            await asyncio.sleep(delay)
            
            # 访问页面
            response = await self.page.goto(url, wait_until="domcontentloaded")
            
            # 等待页面加载完成
            await self.page.wait_for_load_state("networkidle", timeout=10000)
            
            # 模拟人类行为
            if self.config.use_stealth:
                behavior_simulator.human_like_scroll(self.page, steps=5)
            
            # 标记代理成功
            if self.current_proxy:
                proxy_pool.mark_success(self.current_proxy, 0)
            
            return response and response.status == 200
            
        except Exception as e:
            logger.warning(f"Failed to load {url}: {e}")
            
            # 标记代理失败
            if self.current_proxy:
                proxy_pool.mark_failed(self.current_proxy)
            
            # 重试
            if retries < self.config.max_retries:
                logger.info(f"Retrying ({retries + 1}/{self.config.max_retries})...")
                await asyncio.sleep(self.config.retry_delay)
                return await self._goto(url, retries + 1)
            
            return False
    
    async def _extract_text(self, selector: str, attribute: Optional[str] = None, regex: Optional[str] = None) -> Optional[str]:
        """提取文本内容"""
        try:
            element = await self.page.query_selector(selector)
            if not element:
                return None
            
            if attribute:
                value = await element.get_attribute(attribute)
            else:
                value = await element.inner_text()
            
            if value and regex:
                match = re.search(regex, value)
                if match:
                    value = match.group(1) if match.groups() else match.group(0)
            
            return value.strip() if value else None
            
        except Exception as e:
            logger.debug(f"Failed to extract with selector {selector}: {e}")
            return None
    
    async def _extract_all(self, selector: str, attribute: Optional[str] = None) -> List[str]:
        """提取多个元素"""
        try:
            elements = await self.page.query_selector_all(selector)
            results = []
            
            for element in elements:
                if attribute:
                    value = await element.get_attribute(attribute)
                else:
                    value = await element.inner_text()
                
                if value:
                    results.append(value.strip())
            
            return results
            
        except Exception as e:
            logger.debug(f"Failed to extract all with selector {selector}: {e}")
            return []
    
    def _parse_price(self, price_str: Optional[str]) -> Tuple[Optional[float], Optional[str]]:
        """解析价格字符串"""
        if not price_str:
            return None, None
        
        # 提取货币符号
        currency = None
        currency_symbols = {
            '$': 'USD',
            '€': 'EUR',
            '£': 'GBP',
            '¥': 'JPY',
            '₹': 'INR',
            '₩': 'KRW',
            '₽': 'RUB',
            '₺': 'TRY',
            '₴': 'UAH',
            '₦': 'NGN',
            '₱': 'PHP',
            'RM': 'MYR',
            'S$': 'SGD',
            'HK$': 'HKD',
            'NT$': 'TWD',
            'kr': 'SEK',
            'zł': 'PLN',
            'Kč': 'CZK',
            'Ft': 'HUF',
            'lei': 'RON',
            '₸': 'KZT',
        }
        
        for symbol, code in currency_symbols.items():
            if symbol in price_str:
                currency = code
                break
        
        # 提取数字
        # 移除货币符号和空格
        clean_price = re.sub(r'[^\d.,]', '', price_str)
        
        if not clean_price:
            return None, currency
        
        # 处理千分位和小数点
        # 如果同时有逗号和点
        if ',' in clean_price and '.' in clean_price:
            # 判断哪个是小数点
            if clean_price.rfind(',') > clean_price.rfind('.'):
                # 逗号在最后，是小数点（欧洲格式）
                clean_price = clean_price.replace('.', '').replace(',', '.')
            else:
                # 点在最后，是小数点
                clean_price = clean_price.replace(',', '')
        elif ',' in clean_price:
            # 只有逗号，可能是千分位或小数点
            # 如果逗号后面有3位数字，可能是千分位
            parts = clean_price.split(',')
            if len(parts[-1]) == 3 and len(parts) > 1:
                clean_price = clean_price.replace(',', '')
            else:
                clean_price = clean_price.replace(',', '.')
        
        try:
            price = float(clean_price)
            return price, currency
        except ValueError:
            return None, currency
    
    async def scrape_product_page(self, url: str) -> Optional[ScrapedProduct]:
        """采集产品详情页"""
        if url in self.scraped_urls:
            return None
        
        success = await self._goto(url)
        if not success:
            return None
        
        self.scraped_urls.add(url)
        
        product = ScrapedProduct(url=url, source_url=url)
        
        # 使用配置的选择器提取数据
        for field_name, selector_config in self.config.product_selectors.items():
            if selector_config.multiple:
                values = await self._extract_all(
                    selector_config.selector,
                    selector_config.attribute
                )
                setattr(product, field_name, values)
            else:
                value = await self._extract_text(
                    selector_config.selector,
                    selector_config.attribute,
                    selector_config.regex
                )
                if value is not None:
                    setattr(product, field_name, value)
                elif selector_config.default is not None:
                    setattr(product, field_name, selector_config.default)
        
        # 解析价格
        if hasattr(product, 'price') and product.price:
            if isinstance(product.price, str):
                price, currency = self._parse_price(product.price)
                product.price = price
                product.currency = currency
        
        if hasattr(product, 'regular_price') and product.regular_price:
            if isinstance(product.regular_price, str):
                price, _ = self._parse_price(product.regular_price)
                product.regular_price = price
        
        if hasattr(product, 'sale_price') and product.sale_price:
            if isinstance(product.sale_price, str):
                price, _ = self._parse_price(product.sale_price)
                product.sale_price = price
        
        # 提取图片
        if self.config.download_images:
            images = await self._extract_images()
            product.images = images
            if images:
                product.featured_image = images[0]
        
        # 获取原始HTML
        product.raw_html = await self.page.content()
        
        logger.info(f"Scraped product: {product.title or url}")
        
        return product
    
    async def _extract_images(self) -> List[str]:
        """提取产品图片"""
        images = []
        
        # 尝试多种选择器
        selectors = [
            'img.wp-post-image',
            'img.attachment-woocommerce_single',
            'img.product-image',
            '.woocommerce-product-gallery__image img',
            '.product-gallery img',
            '.images img',
            'div[class*="gallery"] img',
            'img[itemprop="image"]',
        ]
        
        for selector in selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                for element in elements:
                    src = await element.get_attribute('src')
                    if src and src not in images:
                        # 尝试获取高清图
                        srcset = await element.get_attribute('srcset')
                        if srcset:
                            # 解析srcset，取最大的图
                            urls = self._parse_srcset(srcset)
                            if urls:
                                src = urls[-1]
                        
                        # 转换为绝对URL
                        src = urljoin(self.page.url, src)
                        images.append(src)
            except Exception:
                continue
        
        # 去重
        images = list(dict.fromkeys(images))
        
        return images
    
    def _parse_srcset(self, srcset: str) -> List[str]:
        """解析srcset属性"""
        urls = []
        parts = srcset.split(',')
        
        for part in parts:
            part = part.strip()
            if ' ' in part:
                url = part.split(' ')[0]
            else:
                url = part
            
            if url:
                urls.append(url.strip())
        
        return urls
    
    async def scrape_list_page(self, url: str) -> Tuple[List[str], Optional[str]]:
        """采集列表页，返回产品链接和下一页链接"""
        success = await self._goto(url)
        if not success:
            return [], None
        
        # 提取产品链接
        product_links = []
        if self.config.product_link_selector:
            elements = await self.page.query_selector_all(self.config.product_link_selector)
            for element in elements:
                href = await element.get_attribute('href')
                if href:
                    full_url = urljoin(url, href)
                    if full_url not in self.scraped_urls:
                        product_links.append(full_url)
        
        # 提取下一页链接
        next_page_url = None
        if self.config.follow_pagination and self.config.next_page_selector:
            next_element = await self.page.query_selector(self.config.next_page_selector)
            if next_element:
                href = await next_element.get_attribute('href')
                if href:
                    next_page_url = urljoin(url, href)
        
        return product_links, next_page_url
    
    async def scrape(self, progress_callback=None) -> List[ScrapedProduct]:
        """执行采集任务"""
        await self._init_browser()
        
        try:
            products = []
            current_url = self.config.start_url
            page_count = 0
            
            while current_url and page_count < self.config.max_pages and len(products) < self.config.max_products:
                page_count += 1
                logger.info(f"Scraping page {page_count}: {current_url}")
                
                # 采集列表页
                product_links, next_page_url = await self.scrape_list_page(current_url)
                
                # 采集每个产品详情页
                for product_url in product_links:
                    if len(products) >= self.config.max_products:
                        break
                    
                    if product_url in self.scraped_urls:
                        continue
                    
                    product = await self.scrape_product_page(product_url)
                    if product:
                        products.append(product)
                        
                        # 更新进度
                        if progress_callback:
                            progress_callback(len(products), self.config.max_products)
                
                # 下一页
                if next_page_url and self.config.follow_pagination:
                    current_url = next_page_url
                else:
                    break
            
            self.scraped_products = products
            logger.info(f"Scraping complete: {len(products)} products from {page_count} pages")
            
            return products
            
        finally:
            await self._close_browser()


class SelectorGenerator:
    """选择器生成器 - 用于可视化点选生成选择器"""
    
    def __init__(self):
        pass
    
    def generate_selector_from_element(self, element_info: Dict) -> str:
        """根据元素信息生成CSS选择器
        
        Args:
            element_info: 元素信息，包含tag, id, class, attributes, nth-child等
        """
        parts = []
        
        # 标签名
        tag = element_info.get('tag', '').lower()
        if tag:
            parts.append(tag)
        
        # ID
        element_id = element_info.get('id')
        if element_id:
            parts.append(f'#{element_id}')
            return ''.join(parts)  # ID选择器最精确，直接返回
        
        # Class
        classes = element_info.get('classes', [])
        if classes:
            # 选择最有辨识度的class
            for cls in classes[:3]:  # 最多用3个class
                if not cls.startswith('hover') and not cls.startswith('active'):
                    parts.append(f'.{cls}')
        
        # 属性
        attributes = element_info.get('attributes', {})
        important_attrs = ['data-product-id', 'data-sku', 'itemprop', 'rel']
        for attr in important_attrs:
            if attr in attributes:
                parts.append(f'[{attr}="{attributes[attr]}"]')
        
        # nth-child
        nth_child = element_info.get('nth_child')
        if nth_child and len(parts) < 3:
            parts.append(f':nth-child({nth_child})')
        
        return ''.join(parts)
    
    def generate_selector_hierarchy(self, element_path: List[Dict]) -> str:
        """根据元素路径生成层级选择器"""
        selectors = []
        
        for element in element_path:
            selector = self.generate_selector_from_element(element)
            selectors.append(selector)
        
        # 从后往前组合，找到最短且唯一的选择器
        for i in range(len(selectors) - 1, -1, -1):
            candidate = ' > '.join(selectors[i:])
            if len(candidate) > 3:  # 至少要有一定复杂度
                return candidate
        
        return selectors[-1] if selectors else ''


# 预设的WooCommerce选择器配置
WOOCOMMERCE_SELECTORS = {
    'title': SelectorConfig(
        name='title',
        selector='.product_title',
        required=True
    ),
    'price': SelectorConfig(
        name='price',
        selector='.price .woocommerce-Price-amount',
    ),
    'regular_price': SelectorConfig(
        name='regular_price',
        selector='.price del .woocommerce-Price-amount',
    ),
    'sale_price': SelectorConfig(
        name='sale_price',
        selector='.price ins .woocommerce-Price-amount',
    ),
    'short_description': SelectorConfig(
        name='short_description',
        selector='.woocommerce-product-details__short-description',
    ),
    'description': SelectorConfig(
        name='description',
        selector='#tab-description',
    ),
    'sku': SelectorConfig(
        name='sku',
        selector='.sku',
    ),
    'categories': SelectorConfig(
        name='categories',
        selector='.posted_in a',
        multiple=True
    ),
    'tags': SelectorConfig(
        name='tags',
        selector='.tagged_as a',
        multiple=True
    ),
    'brand': SelectorConfig(
        name='brand',
        selector='.pwb-brand a',
    ),
}


def create_woocommerce_scraper(start_url: str, **kwargs) -> ProductScraper:
    """创建WooCommerce采集器"""
    config = ScrapingConfig(
        start_url=start_url,
        product_link_selector='.woocommerce-LoopProduct-link',
        next_page_selector='.next.page-numbers',
        product_selectors=WOOCOMMERCE_SELECTORS,
        **kwargs
    )
    return ProductScraper(config)
