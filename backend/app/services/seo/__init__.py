"""
全自动SEO优化模块
包含页面SEO、Schema结构化数据、关键词策略、内部链接建设等
"""

from app.services.seo.seo_service import (
    SEOService,
    SEOSettings,
    SEOAnalysisResult,
    SchemaType,
    get_seo_service,
)

__all__ = [
    "SEOService",
    "SEOSettings",
    "SEOAnalysisResult",
    "SchemaType",
    "get_seo_service",
]
