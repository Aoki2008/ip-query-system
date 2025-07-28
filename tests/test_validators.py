"""
验证器模块测试
"""
import pytest
from utils.validators import IPValidator, RequestValidator, is_valid_ip

class TestIPValidator:
    """IP验证器测试"""
    
    def setup_method(self):
        """设置测试方法"""
        self.validator = IPValidator()
    
    def test_valid_ipv4_addresses(self):
        """测试有效的IPv4地址"""
        valid_ips = [
            '8.8.8.8',
            '192.168.1.1',
            '10.0.0.1',
            '172.16.0.1',
            '127.0.0.1',
            '0.0.0.0',
            '255.255.255.255'
        ]
        
        for ip in valid_ips:
            assert self.validator.is_valid_ip(ip), f"IP {ip} 应该是有效的"
    
    def test_invalid_ip_addresses(self):
        """测试无效的IP地址"""
        invalid_ips = [
            'invalid.ip',
            '999.999.999.999',
            '192.168.1',
            '192.168.1.1.1',
            '192.168.1.256',
            '',
            None,
            '192.168.1.-1',
            'abc.def.ghi.jkl'
        ]
        
        for ip in invalid_ips:
            assert not self.validator.is_valid_ip(ip), f"IP {ip} 应该是无效的"
    
    def test_is_public_ip(self):
        """测试公网IP检查"""
        # 公网IP
        public_ips = ['8.8.8.8', '1.1.1.1', '114.114.114.114']
        for ip in public_ips:
            assert self.validator.is_public_ip(ip), f"IP {ip} 应该是公网IP"
        
        # 私有IP
        private_ips = ['192.168.1.1', '10.0.0.1', '172.16.0.1', '127.0.0.1']
        for ip in private_ips:
            assert not self.validator.is_public_ip(ip), f"IP {ip} 应该是私有IP"
    
    def test_validate_ip_list(self):
        """测试IP列表验证"""
        ips = ['8.8.8.8', 'invalid.ip', '1.1.1.1', '999.999.999.999']
        valid_ips, invalid_ips = self.validator.validate_ip_list(ips)
        
        assert len(valid_ips) == 2
        assert len(invalid_ips) == 2
        assert '8.8.8.8' in valid_ips
        assert '1.1.1.1' in valid_ips
        assert 'invalid.ip' in invalid_ips
        assert '999.999.999.999' in invalid_ips
    
    def test_validate_ip_list_max_count(self):
        """测试IP列表数量限制"""
        ips = ['8.8.8.8'] * 101  # 超过默认限制100
        
        with pytest.raises(ValueError, match="IP地址数量不能超过100个"):
            self.validator.validate_ip_list(ips)
    
    def test_sanitize_ip(self):
        """测试IP地址清理"""
        # 正常IP
        assert self.validator.sanitize_ip('8.8.8.8') == '8.8.8.8'
        
        # 带空格的IP
        assert self.validator.sanitize_ip('  8.8.8.8  ') == '8.8.8.8'
        
        # 无效IP
        assert self.validator.sanitize_ip('invalid.ip') is None
        assert self.validator.sanitize_ip('') is None
        assert self.validator.sanitize_ip(None) is None

class TestRequestValidator:
    """请求验证器测试"""
    
    def setup_method(self):
        """设置测试方法"""
        self.validator = RequestValidator()
    
    def test_validate_single_ip_request(self):
        """测试单个IP请求验证"""
        # 有效IP
        result = self.validator.validate_single_ip_request('8.8.8.8')
        assert result == '8.8.8.8'
        
        # 带空格的IP
        result = self.validator.validate_single_ip_request('  1.1.1.1  ')
        assert result == '1.1.1.1'
        
        # 无效IP
        with pytest.raises(ValueError, match="IP地址格式无效"):
            self.validator.validate_single_ip_request('invalid.ip')
        
        # 空IP
        with pytest.raises(ValueError, match="IP参数不能为空"):
            self.validator.validate_single_ip_request('')
    
    def test_validate_batch_ip_request(self):
        """测试批量IP请求验证"""
        # 有效请求
        data = {'ips': ['8.8.8.8', '1.1.1.1']}
        result = self.validator.validate_batch_ip_request(data)
        assert len(result) == 2
        assert '8.8.8.8' in result
        assert '1.1.1.1' in result
        
        # 缺少ips字段
        with pytest.raises(ValueError, match="请求参数缺少ips字段"):
            self.validator.validate_batch_ip_request({})
        
        # ips不是数组
        with pytest.raises(ValueError, match="ips参数必须是数组格式"):
            self.validator.validate_batch_ip_request({'ips': 'not_array'})
        
        # 空数组
        with pytest.raises(ValueError, match="IP地址列表不能为空"):
            self.validator.validate_batch_ip_request({'ips': []})
        
        # 包含无效IP
        with pytest.raises(ValueError, match="以下IP地址格式无效"):
            self.validator.validate_batch_ip_request({'ips': ['8.8.8.8', 'invalid.ip']})

def test_backward_compatibility():
    """测试向后兼容性"""
    # 测试旧的is_valid_ip函数
    assert is_valid_ip('8.8.8.8') == True
    assert is_valid_ip('invalid.ip') == False
