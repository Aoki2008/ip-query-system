"""
API性能统计分析路由
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session

from .models import (
    APIPerformanceStats, APITrendData, TopEndpointsStats,
    ErrorAnalysis, UserActivityStats, PerformanceSummary,
    APIAnalyticsDashboard, TimeRange, RealTimeMetrics,
    AnalyticsQuery, PerformanceReport, APICallLogResponse
)
from .service import APIAnalyticsService, APIMetricsCollector
from ..admin.models import AdminUser
from ..admin.auth.dependencies import get_current_active_user, require_super_admin
from ..database import get_db

router = APIRouter(prefix="/api/admin/analytics", tags=["API分析"])


@router.get("/dashboard", response_model=APIAnalyticsDashboard)
async def get_analytics_dashboard(
    time_range: TimeRange = Query(TimeRange.LAST_24_HOURS, description="时间范围"),
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取API分析仪表板"""
    analytics_service = APIAnalyticsService(db)
    return analytics_service.get_analytics_dashboard(time_range)


@router.get("/performance", response_model=List[APIPerformanceStats])
async def get_performance_stats(
    time_range: TimeRange = Query(TimeRange.LAST_24_HOURS, description="时间范围"),
    endpoint: Optional[str] = Query(None, description="端点过滤"),
    method: Optional[str] = Query(None, description="HTTP方法过滤"),
    limit: int = Query(50, ge=1, le=200, description="返回数量限制"),
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取API性能统计"""
    analytics_service = APIAnalyticsService(db)
    stats = analytics_service.get_performance_stats(time_range, endpoint, method)
    return stats[:limit]


@router.get("/trends", response_model=List[APITrendData])
async def get_trend_data(
    time_range: TimeRange = Query(TimeRange.LAST_24_HOURS, description="时间范围"),
    interval_minutes: int = Query(60, ge=5, le=1440, description="时间间隔(分钟)"),
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取API趋势数据"""
    analytics_service = APIAnalyticsService(db)
    return analytics_service.get_trend_data(time_range, interval_minutes)


@router.get("/top-endpoints", response_model=List[TopEndpointsStats])
async def get_top_endpoints(
    time_range: TimeRange = Query(TimeRange.LAST_24_HOURS, description="时间范围"),
    limit: int = Query(10, ge=1, le=50, description="返回数量限制"),
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取热门端点统计"""
    analytics_service = APIAnalyticsService(db)
    return analytics_service.get_top_endpoints(time_range, limit)


@router.get("/errors", response_model=List[ErrorAnalysis])
async def get_error_analysis(
    time_range: TimeRange = Query(TimeRange.LAST_24_HOURS, description="时间范围"),
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取错误分析"""
    analytics_service = APIAnalyticsService(db)
    return analytics_service.get_error_analysis(time_range)


@router.get("/users", response_model=List[UserActivityStats])
async def get_user_activity_stats(
    time_range: TimeRange = Query(TimeRange.LAST_24_HOURS, description="时间范围"),
    limit: int = Query(10, ge=1, le=50, description="返回数量限制"),
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户活动统计"""
    analytics_service = APIAnalyticsService(db)
    return analytics_service.get_user_activity_stats(time_range, limit)


@router.get("/summary", response_model=PerformanceSummary)
async def get_performance_summary(
    time_range: TimeRange = Query(TimeRange.LAST_24_HOURS, description="时间范围"),
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取性能摘要"""
    analytics_service = APIAnalyticsService(db)
    return analytics_service.get_performance_summary(time_range)


@router.get("/realtime", response_model=RealTimeMetrics)
async def get_realtime_metrics(
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取实时指标"""
    analytics_service = APIAnalyticsService(db)
    return analytics_service.get_real_time_metrics()


@router.get("/logs", response_model=List[APICallLogResponse])
async def get_api_logs(
    time_range: TimeRange = Query(TimeRange.LAST_24_HOURS, description="时间范围"),
    endpoint: Optional[str] = Query(None, description="端点过滤"),
    method: Optional[str] = Query(None, description="HTTP方法过滤"),
    status_code: Optional[int] = Query(None, description="状态码过滤"),
    user_id: Optional[int] = Query(None, description="用户ID过滤"),
    ip_address: Optional[str] = Query(None, description="IP地址过滤"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取API调用日志"""
    from .models import APICallLog
    from sqlalchemy import and_, desc
    
    analytics_service = APIAnalyticsService(db)
    start_time = analytics_service._get_start_time(time_range)
    
    query = db.query(APICallLog).filter(APICallLog.timestamp >= start_time)
    
    if endpoint:
        query = query.filter(APICallLog.endpoint.like(f"%{endpoint}%"))
    if method:
        query = query.filter(APICallLog.method == method)
    if status_code:
        query = query.filter(APICallLog.status_code == status_code)
    if user_id:
        query = query.filter(APICallLog.user_id == user_id)
    if ip_address:
        query = query.filter(APICallLog.ip_address == ip_address)
    
    logs = query.order_by(desc(APICallLog.timestamp)).limit(limit).all()
    
    return [APICallLogResponse.parse_obj(log.__dict__) for log in logs]


@router.post("/collect")
async def manual_collect_metrics(
    background_tasks: BackgroundTasks,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """手动触发指标收集"""
    def collect_sample_metrics():
        """收集示例指标"""
        import random
        from datetime import datetime, timedelta
        
        # 生成一些示例数据
        endpoints = [
            "/api/query-ip", "/api/admin/auth/login", "/api/admin/auth/profile",
            "/api/admin/permissions/roles", "/api/admin/monitoring/status"
        ]
        methods = ["GET", "POST", "PUT", "DELETE"]
        
        for _ in range(50):  # 生成50条示例记录
            endpoint = random.choice(endpoints)
            method = random.choice(methods)
            status_code = random.choices([200, 201, 400, 401, 404, 500], weights=[70, 10, 8, 5, 4, 3])[0]
            response_time = random.uniform(50, 2000)
            
            APIMetricsCollector.collect_api_metrics(
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time_ms=response_time,
                request_size=random.randint(100, 5000),
                response_size=random.randint(500, 10000),
                ip_address=f"192.168.1.{random.randint(1, 254)}",
                user_id=random.randint(1, 10) if random.random() > 0.3 else None
            )
    
    background_tasks.add_task(collect_sample_metrics)
    
    return {"message": "指标收集任务已启动"}


@router.get("/export")
async def export_analytics_report(
    time_range: TimeRange = Query(TimeRange.LAST_24_HOURS, description="时间范围"),
    format: str = Query("json", description="导出格式: json, csv"),
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """导出分析报告"""
    analytics_service = APIAnalyticsService(db)
    
    # 获取完整的分析数据
    dashboard_data = analytics_service.get_analytics_dashboard(time_range)
    
    if format.lower() == "json":
        return {
            "report_id": f"analytics_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.utcnow().isoformat(),
            "time_range": time_range.value,
            "data": dashboard_data.model_dump()
        }
    elif format.lower() == "csv":
        # 简化的CSV导出
        import io
        import csv
        from fastapi.responses import StreamingResponse
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入性能统计
        writer.writerow(["Endpoint", "Method", "Total Calls", "Avg Response Time", "Error Rate"])
        for endpoint in dashboard_data.top_endpoints:
            writer.writerow([
                endpoint.endpoint,
                endpoint.method,
                endpoint.total_calls,
                f"{endpoint.avg_response_time:.2f}",
                f"{endpoint.error_rate:.2f}%"
            ])
        
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=analytics_report.csv"}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的导出格式"
        )


@router.delete("/logs/cleanup")
async def cleanup_old_logs(
    days: int = Query(30, ge=1, le=365, description="保留天数"),
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """清理旧的API日志"""
    from .models import APICallLog
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    deleted_count = db.query(APICallLog).filter(
        APICallLog.timestamp < cutoff_date
    ).delete()
    
    db.commit()
    
    return {
        "message": f"已清理 {deleted_count} 条超过 {days} 天的API日志记录",
        "cutoff_date": cutoff_date.isoformat()
    }


@router.get("/health")
async def analytics_health_check(
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """分析服务健康检查"""
    from .models import APICallLog
    
    # 检查数据库连接和数据
    try:
        total_logs = db.query(APICallLog).count()
        recent_logs = db.query(APICallLog).filter(
            APICallLog.timestamp >= datetime.utcnow() - timedelta(hours=1)
        ).count()
        
        return {
            "status": "healthy",
            "total_api_logs": total_logs,
            "recent_logs_1h": recent_logs,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析服务健康检查失败: {str(e)}"
        )
