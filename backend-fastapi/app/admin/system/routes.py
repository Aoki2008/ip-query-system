"""
系统管理API路由
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.admin.auth.dependencies import get_current_active_user
from app.admin.models import AdminUser
from app.services.geoip_service import geoip_service
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/admin/system", tags=["系统管理"])


class DatabaseSwitchRequest(BaseModel):
    """数据库切换请求"""
    source: str  # local, api, mixed


class DatabaseSwitchResponse(BaseModel):
    """数据库切换响应"""
    success: bool
    message: str
    old_source: str = None
    new_source: str = None
    available_databases: Dict[str, str] = None


class DatabaseInfoResponse(BaseModel):
    """数据库信息响应"""
    current_source: str
    available_sources: list
    available_databases: Dict[str, str]
    database_status: Dict[str, bool]


class SystemStatsResponse(BaseModel):
    """系统统计响应"""
    geoip_stats: Dict[str, Any]
    database_info: Dict[str, Any]
    concurrent_limit: int


@router.get("/database/info", response_model=DatabaseInfoResponse)
async def get_database_info(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取数据库信息"""
    try:
        info = await geoip_service.get_database_info()
        return DatabaseInfoResponse(**info)
    except Exception as e:
        logger.error(f"获取数据库信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取数据库信息失败: {str(e)}"
        )


@router.post("/database/switch", response_model=DatabaseSwitchResponse)
async def switch_database_source(
    request: DatabaseSwitchRequest,
    current_user: AdminUser = Depends(get_current_active_user)
):
    """切换数据库源"""
    try:
        result = await geoip_service.switch_database_source(request.source)

        if result["success"]:
            logger.info(f"管理员 {current_user.username} 切换数据库源到: {request.source}")
            return DatabaseSwitchResponse(**result)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"切换数据库源失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"切换数据库源失败: {str(e)}"
        )


@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取系统统计信息"""
    try:
        stats = await geoip_service.get_service_stats()
        return SystemStatsResponse(**stats)
    except Exception as e:
        logger.error(f"获取系统统计失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取系统统计失败: {str(e)}"
        )


@router.post("/database/rescan")
async def rescan_databases(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """重新扫描可用数据库"""
    try:
        await geoip_service._scan_available_databases()
        info = await geoip_service.get_database_info()

        logger.info(f"管理员 {current_user.username} 重新扫描数据库")

        return {
            "success": True,
            "message": "数据库扫描完成",
            "database_info": info
        }
    except Exception as e:
        logger.error(f"重新扫描数据库失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重新扫描数据库失败: {str(e)}"
        )


@router.get("/database/test/{source}")
async def test_database_source(
    source: str,
    current_user: AdminUser = Depends(get_current_active_user)
):
    """测试指定数据库源"""
    try:
        # 保存当前源
        original_source = geoip_service.current_source
        
        # 临时切换到测试源
        await geoip_service.switch_database_source(source)
        
        # 执行测试查询
        test_result = await geoip_service.query_ip("8.8.8.8")
        
        # 恢复原始源
        await geoip_service.switch_database_source(original_source)
        
        return {
            "success": True,
            "message": f"数据库源 {source} 测试成功",
            "test_result": {
                "ip": test_result.ip,
                "country": test_result.location.country,
                "isp": test_result.isp.isp,
                "query_time": test_result.query_time
            }
        }
        
    except Exception as e:
        # 确保恢复原始源
        try:
            await geoip_service.switch_database_source(original_source)
        except:
            pass
            
        logger.error(f"测试数据库源失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"测试数据库源失败: {str(e)}"
        )
