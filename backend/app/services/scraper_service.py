"""
产品采集器服务 - 基于Playwright的可视化采集引擎
支持全量字段采集、反检测、代理池
高级功能：变体采集、增量采集、定时采集、整站采集
"""

from typing import List, Dict, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
import asyncio
import time
import random
import re
import hashlib
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

    # 高级功能开关
    scrape_variations: bool = True  # 是否采集变体
    incremental: bool = False  # 是否启用增量采集
    full_site: bool = False  # 是否启用整站采集
    respect_robots_txt: bool = True  # 是否遵守 robots.txt
    max_depth: int = 3  # 整站采集最大深度
    # 增量采集：基于内容 hash 跳过未变化页面
    incremental_hash_field: str = "raw_html"
    # 已采集内容的 hash 集合（外部传入，用于增量判断）
    known_hashes: Set[str] = field(default_factory=set)
    # 已采集 URL -> last_modified 的映射（用于增量判断）
    known_last_modified: Dict[str, str] = field(default_factory=dict)
    # Cron 表达式（用于定时采集）
    cron_expression: Optional[str] = None
    # 整站采集时排除的 URL 模式
    exclude_patterns: List[str] = field(default_factory=list)


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

        # 增量采集：基于 hash 判断是否需要跳过
        if self.config.incremental:
            content_hash = self._compute_content_hash(product)
            product.meta_data["content_hash"] = content_hash
            if content_hash in self.config.known_hashes:
                logger.info(f"Incremental scrape: skip unchanged {url}")
                product.meta_data["skipped_incremental"] = True
                return product
            # 标记为已采集，避免重复
            self.config.known_hashes.add(content_hash)

        # 变体采集：如果是可变产品，提取所有变体
        if self.config.scrape_variations:
            variations = await self._extract_variations()
            if variations:
                product.variations = variations
                product.is_variable = True
                logger.info(f"Extracted {len(variations)} variations for {url}")

        logger.info(f"Scraped product: {product.title or url}")
        
        return product

    def _compute_content_hash(self, product: ScrapedProduct) -> str:
        """计算产品内容的 hash，用于增量采集判断"""
        field_name = self.config.incremental_hash_field
        content = getattr(product, field_name, None) or product.raw_html or ""
        if not isinstance(content, str):
            content = str(content)
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    async def _extract_variations(self) -> List[Dict]:
        """提取可变产品的所有变体（颜色/尺寸/规格）

        支持 WooCommerce 默认的变体表结构，以及常见的自定义属性选择器。
        返回变体字典列表，每个字典包含 attributes 和 price 等字段。
        """
        variations: List[Dict] = []

        # 1. 尝试从内嵌的 JSON 数据中提取变体（WooCommerce variations_form）
        try:
            variations = await self._extract_variations_from_json()
            if variations:
                return variations
        except Exception as e:
            logger.debug(f"Failed to extract variations from JSON: {e}")

        # 2. 回退到 DOM 解析
        try:
            variations = await self._extract_variations_from_dom()
        except Exception as e:
            logger.debug(f"Failed to extract variations from DOM: {e}")

        return variations

    async def _extract_variations_from_json(self) -> List[Dict]:
        """从 WooCommerce 内嵌 JSON 提取变体"""
        try:
            script_content = await self.page.evaluate(
                """() => {
                    const scripts = document.querySelectorAll('script[type="application/json"]');
                    for (const s of scripts) {
                        const text = s.textContent || '';
                        if (text.includes('variations') || text.includes('product_variations')) {
                            return text;
                        }
                    }
                    return null;
                }"""
            )
            if not script_content:
                return []
            import json
            data = json.loads(script_content)
            if isinstance(data, list):
                return [
                    {
                        "variation_id": v.get("variation_id"),
                        "attributes": {
                            (a.get("attribute") or ""): a.get("value")
                            for a in v.get("attributes", [])
                        },
                        "price": v.get("display_price"),
                        "regular_price": v.get("display_regular_price"),
                        "sku": v.get("sku"),
                        "is_in_stock": v.get("is_in_stock", True),
                        "image": (v.get("image") or {}).get("src"),
                    }
                    for v in data
                ]
        except Exception as e:
            logger.debug(f"Variations JSON parse failed: {e}")
        return []

    async def _extract_variations_from_dom(self) -> List[Dict]:
        """从 DOM 提取变体属性和价格"""
        variations: List[Dict] = []
        # 提取属性
        attribute_selectors = [
            'table.variations select',
            '.variations select',
            'select[name^="attribute_"]',
        ]
        attributes: Dict[str, List[str]] = {}
        for sel in attribute_selectors:
            elements = await self.page.query_selector_all(sel)
            for element in elements:
                name = await element.get_attribute("name") or ""
                options = await element.query_selector_all("option")
                values = []
                for opt in options:
                    val = await opt.get_attribute("value")
                    if val and val != "":
                        values.append(val)
                if name and values:
                    attributes[name] = values

        if not attributes:
            return []

        # 简化：将属性组合作为单个变体记录
        variations.append({
            "attributes": attributes,
            "price": None,
            "source": "dom",
        })
        return variations
    
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

    async def scrape_full_site(self, progress_callback=None) -> List[ScrapedProduct]:
        """整站采集：从起始 URL 出发，自动发现产品链接并爬取整个网站

        通过 BFS 方式遍历网站，根据 product_link_selector 或常见产品 URL 模式识别产品页。
        受 max_depth、max_products、exclude_patterns 等配置限制。
        """
        if not self.config.full_site:
            # 如果未启用整站采集，回退到普通采集
            return await self.scrape(progress_callback=progress_callback)

        await self._init_browser()
        try:
            products: List[ScrapedProduct] = []
            visited: Set[str] = set()
            # 队列元素：(url, depth)
            queue: List[Tuple[str, int]] = [(self.config.start_url, 0)]
            base_domain = self._get_domain(self.config.start_url)

            while queue and len(products) < self.config.max_products:
                url, depth = queue.pop(0)
                if url in visited:
                    continue
                if depth > self.config.max_depth:
                    continue
                if self._is_excluded(url):
                    continue
                visited.add(url)

                logger.info(f"Full-site scrape (depth={depth}): {url}")
                success = await self._goto(url)
                if not success:
                    continue

                # 判断是否是产品页
                is_product = await self._is_product_page()
                if is_product:
                    product = await self.scrape_product_page(url)
                    if product:
                        products.append(product)
                        if progress_callback:
                            progress_callback(len(products), self.config.max_products)
                        if len(products) >= self.config.max_products:
                            break

                # 提取页面上的所有链接，继续 BFS
                if depth < self.config.max_depth:
                    links = await self._extract_page_links(base_domain)
                    for link in links:
                        if link not in visited:
                            queue.append((link, depth + 1))

            self.scraped_products = products
            logger.info(f"Full-site scraping complete: {len(products)} products")
            return products
        finally:
            await self._close_browser()

    def _get_domain(self, url: str) -> str:
        """获取 URL 的域名"""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return ""

    def _is_excluded(self, url: str) -> bool:
        """判断 URL 是否匹配排除模式"""
        for pattern in self.config.exclude_patterns:
            try:
                if re.search(pattern, url):
                    return True
            except re.error:
                if pattern in url:
                    return True
        return False

    async def _is_product_page(self) -> bool:
        """判断当前页面是否是产品详情页"""
        # 优先使用配置的产品选择器
        if self.config.product_selectors:
            for selector_cfg in self.config.product_selectors.values():
                try:
                    element = await self.page.query_selector(selector_cfg.selector)
                    if element:
                        return True
                except Exception:
                    continue
        # 回退到常见的产品页标识
        product_indicators = [
            'body.single-product',
            '.product',
            '.woocommerce-product-details',
            '[itemtype*="Product"]',
        ]
        for selector in product_indicators:
            try:
                element = await self.page.query_selector(selector)
                if element:
                    return True
            except Exception:
                continue
        return False

    async def _extract_page_links(self, base_domain: str) -> List[str]:
        """提取当前页面上同域的所有链接，用于整站采集"""
        links: List[str] = []
        try:
            anchors = await self.page.query_selector_all("a[href]")
            for anchor in anchors:
                href = await anchor.get_attribute("href")
                if not href:
                    continue
                # 跳过锚点、javascript、邮件等
                if href.startswith("#") or href.startswith("javascript:") or href.startswith("mailto:"):
                    continue
                full_url = urljoin(self.page.url, href)
                # 只保留同域链接
                if self._get_domain(full_url) != base_domain:
                    continue
                # 去除 fragment
                full_url = full_url.split("#")[0]
                if full_url and full_url not in links:
                    links.append(full_url)
        except Exception as e:
            logger.debug(f"Failed to extract page links: {e}")
        return links


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


