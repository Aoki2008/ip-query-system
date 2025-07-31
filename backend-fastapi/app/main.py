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
from app.core.security_middleware import SecurityMiddleware
from .core.error_handler import (
    SecurityErrorHandler,
    global_exception_handler,
    http_exception_handler
)
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

    # 添加安全中间件 (必须在其他中间件之前)
    app.add_middleware(SecurityMiddleware)

    # 添加错误处理中间件
    app.add_middleware(SecurityErrorHandler, debug=settings.debug)

    # 添加性能监控中间件
    app.add_middleware(PerformanceMiddleware)

    # 添加API分析中间件 (暂时注释)
    # app.add_middleware(APIAnalyticsMiddleware, sample_rate=1.0)
    # app.add_middleware(PerformanceAnalyticsMiddleware, slow_request_threshold=2000.0)

    # 添加频率限制中间件
    app.add_middleware(RateLimitMiddleware, calls_per_minute=120)
    
    # 设置异常处理器
    setup_exception_handlers(app)

    # 添加安全异常处理器
    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    
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

    # SEO配置路由
    from .seo.routes import router as seo_router
    app.include_router(seo_router)

    # 管理员分析路由
    from .admin.analytics_routes import router as admin_analytics_router
    from .admin.data_routes import router as admin_data_router
    app.include_router(admin_analytics_router)
    app.include_router(admin_data_router)






    
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
