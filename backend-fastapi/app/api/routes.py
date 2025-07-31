"""
API路由定义
定义所有API端点
"""
import time
from typing import Dict, Any
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse

from app.core.logging import get_logger, request_logger, performance_monitor
from app.core.exceptions import ValidationException, GeoIPException
from app.models.schemas import (
    IPQueryRequest, BatchIPQueryRequest, IPQueryResponse, 
    BatchIPQueryResponse, ServiceStats, CacheStats, HealthCheckResponse
)
from app.services.geoip_service import geoip_service
from app.services.cache_service import cache_service
from app.config import settings

logger = get_logger(__name__)

# 创建API路由器
api_router = APIRouter()


async def log_request_middleware(request: Request):
    """请求日志中间件"""
    start_time = time.time()
    
    # 记录请求信息
    request_logger.log_request(
        method=request.method,
        path=request.url.path,
        ip=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "")
    )
    
    return start_time


@api_router.get("/health", response_model=HealthCheckResponse, tags=["系统"])
async def health_check():
    """健康检查接口

    检查服务是否正常运行，返回服务状态信息。
    """
    logger.info("健康检查请求")

    return HealthCheckResponse(
        status="healthy",
        message="FastAPI IP查询服务运行正常",
        service_type="fastapi",
        timestamp=time.time()
    )


@api_router.get("/query-ip", response_model=IPQueryResponse, tags=["查询"])
async def query_single_ip(
    ip: str = Query(..., description="要查询的IP地址", example="8.8.8.8"),
    request: Request = None,
    start_time: float = Depends(log_request_middleware)
):
    """单个IP查询接口

    查询指定IP地址的地理位置信息，包括国家、地区、城市、ISP等详细信息。

    - **ip**: 要查询的IP地址（IPv4或IPv6）

    返回包含位置信息、ISP信息、查询时间等数据。
    """
    try:
        logger.info(f"收到单个IP查询请求: {ip}")
        
        # 验证IP地址
        ip_request = IPQueryRequest(ip=ip)
        clean_ip = ip_request.ip
        
        # 尝试从缓存获取结果
        cached_result = await cache_service.get_cached_result(clean_ip)
        if cached_result:
            logger.info(f"返回缓存结果: {clean_ip}")
            
            # 记录响应
            response_time = time.time() - start_time
            request_logger.log_response(
                method=request.method,
                path=request.url.path,
                status_code=200,
                response_time=response_time
            )
            performance_monitor.record_request(response_time, True)
            
            return IPQueryResponse(success=True, data=cached_result)
        
        # 查询IP信息
        result = await geoip_service.query_ip(clean_ip)
        
        # 缓存结果
        if not result.error:
            await cache_service.cache_result(result)
        
        logger.info(f"查询完成: {clean_ip}")
        
        # 记录响应
        response_time = time.time() - start_time
        request_logger.log_response(
            method=request.method,
            path=request.url.path,
            status_code=200,
            response_time=response_time
        )
        performance_monitor.record_request(response_time, True)
        
        return IPQueryResponse(success=True, data=result)
        
    except ValueError as e:
        logger.warning(f"参数验证失败: {str(e)}")
        raise ValidationException(str(e))
    except Exception as e:
        logger.error(f"查询失败: {str(e)}", exc_info=True)
        raise GeoIPException("查询服务暂时不可用")


