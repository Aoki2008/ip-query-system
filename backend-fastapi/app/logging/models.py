"""
日志分析数据模型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Index
from pydantic import BaseModel, Field

from ..database import Base


class LogLevel(str, Enum):
    """日志级别枚举"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(str, Enum):
    """日志分类枚举"""
    SYSTEM = "system"
    API = "api"
    DATABASE = "database"
    CACHE = "cache"
    AUTH = "auth"
    SECURITY = "security"
    PERFORMANCE = "performance"
    USER = "user"


class SystemLog(Base):
    """系统日志表"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    message = Column(Text, nullable=False)
    module = Column(String(100), index=True)  # 模块名称
    function = Column(String(100))  # 函数名称
    line_number = Column(Integer)  # 行号
    user_id = Column(Integer, index=True)  # 用户ID
    session_id = Column(String(100), index=True)  # 会话ID
    ip_address = Column(String(45), index=True)  # IP地址
    user_agent = Column(String(500))  # 用户代理
    request_id = Column(String(100), index=True)  # 请求ID
    trace_id = Column(String(100), index=True)  # 追踪ID
    extra_data = Column(JSON)  # 额外数据
    stack_trace = Column(Text)  # 堆栈跟踪
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # 创建复合索引
    __table_args__ = (
        Index('idx_level_timestamp', 'level', 'timestamp'),
        Index('idx_category_timestamp', 'category', 'timestamp'),
        Index('idx_module_timestamp', 'module', 'timestamp'),
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
    )


class LogAlert(Base):
    """日志告警表"""
    __tablename__ = "log_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(100), nullable=False, index=True)
    level = Column(String(20), nullable=False)
    category = Column(String(50), nullable=False)
    pattern = Column(String(500))  # 匹配模式
    threshold = Column(Integer, default=1)  # 阈值
    time_window = Column(Integer, default=300)  # 时间窗口(秒)
    triggered_count = Column(Integer, default=0)  # 触发次数
    last_triggered = Column(DateTime)  # 最后触发时间
    is_active = Column(Boolean, default=True)
    notification_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LogStatistic(Base):
    """日志统计表"""
    __tablename__ = "log_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)  # 统计日期(按小时)
    level = Column(String(20), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    count = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    unique_ips = Column(Integer, default=0)
    top_modules = Column(JSON)  # 热门模块
    top_messages = Column(JSON)  # 热门消息
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_date_level', 'date', 'level'),
        Index('idx_date_category', 'date', 'category'),
    )


# Pydantic模型

class LogEntry(BaseModel):
    """日志条目模型"""
    level: LogLevel
    category: LogCategory
    message: str
    module: Optional[str] = None
    function: Optional[str] = None
    line_number: Optional[int] = None
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None


class LogEntryResponse(BaseModel):
    """日志条目响应模型"""
    id: int
    level: str
    category: str
    message: str
    module: Optional[str]
    function: Optional[str]
    line_number: Optional[int]
    user_id: Optional[int]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    request_id: Optional[str]
    trace_id: Optional[str]
    extra_data: Optional[Dict[str, Any]]
    stack_trace: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class LogQuery(BaseModel):
    """日志查询模型"""
    level: Optional[LogLevel] = None
    category: Optional[LogCategory] = None
    module: Optional[str] = None
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    keyword: Optional[str] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


class LogStatistics(BaseModel):
    """日志统计模型"""
    total_logs: int
    error_logs: int
    warning_logs: int
    info_logs: int
    debug_logs: int
    critical_logs: int
    error_rate: float
    top_categories: List[Dict[str, Any]]
    top_modules: List[Dict[str, Any]]
    top_users: List[Dict[str, Any]]
    hourly_distribution: List[Dict[str, Any]]


class LogTrend(BaseModel):
    """日志趋势模型"""
    timestamp: datetime
    total_count: int
    error_count: int
    warning_count: int
    info_count: int
    debug_count: int
    critical_count: int


class LogAlertRule(BaseModel):
    """日志告警规则模型"""
    rule_name: str = Field(..., max_length=100)
    level: LogLevel
    category: LogCategory
    pattern: Optional[str] = Field(None, max_length=500)
    threshold: int = Field(1, ge=1)
    time_window: int = Field(300, ge=60, le=3600)  # 1分钟到1小时
    is_active: bool = True


class LogAlertResponse(BaseModel):
    """日志告警响应模型"""
    id: int
    rule_name: str
    level: str
    category: str
    pattern: Optional[str]
    threshold: int
    time_window: int
    triggered_count: int
    last_triggered: Optional[datetime]
    is_active: bool
    notification_sent: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LogAnalysis(BaseModel):
    """日志分析模型"""
    time_range: str
    total_logs: int
    error_analysis: Dict[str, Any]
    performance_analysis: Dict[str, Any]
    security_analysis: Dict[str, Any]
    user_behavior: Dict[str, Any]
    system_health: Dict[str, Any]
    recommendations: List[str]


class LogExport(BaseModel):
    """日志导出模型"""
    format: str = Field("json", pattern="^(json|csv|txt)$")
    query: LogQuery
    include_stack_trace: bool = False
    max_records: int = Field(10000, ge=1, le=100000)


class LogDashboard(BaseModel):
    """日志仪表板模型"""
    statistics: LogStatistics
    recent_errors: List[LogEntryResponse]
    trends: List[LogTrend]
    active_alerts: List[LogAlertResponse]
    system_health_score: int
    recommendations: List[str]


class LogSearchResult(BaseModel):
    """日志搜索结果模型"""
    total: int
    logs: List[LogEntryResponse]
    facets: Dict[str, List[Dict[str, Any]]]  # 分面搜索结果
    suggestions: List[str]  # 搜索建议


class LogRetentionPolicy(BaseModel):
    """日志保留策略模型"""
    level: LogLevel
    retention_days: int = Field(30, ge=1, le=365)
    archive_enabled: bool = False
    compression_enabled: bool = True


class LogConfiguration(BaseModel):
    """日志配置模型"""
    global_level: LogLevel = LogLevel.INFO
    categories: Dict[LogCategory, LogLevel]
    retention_policies: List[LogRetentionPolicy]
    alert_rules: List[LogAlertRule]
    export_settings: Dict[str, Any]
    performance_settings: Dict[str, Any]
