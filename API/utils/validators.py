import re
import ipaddress
from typing import Union, List, Tuple, Optional

class IPValidator:
    """IP地址验证工具类"""
    
    def __init__(self):
        # IPv4地址正则表达式
        self.ipv4_pattern = re.compile(
            r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$'
        )
    
    def is_valid_ip(self, ip: str) -> bool:
        """
        验证IP地址是否有效
        
        Args:
            ip: IP地址字符串
            
        Returns:
            bool: 如果IP地址有效返回True，否则返回False
        """
        if not ip or not isinstance(ip, str):
            return False
        
        ip = ip.strip()
        
        try:
            # 使用Python内置的ipaddress模块验证
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    def is_valid_ipv4(self, ip: str) -> bool:
        """
        验证IPv4地址是否有效
        
        Args:
            ip: IP地址字符串
            
        Returns:
            bool: 如果IPv4地址有效返回True，否则返回False
        """
        if not ip or not isinstance(ip, str):
            return False
        
        ip = ip.strip()
        
        try:
            ipaddress.IPv4Address(ip)
            return True
        except ValueError:
            return False
    
    def is_valid_ipv6(self, ip: str) -> bool:
        """
        验证IPv6地址是否有效
        
        Args:
            ip: IP地址字符串
            
        Returns:
            bool: 如果IPv6地址有效返回True，否则返回False
        """
        if not ip or not isinstance(ip, str):
            return False
        
        ip = ip.strip()
        
        try:
            ipaddress.IPv6Address(ip)
            return True
        except ValueError:
            return False
    
    def is_private_ip(self, ip: str) -> bool:
        """
        检查IP地址是否为私有地址
        
        Args:
            ip: IP地址字符串
            
        Returns:
            bool: 如果是私有IP返回True，否则返回False
        """
        if not self.is_valid_ip(ip):
            return False
        
        try:
            ip_obj = ipaddress.ip_address(ip.strip())
            return ip_obj.is_private
        except ValueError:
            return False
    
    def is_loopback_ip(self, ip: str) -> bool:
        """
        检查IP地址是否为回环地址
        
        Args:
            ip: IP地址字符串
            
        Returns:
            bool: 如果是回环IP返回True，否则返回False
        """
        if not self.is_valid_ip(ip):
            return False
        
        try:
            ip_obj = ipaddress.ip_address(ip.strip())
            return ip_obj.is_loopback
        except ValueError:
            return False
    
    def get_ip_type(self, ip: str) -> str:
        """
        获取IP地址类型
        
        Args:
            ip: IP地址字符串
            
        Returns:
            str: IP地址类型描述
        """
        if not self.is_valid_ip(ip):
            return "无效IP"
        
        try:
            ip_obj = ipaddress.ip_address(ip.strip())
            
            if ip_obj.is_loopback:
                return "回环地址"
            elif ip_obj.is_private:
                return "私有地址"
            elif ip_obj.is_multicast:
                return "组播地址"
            elif ip_obj.is_reserved:
                return "保留地址"
            else:
                return "公网地址"
                
        except ValueError:
            return "无效IP"

    def validate_ip_list(self, ips: List[str], max_count: int = 100) -> Tuple[List[str], List[str]]:
        """
        验证IP地址列表

        Args:
            ips: IP地址列表
            max_count: 最大允许的IP数量

        Returns:
            Tuple[List[str], List[str]]: (有效IP列表, 无效IP列表)
        """
        if not isinstance(ips, list):
            raise ValueError("IP列表必须是数组格式")

        if len(ips) > max_count:
            raise ValueError(f"IP地址数量不能超过{max_count}个")

        valid_ips = []
        invalid_ips = []

        for ip in ips:
            if isinstance(ip, str) and ip.strip():
                ip_clean = ip.strip()
                if self.is_valid_ip(ip_clean):
                    valid_ips.append(ip_clean)
                else:
                    invalid_ips.append(ip_clean)

        return valid_ips, invalid_ips

    def sanitize_ip(self, ip: str) -> Optional[str]:
        """
        清理和标准化IP地址

        Args:
            ip: 原始IP地址字符串

        Returns:
            Optional[str]: 标准化后的IP地址，无效时返回None
        """
        if not ip or not isinstance(ip, str):
            return None

        # 移除前后空格
        ip_clean = ip.strip()

        # 验证格式
        if self.is_valid_ip(ip_clean):
            return str(ipaddress.ip_address(ip_clean))

        return None


class RequestValidator:
    """请求参数验证器"""

    def __init__(self):
        self.ip_validator = IPValidator()

    def validate_single_ip_request(self, ip: str) -> str:
        """
        验证单个IP查询请求

        Args:
            ip: IP地址字符串

        Returns:
            str: 清理后的IP地址

        Raises:
            ValueError: 当IP地址无效时
        """
        if not ip:
            raise ValueError("IP参数不能为空")

        clean_ip = self.ip_validator.sanitize_ip(ip)
        if not clean_ip:
            raise ValueError("IP地址格式无效")

        return clean_ip

    def validate_batch_ip_request(self, data: dict) -> List[str]:
        """
        验证批量IP查询请求

        Args:
            data: 请求数据字典

        Returns:
            List[str]: 有效的IP地址列表

        Raises:
            ValueError: 当请求参数无效时
        """
        if not data or 'ips' not in data:
            raise ValueError("请求参数缺少ips字段")

        ips = data['ips']
        if not isinstance(ips, list):
            raise ValueError("ips参数必须是数组格式")

        if not ips:
            raise ValueError("IP地址列表不能为空")

        valid_ips, invalid_ips = self.ip_validator.validate_ip_list(ips)

        if invalid_ips:
            # 只显示前5个无效IP，避免错误信息过长
            invalid_sample = invalid_ips[:5]
            if len(invalid_ips) > 5:
                invalid_sample.append(f"等{len(invalid_ips)}个")
            raise ValueError(f"以下IP地址格式无效: {', '.join(invalid_sample)}")

        if not valid_ips:
            raise ValueError("没有有效的IP地址")

        return valid_ips


# 创建全局实例
ip_validator = IPValidator()
request_validator = RequestValidator()

# 向后兼容的函数
def is_valid_ip(ip: str) -> bool:
    """验证IP地址格式 (向后兼容)"""
    return ip_validator.is_valid_ip(ip)
