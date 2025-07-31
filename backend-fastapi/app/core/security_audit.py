"""
安全审计日志模块
记录和监控安全相关事件
"""
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path

from ..config import settings


class SecurityEventType(Enum):
    """安全事件类型"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGIN_BLOCKED = "login_blocked"
    PASSWORD_CHANGE = "password_change"
    PERMISSION_DENIED = "permission_denied"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_ERROR = "system_error"
    SECURITY_VIOLATION = "security_violation"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    CSRF_ATTACK = "csrf_attack"
    XSS_ATTEMPT = "xss_attempt"
    SQL_INJECTION_ATTEMPT = "sql_injection_attempt"
    FILE_ACCESS = "file_access"
    API_ABUSE = "api_abuse"
    CONFIGURATION_CHANGE = "configuration_change"
    BACKUP_CREATED = "backup_created"
    BACKUP_RESTORED = "backup_restored"
    ENCRYPTION_ERROR = "encryption_error"
    CERTIFICATE_EXPIRY = "certificate_expiry"


class SecurityLevel(Enum):
    """安全级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """安全事件数据结构"""
    event_type: SecurityEventType
    level: SecurityLevel
    timestamp: datetime
    user_id: Optional[str] = None
    username: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    message: str = ""
    details: Dict[str, Any] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


class SecurityAuditLogger:
    """安全审计日志记录器"""
    
    def __init__(self, log_file: Optional[str] = None):
        """
        初始化审计日志记录器
        
        Args:
            log_file: 日志文件路径
        """
        self.log_file = log_file or getattr(settings, 'security_log_file', '/var/log/security.log')
        self.ensure_log_directory()
        
        # 事件计数器
        self.event_counters: Dict[SecurityEventType, int] = {}
        
        # 最近事件缓存
        self.recent_events: List[SecurityEvent] = []
        self.max_recent_events = 1000
    
    def ensure_log_directory(self):
        """确保日志目录存在"""
        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log_event(self, event: SecurityEvent):
        """
        记录安全事件
        
        Args:
            event: 安全事件
        """
        # 更新计数器
        self.event_counters[event.event_type] = self.event_counters.get(event.event_type, 0) + 1
        
        # 添加到最近事件缓存
        self.recent_events.append(event)
        if len(self.recent_events) > self.max_recent_events:
            self.recent_events.pop(0)
        
        # 写入日志文件
        self._write_to_file(event)
        
        # 检查是否需要告警
        self._check_alert_conditions(event)
    
    def _write_to_file(self, event: SecurityEvent):
        """写入日志文件"""
        try:
            log_entry = {
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type.value,
                "level": event.level.value,
                "user_id": event.user_id,
                "username": event.username,
                "ip_address": event.ip_address,
                "user_agent": event.user_agent,
                "endpoint": event.endpoint,
                "method": event.method,
                "status_code": event.status_code,
                "message": event.message,
                "details": event.details,
                "session_id": event.session_id,
                "request_id": event.request_id
            }
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                
        except Exception as e:
            # 如果写入失败，至少打印到控制台
            print(f"安全日志写入失败: {e}")
            print(f"事件: {event}")
    
    def _check_alert_conditions(self, event: SecurityEvent):
        """检查告警条件"""
        # 关键安全事件立即告警
        critical_events = {
            SecurityEventType.SQL_INJECTION_ATTEMPT,
            SecurityEventType.XSS_ATTEMPT,
            SecurityEventType.CSRF_ATTACK,
            SecurityEventType.SECURITY_VIOLATION
        }
        
        if event.event_type in critical_events or event.level == SecurityLevel.CRITICAL:
            self._send_alert(event)
        
        # 检查频率异常
        self._check_frequency_anomalies(event)
    
    def _send_alert(self, event: SecurityEvent):
        """发送安全告警"""
        # 这里可以集成邮件、短信、Webhook等告警方式
        alert_message = f"安全告警: {event.event_type.value} - {event.message}"
        print(f"🚨 {alert_message}")
        
        # TODO: 实现实际的告警发送逻辑
        # - 发送邮件
        # - 调用Webhook
        # - 发送到监控系统
    
    def _check_frequency_anomalies(self, event: SecurityEvent):
        """检查频率异常"""
        # 检查最近5分钟内的同类事件
        now = datetime.now(timezone.utc)
        recent_same_events = [
            e for e in self.recent_events
            if e.event_type == event.event_type and
            (now - e.timestamp).total_seconds() < 300  # 5分钟
        ]
        
        # 如果同类事件过多，发送告警
        if len(recent_same_events) > 10:
            alert_event = SecurityEvent(
                event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                level=SecurityLevel.HIGH,
                timestamp=now,
                message=f"检测到异常频率的{event.event_type.value}事件",
                details={"count": len(recent_same_events), "timeframe": "5分钟"}
            )
            self._send_alert(alert_event)
    
    def get_event_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """
        获取事件统计信息
        
        Args:
            hours: 统计时间范围（小时）
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(hours=hours)
        
        recent_events = [
            e for e in self.recent_events
            if e.timestamp >= cutoff_time
        ]
        
        # 按事件类型统计
        type_counts = {}
        for event in recent_events:
            type_counts[event.event_type.value] = type_counts.get(event.event_type.value, 0) + 1
        
        # 按安全级别统计
        level_counts = {}
        for event in recent_events:
            level_counts[event.level.value] = level_counts.get(event.level.value, 0) + 1
        
        # 按IP地址统计
        ip_counts = {}
        for event in recent_events:
            if event.ip_address:
                ip_counts[event.ip_address] = ip_counts.get(event.ip_address, 0) + 1
        
        return {
            "timeframe_hours": hours,
            "total_events": len(recent_events),
            "event_types": type_counts,
            "security_levels": level_counts,
            "top_ips": dict(sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "generated_at": now.isoformat()
        }
    
    def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取最近的安全事件
        
        Args:
            limit: 返回事件数量限制
            
        Returns:
            List[Dict[str, Any]]: 最近的安全事件列表
        """
        recent = self.recent_events[-limit:] if limit < len(self.recent_events) else self.recent_events
        return [asdict(event) for event in reversed(recent)]


