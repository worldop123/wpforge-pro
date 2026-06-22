"""
采集配置模型 - 可视化点选选择器配置
支持列表页+详情页配置、可视化字段映射
"""
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json


class SelectorType(str, Enum):
    """选择器类型"""
    CSS = "css"
    XPATH = "xpath"
    TEXT = "text"
    REGEX = "regex"


class FieldType(str, Enum):
    """字段类型"""
    TITLE = "title"
    DESCRIPTION = "description"
    PRICE = "price"
    SALE_PRICE = "sale_price"
    IMAGE = "image"
    GALLERY = "gallery"
    CATEGORY = "category"
    TAG = "tag"
    SKU = "sku"
    STOCK = "stock"
    VARIANT = "variant"
    SPECIFICATION = "specification"
    FAQ = "faq"
    REVIEW = "review"
    CUSTOM = "custom"


class PaginationType(str, Enum):
    """分页类型"""
    NONE = "none"
    PAGE_NUMBERS = "page_numbers"
    LOAD_MORE = "load_more"
    INFINITE_SCROLL = "infinite_scroll"
    NEXT_BUTTON = "next_button"


@dataclass
class FieldSelector:
    """字段选择器配置"""
    field_name: str
    field_type: FieldType
    selector: str
    selector_type: SelectorType = SelectorType.CSS
    attribute: Optional[str] = None  # 提取属性，如href、src
    regex: Optional[str] = None  # 正则提取
    multiple: bool = False  # 是否提取多个值
    required: bool = False
    default_value: Optional[Any] = None
    transform: Optional[str] = None  # 转换函数：strip、lower、upper、to_int、to_float等

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field_name": self.field_name,
            "field_type": self.field_type.value,
            "selector": self.selector,
            "selector_type": self.selector_type.value,
            "attribute": self.attribute,
            "regex": self.regex,
            "multiple": self.multiple,
            "required": self.required,
            "default_value": self.default_value,
            "transform": self.transform,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FieldSelector':
        return cls(
            field_name=data["field_name"],
            field_type=FieldType(data["field_type"]),
            selector=data["selector"],
            selector_type=SelectorType(data.get("selector_type", "css")),
            attribute=data.get("attribute"),
            regex=data.get("regex"),
            multiple=data.get("multiple", False),
            required=data.get("required", False),
            default_value=data.get("default_value"),
            transform=data.get("transform"),
        )


@dataclass
class ListPageConfig:
    """列表页配置"""
    url_pattern: str  # 列表页URL模式
    item_selector: str  # 列表项选择器
    item_link_selector: str  # 详情页链接选择器
    item_link_attribute: str = "href"
    pagination_type: PaginationType = PaginationType.NONE
    pagination_selector: Optional[str] = None  # 分页选择器
    max_pages: int = 10
    items_per_page: int = 24

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url_pattern": self.url_pattern,
            "item_selector": self.item_selector,
            "item_link_selector": self.item_link_selector,
            "item_link_attribute": self.item_link_attribute,
            "pagination_type": self.pagination_type.value,
            "pagination_selector": self.pagination_selector,
            "max_pages": self.max_pages,
            "items_per_page": self.items_per_page,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ListPageConfig':
        return cls(
            url_pattern=data["url_pattern"],
            item_selector=data["item_selector"],
            item_link_selector=data["item_link_selector"],
            item_link_attribute=data.get("item_link_attribute", "href"),
            pagination_type=PaginationType(data.get("pagination_type", "none")),
            pagination_selector=data.get("pagination_selector"),
            max_pages=data.get("max_pages", 10),
            items_per_page=data.get("items_per_page", 24),
        )


@dataclass
class DetailPageConfig:
    """详情页配置"""
    url_pattern: str  # 详情页URL模式
    fields: List[FieldSelector] = field(default_factory=list)
    variant_config: Optional['VariantConfig'] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url_pattern": self.url_pattern,
            "fields": [f.to_dict() for f in self.fields],
            "variant_config": self.variant_config.to_dict() if self.variant_config else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DetailPageConfig':
        fields = [FieldSelector.from_dict(f) for f in data.get("fields", [])]
        variant_config = VariantConfig.from_dict(data["variant_config"]) if data.get("variant_config") else None
        return cls(
            url_pattern=data["url_pattern"],
            fields=fields,
            variant_config=variant_config,
        )


