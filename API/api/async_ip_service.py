"""
异步IP查询服务
支持高并发的异步IP地址查询
"""
import asyncio
import geoip2.database
import logging
import os
import time
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from utils.validators import IPValidator
from utils.cache_service import cache_service

logger = logging.getLogger(__name__)

class AsyncIPService:
    """异步IP查询服务"""
    
    def __init__(self, db_path: Optional[str] = None, max_workers: int = 10):
        """
        初始化异步IP服务
        
        Args:
            db_path: GeoIP数据库路径
            max_workers: 最大工作线程数
        """
        self.db_path = db_path or os.path.join(os.path.dirname(__file__), '..', 'GeoLite2-City.mmdb')
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.ip_validator = IPValidator()
        
        # 验证数据库文件
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"GeoIP数据库文件未找到: {self.db_path}")
        
        logger.info(f"异步IP服务初始化完成，数据库: {self.db_path}, 最大工作线程: {max_workers}")
    
    def _query_ip_sync(self, ip: str) -> Dict[str, Any]:
        """
        同步查询单个IP（在线程池中执行）
        
        Args:
            ip: IP地址
            
        Returns:
            Dict: 查询结果
        """
        try:
            with geoip2.database.Reader(self.db_path) as reader:
                response = reader.city(ip)
                
                return {
                    'ip': ip,
                    'country': response.country.name or '未知',
                    'country_code': response.country.iso_code or '',
                    'region': response.subdivisions.most_specific.name or '未知',
                    'city': response.city.name or '未知',
                    'postal_code': response.postal.code or '',
                    'latitude': float(response.location.latitude) if response.location.latitude else 0.0,
                    'longitude': float(response.location.longitude) if response.location.longitude else 0.0,
                    'accuracy_radius': response.location.accuracy_radius or 0,
                    'timezone': response.location.time_zone or '未知',
                    'isp': '未知',  # GeoLite2不包含ISP信息
                    'organization': '未知'
                }
                
        except geoip2.errors.AddressNotFoundError:
            return {
                'ip': ip,
                'country': '未知',
                'country_code': '',
                'region': '未知', 
                'city': '未知',
                'postal_code': '',
                'latitude': 0.0,
                'longitude': 0.0,
                'accuracy_radius': 0,
                'timezone': '未知',
                'isp': '未知',
                'organization': '未知',
                'error': 'IP地址未找到'
            }
        except Exception as e:
            logger.error(f"查询IP {ip} 失败: {str(e)}")
            return {
                'ip': ip,
                'error': f'查询失败: {str(e)}'
            }
    
    async def query_ip(self, ip: str) -> Dict[str, Any]:
        """
        异步查询单个IP地址
        
        Args:
            ip: IP地址
            
        Returns:
            Dict: 查询结果
        """
        # 验证IP地址
        if not self.ip_validator.is_valid_ip(ip):
            return {
                'ip': ip,
                'error': 'IP地址格式无效'
            }
        
        # 检查缓存
        cache_key = f"ip_query:{ip}"
        cached_result = cache_service.get_ip_cache(ip)
        if cached_result:
            logger.info(f"从缓存获取IP查询结果: {ip}")
            return cached_result
        
        # 异步执行查询
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self.executor, self._query_ip_sync, ip)
        
        # 缓存结果（只缓存成功的查询）
        if not result.get('error'):
            cache_service.set_ip_cache(ip, result, ttl=3600)
            logger.info(f"缓存IP查询结果: {ip}")
        
        return result
    
    async def query_batch_ips(self, ips: List[str], batch_size: int = 50) -> List[Dict[str, Any]]:
        """
        异步批量查询IP地址
        
        Args:
            ips: IP地址列表
            batch_size: 批处理大小
            
        Returns:
            List[Dict]: 查询结果列表
        """
        if not ips:
            return []
        
        logger.info(f"开始异步批量查询，共{len(ips)}个IP，批大小{batch_size}")
        start_time = time.time()
        
        # 验证所有IP地址
        valid_ips = []
        results = []
        
        for ip in ips:
            if self.ip_validator.is_valid_ip(ip):
                valid_ips.append(ip)
            else:
                results.append({
                    'ip': ip,
                    'error': 'IP地址格式无效'
                })
        
        if not valid_ips:
            return results
        
        # 检查缓存
        cached_results = []
        uncached_ips = []
        
        for ip in valid_ips:
            cached_result = cache_service.get_ip_cache(ip)
            if cached_result:
                cached_results.append(cached_result)
                logger.debug(f"从缓存获取: {ip}")
            else:
                uncached_ips.append(ip)
        
        logger.info(f"缓存命中: {len(cached_results)}, 需要查询: {len(uncached_ips)}")
        
        # 异步查询未缓存的IP
        if uncached_ips:
            # 分批处理以避免过载
            new_results = []
            for i in range(0, len(uncached_ips), batch_size):
                batch = uncached_ips[i:i + batch_size]
                
                # 创建异步任务
                tasks = [self.query_ip(ip) for ip in batch]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 处理结果
                for result in batch_results:
                    if isinstance(result, Exception):
                        logger.error(f"批量查询异常: {result}")
                        new_results.append({
                            'ip': 'unknown',
                            'error': f'查询异常: {str(result)}'
                        })
                    else:
                        new_results.append(result)
                
                # 避免过快的请求
                if i + batch_size < len(uncached_ips):
                    await asyncio.sleep(0.1)
            
            # 合并结果
            all_results = cached_results + new_results
        else:
            all_results = cached_results
        
        # 添加验证失败的结果
        all_results.extend(results)
        
        end_time = time.time()
        logger.info(f"异步批量查询完成，耗时{end_time - start_time:.2f}秒，成功{len([r for r in all_results if not r.get('error')])}个")
        
        return all_results
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        return {
            'service_type': 'async',
            'max_workers': self.max_workers,
            'database_path': self.db_path,
            'database_exists': os.path.exists(self.db_path),
            'cache_stats': cache_service.get_cache_stats()
        }
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)

# 创建全局异步IP服务实例
async_ip_service = AsyncIPService(
    max_workers=int(os.getenv('IP_SERVICE_MAX_WORKERS', 10))
)
