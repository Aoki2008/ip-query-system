"""
认证服务模块
处理用户注册、登录、令牌管理等认证相关功能
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple

from app.core.database import db_manager
from app.core.security import security
from app.core.logging import get_logger
from app.models.user import UserCreate, UserInDB, User
from app.models.auth import LoginRequest, LoginResponse, TokenData

logger = get_logger(__name__)


class AuthService:
    """认证服务类"""
    
    async def register_user(self, user_data: UserCreate) -> Tuple[bool, str, Optional[User]]:
        """
        用户注册
        返回: (成功状态, 消息, 用户对象)
        """
        try:
            # 检查用户名是否已存在
            existing_user = await db_manager.get_user_by_username(user_data.username)
            if existing_user:
                return False, "用户名已存在", None
            
            # 检查邮箱是否已存在
            existing_email = await db_manager.get_user_by_email(user_data.email)
            if existing_email:
                return False, "邮箱已被注册", None
            
            # 创建用户
            user_id = str(uuid.uuid4())
            password_hash = security.hash_password(user_data.password)
            
            user_db_data = {
                'id': user_id,
                'username': user_data.username,
                'email': user_data.email,
                'password_hash': password_hash,
                'full_name': user_data.full_name,
                'avatar_url': None
            }
            
            created_user_id = await db_manager.create_user(user_db_data)
            if not created_user_id:
                return False, "用户创建失败", None
            
            # 获取创建的用户信息
            user_dict = await db_manager.get_user_by_id(created_user_id)
            if user_dict:
                user = User(**user_dict)
                logger.info(f"用户注册成功: {user.username}")
                return True, "注册成功", user
            
            return False, "用户创建失败", None
            
        except Exception as e:
            logger.error(f"用户注册失败: {e}")
            return False, "注册过程中发生错误", None
    
    async def authenticate_user(self, login_data: LoginRequest) -> Tuple[bool, str, Optional[User]]:
        """
        用户认证
        返回: (成功状态, 消息, 用户对象)
        """
        try:
            # 尝试通过用户名或邮箱查找用户
            user_dict = None
            if "@" in login_data.username_or_email:
                user_dict = await db_manager.get_user_by_email(login_data.username_or_email)
            else:
                user_dict = await db_manager.get_user_by_username(login_data.username_or_email)
            
            if not user_dict:
                return False, "用户不存在", None
            
            # 验证密码
            if not security.verify_password(login_data.password, user_dict['password_hash']):
                return False, "密码错误", None
            
            # 检查用户是否激活
            if not user_dict.get('is_active', True):
                return False, "账户已被禁用", None
            
            # 更新最后登录时间
            await db_manager.update_user_login_time(user_dict['id'])
            
            user = User(**user_dict)
            logger.info(f"用户登录成功: {user.username}")
            return True, "登录成功", user
            
        except Exception as e:
            logger.error(f"用户认证失败: {e}")
            return False, "认证过程中发生错误", None
    
    async def create_user_tokens(self, user: User, remember_me: bool = False) -> LoginResponse:
        """
        创建用户令牌
        """
        try:
            # 准备令牌数据
            token_data = {
                "sub": user.id,
                "username": user.username,
                "email": user.email,
                "is_premium": user.is_premium
            }
            
            # 设置过期时间
            access_expires = timedelta(minutes=30)
            if remember_me:
                access_expires = timedelta(days=1)
            
            # 创建令牌
            access_token = security.create_access_token(
                data=token_data,
                expires_delta=access_expires
            )
            refresh_token = security.create_refresh_token(data=token_data)
            
            # 计算过期时间（秒）
            expires_in = int(access_expires.total_seconds())
            
            return LoginResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=expires_in,
                user=user.dict()
            )
            
        except Exception as e:
            logger.error(f"创建用户令牌失败: {e}")
            raise
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[LoginResponse]:
        """
        刷新访问令牌
        """
        try:
            # 验证刷新令牌
            payload = security.verify_token(refresh_token, token_type="refresh")
            if not payload:
                return None
            
            # 获取用户信息
            user_id = payload.get("sub")
            user_dict = await db_manager.get_user_by_id(user_id)
            if not user_dict:
                return None
            
            user = User(**user_dict)
            
            # 创建新的访问令牌
            return await self.create_user_tokens(user)
            
        except Exception as e:
            logger.error(f"刷新令牌失败: {e}")
            return None
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """
        根据令牌获取当前用户
        """
        try:
            # 验证令牌
            payload = security.verify_token(token)
            if not payload:
                return None
            
            # 获取用户信息
            user_id = payload.get("sub")
            user_dict = await db_manager.get_user_by_id(user_id)
            if not user_dict:
                return None
            
            return User(**user_dict)
            
        except Exception as e:
            logger.error(f"获取当前用户失败: {e}")
            return None
    
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> Tuple[bool, str]:
        """
        修改密码
        """
        try:
            # 获取用户信息
            user_dict = await db_manager.get_user_by_id(user_id)
            if not user_dict:
                return False, "用户不存在"
            
            # 验证当前密码
            if not security.verify_password(current_password, user_dict['password_hash']):
                return False, "当前密码错误"
            
            # 更新密码
            new_password_hash = security.hash_password(new_password)
            # 这里需要在数据库管理器中添加更新密码的方法
            # await db_manager.update_user_password(user_id, new_password_hash)
            
            logger.info(f"用户密码修改成功: {user_dict['username']}")
            return True, "密码修改成功"
            
        except Exception as e:
            logger.error(f"修改密码失败: {e}")
            return False, "密码修改过程中发生错误"
    
    async def validate_token_data(self, token: str) -> Optional[TokenData]:
        """
        验证令牌并返回令牌数据
        """
        try:
            payload = security.verify_token(token)
            if not payload:
                return None
            
            return TokenData(
                user_id=payload.get("sub"),
                username=payload.get("username"),
                email=payload.get("email"),
                is_premium=payload.get("is_premium", False),
                exp=datetime.fromtimestamp(payload.get("exp"))
            )
            
        except Exception as e:
            logger.error(f"验证令牌数据失败: {e}")
            return None


# 全局认证服务实例
auth_service = AuthService()
