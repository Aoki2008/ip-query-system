"""
缓存优化系统
"""
import json
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List
from functools import wraps
import redis
from pydantic import BaseModel

from ..database import SessionLocal


class CacheConfig(BaseModel):
    """缓存配置模型"""
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    default_ttl: int = 3600  # 默认过期时间(秒)
    max_memory: str = "100mb"
    eviction_policy: str = "allkeys-lru"


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.redis_available = False
        try:
            self.redis_client = redis.Redis(
                host=config.redis_host,
                port=config.redis_port,
                db=config.redis_db,
                password=config.redis_password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # 测试连接
            self.redis_client.ping()
            self.redis_available = True
            self._setup_redis_config()
        except Exception as e:
            print(f"Redis连接失败，缓存功能将被禁用: {e}")
            self.redis_client = None
    
    def _setup_redis_config(self):
        """设置Redis配置"""
        try:
            self.redis_client.config_set("maxmemory", self.config.max_memory)
            self.redis_client.config_set("maxmemory-policy", self.config.eviction_policy)
        except Exception as e:
            print(f"Redis配置设置失败: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if not self.redis_available or not self.redis_client:
            return None
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"缓存获取失败: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存"""
        if not self.redis_available or not self.redis_client:
            return False
        try:
            ttl = ttl or self.config.default_ttl
            serialized_value = json.dumps(value, default=str)
            return self.redis_client.setex(key, ttl, serialized_value)
        except Exception as e:
            print(f"缓存设置失败: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"缓存删除失败: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            print(f"缓存检查失败: {e}")
            return False
    
    def get_ttl(self, key: str) -> int:
        """获取缓存剩余时间"""
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            print(f"获取TTL失败: {e}")
            return -1
    
    def extend_ttl(self, key: str, ttl: int) -> bool:
        """延长缓存时间"""
        try:
            return bool(self.redis_client.expire(key, ttl))
        except Exception as e:
            print(f"延长TTL失败: {e}")
            return False
    
    def get_keys_by_pattern(self, pattern: str) -> List[str]:
        """根据模式获取键列表"""
        try:
            return self.redis_client.keys(pattern)
        except Exception as e:
            print(f"获取键列表失败: {e}")
            return []
    
    def delete_by_pattern(self, pattern: str) -> int:
        """根据模式删除缓存"""
        try:
            keys = self.get_keys_by_pattern(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"批量删除失败: {e}")
            return 0
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        try:
            info = self.redis_client.info()
            return {
                "used_memory": info.get("used_memory_human", "0B"),
                "used_memory_peak": info.get("used_memory_peak_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "instantaneous_ops_per_sec": info.get("instantaneous_ops_per_sec", 0),
                "hit_rate": self._calculate_hit_rate(info)
            }
        except Exception as e:
            print(f"获取缓存信息失败: {e}")
            return {}
    
    def _calculate_hit_rate(self, info: Dict) -> float:
        """计算缓存命中率"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0
    
    def flush_all(self) -> bool:
        """清空所有缓存"""
        try:
            return self.redis_client.flushall()
        except Exception as e:
            print(f"清空缓存失败: {e}")
            return False


class IPQueryCache:
    """IP查询缓存"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.cache_prefix = "ip_query:"
        self.default_ttl = 86400  # 24小时
    
    def _generate_cache_key(self, ip_address: str) -> str:
        """生成缓存键"""
        return f"{self.cache_prefix}{ip_address}"
    
    def get_ip_info(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """获取IP信息缓存"""
        cache_key = self._generate_cache_key(ip_address)
        return self.cache_manager.get(cache_key)
    
    def set_ip_info(self, ip_address: str, ip_info: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """设置IP信息缓存"""
        cache_key = self._generate_cache_key(ip_address)
        ttl = ttl or self.default_ttl
        
        # 添加缓存时间戳
        ip_info["cached_at"] = datetime.utcnow().isoformat()
        ip_info["cache_ttl"] = ttl
        
        return self.cache_manager.set(cache_key, ip_info, ttl)
    
    def delete_ip_info(self, ip_address: str) -> bool:
        """删除IP信息缓存"""
        cache_key = self._generate_cache_key(ip_address)
        return self.cache_manager.delete(cache_key)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取IP查询缓存统计"""
        pattern = f"{self.cache_prefix}*"
        keys = self.cache_manager.get_keys_by_pattern(pattern)
        
        total_cached_ips = len(keys)
        
        # 统计不同TTL的缓存
        ttl_distribution = {}
        for key in keys[:100]:  # 限制检查数量
            ttl = self.cache_manager.get_ttl(key)
            if ttl > 0:
                ttl_range = self._get_ttl_range(ttl)
                ttl_distribution[ttl_range] = ttl_distribution.get(ttl_range, 0) + 1
        
        return {
            "total_cached_ips": total_cached_ips,
            "ttl_distribution": ttl_distribution,
            "cache_prefix": self.cache_prefix
        }
    
    def _get_ttl_range(self, ttl: int) -> str:
        """获取TTL范围"""
        if ttl < 3600:
            return "< 1 hour"
        elif ttl < 86400:
            return "1-24 hours"
        elif ttl < 604800:
            return "1-7 days"
        else:
            return "> 7 days"
    
    def cleanup_expired(self) -> int:
        """清理过期缓存"""
        pattern = f"{self.cache_prefix}*"
        keys = self.cache_manager.get_keys_by_pattern(pattern)
        
        expired_count = 0
        for key in keys:
            ttl = self.cache_manager.get_ttl(key)
            if ttl == -2:  # 键不存在
                expired_count += 1
        
        return expired_count


class QueryResultCache:
    """查询结果缓存"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.cache_prefix = "query_result:"
        self.default_ttl = 3600  # 1小时
    
    def _generate_cache_key(self, query_params: Dict[str, Any]) -> str:
        """生成查询缓存键"""
        # 创建查询参数的哈希
        query_string = json.dumps(query_params, sort_keys=True)
        query_hash = hashlib.md5(query_string.encode()).hexdigest()
        return f"{self.cache_prefix}{query_hash}"
    
    def get_query_result(self, query_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """获取查询结果缓存"""
        cache_key = self._generate_cache_key(query_params)
        return self.cache_manager.get(cache_key)
    
    def set_query_result(self, query_params: Dict[str, Any], result: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """设置查询结果缓存"""
        cache_key = self._generate_cache_key(query_params)
        ttl = ttl or self.default_ttl
        
        # 添加缓存元数据
        cached_result = {
            "data": result,
            "cached_at": datetime.utcnow().isoformat(),
            "query_params": query_params,
            "cache_ttl": ttl
        }
        
        return self.cache_manager.set(cache_key, cached_result, ttl)


class StatisticsCache:
    """统计数据缓存"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.cache_prefix = "stats:"
        self.default_ttl = 1800  # 30分钟
    
    def get_statistics(self, stats_type: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """获取统计数据缓存"""
        cache_key = self._generate_stats_key(stats_type, params)
        return self.cache_manager.get(cache_key)
    
    def set_statistics(self, stats_type: str, data: Dict[str, Any], params: Optional[Dict] = None, ttl: Optional[int] = None) -> bool:
        """设置统计数据缓存"""
        cache_key = self._generate_stats_key(stats_type, params)
        ttl = ttl or self.default_ttl
        
        cached_data = {
            "data": data,
            "cached_at": datetime.utcnow().isoformat(),
            "stats_type": stats_type,
            "params": params
        }
        
        return self.cache_manager.set(cache_key, cached_data, ttl)
    
    def _generate_stats_key(self, stats_type: str, params: Optional[Dict] = None) -> str:
        """生成统计缓存键"""
        if params:
            params_string = json.dumps(params, sort_keys=True)
            params_hash = hashlib.md5(params_string.encode()).hexdigest()[:8]
            return f"{self.cache_prefix}{stats_type}:{params_hash}"
        return f"{self.cache_prefix}{stats_type}"
    
    def invalidate_statistics(self, stats_type: str) -> int:
        """使统计缓存失效"""
        pattern = f"{self.cache_prefix}{stats_type}*"
        return self.cache_manager.delete_by_pattern(pattern)


def cache_result(cache_manager: CacheManager, ttl: int = 3600, key_prefix: str = "func:"):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}{func.__name__}:{hashlib.md5(str(args + tuple(kwargs.items())).encode()).hexdigest()[:8]}"
            
            # 尝试从缓存获取
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


class CacheOptimizer:
    """缓存优化器"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
    
    def analyze_cache_performance(self) -> Dict[str, Any]:
        """分析缓存性能"""
        cache_info = self.cache_manager.get_cache_info()
        
        # 计算性能指标
        hit_rate = cache_info.get("hit_rate", 0)
        memory_usage = cache_info.get("used_memory", "0B")
        ops_per_sec = cache_info.get("instantaneous_ops_per_sec", 0)
        
        # 性能评估
        performance_score = self._calculate_performance_score(hit_rate, ops_per_sec)
        
        # 优化建议
        recommendations = self._generate_optimization_recommendations(cache_info)
        
        return {
            "performance_score": performance_score,
            "hit_rate": hit_rate,
            "memory_usage": memory_usage,
            "ops_per_sec": ops_per_sec,
            "recommendations": recommendations,
            "cache_info": cache_info
        }
    
    def _calculate_performance_score(self, hit_rate: float, ops_per_sec: int) -> int:
        """计算性能评分"""
        score = 0
        
        # 命中率评分 (0-60分)
        if hit_rate >= 90:
            score += 60
        elif hit_rate >= 80:
            score += 50
        elif hit_rate >= 70:
            score += 40
        elif hit_rate >= 60:
            score += 30
        else:
            score += int(hit_rate / 2)
        
        # 操作性能评分 (0-40分)
        if ops_per_sec >= 1000:
            score += 40
        elif ops_per_sec >= 500:
            score += 30
        elif ops_per_sec >= 100:
            score += 20
        else:
            score += int(ops_per_sec / 5)
        
        return min(score, 100)
    
    def _generate_optimization_recommendations(self, cache_info: Dict) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        hit_rate = cache_info.get("hit_rate", 0)
        if hit_rate < 80:
            recommendations.append(f"缓存命中率较低({hit_rate:.1f}%)，建议增加缓存时间或优化缓存策略")
        
        ops_per_sec = cache_info.get("instantaneous_ops_per_sec", 0)
        if ops_per_sec > 1000:
            recommendations.append("缓存操作频率较高，建议考虑增加缓存容量")
        
        # 内存使用建议
        used_memory = cache_info.get("used_memory", "0B")
        if "GB" in used_memory:
            recommendations.append("内存使用量较大，建议优化缓存策略或增加内存")
        
        return recommendations
    
    def optimize_cache_settings(self) -> Dict[str, Any]:
        """优化缓存设置"""
        cache_info = self.cache_manager.get_cache_info()
        
        # 基于当前性能调整设置
        optimizations = []
        
        hit_rate = cache_info.get("hit_rate", 0)
        if hit_rate < 70:
            # 调整淘汰策略
            try:
                self.cache_manager.redis_client.config_set("maxmemory-policy", "allkeys-lfu")
                optimizations.append("调整淘汰策略为LFU")
            except:
                pass
        
        return {
            "optimizations_applied": optimizations,
            "new_cache_info": self.cache_manager.get_cache_info()
        }


# 全局缓存管理器实例
cache_config = CacheConfig()
cache_manager = CacheManager(cache_config)
ip_query_cache = IPQueryCache(cache_manager)
query_result_cache = QueryResultCache(cache_manager)
statistics_cache = StatisticsCache(cache_manager)
cache_optimizer = CacheOptimizer(cache_manager)
