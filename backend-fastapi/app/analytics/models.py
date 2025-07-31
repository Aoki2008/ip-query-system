"""
API性能统计数据模型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, JSON, Index
from pydantic import BaseModel, Field

from ..database import Base


class APICallLog(Base):
    """API调用日志表"""
    __tablename__ = "api_call_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(200), nullable=False, index=True)
    method = Column(String(10), nullable=False, index=True)
    status_code = Column(Integer, nullable=False, index=True)
    response_time_ms = Column(Float, nullable=False)  # 响应时间(毫秒)
    request_size = Column(Integer, default=0)  # 请求大小(字节)
    response_size = Column(Integer, default=0)  # 响应大小(字节)
    user_agent = Column(String(500))
    ip_address = Column(String(45), index=True)
    user_id = Column(Integer, index=True)  # 用户ID(如果已认证)
    error_message = Column(Text)  # 错误信息
    request_data = Column(JSON)  # 请求数据摘要
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # 创建复合索引
    __table_args__ = (
        Index('idx_endpoint_timestamp', 'endpoint', 'timestamp'),
        Index('idx_status_timestamp', 'status_code', 'timestamp'),
        Index('idx_ip_timestamp', 'ip_address', 'timestamp'),
    )


class APIPerformanceMetric(Base):
    """API性能指标聚合表"""
    __tablename__ = "api_performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(200), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    date = Column(DateTime, nullable=False, index=True)  # 统计日期(按小时聚合)
    
    # 调用统计
    total_calls = Column(Integer, default=0)
    success_calls = Column(Integer, default=0)
    error_calls = Column(Integer, default=0)
    
    # 响应时间统计
    avg_response_time = Column(Float, default=0.0)
    min_response_time = Column(Float, default=0.0)
    max_response_time = Column(Float, default=0.0)
    p95_response_time = Column(Float, default=0.0)  # 95分位数
    p99_response_time = Column(Float, default=0.0)  # 99分位数
    
    # 数据量统计
    total_request_size = Column(Integer, default=0)
    total_response_size = Column(Integer, default=0)
    avg_request_size = Column(Float, default=0.0)
    avg_response_size = Column(Float, default=0.0)
    
    # 错误统计
    error_rate = Column(Float, default=0.0)  # 错误率百分比
    timeout_count = Column(Integer, default=0)
    server_error_count = Column(Integer, default=0)
    client_error_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_endpoint_date', 'endpoint', 'date'),
    )


class UserActivityLog(Base):
    """用户活动日志表"""
    __tablename__ = "user_activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    username = Column(String(50), index=True)
    action = Column(String(100), nullable=False, index=True)
    resource = Column(String(100), index=True)
    ip_address = Column(String(45), index=True)
    user_agent = Column(String(500))
    details = Column(JSON)  # 活动详情
    success = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


# Pydantic模型

class APICallLogCreate(BaseModel):
    """创建API调用日志模型"""
    endpoint: str = Field(..., max_length=200)
    method: str = Field(..., max_length=10)
    status_code: int
    response_time_ms: float
    request_size: int = 0
    response_size: int = 0
    user_agent: Optional[str] = Field(None, max_length=500)
    ip_address: Optional[str] = Field(None, max_length=45)
    user_id: Optional[int] = None
    error_message: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None


class APICallLogResponse(BaseModel):
    """API调用日志响应模型"""
    id: int
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    request_size: int
    response_size: int
    user_agent: Optional[str]
    ip_address: Optional[str]
    user_id: Optional[int]
    error_message: Optional[str]
    timestamp: datetime
    
    class Config:
        orm_mode = True


class APIPerformanceStats(BaseModel):
    """API性能统计模型"""
    endpoint: str
    method: str
    total_calls: int
    success_calls: int
    error_calls: int
    error_rate: float
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    calls_per_hour: float
    avg_request_size: float
    avg_response_size: float


class APITrendData(BaseModel):
    """API趋势数据模型"""
    timestamp: datetime
    total_calls: int
    avg_response_time: float
    error_rate: float
    success_rate: float


class TopEndpointsStats(BaseModel):
    """热门端点统计模型"""
    endpoint: str
    method: str
    total_calls: int
    avg_response_time: float
    error_rate: float
    last_called: datetime


class ErrorAnalysis(BaseModel):
    """错误分析模型"""
    status_code: int
    count: int
    percentage: float
    endpoints: List[str]
    recent_errors: List[str]


class UserActivityStats(BaseModel):
    """用户活动统计模型"""
    user_id: int
    username: str
    total_actions: int
    unique_resources: int
    success_rate: float
    last_activity: datetime
    top_actions: List[Dict[str, Any]]


class PerformanceSummary(BaseModel):
    """性能摘要模型"""
    total_requests: int
    total_errors: int
    avg_response_time: float
    requests_per_minute: float
    error_rate: float
    uptime_percentage: float
    peak_hour: str
    slowest_endpoint: str
    most_active_user: str


class APIAnalyticsDashboard(BaseModel):
    """API分析仪表板模型"""
    summary: PerformanceSummary
    top_endpoints: List[TopEndpointsStats]
    error_analysis: List[ErrorAnalysis]
    trend_data: List[APITrendData]
    user_activity: List[UserActivityStats]
    performance_alerts: List[str]


class TimeRange(str, Enum):
    """时间范围枚举"""
    LAST_HOUR = "1h"
    LAST_6_HOURS = "6h"
    LAST_24_HOURS = "24h"
    LAST_7_DAYS = "7d"
    LAST_30_DAYS = "30d"


class MetricType(str, Enum):
    """指标类型枚举"""
    RESPONSE_TIME = "response_time"
    REQUEST_COUNT = "request_count"
    ERROR_RATE = "error_rate"
    DATA_TRANSFER = "data_transfer"


class AnalyticsQuery(BaseModel):
    """分析查询模型"""
    time_range: TimeRange = TimeRange.LAST_24_HOURS
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    metric_type: MetricType = MetricType.RESPONSE_TIME
    group_by: Optional[str] = None  # hour, day, endpoint, user
    limit: int = Field(100, ge=1, le=1000)


class RealTimeMetrics(BaseModel):
    """实时指标模型"""
    current_rps: float  # 当前每秒请求数
    current_error_rate: float  # 当前错误率
    avg_response_time_1min: float  # 1分钟平均响应时间
    active_connections: int  # 活跃连接数
    memory_usage: float  # 内存使用率
    cpu_usage: float  # CPU使用率
    timestamp: datetime


class AlertRule(BaseModel):
    """告警规则模型"""
    name: str
    metric: str  # response_time, error_rate, request_count
    operator: str  # >, <, >=, <=, ==
    threshold: float
    duration_minutes: int  # 持续时间
    enabled: bool = True
    notification_channels: List[str] = []  # email, webhook, slack


class PerformanceReport(BaseModel):
    """性能报告模型"""
    report_id: str
    generated_at: datetime
    time_range: TimeRange
    summary: PerformanceSummary
    detailed_stats: List[APIPerformanceStats]
    recommendations: List[str]
    charts_data: Dict[str, Any]
