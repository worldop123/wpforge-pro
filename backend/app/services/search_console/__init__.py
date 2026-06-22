"""
搜索引擎自动提交与索引模块
支持Google Search Console、Bing Webmaster Tools等
"""

from app.services.search_console.search_console_service import (
    SearchConsoleService,
    SearchConsoleConfig,
    IndexingResult,
    SearchAnalyticsData,
    RankingData,
    SearchEngine,
    IndexingStatus,
    get_search_console_service,
)

__all__ = [
    "SearchConsoleService",
    "SearchConsoleConfig",
    "IndexingResult",
    "SearchAnalyticsData",
    "RankingData",
    "SearchEngine",
    "IndexingStatus",
    "get_search_console_service",
]