@dataclass
class VariantConfig:
    """变体配置"""
    enabled: bool = False
    variant_type: str = "attribute"  # attribute / combined
    variant_selector: Optional[str] = None  # 变体容器选择器
    attribute_selectors: List[FieldSelector] = field(default_factory=list)
    price_selector: Optional[str] = None
    sku_selector: Optional[str] = None
    stock_selector: Optional[str] = None
    image_selector: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "variant_type": self.variant_type,
            "variant_selector": self.variant_selector,
            "attribute_selectors": [s.to_dict() for s in self.attribute_selectors],
            "price_selector": self.price_selector,
            "sku_selector": self.sku_selector,
            "stock_selector": self.stock_selector,
            "image_selector": self.image_selector,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VariantConfig':
        attribute_selectors = [FieldSelector.from_dict(s) for s in data.get("attribute_selectors", [])]
        return cls(
            enabled=data.get("enabled", False),
            variant_type=data.get("variant_type", "attribute"),
            variant_selector=data.get("variant_selector"),
            attribute_selectors=attribute_selectors,
            price_selector=data.get("price_selector"),
            sku_selector=data.get("sku_selector"),
            stock_selector=data.get("stock_selector"),
            image_selector=data.get("image_selector"),
        )


@dataclass
class ScraperConfig:
    """采集器完整配置"""
    name: str
    base_url: str
    site_type: str = "woocommerce"  # woocommerce / shopify / magento / custom
    list_page: ListPageConfig
    detail_page: DetailPageConfig
    language: str = "en"
    currency: str = "USD"
    auto_detect: bool = True  # 是否自动检测配置
    use_proxy: bool = True
    use_stealth: bool = True
    stealth_intensity: str = "medium"  # low / medium / high / extreme
    delay_between_requests: float = 2.0  # 请求间隔（秒）
    max_concurrent: int = 5
    timeout: int = 30
    retry_count: int = 3
    retry_delay: float = 5.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "base_url": self.base_url,
            "site_type": self.site_type,
            "list_page": self.list_page.to_dict(),
            "detail_page": self.detail_page.to_dict(),
            "language": self.language,
            "currency": self.currency,
            "auto_detect": self.auto_detect,
            "use_proxy": self.use_proxy,
            "use_stealth": self.use_stealth,
            "stealth_intensity": self.stealth_intensity,
            "delay_between_requests": self.delay_between_requests,
            "max_concurrent": self.max_concurrent,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "retry_delay": self.retry_delay,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScraperConfig':
        return cls(
            name=data["name"],
            base_url=data["base_url"],
            site_type=data.get("site_type", "woocommerce"),
            list_page=ListPageConfig.from_dict(data["list_page"]),
            detail_page=DetailPageConfig.from_dict(data["detail_page"]),
            language=data.get("language", "en"),
            currency=data.get("currency", "USD"),
            auto_detect=data.get("auto_detect", True),
            use_proxy=data.get("use_proxy", True),
            use_stealth=data.get("use_stealth", True),
            stealth_intensity=data.get("stealth_intensity", "medium"),
            delay_between_requests=data.get("delay_between_requests", 2.0),
            max_concurrent=data.get("max_concurrent", 5),
            timeout=data.get("timeout", 30),
            retry_count=data.get("retry_count", 3),
            retry_delay=data.get("retry_delay", 5.0),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> 'ScraperConfig':
        return cls.from_dict(json.loads(json_str))


@dataclass
class ScraperTask:
    """采集任务"""
    task_id: str
    config: ScraperConfig
    status: str = "pending"  # pending / running / completed / failed / paused
    total_items: int = 0
    processed_items: int = 0
    failed_items: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error_message: Optional[str] = None
    collected_data: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "config": self.config.to_dict(),
            "status": self.status,
            "total_items": self.total_items,
            "processed_items": self.processed_items,
            "failed_items": self.failed_items,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "error_message": self.error_message,
            "progress": self.get_progress(),
        }

    def get_progress(self) -> float:
        """获取进度百分比"""
        if self.total_items == 0:
            return 0.0
        return round((self.processed_items / self.total_items) * 100, 2)


@dataclass
class IncrementalConfig:
    """增量采集配置"""
    enabled: bool = False
    mode: str = "new_only"  # new_only / update_existing / full_refresh
    check_field: str = "url"  # 用于判断是否已存在的字段
    last_run_time: Optional[float] = None
    update_existing: bool = False  # 是否已存在的产品是否更新
    skip_unchanged: bool = True  # 跳过未变化的产品

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "mode": self.mode,
            "check_field": self.check_field,
            "last_run_time": self.last_run_time,
            "update_existing": self.update_existing,
            "skip_unchanged": self.skip_unchanged,
        }


@dataclass
class ScheduleConfig:
    """定时采集配置"""
    enabled: bool = False
    schedule_type: str = "interval"  # interval / cron / daily / weekly
    interval_minutes: int = 60  # 间隔分钟数
    cron_expression: Optional[str] = None  # Cron表达式
    run_at: Optional[str] = None  # 每天运行时间 HH:MM
    day_of_week: Optional[int] = None  # 每周运行 0-6
    incremental: bool = True  # 定时任务是否使用增量采集

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "schedule_type": self.schedule_type,
            "interval_minutes": self.interval_minutes,
            "cron_expression": self.cron_expression,
            "run_at": self.run_at,
            "day_of_week": self.day_of_week,
            "incremental": self.incremental,
        }
