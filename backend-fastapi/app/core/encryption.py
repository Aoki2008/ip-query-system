"""
数据加密模块
提供数据库字段加密和解密功能
"""
import base64
import secrets
from typing import Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..config import settings


class DataEncryption:
    """数据加密工具类"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        初始化加密工具
        
        Args:
            encryption_key: 加密密钥，如果不提供则从配置获取
        """
        if encryption_key:
            self.key = encryption_key.encode()
        else:
            # 从环境变量获取或生成新密钥
            self.key = self._get_or_generate_key()
        
        self.fernet = Fernet(self._derive_key(self.key))
    
    def _get_or_generate_key(self) -> bytes:
        """获取或生成加密密钥"""
        # 尝试从环境变量获取
        env_key = getattr(settings, 'db_encryption_key', None)
        if env_key and len(env_key) >= 32:
            return env_key.encode()
        
        # 生成新密钥
        return secrets.token_bytes(32)
    
    def _derive_key(self, password: bytes) -> bytes:
        """从密码派生加密密钥"""
        # 使用固定盐值（生产环境应该使用随机盐值并存储）
        salt = b'ip_query_system_salt_2024'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt(self, data: Union[str, bytes]) -> str:
        """
        加密数据
        
        Args:
            data: 要加密的数据
            
        Returns:
            str: Base64编码的加密数据
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted_data = self.fernet.encrypt(data)
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        解密数据
        
        Args:
            encrypted_data: Base64编码的加密数据
            
        Returns:
            str: 解密后的原始数据
        """
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = self.fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            raise ValueError(f"解密失败: {e}")
    
    def encrypt_if_needed(self, data: Optional[str]) -> Optional[str]:
        """
        如果数据不为空则加密
        
        Args:
            data: 要加密的数据
            
        Returns:
            Optional[str]: 加密后的数据或None
        """
        if data is None or data == "":
            return data
        return self.encrypt(data)
    
    def decrypt_if_needed(self, encrypted_data: Optional[str]) -> Optional[str]:
        """
        如果数据不为空则解密
        
        Args:
            encrypted_data: 要解密的数据
            
        Returns:
            Optional[str]: 解密后的数据或None
        """
        if encrypted_data is None or encrypted_data == "":
            return encrypted_data
        
        try:
            return self.decrypt(encrypted_data)
        except ValueError:
            # 如果解密失败，可能是未加密的数据，直接返回
            return encrypted_data


class FieldEncryption:
    """数据库字段加密装饰器"""
    
    def __init__(self, encryption: DataEncryption):
        self.encryption = encryption
    
    def encrypt_field(self, field_name: str):
        """字段加密装饰器"""
        def decorator(cls):
            original_setattr = cls.__setattr__
            original_getattribute = cls.__getattribute__
            
            def new_setattr(self, name, value):
                if name == field_name and value is not None:
                    value = self.encryption.encrypt_if_needed(str(value))
                original_setattr(self, name, value)
            
            def new_getattribute(self, name):
                value = original_getattribute(self, name)
                if name == field_name and value is not None:
                    try:
                        value = self.encryption.decrypt_if_needed(value)
                    except:
                        pass  # 如果解密失败，返回原值
                return value
            
            cls.__setattr__ = new_setattr
            cls.__getattribute__ = new_getattribute
            return cls
        
        return decorator


# 全局加密实例
_encryption_instance = None


def get_encryption() -> DataEncryption:
    """获取全局加密实例"""
    global _encryption_instance
    if _encryption_instance is None:
        _encryption_instance = DataEncryption()
    return _encryption_instance


def encrypt_sensitive_data(data: str) -> str:
    """加密敏感数据的便捷函数"""
    return get_encryption().encrypt(data)


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """解密敏感数据的便捷函数"""
    return get_encryption().decrypt(encrypted_data)


# 敏感字段列表
SENSITIVE_FIELDS = {
    'password',
    'secret',
    'token',
    'key',
    'private',
    'confidential',
    'email',
    'phone',
    'address',
    'credit_card',
    'ssn',
    'id_number'
}


def is_sensitive_field(field_name: str) -> bool:
    """
    检查字段是否为敏感字段
    
    Args:
        field_name: 字段名称
        
    Returns:
        bool: 是否为敏感字段
    """
    field_lower = field_name.lower()
    return any(sensitive in field_lower for sensitive in SENSITIVE_FIELDS)


def auto_encrypt_model(model_class):
    """
    自动加密模型中的敏感字段
    
    Args:
        model_class: 数据模型类
        
    Returns:
        加密后的模型类
    """
    encryption = get_encryption()
    field_encryption = FieldEncryption(encryption)
    
    # 获取模型的所有字段
    if hasattr(model_class, '__table__'):
        # SQLAlchemy模型
        for column in model_class.__table__.columns:
            if is_sensitive_field(column.name):
                model_class = field_encryption.encrypt_field(column.name)(model_class)
    elif hasattr(model_class, '__annotations__'):
        # Pydantic模型
        for field_name in model_class.__annotations__:
            if is_sensitive_field(field_name):
                model_class = field_encryption.encrypt_field(field_name)(model_class)
    
    return model_class


class SecureStorage:
    """安全存储工具"""
    
    def __init__(self):
        self.encryption = get_encryption()
    
    def store_secret(self, key: str, value: str) -> bool:
        """
        安全存储密钥
        
        Args:
            key: 密钥名称
            value: 密钥值
            
        Returns:
            bool: 是否存储成功
        """
        try:
            encrypted_value = self.encryption.encrypt(value)
            # 这里可以存储到数据库或文件
            # 示例：存储到环境变量或配置文件
            return True
        except Exception:
            return False
    
    def retrieve_secret(self, key: str) -> Optional[str]:
        """
        安全检索密钥
        
        Args:
            key: 密钥名称
            
        Returns:
            Optional[str]: 密钥值或None
        """
        try:
            # 这里从存储中检索加密的值
            # encrypted_value = get_from_storage(key)
            # return self.encryption.decrypt(encrypted_value)
            return None
        except Exception:
            return None


# 全局安全存储实例
secure_storage = SecureStorage()
