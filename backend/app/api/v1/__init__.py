"""
API v1 路由模块
"""
from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.sites import router as sites_router
from app.api.v1.products import router as products_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.scraping import router as scraping_router
from app.api.v1.translation import router as translation_router
from app.api.v1.seo import router as seo_router
from app.api.v1.price import router as price_router
from app.api.v1.wordpress import router as wordpress_router
from app.api.v1.ai import router as ai_router
from app.api.v1.proxy import router as proxy_router
from app.api.v1.monitoring import router as monitoring_router

api_v1_router = APIRouter(prefix="/v1", tags=["API v1"])

# 注册各模块路由
api_v1_router.include_router(auth_router)
api_v1_router.include_router(sites_router)
api_v1_router.include_router(products_router)
api_v1_router.include_router(tasks_router)
api_v1_router.include_router(scraping_router)
api_v1_router.include_router(translation_router)
api_v1_router.include_router(seo_router)
api_v1_router.include_router(price_router)
api_v1_router.include_router(wordpress_router)
api_v1_router.include_router(ai_router)
api_v1_router.include_router(proxy_router)
api_v1_router.include_router(monitoring_router)
