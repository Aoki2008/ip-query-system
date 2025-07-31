"""
告警通知数据模型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Float
from pydantic import BaseModel, Field, EmailStr

from ..database import Base


class NotificationType(str, Enum):
    """通知类型枚举"""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DINGTALK = "dingtalk"
    WECHAT = "wechat"


class AlertSeverity(str, Enum):
    """告警严重程度枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """告警状态枚举"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ACKNOWLEDGED = "acknowledged"


class NotificationChannel(Base):
    """通知渠道表"""
    __tablename__ = "notification_channels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    type = Column(String(20), nullable=False, index=True)
    config = Column(JSON, nullable=False)  # 渠道配置
    is_enabled = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    created_by = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AlertRule(Base):
    """告警规则表"""
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    metric_type = Column(String(50), nullable=False, index=True)  # cpu, memory, disk, api_error_rate等
    condition = Column(String(20), nullable=False)  # >, <, >=, <=, ==
    threshold = Column(Float, nullable=False)
    duration = Column(Integer, default=300)  # 持续时间(秒)
    severity = Column(String(20), nullable=False, index=True)
    is_enabled = Column(Boolean, default=True)
    notification_channels = Column(JSON)  # 通知渠道ID列表
    cooldown_period = Column(Integer, default=3600)  # 冷却期(秒)
    tags = Column(JSON)  # 标签
    created_by = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Alert(Base):
    """告警记录表"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, nullable=False, index=True)
    rule_name = Column(String(100), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    severity = Column(String(20), nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True, default="active")
    metric_value = Column(Float)  # 触发时的指标值
    threshold = Column(Float)  # 阈值
    started_at = Column(DateTime, nullable=False, index=True)
    resolved_at = Column(DateTime, index=True)
    acknowledged_at = Column(DateTime)
    acknowledged_by = Column(Integer)
    resolved_by = Column(Integer)
    notification_sent = Column(Boolean, default=False)
    notification_count = Column(Integer, default=0)
    last_notification = Column(DateTime)
    tags = Column(JSON)
    extra_data = Column(JSON)


class NotificationLog(Base):
    """通知日志表"""
    __tablename__ = "notification_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, nullable=False, index=True)
    channel_id = Column(Integer, nullable=False, index=True)
    channel_type = Column(String(20), nullable=False)
    recipient = Column(String(200), nullable=False)
    subject = Column(String(200))
    content = Column(Text)
    status = Column(String(20), nullable=False, index=True)  # sent, failed, pending
    error_message = Column(Text)
    sent_at = Column(DateTime, default=datetime.utcnow, index=True)
    response_data = Column(JSON)


# Pydantic模型

class NotificationChannelCreate(BaseModel):
    """创建通知渠道模型"""
    name: str = Field(..., max_length=100)
    type: NotificationType
    config: Dict[str, Any]
    is_enabled: bool = True
    is_default: bool = False


class NotificationChannelResponse(BaseModel):
    """通知渠道响应模型"""
    id: int
    name: str
    type: str
    config: Dict[str, Any]
    is_enabled: bool
    is_default: bool
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AlertRuleCreate(BaseModel):
    """创建告警规则模型"""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    metric_type: str = Field(..., max_length=50)
    condition: str = Field(..., pattern="^(>|<|>=|<=|==)$")
    threshold: float
    duration: int = Field(300, ge=60, le=3600)
    severity: AlertSeverity
    is_enabled: bool = True
    notification_channels: List[int] = []
    cooldown_period: int = Field(3600, ge=300, le=86400)
    tags: Optional[Dict[str, str]] = None


class AlertRuleResponse(BaseModel):
    """告警规则响应模型"""
    id: int
    name: str
    description: Optional[str]
    metric_type: str
    condition: str
    threshold: float
    duration: int
    severity: str
    is_enabled: bool
    notification_channels: Optional[List[int]]
    cooldown_period: int
    tags: Optional[Dict[str, str]]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    """告警响应模型"""
    id: int
    rule_id: int
    rule_name: str
    title: str
    description: Optional[str]
    severity: str
    status: str
    metric_value: Optional[float]
    threshold: Optional[float]
    started_at: datetime
    resolved_at: Optional[datetime]
    acknowledged_at: Optional[datetime]
    acknowledged_by: Optional[int]
    resolved_by: Optional[int]
    notification_sent: bool
    notification_count: int
    last_notification: Optional[datetime]
    tags: Optional[Dict[str, Any]]
    extra_data: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class NotificationLogResponse(BaseModel):
    """通知日志响应模型"""
    id: int
    alert_id: int
    channel_id: int
    channel_type: str
    recipient: str
    subject: Optional[str]
    content: Optional[str]
    status: str
    error_message: Optional[str]
    sent_at: datetime
    response_data: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class AlertQuery(BaseModel):
    """告警查询模型"""
    severity: Optional[AlertSeverity] = None
    status: Optional[AlertStatus] = None
    rule_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


class AlertStatistics(BaseModel):
    """告警统计模型"""
    total_alerts: int
    active_alerts: int
    resolved_alerts: int
    critical_alerts: int
    high_alerts: int
    medium_alerts: int
    low_alerts: int
    alert_rate: float
    resolution_time_avg: float
    top_rules: List[Dict[str, Any]]
    severity_distribution: Dict[str, int]
    status_distribution: Dict[str, int]


class NotificationTest(BaseModel):
    """通知测试模型"""
    channel_id: int
    recipient: str
    subject: str = "测试通知"
    content: str = "这是一条测试通知消息"


class AlertDashboard(BaseModel):
    """告警仪表板模型"""
    statistics: AlertStatistics
    recent_alerts: List[AlertResponse]
    active_rules: List[AlertRuleResponse]
    notification_channels: List[NotificationChannelResponse]
    system_health: Dict[str, Any]


class EmailConfig(BaseModel):
    """邮件配置模型"""
    smtp_server: str
    smtp_port: int = 587
    username: str
    password: str
    use_tls: bool = True
    from_email: EmailStr
    from_name: str = "系统告警"


class WebhookConfig(BaseModel):
    """Webhook配置模型"""
    url: str
    method: str = "POST"
    headers: Optional[Dict[str, str]] = None
    timeout: int = 30
    retry_count: int = 3


class SlackConfig(BaseModel):
    """Slack配置模型"""
    webhook_url: str
    channel: str
    username: str = "AlertBot"
    icon_emoji: str = ":warning:"


class DingTalkConfig(BaseModel):
    """钉钉配置模型"""
    webhook_url: str
    secret: Optional[str] = None
    at_mobiles: Optional[List[str]] = None
    at_all: bool = False


class NotificationTemplate(BaseModel):
    """通知模板模型"""
    type: NotificationType
    subject_template: str
    content_template: str
    variables: List[str]


class AlertEscalation(BaseModel):
    """告警升级模型"""
    rule_id: int
    escalation_levels: List[Dict[str, Any]]
    escalation_interval: int = 1800  # 升级间隔(秒)


class MaintenanceWindow(BaseModel):
    """维护窗口模型"""
    name: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    affected_rules: List[int]
    suppress_notifications: bool = True
