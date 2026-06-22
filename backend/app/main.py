"""
WPForge - WordPress全自动AI仿站原创软件
主应用入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.core.logging import get_logger
from app.api import api_router
from app.api.v1 import api_v1_router
from app.middleware import (
    RequestLoggingMiddleware,
    RateLimitingMiddleware,
    ErrorHandlerMiddleware,
    SecurityHeadersMiddleware,
    CSRFMiddleware,
)

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title="WPForge API",
        description="WordPress全自动AI仿站原创软件 - API接口文档",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # CORS配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 自定义中间件（注意：中间件的添加顺序很重要，最先添加的最后执行）
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(CSRFMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitingMiddleware, default_limit=settings.RATE_LIMIT_PER_MINUTE)
    
    # 注册API路由
    app.include_router(api_router, prefix="/api")
    app.include_router(api_v1_router, prefix="/api")
    
    # 静态文件服务（前端）
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
    if os.path.exists(frontend_dir):
        app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
    
    # 健康检查
    @app.get("/api/health")
    async def health_check():
        """健康检查"""
        return {
            "status": "healthy",
            "version": "1.0.0",
            "app": "WPForge"
        }
    
    # 启动事件
    @app.on_event("startup")
    async def startup_event():
        logger.info("WPForge API started")
        # 确保上传目录存在
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        os.makedirs(os.path.join(settings.UPLOAD_DIR, "checkpoints"), exist_ok=True)
    
    # 关闭事件
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("WPForge API shutdown")
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
