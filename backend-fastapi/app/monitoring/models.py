"""
系统监控数据模型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, JSON
from pydantic import BaseModel, Field

from ..database import Base


class MetricType(str, Enum):
    """指标类型枚举"""
    SYSTEM = "system"           # 系统指标
    API = "api"                # API指标
    DATABASE = "database"       # 数据库指标
    NETWORK = "network"         # 网络指标
    APPLICATION = "application" # 应用指标


class AlertLevel(str, Enum):
    """告警级别枚举"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SystemMetric(Base):
    """系统指标表"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_type = Column(String(50), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20))
    extra_data = Column(JSON)  # 额外的元数据
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class APIMetric(Base):
    """API指标表"""
    __tablename__ = "api_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(200), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time = Column(Float, nullable=False)  # 毫秒
    request_size = Column(Integer)  # 字节
    response_size = Column(Integer)  # 字节
    user_agent = Column(String(500))
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class SystemAlert(Base):
    """系统告警表"""
    __tablename__ = "system_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False, index=True)
    level = Column(String(20), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    metric_name = Column(String(100))
    metric_value = Column(Float)
    threshold_value = Column(Float)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# Pydantic模型

class SystemStatus(BaseModel):
    """系统状态模型"""
    cpu_percent: float = Field(..., description="CPU使用率")
    memory_percent: float = Field(..., description="内存使用率")
    memory_used: int = Field(..., description="已使用内存(MB)")
    memory_total: int = Field(..., description="总内存(MB)")
    disk_percent: float = Field(..., description="磁盘使用率")
    disk_used: int = Field(..., description="已使用磁盘(GB)")
    disk_total: int = Field(..., description="总磁盘(GB)")
    network_sent: int = Field(..., description="网络发送(MB)")
    network_recv: int = Field(..., description="网络接收(MB)")
    uptime: int = Field(..., description="运行时间(秒)")
    load_average: List[float] = Field(..., description="负载平均值")
    process_count: int = Field(..., description="进程数量")
    timestamp: datetime = Field(..., description="时间戳")


class ServiceStatus(BaseModel):
    """服务状态模型"""
    name: str = Field(..., description="服务名称")
    status: str = Field(..., description="服务状态")
    pid: Optional[int] = Field(None, description="进程ID")
    cpu_percent: float = Field(..., description="CPU使用率")
    memory_percent: float = Field(..., description="内存使用率")
    memory_mb: float = Field(..., description="内存使用(MB)")
    uptime: int = Field(..., description="运行时间(秒)")


class APIStats(BaseModel):
    """API统计模型"""
    total_requests: int = Field(..., description="总请求数")
    success_requests: int = Field(..., description="成功请求数")
    error_requests: int = Field(..., description="错误请求数")
    avg_response_time: float = Field(..., description="平均响应时间(ms)")
    max_response_time: float = Field(..., description="最大响应时间(ms)")
    min_response_time: float = Field(..., description="最小响应时间(ms)")
    requests_per_minute: float = Field(..., description="每分钟请求数")
    error_rate: float = Field(..., description="错误率")


class EndpointStats(BaseModel):
    """端点统计模型"""
    endpoint: str = Field(..., description="端点路径")
    method: str = Field(..., description="HTTP方法")
    request_count: int = Field(..., description="请求次数")
    avg_response_time: float = Field(..., description="平均响应时间(ms)")
    error_count: int = Field(..., description="错误次数")
    error_rate: float = Field(..., description="错误率")
    last_request: datetime = Field(..., description="最后请求时间")


class AlertCreate(BaseModel):
    """创建告警模型"""
    alert_type: str = Field(..., max_length=50)
    level: AlertLevel
    title: str = Field(..., max_length=200)
    message: str
    metric_name: Optional[str] = Field(None, max_length=100)
    metric_value: Optional[float] = None
    threshold_value: Optional[float] = None


class AlertResponse(BaseModel):
    """告警响应模型"""
    id: int
    alert_type: str
    level: AlertLevel
    title: str
    message: str
    metric_name: Optional[str]
    metric_value: Optional[float]
    threshold_value: Optional[float]
    is_resolved: bool
    resolved_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MetricCreate(BaseModel):
    """创建指标模型"""
    metric_type: MetricType
    metric_name: str = Field(..., max_length=100)
    metric_value: float
    metric_unit: Optional[str] = Field(None, max_length=20)
    extra_data: Optional[Dict[str, Any]] = None


class MetricResponse(BaseModel):
    """指标响应模型"""
    id: int
    metric_type: MetricType
    metric_name: str
    metric_value: float
    metric_unit: Optional[str]
    extra_data: Optional[Dict[str, Any]]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class MonitoringDashboard(BaseModel):
    """监控仪表板模型"""
    system_status: SystemStatus
    service_status: List[ServiceStatus]
    api_stats: APIStats
    recent_alerts: List[AlertResponse]
    top_endpoints: List[EndpointStats]


class PerformanceMetrics(BaseModel):
    """性能指标模型"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    api_response_time: float
    active_connections: int


class SystemHealth(BaseModel):
    """系统健康状态模型"""
    overall_status: str = Field(..., description="总体状态")
    cpu_status: str = Field(..., description="CPU状态")
    memory_status: str = Field(..., description="内存状态")
    disk_status: str = Field(..., description="磁盘状态")
    network_status: str = Field(..., description="网络状态")
    service_status: str = Field(..., description="服务状态")
    score: int = Field(..., description="健康评分(0-100)")
    issues: List[str] = Field(..., description="发现的问题")
    recommendations: List[str] = Field(..., description="优化建议")


class AlertRule(BaseModel):
    """告警规则模型"""
    name: str = Field(..., description="规则名称")
    metric_name: str = Field(..., description="指标名称")
    operator: str = Field(..., description="操作符(>, <, >=, <=, ==)")
    threshold: float = Field(..., description="阈值")
    level: AlertLevel = Field(..., description="告警级别")
    enabled: bool = Field(True, description="是否启用")
    description: Optional[str] = Field(None, description="规则描述")
