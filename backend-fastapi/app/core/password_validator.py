"""
强密码验证模块
实施企业级密码安全策略
"""
import re
import string
from typing import List, Tuple
from collections import Counter

from ..config import settings


class PasswordValidator:
    """强密码验证器"""
    
    # 常见弱密码列表
    COMMON_PASSWORDS = {
        "123456", "password", "123456789", "12345678", "12345", "1234567",
        "1234567890", "qwerty", "abc123", "111111", "123123", "admin",
        "letmein", "welcome", "monkey", "dragon", "master", "sunshine",
        "princess", "football", "charlie", "aa123456", "donald", "password1",
        "qwerty123", "admin123", "root", "toor", "pass", "test", "guest"
    }
    
    # 键盘模式
    KEYBOARD_PATTERNS = [
        "qwerty", "asdf", "zxcv", "1234", "abcd", "qwertyuiop",
        "asdfghjkl", "zxcvbnm", "123456789", "abcdefgh"
    ]
    
    @classmethod
    def validate_password(cls, password: str) -> Tuple[bool, List[str]]:
        """
        验证密码强度
        
        Args:
            password: 待验证的密码
            
        Returns:
            Tuple[bool, List[str]]: (是否通过验证, 错误信息列表)
        """
        errors = []
        
        # 检查长度
        if len(password) < settings.password_min_length:
            errors.append(f"密码长度至少需要{settings.password_min_length}位字符")
        
        # 检查字符类型要求
        if settings.password_require_uppercase and not any(c.isupper() for c in password):
            errors.append("密码必须包含至少一个大写字母")
            
        if settings.password_require_lowercase and not any(c.islower() for c in password):
            errors.append("密码必须包含至少一个小写字母")
            
        if settings.password_require_numbers and not any(c.isdigit() for c in password):
            errors.append("密码必须包含至少一个数字")
            
        if settings.password_require_symbols and not any(c in string.punctuation for c in password):
            errors.append("密码必须包含至少一个特殊字符")
        
        # 检查字符多样性
        unique_chars = len(set(password))
        if unique_chars < settings.password_min_unique_chars:
            errors.append(f"密码至少需要包含{settings.password_min_unique_chars}个不同的字符")
        
        # 检查重复字符
        char_counts = Counter(password)
        max_repeated = max(char_counts.values())
        if max_repeated > settings.password_max_repeated_chars:
            errors.append(f"密码中同一字符重复次数不能超过{settings.password_max_repeated_chars}次")
        
        # 检查常见弱密码
        if password.lower() in cls.COMMON_PASSWORDS:
            errors.append("密码过于常见，请使用更复杂的密码")
        
        # 检查键盘模式
        password_lower = password.lower()
        for pattern in cls.KEYBOARD_PATTERNS:
            if pattern in password_lower or pattern[::-1] in password_lower:
                errors.append("密码不能包含键盘连续字符模式")
                break
        
        # 检查连续字符
        if cls._has_sequential_chars(password):
            errors.append("密码不能包含连续的字符序列")
        
        # 检查重复模式
        if cls._has_repeated_patterns(password):
            errors.append("密码不能包含重复的字符模式")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _has_sequential_chars(password: str, min_length: int = 3) -> bool:
        """检查是否包含连续字符"""
        password_lower = password.lower()
        
        # 检查字母连续
        for i in range(len(password_lower) - min_length + 1):
            substr = password_lower[i:i + min_length]
            if all(ord(substr[j]) == ord(substr[0]) + j for j in range(len(substr))):
                return True
            # 检查倒序连续
            if all(ord(substr[j]) == ord(substr[0]) - j for j in range(len(substr))):
                return True
        
        # 检查数字连续
        for i in range(len(password) - min_length + 1):
            substr = password[i:i + min_length]
            if substr.isdigit():
                if all(int(substr[j]) == int(substr[0]) + j for j in range(len(substr))):
                    return True
                # 检查倒序连续
                if all(int(substr[j]) == int(substr[0]) - j for j in range(len(substr))):
                    return True
        
        return False
    
    @staticmethod
    def _has_repeated_patterns(password: str, min_pattern_length: int = 2) -> bool:
        """检查是否包含重复模式"""
        for pattern_length in range(min_pattern_length, len(password) // 2 + 1):
            for i in range(len(password) - pattern_length * 2 + 1):
                pattern = password[i:i + pattern_length]
                next_part = password[i + pattern_length:i + pattern_length * 2]
                if pattern == next_part:
                    return True
        return False
    
    @classmethod
    def get_password_strength_score(cls, password: str) -> Tuple[int, str]:
        """
        计算密码强度分数
        
        Args:
            password: 密码
            
        Returns:
            Tuple[int, str]: (分数0-100, 强度等级)
        """
        score = 0
        
        # 长度分数 (最多30分)
        length_score = min(30, len(password) * 2)
        score += length_score
        
        # 字符类型分数 (最多40分)
        char_types = 0
        if any(c.islower() for c in password):
            char_types += 1
        if any(c.isupper() for c in password):
            char_types += 1
        if any(c.isdigit() for c in password):
            char_types += 1
        if any(c in string.punctuation for c in password):
            char_types += 1
        
        score += char_types * 10
        
        # 字符多样性分数 (最多20分)
        unique_ratio = len(set(password)) / len(password) if password else 0
        score += int(unique_ratio * 20)
        
        # 复杂性分数 (最多10分)
        if not cls._has_sequential_chars(password):
            score += 5
        if not cls._has_repeated_patterns(password):
            score += 5
        
        # 扣分项
        if password.lower() in cls.COMMON_PASSWORDS:
            score -= 20
        
        # 确保分数在0-100范围内
        score = max(0, min(100, score))
        
        # 确定强度等级
        if score >= 80:
            strength = "很强"
        elif score >= 60:
            strength = "强"
        elif score >= 40:
            strength = "中等"
        elif score >= 20:
            strength = "弱"
        else:
            strength = "很弱"
        
        return score, strength
    
    @classmethod
    def generate_password_suggestions(cls) -> List[str]:
        """生成密码建议"""
        suggestions = [
            "使用至少12个字符的长度",
            "包含大写字母、小写字母、数字和特殊字符",
            "避免使用个人信息（姓名、生日、电话等）",
            "避免使用常见单词或短语",
            "避免使用键盘连续字符（如qwerty、123456）",
            "使用密码管理器生成和存储复杂密码",
            "定期更换密码（建议每90天）",
            "不要在多个账户中重复使用相同密码"
        ]
        return suggestions


def validate_password_strength(password: str) -> dict:
    """
    验证密码强度的便捷函数
    
    Args:
        password: 待验证的密码
        
    Returns:
        dict: 验证结果
    """
    is_valid, errors = PasswordValidator.validate_password(password)
    score, strength = PasswordValidator.get_password_strength_score(password)
    suggestions = PasswordValidator.generate_password_suggestions()
    
    return {
        "is_valid": is_valid,
        "errors": errors,
        "score": score,
        "strength": strength,
        "suggestions": suggestions if not is_valid else []
    }
