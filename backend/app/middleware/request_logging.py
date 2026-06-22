"""
请求日志中间件
记录所有HTTP请求的详细信息
"""
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.core.logging import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 记录开始时间
        start_time = time.time()
        
        # 记录请求信息
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        url = str(request.url.path)
        query_params = str(request.query_params) if request.query_params else ""
        
        logger.info(
            f"Request started - ID: {request_id} | "
            f"Method: {method} | "
            f"Path: {url} | "
            f"IP: {client_ip} | "
            f"Query: {query_params}"
        )
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算耗时
            duration = time.time() - start_time
            
            # 添加请求ID到响应头
            response.headers["X-Request-ID"] = request_id
            
            # 记录响应信息
            status_code = response.status_code
            
            logger.info(
                f"Request completed - ID: {request_id} | "
                f"Status: {status_code} | "
                f"Duration: {duration:.3f}s"
            )
            
            return response
            
        except Exception as e:
            # 计算耗时
            duration = time.time() - start_time
            
            # 记录错误
            logger.error(
                f"Request failed - ID: {request_id} | "
                f"Error: {str(e)} | "
                f"Duration: {duration:.3f}s",
                exc_info=True
            )
            
            raise
