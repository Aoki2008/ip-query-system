"""
系统监控路由
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session

from .models import (
    SystemStatus, ServiceStatus, APIStats, EndpointStats,
    AlertResponse, MetricResponse, MonitoringDashboard,
    SystemHealth, PerformanceMetrics, AlertCreate, MetricCreate
)
from .service import MonitoringService, SystemMonitorService
from ..admin.models import AdminUser
from ..admin.auth.dependencies import get_current_active_user, require_super_admin
from ..database import get_db

router = APIRouter(prefix="/api/admin/monitoring", tags=["系统监控"])


@router.get("/dashboard", response_model=MonitoringDashboard)
async def get_monitoring_dashboard(
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取监控仪表板数据"""
    monitoring_service = MonitoringService(db)
    return monitoring_service.get_dashboard_data()


@router.get("/system/status", response_model=SystemStatus)
async def get_system_status(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取系统状态"""
    system_monitor = SystemMonitorService()
    return system_monitor.get_system_status()


@router.get("/system/health", response_model=SystemHealth)
async def get_system_health(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取系统健康状态"""
    system_monitor = SystemMonitorService()
    return system_monitor.get_system_health()


@router.get("/services", response_model=List[ServiceStatus])
async def get_service_status(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取服务状态"""
    system_monitor = SystemMonitorService()
    return system_monitor.get_service_status()


@router.get("/api/stats", response_model=APIStats)
async def get_api_stats(
    hours: int = Query(24, ge=1, le=168, description="统计时间范围(小时)"),
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取API统计"""
    monitoring_service = MonitoringService(db)
    start_time = datetime.utcnow() - timedelta(hours=hours)
    end_time = datetime.utcnow()
    
    return monitoring_service.api_metric_service.get_api_stats(start_time, end_time)


@router.get("/api/endpoints", response_model=List[EndpointStats])
async def get_endpoint_stats(
    limit: int = Query(10, ge=1, le=50, description="返回数量限制"),
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取端点统计"""
    monitoring_service = MonitoringService(db)
    return monitoring_service.api_metric_service.get_endpoint_stats(limit)


@router.get("/metrics", response_model=List[MetricResponse])
async def get_metrics(
    metric_type: Optional[str] = Query(None, description="指标类型"),
    metric_name: Optional[str] = Query(None, description="指标名称"),
    hours: int = Query(24, ge=1, le=168, description="时间范围(小时)"),
    limit: int = Query(1000, ge=1, le=10000, description="返回数量限制"),
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取系统指标"""
    monitoring_service = MonitoringService(db)
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    metrics = monitoring_service.metric_service.get_metrics(
        metric_type=metric_type,
        metric_name=metric_name,
        start_time=start_time,
        limit=limit
    )
    
    return [MetricResponse.parse_obj(m.__dict__) for m in metrics]


@router.post("/metrics", response_model=MetricResponse)
async def create_metric(
    metric: MetricCreate,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """创建自定义指标"""
    monitoring_service = MonitoringService(db)
    db_metric = monitoring_service.metric_service.save_metric(metric)
    return MetricResponse.parse_obj(db_metric.__dict__)


@router.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    limit: int = Query(50, ge=1, le=200, description="返回数量限制"),
    resolved: Optional[bool] = Query(None, description="是否已解决"),
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取系统告警"""
    from .models import SystemAlert

    query = db.query(SystemAlert)

    if resolved is not None:
        query = query.filter(SystemAlert.is_resolved == resolved)

    alerts = query.order_by(SystemAlert.created_at.desc()).limit(limit).all()

    return [AlertResponse.parse_obj(alert.__dict__) for alert in alerts]


@router.post("/alerts", response_model=AlertResponse)
async def create_alert(
    alert: AlertCreate,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """创建告警"""
    monitoring_service = MonitoringService(db)
    db_alert = monitoring_service.alert_service.create_alert(alert)
    return AlertResponse.parse_obj(db_alert.__dict__)


@router.put("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """解决告警"""
    monitoring_service = MonitoringService(db)
    
    if not monitoring_service.alert_service.resolve_alert(alert_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="告警不存在"
        )
    
    return {"message": "告警已解决"}


@router.post("/collect")
async def collect_metrics(
    background_tasks: BackgroundTasks,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """手动收集系统指标"""
    monitoring_service = MonitoringService(db)
    
    # 在后台任务中收集指标
    background_tasks.add_task(monitoring_service.collect_system_metrics)
    
    return {"message": "指标收集任务已启动"}


@router.get("/performance", response_model=List[PerformanceMetrics])
async def get_performance_metrics(
    hours: int = Query(24, ge=1, le=168, description="时间范围(小时)"),
    interval: int = Query(60, ge=1, le=3600, description="采样间隔(秒)"),
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取性能指标时序数据"""
    monitoring_service = MonitoringService(db)
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    # 获取系统指标
    cpu_metrics = monitoring_service.metric_service.get_metrics(
        metric_name="cpu_percent",
        start_time=start_time,
        limit=hours * 3600 // interval
    )
    
    memory_metrics = monitoring_service.metric_service.get_metrics(
        metric_name="memory_percent",
        start_time=start_time,
        limit=hours * 3600 // interval
    )
    
    disk_metrics = monitoring_service.metric_service.get_metrics(
        metric_name="disk_percent",
        start_time=start_time,
        limit=hours * 3600 // interval
    )
    
    # 组合数据
    performance_data = []
    
    # 简化处理：取最近的指标数据
    for i in range(min(len(cpu_metrics), len(memory_metrics), len(disk_metrics))):
        performance_data.append(PerformanceMetrics(
            timestamp=cpu_metrics[i].timestamp,
            cpu_percent=cpu_metrics[i].metric_value,
            memory_percent=memory_metrics[i].metric_value,
            disk_percent=disk_metrics[i].metric_value,
            network_io={"sent": 0, "recv": 0},  # 简化处理
            api_response_time=0.0,  # 简化处理
            active_connections=0  # 简化处理
        ))
    
    return performance_data[:50]  # 限制返回数量


@router.get("/realtime")
async def get_realtime_data(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取实时监控数据（WebSocket端点的HTTP版本）"""
    system_monitor = SystemMonitorService()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "system_status": system_monitor.get_system_status(),
        "system_health": system_monitor.get_system_health(),
        "service_status": system_monitor.get_service_status()
    }