# 全局审计日志记录器实例
_audit_logger = None


def get_audit_logger() -> SecurityAuditLogger:
    """获取全局审计日志记录器实例"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = SecurityAuditLogger()
    return _audit_logger


def log_security_event(
    event_type: SecurityEventType,
    level: SecurityLevel,
    message: str,
    user_id: Optional[str] = None,
    username: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    endpoint: Optional[str] = None,
    method: Optional[str] = None,
    status_code: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None,
    request_id: Optional[str] = None
):
    """
    记录安全事件的便捷函数
    
    Args:
        event_type: 事件类型
        level: 安全级别
        message: 事件消息
        user_id: 用户ID
        username: 用户名
        ip_address: IP地址
        user_agent: 用户代理
        endpoint: 访问端点
        method: HTTP方法
        status_code: 状态码
        details: 详细信息
        session_id: 会话ID
        request_id: 请求ID
    """
    event = SecurityEvent(
        event_type=event_type,
        level=level,
        timestamp=datetime.now(timezone.utc),
        user_id=user_id,
        username=username,
        ip_address=ip_address,
        user_agent=user_agent,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        message=message,
        details=details or {},
        session_id=session_id,
        request_id=request_id
    )
    
    get_audit_logger().log_event(event)


# 便捷的日志记录函数
def log_login_success(username: str, ip_address: str, **kwargs):
    """记录登录成功事件"""
    log_security_event(
        SecurityEventType.LOGIN_SUCCESS,
        SecurityLevel.LOW,
        f"用户 {username} 登录成功",
        username=username,
        ip_address=ip_address,
        **kwargs
    )


def log_login_failure(username: str, ip_address: str, reason: str = "", **kwargs):
    """记录登录失败事件"""
    log_security_event(
        SecurityEventType.LOGIN_FAILURE,
        SecurityLevel.MEDIUM,
        f"用户 {username} 登录失败: {reason}",
        username=username,
        ip_address=ip_address,
        details={"failure_reason": reason},
        **kwargs
    )


def log_permission_denied(username: str, endpoint: str, ip_address: str, **kwargs):
    """记录权限拒绝事件"""
    log_security_event(
        SecurityEventType.PERMISSION_DENIED,
        SecurityLevel.MEDIUM,
        f"用户 {username} 访问 {endpoint} 被拒绝",
        username=username,
        endpoint=endpoint,
        ip_address=ip_address,
        **kwargs
    )


def log_suspicious_activity(message: str, ip_address: str, **kwargs):
    """记录可疑活动事件"""
    log_security_event(
        SecurityEventType.SUSPICIOUS_ACTIVITY,
        SecurityLevel.HIGH,
        message,
        ip_address=ip_address,
        **kwargs
    )
