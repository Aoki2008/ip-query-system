"""
异常处理模块
定义自定义异常和全局异常处理器
"""
from typing import Any, Dict
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger

logger = get_logger(__name__)


class IPQueryException(Exception):
    """IP查询相关异常基类"""
    
    def __init__(self, message: str, error_code: str = "IP_QUERY_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ValidationException(IPQueryException):
    """参数验证异常"""
    
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class GeoIPException(IPQueryException):
    """GeoIP查询异常"""
    
    def __init__(self, message: str):
        super().__init__(message, "GEOIP_ERROR")


class CacheException(IPQueryException):
    """缓存服务异常"""
    
    def __init__(self, message: str):
        super().__init__(message, "CACHE_ERROR")


class RateLimitException(IPQueryException):
    """频率限制异常"""
    
    def __init__(self, message: str):
        super().__init__(message, "RATE_LIMIT_ERROR")


def create_error_response(
    status_code: int,
    message: str,
    error_code: str = "UNKNOWN_ERROR",
    details: Any = None
) -> JSONResponse:
    """创建错误响应"""
    content = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message
        }
    }
    
    if details:
        content["error"]["details"] = details
    
    return JSONResponse(
        status_code=status_code,
        content=content
    )


async def ip_query_exception_handler(request: Request, exc: IPQueryException) -> JSONResponse:
    """IP查询异常处理器"""
    logger.error(
        "IP查询异常",
        error_code=exc.error_code,
        message=exc.message,
        path=request.url.path
    )
    
    status_code = 400
    if exc.error_code == "RATE_LIMIT_ERROR":
        status_code = 429
    elif exc.error_code == "GEOIP_ERROR":
        status_code = 503
    
    return create_error_response(
        status_code=status_code,
        message=exc.message,
        error_code=exc.error_code
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """参数验证异常处理器"""
    logger.warning(
        "参数验证失败",
        errors=exc.errors(),
        path=request.url.path
    )
    
    return create_error_response(
        status_code=422,
        message="请求参数验证失败",
        error_code="VALIDATION_ERROR",
        details=exc.errors()
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """HTTP异常处理器"""
    logger.warning(
        "HTTP异常",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path
    )
    
    return create_error_response(
        status_code=exc.status_code,
        message=exc.detail or "请求处理失败",
        error_code="HTTP_ERROR"
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """通用异常处理器"""
    logger.error(
        "未处理的异常",
        exception_type=type(exc).__name__,
        exception_message=str(exc),
        path=request.url.path,
        exc_info=True
    )
    
    return create_error_response(
        status_code=500,
        message="服务器内部错误",
        error_code="INTERNAL_ERROR"
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """设置异常处理器"""
    
    # 自定义异常处理器
    app.add_exception_handler(IPQueryException, ip_query_exception_handler)
    
    # 参数验证异常处理器
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # HTTP异常处理器
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # 通用异常处理器
    app.add_exception_handler(Exception, general_exception_handler)
