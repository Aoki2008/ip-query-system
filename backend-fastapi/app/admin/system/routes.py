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


class DatabaseFileSwitchRequest(BaseModel):
    """数据库文件切换请求"""
    city_db_key: str = None     # 城市数据库文件key
    asn_db_key: str = None      # ASN数据库文件key
    country_db_key: str = None  # 国家数据库文件key


class DatabaseFileSwitchResponse(BaseModel):
    """数据库文件切换响应"""
    success: bool
    message: str
    changes: Dict[str, Dict[str, str]] = None
    current_databases: Dict[str, str] = None


class DatabaseInfoResponse(BaseModel):
    """数据库信息响应"""
    current_databases: Dict[str, str]
    available_databases: Dict[str, Any]
    database_status: Dict[str, bool]
    database_files: Dict[str, list]


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


@router.get("/database/files/detailed")
async def get_detailed_database_info(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取详细的数据库文件信息，用于前端下拉菜单显示"""
    try:
        info = await geoip_service.get_detailed_database_info()
        return info
    except Exception as e:
        logger.error(f"获取详细数据库文件信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取详细数据库文件信息失败: {str(e)}"
        )


@router.post("/database/switch", response_model=DatabaseFileSwitchResponse)
async def switch_database_files(
    request: DatabaseFileSwitchRequest,
    current_user: AdminUser = Depends(get_current_active_user)
):
    """切换数据库文件"""
    try:
        result = await geoip_service.switch_database_file(
            city_db_key=request.city_db_key,
            asn_db_key=request.asn_db_key,
            country_db_key=request.country_db_key
        )

        if result["success"]:
            changes_desc = []
            if request.city_db_key:
                changes_desc.append(f"城市数据库: {request.city_db_key}")
            if request.asn_db_key:
                changes_desc.append(f"ASN数据库: {request.asn_db_key}")
            if request.country_db_key:
                changes_desc.append(f"国家数据库: {request.country_db_key}")

            logger.info(f"管理员 {current_user.username} 切换数据库文件: {', '.join(changes_desc)}")
            return DatabaseFileSwitchResponse(**result)
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
        logger.error(f"切换数据库文件失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"切换数据库文件失败: {str(e)}"
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


@router.get("/database/test/current")
async def test_current_databases(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """测试当前数据库配置"""
    try:
        # 执行测试查询
        test_result = await geoip_service.query_ip("8.8.8.8")

        return {
            "success": True,
            "message": f"当前数据库配置测试成功",
            "current_databases": {
                "city_db": geoip_service.current_city_db,
                "asn_db": geoip_service.current_asn_db,
                "country_db": geoip_service.current_country_db
            },
            "test_result": {
                "ip": test_result.ip,
                "country": test_result.location.country,
                "isp": test_result.isp.isp,
                "query_time": test_result.query_time
            }
        }

    except Exception as e:
        logger.error(f"测试当前数据库配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"测试当前数据库配置失败: {str(e)}"
        )
