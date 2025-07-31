"""
权限管理数据模型
"""
from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field

from ...database import Base


# 角色权限关联表
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

# 用户角色关联表
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('admin_users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)


class Permission(Base):
    """权限表"""
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    resource = Column(String(50), nullable=False)  # 资源类型：system, user, data, config等
    action = Column(String(50), nullable=False)    # 操作类型：read, write, delete等
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")


class Role(Base):
    """角色表"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    is_system = Column(Boolean, default=False)  # 是否为系统内置角色
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("admin_users.id"))
    
    # 关联关系
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    users = relationship("AdminUser", secondary=user_roles)


class ResourceType(str, Enum):
    """资源类型枚举"""
    SYSTEM = "system"           # 系统管理
    USER = "user"              # 用户管理
    DATA = "data"              # 数据管理
    CONFIG = "config"          # 配置管理
    MONITORING = "monitoring"   # 监控管理
    BACKUP = "backup"          # 备份管理
    LOG = "log"                # 日志管理
    API = "api"                # API管理


class ActionType(str, Enum):
    """操作类型枚举"""
    READ = "read"              # 读取
    WRITE = "write"            # 写入
    DELETE = "delete"          # 删除
    EXECUTE = "execute"        # 执行
    MANAGE = "manage"          # 管理


# Pydantic模型

class PermissionBase(BaseModel):
    """权限基础模型"""
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=100)
    description: Optional[str] = None
    resource: ResourceType
    action: ActionType
    is_active: bool = True


class PermissionCreate(PermissionBase):
    """创建权限模型"""
    pass


class PermissionUpdate(BaseModel):
    """更新权限模型"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PermissionResponse(PermissionBase):
    """权限响应模型"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    """角色基础模型"""
    name: str = Field(..., max_length=50)
    code: str = Field(..., max_length=50)
    description: Optional[str] = None
    is_active: bool = True


class RoleCreate(RoleBase):
    """创建角色模型"""
    permission_ids: List[int] = []


class RoleUpdate(BaseModel):
    """更新角色模型"""
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    permission_ids: Optional[List[int]] = None


class RoleResponse(RoleBase):
    """角色响应模型"""
    id: int
    is_system: bool
    created_at: datetime
    created_by: Optional[int]
    permissions: List[PermissionResponse] = []
    
    class Config:
        from_attributes = True


class UserRoleAssignment(BaseModel):
    """用户角色分配模型"""
    user_id: int
    role_ids: List[int]


class RolePermissionAssignment(BaseModel):
    """角色权限分配模型"""
    role_id: int
    permission_ids: List[int]


class PermissionCheck(BaseModel):
    """权限检查模型"""
    resource: ResourceType
    action: ActionType


class UserPermissions(BaseModel):
    """用户权限模型"""
    user_id: int
    username: str
    roles: List[RoleResponse]
    permissions: List[PermissionResponse]
    
    class Config:
        orm_mode = True


class PermissionMatrix(BaseModel):
    """权限矩阵模型"""
    resources: List[str]
    actions: List[str]
    roles: List[dict]  # 包含角色信息和权限矩阵
    
    
class SystemPermissions:
    """系统权限定义"""
    
    # 系统管理权限
    SYSTEM_READ = "system:read"
    SYSTEM_WRITE = "system:write"
    SYSTEM_DELETE = "system:delete"
    SYSTEM_MANAGE = "system:manage"
    
    # 用户管理权限
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    USER_MANAGE = "user:manage"
    
    # 数据管理权限
    DATA_READ = "data:read"
    DATA_WRITE = "data:write"
    DATA_DELETE = "data:delete"
    DATA_EXPORT = "data:export"
    
    # 配置管理权限
    CONFIG_READ = "config:read"
    CONFIG_WRITE = "config:write"
    CONFIG_MANAGE = "config:manage"
    
    # 监控管理权限
    MONITORING_READ = "monitoring:read"
    MONITORING_WRITE = "monitoring:write"
    MONITORING_MANAGE = "monitoring:manage"
    
    # 备份管理权限
    BACKUP_READ = "backup:read"
    BACKUP_WRITE = "backup:write"
    BACKUP_EXECUTE = "backup:execute"
    
    # 日志管理权限
    LOG_READ = "log:read"
    LOG_WRITE = "log:write"
    LOG_DELETE = "log:delete"
    
    # API管理权限
    API_READ = "api:read"
    API_WRITE = "api:write"
    API_MANAGE = "api:manage"
    
    @classmethod
    def get_all_permissions(cls) -> List[dict]:
        """获取所有系统权限定义"""
        return [
            # 系统管理
            {"name": "系统信息查看", "code": cls.SYSTEM_READ, "resource": "system", "action": "read", "description": "查看系统基本信息和状态"},
            {"name": "系统配置修改", "code": cls.SYSTEM_WRITE, "resource": "system", "action": "write", "description": "修改系统基础配置"},
            {"name": "系统数据删除", "code": cls.SYSTEM_DELETE, "resource": "system", "action": "delete", "description": "删除系统数据"},
            {"name": "系统完全管理", "code": cls.SYSTEM_MANAGE, "resource": "system", "action": "manage", "description": "系统完全管理权限"},
            
            # 用户管理
            {"name": "用户信息查看", "code": cls.USER_READ, "resource": "user", "action": "read", "description": "查看用户基本信息"},
            {"name": "用户信息修改", "code": cls.USER_WRITE, "resource": "user", "action": "write", "description": "修改用户信息"},
            {"name": "用户删除", "code": cls.USER_DELETE, "resource": "user", "action": "delete", "description": "删除用户账户"},
            {"name": "用户完全管理", "code": cls.USER_MANAGE, "resource": "user", "action": "manage", "description": "用户完全管理权限"},
            
            # 数据管理
            {"name": "数据查看", "code": cls.DATA_READ, "resource": "data", "action": "read", "description": "查看系统数据"},
            {"name": "数据修改", "code": cls.DATA_WRITE, "resource": "data", "action": "write", "description": "修改系统数据"},
            {"name": "数据删除", "code": cls.DATA_DELETE, "resource": "data", "action": "delete", "description": "删除系统数据"},
            {"name": "数据导出", "code": cls.DATA_EXPORT, "resource": "data", "action": "execute", "description": "导出系统数据"},
            
            # 配置管理
            {"name": "配置查看", "code": cls.CONFIG_READ, "resource": "config", "action": "read", "description": "查看系统配置"},
            {"name": "配置修改", "code": cls.CONFIG_WRITE, "resource": "config", "action": "write", "description": "修改系统配置"},
            {"name": "配置完全管理", "code": cls.CONFIG_MANAGE, "resource": "config", "action": "manage", "description": "配置完全管理权限"},
            
            # 监控管理
            {"name": "监控数据查看", "code": cls.MONITORING_READ, "resource": "monitoring", "action": "read", "description": "查看监控数据"},
            {"name": "监控配置修改", "code": cls.MONITORING_WRITE, "resource": "monitoring", "action": "write", "description": "修改监控配置"},
            {"name": "监控完全管理", "code": cls.MONITORING_MANAGE, "resource": "monitoring", "action": "manage", "description": "监控完全管理权限"},
            
            # 备份管理
            {"name": "备份信息查看", "code": cls.BACKUP_READ, "resource": "backup", "action": "read", "description": "查看备份信息"},
            {"name": "备份配置修改", "code": cls.BACKUP_WRITE, "resource": "backup", "action": "write", "description": "修改备份配置"},
            {"name": "备份执行", "code": cls.BACKUP_EXECUTE, "resource": "backup", "action": "execute", "description": "执行备份操作"},
            
            # 日志管理
            {"name": "日志查看", "code": cls.LOG_READ, "resource": "log", "action": "read", "description": "查看系统日志"},
            {"name": "日志配置", "code": cls.LOG_WRITE, "resource": "log", "action": "write", "description": "配置日志设置"},
            {"name": "日志删除", "code": cls.LOG_DELETE, "resource": "log", "action": "delete", "description": "删除日志文件"},
            
            # API管理
            {"name": "API信息查看", "code": cls.API_READ, "resource": "api", "action": "read", "description": "查看API信息"},
            {"name": "API配置修改", "code": cls.API_WRITE, "resource": "api", "action": "write", "description": "修改API配置"},
            {"name": "API完全管理", "code": cls.API_MANAGE, "resource": "api", "action": "manage", "description": "API完全管理权限"},
        ]


class SystemRoles:
    """系统角色定义"""
    
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    READONLY = "readonly"
    
    @classmethod
    def get_default_roles(cls) -> List[dict]:
        """获取默认角色定义"""
        return [
            {
                "name": "超级管理员",
                "code": cls.SUPER_ADMIN,
                "description": "拥有系统所有权限的超级管理员",
                "is_system": True,
                "permissions": SystemPermissions.get_all_permissions()
            },
            {
                "name": "系统管理员",
                "code": cls.ADMIN,
                "description": "拥有大部分系统管理权限的管理员",
                "is_system": True,
                "permissions": [p for p in SystemPermissions.get_all_permissions() 
                              if p["action"] in ["read", "write"] and p["resource"] != "user"]
            },
            {
                "name": "只读用户",
                "code": cls.READONLY,
                "description": "只能查看系统信息的只读用户",
                "is_system": True,
                "permissions": [p for p in SystemPermissions.get_all_permissions() 
                              if p["action"] == "read"]
            }
        ]
