"""
数据库配置和初始化
"""
import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from .config import settings

# 创建数据库引擎
if settings.database_url.startswith("sqlite"):
    # SQLite配置
    engine = create_engine(
        settings.database_url,
        echo=settings.database_echo,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL/MySQL配置
    engine = create_engine(
        settings.database_url,
        echo=settings.database_echo,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
    )

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """创建所有表"""
    # 确保数据目录存在
    if settings.database_url.startswith("sqlite"):
        db_path = settings.database_url.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    # 导入所有模型以确保它们被注册
    from .admin.models import AdminUser, QueryLog, SystemConfig, AlertLog
    from .admin.permissions.models import Permission, Role
    from .monitoring.models import SystemMetric, APIMetric, SystemAlert
    from .simple_analytics import SimpleAPILog
    from .logging.models import SystemLog, LogAlert, LogStatistic
    from .notifications.models import NotificationChannel, AlertRule, Alert, NotificationLog
    from .data_management.models import IPQueryRecord, QueryStatistic, DataCleanupRule, DataExportTask
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)


def init_default_data():
    """初始化默认数据"""
    from .admin.models import AdminUser, SystemConfig, AdminRole
    from .admin.auth.utils import get_password_hash
    
    db = SessionLocal()
    try:
        # 检查是否已有管理员用户
        admin_count = db.query(AdminUser).count()
        
        if admin_count == 0:
            # 创建默认超级管理员
            default_admin = AdminUser(
                username="admin",
                password_hash=get_password_hash("admin123"),
                email="admin@example.com",
                role=AdminRole.SUPER_ADMIN.value,
                is_active=True
            )
            db.add(default_admin)
            print("✅ 创建默认管理员用户: admin/admin123")
        
        # 初始化系统配置
        default_configs = [
            {
                "config_key": "system.name",
                "config_value": "IP查询工具管理后台",
                "config_type": "string",
                "description": "系统名称"
            },
            {
                "config_key": "system.version",
                "config_value": "1.0.0",
                "config_type": "string",
                "description": "系统版本"
            },
            {
                "config_key": "cache.enabled",
                "config_value": "true",
                "config_type": "bool",
                "description": "启用缓存"
            },
            {
                "config_key": "cache.ttl",
                "config_value": "3600",
                "config_type": "int",
                "description": "缓存过期时间(秒)"
            },
            {
                "config_key": "api.rate_limit",
                "config_value": "100",
                "config_type": "int",
                "description": "API速率限制(每小时)"
            },
            {
                "config_key": "monitoring.enabled",
                "config_value": "true",
                "config_type": "bool",
                "description": "启用系统监控"
            },
            {
                "config_key": "alerts.email_enabled",
                "config_value": "false",
                "config_type": "bool",
                "description": "启用邮件告警"
            },
            {
                "config_key": "alerts.email_smtp_host",
                "config_value": "smtp.gmail.com",
                "config_type": "string",
                "description": "SMTP服务器地址",
                "is_sensitive": False
            },
            {
                "config_key": "alerts.email_smtp_port",
                "config_value": "587",
                "config_type": "int",
                "description": "SMTP服务器端口"
            },
            {
                "config_key": "backup.enabled",
                "config_value": "true",
                "config_type": "bool",
                "description": "启用自动备份"
            },
            {
                "config_key": "backup.interval_hours",
                "config_value": "24",
                "config_type": "int",
                "description": "备份间隔(小时)"
            }
        ]
        
        for config_data in default_configs:
            existing_config = db.query(SystemConfig).filter(
                SystemConfig.config_key == config_data["config_key"]
            ).first()
            
            if not existing_config:
                config = SystemConfig(**config_data)
                db.add(config)
        
        db.commit()
        print("✅ 初始化系统配置完成")

        # 初始化权限系统
        from .admin.permissions.service import PermissionInitService
        PermissionInitService.init_all()
        
    except Exception as e:
        print(f"❌ 初始化默认数据失败: {e}")
        db.rollback()
    finally:
        db.close()


def check_database_connection():
    """检查数据库连接"""
    try:
        db = SessionLocal()
        # 执行简单查询测试连接
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


def get_database_info():
    """获取数据库信息"""
    try:
        db = SessionLocal()
        
        # 获取数据库版本信息
        if settings.database_url.startswith("sqlite"):
            result = db.execute("SELECT sqlite_version()").fetchone()
            db_type = "SQLite"
            db_version = result[0] if result else "Unknown"
        elif settings.database_url.startswith("postgresql"):
            result = db.execute("SELECT version()").fetchone()
            db_type = "PostgreSQL"
            db_version = result[0].split()[1] if result else "Unknown"
        elif settings.database_url.startswith("mysql"):
            result = db.execute("SELECT VERSION()").fetchone()
            db_type = "MySQL"
            db_version = result[0] if result else "Unknown"
        else:
            db_type = "Unknown"
            db_version = "Unknown"
        
        db.close()
        
        return {
            "type": db_type,
            "version": db_version,
            "url": settings.database_url.split("@")[-1] if "@" in settings.database_url else settings.database_url,
            "pool_size": settings.database_pool_size,
            "max_overflow": settings.database_max_overflow
        }
        
    except Exception as e:
        return {
            "type": "Unknown",
            "version": "Unknown",
            "url": "Connection failed",
            "error": str(e)
        }


# SQLite优化配置
if settings.database_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """设置SQLite优化参数"""
        cursor = dbapi_connection.cursor()
        # 启用外键约束
        cursor.execute("PRAGMA foreign_keys=ON")
        # 设置WAL模式以提高并发性能
        cursor.execute("PRAGMA journal_mode=WAL")
        # 设置同步模式
        cursor.execute("PRAGMA synchronous=NORMAL")
        # 设置缓存大小
        cursor.execute("PRAGMA cache_size=10000")
        # 设置临时存储
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()


def init_database():
    """初始化数据库"""
    print("🔧 初始化数据库...")
    
    # 检查数据库连接
    if not check_database_connection():
        print("❌ 数据库连接失败，请检查配置")
        return False
    
    try:
        # 创建表
        create_tables()
        print("✅ 数据库表创建完成")
        
        # 初始化默认数据
        init_default_data()
        
        # 显示数据库信息
        db_info = get_database_info()
        print(f"✅ 数据库初始化完成")
        print(f"   类型: {db_info['type']}")
        print(f"   版本: {db_info['version']}")
        print(f"   连接: {db_info['url']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False


if __name__ == "__main__":
    # 直接运行此文件时初始化数据库
    init_database()
