"""
系统优化路由
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session

from .cache import cache_manager, cache_optimizer, ip_query_cache, statistics_cache
from .performance import performance_optimizer
from .security import security_manager
from ..admin.models import AdminUser
from ..admin.auth.dependencies import get_current_active_user, require_super_admin
from ..database import get_db

router = APIRouter(prefix="/api/admin/optimization", tags=["系统优化"])


# 缓存管理路由

@router.get("/cache/info")
async def get_cache_info(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取缓存信息"""
    cache_info = cache_manager.get_cache_info()
    ip_cache_stats = ip_query_cache.get_cache_stats()
    
    return {
        "cache_info": cache_info,
        "ip_cache_stats": ip_cache_stats,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/cache/performance")
async def get_cache_performance(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取缓存性能分析"""
    performance_analysis = cache_optimizer.analyze_cache_performance()
    return performance_analysis


@router.post("/cache/optimize")
async def optimize_cache(
    current_user: AdminUser = Depends(require_super_admin)
):
    """优化缓存设置"""
    optimization_result = cache_optimizer.optimize_cache_settings()
    return optimization_result


@router.delete("/cache/clear")
async def clear_cache(
    pattern: Optional[str] = Query(None, description="缓存键模式"),
    current_user: AdminUser = Depends(require_super_admin)
):
    """清理缓存"""
    if pattern:
        deleted_count = cache_manager.delete_by_pattern(pattern)
        return {
            "message": f"已删除匹配模式 '{pattern}' 的 {deleted_count} 个缓存项",
            "deleted_count": deleted_count
        }
    else:
        success = cache_manager.flush_all()
        return {
            "message": "已清空所有缓存" if success else "清空缓存失败",
            "success": success
        }


@router.post("/cache/ip/{ip_address}/refresh")
async def refresh_ip_cache(
    ip_address: str,
    current_user: AdminUser = Depends(require_super_admin)
):
    """刷新IP缓存"""
    deleted = ip_query_cache.delete_ip_info(ip_address)
    return {
        "message": f"IP {ip_address} 缓存已{'删除' if deleted else '不存在'}",
        "deleted": deleted
    }


# 性能监控路由

@router.get("/performance/metrics")
async def get_performance_metrics(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取性能指标"""
    metrics = performance_optimizer.monitor.get_current_metrics()
    return metrics.dict()


@router.get("/performance/summary")
async def get_performance_summary(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取性能摘要"""
    summary = performance_optimizer.monitor.get_performance_summary()
    return summary


@router.get("/performance/report")
async def get_performance_report(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取系统性能报告"""
    report = performance_optimizer.get_system_performance_report()
    return report


@router.get("/performance/alerts")
async def get_performance_alerts(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取性能告警"""
    alerts = performance_optimizer.get_performance_alerts()
    return {"alerts": alerts}


@router.post("/performance/optimize")
async def optimize_system_performance(
    background_tasks: BackgroundTasks,
    current_user: AdminUser = Depends(require_super_admin)
):
    """优化系统性能"""
    def run_optimization():
        return performance_optimizer.optimize_system()
    
    background_tasks.add_task(run_optimization)
    
    return {"message": "系统性能优化任务已启动"}


@router.get("/performance/database")
async def get_database_performance(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取数据库性能"""
    db_performance = performance_optimizer.db_optimizer.analyze_database_performance()
    return db_performance.dict()


@router.get("/performance/api")
async def get_api_performance(
    endpoint: Optional[str] = Query(None, description="端点过滤"),
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取API性能统计"""
    api_performance = performance_optimizer.api_optimizer.get_api_performance(endpoint)
    return [api.dict() for api in api_performance]


@router.post("/performance/monitoring/start")
async def start_performance_monitoring(
    current_user: AdminUser = Depends(require_super_admin)
):
    """开始性能监控"""
    performance_optimizer.monitor.start_monitoring()
    return {"message": "性能监控已启动"}


@router.post("/performance/monitoring/stop")
async def stop_performance_monitoring(
    current_user: AdminUser = Depends(require_super_admin)
):
    """停止性能监控"""
    performance_optimizer.monitor.stop_monitoring()
    return {"message": "性能监控已停止"}


# 安全管理路由

@router.get("/security/status")
async def get_security_status(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取安全状态"""
    threat_analysis = security_manager.analyze_security_threats()
    return {
        "security_status": "secure" if threat_analysis["threat_level"] == "low" else "at_risk",
        "threat_analysis": threat_analysis,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/security/report")
async def get_security_report(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取安全报告"""
    report = security_manager.generate_security_report()
    return report


@router.get("/security/events")
async def get_security_events(
    hours: int = Query(24, ge=1, le=168, description="时间范围(小时)"),
    severity: Optional[str] = Query(None, description="严重程度过滤"),
    event_type: Optional[str] = Query(None, description="事件类型过滤"),
    limit: int = Query(100, ge=1, le=500, description="返回数量"),
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取安全事件"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    events = [
        e for e in security_manager.security_events
        if e.timestamp > cutoff_time
    ]
    
    if severity:
        events = [e for e in events if e.severity == severity]
    
    if event_type:
        events = [e for e in events if e.event_type == event_type]
    
    # 按时间倒序排列
    events = sorted(events, key=lambda x: x.timestamp, reverse=True)
    
    return {
        "events": [e.dict() for e in events[:limit]],
        "total": len(events),
        "filtered": len(events) < len(security_manager.security_events)
    }


@router.get("/security/blocked-ips")
async def get_blocked_ips(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取被封禁的IP列表"""
    return {
        "blocked_ips": list(security_manager.blocked_ips),
        "count": len(security_manager.blocked_ips)
    }


@router.post("/security/block-ip")
async def block_ip(
    ip_address: str,
    reason: str = "手动封禁",
    current_user: AdminUser = Depends(require_super_admin)
):
    """封禁IP地址"""
    security_manager.blocked_ips.add(ip_address)
    security_manager._log_security_event(
        "manual_ip_block",
        "medium",
        ip_address,
        "",
        f"管理员手动封禁IP: {reason}",
        {"admin_user": current_user.username, "reason": reason}
    )
    
    return {
        "message": f"IP {ip_address} 已被封禁",
        "reason": reason
    }


@router.delete("/security/unblock-ip")
async def unblock_ip(
    ip_address: str,
    current_user: AdminUser = Depends(require_super_admin)
):
    """解封IP地址"""
    if ip_address in security_manager.blocked_ips:
        security_manager.blocked_ips.remove(ip_address)
        security_manager._log_security_event(
            "manual_ip_unblock",
            "low",
            ip_address,
            "",
            f"管理员手动解封IP",
            {"admin_user": current_user.username}
        )
        return {
            "message": f"IP {ip_address} 已解封",
            "success": True
        }
    else:
        return {
            "message": f"IP {ip_address} 未在封禁列表中",
            "success": False
        }


@router.post("/security/password/validate")
async def validate_password(
    password: str,
    current_user: AdminUser = Depends(get_current_active_user)
):
    """验证密码强度"""
    validation_result = security_manager.validate_password(password)
    return validation_result


@router.get("/security/recommendations")
async def get_security_recommendations(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取安全建议"""
    recommendations = security_manager.get_security_recommendations()
    return {"recommendations": recommendations}


# 综合优化路由

@router.get("/dashboard")
async def get_optimization_dashboard(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """获取优化仪表板"""
    # 缓存性能
    cache_performance = cache_optimizer.analyze_cache_performance()
    
    # 系统性能
    system_performance = performance_optimizer.get_system_performance_report()
    
    # 安全状态
    security_status = security_manager.analyze_security_threats()
    
    return {
        "cache_performance": cache_performance,
        "system_performance": system_performance,
        "security_status": security_status,
        "dashboard_generated_at": datetime.utcnow().isoformat()
    }


@router.post("/optimize-all")
async def optimize_all_systems(
    background_tasks: BackgroundTasks,
    current_user: AdminUser = Depends(require_super_admin)
):
    """优化所有系统"""
    def run_full_optimization():
        results = {}
        
        # 缓存优化
        try:
            cache_result = cache_optimizer.optimize_cache_settings()
            results["cache"] = cache_result
        except Exception as e:
            results["cache"] = {"error": str(e)}
        
        # 性能优化
        try:
            performance_result = performance_optimizer.optimize_system()
            results["performance"] = performance_result
        except Exception as e:
            results["performance"] = {"error": str(e)}
        
        return results
    
    background_tasks.add_task(run_full_optimization)
    
    return {"message": "全系统优化任务已启动"}


@router.get("/health")
async def optimization_system_health(
    current_user: AdminUser = Depends(get_current_active_user)
):
    """优化系统健康检查"""
    try:
        # 检查缓存系统
        cache_info = cache_manager.get_cache_info()
        cache_healthy = cache_info.get("hit_rate", 0) > 50
        
        # 检查性能监控
        performance_metrics = performance_optimizer.monitor.get_current_metrics()
        performance_healthy = (
            performance_metrics.cpu_usage < 90 and 
            performance_metrics.memory_usage < 90
        )
        
        # 检查安全系统
        security_analysis = security_manager.analyze_security_threats()
        security_healthy = security_analysis["threat_level"] in ["low", "medium"]
        
        overall_health = cache_healthy and performance_healthy and security_healthy
        
        return {
            "status": "healthy" if overall_health else "degraded",
            "cache_healthy": cache_healthy,
            "performance_healthy": performance_healthy,
            "security_healthy": security_healthy,
            "cache_hit_rate": cache_info.get("hit_rate", 0),
            "cpu_usage": performance_metrics.cpu_usage,
            "memory_usage": performance_metrics.memory_usage,
            "threat_level": security_analysis["threat_level"],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"优化系统健康检查失败: {str(e)}"
        )
