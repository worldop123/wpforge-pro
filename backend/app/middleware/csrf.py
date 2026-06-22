"""
CSRF 中间件
为状态变更请求（POST/PUT/DELETE/PATCH）提供 CSRF 防护

策略：
- 对于 API 请求（使用 Bearer Token 认证），CSRF 风险较低，因为浏览器不会自动附带 Authorization 头
- 对于使用 Cookie 认证的请求，需要验证 CSRF Token
- 豁免 API 文档路径和健康检查
"""
import hmac
import secrets
from typing import Optional, Set

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import status

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# 需要 CSRF 防护的 HTTP 方法
CSRF_PROTECTED_METHODS: Set[str] = {"POST", "PUT", "PATCH", "DELETE"}

# 豁免路径前缀
CSRF_EXEMPT_PATHS = {
    "/api/health",
    "/api/docs",
    "/api/redoc",
    "/api/openapi.json",
    "/docs",
    "/redoc",
    "/openapi.json",
}

# 豁免路径（精确匹配，用于认证等不需要 CSRF 的端点）
CSRF_EXEMPT_EXACT_PATHS = {
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/refresh",
}

# CSRF Token 的请求头名称和 Cookie 名称
CSRF_HEADER_NAME = "X-CSRF-Token"
CSRF_COOKIE_NAME = "csrf_token"


class CSRFMiddleware(BaseHTTPMiddleware):
    """CSRF 防护中间件

    对于需要 CSRF 防护的方法，检查请求头中的 CSRF Token 是否与 Cookie 中的一致。
    使用 Bearer Token 认证的 API 请求可豁免（因为不依赖 Cookie）。
    """

    def __init__(self, app, secret: str = None):
        super().__init__(app)
        self.secret = secret or settings.SECRET_KEY

    async def dispatch(self, request: Request, call_next):
        # 非 CSRF 保护方法直接放行
        if request.method not in CSRF_PROTECTED_METHODS:
            return await call_next(request)

        # 豁免路径直接放行
        path = request.url.path
        for exempt in CSRF_EXEMPT_PATHS:
            if path.startswith(exempt):
                return await call_next(request)

        # 精确匹配豁免路径（认证端点等）
        if path in CSRF_EXEMPT_EXACT_PATHS:
            return await call_next(request)

        # 使用 Bearer Token 认证的请求豁免 CSRF 检查
        # （Bearer Token 不会被浏览器自动发送，不存在 CSRF 风险）
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return await call_next(request)

        # 没有 Cookie 的请求不涉及 CSRF 风险，放行让后续认证逻辑处理
        cookie_header = request.headers.get("Cookie", "")
        if not cookie_header:
            return await call_next(request)

        # 对于使用 Cookie 的请求，验证 CSRF Token
        cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
        header_token = request.headers.get(CSRF_HEADER_NAME)

        if not cookie_token or not header_token:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "缺少 CSRF Token", "code": "CSRF_TOKEN_MISSING"}
            )

        if not self._verify_token(cookie_token, header_token):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "CSRF Token 验证失败", "code": "CSRF_TOKEN_INVALID"}
            )

        return await call_next(request)

    def _verify_token(self, cookie_token: str, header_token: str) -> bool:
        """使用恒定时间比较验证 CSRF Token，防止时序攻击"""
        try:
            return hmac.compare_digest(cookie_token, header_token)
        except Exception:
            return False


def generate_csrf_token() -> str:
    """生成 CSRF Token"""
    return secrets.token_urlsafe(32)
