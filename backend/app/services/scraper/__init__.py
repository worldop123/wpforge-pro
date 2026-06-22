"""
智能采集器模块
支持可视化点选选择器、变体采集、增量采集、定时采集
与反检测体系深度集成
"""

from app.services.scraper.scraper_config import (
    ScraperConfig,
    ScraperTask,
    FieldSelector,
    SelectorType,
    FieldType,
    PaginationType,
    ListPageConfig,
    DetailPageConfig,
    VariantConfig,
    IncrementalConfig,
    ScheduleConfig,
)
from app.services.scraper.enhanced_scraper import (
    EnhancedScraper,
    ScraperManager,
    get_scraper_manager,
)

__all__ = [
    # 配置模型
    "ScraperConfig",
    "ScraperTask",
    "FieldSelector",
    "SelectorType",
    "FieldType",
    "PaginationType",
    "ListPageConfig",
    "DetailPageConfig",
    "VariantConfig",
    "IncrementalConfig",
    "ScheduleConfig",
    # 采集器
    "EnhancedScraper",
    "ScraperManager",
    "get_scraper_manager",
]
