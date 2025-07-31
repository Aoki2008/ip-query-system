"""
安全中间件模块
实施Web安全防护措施
"""
import time
import secrets
from typing import Dict, Set, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta

from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from ..config import settings


class SecurityHeaders:
    """安全头配置"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """获取安全响应头"""
        return {
            # XSS防护
            "X-XSS-Protection": "1; mode=block",
            
            # 内容类型嗅探防护
            "X-Content-Type-Options": "nosniff",
            
            # 点击劫持防护
            "X-Frame-Options": "DENY",
            
            # 内容安全策略
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            ),
            
            # 严格传输安全
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            
            # 推荐人策略
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # 权限策略
            "Permissions-Policy": (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "speaker=()"
            ),
            
            # 服务器信息隐藏
            "Server": "SecureServer/1.0"
        }


class RateLimiter:
    """速率限制器"""
    
    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.blocked_ips: Set[str] = set()
        self.block_until: Dict[str, datetime] = {}
    
    def is_allowed(self, client_ip: str, max_requests: int = 100, window_seconds: int = 60) -> bool:
        """
        检查是否允许请求
        
        Args:
            client_ip: 客户端IP
            max_requests: 最大请求数
            window_seconds: 时间窗口（秒）
            
        Returns:
            bool: 是否允许请求
        """
        now = datetime.utcnow()
        
        # 检查是否在封禁期内
        if client_ip in self.block_until:
            if now < self.block_until[client_ip]:
                return False
            else:
                # 解除封禁
                self.blocked_ips.discard(client_ip)
                del self.block_until[client_ip]
        
        # 清理过期请求记录
        cutoff_time = now - timedelta(seconds=window_seconds)
        request_times = self.requests[client_ip]
        
        while request_times and request_times[0] < cutoff_time:
            request_times.popleft()
        
        # 检查请求频率
        if len(request_times) >= max_requests:
            # 触发速率限制，封禁IP
            self.blocked_ips.add(client_ip)
            self.block_until[client_ip] = now + timedelta(minutes=15)  # 封禁15分钟
            return False
        
        # 记录当前请求
        request_times.append(now)
        return True


class CSRFProtection:
    """CSRF防护"""
    
    def __init__(self):
        self.tokens: Dict[str, datetime] = {}
        self.token_lifetime = timedelta(hours=1)
    
    def generate_token(self) -> str:
        """生成CSRF令牌"""
        token = secrets.token_urlsafe(32)
        self.tokens[token] = datetime.utcnow()
        return token
    
    def validate_token(self, token: str) -> bool:
        """验证CSRF令牌"""
        if not token or token not in self.tokens:
            return False
        
        # 检查令牌是否过期
        if datetime.utcnow() - self.tokens[token] > self.token_lifetime:
            del self.tokens[token]
            return False
        
        return True
    
    def cleanup_expired_tokens(self):
        """清理过期令牌"""
        now = datetime.utcnow()
        expired_tokens = [
            token for token, created_at in self.tokens.items()
            if now - created_at > self.token_lifetime
        ]
        for token in expired_tokens:
            del self.tokens[token]


class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""
    
    def __init__(self, app):
        super().__init__(app)
        self.rate_limiter = RateLimiter()
        self.csrf_protection = CSRFProtection()
        self.security_headers = SecurityHeaders()
        
        # 不需要CSRF保护的路径
        self.csrf_exempt_paths = {
            "/api/health",
            "/api/metrics",
            "/docs",
            "/redoc",
            "/openapi.json"
        }
        
        # 不需要速率限制的路径
        self.rate_limit_exempt_paths = {
            "/api/health",
            "/docs",
            "/redoc",
            "/openapi.json"
        }
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        start_time = time.time()
        
        # 获取客户端IP
        client_ip = self._get_client_ip(request)
        
        # 速率限制检查
        if request.url.path not in self.rate_limit_exempt_paths:
            if not self.rate_limiter.is_allowed(client_ip):
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "请求过于频繁，请稍后再试"}
                )
        
        # CSRF保护检查
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            if request.url.path not in self.csrf_exempt_paths:
                csrf_token = request.headers.get("X-CSRF-Token")
                if not csrf_token or not self.csrf_protection.validate_token(csrf_token):
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"detail": "CSRF令牌无效或缺失"}
                    )
        
        # 输入验证
        if not self._validate_request_input(request):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "请求包含非法字符"}
            )
        
        # 处理请求
        response = await call_next(request)
        
        # 添加安全响应头
        for header, value in self.security_headers.get_security_headers().items():
            response.headers[header] = value
        
        # 添加处理时间头
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # 定期清理过期令牌
        if time.time() % 3600 < 1:  # 每小时清理一次
            self.csrf_protection.cleanup_expired_tokens()
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端真实IP"""
        # 检查代理头
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # 取第一个IP（原始客户端IP）
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 检查Cloudflare头
        cf_connecting_ip = request.headers.get("CF-Connecting-IP")
        if cf_connecting_ip:
            return cf_connecting_ip
        
        return request.client.host if request.client else "unknown"
    
    def _validate_request_input(self, request: Request) -> bool:
        """验证请求输入"""
        # 检查URL路径
        if self._contains_malicious_patterns(request.url.path):
            return False
        
        # 检查查询参数
        for key, value in request.query_params.items():
            if self._contains_malicious_patterns(key) or self._contains_malicious_patterns(value):
                return False
        
        # 检查请求头
        for key, value in request.headers.items():
            if self._contains_malicious_patterns(value):
                return False
        
        return True
    
    def _contains_malicious_patterns(self, text: str) -> bool:
        """检查是否包含恶意模式"""
        if not text:
            return False
        
        text_lower = text.lower()
        
        # SQL注入模式
        sql_patterns = [
            "union select", "drop table", "delete from", "insert into",
            "update set", "exec(", "execute(", "sp_", "xp_", "/*", "*/",
            "--", ";--", "0x", "char(", "ascii(", "substring("
        ]
        
        # XSS模式
        xss_patterns = [
            "<script", "</script>", "javascript:", "vbscript:", "onload=",
            "onerror=", "onclick=", "onmouseover=", "onfocus=", "onblur=",
            "eval(", "expression(", "url(javascript", "mocha:", "livescript:"
        ]
        
        # 路径遍历模式
        path_patterns = [
            "../", "..\\", "..\\/", "..%2f", "..%5c", "%2e%2e%2f", "%2e%2e%5c"
        ]
        
        # 命令注入模式
        command_patterns = [
            "|", "&", ";", "`", "$", "(", ")", "{", "}", "[", "]",
            "&&", "||", "$(", "${", "<%", "%>", "<?", "?>"
        ]
        
        all_patterns = sql_patterns + xss_patterns + path_patterns + command_patterns
        
        for pattern in all_patterns:
            if pattern in text_lower:
                return True
        
        return False
    
    def get_csrf_token(self) -> str:
        """获取CSRF令牌"""
        return self.csrf_protection.generate_token()


# 全局安全中间件实例
security_middleware = None


def get_security_middleware():
    """获取安全中间件实例"""
    global security_middleware
    if security_middleware is None:
        security_middleware = SecurityMiddleware
    return security_middleware
