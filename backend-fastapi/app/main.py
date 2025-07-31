"""
FastAPI主应用
高性能异步IP查询API服务
"""
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import setup_exception_handlers
from app.api.routes import api_router
from app.services.geoip_service import geoip_service
from app.services.cache_service import cache_service
from app.middleware.performance import PerformanceMiddleware, RateLimitMiddleware
from app.database import init_database, check_database_connection
from app.admin.auth.routes import router as admin_auth_router
from app.admin.permissions.routes import router as admin_permissions_router
from app.admin.users import router as admin_users_router
from app.admin.system.routes import router as admin_system_router
from app.logging.routes import router as logging_router
from app.notifications.routes import router as notifications_router
from app.data_management.routes import router as data_management_router
from app.optimization.routes import router as optimization_router
from app.analytics.routes import router as analytics_router
from app.monitoring.routes import router as monitoring_router
from app.admin.models import AdminUser
from app.admin.auth.dependencies import get_current_active_user
from app.database import get_db
from sqlalchemy.orm import Session


# 设置日志
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("正在启动FastAPI应用...")
    
    try:
        # 初始化数据库
        if not check_database_connection():
            logger.error("数据库连接失败")
            raise Exception("数据库连接失败")

        init_database()
        logger.info("数据库初始化完成")

        # 初始化GeoIP服务
        await geoip_service.initialize()
        logger.info("GeoIP服务初始化完成")

        # 初始化缓存服务
        if settings.redis_enabled:
            await cache_service.initialize()
            logger.info("缓存服务初始化完成")

        logger.info("FastAPI应用启动完成")
        yield
        
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        raise
    finally:
        # 关闭时清理
        logger.info("正在关闭FastAPI应用...")
        
        # 关闭缓存服务
        if settings.redis_enabled:
            await cache_service.close()
            logger.info("缓存服务已关闭")
        
        # 关闭GeoIP服务
        await geoip_service.close()
        logger.info("GeoIP服务已关闭")
        
        logger.info("FastAPI应用已关闭")


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    
    # 创建FastAPI应用
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description=settings.api_description,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        contact={
            "name": "IP查询工具",
            "url": "https://github.com/your-repo/ip-query-tool",
            "email": "admin@example.com"
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        },
        tags_metadata=[
            {
                "name": "查询",
                "description": "IP地理位置查询相关接口"
            },
            {
                "name": "统计",
                "description": "服务统计和监控接口"
            },
            {
                "name": "缓存",
                "description": "缓存管理接口"
            },
            {
                "name": "系统",
                "description": "系统信息和健康检查接口"
            },
            {
                "name": "管理员认证",
                "description": "管理员登录、权限管理等接口"
            }
        ]
    )
    
    # 添加CORS中间件 (必须最先添加，确保最先处理请求)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:5175",  # 添加管理后台新端口
            "http://localhost:8080"
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
    )

    # 添加可信主机中间件
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # 生产环境应该限制具体主机
    )

    # 添加性能监控中间件
    app.add_middleware(PerformanceMiddleware)

    # 添加API分析中间件 (暂时注释)
    # app.add_middleware(APIAnalyticsMiddleware, sample_rate=1.0)
    # app.add_middleware(PerformanceAnalyticsMiddleware, slow_request_threshold=2000.0)

    # 添加频率限制中间件
    app.add_middleware(RateLimitMiddleware, calls_per_minute=120)
    
    # 设置异常处理器
    setup_exception_handlers(app)
    
    # 注册路由
    app.include_router(api_router, prefix="/api")
    app.include_router(admin_auth_router)
    app.include_router(admin_permissions_router)
    app.include_router(admin_users_router)
    app.include_router(admin_system_router)
    app.include_router(logging_router)
    app.include_router(notifications_router)
    app.include_router(data_management_router)
    app.include_router(optimization_router)
    app.include_router(analytics_router)
    app.include_router(monitoring_router)

    # 添加内联分析路由（临时解决方案，应该移到独立模块）
    from datetime import datetime, timedelta
    from sqlalchemy import func, desc
    from .simple_analytics import SimpleAPILog

    @app.get("/api/admin/analytics/health")
    async def analytics_health(current_user: AdminUser = Depends(get_current_active_user), db: Session = Depends(get_db)):
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

    @app.get("/api/admin/analytics/stats")
    async def get_api_stats(hours: int = 24, current_user: AdminUser = Depends(get_current_active_user), db: Session = Depends(get_db)):
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
            "avg_response_time": avg_response_time,
            "error_rate": error_rate,
            "requests_per_hour": requests_per_hour,
            "top_endpoints": []
        }

    @app.post("/api/admin/analytics/collect")
    async def collect_sample_data(current_user: AdminUser = Depends(get_current_active_user), db: Session = Depends(get_db)):
        import random

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

    # 数据管理API已移至 data_management/routes.py
    # 健康检查端点已在各自的路由模块中实现，此处不再重复

    # 简化的日志分析API
    @app.get("/api/admin/logs/dashboard")
    async def get_logs_dashboard(current_user: AdminUser = Depends(get_current_active_user), db: Session = Depends(get_db)):
        try:
            # 简化的日志统计
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

    # 简化的数据统计分析API
    @app.get("/api/admin/data/statistics")
    async def get_data_statistics(current_user: AdminUser = Depends(get_current_active_user), db: Session = Depends(get_db)):
        try:
            # 基于SimpleAPILog的简化统计
            total_queries = db.query(SimpleAPILog).count()
            successful_queries = db.query(SimpleAPILog).filter(SimpleAPILog.status_code < 400).count()
            failed_queries = db.query(SimpleAPILog).filter(SimpleAPILog.status_code >= 400).count()
            cached_queries = 0  # 简化版本暂不统计缓存

            # 计算比率
            success_rate = (successful_queries / total_queries * 100) if total_queries > 0 else 0
            cache_hit_rate = 0  # 简化版本

            # 平均响应时间
            avg_response_time = db.query(func.avg(SimpleAPILog.response_time_ms)).scalar() or 0

            # 唯一统计（简化）
            unique_ips = db.query(SimpleAPILog.ip_address.distinct()).count() if total_queries > 0 else 0
            unique_countries = 5  # 模拟数据
            unique_cities = 12    # 模拟数据
            unique_isps = 8       # 模拟数据

            # 热门统计（模拟数据）
            top_countries = [
                {"name": "中国", "count": int(total_queries * 0.6), "percentage": 60.0},
                {"name": "美国", "count": int(total_queries * 0.2), "percentage": 20.0},
                {"name": "日本", "count": int(total_queries * 0.1), "percentage": 10.0},
                {"name": "德国", "count": int(total_queries * 0.05), "percentage": 5.0},
                {"name": "英国", "count": int(total_queries * 0.05), "percentage": 5.0}
            ]

            top_cities = [
                {"name": "北京", "count": int(total_queries * 0.3), "percentage": 30.0},
                {"name": "上海", "count": int(total_queries * 0.2), "percentage": 20.0},
                {"name": "深圳", "count": int(total_queries * 0.15), "percentage": 15.0},
                {"name": "广州", "count": int(total_queries * 0.1), "percentage": 10.0},
                {"name": "杭州", "count": int(total_queries * 0.08), "percentage": 8.0}
            ]

            top_isps = [
                {"name": "中国电信", "count": int(total_queries * 0.4), "percentage": 40.0},
                {"name": "中国联通", "count": int(total_queries * 0.3), "percentage": 30.0},
                {"name": "中国移动", "count": int(total_queries * 0.2), "percentage": 20.0},
                {"name": "阿里云", "count": int(total_queries * 0.05), "percentage": 5.0},
                {"name": "腾讯云", "count": int(total_queries * 0.05), "percentage": 5.0}
            ]

            # 查询趋势（基于最近24小时）
            query_trends = []
            for i in range(24):
                hour_start = datetime.utcnow() - timedelta(hours=23-i)
                hour_end = hour_start + timedelta(hours=1)
                hour_queries = db.query(SimpleAPILog).filter(
                    SimpleAPILog.timestamp.between(hour_start, hour_end)
                ).count()

                query_trends.append({
                    "timestamp": hour_start.isoformat(),
                    "total_queries": hour_queries,
                    "successful_queries": int(hour_queries * 0.9),
                    "failed_queries": int(hour_queries * 0.1),
                    "cached_queries": 0,
                    "avg_response_time": avg_response_time,
                    "unique_ips": max(1, hour_queries // 3)
                })

            return {
                "total_queries": total_queries,
                "successful_queries": successful_queries,
                "failed_queries": failed_queries,
                "cached_queries": cached_queries,
                "success_rate": round(success_rate, 2),
                "cache_hit_rate": round(cache_hit_rate, 2),
                "avg_response_time": round(avg_response_time, 2),
                "unique_ips": unique_ips,
                "unique_countries": unique_countries,
                "unique_cities": unique_cities,
                "unique_isps": unique_isps,
                "top_countries": top_countries,
                "top_cities": top_cities,
                "top_isps": top_isps,
                "query_trends": query_trends
            }
        except Exception as e:
            return {
                "total_queries": 0,
                "successful_queries": 0,
                "failed_queries": 0,
                "cached_queries": 0,
                "success_rate": 0,
                "cache_hit_rate": 0,
                "avg_response_time": 0,
                "unique_ips": 0,
                "unique_countries": 0,
                "unique_cities": 0,
                "unique_isps": 0,
                "top_countries": [],
                "top_cities": [],
                "top_isps": [],
                "query_trends": [],
                "error": str(e)
            }

    # 监控路由已在 monitoring/routes.py 中实现

    # 系统监控端点已移至 monitoring/routes.py，此处不再重复实现
    
    # 根路径
    @app.get("/", response_model=Dict[str, Any])
    async def root():
        """根路径信息"""
        return {
            "message": "IP查询API服务",
            "version": settings.api_version,
            "service_type": "fastapi",
            "endpoints": {
                "health": "/api/health",
                "query_ip": "/api/query-ip?ip=<ip_address>",
                "query_batch": "/api/query-batch",
                "stats": "/api/stats",
                "cache_stats": "/api/cache/stats",
                "cache_clear": "/api/cache/clear"
            },
            "documentation": {
                "swagger": "/docs",
                "redoc": "/redoc",
                "openapi": "/openapi.json"
            }
        }
    
    # API信息接口
    @app.get("/api", response_model=Dict[str, Any])
    async def api_info():
        """API信息接口"""
        return {
            "message": "IP查询API服务",
            "version": settings.api_version,
            "status": "running",
            "service_type": "fastapi",
            "endpoints": [
                "/api/health",
                "/api/query-ip",
                "/api/query-batch",
                "/api/stats",
                "/api/cache/stats",
                "/api/cache/clear"
            ]
        }

    # 健康检查
    @app.get("/health", response_model=Dict[str, Any])
    async def health_check():
        """健康检查接口"""
        return {
            "status": "healthy",
            "message": "服务运行正常",
            "service_type": "fastapi"
        }
    
    return app


# 创建应用实例
app = create_app()
