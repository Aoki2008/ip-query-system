"""
数据管理数据模型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Float, Index
from pydantic import BaseModel, Field, IPvAnyAddress

from ..database import Base


class QueryStatus(str, Enum):
    """查询状态枚举"""
    SUCCESS = "success"
    FAILED = "failed"
    CACHED = "cached"
    RATE_LIMITED = "rate_limited"


class DataSource(str, Enum):
    """数据源枚举"""
    MAXMIND = "maxmind"
    IPAPI = "ipapi"
    IPINFO = "ipinfo"
    CACHE = "cache"
    LOCAL = "local"


class IPQueryRecord(Base):
    """IP查询记录表"""
    __tablename__ = "ip_query_records"
    
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), nullable=False, index=True)
    query_type = Column(String(20), default="single", index=True)  # single, batch, api
    status = Column(String(20), nullable=False, index=True)
    data_source = Column(String(20), nullable=False, index=True)
    
    # 地理位置信息
    country = Column(String(100), index=True)
    country_code = Column(String(10), index=True)
    region = Column(String(100), index=True)
    region_code = Column(String(10))
    city = Column(String(100), index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    timezone = Column(String(50))
    
    # ISP信息
    isp = Column(String(200), index=True)
    organization = Column(String(200))
    asn = Column(String(50), index=True)
    asn_org = Column(String(200))
    
    # 查询信息
    user_agent = Column(String(500))
    client_ip = Column(String(45), index=True)
    referer = Column(String(500))
    response_time_ms = Column(Float)
    cache_hit = Column(Boolean, default=False, index=True)
    
    # 完整响应数据
    raw_response = Column(JSON)
    error_message = Column(Text)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # 创建复合索引
    __table_args__ = (
        Index('idx_ip_created', 'ip_address', 'created_at'),
        Index('idx_country_created', 'country', 'created_at'),
        Index('idx_city_created', 'city', 'created_at'),
        Index('idx_isp_created', 'isp', 'created_at'),
        Index('idx_status_created', 'status', 'created_at'),
        Index('idx_client_created', 'client_ip', 'created_at'),
    )


class QueryStatistic(Base):
    """查询统计表"""
    __tablename__ = "query_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)  # 统计日期(按小时聚合)
    
    # 查询统计
    total_queries = Column(Integer, default=0)
    successful_queries = Column(Integer, default=0)
    failed_queries = Column(Integer, default=0)
    cached_queries = Column(Integer, default=0)
    
    # 响应时间统计
    avg_response_time = Column(Float, default=0.0)
    min_response_time = Column(Float, default=0.0)
    max_response_time = Column(Float, default=0.0)
    
    # 地理分布统计
    top_countries = Column(JSON)  # 热门国家
    top_cities = Column(JSON)     # 热门城市
    top_isps = Column(JSON)       # 热门ISP
    
    # 数据源统计
    source_distribution = Column(JSON)  # 数据源分布
    
    # 用户统计
    unique_clients = Column(Integer, default=0)
    top_clients = Column(JSON)  # 热门客户端IP
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_date_hour', 'date'),
    )


class DataCleanupRule(Base):
    """数据清理规则表"""
    __tablename__ = "data_cleanup_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    
    # 清理条件
    retention_days = Column(Integer, nullable=False)  # 保留天数
    status_filter = Column(JSON)  # 状态过滤
    source_filter = Column(JSON)  # 数据源过滤
    
    # 执行配置
    is_enabled = Column(Boolean, default=True)
    auto_execute = Column(Boolean, default=False)
    cron_expression = Column(String(100))  # 定时执行表达式
    
    # 统计信息
    last_executed = Column(DateTime)
    last_cleanup_count = Column(Integer, default=0)
    total_cleanup_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DataExportTask(Base):
    """数据导出任务表"""
    __tablename__ = "data_export_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String(100), nullable=False)
    export_format = Column(String(20), nullable=False)  # csv, json, excel
    
    # 导出条件
    query_conditions = Column(JSON)  # 查询条件
    date_range = Column(JSON)        # 时间范围
    fields = Column(JSON)            # 导出字段
    
    # 任务状态
    status = Column(String(20), default="pending", index=True)  # pending, running, completed, failed
    progress = Column(Float, default=0.0)
    total_records = Column(Integer, default=0)
    exported_records = Column(Integer, default=0)
    
    # 文件信息
    file_path = Column(String(500))
    file_size = Column(Integer, default=0)
    download_url = Column(String(500))
    
    # 错误信息
    error_message = Column(Text)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    expires_at = Column(DateTime)  # 文件过期时间


# Pydantic模型

class IPQueryRecordCreate(BaseModel):
    """创建IP查询记录模型"""
    ip_address: str = Field(..., max_length=45)
    query_type: str = Field("single", max_length=20)
    status: QueryStatus
    data_source: DataSource
    country: Optional[str] = Field(None, max_length=100)
    country_code: Optional[str] = Field(None, max_length=10)
    region: Optional[str] = Field(None, max_length=100)
    region_code: Optional[str] = Field(None, max_length=10)
    city: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = Field(None, max_length=50)
    isp: Optional[str] = Field(None, max_length=200)
    organization: Optional[str] = Field(None, max_length=200)
    asn: Optional[str] = Field(None, max_length=50)
    asn_org: Optional[str] = Field(None, max_length=200)
    user_agent: Optional[str] = Field(None, max_length=500)
    client_ip: Optional[str] = Field(None, max_length=45)
    referer: Optional[str] = Field(None, max_length=500)
    response_time_ms: Optional[float] = None
    cache_hit: bool = False
    raw_response: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class IPQueryRecordResponse(BaseModel):
    """IP查询记录响应模型"""
    id: int
    ip_address: str
    query_type: str
    status: str
    data_source: str
    country: Optional[str]
    country_code: Optional[str]
    region: Optional[str]
    region_code: Optional[str]
    city: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    timezone: Optional[str]
    isp: Optional[str]
    organization: Optional[str]
    asn: Optional[str]
    asn_org: Optional[str]
    user_agent: Optional[str]
    client_ip: Optional[str]
    referer: Optional[str]
    response_time_ms: Optional[float]
    cache_hit: bool
    raw_response: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class QueryStatisticsResponse(BaseModel):
    """查询统计响应模型"""
    id: int
    date: datetime
    total_queries: int
    successful_queries: int
    failed_queries: int
    cached_queries: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    top_countries: Optional[Dict[str, Any]]
    top_cities: Optional[Dict[str, Any]]
    top_isps: Optional[Dict[str, Any]]
    source_distribution: Optional[Dict[str, Any]]
    unique_clients: int
    top_clients: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        orm_mode = True


class DataQuery(BaseModel):
    """数据查询模型"""
    ip_address: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    isp: Optional[str] = None
    status: Optional[QueryStatus] = None
    data_source: Optional[DataSource] = None
    client_ip: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


class DataStatistics(BaseModel):
    """数据统计模型"""
    total_queries: int
    successful_queries: int
    failed_queries: int
    cached_queries: int
    success_rate: float
    cache_hit_rate: float
    avg_response_time: float
    unique_ips: int
    unique_countries: int
    unique_cities: int
    unique_isps: int
    top_countries: List[Dict[str, Any]]
    top_cities: List[Dict[str, Any]]
    top_isps: List[Dict[str, Any]]
    query_trends: List[Dict[str, Any]]


class DataCleanupRuleCreate(BaseModel):
    """创建数据清理规则模型"""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    retention_days: int = Field(..., ge=1, le=3650)
    status_filter: Optional[List[str]] = None
    source_filter: Optional[List[str]] = None
    is_enabled: bool = True
    auto_execute: bool = False
    cron_expression: Optional[str] = Field(None, max_length=100)


class DataCleanupRuleResponse(BaseModel):
    """数据清理规则响应模型"""
    id: int
    name: str
    description: Optional[str]
    retention_days: int
    status_filter: Optional[List[str]]
    source_filter: Optional[List[str]]
    is_enabled: bool
    auto_execute: bool
    cron_expression: Optional[str]
    last_executed: Optional[datetime]
    last_cleanup_count: int
    total_cleanup_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DataExportRequest(BaseModel):
    """数据导出请求模型"""
    task_name: str = Field(..., max_length=100)
    export_format: str = Field(..., pattern="^(csv|json|excel)$")
    query_conditions: Optional[Dict[str, Any]] = None
    date_range: Optional[Dict[str, str]] = None
    fields: Optional[List[str]] = None


class DataExportTaskResponse(BaseModel):
    """数据导出任务响应模型"""
    id: int
    task_name: str
    export_format: str
    query_conditions: Optional[Dict[str, Any]]
    date_range: Optional[Dict[str, str]]
    fields: Optional[List[str]]
    status: str
    progress: float
    total_records: int
    exported_records: int
    file_path: Optional[str]
    file_size: int
    download_url: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    expires_at: Optional[datetime]
    
    class Config:
        orm_mode = True


class GeoDistribution(BaseModel):
    """地理分布模型"""
    country_distribution: Dict[str, int]
    city_distribution: Dict[str, int]
    region_distribution: Dict[str, int]
    coordinates: List[Dict[str, Any]]  # 地图坐标点


class ISPAnalysis(BaseModel):
    """ISP分析模型"""
    isp_distribution: Dict[str, int]
    asn_distribution: Dict[str, int]
    organization_distribution: Dict[str, int]
    top_isps: List[Dict[str, Any]]


class QueryTrend(BaseModel):
    """查询趋势模型"""
    timestamp: datetime
    total_queries: int
    successful_queries: int
    failed_queries: int
    cached_queries: int
    avg_response_time: float
    unique_ips: int


class DataDashboard(BaseModel):
    """数据仪表板模型"""
    statistics: DataStatistics
    geo_distribution: GeoDistribution
    isp_analysis: ISPAnalysis
    query_trends: List[QueryTrend]
    recent_queries: List[IPQueryRecordResponse]
    system_health: Dict[str, Any]
