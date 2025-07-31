"""
认证API路由
处理用户注册、登录、令牌刷新等认证相关接口
"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from app.models.user import UserCreate, User
from app.models.auth import (
    LoginRequest, LoginResponse, RefreshTokenRequest, 
    AuthResponse, PasswordResetRequest
)
from app.services.auth_service import auth_service
from app.middleware.auth import get_current_active_user
from app.core.logging import get_logger

logger = get_logger(__name__)

# 创建认证路由器
auth_router = APIRouter(prefix="/auth", tags=["认证"])


@auth_router.post("/register", response_model=AuthResponse)
async def register_user(user_data: UserCreate):
    """
    用户注册
    
    - **username**: 用户名（3-50字符，只能包含字母、数字、下划线和连字符）
    - **email**: 邮箱地址
    - **password**: 密码（至少6字符）
    - **confirm_password**: 确认密码
    - **full_name**: 真实姓名（可选）
    """
    try:
        success, message, user = await auth_service.register_user(user_data)
        
        if success:
            logger.info(f"用户注册成功: {user.username}")
            return AuthResponse(
                success=True,
                message=message,
                data={
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户注册失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册过程中发生错误"
        )


@auth_router.post("/login", response_model=LoginResponse)
async def login_user(login_data: LoginRequest):
    """
    用户登录
    
    - **username_or_email**: 用户名或邮箱地址
    - **password**: 密码
    - **remember_me**: 是否记住登录状态（延长令牌有效期）
    """
    try:
        # 认证用户
        success, message, user = await auth_service.authenticate_user(login_data)

        if not success:
            logger.warning(f"用户登录失败: {message}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=message,
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 创建令牌
        login_response = await auth_service.create_user_tokens(user, login_data.remember_me)

        logger.info(f"用户登录成功: {user.username}")
        return login_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户登录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录过程中发生错误"
        )


@auth_router.post("/refresh", response_model=LoginResponse)
async def refresh_token(refresh_data: RefreshTokenRequest):
    """
    刷新访问令牌
    
    - **refresh_token**: 刷新令牌
    """
    try:
        login_response = await auth_service.refresh_access_token(refresh_data.refresh_token)
        
        if not login_response:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info("令牌刷新成功")
        return login_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"令牌刷新失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="令牌刷新过程中发生错误"
        )


@auth_router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    获取当前用户信息
    
    需要提供有效的访问令牌
    """
    logger.info(f"获取用户信息: {current_user.username}")
    return current_user


@auth_router.post("/logout", response_model=AuthResponse)
async def logout_user(current_user: User = Depends(get_current_active_user)):
    """
    用户登出
    
    需要提供有效的访问令牌
    """
    try:
        # 这里可以实现令牌黑名单或会话清理逻辑
        # 目前只是简单返回成功响应
        
        logger.info(f"用户登出: {current_user.username}")
        return AuthResponse(
            success=True,
            message="登出成功",
            data={"user_id": current_user.id}
        )
        
    except Exception as e:
        logger.error(f"用户登出失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登出过程中发生错误"
        )


@auth_router.post("/password-reset", response_model=AuthResponse)
async def request_password_reset(reset_data: PasswordResetRequest):
    """
    请求密码重置
    
    - **email**: 邮箱地址
    """
    try:
        # 这里需要实现密码重置逻辑
        # 1. 验证邮箱是否存在
        # 2. 生成重置令牌
        # 3. 发送重置邮件
        
        # 暂时返回成功响应
        logger.info(f"密码重置请求: {reset_data.email}")
        return AuthResponse(
            success=True,
            message="密码重置邮件已发送，请检查您的邮箱",
            data={"email": reset_data.email}
        )
        
    except Exception as e:
        logger.error(f"密码重置请求失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="密码重置过程中发生错误"
        )


@auth_router.get("/check-username/{username}", response_model=AuthResponse)
async def check_username_availability(username: str):
    """
    检查用户名是否可用
    
    - **username**: 要检查的用户名
    """
    try:
        from app.core.database import db_manager
        
        existing_user = await db_manager.get_user_by_username(username)
        available = existing_user is None
        
        return AuthResponse(
            success=True,
            message="用户名可用" if available else "用户名已被使用",
            data={"username": username, "available": available}
        )
        
    except Exception as e:
        logger.error(f"检查用户名可用性失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="检查用户名时发生错误"
        )


@auth_router.get("/check-email/{email}", response_model=AuthResponse)
async def check_email_availability(email: str):
    """
    检查邮箱是否可用
    
    - **email**: 要检查的邮箱地址
    """
    try:
        from app.core.database import db_manager
        
        existing_user = await db_manager.get_user_by_email(email)
        available = existing_user is None
        
        return AuthResponse(
            success=True,
            message="邮箱可用" if available else "邮箱已被注册",
            data={"email": email, "available": available}
        )
        
    except Exception as e:
        logger.error(f"检查邮箱可用性失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="检查邮箱时发生错误"
        )
