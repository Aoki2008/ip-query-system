"""
数据模型定义
使用Pydantic进行数据验证和序列化
"""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
import ipaddress


class IPQueryRequest(BaseModel):
    """单个IP查询请求模型"""
    ip: str = Field(..., description="要查询的IP地址")
    
    @validator('ip')
    def validate_ip(cls, v):
        """验证IP地址格式"""
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            raise ValueError(f"无效的IP地址: {v}")


class BatchIPQueryRequest(BaseModel):
    """批量IP查询请求模型"""
    ips: List[str] = Field(..., description="要查询的IP地址列表", min_items=1, max_items=100)
    batch_size: Optional[int] = Field(default=50, description="批处理大小", ge=1, le=100)
    
    @validator('ips')
    def validate_ips(cls, v):
        """验证IP地址列表"""
        valid_ips = []
        for ip in v:
            try:
                ipaddress.ip_address(ip.strip())
                valid_ips.append(ip.strip())
            except ValueError:
                continue  # 跳过无效IP
        
        if not valid_ips:
            raise ValueError("没有有效的IP地址")
        
        return valid_ips


class LocationInfo(BaseModel):
    """位置信息模型"""
    country: Optional[str] = Field(None, description="国家")
    country_code: Optional[str] = Field(None, description="国家代码")
    region: Optional[str] = Field(None, description="地区/省份")
    region_code: Optional[str] = Field(None, description="地区代码")
    city: Optional[str] = Field(None, description="城市")
    postal_code: Optional[str] = Field(None, description="邮政编码")
    latitude: Optional[float] = Field(None, description="纬度")
    longitude: Optional[float] = Field(None, description="经度")
    timezone: Optional[str] = Field(None, description="时区")


class ISPInfo(BaseModel):
    """ISP信息模型"""
    isp: Optional[str] = Field(None, description="ISP名称")
    organization: Optional[str] = Field(None, description="组织")
    asn: Optional[str] = Field(None, description="ASN号码")
    asn_organization: Optional[str] = Field(None, description="ASN组织")


class IPQueryResult(BaseModel):
    """IP查询结果模型"""
    ip: str = Field(..., description="查询的IP地址")
    location: LocationInfo = Field(..., description="位置信息")
    isp: ISPInfo = Field(..., description="ISP信息")
    query_time: float = Field(..., description="查询耗时(秒)")
    cached: bool = Field(default=False, description="是否来自缓存")
    error: Optional[str] = Field(None, description="错误信息")


class IPQueryResponse(BaseModel):
    """单个IP查询响应模型"""
    success: bool = Field(..., description="查询是否成功")
    data: Optional[IPQueryResult] = Field(None, description="查询结果")
    error: Optional[Dict[str, Any]] = Field(None, description="错误信息")


class BatchIPQueryResponse(BaseModel):
    """批量IP查询响应模型"""
    success: bool = Field(..., description="查询是否成功")
    data: Optional[Dict[str, Any]] = Field(None, description="查询结果")
    error: Optional[Dict[str, Any]] = Field(None, description="错误信息")


class CacheStats(BaseModel):
    """缓存统计模型"""
    enabled: bool = Field(..., description="缓存是否启用")
    total_keys: int = Field(..., description="总键数")
    hit_count: int = Field(..., description="命中次数")
    miss_count: int = Field(..., description="未命中次数")
    hit_rate: float = Field(..., description="命中率")
    memory_usage: Optional[str] = Field(None, description="内存使用")


class ServiceStats(BaseModel):
    """服务统计模型"""
    total_requests: int = Field(..., description="总请求数")
    successful_requests: int = Field(..., description="成功请求数")
    failed_requests: int = Field(..., description="失败请求数")
    avg_response_time: float = Field(..., description="平均响应时间(秒)")
    cache_stats: Optional[CacheStats] = Field(None, description="缓存统计")


class HealthCheckResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    message: str = Field(..., description="状态消息")
    service_type: str = Field(..., description="服务类型")
    timestamp: float = Field(..., description="检查时间戳")


class APIInfoResponse(BaseModel):
    """API信息响应模型"""
    message: str = Field(..., description="服务描述")
    version: str = Field(..., description="API版本")
    service_type: str = Field(..., description="服务类型")
    status: str = Field(..., description="服务状态")
    docs: str = Field(..., description="文档地址")
    redoc: str = Field(..., description="ReDoc地址")
    openapi: str = Field(..., description="OpenAPI地址")
