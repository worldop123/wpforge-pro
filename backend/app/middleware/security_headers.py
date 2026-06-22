"""
安全头中间件
为所有响应添加安全相关的 HTTP 头，增强 XSS、点击劫持、MIME 嗅探等防护
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


# 默认安全头配置
DEFAULT_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "SAMEORIGIN",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-Permitted-Cross-Domain-Policies": "none",
    "Cross-Origin-Opener-Policy": "same-origin",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全头中间件

    为所有响应添加安全相关的 HTTP 头：
    - X-Content-Type-Options: nosniff  防止 MIME 嗅探
    - X-Frame-Options: SAMEORIGIN  防止点击劫持
    - X-XSS-Protection: 1; mode=block  XSS 过滤
    - Referrer-Policy  控制 Referer 信息泄露
    """

    def __init__(self, app, extra_headers: dict = None):
        super().__init__(app)
        self.headers = dict(DEFAULT_SECURITY_HEADERS)
        if extra_headers:
            self.headers.update(extra_headers)

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # 添加安全头（不覆盖已存在的头）
        for key, value in self.headers.items():
            if key not in response.headers:
                response.headers[key] = value

        return response
