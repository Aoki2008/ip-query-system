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
        self.asn_reader: Optional[geoip2.database.Reader] = None
        self.executor: Optional[ThreadPoolExecutor] = None
        self.current_source: str = "local"  # local, api, mixed
        self.available_databases = {}  # 存储可用的数据库信息
        self.stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "total_query_time": 0.0,
            "avg_query_time": 0.0,
            "current_source": "local",
            "available_sources": []
        }
    
    async def initialize(self) -> None:
        """初始化GeoIP服务"""
        try:
            # 创建线程池执行器
            self.executor = ThreadPoolExecutor(
                max_workers=settings.concurrent_limit,
                thread_name_prefix="geoip"
            )

            # 扫描可用的数据库
            await self._scan_available_databases()

            # 设置当前数据源
            self.current_source = settings.current_geoip_source

            # 初始化数据库读取器
            await self._initialize_readers()

            logger.info(f"GeoIP服务初始化成功，当前数据源: {self.current_source}")

        except Exception as e:
            logger.error(f"GeoIP服务初始化失败: {e}")
            raise GeoIPException(f"GeoIP服务初始化失败: {e}")

    async def _scan_available_databases(self) -> None:
        """扫描可用的数据库"""
        self.available_databases = {}
        available_sources = []

        # 检查本地数据库
        local_city_path = Path(settings.geoip_db_path)
        local_asn_path = Path(settings.geoip_asn_db_path)

        if local_city_path.exists():
            self.available_databases["local_city"] = str(local_city_path)
            if "local" not in available_sources:
                available_sources.append("local")

        if local_asn_path.exists():
            self.available_databases["local_asn"] = str(local_asn_path)
            if "local" not in available_sources:
                available_sources.append("local")

        # 检查API目录数据库
        api_city_path = Path("API/GeoLite2-City.mmdb")
        api_asn_path = Path("API/GeoLite2-ASN.mmdb")

        if api_city_path.exists():
            self.available_databases["api_city"] = str(api_city_path)
            if "api" not in available_sources:
                available_sources.append("api")

        if api_asn_path.exists():
            self.available_databases["api_asn"] = str(api_asn_path)
            if "api" not in available_sources:
                available_sources.append("api")

        # 如果两个源都可用，添加混合模式
        if "local" in available_sources and "api" in available_sources:
            available_sources.append("mixed")

        self.stats["available_sources"] = available_sources
        logger.info(f"发现可用数据库: {self.available_databases}")
        logger.info(f"可用数据源: {available_sources}")

    async def _initialize_readers(self) -> None:
        """根据当前数据源初始化读取器"""
        try:
            # 关闭现有读取器
            if self.db_reader:
                await asyncio.get_event_loop().run_in_executor(
                    self.executor, self.db_reader.close
                )
                self.db_reader = None

            if self.asn_reader:
                await asyncio.get_event_loop().run_in_executor(
                    self.executor, self.asn_reader.close
                )
                self.asn_reader = None

            # 根据数据源选择数据库
            city_db_path = None
            asn_db_path = None

            if self.current_source == "local":
                city_db_path = self.available_databases.get("local_city")
                asn_db_path = self.available_databases.get("local_asn")
            elif self.current_source == "api":
                city_db_path = self.available_databases.get("api_city")
                asn_db_path = self.available_databases.get("api_asn")
            elif self.current_source == "mixed":
                # 混合模式：优先使用本地，回退到API
                city_db_path = (self.available_databases.get("local_city") or
                               self.available_databases.get("api_city"))
                asn_db_path = (self.available_databases.get("local_asn") or
                              self.available_databases.get("api_asn"))

            # 初始化城市数据库
            if city_db_path:
                self.db_reader = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    geoip2.database.Reader,
                    city_db_path
                )
                logger.info(f"城市数据库初始化成功: {city_db_path}")
            else:
                logger.warning("未找到可用的城市数据库")

            # 初始化ASN数据库
            if asn_db_path:
                self.asn_reader = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    geoip2.database.Reader,
                    asn_db_path
                )
                logger.info(f"ASN数据库初始化成功: {asn_db_path}")
            else:
                logger.warning("未找到可用的ASN数据库")

            # 更新统计信息
            self.stats["current_source"] = self.current_source

        except Exception as e:
            logger.error(f"初始化数据库读取器失败: {e}")
            raise
    
    async def close(self) -> None:
        """关闭GeoIP服务"""
        try:
            if self.db_reader:
                await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self.db_reader.close
                )
                self.db_reader = None

            if self.asn_reader:
                await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self.asn_reader.close
                )
                self.asn_reader = None

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
            
            # 提取ISP信息
            isp = ISPInfo()

            # 首先尝试从城市数据库获取ASN信息
            try:
                if hasattr(response, 'traits') and response.traits.autonomous_system_number:
                    isp.asn = str(response.traits.autonomous_system_number)
                    isp.asn_organization = response.traits.autonomous_system_organization
                    isp.isp = response.traits.autonomous_system_organization
                    isp.organization = response.traits.autonomous_system_organization
            except:
                pass

            # 如果有专门的ASN数据库，使用它获取更详细的ISP信息
            if self.asn_reader and (not isp.asn or not isp.isp):
                try:
                    asn_response = self.asn_reader.asn(ip)
                    if asn_response.autonomous_system_number:
                        isp.asn = str(asn_response.autonomous_system_number)
                        isp.asn_organization = asn_response.autonomous_system_organization
                        isp.isp = asn_response.autonomous_system_organization
                        isp.organization = asn_response.autonomous_system_organization
                except:
                    pass

            # 如果仍然没有ISP信息，尝试根据IP段推断
            if not isp.isp:
                isp_info = self._infer_isp_from_ip(ip)
                if isp_info:
                    isp.isp = isp_info.get('isp')
                    isp.organization = isp_info.get('organization')
            
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

    def _infer_isp_from_ip(self, ip: str) -> Optional[Dict[str, str]]:
        """根据IP地址推断ISP信息"""
        try:
            import ipaddress
            ip_obj = ipaddress.ip_address(ip)

            # 知名的公共DNS和CDN服务
            known_ranges = {
                # Google DNS
                "8.8.8.0/24": {"isp": "Google LLC", "organization": "Google Public DNS"},
                "8.8.4.0/24": {"isp": "Google LLC", "organization": "Google Public DNS"},

                # Cloudflare DNS
                "1.1.1.0/24": {"isp": "Cloudflare, Inc.", "organization": "Cloudflare DNS"},
                "1.0.0.0/24": {"isp": "Cloudflare, Inc.", "organization": "Cloudflare DNS"},

                # Quad9 DNS
                "9.9.9.0/24": {"isp": "Quad9", "organization": "Quad9 DNS"},

                # OpenDNS
                "208.67.222.0/24": {"isp": "Cisco OpenDNS", "organization": "OpenDNS"},
                "208.67.220.0/24": {"isp": "Cisco OpenDNS", "organization": "OpenDNS"},

                # 中国常见DNS
                "114.114.114.0/24": {"isp": "114DNS", "organization": "114DNS Public DNS"},
                "223.5.5.0/24": {"isp": "Alibaba Cloud", "organization": "Alibaba Public DNS"},
                "223.6.6.0/24": {"isp": "Alibaba Cloud", "organization": "Alibaba Public DNS"},
                "180.76.76.0/24": {"isp": "Baidu", "organization": "Baidu Public DNS"},

                # 其他知名服务
                "4.2.2.0/24": {"isp": "Level 3 Communications", "organization": "Level 3 DNS"},
            }

            # 检查IP是否在已知范围内
            for network_str, info in known_ranges.items():
                network = ipaddress.ip_network(network_str)
                if ip_obj in network:
                    return info

            # 根据IP段特征推断
            if ip.startswith("8.8."):
                return {"isp": "Google LLC", "organization": "Google Services"}
            elif ip.startswith("1.1.") or ip.startswith("1.0."):
                return {"isp": "Cloudflare, Inc.", "organization": "Cloudflare Services"}
            elif ip.startswith("114.114."):
                return {"isp": "114DNS", "organization": "114DNS Public DNS"}
            elif ip.startswith("223.5.") or ip.startswith("223.6."):
                return {"isp": "Alibaba Cloud", "organization": "Alibaba Public DNS"}
            elif ip.startswith("180.76."):
                return {"isp": "Baidu", "organization": "Baidu Public DNS"}

            return None

        except Exception as e:
            logger.debug(f"ISP推断失败: {e}")
            return None
    
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
    
    async def switch_database_source(self, source: str) -> Dict[str, Any]:
        """切换数据库源"""
        try:
            if source not in self.stats["available_sources"]:
                raise ValueError(f"不支持的数据源: {source}")

            old_source = self.current_source
            self.current_source = source

            # 重新初始化读取器
            await self._initialize_readers()

            logger.info(f"数据库源已从 {old_source} 切换到 {source}")

            return {
                "success": True,
                "message": f"数据库源已切换到: {source}",
                "old_source": old_source,
                "new_source": source,
                "available_databases": self.available_databases
            }

        except Exception as e:
            logger.error(f"切换数据库源失败: {e}")
            return {
                "success": False,
                "message": f"切换数据库源失败: {str(e)}",
                "current_source": self.current_source
            }

    async def get_database_info(self) -> Dict[str, Any]:
        """获取数据库信息"""
        return {
            "current_source": self.current_source,
            "available_sources": self.stats["available_sources"],
            "available_databases": self.available_databases,
            "database_status": {
                "city_db": self.db_reader is not None,
                "asn_db": self.asn_reader is not None
            }
        }

    async def get_service_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        return {
            "geoip_stats": self.stats.copy(),
            "database_info": await self.get_database_info(),
            "concurrent_limit": settings.concurrent_limit
        }


# 全局服务实例
geoip_service = AsyncGeoIPService()
