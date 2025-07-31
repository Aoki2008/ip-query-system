"""
认证相关数据模型
"""
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator


class LoginRequest(BaseModel):
    """登录请求模型"""
    username_or_email: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")
    remember_me: bool = Field(default=False, description="记住我")


class LoginResponse(BaseModel):
    """登录响应模型"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间(秒)")
    user: dict = Field(..., description="用户信息")


class TokenData(BaseModel):
    """令牌数据模型"""
    user_id: str
    username: str
    email: str
    is_premium: bool = False
    exp: datetime
    
    class Config:
        from_attributes = True


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模型"""
    refresh_token: str = Field(..., description="刷新令牌")


class PasswordResetRequest(BaseModel):
    """密码重置请求模型"""
    email: str = Field(..., description="邮箱地址")


class PasswordResetConfirm(BaseModel):
    """密码重置确认模型"""
    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")
    confirm_password: str = Field(..., description="确认新密码")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """验证密码确认"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的密码不一致')
        return v


class EmailVerificationRequest(BaseModel):
    """邮箱验证请求模型"""
    email: str = Field(..., description="邮箱地址")


class EmailVerificationConfirm(BaseModel):
    """邮箱验证确认模型"""
    token: str = Field(..., description="验证令牌")


class SessionInfo(BaseModel):
    """会话信息模型"""
    session_id: str
    user_id: str
    ip_address: str
    user_agent: str
    created_at: datetime
    last_activity: datetime
    is_active: bool = True


class AuthResponse(BaseModel):
    """通用认证响应模型"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[dict] = Field(None, description="响应数据")


class UserPermissions(BaseModel):
    """用户权限模型"""
    can_query_ip: bool = True
    can_batch_query: bool = True
    can_export_data: bool = False
    can_use_api: bool = False
    daily_query_limit: int = 100
    monthly_query_limit: int = 1000
    
    @validator('daily_query_limit', 'monthly_query_limit')
    def validate_limits(cls, v):
        """验证查询限制"""
        if v < 0:
            raise ValueError('查询限制不能为负数')
        return v
