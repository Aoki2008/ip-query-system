import geoip2.database
import logging
import os
from typing import Dict, List, Any
from utils.validators import IPValidator
from utils.cache_service import cache_ip_query, cache_batch_query

logger = logging.getLogger(__name__)

class IPService:
    """IP查询服务类"""
    
    def __init__(self):
        """初始化IP服务"""
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'GeoLite2-City.mmdb')
        self.validator = IPValidator()
        self._check_database()
    
    def _check_database(self):
        """检查数据库文件是否存在"""
        if not os.path.exists(self.db_path):
            logger.error(f'数据库文件不存在: {os.path.abspath(self.db_path)}')
            raise FileNotFoundError('GeoLite2-City.mmdb数据库文件未找到，请从MaxMind官网下载')
        
        logger.info(f'使用数据库文件: {os.path.abspath(self.db_path)}')
    
    @cache_ip_query(ttl=3600)  # 缓存1小时
    def query_ip(self, ip: str) -> Dict[str, Any]:
        """
        查询单个IP地址信息
        
        Args:
            ip: IP地址字符串
            
        Returns:
            包含IP信息的字典
            
        Raises:
            ValueError: IP地址格式无效
            Exception: 查询过程中的其他错误
        """
        # 验证IP地址格式
        if not self.validator.is_valid_ip(ip):
            raise ValueError(f'无效的IP地址格式: {ip}')
        
        try:
            with geoip2.database.Reader(self.db_path) as reader:
                logger.info(f'查询IP: {ip}')
                response = reader.city(ip)
                logger.info(f'查询成功，IP信息: {response}')
                
                # 构建返回数据
                data = {
                    'ip': ip,
                    'country': response.country.name or '未知',
                    'country_code': response.country.iso_code or '',
                    'region': response.subdivisions.most_specific.name or '未知',
                    'region_code': response.subdivisions.most_specific.iso_code or '',
                    'city': response.city.name or '未知',
                    'postal': response.postal.code or '',
                    'latitude': float(response.location.latitude) if response.location.latitude else None,
                    'longitude': float(response.location.longitude) if response.location.longitude else None,
                    'timezone': response.location.time_zone or '未知',
                    'isp': getattr(response.traits, 'isp', '未知') or '未知',
                    'organization': getattr(response.traits, 'organization', '未知') or '未知',
                    'accuracy_radius': response.location.accuracy_radius
                }
                
                logger.info(f'返回查询结果: {data}')
                return data
                
        except geoip2.errors.AddressNotFoundError:
            logger.warning(f'IP地址未在数据库中找到: {ip}')
            return {
                'ip': ip,
                'error': 'IP地址信息未找到',
                'country': '未知',
                'region': '未知',
                'city': '未知',
                'timezone': '未知',
                'isp': '未知'
            }
        except Exception as e:
            logger.error(f'查询IP {ip} 时发生错误: {str(e)}')
            raise Exception(f'查询失败: {str(e)}')
    
    @cache_batch_query(ttl=1800)  # 缓存30分钟
    def query_batch_ips(self, ips: List[str]) -> List[Dict[str, Any]]:
        """
        批量查询IP地址信息
        
        Args:
            ips: IP地址列表
            
        Returns:
            包含所有IP查询结果的列表
        """
        results = []
        
        for ip in ips:
            try:
                result = self.query_ip(ip.strip())
                results.append(result)
            except Exception as e:
                logger.error(f'批量查询中IP {ip} 失败: {str(e)}')
                results.append({
                    'ip': ip,
                    'error': str(e),
                    'country': '查询失败',
                    'region': '查询失败',
                    'city': '查询失败',
                    'timezone': '查询失败',
                    'isp': '查询失败'
                })
        
        return results
