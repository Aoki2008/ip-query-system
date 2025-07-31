"""
应用配置模块
使用Pydantic Settings进行配置管理
"""
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 服务器配置
    host: str = Field(default="0.0.0.0", description="服务器主机地址")
    port: int = Field(default=8000, description="服务器端口")
    debug: bool = Field(default=False, description="调试模式")
    reload: bool = Field(default=False, description="自动重载")
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(default="json", description="日志格式")
    
    # Redis配置
    redis_host: str = Field(default="localhost", description="Redis主机")
    redis_port: int = Field(default=6379, description="Redis端口")
    redis_db: int = Field(default=0, description="Redis数据库")
    redis_password: Optional[str] = Field(default=None, description="Redis密码")
    redis_enabled: bool = Field(default=True, description="启用Redis缓存")
    
    # 缓存配置
    cache_ttl: int = Field(default=3600, description="缓存过期时间(秒)")
    cache_max_size: int = Field(default=10000, description="缓存最大条目数")
    
    # GeoIP配置
    geoip_db_path: str = Field(
        default="./data/GeoLite2-City.mmdb",
        description="GeoIP数据库路径"
    )
    geoip_asn_db_path: str = Field(
        default="../GeoLite2-ASN.mmdb",
        description="GeoIP ASN数据库路径"
    )
    geoip_update_interval: int = Field(
        default=86400,
        description="GeoIP数据库更新间隔(秒)"
    )

    # 数据库切换配置
    current_geoip_source: str = Field(
        default="local",  # local, api, mixed
        description="当前使用的GeoIP数据源"
    )
    
    # API配置
    api_title: str = Field(default="IP查询API服务", description="API标题")
    api_version: str = Field(default="1.0.0", description="API版本")
    api_description: str = Field(
        default="高性能异步IP地理位置查询服务", 
        description="API描述"
    )
    
    # CORS配置
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:5174",  # 管理后台
            "http://localhost:8080"
        ],
        description="允许的CORS源"
    )
    cors_allow_credentials: bool = Field(default=True, description="允许凭证")
    cors_allow_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="允许的HTTP方法"
    )
    cors_allow_headers: List[str] = Field(
        default=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
        description="允许的请求头"
    )
    
    # 性能配置
    max_batch_size: int = Field(default=100, description="最大批量查询数量")
    concurrent_limit: int = Field(default=50, description="并发限制")
    request_timeout: int = Field(default=30, description="请求超时时间(秒)")
    
    # 监控配置
    enable_metrics: bool = Field(default=True, description="启用指标收集")
    metrics_path: str = Field(default="/metrics", description="指标路径")

    # 数据库配置
    database_url: str = Field(
        default="sqlite:///./data/admin.db",
        description="数据库连接URL"
    )
    database_echo: bool = Field(default=False, description="数据库SQL日志")
    database_pool_size: int = Field(default=5, description="数据库连接池大小")
    database_max_overflow: int = Field(default=10, description="数据库连接池最大溢出")

    # 管理后台配置
    admin_secret_key: str = Field(
        default="dev-secret-key-change-in-production-must-be-32-chars-long",
        description="管理后台JWT密钥"
    )
    admin_access_token_expire_minutes: int = Field(
        default=15,
        description="访问令牌过期时间(分钟)"
    )
    admin_refresh_token_expire_days: int = Field(
        default=7,
        description="刷新令牌过期时间(天)"
    )
    admin_max_login_attempts: int = Field(
        default=5,
        description="最大登录尝试次数"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局配置实例
settings = Settings()
