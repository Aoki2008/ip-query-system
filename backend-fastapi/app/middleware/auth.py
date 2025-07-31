"""
认证中间件
处理JWT令牌验证和用户认证
"""
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.auth_service import auth_service
from app.models.user import User
from app.core.logging import get_logger

logger = get_logger(__name__)

# HTTP Bearer 认证方案
security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> Optional[User]:
    """
    获取当前认证用户（可选）
    如果没有提供令牌或令牌无效，返回None而不抛出异常
    """
    if not credentials:
        return None
    
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        return user
    except Exception as e:
        logger.warning(f"获取当前用户失败: {e}")
        return None


async def get_current_active_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> User:
    """
    获取当前活跃用户（必需）
    如果没有提供令牌或令牌无效，抛出认证异常
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户账户已被禁用"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户认证失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证过程中发生错误",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_premium_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    获取当前高级用户（必需）
    只有高级用户才能访问某些功能
    """
    if not current_user.is_premium:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="此功能仅限高级用户使用"
        )
    
    return current_user


class AuthMiddleware:
    """认证中间件类"""
    
    @staticmethod
    async def verify_api_key(api_key: str) -> Optional[User]:
        """
        验证API密钥
        """
        try:
            # 这里需要实现API密钥验证逻辑
            # 从数据库中查找API密钥对应的用户
            # 暂时返回None，后续实现
            return None
        except Exception as e:
            logger.error(f"API密钥验证失败: {e}")
            return None
    
    @staticmethod
    async def check_rate_limit(user: User, endpoint: str) -> bool:
        """
        检查用户请求频率限制
        """
        try:
            # 这里需要实现频率限制逻辑
            # 可以使用Redis或内存缓存来跟踪用户请求
            # 暂时返回True，后续实现
            return True
        except Exception as e:
            logger.error(f"频率限制检查失败: {e}")
            return False


# 全局认证中间件实例
auth_middleware = AuthMiddleware()
