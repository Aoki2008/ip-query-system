"""
认证依赖项
"""
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..models import AdminUser, AdminRole
from .utils import get_user_from_token, check_user_permissions, check_account_lockout
from ...database import get_db

# HTTP Bearer认证
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> AdminUser:
    """获取当前认证用户"""
    try:
        # 验证令牌并获取用户信息
        payload = get_user_from_token(credentials.credentials)
        username = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 从数据库获取用户信息
        user = db.query(AdminUser).filter(AdminUser.username == username).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 检查用户是否激活
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 检查账户是否被锁定
        if check_account_lockout(user.login_attempts, user.locked_until):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is locked due to too many failed login attempts",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: AdminUser = Depends(get_current_user)
) -> AdminUser:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_permissions(permissions: List[str]):
    """权限检查装饰器"""
    def permission_checker(
        current_user: AdminUser = Depends(get_current_active_user)
    ) -> AdminUser:
        if not check_user_permissions(current_user.role, permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    
    return permission_checker


def require_role(required_role: AdminRole):
    """角色检查装饰器"""
    def role_checker(
        current_user: AdminUser = Depends(get_current_active_user)
    ) -> AdminUser:
        # 角色层级检查
        role_hierarchy = {
            AdminRole.READONLY: 1,
            AdminRole.ADMIN: 2,
            AdminRole.SUPER_ADMIN: 3
        }
        
        user_level = role_hierarchy.get(AdminRole(current_user.role), 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role.value} role or higher"
            )
        
        return current_user
    
    return role_checker


# 常用权限检查依赖项
require_read_permission = require_permissions(["system:read"])
require_write_permission = require_permissions(["system:write"])
require_delete_permission = require_permissions(["system:delete"])

require_config_read = require_permissions(["config:read"])
require_config_write = require_permissions(["config:write"])

require_monitoring_read = require_permissions(["monitoring:read"])
require_monitoring_write = require_permissions(["monitoring:write"])

require_data_read = require_permissions(["data:read"])
require_data_write = require_permissions(["data:write"])
require_data_delete = require_permissions(["data:delete"])

require_user_management = require_permissions(["users:read", "users:write"])
require_backup_access = require_permissions(["backup:read", "backup:write"])

# 角色检查依赖项
require_admin = require_role(AdminRole.ADMIN)
require_super_admin = require_role(AdminRole.SUPER_ADMIN)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
    db: Session = Depends(get_db)
) -> Optional[AdminUser]:
    """获取可选的当前用户（用于某些不强制要求认证的接口）"""
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


def check_api_access(
    api_key: Optional[str] = None,
    current_user: Optional[AdminUser] = Depends(get_optional_user)
) -> bool:
    """检查API访问权限（支持API密钥或用户认证）"""
    # 如果有用户认证，直接允许
    if current_user:
        return True
    
    # 检查API密钥
    if api_key:
        # 这里可以实现API密钥验证逻辑
        # 暂时简单检查环境变量中的API密钥
        import os
        valid_api_keys = os.getenv("ADMIN_API_KEYS", "").split(",")
        if api_key in valid_api_keys and api_key:
            return True
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required"
    )


class RateLimiter:
    """简单的速率限制器"""
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, identifier: str) -> bool:
        """检查是否允许请求"""
        import time
        
        now = time.time()
        window_start = now - self.window_seconds
        
        # 清理过期记录
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > window_start
            ]
        else:
            self.requests[identifier] = []
        
        # 检查请求数量
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        # 记录当前请求
        self.requests[identifier].append(now)
        return True


# 全局速率限制器实例
rate_limiter = RateLimiter()


def check_rate_limit(identifier: str = None):
    """速率限制检查"""
    def rate_limit_checker(
        request,
        current_user: Optional[AdminUser] = Depends(get_optional_user)
    ):
        # 使用用户ID或IP地址作为标识符
        if current_user:
            limit_id = f"user_{current_user.id}"
        else:
            limit_id = identifier or request.client.host
        
        if not rate_limiter.is_allowed(limit_id):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        return True
    
    return rate_limit_checker
