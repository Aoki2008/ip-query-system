"""
异步GeoIP查询服务
提供高性能的IP地理位置查询功能
"""
import asyncio
import time
from datetime import datetime
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
        # 改为独立的数据库文件选择
        self.current_city_db: str = ""  # 当前使用的城市数据库文件key
        self.current_asn_db: str = ""   # 当前使用的ASN数据库文件key
        self.available_databases = {}  # 存储可用的数据库信息
        self.stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "total_query_time": 0.0,
            "avg_query_time": 0.0,
            "current_city_db": "",
            "current_asn_db": "",
            "available_databases": []
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

            # 设置默认数据库文件（优先选择本地数据库）
            await self._set_default_databases()

            # 初始化数据库读取器
            await self._initialize_readers()

            logger.info(f"GeoIP服务初始化成功，城市数据库: {self.current_city_db}, ASN数据库: {self.current_asn_db}")

        except Exception as e:
            logger.error(f"GeoIP服务初始化失败: {e}")
            raise GeoIPException(f"GeoIP服务初始化失败: {e}")

    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """获取文件详细信息"""
        try:
            if not file_path.exists():
                return {
                    "exists": False,
                    "size": 0,
                    "size_mb": 0,
                    "modified_time": None,
                    "status": "不存在"
                }

            stat = file_path.stat()
            size_bytes = stat.st_size
            size_mb = round(size_bytes / (1024 * 1024), 1)
            modified_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

            return {
                "exists": True,
                "size": size_bytes,
                "size_mb": size_mb,
                "modified_time": modified_time,
                "status": "可用"  # 初始状态，稍后会在扫描时更新
            }
        except Exception as e:
            logger.error(f"获取文件信息失败 {file_path}: {e}")
            return {
                "exists": False,
                "size": 0,
                "size_mb": 0,
                "modified_time": None,
                "status": "错误"
            }

    def _is_database_loaded(self, db_key: str, db_info: Dict[str, Any]) -> bool:
        """检查数据库是否已加载"""
        try:
            # 基于数据库key和类型判断是否为当前使用的数据库
            if db_info["type"] == "city":
                return db_key == self.current_city_db and self.db_reader is not None
            elif db_info["type"] == "asn":
                return db_key == self.current_asn_db and self.asn_reader is not None
            return False
        except:
            return False

    async def _scan_available_databases(self) -> None:
        """扫描可用的数据库文件"""
        self.available_databases = {}
        available_db_keys = []

        # 检查本地数据库
        local_city_path = Path(settings.geoip_db_path)
        local_asn_path = Path(settings.geoip_asn_db_path)

        if local_city_path.exists():
            db_key = "local_city"
            self.available_databases[db_key] = {
                "key": db_key,
                "path": str(local_city_path),
                "type": "city",
                "source_location": "本地数据目录",
                "display_name": f"城市数据库 (data目录)",
                "file_name": local_city_path.name,
                **self._get_file_info(local_city_path)
            }
            available_db_keys.append(db_key)

        if local_asn_path.exists():
            db_key = "local_asn"
            self.available_databases[db_key] = {
                "key": db_key,
                "path": str(local_asn_path),
                "type": "asn",
                "source_location": "项目根目录",
                "display_name": f"ASN数据库 (根目录)",
                "file_name": local_asn_path.name,
                **self._get_file_info(local_asn_path)
            }
            available_db_keys.append(db_key)

        # 检查API目录数据库
        api_city_path = Path("API/GeoLite2-City.mmdb")
        api_asn_path = Path("API/GeoLite2-ASN.mmdb")

        if api_city_path.exists():
            db_key = "api_city"
            self.available_databases[db_key] = {
                "key": db_key,
                "path": str(api_city_path),
                "type": "city",
                "source_location": "API目录",
                "display_name": f"城市数据库 (API目录)",
                "file_name": api_city_path.name,
                **self._get_file_info(api_city_path)
            }
            available_db_keys.append(db_key)

        if api_asn_path.exists():
            db_key = "api_asn"
            self.available_databases[db_key] = {
                "key": db_key,
                "path": str(api_asn_path),
                "type": "asn",
                "source_location": "API目录",
                "display_name": f"ASN数据库 (API目录)",
                "file_name": api_asn_path.name,
                **self._get_file_info(api_asn_path)
            }
            available_db_keys.append(db_key)

        self.stats["available_databases"] = available_db_keys
        logger.info(f"发现可用数据库文件: {len(self.available_databases)} 个")
        logger.info(f"可用数据库: {available_db_keys}")

    def _update_database_status(self) -> None:
        """更新数据库状态信息"""
        for db_key, db_info in self.available_databases.items():
            if self._is_database_loaded(db_key, db_info):
                db_info["status"] = "已加载"
            else:
                db_info["status"] = "可用"

    async def _set_default_databases(self) -> None:
        """设置默认数据库文件（优先选择本地数据库）"""
        # 为城市数据库选择默认值
        city_dbs = [key for key, db in self.available_databases.items() if db["type"] == "city"]
        if city_dbs:
            # 优先选择本地城市数据库
            self.current_city_db = next((key for key in city_dbs if key.startswith("local_")), city_dbs[0])

        # 为ASN数据库选择默认值
        asn_dbs = [key for key, db in self.available_databases.items() if db["type"] == "asn"]
        if asn_dbs:
            # 优先选择本地ASN数据库
            self.current_asn_db = next((key for key in asn_dbs if key.startswith("local_")), asn_dbs[0])

        # 更新统计信息
        self.stats["current_city_db"] = self.current_city_db
        self.stats["current_asn_db"] = self.current_asn_db

        logger.info(f"默认数据库设置 - 城市: {self.current_city_db}, ASN: {self.current_asn_db}")

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

            # 根据选择的数据库文件获取路径
            city_db_path = None
            asn_db_path = None

            # 获取城市数据库路径
            if self.current_city_db and self.current_city_db in self.available_databases:
                city_db_info = self.available_databases[self.current_city_db]
                city_db_path = city_db_info["path"]

            # 获取ASN数据库路径
            if self.current_asn_db and self.current_asn_db in self.available_databases:
                asn_db_info = self.available_databases[self.current_asn_db]
                asn_db_path = asn_db_info["path"]

            # 初始化城市数据库
            if city_db_path and Path(city_db_path).exists():
                self.db_reader = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    geoip2.database.Reader,
                    city_db_path
                )

                logger.info(f"城市数据库初始化成功: {city_db_path} ({self.current_city_db})")
            else:
                logger.warning(f"未找到可用的城市数据库: {self.current_city_db}")

            # 初始化ASN数据库
            if asn_db_path and Path(asn_db_path).exists():
                self.asn_reader = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    geoip2.database.Reader,
                    asn_db_path
                )

                logger.info(f"ASN数据库初始化成功: {asn_db_path} ({self.current_asn_db})")
            else:
                logger.warning(f"未找到可用的ASN数据库: {self.current_asn_db}")

            # 更新统计信息
            self.stats["current_city_db"] = self.current_city_db
            self.stats["current_asn_db"] = self.current_asn_db

            # 更新数据库状态
            self._update_database_status()

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
    
    async def switch_database_file(self, city_db_key: str = None, asn_db_key: str = None) -> Dict[str, Any]:
        """切换数据库文件"""
        try:
            old_city_db = self.current_city_db
            old_asn_db = self.current_asn_db

            # 验证并设置城市数据库
            if city_db_key is not None:
                if city_db_key not in self.available_databases:
                    raise ValueError(f"不支持的城市数据库: {city_db_key}")
                if self.available_databases[city_db_key]["type"] != "city":
                    raise ValueError(f"数据库类型错误: {city_db_key} 不是城市数据库")
                self.current_city_db = city_db_key

            # 验证并设置ASN数据库
            if asn_db_key is not None:
                if asn_db_key not in self.available_databases:
                    raise ValueError(f"不支持的ASN数据库: {asn_db_key}")
                if self.available_databases[asn_db_key]["type"] != "asn":
                    raise ValueError(f"数据库类型错误: {asn_db_key} 不是ASN数据库")
                self.current_asn_db = asn_db_key

            # 重新初始化读取器
            await self._initialize_readers()

            changes = []
            if city_db_key is not None:
                changes.append(f"城市数据库: {old_city_db} → {self.current_city_db}")
            if asn_db_key is not None:
                changes.append(f"ASN数据库: {old_asn_db} → {self.current_asn_db}")

            logger.info(f"数据库文件已切换: {', '.join(changes)}")

            return {
                "success": True,
                "message": f"数据库文件已切换: {', '.join(changes)}",
                "changes": {
                    "city_db": {"old": old_city_db, "new": self.current_city_db},
                    "asn_db": {"old": old_asn_db, "new": self.current_asn_db}
                },
                "current_databases": {
                    "city_db": self.current_city_db,
                    "asn_db": self.current_asn_db
                }
            }

        except Exception as e:
            logger.error(f"切换数据库文件失败: {e}")
            return {
                "success": False,
                "message": f"切换数据库文件失败: {str(e)}",
                "current_databases": {
                    "city_db": self.current_city_db,
                    "asn_db": self.current_asn_db
                }
            }

    async def get_database_info(self) -> Dict[str, Any]:
        """获取数据库信息"""
        return {
            "current_databases": {
                "city_db": self.current_city_db,
                "asn_db": self.current_asn_db
            },
            "available_databases": self.available_databases,
            "database_status": {
                "city_db": self.db_reader is not None,
                "asn_db": self.asn_reader is not None
            },
            "database_files": {
                "city_databases": [key for key, db in self.available_databases.items() if db["type"] == "city"],
                "asn_databases": [key for key, db in self.available_databases.items() if db["type"] == "asn"]
            }
        }

    async def get_detailed_database_info(self) -> Dict[str, Any]:
        """获取详细的数据库文件信息，用于前端下拉菜单显示"""
        database_details = {}

        # 为每个可用的数据库文件创建详细信息
        for db_key, db_info in self.available_databases.items():
            database_details[db_key] = {
                "key": db_key,
                "display_name": db_info["display_name"],
                "file_name": db_info["file_name"],
                "path": db_info["path"],
                "type": db_info["type"],
                "source_location": db_info["source_location"],
                "size_mb": db_info["size_mb"],
                "modified_time": db_info["modified_time"],
                "status": db_info["status"],
                "is_current": (
                    (db_info["type"] == "city" and db_key == self.current_city_db) or
                    (db_info["type"] == "asn" and db_key == self.current_asn_db)
                )
            }
        # 按类型分组数据库
        city_databases = {k: v for k, v in database_details.items() if v["type"] == "city"}
        asn_databases = {k: v for k, v in database_details.items() if v["type"] == "asn"}

        return {
            "current_databases": {
                "city_db": self.current_city_db,
                "asn_db": self.current_asn_db
            },
            "database_details": database_details,
            "city_databases": city_databases,
            "asn_databases": asn_databases
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