@api_router.post("/query-batch", response_model=BatchIPQueryResponse, tags=["查询"])
async def query_batch_ips(
    batch_request: BatchIPQueryRequest,
    request: Request = None,
    start_time: float = Depends(log_request_middleware)
):
    """批量IP查询接口

    批量查询多个IP地址的地理位置信息，支持异步并发处理。

    - **ips**: IP地址列表（最多100个）
    - **batch_size**: 批处理大小（默认50）

    返回所有IP的查询结果，包括成功数量、缓存命中数等统计信息。
    """
    try:
        logger.info(f"收到批量IP查询请求，共{len(batch_request.ips)}个IP")
        
        # 检查批量大小限制
        if len(batch_request.ips) > settings.max_batch_size:
            raise ValidationException(f"批量查询数量不能超过{settings.max_batch_size}个")
        
        valid_ips = batch_request.ips
        batch_size = batch_request.batch_size or 50
        
        logger.info(f"验证通过，共{len(valid_ips)}个有效IP，开始批量查询")
        
        # 先尝试从缓存获取结果（优化：并发检查缓存）
        import asyncio
        cache_tasks = [cache_service.get_cached_result(ip) for ip in valid_ips]
        cache_results = await asyncio.gather(*cache_tasks, return_exceptions=True)

        cached_results = []
        uncached_ips = []

        for ip, cached_result in zip(valid_ips, cache_results):
            if cached_result and not isinstance(cached_result, Exception):
                cached_results.append(cached_result)
            else:
                uncached_ips.append(ip)
        
        # 查询未缓存的IP
        uncached_results = []
        if uncached_ips:
            uncached_results = await geoip_service.query_batch_ips(
                uncached_ips, 
                batch_size=batch_size
            )
            
            # 缓存新查询的结果
            await cache_service.cache_batch_results(uncached_results)
        
        # 合并结果
        all_results = cached_results + uncached_results
        success_count = len([r for r in all_results if not r.error])
        
        logger.info(f"批量查询完成，成功{success_count}个，缓存命中{len(cached_results)}个")
        
        # 记录响应
        response_time = time.time() - start_time
        request_logger.log_response(
            method=request.method,
            path=request.url.path,
            status_code=200,
            response_time=response_time
        )
        performance_monitor.record_request(response_time, True)
        
        return BatchIPQueryResponse(
            success=True,
            data={
                "total": len(valid_ips),
                "success_count": success_count,
                "cached_count": len(cached_results),
                "results": [result.model_dump() for result in all_results],
                "query_type": "fastapi_async"
            }
        )
        
    except ValueError as e:
        logger.warning(f"参数验证失败: {str(e)}")
        raise ValidationException(str(e))
    except Exception as e:
        logger.error(f"批量查询失败: {str(e)}", exc_info=True)
        raise GeoIPException("批量查询服务暂时不可用")


@api_router.get("/stats", response_model=Dict[str, Any], tags=["统计"])
async def get_stats():
    """获取服务统计信息

    获取服务的详细统计信息，包括性能数据、GeoIP统计、缓存统计等。
    """
    try:
        # 获取基础统计
        base_stats = performance_monitor.get_stats()
        
        # 获取GeoIP服务统计
        geoip_stats = await geoip_service.get_service_stats()
        
        # 获取缓存统计
        cache_stats = await cache_service.get_cache_stats()
        
        # 合并统计信息
        stats = {
            "performance": base_stats,
            "geoip": geoip_stats,
            "cache": cache_stats.dict(),
            "timestamp": time.time(),
            "service_type": "fastapi"
        }
        
        logger.info("获取服务统计信息")
        return {"success": True, "data": stats}
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}", exc_info=True)
        raise GeoIPException("获取统计信息失败")


@api_router.get("/cache/stats", response_model=Dict[str, Any], tags=["缓存"])
async def get_cache_stats():
    """获取缓存统计信息

    获取Redis缓存的详细统计信息，包括命中率、键数量、内存使用等。
    """
    try:
        stats = await cache_service.get_cache_stats()
        return {"success": True, "data": stats.dict()}
        
    except Exception as e:
        logger.error(f"获取缓存统计失败: {str(e)}", exc_info=True)
        raise GeoIPException("获取缓存统计失败")


@api_router.post("/cache/clear", response_model=Dict[str, Any], tags=["缓存"])
async def clear_cache():
    """清空缓存

    清空Redis缓存中的所有数据，用于缓存重置或故障排除。
    """
    try:
        success = await cache_service.clear_cache()
        
        if success:
            logger.info("缓存已清空")
            return {"success": True, "message": "缓存已清空"}
        else:
            raise GeoIPException("清空缓存失败")
            
    except Exception as e:
        logger.error(f"清空缓存失败: {str(e)}", exc_info=True)
        raise GeoIPException("清空缓存失败")
