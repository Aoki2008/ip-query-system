"""
安全错误处理中间件
优化错误响应，避免敏感信息泄露
"""
import logging
import traceback
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from ..config import settings
from .security_audit import log_security_event, SecurityEventType, SecurityLevel


# 配置日志
logger = logging.getLogger(__name__)


class SecurityErrorHandler(BaseHTTPMiddleware):
    """安全错误处理中间件"""
    
    def __init__(self, app, debug: bool = False):
        super().__init__(app)
        self.debug = debug or settings.debug
        
        # 敏感信息模式
        self.sensitive_patterns = [
            r'password',
            r'secret',
            r'token',
            r'key',
            r'api_key',
            r'database',
            r'connection',
            r'file.*not.*found',
            r'permission.*denied',
            r'access.*denied',
            r'unauthorized',
            r'forbidden',
            r'internal.*error',
            r'traceback',
            r'exception',
            r'stack.*trace'
        ]
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """处理请求和错误响应"""
        try:
            response = await call_next(request)
            return response
            
        except HTTPException as exc:
            return await self._handle_http_exception(request, exc)
            
        except Exception as exc:
            return await self._handle_general_exception(request, exc)
    
    async def _handle_http_exception(self, request: Request, exc: HTTPException) -> JSONResponse:
        """处理HTTP异常"""
        # 记录安全事件
        if exc.status_code in [401, 403, 404]:
            await self._log_security_event(request, exc)
        
        # 生成安全的错误响应
        error_response = self._create_safe_error_response(
            status_code=exc.status_code,
            error_type="http_error",
            message=exc.detail,
            request=request
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response
        )
    
    async def _handle_general_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """处理一般异常"""
        # 记录详细错误信息到日志
        logger.error(
            f"未处理的异常: {type(exc).__name__}: {str(exc)}",
            extra={
                "request_path": str(request.url),
                "request_method": request.method,
                "client_ip": self._get_client_ip(request),
                "traceback": traceback.format_exc()
            }
        )
        
        # 记录安全事件
        await self._log_security_event(request, exc, is_internal=True)
        
        # 生成安全的错误响应
        error_response = self._create_safe_error_response(
            status_code=500,
            error_type="internal_error",
            message="内部服务器错误",
            request=request,
            original_exception=exc
        )
        
        return JSONResponse(
            status_code=500,
            content=error_response
        )
    
    def _create_safe_error_response(
        self,
        status_code: int,
        error_type: str,
        message: str,
        request: Request,
        original_exception: Optional[Exception] = None
    ) -> Dict[str, Any]:
        """创建安全的错误响应"""
        
        # 基础错误响应
        error_response = {
            "error": True,
            "error_type": error_type,
            "status_code": status_code,
            "message": self._sanitize_error_message(message),
            "timestamp": self._get_current_timestamp(),
            "request_id": self._generate_request_id(request)
        }
        
        # 根据状态码提供用户友好的消息
        user_messages = {
            400: "请求参数错误，请检查输入数据",
            401: "身份验证失败，请重新登录",
            403: "权限不足，无法访问此资源",
            404: "请求的资源不存在",
            405: "不支持的请求方法",
            422: "请求数据格式错误",
            429: "请求过于频繁，请稍后重试",
            500: "服务器内部错误，请稍后重试",
            502: "服务暂时不可用，请稍后重试",
            503: "服务维护中，请稍后重试"
        }
        
        if status_code in user_messages:
            error_response["user_message"] = user_messages[status_code]
        
        # 开发环境提供更多调试信息
        if self.debug and original_exception:
            error_response["debug_info"] = {
                "exception_type": type(original_exception).__name__,
                "exception_message": str(original_exception),
                "request_path": str(request.url),
                "request_method": request.method
            }
        
        # 生产环境隐藏敏感信息
        if not self.debug:
            error_response = self._remove_sensitive_info(error_response)
        
        return error_response
    
    def _sanitize_error_message(self, message: str) -> str:
        """清理错误消息，移除敏感信息"""
        import re
        
        # 如果是生产环境，使用通用错误消息
        if not self.debug:
            generic_messages = {
                "database": "数据访问错误",
                "file": "文件操作错误", 
                "permission": "权限错误",
                "connection": "连接错误",
                "authentication": "认证错误",
                "authorization": "授权错误"
            }
            
            message_lower = message.lower()
            for keyword, generic_msg in generic_messages.items():
                if keyword in message_lower:
                    return generic_msg
        
        # 移除敏感信息模式
        sanitized = message
        for pattern in self.sensitive_patterns:
            sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE)
        
        # 移除文件路径
        sanitized = re.sub(r'/[^\s]*', '[PATH]', sanitized)
        
        # 移除IP地址
        sanitized = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP]', sanitized)
        
        return sanitized
    
    def _remove_sensitive_info(self, error_response: Dict[str, Any]) -> Dict[str, Any]:
        """移除响应中的敏感信息"""
        # 移除调试信息
        if "debug_info" in error_response:
            del error_response["debug_info"]
        
        # 简化错误消息
        if "message" in error_response:
            error_response["message"] = self._sanitize_error_message(error_response["message"])
        
        return error_response
    
    async def _log_security_event(
        self,
        request: Request,
        exception: Exception,
        is_internal: bool = False
    ):
        """记录安全事件"""
        try:
            if is_internal:
                event_type = SecurityEventType.SYSTEM_ERROR
                level = SecurityLevel.HIGH
                message = f"系统内部错误: {type(exception).__name__}"
            elif isinstance(exception, HTTPException):
                if exception.status_code == 401:
                    event_type = SecurityEventType.LOGIN_FAILURE
                    level = SecurityLevel.MEDIUM
                    message = "身份验证失败"
                elif exception.status_code == 403:
                    event_type = SecurityEventType.PERMISSION_DENIED
                    level = SecurityLevel.MEDIUM
                    message = "权限访问被拒绝"
                else:
                    event_type = SecurityEventType.SYSTEM_ERROR
                    level = SecurityLevel.LOW
                    message = f"HTTP错误: {exception.status_code}"
            else:
                event_type = SecurityEventType.SYSTEM_ERROR
                level = SecurityLevel.MEDIUM
                message = f"未知错误: {type(exception).__name__}"
            
            log_security_event(
                event_type=event_type,
                level=level,
                message=message,
                ip_address=self._get_client_ip(request),
                user_agent=request.headers.get("user-agent"),
                endpoint=str(request.url.path),
                method=request.method,
                status_code=getattr(exception, 'status_code', 500),
                details={
                    "exception_type": type(exception).__name__,
                    "exception_message": str(exception)[:200],  # 限制长度
                    "request_id": self._generate_request_id(request)
                }
            )
            
        except Exception as log_error:
            logger.error(f"记录安全事件失败: {log_error}")
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 检查代理头
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # 回退到直接连接IP
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return "unknown"
    
    def _generate_request_id(self, request: Request) -> str:
        """生成请求ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()


# 全局异常处理器
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理器"""
    handler = SecurityErrorHandler(None, debug=settings.debug)
    return await handler._handle_general_exception(request, exc)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP异常处理器"""
    handler = SecurityErrorHandler(None, debug=settings.debug)
    return await handler._handle_http_exception(request, exc)


# 自定义异常类
class SecurityException(HTTPException):
    """安全相关异常"""
    
    def __init__(self, status_code: int, detail: str, security_event: bool = True):
        super().__init__(status_code=status_code, detail=detail)
        self.security_event = security_event


class RateLimitException(SecurityException):
    """速率限制异常"""
    
    def __init__(self, detail: str = "请求过于频繁，请稍后重试"):
        super().__init__(status_code=429, detail=detail)


class AuthenticationException(SecurityException):
    """认证异常"""
    
    def __init__(self, detail: str = "身份验证失败"):
        super().__init__(status_code=401, detail=detail)


class AuthorizationException(SecurityException):
    """授权异常"""
    
    def __init__(self, detail: str = "权限不足"):
        super().__init__(status_code=403, detail=detail)


class ValidationException(SecurityException):
    """验证异常"""
    
    def __init__(self, detail: str = "数据验证失败"):
        super().__init__(status_code=422, detail=detail, security_event=False)


# 错误响应模板
ERROR_TEMPLATES = {
    "generic": {
        "error": True,
        "message": "操作失败，请稍后重试",
        "code": "GENERIC_ERROR"
    },
    "validation": {
        "error": True,
        "message": "输入数据格式错误",
        "code": "VALIDATION_ERROR"
    },
    "authentication": {
        "error": True,
        "message": "身份验证失败，请重新登录",
        "code": "AUTH_ERROR"
    },
    "authorization": {
        "error": True,
        "message": "权限不足，无法访问此资源",
        "code": "PERMISSION_ERROR"
    },
    "rate_limit": {
        "error": True,
        "message": "请求过于频繁，请稍后重试",
        "code": "RATE_LIMIT_ERROR"
    },
    "not_found": {
        "error": True,
        "message": "请求的资源不存在",
        "code": "NOT_FOUND_ERROR"
    },
    "internal": {
        "error": True,
        "message": "服务器内部错误，请稍后重试",
        "code": "INTERNAL_ERROR"
    }
}
