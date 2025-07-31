"""
异步缓存服务
使用Redis提供高性能缓存功能
"""
import json
import time
from typing import Optional, Dict, Any, List
import redis.asyncio as redis
from redis.asyncio import Redis

from app.config import settings
from app.core.logging import get_logger
from app.core.exceptions import CacheException
from app.models.schemas import IPQueryResult, CacheStats

logger = get_logger(__name__)


class AsyncCacheService:
    """异步缓存服务"""
    
    def __init__(self):
        self.redis: Optional[Redis] = None
        self.stats = {
            "hit_count": 0,
            "miss_count": 0,
            "total_operations": 0
        }
    
    async def initialize(self) -> None:
        """初始化缓存服务"""
        if not settings.redis_enabled:
            logger.info("Redis缓存已禁用")
            return
        
        try:
            # 创建Redis连接
            redis_url = f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}"
            if settings.redis_password:
                redis_url = f"redis://:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}/{settings.redis_db}"
            
            self.redis = await redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            
            # 测试连接
            await self.redis.ping()
            logger.info(f"Redis缓存服务初始化成功: {settings.redis_host}:{settings.redis_port}")
            
        except Exception as e:
            logger.error(f"Redis缓存服务初始化失败: {e}")
            self.redis = None
            # 不抛出异常，允许应用在没有缓存的情况下运行
    
    async def close(self) -> None:
        """关闭缓存服务"""
        if self.redis:
            try:
                await self.redis.close()
                logger.info("Redis缓存服务已关闭")
            except Exception as e:
                logger.error(f"关闭Redis连接时出错: {e}")
            finally:
                self.redis = None
    
    def _get_cache_key(self, ip: str) -> str:
        """生成缓存键"""
        return f"ip_query:{ip}"
    
    async def get_cached_result(self, ip: str) -> Optional[IPQueryResult]:
        """获取缓存的查询结果"""
        if not self.redis:
            return None
        
        try:
            cache_key = self._get_cache_key(ip)
            cached_data = await self.redis.get(cache_key)
            
            if cached_data:
                # 解析缓存数据
                data = json.loads(cached_data)
                result = IPQueryResult(**data)
                result.cached = True
                
                # 更新统计
                self.stats["hit_count"] += 1
                self.stats["total_operations"] += 1
                
                logger.debug(f"缓存命中: {ip}")
                return result
            else:
                # 缓存未命中
                self.stats["miss_count"] += 1
                self.stats["total_operations"] += 1
                
                logger.debug(f"缓存未命中: {ip}")
                return None
                
        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
            return None
    
    async def cache_result(self, result: IPQueryResult) -> bool:
        """缓存查询结果"""
        if not self.redis or result.error:
            return False
        
        try:
            cache_key = self._get_cache_key(result.ip)
            
            # 准备缓存数据
            cache_data = result.dict()
            cache_data["cached"] = False  # 存储时标记为非缓存
            
            # 设置缓存
            await self.redis.setex(
                cache_key,
                settings.cache_ttl,
                json.dumps(cache_data, ensure_ascii=False)
            )
            
            logger.debug(f"缓存已保存: {result.ip}")
            return True
            
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
            return False
    
    async def cache_batch_results(self, results: List[IPQueryResult]) -> int:
        """批量缓存查询结果"""
        if not self.redis:
            return 0
        
        cached_count = 0
        
        try:
            # 使用管道批量操作
            pipe = self.redis.pipeline()
            
            for result in results:
                if not result.error:
                    cache_key = self._get_cache_key(result.ip)
                    cache_data = result.model_dump()
                    cache_data["cached"] = False
                    
                    pipe.setex(
                        cache_key,
                        settings.cache_ttl,
                        json.dumps(cache_data, ensure_ascii=False)
                    )
                    cached_count += 1
            
            # 执行批量操作
            if cached_count > 0:
                await pipe.execute()
                logger.debug(f"批量缓存完成: {cached_count} 条记录")
            
        except Exception as e:
            logger.error(f"批量缓存失败: {e}")
            cached_count = 0
        
        return cached_count
    
    async def get_cache_stats(self) -> CacheStats:
        """获取缓存统计信息"""
        if not self.redis:
            return CacheStats(
                enabled=False,
                total_keys=0,
                hit_count=self.stats["hit_count"],
                miss_count=self.stats["miss_count"],
                hit_rate=0.0
            )
        
        try:
            # 获取Redis信息
            info = await self.redis.info()
            total_keys = info.get("db0", {}).get("keys", 0) if "db0" in info else 0
            
            # 计算命中率
            total_requests = self.stats["hit_count"] + self.stats["miss_count"]
            hit_rate = (
                self.stats["hit_count"] / total_requests 
                if total_requests > 0 else 0.0
            )
            
            return CacheStats(
                enabled=True,
                total_keys=total_keys,
                hit_count=self.stats["hit_count"],
                miss_count=self.stats["miss_count"],
                hit_rate=round(hit_rate, 4),
                memory_usage=info.get("used_memory_human", "N/A")
            )
            
        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
            return CacheStats(
                enabled=True,
                total_keys=0,
                hit_count=self.stats["hit_count"],
                miss_count=self.stats["miss_count"],
                hit_rate=0.0
            )
    
    async def clear_cache(self) -> bool:
        """清空缓存"""
        if not self.redis:
            return False
        
        try:
            await self.redis.flushdb()
            logger.info("缓存已清空")
            return True
            
        except Exception as e:
            logger.error(f"清空缓存失败: {e}")
            return False
    
    async def delete_cache(self, ip: str) -> bool:
        """删除指定IP的缓存"""
        if not self.redis:
            return False
        
        try:
            cache_key = self._get_cache_key(ip)
            result = await self.redis.delete(cache_key)
            return result > 0
            
        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
            return False


# 全局服务实例
cache_service = AsyncCacheService()
