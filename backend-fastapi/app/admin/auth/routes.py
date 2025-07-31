"""
管理员认证路由
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from ..models import (
    AdminUser, LoginRequest, LoginResponse, TokenRefreshRequest, 
    TokenResponse, AdminUserResponse, AdminUserCreate, AdminUserUpdate
)
from .utils import (
    verify_password, get_password_hash, create_access_token, 
    create_refresh_token, verify_token, calculate_lockout_time,
    log_security_event, is_password_strong
)
from .dependencies import (
    get_current_active_user, require_super_admin, check_rate_limit
)
from ...database import get_db

router = APIRouter(prefix="/api/admin/auth", tags=["管理员认证"])


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """管理员登录"""
    # 查找用户
    user = db.query(AdminUser).filter(AdminUser.username == login_data.username).first()
    
    if not user:
        # 记录安全事件
        log_security_event("login_failed", None, {
            "username": login_data.username,
            "reason": "user_not_found"
        })
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 检查账户是否被锁定
    if user.locked_until and datetime.utcnow() < user.locked_until:
        remaining_time = user.locked_until - datetime.utcnow()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"账户已被锁定，请在 {remaining_time.seconds // 60} 分钟后重试"
        )
    
    # 检查账户是否激活
    if not user.is_active:
        log_security_event("login_failed", user.id, {
            "username": login_data.username,
            "reason": "account_inactive"
        })
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账户已被禁用"
        )
    
    # 验证密码
    if not verify_password(login_data.password, user.password_hash):
        # 增加失败尝试次数
        user.login_attempts += 1
        
        # 计算锁定时间
        if user.login_attempts >= 5:
            user.locked_until = calculate_lockout_time(user.login_attempts)
        
        db.commit()
        
        log_security_event("login_failed", user.id, {
            "username": login_data.username,
            "reason": "invalid_password",
            "attempts": user.login_attempts
        })
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 登录成功，重置失败尝试次数
    user.login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.utcnow()
    db.commit()
    
    # 创建令牌
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "user_id": user.id}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id}
    )
    
    log_security_event("login_success", user.id, {
        "username": login_data.username
    })
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=15 * 60,  # 15分钟
        user=AdminUserResponse.parse_obj(user.__dict__)
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """刷新访问令牌"""
    try:
        # 验证刷新令牌
        payload = verify_token(refresh_data.refresh_token, "refresh")
        username = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # 查找用户
        user = db.query(AdminUser).filter(AdminUser.username == username).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # 创建新的访问令牌
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role, "user_id": user.id}
        )
        
        return TokenResponse(
            access_token=access_token,
            expires_in=15 * 60
        )
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """管理员登出"""
    # 在实际应用中，这里可以将令牌加入黑名单
    # 或者在Redis中记录已登出的令牌
    
    log_security_event("logout", current_user.id, {
        "username": current_user.username
    })
    
    return {"message": "Successfully logged out"}


@router.get("/profile", response_model=AdminUserResponse)
async def get_profile(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取当前用户信息"""
    return AdminUserResponse.parse_obj(current_user.__dict__)


@router.put("/profile", response_model=AdminUserResponse)
async def update_profile(
    profile_data: AdminUserUpdate,
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新当前用户信息"""
    # 只允许更新邮箱和密码
    if profile_data.email is not None:
        current_user.email = profile_data.email
    
    if profile_data.password is not None:
        # 检查密码强度
        is_strong, message = is_password_strong(profile_data.password)
        if not is_strong:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        current_user.password_hash = get_password_hash(profile_data.password)
        
        log_security_event("password_changed", current_user.id, {
            "username": current_user.username
        })
    
    db.commit()
    db.refresh(current_user)
    
    return AdminUserResponse.parse_obj(current_user.__dict__)


@router.post("/users", response_model=AdminUserResponse)
async def create_user(
    user_data: AdminUserCreate,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """创建新的管理员用户（仅超级管理员）"""
    # 检查用户名是否已存在
    existing_user = db.query(AdminUser).filter(AdminUser.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if user_data.email:
        existing_email = db.query(AdminUser).filter(AdminUser.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
    
    # 检查密码强度
    is_strong, message = is_password_strong(user_data.password)
    if not is_strong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # 创建新用户
    new_user = AdminUser(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        email=user_data.email,
        role=user_data.role.value,
        is_active=user_data.is_active
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    log_security_event("user_created", current_user.id, {
        "created_user_id": new_user.id,
        "created_username": new_user.username,
        "created_role": new_user.role
    })
    
    return AdminUserResponse.parse_obj(new_user.__dict__)


@router.get("/users", response_model=list[AdminUserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """获取管理员用户列表（仅超级管理员）"""
    users = db.query(AdminUser).offset(skip).limit(limit).all()
    return [AdminUserResponse.parse_obj(user.__dict__) for user in users]


@router.put("/users/{user_id}", response_model=AdminUserResponse)
async def update_user(
    user_id: int,
    user_data: AdminUserUpdate,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """更新管理员用户（仅超级管理员）"""
    user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不允许修改自己的角色和状态
    if user.id == current_user.id:
        if user_data.role is not None or user_data.is_active is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能修改自己的角色和状态"
            )
    
    # 更新用户信息
    if user_data.email is not None:
        user.email = user_data.email
    
    if user_data.role is not None:
        user.role = user_data.role.value
    
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    if user_data.password is not None:
        is_strong, message = is_password_strong(user_data.password)
        if not is_strong:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        user.password_hash = get_password_hash(user_data.password)
    
    db.commit()
    db.refresh(user)
    
    log_security_event("user_updated", current_user.id, {
        "updated_user_id": user.id,
        "updated_username": user.username,
        "changes": user_data.dict(exclude_unset=True)
    })
    
    return AdminUserResponse.parse_obj(user.__dict__)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """删除管理员用户（仅超级管理员）"""
    user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不允许删除自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )
    
    db.delete(user)
    db.commit()
    
    log_security_event("user_deleted", current_user.id, {
        "deleted_user_id": user.id,
        "deleted_username": user.username
    })
    
    return {"message": "用户已删除"}
