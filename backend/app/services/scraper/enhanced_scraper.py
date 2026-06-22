"""
增强版产品采集器引擎
支持变体采集、增量采集、定时采集、与反检测体系深度集成
"""
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
import asyncio
import time
import random
import re
import json
from urllib.parse import urljoin, urlparse
from pathlib import Path
from bs4 import BeautifulSoup
from decimal import Decimal

from app.core.config import settings
from app.services.proxy.stealth_service import StealthService
from app.services.proxy.proxy_pool import ProxyManager
from app.services.scraper.scraper_config import (
    ScraperConfig,
    ScraperTask,
    FieldSelector,
    SelectorType,
    IncrementalConfig,
    ScheduleConfig,
)
from app.utils.string_utils import clean_text, extract_numbers
from app.utils.file_utils import ensure_directory


class EnhancedScraper:
    """
    增强版产品采集器
    支持变体采集、增量采集、定时采集、反检测深度集成
    """

    def __init__(self, config: ScraperConfig):
        self.config = config
        self.stealth_service = StealthService()
        self.proxy_manager = ProxyManager()
        self.browser = None
        self.context = None
        self.page = None
        self.task: Optional[ScraperTask] = None
        self.collected_urls: set = set()
        self.collected_products: List[Dict[str, Any]] = []

    async def initialize(self):
        """初始化浏览器和反检测"""
        from playwright.async_api import async_playwright

        # 设置反检测强度
        if self.config.use_stealth:
            self.stealth_service.set_intensity(self.config.stealth_intensity)

        # 启动Playwright
        self.playwright = await async_playwright().start()

        # 配置浏览器启动参数
        browser_args = {
            "headless": True,
            "args": [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
        }

        # 如果使用代理
        if self.config.use_proxy:
            proxy = self.proxy_manager.get_next_proxy()
            if proxy:
                browser_args["proxy"] = {
                    "server": f"{proxy.protocol}://{proxy.host}:{proxy.port}",
                    "username": proxy.username if proxy.username else None,
                    "password": proxy.password if proxy.password else None,
                }

        self.browser = await self.playwright.chromium.launch(**browser_args)

        # 创建带指纹的上下文
        fingerprint = self.stealth_service.generate_fingerprint()
        context_options = {
            "user_agent": fingerprint.navigator.user_agent,
            "viewport": {
                "width": fingerprint.screen.width,
                "height": fingerprint.screen.height,
            },
            "device_scale_factor": fingerprint.screen.device_pixel_ratio,
            "locale": fingerprint.navigator.language,
            "timezone_id": fingerprint.timezone.timezone,
        }

        self.context = await self.browser.new_context(**context_options)

        # 注入反检测脚本
        await self._inject_stealth_scripts()

        # 创建页面
        self.page = await self.context.new_page()

    async def _inject_stealth_scripts(self):
        """注入反检测脚本"""
        stealth_config = self.stealth_service.get_config()

        # 注入Canvas指纹
        if stealth_config.get("canvas_fingerprint", True):
            await self.context.add_init_script(
                self.stealth_service.get_canvas_stealth_script()
            )

        # 注入WebGL指纹
        if stealth_config.get("webgl_fingerprint", True):
            await self.context.add_init_script(
                self.stealth_service.get_webgl_stealth_script()
            )

        # 注入Navigator指纹
        if stealth_config.get("navigator_fingerprint", True):
            await self.context.add_init_script(
                self.stealth_service.get_navigator_stealth_script()
            )

        # 注入其他反检测脚本
        await self.context.add_init_script(
            self.stealth_service.get_all_stealth_scripts()
        )

    async def scrape_site(self, task: ScraperTask) -> ScraperTask:
        """
        执行完整的站点采集

        Args:
            task: 采集任务

        Returns:
            更新后的采集任务
        """
        self.task = task
        task.status = "running"
        task.start_time = time.time()

        try:
            await self.initialize()

            # 获取所有详情页URL
            detail_urls = await self._collect_detail_urls()
            task.total_items = len(detail_urls)

            # 逐个采集详情页
            for i, url in enumerate(detail_urls):
                try:
                    product = await self._scrape_product_page(url)
                    if product:
                        self.collected_products.append(product)
                        task.collected_data.append(product)
                        task.processed_items += 1
                    else:
                        task.failed_items += 1
                except Exception as e:
                    task.failed_items += 1
                    print(f"Error scraping {url}: {e}")

                # 请求间隔
                await self._random_delay()

            task.status = "completed"
        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
        finally:
            task.end_time = time.time()
            await self.close()

        return task

    async def _collect_detail_urls(self) -> List[str]:
        """
        从列表页收集所有详情页URL

        Returns:
            详情页URL列表
        """
        detail_urls = []
        list_config = self.config.list_page
        base_url = self.config.base_url

        # 生成所有列表页URL
        list_urls = self._generate_list_urls(base_url, list_config)

        for list_url in list_urls:
            try:
                await self._navigate_with_behavior(list_url)

                # 提取详情页链接
                links = await self.page.evaluate(
                    """(selector, attr) => {
                        const items = document.querySelectorAll(selector);
                        return Array.from(items).map(item => {
                            const link = item.querySelector('a');
                            return link ? link.getAttribute(attr) : null;
                        }).filter(Boolean);
                    }""",
                    list_config.item_link_selector,
                    list_config.item_link_attribute,
                )

                # 转换为绝对URL并去重
                for link in links:
                    absolute_url = urljoin(base_url, link)
                    if absolute_url not in self.collected_urls:
                        self.collected_urls.add(absolute_url)
                        detail_urls.append(absolute_url)

                # 检查是否还有下一页
                if not await self._has_next_page(list_config):
                    break

            except Exception as e:
                print(f"Error collecting URLs from {list_url}: {e}")
                continue

        return detail_urls

    def _generate_list_urls(self, base_url: str, list_config) -> List[str]:
        """生成所有列表页URL"""
        urls = []
        url_pattern = list_config.url_pattern

        if "{page}" in url_pattern:
            for page in range(1, list_config.max_pages + 1):
                url = url_pattern.format(page=page)
                urls.append(urljoin(base_url, url))
        else:
            urls.append(urljoin(base_url, url_pattern))

        return urls

    async def _has_next_page(self, list_config) -> bool:
        """检查是否有下一页"""
        if list_config.pagination_type.value == "none":
            return False

        try:
            has_next = await self.page.evaluate(
                """(selector) => {
                    const nextBtn = document.querySelector(selector);
                    return nextBtn && !nextBtn.disabled && !nextBtn.classList.contains('disabled');
                }""",
                list_config.pagination_selector,
            )
            return has_next
        except:
            return False

    async def _scrape_product_page(self, url: str) -> Optional[Dict[str, Any]]:
        """
        采集单个产品详情页

        Args:
            url: 产品详情页URL

        Returns:
            产品数据字典
        """
        try:
            await self._navigate_with_behavior(url)

            # 等待页面加载完成
            await self.page.wait_for_load_state("networkidle", timeout=self.config.timeout * 1000)

            # 提取所有字段
            product_data = {"url": url}

            for field_config in self.config.detail_page.fields:
                try:
                    value = await self._extract_field(field_config)
                    product_data[field_config.field_name] = value
                except Exception as e:
                    if field_config.required:
                        raise
                    product_data[field_config.field_name] = field_config.default_value

            # 采集变体
            if self.config.detail_page.variant_config and self.config.detail_page.variant_config.enabled:
                variants = await self._scrape_variants()
                product_data["variants"] = variants

            # 采集图片
            product_data["images"] = await self._scrape_images()

            return product_data

        except Exception as e:
            print(f"Error scraping product {url}: {e}")
            return None

    async def _extract_field(self, field_config: FieldSelector) -> Any:
        """
        提取单个字段

        Args:
            field_config: 字段配置

        Returns:
            提取的值
        """
        if field_config.selector_type == SelectorType.CSS:
            value = await self._extract_css(field_config)
        elif field_config.selector_type == SelectorType.XPATH:
            value = await self._extract_xpath(field_config)
        elif field_config.selector_type == SelectorType.TEXT:
            value = await self._extract_text(field_config)
        elif field_config.selector_type == SelectorType.REGEX:
            value = await self._extract_regex(field_config)
        else:
            value = None

        # 应用转换
        if value and field_config.transform:
            value = self._apply_transform(value, field_config.transform)

        return value

    async def _extract_css(self, field_config: FieldSelector) -> Any:
        """CSS选择器提取"""
        if field_config.multiple:
            values = await self.page.evaluate(
                """(selector, attr) => {
                    const elements = document.querySelectorAll(selector);
                    return Array.from(elements).map(el => {
                        return attr ? el.getAttribute(attr) : el.textContent.trim();
                    });
                }""",
                field_config.selector,
                field_config.attribute,
            )
            return values
        else:
            value = await self.page.evaluate(
                """(selector, attr) => {
                    const el = document.querySelector(selector);
                    if (!el) return null;
                    return attr ? el.getAttribute(attr) : el.textContent.trim();
                }""",
                field_config.selector,
                field_config.attribute,
            )
            return value

    async def _extract_xpath(self, field_config: FieldSelector) -> Any:
        """XPath提取"""
        # 使用JavaScript执行XPath
        value = await self.page.evaluate(
            """(xpath, multiple, attr) => {
                const result = document.evaluate(xpath, document, null, 
                    multiple ? XPathResult.ORDERED_NODE_SNAPSHOT_TYPE : XPathResult.FIRST_ORDERED_NODE_TYPE, null);

                if (multiple) {
                    const values = [];
                    for (let i = 0; i < result.snapshotLength; i++) {
                        const node = result.snapshotItem(i);
                        values.push(attr ? node.getAttribute(attr) : node.textContent.trim());
                    }
                    return values;
                } else {
                    const node = result.singleNodeValue;
                    if (!node) return null;
                    return attr ? node.getAttribute(attr) : node.textContent.trim();
                }
            }""",
            field_config.selector,
            field_config.multiple,
            field_config.attribute,
        )
        return value

    async def _extract_text(self, field_config: FieldSelector) -> Any:
        """文本内容提取"""
        # 查找包含特定文本的元素
        value = await self.page.evaluate(
            """(text, multiple) => {
                const xpath = `//*[contains(text(), '${text}')]`;
                const result = document.evaluate(xpath, document, null, 
                    multiple ? XPathResult.ORDERED_NODE_SNAPSHOT_TYPE : XPathResult.FIRST_ORDERED_NODE_TYPE, null);

                if (multiple) {
                    const values = [];
                    for (let i = 0; i < result.snapshotLength; i++) {
                        values.push(result.snapshotItem(i).textContent.trim());
                    }
                    return values;
                } else {
                    const node = result.singleNodeValue;
                    return node ? node.textContent.trim() : null;
                }
            }""",
            field_config.selector,
            field_config.multiple,
        )
        return value

    async def _extract_regex(self, field_config: FieldSelector) -> Any:
        """正则表达式提取"""
        # 获取页面HTML，然后用正则匹配
        html = await self.page.content()
        pattern = re.compile(field_config.regex or field_config.selector, re.IGNORECASE)

        if field_config.multiple:
            matches = pattern.findall(html)
            return matches
        else:
            match = pattern.search(html)
            return match.group(1) if match and match.groups() else match.group(0) if match else None

    def _apply_transform(self, value: Any, transform: str) -> Any:
        """应用转换函数"""
        transforms = {
            "strip": lambda v: v.strip() if isinstance(v, str) else v,
            "lower": lambda v: v.lower() if isinstance(v, str) else v,
            "upper": lambda v: v.upper() if isinstance(v, str) else v,
            "to_int": lambda v: int(v) if v else 0,
            "to_float": lambda v: float(v) if v else 0.0,
            "clean_text": lambda v: clean_text(v) if isinstance(v, str) else v,
            "extract_number": lambda v: extract_numbers(v) if isinstance(v, str) else v,
        }

        transform_func = transforms.get(transform)
        if transform_func:
            if isinstance(value, list):
                return [transform_func(v) for v in value]
            return transform_func(value)
        return value

    async def _scrape_variants(self) -> List[Dict[str, Any]]:
        """采集产品变体"""
        variant_config = self.config.detail_page.variant_config
        if not variant_config or not variant_config.enabled:
            return []

        variants = []

        try:
            # 检查变体类型
            if variant_config.variant_type == "attribute":
                variants = await self._scrape_attribute_variants(variant_config)
            elif variant_config.variant_type == "combined":
                variants = await self._scrape_combined_variants(variant_config)

        except Exception as e:
            print(f"Error scraping variants: {e}")

        return variants

    async def _scrape_attribute_variants(self, variant_config) -> List[Dict[str, Any]]:
        """采集属性变体（如颜色、尺寸等）"""
        variants = []

        # 获取所有属性选项
        attribute_data = {}
        for attr_selector in variant_config.attribute_selectors:
            values = await self._extract_field(attr_selector)
            attribute_data[attr_selector.field_name] = values if isinstance(values, list) else [values]

        # 生成所有组合
        if attribute_data:
            from itertools import product
            keys = list(attribute_data.keys())
            values_list = [attribute_data[k] for k in keys]

            for combo in product(*values_list):
                variant = {}
                for i, key in enumerate(keys):
                    variant[key] = combo[i]

                # 尝试获取变体价格、SKU等
                # 这里简化处理，实际需要点击每个变体组合获取数据
                variants.append(variant)

        return variants

    async def _scrape_combined_variants(self, variant_config) -> List[Dict[str, Any]]:
        """采集组合变体（如表格形式的变体）"""
        variants = []

        if variant_config.variant_selector:
            # 提取变体表格
            variant_rows = await self.page.evaluate(
                """(selector) => {
                    const rows = document.querySelectorAll(selector);
                    return Array.from(rows).map(row => {
                        const cells = row.querySelectorAll('td, th');
                        return Array.from(cells).map(cell => cell.textContent.trim());
                    });
                }""",
                variant_config.variant_selector,
            )

            # 解析变体数据
            if variant_rows and len(variant_rows) > 1:
                headers = variant_rows[0]
                for row in variant_rows[1:]:
                    variant = {}
                    for i, header in enumerate(headers):
                        if i < len(row):
                            variant[header] = row[i]
                    variants.append(variant)

        return variants

    async def _scrape_images(self) -> List[str]:
        """采集产品图片"""
        images = []

        try:
            # 查找产品图片
            image_urls = await self.page.evaluate(
                """() => {
                    const images = [];
                    
                    // 查找主图
                    const mainImage = document.querySelector('.wp-post-image, .product-image img, .woocommerce-main-image img');
                    if (mainImage && mainImage.src) {
                        images.push(mainImage.src);
                    }
                    
                    // 查找图库
                    const galleryImages = document.querySelectorAll('.woocommerce-product-gallery img, .product-gallery img, .thumbnails img');
                    galleryImages.forEach(img => {
                        if (img.src && !images.includes(img.src)) {
                            images.push(img.src);
                        }
                    });
                    
                    // 查找所有产品相关图片
                    const allImages = document.querySelectorAll('img[src*="product"], img[src*="wp-content/uploads"]');
                    allImages.forEach(img => {
                        if (img.src && !images.includes(img.src)) {
                            images.push(img.src);
                        }
                    });
                    
                    return images;
                }"""
            )

            images = image_urls

        except Exception as e:
            print(f"Error scraping images: {e}")

        return images

    async def _navigate_with_behavior(self, url: str):
        """
        带行为模拟的页面导航
        模拟真人浏览行为
        """
        # 随机延迟
        await self._random_delay(min_delay=0.5, max_delay=2.0)

        # 导航到页面
        await self.page.goto(url, wait_until="domcontentloaded", timeout=self.config.timeout * 1000)

        # 模拟滚动行为
        await self._simulate_scroll()

        # 随机悬停在元素上
        await self._simulate_hover()

    async def _simulate_scroll(self):
        """模拟滚动行为"""
        try:
            # 滚动到页面底部，然后回到顶部
            await self.page.evaluate(
                """async () => {
                    await new Promise(resolve => {
                        let totalHeight = 0;
                        const distance = 100;
                        const timer = setInterval(() => {
                            const scrollHeight = document.body.scrollHeight;
                            window.scrollBy(0, distance);
                            totalHeight += distance;

                            if (totalHeight >= scrollHeight) {
                                clearInterval(timer);
                                resolve();
                            }
                        }, 100);
                    });

                    // 回到顶部
                    await new Promise(resolve => {
                        let currentPosition = window.pageYOffset;
                        const timer = setInterval(() => {
                            if (currentPosition > 0) {
                                window.scrollBy(0, -50);
                                currentPosition -= 50;
                            } else {
                                clearInterval(timer);
                                resolve();
                            }
                        }, 50);
                    });
                }"""
            )
        except:
            pass

    async def _simulate_hover(self):
        """模拟悬停行为"""
        try:
            # 随机选择几个元素悬停
            elements = await self.page.query_selector_all("a, button, .product")
            if elements:
                # 随机选择1-3个元素悬停
                num_hovers = min(random.randint(1, 3), len(elements))
                selected = random.sample(elements, num_hovers)

                for element in selected:
                    try:
                        await element.hover()
                        await asyncio.sleep(random.uniform(0.3, 1.0))
                    except:
                        pass
        except:
            pass

    async def _random_delay(self, min_delay: float = None, max_delay: float = None):
        """随机延迟"""
        if min_delay is None:
            min_delay = self.config.delay_between_requests * 0.5
        if max_delay is None:
            max_delay = self.config.delay_between_requests * 1.5

        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)

    async def incremental_scrape(self, task: ScraperTask, incremental_config: IncrementalConfig) -> ScraperTask:
        """
        增量采集

        Args:
            task: 采集任务
            incremental_config: 增量配置

        Returns:
            更新后的采集任务
        """
        # 记录上次运行时间
        last_run = incremental_config.last_run_time
        incremental_config.last_run_time = time.time()

        # 执行完整采集
        task = await self.scrape_site(task)

        # 过滤新增/更新的产品
        if incremental_config.mode == "new_only":
            # 只保留新产品（这里简化处理，实际需要对比数据库）
            pass
        elif incremental_config.mode == "update_existing":
            # 更新已存在的产品
            pass

        return task

    async def close(self):
        """关闭浏览器"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright') and self.playwright:
                await self.playwright.stop()
        except Exception as e:
            print(f"Error closing browser: {e}")


class ScraperManager:
    """
    采集器管理器
    管理多个采集任务、任务队列、定时任务等
    """

    def __init__(self):
        self.tasks: Dict[str, ScraperTask] = {}
        self.active_tasks: set = set()
        self.max_concurrent = 5
        self.scheduled_tasks: Dict[str, ScheduleConfig] = {}

    def create_task(self, config: ScraperConfig) -> ScraperTask:
        """创建采集任务"""
        import uuid
        task_id = str(uuid.uuid4())
        task = ScraperTask(task_id=task_id, config=config)
        self.tasks[task_id] = task
        return task

    async def run_task(self, task_id: str) -> Optional[ScraperTask]:
        """运行采集任务"""
        task = self.tasks.get(task_id)
        if not task:
            return None

        if len(self.active_tasks) >= self.max_concurrent:
            task.status = "queued"
            return task

        self.active_tasks.add(task_id)

        try:
            scraper = EnhancedScraper(task.config)
            task = await scraper.scrape_site(task)
        finally:
            self.active_tasks.discard(task_id)

        return task

    def get_task(self, task_id: str) -> Optional[ScraperTask]:
        """获取任务状态"""
        return self.tasks.get(task_id)

    def list_tasks(self, status: str = None) -> List[ScraperTask]:
        """列出任务"""
        tasks = list(self.tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return tasks

    def pause_task(self, task_id: str) -> bool:
        """暂停任务"""
        task = self.tasks.get(task_id)
        if task and task.status == "running":
            task.status = "paused"
            return True
        return False

    def resume_task(self, task_id: str) -> bool:
        """恢复任务"""
        task = self.tasks.get(task_id)
        if task and task.status == "paused":
            task.status = "running"
            return True
        return False

    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        task = self.tasks.get(task_id)
        if task and task.status in ["running", "paused", "queued"]:
            task.status = "cancelled"
            self.active_tasks.discard(task_id)
            return True
        return False

    def add_scheduled_task(self, task_id: str, schedule_config: ScheduleConfig):
        """添加定时任务"""
        self.scheduled_tasks[task_id] = schedule_config

    def remove_scheduled_task(self, task_id: str):
        """移除定时任务"""
        self.scheduled_tasks.pop(task_id, None)

    def get_scheduled_tasks(self) -> Dict[str, ScheduleConfig]:
        """获取所有定时任务"""
        return self.scheduled_tasks.copy()


# 单例实例
_scraper_manager = None


def get_scraper_manager() -> ScraperManager:
    """获取采集器管理器单例"""
    global _scraper_manager
    if _scraper_manager is None:
        _scraper_manager = ScraperManager()
    return _scraper_manager
