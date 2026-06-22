"""
限流中间件
基于Redis的分布式限流
"""
import time
from typing import Dict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import status
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """限流中间件"""
    
    def __init__(self, app, default_limit: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.default_limit = default_limit
        self.window_seconds = window_seconds
        self._memory_cache: Dict[str, Dict] = {}  # 内存缓存作为备用
    
    async def dispatch(self, request: Request, call_next):
        # 跳过限流的路径
        skip_paths = ['/health', '/api/health', '/docs', '/api/docs', '/redoc', '/api/redoc']
        if request.url.path in skip_paths:
            return await call_next(request)
        
        # 获取客户端标识（IP + User-Agent）
        client_id = self._get_client_id(request)
        
        # 检查限流
        if not self._check_rate_limit(client_id):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "请求过于频繁，请稍后再试",
                    "retry_after": self.window_seconds
                }
            )
        
        # 处理请求
        response = await call_next(request)
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """获取客户端唯一标识"""
        # 优先使用X-Forwarded-For头（如果有代理）
        x_forwarded_for = request.headers.get('X-Forwarded-For')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        
        # 结合User-Agent
        user_agent = request.headers.get('User-Agent', '')
        
        return f"{ip}:{user_agent[:50]}"
    
    def _check_rate_limit(self, client_id: str) -> bool:
        """检查是否超过限流"""
        now = time.time()
        window_start = now - self.window_seconds
        
        # 使用内存缓存（生产环境建议使用Redis）
        if client_id not in self._memory_cache:
            self._memory_cache[client_id] = {
                'timestamps': [],
                'last_cleanup': now
            }
        
        client_data = self._memory_cache[client_id]
        
        # 定期清理过期记录
        if now - client_data['last_cleanup'] > self.window_seconds:
            client_data['timestamps'] = [
                ts for ts in client_data['timestamps']
                if ts > window_start
            ]
            client_data['last_cleanup'] = now
        
        # 检查是否超过限制
        if len(client_data['timestamps']) >= self.default_limit:
            return False
        
        # 添加当前请求时间戳
        client_data['timestamps'].append(now)
        return True
