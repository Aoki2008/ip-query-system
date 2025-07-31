"""
用户数据模型
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
import uuid


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    full_name: Optional[str] = Field(None, max_length=100, description="真实姓名")
    
    @validator('username')
    def validate_username(cls, v):
        """验证用户名格式"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('用户名只能包含字母、数字、下划线和连字符')
        return v.lower()


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    confirm_password: str = Field(..., description="确认密码")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """验证密码确认"""
        if 'password' in values and v != values['password']:
            raise ValueError('两次输入的密码不一致')
        return v


class UserUpdate(BaseModel):
    """用户更新模型"""
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = Field(None, max_length=500)


class UserPasswordUpdate(BaseModel):
    """密码更新模型"""
    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")
    confirm_password: str = Field(..., description="确认新密码")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """验证密码确认"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的新密码不一致')
        return v


class UserInDB(UserBase):
    """数据库中的用户模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    password_hash: str
    avatar_url: Optional[str] = None
    is_active: bool = True
    is_premium: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class User(UserBase):
    """用户响应模型"""
    id: str
    avatar_url: Optional[str] = None
    is_active: bool
    is_premium: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserProfile(User):
    """用户详细资料模型"""
    query_count: int = 0
    last_query_at: Optional[datetime] = None


class UserStats(BaseModel):
    """用户统计模型"""
    total_queries: int = 0
    queries_today: int = 0
    queries_this_month: int = 0
    success_rate: float = 0.0
    avg_response_time: float = 0.0
    most_queried_ips: List[dict] = []
    query_trend: List[dict] = []


class UserSettings(BaseModel):
    """用户设置模型"""
    theme: str = Field(default="auto", description="主题设置")
    language: str = Field(default="zh-CN", description="语言设置")
    timezone: str = Field(default="Asia/Shanghai", description="时区设置")
    email_notifications: bool = Field(default=True, description="邮件通知")
    history_retention_days: int = Field(default=90, description="历史记录保留天数")
    
    @validator('theme')
    def validate_theme(cls, v):
        """验证主题设置"""
        allowed_themes = ['light', 'dark', 'auto']
        if v not in allowed_themes:
            raise ValueError(f'主题必须是: {", ".join(allowed_themes)}')
        return v
    
    @validator('history_retention_days')
    def validate_retention_days(cls, v):
        """验证历史记录保留天数"""
        if v < 1 or v > 365:
            raise ValueError('历史记录保留天数必须在1-365天之间')
        return v