# ==================== 定时采集调度 ====================

# 默认的 Celery beat 调度配置：将 cron_expression 映射到 Celery beat schedule
DEFAULT_SCHEDULED_SCRAPES: List[Dict[str, Any]] = [
    {
        "name": "daily-product-scrape",
        "task": "app.tasks.scraping_tasks.scrape_products_task",
        "cron": "0 2 * * *",  # 每天 02:00 执行
        "description": "每日定时采集产品",
    },
    {
        "name": "weekly-full-site-scrape",
        "task": "app.tasks.scraping_tasks.scrape_products_task",
        "cron": "0 3 * * 1",  # 每周一 03:00 执行
        "description": "每周整站采集",
    },
]


def build_celery_beat_schedule(scheduled_scrapes: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Dict[str, Any]]:
    """根据定时采集配置生成 Celery beat schedule 字典

    Args:
        scheduled_scrapes: 定时采集配置列表，每项包含 name/task/cron/args 等

    Returns:
        Celery beat schedule 字典，可直接传给 celery_app.conf.beat_schedule
    """
    from celery.schedules import crontab

    schedule: Dict[str, Dict[str, Any]] = {}
    scrapes = scheduled_scrapes or DEFAULT_SCHEDULED_SCRAPES
    for item in scrapes:
        name = item.get("name")
        task = item.get("task")
        cron_expr = item.get("cron") or item.get("cron_expression")
        if not name or not task or not cron_expr:
            continue
        try:
            parts = cron_expr.split()
            if len(parts) != 5:
                continue
            minute, hour, day_of_month, month_of_year, day_of_week = parts
            schedule[name] = {
                "task": task,
                "schedule": crontab(
                    minute=minute,
                    hour=hour,
                    day_of_month=day_of_month,
                    month_of_year=month_of_year,
                    day_of_week=day_of_week,
                ),
                "args": item.get("args", []),
                "kwargs": item.get("kwargs", {}),
            }
        except Exception as e:
            logger.warning(f"Failed to build schedule for {name}: {e}")
            continue
    return schedule


