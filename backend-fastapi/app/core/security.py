"""
安全工具模块
提供密码哈希、JWT令牌等安全功能
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
SECRET_KEY = getattr(settings, 'secret_key', secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


class SecurityManager:
    """安全管理器"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """哈希密码"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        
        try:
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            logger.debug(f"创建访问令牌成功，用户: {data.get('sub')}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"创建访问令牌失败: {e}")
            raise
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """创建刷新令牌"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        try:
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            logger.debug(f"创建刷新令牌成功，用户: {data.get('sub')}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"创建刷新令牌失败: {e}")
            raise
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # 检查令牌类型
            if payload.get("type") != token_type:
                logger.warning(f"令牌类型不匹配: 期望 {token_type}, 实际 {payload.get('type')}")
                return None
            
            # 检查过期时间
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                logger.warning("令牌已过期")
                return None
            
            return payload
            
        except JWTError as e:
            logger.warning(f"令牌验证失败: {e}")
            return None
        except Exception as e:
            logger.error(f"令牌验证异常: {e}")
            return None
    
    @staticmethod
    def generate_reset_token(email: str) -> str:
        """生成密码重置令牌"""
        data = {
            "email": email,
            "purpose": "password_reset",
            "exp": datetime.utcnow() + timedelta(hours=1)  # 1小时有效期
        }
        return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def verify_reset_token(token: str) -> Optional[str]:
        """验证密码重置令牌"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            if payload.get("purpose") != "password_reset":
                return None
            
            return payload.get("email")
            
        except JWTError:
            return None
    
    @staticmethod
    def generate_verification_token(email: str) -> str:
        """生成邮箱验证令牌"""
        data = {
            "email": email,
            "purpose": "email_verification",
            "exp": datetime.utcnow() + timedelta(days=1)  # 24小时有效期
        }
        return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def verify_verification_token(token: str) -> Optional[str]:
        """验证邮箱验证令牌"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            if payload.get("purpose") != "email_verification":
                return None
            
            return payload.get("email")
            
        except JWTError:
            return None
    
    @staticmethod
    def generate_api_key(user_id: str, key_name: str) -> str:
        """生成API密钥"""
        # 创建唯一的API密钥
        timestamp = str(int(datetime.utcnow().timestamp()))
        raw_key = f"{user_id}:{key_name}:{timestamp}:{secrets.token_urlsafe(32)}"
        
        # 使用SHA256哈希
        api_key = hashlib.sha256(raw_key.encode()).hexdigest()
        
        return f"ipq_{api_key[:32]}"
    
    @staticmethod
    def generate_session_id() -> str:
        """生成会话ID"""
        return secrets.token_urlsafe(32)


# 全局安全管理器实例
security = SecurityManager()
