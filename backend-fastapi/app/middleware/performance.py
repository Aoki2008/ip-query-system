"""
性能监控中间件
"""
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger, request_logger, performance_monitor

logger = get_logger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """性能监控中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并记录性能数据"""
        start_time = time.time()
        
        # 记录请求信息
        request_logger.log_request(
            method=request.method,
            path=request.url.path,
            ip=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "")
        )
        
        # 处理请求
        response = await call_next(request)
        
        # 计算响应时间
        response_time = time.time() - start_time
        
        # 记录响应信息
        request_logger.log_response(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            response_time=response_time
        )
        
        # 记录性能数据
        performance_monitor.record_request(
            response_time=response_time,
            success=response.status_code < 400
        )
        
        # 添加响应头
        response.headers["X-Response-Time"] = f"{response_time:.3f}s"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """简单的频率限制中间件"""
    
    def __init__(self, app, calls_per_minute: int = 60):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.requests = {}  # {ip: [timestamp, ...]}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """频率限制检查"""
        # OPTIONS预检请求不进行频率限制
        if request.method == "OPTIONS":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()

        # 清理过期记录
        if client_ip in self.requests:
            self.requests[client_ip] = [
                timestamp for timestamp in self.requests[client_ip]
                if current_time - timestamp < 60  # 保留最近1分钟的记录
            ]
        else:
            self.requests[client_ip] = []

        # 检查频率限制
        if len(self.requests[client_ip]) >= self.calls_per_minute:
            logger.warning(f"频率限制触发: {client_ip}")

            # 创建带CORS头的429响应
            response = Response(
                content='{"error": {"code": "RATE_LIMIT_ERROR", "message": "请求过于频繁，请稍后再试"}}',
                status_code=429,
                media_type="application/json"
            )

            # 添加CORS头
            origin = request.headers.get("origin")
            if origin:
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
                response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept, Origin, X-Requested-With"

            return response

        # 记录请求时间
        self.requests[client_ip].append(current_time)

        # 处理请求
        response = await call_next(request)
        return response
