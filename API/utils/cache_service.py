"""
缓存服务模块
支持内存缓存和Redis缓存
"""
import json
import time
import hashlib
import os
from typing import Any, Optional, Dict
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# 尝试导入Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis未安装，将使用内存缓存")

class MemoryCache:
    """内存缓存实现"""
    
    def __init__(self, default_ttl: int = 3600):
        self._cache: Dict[str, Dict] = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key not in self._cache:
            return None
        
        item = self._cache[key]
        if time.time() > item['expires']:
            del self._cache[key]
            return None
        
        return item['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        if ttl is None:
            ttl = self.default_ttl
        
        self._cache[key] = {
            'value': value,
            'expires': time.time() + ttl
        }
        return True
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> bool:
        """清空所有缓存"""
        self._cache.clear()
        return True
    
    def cleanup_expired(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            key for key, item in self._cache.items()
            if current_time > item['expires']
        ]
        for key in expired_keys:
            del self._cache[key]
        
        logger.info(f"清理了{len(expired_keys)}个过期缓存项")

class RedisCache:
    """Redis缓存实现"""

    def __init__(self,
                 host: str = 'localhost',
                 port: int = 6379,
                 db: int = 0,
                 password: Optional[str] = None,
                 default_ttl: int = 3600):

        if not REDIS_AVAILABLE:
            raise ImportError("Redis未安装，无法使用Redis缓存")

        self.default_ttl = default_ttl
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )

        # 测试连接
        try:
            self.redis_client.ping()
            logger.info(f"Redis连接成功: {host}:{port}")
        except redis.ConnectionError as e:
            logger.error(f"Redis连接失败: {e}")
            raise

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.error(f"Redis获取缓存失败: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            if ttl is None:
                ttl = self.default_ttl

            json_value = json.dumps(value, ensure_ascii=False)
            return self.redis_client.setex(key, ttl, json_value)
        except (redis.RedisError, json.JSONEncodeError) as e:
            logger.error(f"Redis设置缓存失败: {e}")
            return False

    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            return bool(self.redis_client.delete(key))
        except redis.RedisError as e:
            logger.error(f"Redis删除缓存失败: {e}")
            return False

    def clear(self) -> bool:
        """清空所有缓存"""
        try:
            return self.redis_client.flushdb()
        except redis.RedisError as e:
            logger.error(f"Redis清空缓存失败: {e}")
            return False

    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return bool(self.redis_client.exists(key))
        except redis.RedisError as e:
            logger.error(f"Redis检查键存在失败: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """获取Redis统计信息"""
        try:
            info = self.redis_client.info()
            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'total_commands_processed': info.get('total_commands_processed', 0)
            }
        except redis.RedisError as e:
            logger.error(f"获取Redis统计信息失败: {e}")
            return {}

class CacheService:
    """统一缓存服务"""

    def __init__(self, cache_type: str = "auto", **kwargs):
        self.cache_type = cache_type

        # 自动选择缓存类型
        if cache_type == "auto":
            # 优先使用Redis，如果不可用则使用内存缓存
            if REDIS_AVAILABLE and self._test_redis_connection(**kwargs):
                cache_type = "redis"
            else:
                cache_type = "memory"
                logger.info("Redis不可用，使用内存缓存")

        if cache_type == "redis":
            if not REDIS_AVAILABLE:
                logger.warning("Redis未安装，回退到内存缓存")
                self.cache = MemoryCache(kwargs.get('default_ttl', 3600))
                self.cache_type = "memory"
            else:
                try:
                    self.cache = RedisCache(**kwargs)
                    self.cache_type = "redis"
                    logger.info("使用Redis缓存")
                except Exception as e:
                    logger.warning(f"Redis初始化失败，回退到内存缓存: {e}")
                    self.cache = MemoryCache(kwargs.get('default_ttl', 3600))
                    self.cache_type = "memory"
        else:
            self.cache = MemoryCache(kwargs.get('default_ttl', 3600))
            self.cache_type = "memory"
            logger.info("使用内存缓存")

    def _test_redis_connection(self, **kwargs) -> bool:
        """测试Redis连接"""
        try:
            host = kwargs.get('host', os.getenv('REDIS_HOST', 'localhost'))
            port = kwargs.get('port', int(os.getenv('REDIS_PORT', 6379)))
            password = kwargs.get('password', os.getenv('REDIS_PASSWORD'))

            test_client = redis.Redis(
                host=host,
                port=port,
                password=password,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            test_client.ping()
            return True
        except:
            return False
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        # 将参数转换为字符串并生成哈希
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_ip_cache(self, ip: str) -> Optional[Dict]:
        """获取IP查询缓存"""
        key = self._generate_key("ip_query", ip)
        return self.cache.get(key)
    
    def set_ip_cache(self, ip: str, result: Dict, ttl: int = 3600) -> bool:
        """设置IP查询缓存"""
        key = self._generate_key("ip_query", ip)
        return self.cache.set(key, result, ttl)
    
    def get_batch_cache(self, ips: list) -> Optional[Dict]:
        """获取批量查询缓存"""
        # 对IP列表排序以确保缓存键一致
        sorted_ips = sorted(ips)
        key = self._generate_key("batch_query", *sorted_ips)
        return self.cache.get(key)
    
    def set_batch_cache(self, ips: list, results: list, ttl: int = 1800) -> bool:
        """设置批量查询缓存"""
        sorted_ips = sorted(ips)
        key = self._generate_key("batch_query", *sorted_ips)
        return self.cache.set(key, results, ttl)
    
    def clear_all(self) -> bool:
        """清空所有缓存"""
        return self.cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        base_stats = {
            'cache_type': self.cache_type,
            'status': 'active'
        }

        if hasattr(self.cache, 'get_stats'):
            cache_stats = self.cache.get_stats()
            base_stats.update(cache_stats)

        return base_stats

# 创建全局缓存服务实例
cache_service = CacheService(
    cache_type=os.getenv('CACHE_TYPE', 'auto'),
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    password=os.getenv('REDIS_PASSWORD'),
    default_ttl=int(os.getenv('CACHE_TTL', 3600))
)

def cache_ip_query(ttl: int = 3600):
    """IP查询缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, ip: str, *args, **kwargs):
            # 尝试从缓存获取
            cached_result = cache_service.get_ip_cache(ip)
            if cached_result is not None:
                logger.info(f"从缓存获取IP查询结果: {ip}")
                return cached_result
            
            # 执行查询
            result = func(self, ip, *args, **kwargs)
            
            # 缓存结果（只缓存成功的查询）
            if result and not result.get('error'):
                cache_service.set_ip_cache(ip, result, ttl)
                logger.info(f"缓存IP查询结果: {ip}")
            
            return result
        return wrapper
    return decorator

def cache_batch_query(ttl: int = 1800):
    """批量查询缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, ips: list, *args, **kwargs):
            # 检查是否有缓存的结果
            cached_results = []
            uncached_ips = []
            
            for ip in ips:
                cached_result = cache_service.get_ip_cache(ip)
                if cached_result is not None:
                    cached_results.append(cached_result)
                    logger.info(f"从缓存获取IP: {ip}")
                else:
                    uncached_ips.append(ip)
            
            # 查询未缓存的IP
            if uncached_ips:
                new_results = func(self, uncached_ips, *args, **kwargs)
                
                # 缓存新的查询结果
                for ip, result in zip(uncached_ips, new_results):
                    if result and not result.get('error'):
                        cache_service.set_ip_cache(ip, result, ttl)
                
                # 合并结果
                all_results = cached_results + new_results
            else:
                all_results = cached_results
            
            return all_results
        return wrapper
    return decorator
