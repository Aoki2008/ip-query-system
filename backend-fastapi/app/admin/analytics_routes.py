"""
管理员分析路由
提供API分析、日志分析和数据统计功能
"""
from datetime import datetime, timedelta
from typing import Dict, Any
import random

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from .models import AdminUser
from .auth.dependencies import get_current_active_user
from ..database import get_db
from ..simple_analytics import SimpleAPILog

router = APIRouter(prefix="/api/admin", tags=["管理员分析"])


@router.get("/analytics/health")
async def analytics_health(
    current_user: AdminUser = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """分析系统健康检查"""
    try:
        total_logs = db.query(SimpleAPILog).count()
        recent_logs = db.query(SimpleAPILog).filter(
            SimpleAPILog.timestamp >= datetime.utcnow() - timedelta(hours=1)
        ).count()

        return {
            "status": "healthy",
            "total_api_logs": total_logs,
            "recent_logs_1h": recent_logs,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/analytics/stats")
async def get_api_stats(
    hours: int = 24, 
    current_user: AdminUser = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """获取API统计数据"""
    start_time = datetime.utcnow() - timedelta(hours=hours)

    total_requests = db.query(SimpleAPILog).filter(SimpleAPILog.timestamp >= start_time).count()

    if total_requests == 0:
        return {
            "total_requests": 0,
            "avg_response_time": 0,
            "error_rate": 0,
            "requests_per_hour": 0,
            "top_endpoints": []
        }

    avg_response_time = db.query(func.avg(SimpleAPILog.response_time_ms)).filter(
        SimpleAPILog.timestamp >= start_time
    ).scalar() or 0

    error_count = db.query(SimpleAPILog).filter(
        SimpleAPILog.timestamp >= start_time,
        SimpleAPILog.status_code >= 400
    ).count()

    error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0
    requests_per_hour = total_requests / hours

    return {
        "total_requests": total_requests,
        "avg_response_time": round(avg_response_time, 2),
        "error_rate": round(error_rate, 2),
        "requests_per_hour": round(requests_per_hour, 2),
        "top_endpoints": []
    }


@router.post("/analytics/collect")
async def collect_sample_data(
    current_user: AdminUser = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """生成示例分析数据"""
    endpoints = [
        ("/api/query-ip", "POST"),
        ("/api/admin/auth/login", "POST"),
        ("/api/admin/auth/profile", "GET"),
        ("/api/admin/permissions/roles", "GET"),
        ("/health", "GET")
    ]

    for _ in range(20):
        endpoint, method = random.choice(endpoints)
        status_code = random.choices([200, 201, 400, 401, 404, 500], weights=[70, 10, 8, 5, 4, 3])[0]
        response_time = random.uniform(50, 2000)

        log_entry = SimpleAPILog(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time
        )

        db.add(log_entry)

    db.commit()
    return {"message": "已生成20条示例API调用记录"}


@router.get("/logs/dashboard")
async def get_logs_dashboard(
    current_user: AdminUser = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """获取日志仪表板数据"""
    try:
        total_logs = db.query(SimpleAPILog).count()
        error_logs = db.query(SimpleAPILog).filter(SimpleAPILog.status_code >= 400).count()
        error_rate = (error_logs / total_logs * 100) if total_logs > 0 else 0

        return {
            "total_logs": total_logs,
            "error_logs": error_logs,
            "error_rate": round(error_rate, 2),
            "log_levels": {
                "info": total_logs - error_logs,
                "warning": 0,
                "error": error_logs,
                "critical": 0
            },
            "recent_activity": {
                "last_hour": db.query(SimpleAPILog).filter(
                    SimpleAPILog.timestamp >= datetime.utcnow() - timedelta(hours=1)
                ).count(),
                "last_24h": db.query(SimpleAPILog).filter(
                    SimpleAPILog.timestamp >= datetime.utcnow() - timedelta(hours=24)
                ).count()
            },
            "status": "healthy"
        }
    except Exception as e:
        return {
            "total_logs": 0,
            "error_logs": 0,
            "error_rate": 0,
            "log_levels": {"info": 0, "warning": 0, "error": 0, "critical": 0},
            "recent_activity": {"last_hour": 0, "last_24h": 0},
            "status": "error",
            "error": str(e)
        }