def parse_cron_expression(cron_expr: str) -> Optional[Dict[str, str]]:
    """解析 cron 表达式为各字段字典

    Args:
        cron_expr: 标准 5 字段 cron 表达式，如 "0 2 * * *"

    Returns:
        包含 minute/hour/day_of_month/month_of_year/day_of_week 的字典，解析失败返回 None
    """
    if not cron_expr:
        return None
    parts = cron_expr.split()
    if len(parts) != 5:
        return None
    return {
        "minute": parts[0],
        "hour": parts[1],
        "day_of_month": parts[2],
        "month_of_year": parts[3],
        "day_of_week": parts[4],
    }


def should_run_now(cron_expr: str, now=None) -> bool:
    """判断给定 cron 表达式是否在当前时间应该触发（简化版，用于测试和预检）

    Args:
        cron_expr: 标准 5 字段 cron 表达式
        now: 可选的当前时间 datetime，默认 utcnow()

    Returns:
        是否应该触发
    """
    from datetime import datetime
    parsed = parse_cron_expression(cron_expr)
    if not parsed:
        return False
    if now is None:
        now = datetime.utcnow()

    def _match(value: str, current: int, max_val: int) -> bool:
        if value == "*":
            return True
        # 处理逗号分隔
        if "," in value:
            for v in value.split(","):
                if _match(v, current, max_val):
                    return True
            return False
        # 处理步长
        if "/" in value:
            base, step = value.split("/")
            try:
                step_int = int(step)
                if base == "*":
                    return current % step_int == 0
                try:
                    base_int = int(base)
                    return current >= base_int and (current - base_int) % step_int == 0
                except ValueError:
                    return True
            except ValueError:
                return False
        try:
            return int(value) == current
        except ValueError:
            return True

    return (
        _match(parsed["minute"], now.minute, 59)
        and _match(parsed["hour"], now.hour, 23)
        and _match(parsed["day_of_month"], now.day, 31)
        and _match(parsed["month_of_year"], now.month, 12)
        and _match(parsed["day_of_week"], now.weekday(), 6)
    )
