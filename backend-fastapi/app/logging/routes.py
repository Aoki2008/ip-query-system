"""
日志分析路由
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session

from .models import (
    LogQuery, LogStatistics, LogTrend, LogAlertRule, LogAlertResponse,
    LogAnalysis, LogDashboard, LogSearchResult, LogEntryResponse,
    LogLevel, LogCategory
)
from .service import LogAnalysisService, LogCollector
from ..admin.models import AdminUser
from ..admin.auth.dependencies import get_current_active_user, require_super_admin
from ..database import get_db

router = APIRouter(prefix="/api/admin/logs", tags=["日志分析"])


@router.get("/dashboard", response_model=LogDashboard)
async def get_log_dashboard(
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取日志仪表板"""
    log_service = LogAnalysisService(db)
    return log_service.get_dashboard_data()


@router.get("/search", response_model=LogSearchResult)
async def search_logs_get(
    limit: int = Query(10, ge=1, le=1000, description="返回记录数"),
    offset: int = Query(0, ge=0, description="偏移量"),
    level: Optional[str] = Query(None, description="日志级别"),
    category: Optional[str] = Query(None, description="日志分类"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """搜索日志 (GET方法)"""
    query = LogQuery(
        limit=limit,
        offset=offset,
        level=level,
        category=category,
        start_time=start_time,
        end_time=end_time
    )
    log_service = LogAnalysisService(db)
    return log_service.search_logs(query)


@router.post("/search", response_model=LogSearchResult)
async def search_logs(
    query: LogQuery,
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """搜索日志"""
    log_service = LogAnalysisService(db)
    return log_service.search_logs(query)


@router.get("/statistics", response_model=LogStatistics)
async def get_log_statistics(
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取日志统计"""
    log_service = LogAnalysisService(db)
    return log_service.get_log_statistics(start_time, end_time)


@router.get("/trends", response_model=List[LogTrend])
async def get_log_trends(
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    interval_hours: int = Query(1, ge=1, le=24, description="时间间隔(小时)"),
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取日志趋势"""
    log_service = LogAnalysisService(db)
    return log_service.get_log_trends(start_time, end_time, interval_hours)


@router.get("/analysis", response_model=LogAnalysis)
async def analyze_logs(
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """分析日志"""
    log_service = LogAnalysisService(db)
    return log_service.analyze_logs(start_time, end_time)


@router.get("/alerts", response_model=List[LogAlertResponse])
async def get_alert_rules(
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取告警规则"""
    log_service = LogAnalysisService(db)
    return log_service.get_alert_rules()


@router.post("/alerts", response_model=LogAlertResponse)
async def create_alert_rule(
    rule: LogAlertRule,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """创建告警规则"""
    log_service = LogAnalysisService(db)
    alert = log_service.create_alert_rule(rule)
    return LogAlertResponse.from_orm(alert)


@router.get("/recent", response_model=List[LogEntryResponse])
async def get_recent_logs(
    level: Optional[LogLevel] = Query(None, description="日志级别"),
    category: Optional[LogCategory] = Query(None, description="日志分类"),
    limit: int = Query(50, ge=1, le=200, description="返回数量"),
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取最近日志"""
    query = LogQuery(
        level=level,
        category=category,
        limit=limit,
        offset=0
    )
    
    log_service = LogAnalysisService(db)
    result = log_service.search_logs(query)
    return result.logs


@router.get("/errors", response_model=List[LogEntryResponse])
async def get_error_logs(
    hours: int = Query(24, ge=1, le=168, description="时间范围(小时)"),
    limit: int = Query(100, ge=1, le=500, description="返回数量"),
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取错误日志"""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    query = LogQuery(
        level=LogLevel.ERROR,
        start_time=start_time,
        limit=limit,
        offset=0
    )
    
    log_service = LogAnalysisService(db)
    result = log_service.search_logs(query)
    return result.logs


@router.post("/collect")
async def collect_sample_logs(
    background_tasks: BackgroundTasks,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """收集示例日志"""
    def generate_sample_logs():
        """生成示例日志"""
        import random
        
        levels = [LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.DEBUG]
        categories = [LogCategory.SYSTEM, LogCategory.API, LogCategory.DATABASE, LogCategory.AUTH]
        modules = ["auth", "api", "database", "cache", "monitoring"]
        
        messages = [
            "用户登录成功",
            "API请求处理完成",
            "数据库连接建立",
            "缓存更新完成",
            "系统监控检查",
            "用户权限验证失败",
            "API请求超时",
            "数据库查询错误",
            "内存使用率过高",
            "磁盘空间不足"
        ]
        
        for _ in range(100):  # 生成100条示例日志
            level = random.choice(levels)
            category = random.choice(categories)
            message = random.choice(messages)
            module = random.choice(modules)
            
            LogCollector.collect_log(
                level=level,
                category=category,
                message=message,
                module=module,
                function=f"test_function_{random.randint(1, 10)}",
                line_number=random.randint(1, 1000),
                user_id=random.randint(1, 10) if random.random() > 0.3 else None,
                ip_address=f"192.168.1.{random.randint(1, 254)}",
                extra_data={"test": True, "value": random.randint(1, 100)}
            )
    
    background_tasks.add_task(generate_sample_logs)
    
    return {"message": "示例日志生成任务已启动"}


@router.delete("/cleanup")
async def cleanup_old_logs(
    days: int = Query(30, ge=1, le=365, description="保留天数"),
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """清理旧日志"""
    log_service = LogAnalysisService(db)
    deleted_count = log_service.cleanup_old_logs(days)
    
    return {
        "message": f"已清理 {deleted_count} 条超过 {days} 天的日志记录",
        "deleted_count": deleted_count
    }


@router.get("/export")
async def export_logs(
    level: Optional[LogLevel] = Query(None, description="日志级别"),
    category: Optional[LogCategory] = Query(None, description="日志分类"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    format: str = Query("json", description="导出格式: json, csv"),
    limit: int = Query(1000, ge=1, le=10000, description="最大记录数"),
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """导出日志"""
    query = LogQuery(
        level=level,
        category=category,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=0
    )
    
    log_service = LogAnalysisService(db)
    result = log_service.search_logs(query)
    
    if format.lower() == "json":
        return {
            "export_id": f"logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.utcnow().isoformat(),
            "total_records": result.total,
            "exported_records": len(result.logs),
            "logs": [log.dict() for log in result.logs]
        }
    elif format.lower() == "csv":
        # 简化的CSV导出
        import io
        import csv
        from fastapi.responses import StreamingResponse
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        writer.writerow([
            "Timestamp", "Level", "Category", "Module", "Message", 
            "User ID", "IP Address", "Request ID"
        ])
        
        # 写入数据
        for log in result.logs:
            writer.writerow([
                log.timestamp.isoformat(),
                log.level,
                log.category,
                log.module or "",
                log.message,
                log.user_id or "",
                log.ip_address or "",
                log.request_id or ""
            ])
        
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=logs_export.csv"}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的导出格式"
        )


@router.get("/health")
async def log_system_health(
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """日志系统健康检查"""
    from .models import SystemLog
    
    try:
        total_logs = db.query(SystemLog).count()
        recent_logs = db.query(SystemLog).filter(
            SystemLog.timestamp >= datetime.utcnow() - timedelta(hours=1)
        ).count()
        
        error_logs = db.query(SystemLog).filter(
            SystemLog.level == 'ERROR',
            SystemLog.timestamp >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        return {
            "status": "healthy",
            "total_logs": total_logs,
            "recent_logs_1h": recent_logs,
            "error_logs_24h": error_logs,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"日志系统健康检查失败: {str(e)}"
        )
