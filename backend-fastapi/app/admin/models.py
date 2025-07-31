"""
管理后台数据模型
"""
from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field

# 导入Base类
from ..database import Base


class AdminRole(str, Enum):
    """管理员角色枚举"""
    SUPER_ADMIN = "super_admin"  # 超级管理员
    ADMIN = "admin"              # 系统管理员
    READONLY = "readonly"        # 只读用户


class AdminUser(Base):
    """管理员用户表"""
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), index=True)
    role = Column(String(20), default=AdminRole.ADMIN.value)  # 保留兼容性
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)

    # 关联关系将在权限模块中定义


class QueryLog(Base):
    """查询日志表"""
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), nullable=False, index=True)
    query_ip = Column(String(45), nullable=False, index=True)
    result = Column(Text)  # JSON格式存储查询结果
    query_time = Column(String(20))  # 查询耗时
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    user_agent = Column(Text)
    source = Column(String(20), default="web")  # web, api, batch
    response_size = Column(Integer)
    cache_hit = Column(Boolean, default=False)


class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, nullable=False, index=True)
    config_value = Column(Text)
    config_type = Column(String(20), default="string")  # string, int, bool, json
    description = Column(Text)
    is_sensitive = Column(Boolean, default=False)  # 是否为敏感配置
    updated_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey("admin_users.id"))


class AlertLog(Base):
    """告警记录表"""
    __tablename__ = "alert_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_name = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)  # info, warning, error, critical
    message = Column(Text)
    triggered_at = Column(DateTime, nullable=False, index=True)
    resolved_at = Column(DateTime)
    status = Column(String(20), default="active")  # active, resolved, ignored
    notification_sent = Column(Boolean, default=False)


# Pydantic模型用于API

class AdminUserBase(BaseModel):
    """管理员用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    role: AdminRole = AdminRole.ADMIN
    is_active: bool = True


class AdminUserCreate(AdminUserBase):
    """创建管理员用户模型"""
    password: str = Field(..., min_length=6, max_length=100)


class AdminUserUpdate(BaseModel):
    """更新管理员用户模型"""
    email: Optional[str] = None
    role: Optional[AdminRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)


class AdminUserResponse(AdminUserBase):
    """管理员用户响应模型"""
    id: int
    created_at: datetime
    last_login: Optional[datetime]
    login_attempts: int
    locked_until: Optional[datetime]
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=1, max_length=100)


class LoginResponse(BaseModel):
    """登录响应模型"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: AdminUserResponse


class TokenRefreshRequest(BaseModel):
    """令牌刷新请求模型"""
    refresh_token: str


class TokenResponse(BaseModel):
    """令牌响应模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class QueryLogResponse(BaseModel):
    """查询日志响应模型"""
    id: int
    ip_address: str
    query_ip: str
    result: Optional[str]
    query_time: Optional[str]
    created_at: datetime
    user_agent: Optional[str]
    source: str
    response_size: Optional[int]
    cache_hit: bool
    
    class Config:
        orm_mode = True


class SystemConfigBase(BaseModel):
    """系统配置基础模型"""
    config_key: str = Field(..., max_length=100)
    config_value: Optional[str] = None
    config_type: str = "string"
    description: Optional[str] = None
    is_sensitive: bool = False


class SystemConfigCreate(SystemConfigBase):
    """创建系统配置模型"""
    pass


class SystemConfigUpdate(BaseModel):
    """更新系统配置模型"""
    config_value: Optional[str] = None
    description: Optional[str] = None
    is_sensitive: Optional[bool] = None


class SystemConfigResponse(SystemConfigBase):
    """系统配置响应模型"""
    id: int
    updated_at: datetime
    updated_by: Optional[int]
    
    class Config:
        from_attributes = True


class AlertLogResponse(BaseModel):
    """告警记录响应模型"""
    id: int
    alert_name: str
    severity: str
    message: Optional[str]
    triggered_at: datetime
    resolved_at: Optional[datetime]
    status: str
    notification_sent: bool
    
    class Config:
        orm_mode = True


class DashboardStats(BaseModel):
    """仪表板统计模型"""
    total_queries_today: int
    total_queries_week: int
    total_queries_month: int
    unique_ips_today: int
    cache_hit_rate: float
    avg_response_time: float
    active_alerts: int
    system_status: str


class SystemMetrics(BaseModel):
    """系统指标模型"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: dict
    load_average: List[float]
    uptime: int
    timestamp: datetime
