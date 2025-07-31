"""
认证工具函数
"""
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """创建刷新令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """验证令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 检查令牌类型
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 检查过期时间
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing expiration",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if datetime.utcnow() > datetime.fromtimestamp(exp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_from_token(token: str) -> Dict[str, Any]:
    """从令牌中获取用户信息"""
    payload = verify_token(token, "access")
    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def check_user_permissions(user_role: str, required_permissions: list) -> bool:
    """检查用户权限"""
    # 权限层级定义
    role_permissions = {
        "super_admin": [
            "system:read", "system:write", "system:delete",
            "users:read", "users:write", "users:delete",
            "config:read", "config:write", "config:delete",
            "monitoring:read", "monitoring:write",
            "data:read", "data:write", "data:delete",
            "backup:read", "backup:write"
        ],
        "admin": [
            "system:read", "system:write",
            "config:read", "config:write",
            "monitoring:read", "monitoring:write",
            "data:read", "data:write"
        ],
        "readonly": [
            "system:read",
            "monitoring:read",
            "data:read"
        ]
    }
    
    user_permissions = role_permissions.get(user_role, [])
    return all(perm in user_permissions for perm in required_permissions)


def generate_secure_password(length: int = 12) -> str:
    """生成安全密码"""
    import string
    import random
    
    # 确保密码包含各种字符类型
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(random.choice(chars) for _ in range(length))
    return password


def is_password_strong(password: str) -> tuple[bool, str]:
    """检查密码强度"""
    import re
    
    if len(password) < 8:
        return False, "密码长度至少8位"
    
    if not re.search(r"[a-z]", password):
        return False, "密码必须包含小写字母"
    
    if not re.search(r"[A-Z]", password):
        return False, "密码必须包含大写字母"
    
    if not re.search(r"\d", password):
        return False, "密码必须包含数字"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "密码必须包含特殊字符"
    
    return True, "密码强度符合要求"


def check_account_lockout(login_attempts: int, locked_until: Optional[datetime]) -> bool:
    """检查账户是否被锁定"""
    if locked_until and datetime.utcnow() < locked_until:
        return True
    
    # 超过5次失败尝试锁定账户
    if login_attempts >= 5:
        return True
    
    return False


def calculate_lockout_time(login_attempts: int) -> Optional[datetime]:
    """计算锁定时间"""
    if login_attempts >= 5:
        # 锁定时间递增：5次=5分钟，6次=10分钟，7次=30分钟，8次及以上=1小时
        lockout_minutes = {
            5: 5,
            6: 10,
            7: 30
        }.get(login_attempts, 60)
        
        return datetime.utcnow() + timedelta(minutes=lockout_minutes)
    
    return None


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """遮蔽敏感数据"""
    if len(data) <= visible_chars:
        return mask_char * len(data)
    
    return data[:visible_chars] + mask_char * (len(data) - visible_chars)


def log_security_event(event_type: str, user_id: Optional[int], details: Dict[str, Any]) -> None:
    """记录安全事件"""
    # 这里可以集成到日志系统或安全审计系统
    import logging
    
    logger = logging.getLogger("security")
    logger.info(f"Security Event: {event_type}", extra={
        "user_id": user_id,
        "event_type": event_type,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    })
