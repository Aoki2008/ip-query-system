"""
简化的API性能统计功能
"""
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from .admin.models import AdminUser
from .admin.auth.dependencies import get_current_active_user
from .database import get_db, Base
from sqlalchemy import Column, Integer, String, Float, DateTime

# 创建简化的API日志表
class SimpleAPILog(Base):
    __tablename__ = "simple_api_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(200), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

# 创建路由
analytics_router = APIRouter(prefix="/api/admin/analytics", tags=["API分析"])

class APIStats(BaseModel):
    """API统计模型"""
    total_requests: int
    avg_response_time: float
    error_rate: float
    requests_per_hour: float
    top_endpoints: List[Dict[str, Any]]

class EndpointStats(BaseModel):
    """端点统计模型"""
    endpoint: str
    method: str
    total_calls: int
    avg_response_time: float
    error_rate: float

def log_api_call(endpoint: str, method: str, status_code: int, response_time_ms: float):
    """记录API调用"""
    try:
        from .database import SessionLocal
        db = SessionLocal()
        
        log_entry = SimpleAPILog(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms
        )
        
        db.add(log_entry)
        db.commit()
        db.close()
        
    except Exception as e:
        print(f"记录API调用失败: {e}")

@analytics_router.get("/health")
async def analytics_health(
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """分析服务健康检查"""
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

@analytics_router.get("/stats", response_model=APIStats)
async def get_api_stats(
    hours: int = 24,
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取API统计"""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    # 基础统计
    total_requests = db.query(SimpleAPILog).filter(
        SimpleAPILog.timestamp >= start_time
    ).count()
    
    if total_requests == 0:
        return APIStats(
            total_requests=0,
            avg_response_time=0,
            error_rate=0,
            requests_per_hour=0,
            top_endpoints=[]
        )
    
    # 平均响应时间
    avg_response_time = db.query(func.avg(SimpleAPILog.response_time_ms)).filter(
        SimpleAPILog.timestamp >= start_time
    ).scalar() or 0
    
    # 错误率
    error_count = db.query(SimpleAPILog).filter(
        SimpleAPILog.timestamp >= start_time,
        SimpleAPILog.status_code >= 400
    ).count()
    
    error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0
    requests_per_hour = total_requests / hours
    
    # 热门端点
    top_endpoints_query = db.query(
        SimpleAPILog.endpoint,
        SimpleAPILog.method,
        func.count(SimpleAPILog.id).label('total_calls'),
        func.avg(SimpleAPILog.response_time_ms).label('avg_response_time'),
        func.sum(func.case([(SimpleAPILog.status_code >= 400, 1)], else_=0)).label('error_count')
    ).filter(
        SimpleAPILog.timestamp >= start_time
    ).group_by(
        SimpleAPILog.endpoint, SimpleAPILog.method
    ).order_by(
        desc('total_calls')
    ).limit(5).all()
    
    top_endpoints = []
    for result in top_endpoints_query:
        endpoint_error_rate = (result.error_count / result.total_calls * 100) if result.total_calls > 0 else 0
        top_endpoints.append({
            "endpoint": result.endpoint,
            "method": result.method,
            "total_calls": result.total_calls,
            "avg_response_time": result.avg_response_time or 0,
            "error_rate": endpoint_error_rate
        })
    
    return APIStats(
        total_requests=total_requests,
        avg_response_time=avg_response_time,
        error_rate=error_rate,
        requests_per_hour=requests_per_hour,
        top_endpoints=top_endpoints
    )

@analytics_router.get("/endpoints", response_model=List[EndpointStats])
async def get_endpoint_stats(
    hours: int = 24,
    limit: int = 10,
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取端点统计"""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    results = db.query(
        SimpleAPILog.endpoint,
        SimpleAPILog.method,
        func.count(SimpleAPILog.id).label('total_calls'),
        func.avg(SimpleAPILog.response_time_ms).label('avg_response_time'),
        func.sum(func.case([(SimpleAPILog.status_code >= 400, 1)], else_=0)).label('error_count')
    ).filter(
        SimpleAPILog.timestamp >= start_time
    ).group_by(
        SimpleAPILog.endpoint, SimpleAPILog.method
    ).order_by(
        desc('total_calls')
    ).limit(limit).all()
    
    endpoint_stats = []
    for result in results:
        error_rate = (result.error_count / result.total_calls * 100) if result.total_calls > 0 else 0
        
        endpoint_stats.append(EndpointStats(
            endpoint=result.endpoint,
            method=result.method,
            total_calls=result.total_calls,
            avg_response_time=result.avg_response_time or 0,
            error_rate=error_rate
        ))
    
    return endpoint_stats

@analytics_router.post("/collect")
async def collect_sample_data(
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """收集示例数据"""
    import random
    
    # 生成示例数据
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

@analytics_router.get("/dashboard")
async def get_analytics_dashboard(
    hours: int = 24,
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取分析仪表板"""
    stats = await get_api_stats(hours, current_user, db)
    endpoints = await get_endpoint_stats(hours, 5, current_user, db)
    
    return {
        "summary": stats,
        "top_endpoints": endpoints,
        "timestamp": datetime.utcnow().isoformat()
    }
