"""
安全加固系统
"""
import hashlib
import secrets
import re
import ipaddress
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from functools import wraps
from collections import defaultdict
# import jwt  # 暂时注释，避免依赖问题
from pydantic import BaseModel
from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session

from ..database import SessionLocal


class SecurityConfig(BaseModel):
    """安全配置模型"""
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_symbols: bool = True
    jwt_secret_key: str = secrets.token_urlsafe(32)
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24小时
    rate_limit_requests: int = 100
    rate_limit_window_minutes: int = 1
    allowed_origins: List[str] = ["*"]
    blocked_ips: List[str] = []
    trusted_proxies: List[str] = []


class SecurityEvent(BaseModel):
    """安全事件模型"""
    event_type: str
    severity: str  # low, medium, high, critical
    source_ip: str
    user_agent: str
    description: str
    details: Dict[str, Any]
    timestamp: datetime


class LoginAttempt(BaseModel):
    """登录尝试模型"""
    ip_address: str
    username: str
    success: bool
    timestamp: datetime
    user_agent: str


class RateLimitRecord(BaseModel):
    """速率限制记录模型"""
    ip_address: str
    endpoint: str
    request_count: int
    window_start: datetime
    blocked: bool


class SecurityManager:
    """安全管理器"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.login_attempts: Dict[str, List[LoginAttempt]] = defaultdict(list)
        self.rate_limit_records: Dict[str, RateLimitRecord] = {}
        self.security_events: List[SecurityEvent] = []
        self.blocked_ips: Set[str] = set(config.blocked_ips)
        self.suspicious_ips: Set[str] = set()
    
    def validate_password(self, password: str) -> Dict[str, Any]:
        """验证密码强度"""
        errors = []
        score = 0
        
        # 长度检查
        if len(password) < self.config.password_min_length:
            errors.append(f"密码长度至少{self.config.password_min_length}位")
        else:
            score += 20
        
        # 大写字母检查
        if self.config.password_require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("密码必须包含大写字母")
        elif re.search(r'[A-Z]', password):
            score += 20
        
        # 小写字母检查
        if self.config.password_require_lowercase and not re.search(r'[a-z]', password):
            errors.append("密码必须包含小写字母")
        elif re.search(r'[a-z]', password):
            score += 20
        
        # 数字检查
        if self.config.password_require_numbers and not re.search(r'\d', password):
            errors.append("密码必须包含数字")
        elif re.search(r'\d', password):
            score += 20
        
        # 特殊字符检查
        if self.config.password_require_symbols and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("密码必须包含特殊字符")
        elif re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 20
        
        # 常见密码检查
        common_passwords = ["password", "123456", "admin", "root", "qwerty"]
        if password.lower() in common_passwords:
            errors.append("不能使用常见密码")
            score = max(0, score - 50)
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "score": min(score, 100),
            "strength": self._get_password_strength(score)
        }
    
    def _get_password_strength(self, score: int) -> str:
        """获取密码强度等级"""
        if score >= 80:
            return "强"
        elif score >= 60:
            return "中等"
        elif score >= 40:
            return "弱"
        else:
            return "很弱"
    
    def hash_password(self, password: str) -> str:
        """哈希密码"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """验证密码"""
        try:
            salt, stored_hash = hashed_password.split(':')
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return password_hash.hex() == stored_hash
        except:
            return False
    
    def record_login_attempt(self, ip_address: str, username: str, success: bool, user_agent: str = ""):
        """记录登录尝试"""
        attempt = LoginAttempt(
            ip_address=ip_address,
            username=username,
            success=success,
            timestamp=datetime.utcnow(),
            user_agent=user_agent
        )
        
        self.login_attempts[ip_address].append(attempt)
        
        # 清理旧记录
        cutoff_time = datetime.utcnow() - timedelta(minutes=self.config.lockout_duration_minutes)
        self.login_attempts[ip_address] = [
            a for a in self.login_attempts[ip_address] 
            if a.timestamp > cutoff_time
        ]
        
        # 检查是否需要锁定
        if not success:
            failed_attempts = [a for a in self.login_attempts[ip_address] if not a.success]
            if len(failed_attempts) >= self.config.max_login_attempts:
                self._block_ip_temporarily(ip_address, "多次登录失败")
                self._log_security_event(
                    "login_brute_force",
                    "high",
                    ip_address,
                    user_agent,
                    f"IP {ip_address} 多次登录失败，已临时封禁",
                    {"username": username, "attempts": len(failed_attempts)}
                )
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """检查IP是否被封禁"""
        return ip_address in self.blocked_ips
    
    def is_ip_rate_limited(self, ip_address: str, endpoint: str) -> bool:
        """检查IP是否被速率限制"""
        key = f"{ip_address}:{endpoint}"
        now = datetime.utcnow()
        
        if key in self.rate_limit_records:
            record = self.rate_limit_records[key]
            window_end = record.window_start + timedelta(minutes=self.config.rate_limit_window_minutes)
            
            if now < window_end:
                if record.request_count >= self.config.rate_limit_requests:
                    return True
                else:
                    record.request_count += 1
                    return False
            else:
                # 新窗口
                self.rate_limit_records[key] = RateLimitRecord(
                    ip_address=ip_address,
                    endpoint=endpoint,
                    request_count=1,
                    window_start=now,
                    blocked=False
                )
                return False
        else:
            # 首次请求
            self.rate_limit_records[key] = RateLimitRecord(
                ip_address=ip_address,
                endpoint=endpoint,
                request_count=1,
                window_start=now,
                blocked=False
            )
            return False
    
    def _block_ip_temporarily(self, ip_address: str, reason: str):
        """临时封禁IP"""
        self.blocked_ips.add(ip_address)
        # 这里应该设置定时器在lockout_duration_minutes后解封
        # 简化实现，实际应该使用任务队列
    
    def _log_security_event(self, event_type: str, severity: str, source_ip: str, 
                           user_agent: str, description: str, details: Dict[str, Any]):
        """记录安全事件"""
        event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            source_ip=source_ip,
            user_agent=user_agent,
            description=description,
            details=details,
            timestamp=datetime.utcnow()
        )
        
        self.security_events.append(event)
        
        # 保持最近1000个事件
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]
    
    def analyze_security_threats(self) -> Dict[str, Any]:
        """分析安全威胁"""
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        
        recent_events = [e for e in self.security_events if e.timestamp > last_24h]
        
        # 统计事件类型
        event_types = defaultdict(int)
        severity_counts = defaultdict(int)
        source_ips = defaultdict(int)
        
        for event in recent_events:
            event_types[event.event_type] += 1
            severity_counts[event.severity] += 1
            source_ips[event.source_ip] += 1
        
        # 识别可疑IP
        suspicious_ips = [ip for ip, count in source_ips.items() if count > 10]
        
        # 计算威胁等级
        threat_level = self._calculate_threat_level(recent_events)
        
        return {
            "threat_level": threat_level,
            "total_events_24h": len(recent_events),
            "event_types": dict(event_types),
            "severity_distribution": dict(severity_counts),
            "suspicious_ips": suspicious_ips,
            "blocked_ips": list(self.blocked_ips),
            "top_source_ips": dict(sorted(source_ips.items(), key=lambda x: x[1], reverse=True)[:10])
        }
    
    def _calculate_threat_level(self, events: List[SecurityEvent]) -> str:
        """计算威胁等级"""
        if not events:
            return "low"
        
        critical_events = [e for e in events if e.severity == "critical"]
        high_events = [e for e in events if e.severity == "high"]
        
        if len(critical_events) > 5:
            return "critical"
        elif len(critical_events) > 0 or len(high_events) > 10:
            return "high"
        elif len(high_events) > 0:
            return "medium"
        else:
            return "low"
    
    def get_security_recommendations(self) -> List[str]:
        """获取安全建议"""
        recommendations = []
        
        analysis = self.analyze_security_threats()
        
        if analysis["threat_level"] in ["high", "critical"]:
            recommendations.append("检测到高威胁活动，建议立即检查安全日志")
        
        if len(analysis["suspicious_ips"]) > 0:
            recommendations.append(f"发现{len(analysis['suspicious_ips'])}个可疑IP，建议加强监控")
        
        if analysis["total_events_24h"] > 100:
            recommendations.append("安全事件频率较高，建议检查系统配置")
        
        # 检查密码策略
        if not self.config.password_require_symbols:
            recommendations.append("建议启用密码特殊字符要求")
        
        if self.config.max_login_attempts > 5:
            recommendations.append("建议降低最大登录尝试次数")
        
        return recommendations
    
    def generate_security_report(self) -> Dict[str, Any]:
        """生成安全报告"""
        analysis = self.analyze_security_threats()
        recommendations = self.get_security_recommendations()
        
        # 最近的安全事件
        recent_events = sorted(
            [e for e in self.security_events if e.timestamp > datetime.utcnow() - timedelta(hours=24)],
            key=lambda x: x.timestamp,
            reverse=True
        )[:10]
        
        return {
            "report_generated_at": datetime.utcnow().isoformat(),
            "threat_analysis": analysis,
            "security_recommendations": recommendations,
            "recent_security_events": [e.dict() for e in recent_events],
            "security_config": {
                "max_login_attempts": self.config.max_login_attempts,
                "lockout_duration_minutes": self.config.lockout_duration_minutes,
                "rate_limit_requests": self.config.rate_limit_requests,
                "password_policy": {
                    "min_length": self.config.password_min_length,
                    "require_uppercase": self.config.password_require_uppercase,
                    "require_lowercase": self.config.password_require_lowercase,
                    "require_numbers": self.config.password_require_numbers,
                    "require_symbols": self.config.password_require_symbols
                }
            }
        }


class SecurityMiddleware:
    """安全中间件"""
    
    def __init__(self, security_manager: SecurityManager):
        self.security_manager = security_manager
    
    async def __call__(self, request: Request, call_next):
        """中间件处理"""
        client_ip = self._get_client_ip(request)
        
        # 检查IP封禁
        if self.security_manager.is_ip_blocked(client_ip):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="IP地址已被封禁"
            )
        
        # 检查速率限制
        endpoint = request.url.path
        if self.security_manager.is_ip_rate_limited(client_ip, endpoint):
            self.security_manager._log_security_event(
                "rate_limit_exceeded",
                "medium",
                client_ip,
                request.headers.get("user-agent", ""),
                f"IP {client_ip} 超过速率限制",
                {"endpoint": endpoint}
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="请求过于频繁，请稍后再试"
            )
        
        # 安全头检查
        self._add_security_headers(request)
        
        response = await call_next(request)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP"""
        # 检查代理头
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _add_security_headers(self, request: Request):
        """添加安全头"""
        # 这里可以添加安全相关的请求头检查
        pass


def require_strong_password(func):
    """强密码要求装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 这里应该检查密码强度
        return func(*args, **kwargs)
    return wrapper


def security_audit_log(action: str):
    """安全审计日志装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            try:
                result = func(*args, **kwargs)
                # 记录成功的安全操作
                print(f"安全审计: {action} 执行成功 - {start_time.isoformat()}")
                return result
            except Exception as e:
                # 记录失败的安全操作
                print(f"安全审计: {action} 执行失败 - {start_time.isoformat()} - 错误: {str(e)}")
                raise
        return wrapper
    return decorator


# 全局安全管理器实例
security_config = SecurityConfig()
security_manager = SecurityManager(security_config)
security_middleware = SecurityMiddleware(security_manager)
