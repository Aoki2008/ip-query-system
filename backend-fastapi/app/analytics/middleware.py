"""
API性能监控中间件
"""
import time
import json
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .service import APIMetricsCollector


class APIAnalyticsMiddleware(BaseHTTPMiddleware):
    """API分析中间件"""
    
    def __init__(self, app, exclude_paths: list = None, sample_rate: float = 1.0):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/docs", "/redoc", "/openapi.json", "/favicon.ico",
            "/static", "/health", "/metrics"
        ]
        self.sample_rate = sample_rate  # 采样率，1.0表示100%采样
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 检查是否需要排除监控
        if self._should_exclude(request):
            return await call_next(request)
        
        # 采样控制
        import random
        if random.random() > self.sample_rate:
            return await call_next(request)
        
        # 记录开始时间
        start_time = time.time()
        
        # 获取请求信息
        method = request.method
        endpoint = self._normalize_endpoint(request.url.path)
        user_agent = request.headers.get("user-agent", "")
        ip_address = self._get_client_ip(request)
        user_id = self._get_user_id(request)
        
        # 计算请求大小
        request_size = await self._get_request_size(request)
        
        # 处理请求
        response = None
        error_message = None
        
        try:
            response = await call_next(request)
        except Exception as e:
            error_message = str(e)
            # 创建错误响应
            response = Response(
                content=json.dumps({"error": "Internal Server Error"}),
                status_code=500,
                media_type="application/json"
            )
        
        # 计算响应时间
        response_time = (time.time() - start_time) * 1000  # 转换为毫秒
        
        # 计算响应大小
        response_size = self._get_response_size(response)
        
        # 异步记录API指标
        try:
            APIMetricsCollector.collect_api_metrics(
                endpoint=endpoint,
                method=method,
                status_code=response.status_code,
                response_time_ms=response_time,
                request_size=request_size,
                response_size=response_size,
                user_agent=user_agent,
                ip_address=ip_address,
                user_id=user_id,
                error_message=error_message
            )
        except Exception as e:
            # 监控失败不应该影响正常请求
            print(f"API指标收集失败: {e}")
        
        # 添加性能头
        response.headers["X-Response-Time"] = f"{response_time:.2f}ms"
        response.headers["X-Request-ID"] = self._generate_request_id()
        
        return response
    
    def _should_exclude(self, request: Request) -> bool:
        """检查是否应该排除监控"""
        path = request.url.path
        return any(path.startswith(exclude_path) for exclude_path in self.exclude_paths)
    
    def _normalize_endpoint(self, path: str) -> str:
        """标准化端点路径"""
        # 移除查询参数
        if "?" in path:
            path = path.split("?")[0]
        
        # 标准化路径参数（简化处理）
        # 例如：/api/users/123 -> /api/users/{id}
        import re
        
        # 替换数字ID
        path = re.sub(r'/\d+', '/{id}', path)
        
        # 替换UUID
        path = re.sub(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/{uuid}', path, flags=re.IGNORECASE)
        
        return path
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 检查代理头
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # 返回直接连接的IP
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return "unknown"
    
    def _get_user_id(self, request: Request) -> Optional[int]:
        """获取用户ID"""
        # 从请求状态中获取用户信息（如果有认证中间件设置）
        if hasattr(request.state, "user"):
            user = request.state.user
            if hasattr(user, "id"):
                return user.id
        
        # 从JWT令牌中解析用户ID（简化处理）
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                # 这里应该解析JWT令牌，简化处理
                return None
            except:
                pass
        
        return None
    
    async def _get_request_size(self, request: Request) -> int:
        """获取请求大小"""
        try:
            content_length = request.headers.get("content-length")
            if content_length:
                return int(content_length)
            
            # 如果没有content-length头，尝试读取body
            if hasattr(request, "_body"):
                return len(request._body) if request._body else 0
            
            return 0
        except:
            return 0
    
    def _get_response_size(self, response: Response) -> int:
        """获取响应大小"""
        try:
            if hasattr(response, "body") and response.body:
                return len(response.body)
            
            content_length = response.headers.get("content-length")
            if content_length:
                return int(content_length)
            
            return 0
        except:
            return 0
    
    def _generate_request_id(self) -> str:
        """生成请求ID"""
        import uuid
        return str(uuid.uuid4())[:8]


class PerformanceAnalyticsMiddleware(BaseHTTPMiddleware):
    """性能分析中间件"""
    
    def __init__(self, app, slow_request_threshold: float = 2000.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold  # 毫秒
        self.request_count = 0
        self.slow_request_count = 0
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        response = await call_next(request)
        
        response_time = (time.time() - start_time) * 1000
        self.request_count += 1
        
        # 检查慢请求
        if response_time > self.slow_request_threshold:
            self.slow_request_count += 1
            print(f"慢请求检测: {request.method} {request.url.path} - {response_time:.2f}ms")
            
            # 记录慢请求到用户活动日志
            self._log_slow_request(request, response_time)
        
        # 添加性能统计头
        response.headers["X-Request-Count"] = str(self.request_count)
        response.headers["X-Slow-Request-Rate"] = f"{(self.slow_request_count / self.request_count * 100):.2f}%"
        
        return response
    
    def _log_slow_request(self, request: Request, response_time: float):
        """记录慢请求"""
        try:
            APIMetricsCollector.log_user_activity(
                user_id=0,  # 系统用户
                username="system",
                action="slow_request_detected",
                resource=f"{request.method} {request.url.path}",
                ip_address=request.client.host if request.client else "unknown",
                details={
                    "response_time_ms": response_time,
                    "threshold_ms": self.slow_request_threshold,
                    "user_agent": request.headers.get("user-agent", "")
                },
                success=False
            )
        except Exception as e:
            print(f"记录慢请求失败: {e}")


class RateLimitAnalyticsMiddleware(BaseHTTPMiddleware):
    """速率限制分析中间件"""
    
    def __init__(self, app, window_size: int = 60):
        super().__init__(app)
        self.window_size = window_size  # 时间窗口大小（秒）
        self.request_history = {}  # IP -> [timestamp, ...]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        ip_address = self._get_client_ip(request)
        current_time = time.time()
        
        # 清理过期记录
        self._cleanup_expired_records(current_time)
        
        # 记录当前请求
        if ip_address not in self.request_history:
            self.request_history[ip_address] = []
        
        self.request_history[ip_address].append(current_time)
        
        # 计算当前窗口内的请求数
        window_start = current_time - self.window_size
        recent_requests = [
            ts for ts in self.request_history[ip_address]
            if ts >= window_start
        ]
        
        request_rate = len(recent_requests) / self.window_size
        
        response = await call_next(request)
        
        # 添加速率限制头
        response.headers["X-Rate-Limit-Window"] = str(self.window_size)
        response.headers["X-Rate-Limit-Requests"] = str(len(recent_requests))
        response.headers["X-Rate-Limit-Rate"] = f"{request_rate:.2f}"
        
        # 如果请求率过高，记录到分析系统
        if request_rate > 10:  # 每秒超过10个请求
            self._log_high_rate_activity(request, ip_address, request_rate)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return "unknown"
    
    def _cleanup_expired_records(self, current_time: float):
        """清理过期记录"""
        window_start = current_time - self.window_size
        
        for ip in list(self.request_history.keys()):
            self.request_history[ip] = [
                ts for ts in self.request_history[ip]
                if ts >= window_start
            ]
            
            # 如果没有最近的请求，删除该IP的记录
            if not self.request_history[ip]:
                del self.request_history[ip]
    
    def _log_high_rate_activity(self, request: Request, ip_address: str, request_rate: float):
        """记录高频率活动"""
        try:
            APIMetricsCollector.log_user_activity(
                user_id=0,  # 系统用户
                username="system",
                action="high_rate_detected",
                resource=f"{request.method} {request.url.path}",
                ip_address=ip_address,
                details={
                    "request_rate": request_rate,
                    "window_size": self.window_size,
                    "user_agent": request.headers.get("user-agent", "")
                },
                success=False
            )
        except Exception as e:
            print(f"记录高频率活动失败: {e}")
