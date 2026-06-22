"""
API路由 - 采集相关接口
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import asyncio
import uuid

from app.core.logging import get_logger
from app.services.scraper_service import (
    ProductScraper,
    ScrapingConfig,
    SelectorConfig,
    create_woocommerce_scraper
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/scraping", tags=["采集管理"])

# 内存中的任务状态
scraping_tasks: Dict[str, Dict] = {}


class SelectorConfigSchema(BaseModel):
    """选择器配置"""
    name: str
    selector: str
    attribute: Optional[str] = None
    multiple: bool = False
    required: bool = False
    default: Optional[Any] = None
    regex: Optional[str] = None


class ScrapingConfigSchema(BaseModel):
    """采集配置"""
    start_url: str
    max_pages: int = 10
    max_products: int = 100
    follow_pagination: bool = True
    product_link_selector: str = ""
    next_page_selector: str = ""
    product_selectors: Dict[str, SelectorConfigSchema] = Field(default_factory=dict)
    delay_between_requests: float = 2.0
    randomize_delay: bool = True
    use_stealth: bool = True
    use_proxy: bool = True
    proxy_country: Optional[str] = None
    download_images: bool = True
    headless: bool = True
    preset: Optional[str] = None  # woocommerce, shopify, etc.


class ScrapingTaskResponse(BaseModel):
    """采集任务响应"""
    task_id: str
    status: str
    start_url: str
    created_at: float


class ScrapingProgressResponse(BaseModel):
    """采集进度响应"""
    task_id: str
    status: str
    progress: float
    total: int
    completed: int
    products: List[Dict] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


@router.post("/tasks", response_model=ScrapingTaskResponse)
async def create_scraping_task(
    config: ScrapingConfigSchema,
    background_tasks: BackgroundTasks
):
    """创建采集任务"""
    task_id = str(uuid.uuid4())
    
    # 构建采集配置
    if config.preset == "woocommerce":
        # 使用预设的WooCommerce选择器
        from app.services.scraper_service import WOOCOMMERCE_SELECTORS
        product_selectors = WOOCOMMERCE_SELECTORS
    else:
        product_selectors = {}
        for name, sel in config.product_selectors.items():
            product_selectors[name] = SelectorConfig(
                name=sel.name,
                selector=sel.selector,
                attribute=sel.attribute,
                multiple=sel.multiple,
                required=sel.required,
                default=sel.default,
                regex=sel.regex
            )
    
    scraping_config = ScrapingConfig(
        start_url=config.start_url,
        max_pages=config.max_pages,
        max_products=config.max_products,
        follow_pagination=config.follow_pagination,
        product_link_selector=config.product_link_selector,
        next_page_selector=config.next_page_selector,
        product_selectors=product_selectors,
        delay_between_requests=config.delay_between_requests,
        randomize_delay=config.randomize_delay,
        use_stealth=config.use_stealth,
        use_proxy=config.use_proxy,
        proxy_country=config.proxy_country,
        download_images=config.download_images,
        headless=config.headless
    )
    
    # 初始化任务状态
    scraping_tasks[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "config": scraping_config,
        "progress": 0,
        "total": 0,
        "completed": 0,
        "products": [],
        "errors": [],
        "created_at": asyncio.get_event_loop().time()
    }
    
    # 后台执行采集
    background_tasks.add_task(run_scraping_task, task_id, scraping_config)
    
    return ScrapingTaskResponse(
        task_id=task_id,
        status="pending",
        start_url=config.start_url,
        created_at=scraping_tasks[task_id]["created_at"]
    )


async def run_scraping_task(task_id: str, config: ScrapingConfig):
    """执行采集任务"""
    try:
        scraping_tasks[task_id]["status"] = "running"
        
        scraper = ProductScraper(config)
        
        def progress_callback(current, total):
            scraping_tasks[task_id]["progress"] = current / total if total > 0 else 0
            scraping_tasks[task_id]["completed"] = current
            scraping_tasks[task_id]["total"] = total
        
        products = await scraper.scrape(progress_callback=progress_callback)
        
        # 转换为字典
        product_dicts = []
        for product in products:
            product_dict = {
                "url": product.url,
                "title": product.title,
                "description": product.description,
                "short_description": product.short_description,
                "sku": product.sku,
                "regular_price": product.regular_price,
                "sale_price": product.sale_price,
                "price": product.price,
                "currency": product.currency,
                "stock_quantity": product.stock_quantity,
                "in_stock": product.in_stock,
                "categories": product.categories,
                "tags": product.tags,
                "brand": product.brand,
                "images": product.images,
                "featured_image": product.featured_image,
                "attributes": product.attributes,
                "variations": product.variations,
                "is_variable": product.is_variable,
                "meta_data": product.meta_data,
                "scraped_at": product.scraped_at,
                "source_url": product.source_url
            }
            product_dicts.append(product_dict)
        
        scraping_tasks[task_id]["products"] = product_dicts
        scraping_tasks[task_id]["status"] = "completed"
        scraping_tasks[task_id]["progress"] = 1.0
        scraping_tasks[task_id]["completed"] = len(products)
        scraping_tasks[task_id]["total"] = len(products)
        
        logger.info(f"Scraping task {task_id} completed: {len(products)} products")
        
    except Exception as e:
        scraping_tasks[task_id]["status"] = "failed"
        scraping_tasks[task_id]["errors"].append(str(e))
        logger.error(f"Scraping task {task_id} failed: {e}")


@router.get("/tasks/{task_id}", response_model=ScrapingProgressResponse)
async def get_scraping_task(task_id: str):
    """获取采集任务状态"""
    if task_id not in scraping_tasks:
        raise HTTPException(status_code=404, detail="采集任务不存在")
    
    task = scraping_tasks[task_id]
    
    return ScrapingProgressResponse(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        total=task["total"],
        completed=task["completed"],
        products=task["products"][:10] if task["products"] else [],  # 只返回前10个
        errors=task["errors"]
    )


@router.get("/tasks/{task_id}/products")
async def get_scraping_products(
    task_id: str,
    page: int = 1,
    page_size: int = 20
):
    """获取采集到的产品列表"""
    if task_id not in scraping_tasks:
        raise HTTPException(status_code=404, detail="采集任务不存在")
    
    task = scraping_tasks[task_id]
    products = task["products"]
    
    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    paginated_products = products[start:end]
    
    return {
        "task_id": task_id,
        "total": len(products),
        "page": page,
        "page_size": page_size,
        "products": paginated_products
    }


@router.get("/selectors/presets")
async def get_selector_presets():
    """获取预设选择器"""
    from app.services.scraper_service import WOOCOMMERCE_SELECTORS
    
    presets = {
        "woocommerce": {
            "name": "WooCommerce",
            "description": "WooCommerce标准主题选择器",
            "product_link_selector": ".woocommerce-LoopProduct-link",
            "next_page_selector": ".next.page-numbers",
            "product_selectors": {
                name: {
                    "name": sel.name,
                    "selector": sel.selector,
                    "attribute": sel.attribute,
                    "multiple": sel.multiple,
                    "required": sel.required
                }
                for name, sel in WOOCOMMERCE_SELECTORS.items()
            }
        }
    }
    
    return presets


@router.post("/selectors/generate")
async def generate_selector(element_info: Dict):
    """生成CSS选择器"""
    from app.services.scraper_service import SelectorGenerator
    
    generator = SelectorGenerator()
    
    if "element_path" in element_info:
        selector = generator.generate_selector_hierarchy(element_info["element_path"])
    else:
        selector = generator.generate_selector_from_element(element_info)
    
    return {
        "selector": selector,
        "element_info": element_info
    }


@router.get("/proxy/stats")
async def get_proxy_stats():
    """获取代理池统计"""
    from app.services.proxy_service import proxy_pool
    
    stats = proxy_pool.get_stats()
    return stats


@router.post("/proxy/check")
async def check_proxies():
    """检测代理可用性"""
    from app.services.proxy_service import proxy_pool
    
    alive, dead = await proxy_pool.check_all_proxies()
    
    return {
        "alive": alive,
        "dead": dead,
        "total": alive + dead
    }
