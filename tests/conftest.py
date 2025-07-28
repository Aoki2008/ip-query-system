"""
pytest配置文件
定义测试夹具和配置
"""
import pytest
import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, patch

# 添加API目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'API'))

@pytest.fixture
def mock_geoip_database():
    """模拟GeoIP数据库"""
    with patch('geoip2.database.Reader') as mock_reader:
        # 模拟查询结果
        mock_response = Mock()
        mock_response.country.name = "United States"
        mock_response.country.iso_code = "US"
        mock_response.subdivisions.most_specific.name = "California"
        mock_response.city.name = "Mountain View"
        mock_response.postal.code = "94043"
        mock_response.location.latitude = 37.4056
        mock_response.location.longitude = -122.0775
        mock_response.location.accuracy_radius = 1000
        mock_response.location.time_zone = "America/Los_Angeles"
        
        mock_reader.return_value.__enter__.return_value.city.return_value = mock_response
        yield mock_reader

@pytest.fixture
def temp_db_file():
    """创建临时数据库文件"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mmdb')
    temp_file.write(b'fake_geoip_data')
    temp_file.close()
    
    yield temp_file.name
    
    # 清理
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)

@pytest.fixture
def mock_redis():
    """模拟Redis连接"""
    with patch('redis.Redis') as mock_redis_class:
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.get.return_value = None
        mock_redis_instance.setex.return_value = True
        mock_redis_instance.delete.return_value = 1
        mock_redis_instance.flushdb.return_value = True
        mock_redis_instance.exists.return_value = False
        mock_redis_instance.info.return_value = {
            'connected_clients': 1,
            'used_memory_human': '1M',
            'keyspace_hits': 100,
            'keyspace_misses': 10,
            'total_commands_processed': 1000
        }
        
        mock_redis_class.return_value = mock_redis_instance
        yield mock_redis_instance

@pytest.fixture
def test_app():
    """创建测试Flask应用"""
    from app import app
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def async_test_app():
    """创建异步测试Flask应用"""
    from async_app import app
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def sample_ips():
    """测试用IP地址样本"""
    return {
        'valid': ['8.8.8.8', '1.1.1.1', '114.114.114.114'],
        'invalid': ['invalid.ip', '999.999.999.999', '192.168.1'],
        'private': ['192.168.1.1', '10.0.0.1', '172.16.0.1'],
        'localhost': ['127.0.0.1', '::1']
    }

@pytest.fixture(autouse=True)
def setup_test_environment():
    """设置测试环境"""
    # 设置测试环境变量
    os.environ['TESTING'] = 'True'
    os.environ['CACHE_TYPE'] = 'memory'  # 测试时使用内存缓存
    os.environ['LOG_LEVEL'] = 'WARNING'  # 减少测试时的日志输出
    
    yield
    
    # 清理环境变量
    test_vars = ['TESTING', 'CACHE_TYPE', 'LOG_LEVEL']
    for var in test_vars:
        if var in os.environ:
            del os.environ[var]
