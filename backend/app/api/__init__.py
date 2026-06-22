"""
API路由模块
"""

from fastapi import APIRouter

from app.api.scraping import router as scraping_router
from app.api.wordpress import router as wordpress_router
from app.api.translation import router as translation_router
from app.api.seo import router as seo_router
from app.api.ai import router as ai_router
from app.api.price import router as price_router

api_router = APIRouter()

api_router.include_router(scraping_router)
api_router.include_router(wordpress_router)
api_router.include_router(translation_router)
api_router.include_router(seo_router)
api_router.include_router(ai_router)
api_router.include_router(price_router)
