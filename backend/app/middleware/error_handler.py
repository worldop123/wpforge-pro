"""
错误处理中间件
统一处理全局异常，返回标准化错误响应
"""
import traceback
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import status
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.core.logging import get_logger

logger = get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """全局错误处理中间件"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except RequestValidationError as e:
            # 请求验证错误
            logger.warning(f"Validation error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "detail": "请求参数验证失败",
                    "errors": e.errors(),
                    "code": "VALIDATION_ERROR"
                }
            )
        except SQLAlchemyError as e:
            # 数据库错误
            logger.error(f"Database error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "数据库操作失败",
                    "code": "DATABASE_ERROR"
                }
            )
        except ValueError as e:
            # 值错误
            logger.warning(f"Value error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "detail": str(e),
                    "code": "VALUE_ERROR"
                }
            )
        except PermissionError as e:
            # 权限错误
            logger.warning(f"Permission error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "detail": "权限不足",
                    "code": "PERMISSION_DENIED"
                }
            )
        except TimeoutError as e:
            # 超时错误
            logger.warning(f"Timeout error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                content={
                    "detail": "请求超时",
                    "code": "TIMEOUT_ERROR"
                }
            )
        except Exception as e:
            # 其他未知错误
            request_id = getattr(request.state, 'request_id', 'unknown')
            logger.error(
                f"Unhandled error - Request ID: {request_id} | "
                f"Error: {str(e)} | "
                f"Path: {request.url.path}",
                exc_info=True
            )
            
            # 生产环境不返回详细错误信息
            if settings.DEBUG:
                detail = str(e)
                traceback_info = traceback.format_exc()
            else:
                detail = "服务器内部错误"
                traceback_info = None
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": detail,
                    "code": "INTERNAL_SERVER_ERROR",
                    "request_id": request_id,
                    "traceback": traceback_info
                }
            )
