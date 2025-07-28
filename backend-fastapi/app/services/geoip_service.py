"""
异步GeoIP查询服务
提供高性能的IP地理位置查询功能
"""
import asyncio
import time
from typing import Optional, Dict, Any, List
from pathlib import Path
import geoip2.database
import geoip2.errors
from concurrent.futures import ThreadPoolExecutor

from app.config import settings
from app.core.logging import get_logger
from app.core.exceptions import GeoIPException
from app.models.schemas import IPQueryResult, LocationInfo, ISPInfo

logger = get_logger(__name__)


class AsyncGeoIPService:
    """异步GeoIP查询服务"""
    
    def __init__(self):
        self.db_reader: Optional[geoip2.database.Reader] = None
        self.executor: Optional[ThreadPoolExecutor] = None
        self.stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "total_query_time": 0.0,
            "avg_query_time": 0.0
        }
    
    async def initialize(self) -> None:
        """初始化GeoIP服务"""
        try:
            # 检查数据库文件是否存在
            db_path = Path(settings.geoip_db_path)
            if not db_path.exists():
                # 尝试从API目录复制数据库文件
                api_db_path = Path("API/GeoLite2-City.mmdb")
                if api_db_path.exists():
                    import shutil
                    db_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(api_db_path, db_path)
                    logger.info(f"已复制GeoIP数据库到: {db_path}")
                else:
                    raise GeoIPException(f"GeoIP数据库文件不存在: {db_path}")
            
            # 创建线程池执行器
            self.executor = ThreadPoolExecutor(
                max_workers=settings.concurrent_limit,
                thread_name_prefix="geoip"
            )
            
            # 在线程池中初始化数据库读取器
            self.db_reader = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                geoip2.database.Reader,
                str(db_path)
            )
            
            logger.info(f"GeoIP服务初始化成功，数据库路径: {db_path}")
            
        except Exception as e:
            logger.error(f"GeoIP服务初始化失败: {e}")
            raise GeoIPException(f"GeoIP服务初始化失败: {e}")
    
    async def close(self) -> None:
        """关闭GeoIP服务"""
        try:
            if self.db_reader:
                await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self.db_reader.close
                )
                self.db_reader = None
            
            if self.executor:
                self.executor.shutdown(wait=True)
                self.executor = None
            
            logger.info("GeoIP服务已关闭")
            
        except Exception as e:
            logger.error(f"关闭GeoIP服务时出错: {e}")
    
    def _query_ip_sync(self, ip: str) -> Dict[str, Any]:
        """同步查询IP信息（在线程池中执行）"""
        try:
            if not self.db_reader:
                raise GeoIPException("GeoIP数据库未初始化")
            
            # 查询城市信息
            response = self.db_reader.city(ip)
            
            # 提取位置信息
            location = LocationInfo(
                country=response.country.name,
                country_code=response.country.iso_code,
                region=response.subdivisions.most_specific.name,
                region_code=response.subdivisions.most_specific.iso_code,
                city=response.city.name,
                postal_code=response.postal.code,
                latitude=float(response.location.latitude) if response.location.latitude else None,
                longitude=float(response.location.longitude) if response.location.longitude else None,
                timezone=response.location.time_zone
            )
            
            # 提取ISP信息（如果有ASN数据库）
            isp = ISPInfo()
            try:
                # 尝试查询ASN信息
                if hasattr(response, 'traits') and response.traits.autonomous_system_number:
                    isp.asn = str(response.traits.autonomous_system_number)
                    isp.asn_organization = response.traits.autonomous_system_organization
            except:
                pass  # ASN信息可选
            
            return {
                "location": location.dict(),
                "isp": isp.dict(),
                "success": True
            }
            
        except geoip2.errors.AddressNotFoundError:
            return {
                "location": LocationInfo().dict(),
                "isp": ISPInfo().dict(),
                "success": False,
                "error": "IP地址未找到地理位置信息"
            }
        except Exception as e:
            return {
                "location": LocationInfo().dict(),
                "isp": ISPInfo().dict(),
                "success": False,
                "error": str(e)
            }
    
    async def query_ip(self, ip: str) -> IPQueryResult:
        """异步查询单个IP地址"""
        start_time = time.time()
        
        try:
            if not self.db_reader or not self.executor:
                raise GeoIPException("GeoIP服务未初始化")
            
            # 在线程池中执行查询
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._query_ip_sync,
                ip
            )
            
            query_time = time.time() - start_time
            
            # 更新统计信息
            self._update_stats(query_time, result["success"])
            
            # 构建查询结果
            return IPQueryResult(
                ip=ip,
                location=LocationInfo(**result["location"]),
                isp=ISPInfo(**result["isp"]),
                query_time=query_time,
                cached=False,
                error=result.get("error")
            )
            
        except Exception as e:
            query_time = time.time() - start_time
            self._update_stats(query_time, False)
            
            logger.error(f"查询IP {ip} 失败: {e}")
            return IPQueryResult(
                ip=ip,
                location=LocationInfo(),
                isp=ISPInfo(),
                query_time=query_time,
                cached=False,
                error=str(e)
            )
    
    async def query_batch_ips(self, ips: List[str], batch_size: int = 50) -> List[IPQueryResult]:
        """异步批量查询IP地址"""
        results = []

        # 使用信号量限制并发数
        semaphore = asyncio.Semaphore(settings.concurrent_limit)

        async def query_with_semaphore(ip: str) -> IPQueryResult:
            """带信号量的查询"""
            async with semaphore:
                return await self.query_ip(ip)

        # 分批处理
        for i in range(0, len(ips), batch_size):
            batch = ips[i:i + batch_size]

            # 并发查询当前批次
            tasks = [query_with_semaphore(ip) for ip in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # 处理结果
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"批量查询中出现异常: {result}")
                    # 创建错误结果
                    error_result = IPQueryResult(
                        ip="unknown",
                        location=LocationInfo(),
                        isp=ISPInfo(),
                        query_time=0.0,
                        cached=False,
                        error=str(result)
                    )
                    results.append(error_result)
                else:
                    results.append(result)

        return results
    
    def _update_stats(self, query_time: float, success: bool) -> None:
        """更新统计信息"""
        self.stats["total_queries"] += 1
        self.stats["total_query_time"] += query_time
        
        if success:
            self.stats["successful_queries"] += 1
        else:
            self.stats["failed_queries"] += 1
        
        # 计算平均查询时间
        if self.stats["total_queries"] > 0:
            self.stats["avg_query_time"] = (
                self.stats["total_query_time"] / self.stats["total_queries"]
            )
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        return {
            "geoip_stats": self.stats.copy(),
            "database_path": settings.geoip_db_path,
            "concurrent_limit": settings.concurrent_limit
        }


# 全局服务实例
geoip_service = AsyncGeoIPService()
