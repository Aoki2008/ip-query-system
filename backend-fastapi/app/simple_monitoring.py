"""
简化的系统监控功能
"""
import psutil
import time
from datetime import datetime
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from .admin.models import AdminUser
from .admin.auth.dependencies import get_current_active_user

# 创建路由
monitoring_router = APIRouter(prefix="/api/admin/monitoring", tags=["系统监控"])


class SystemStatus(BaseModel):
    """系统状态模型"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: int
    memory_total_mb: int
    disk_percent: float
    disk_used_gb: int
    disk_total_gb: int
    uptime_seconds: int
    process_count: int
    timestamp: str


class SystemHealth(BaseModel):
    """系统健康状态模型"""
    overall_status: str
    score: int
    cpu_status: str
    memory_status: str
    disk_status: str
    issues: List[str]
    recommendations: List[str]


class ServiceInfo(BaseModel):
    """服务信息模型"""
    name: str
    status: str
    pid: int
    cpu_percent: float
    memory_mb: float


def get_system_status() -> SystemStatus:
    """获取系统状态"""
    # CPU信息
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # 内存信息
    memory = psutil.virtual_memory()
    memory_used_mb = memory.used // (1024 * 1024)
    memory_total_mb = memory.total // (1024 * 1024)
    
    # 磁盘信息
    disk = psutil.disk_usage('/')
    disk_used_gb = disk.used // (1024 * 1024 * 1024)
    disk_total_gb = disk.total // (1024 * 1024 * 1024)
    
    # 系统运行时间
    uptime = int(time.time() - psutil.boot_time())
    
    # 进程数量
    process_count = len(psutil.pids())
    
    return SystemStatus(
        cpu_percent=cpu_percent,
        memory_percent=memory.percent,
        memory_used_mb=memory_used_mb,
        memory_total_mb=memory_total_mb,
        disk_percent=disk.percent,
        disk_used_gb=disk_used_gb,
        disk_total_gb=disk_total_gb,
        uptime_seconds=uptime,
        process_count=process_count,
        timestamp=datetime.utcnow().isoformat()
    )


def get_system_health() -> SystemHealth:
    """获取系统健康状态"""
    status = get_system_status()
    issues = []
    recommendations = []
    score = 100
    
    # CPU检查
    cpu_status = "healthy"
    if status.cpu_percent > 90:
        cpu_status = "critical"
        issues.append(f"CPU使用率过高: {status.cpu_percent:.1f}%")
        recommendations.append("检查CPU密集型进程，考虑优化或扩容")
        score -= 30
    elif status.cpu_percent > 70:
        cpu_status = "warning"
        issues.append(f"CPU使用率较高: {status.cpu_percent:.1f}%")
        recommendations.append("监控CPU使用情况，准备扩容计划")
        score -= 15
    
    # 内存检查
    memory_status = "healthy"
    if status.memory_percent > 90:
        memory_status = "critical"
        issues.append(f"内存使用率过高: {status.memory_percent:.1f}%")
        recommendations.append("释放内存或增加内存容量")
        score -= 25
    elif status.memory_percent > 80:
        memory_status = "warning"
        issues.append(f"内存使用率较高: {status.memory_percent:.1f}%")
        recommendations.append("监控内存使用，考虑内存优化")
        score -= 10
    
    # 磁盘检查
    disk_status = "healthy"
    if status.disk_percent > 95:
        disk_status = "critical"
        issues.append(f"磁盘使用率过高: {status.disk_percent:.1f}%")
        recommendations.append("清理磁盘空间或扩容存储")
        score -= 20
    elif status.disk_percent > 85:
        disk_status = "warning"
        issues.append(f"磁盘使用率较高: {status.disk_percent:.1f}%")
        recommendations.append("定期清理日志和临时文件")
        score -= 10
    
    # 总体状态
    if score >= 90:
        overall_status = "excellent"
    elif score >= 75:
        overall_status = "good"
    elif score >= 60:
        overall_status = "warning"
    else:
        overall_status = "critical"
    
    return SystemHealth(
        overall_status=overall_status,
        score=max(0, score),
        cpu_status=cpu_status,
        memory_status=memory_status,
        disk_status=disk_status,
        issues=issues,
        recommendations=recommendations
    )


def get_service_info() -> List[ServiceInfo]:
    """获取服务信息"""
    services = []
    
    # 获取当前Python进程信息
    current_process = psutil.Process()
    
    services.append(ServiceInfo(
        name="FastAPI Server",
        status="running",
        pid=current_process.pid,
        cpu_percent=current_process.cpu_percent(),
        memory_mb=current_process.memory_info().rss / (1024 * 1024)
    ))
    
    return services


# 路由定义

@monitoring_router.get("/status", response_model=SystemStatus)
async def get_status(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取系统状态"""
    return get_system_status()


@monitoring_router.get("/health", response_model=SystemHealth)
async def get_health(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取系统健康状态"""
    return get_system_health()


@monitoring_router.get("/services", response_model=List[ServiceInfo])
async def get_services(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取服务信息"""
    return get_service_info()


@monitoring_router.get("/dashboard")
async def get_dashboard(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取监控仪表板数据"""
    return {
        "system_status": get_system_status(),
        "system_health": get_system_health(),
        "services": get_service_info(),
        "timestamp": datetime.utcnow().isoformat()
    }


@monitoring_router.get("/realtime")
async def get_realtime(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取实时监控数据"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "system_status": get_system_status(),
        "system_health": get_system_health(),
        "services": get_service_info()
    }
