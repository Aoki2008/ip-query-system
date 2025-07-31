"""
API性能监控中间件
"""
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .service import APIMetricService
from ..database import SessionLocal


class APIMonitoringMiddleware(BaseHTTPMiddleware):
    """API监控中间件"""
    
    def __init__(self, app, exclude_paths: list = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/docs", "/redoc", "/openapi.json", "/favicon.ico",
            "/static", "/health"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 检查是否需要排除监控
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # 记录开始时间
        start_time = time.time()
        
        # 获取请求信息
        method = request.method
        endpoint = request.url.path
        user_agent = request.headers.get("user-agent", "")
        ip_address = self._get_client_ip(request)
        
        # 计算请求大小
        request_size = 0
        if hasattr(request, "body"):
            try:
                body = await request.body()
                request_size = len(body) if body else 0
            except:
                request_size = 0
        
        # 处理请求
        response = await call_next(request)
        
        # 计算响应时间
        response_time = (time.time() - start_time) * 1000  # 转换为毫秒
        
        # 计算响应大小
        response_size = 0
        if hasattr(response, "body"):
            try:
                response_size = len(response.body) if response.body else 0
            except:
                response_size = 0
        
        # 异步记录API指标
        try:
            self._record_api_metric(
                endpoint=endpoint,
                method=method,
                status_code=response.status_code,
                response_time=response_time,
                request_size=request_size,
                response_size=response_size,
                user_agent=user_agent,
                ip_address=ip_address
            )
        except Exception as e:
            # 监控失败不应该影响正常请求
            print(f"API监控记录失败: {e}")
        
        return response
    
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
    
    def _record_api_metric(self, endpoint: str, method: str, status_code: int,
                          response_time: float, request_size: int = 0,
                          response_size: int = 0, user_agent: str = "",
                          ip_address: str = ""):
        """记录API指标到数据库"""
        try:
            db = SessionLocal()
            api_metric_service = APIMetricService(db)
            
            api_metric_service.record_api_call(
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time=response_time,
                request_size=request_size,
                response_size=response_size,
                user_agent=user_agent,
                ip_address=ip_address
            )
            
            db.close()
        except Exception as e:
            print(f"记录API指标失败: {e}")


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """性能监控中间件"""
    
    def __init__(self, app, slow_request_threshold: float = 1000.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold  # 毫秒
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        response = await call_next(request)
        
        response_time = (time.time() - start_time) * 1000
        
        # 检查慢请求
        if response_time > self.slow_request_threshold:
            print(f"慢请求警告: {request.method} {request.url.path} - {response_time:.2f}ms")
            
            # 可以在这里记录慢请求日志或发送告警
            self._log_slow_request(request, response_time)
        
        # 添加性能头
        response.headers["X-Response-Time"] = f"{response_time:.2f}ms"
        
        return response
    
    def _log_slow_request(self, request: Request, response_time: float):
        """记录慢请求"""
        try:
            from .service import AlertService, AlertCreate, AlertLevel
            from ..database import SessionLocal
            
            db = SessionLocal()
            alert_service = AlertService(db)
            
            alert = AlertCreate(
                alert_type="performance",
                level=AlertLevel.WARNING,
                title="慢请求检测",
                message=f"检测到慢请求: {request.method} {request.url.path} - {response_time:.2f}ms",
                metric_name="response_time",
                metric_value=response_time,
                threshold_value=self.slow_request_threshold
            )
            
            alert_service.create_alert(alert)
            db.close()
            
        except Exception as e:
            print(f"记录慢请求告警失败: {e}")


class HealthCheckMiddleware(BaseHTTPMiddleware):
    """健康检查中间件"""
    
    def __init__(self, app):
        super().__init__(app)
        self.request_count = 0
        self.error_count = 0
        self.start_time = time.time()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        self.request_count += 1
        
        response = await call_next(request)
        
        # 统计错误
        if response.status_code >= 400:
            self.error_count += 1
        
        # 添加健康状态头
        uptime = time.time() - self.start_time
        error_rate = (self.error_count / self.request_count) * 100 if self.request_count > 0 else 0
        
        response.headers["X-Request-Count"] = str(self.request_count)
        response.headers["X-Error-Rate"] = f"{error_rate:.2f}%"
        response.headers["X-Uptime"] = f"{uptime:.0f}s"
        
        return response
