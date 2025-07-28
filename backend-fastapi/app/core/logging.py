"""
日志配置模块
使用structlog进行结构化日志记录
"""
import logging
import sys
from typing import Any, Dict

import structlog
from pythonjsonlogger import jsonlogger

from app.config import settings


def setup_logging() -> None:
    """设置日志配置"""
    
    # 配置标准库logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper())
    )
    
    # 配置structlog
    if settings.log_format.lower() == "json":
        # JSON格式日志
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    else:
        # 控制台格式日志
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                structlog.dev.ConsoleRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """获取日志记录器"""
    return structlog.get_logger(name)


class RequestLogger:
    """请求日志记录器"""
    
    def __init__(self):
        self.logger = get_logger("request")
    
    def log_request(self, method: str, path: str, ip: str, user_agent: str = "") -> None:
        """记录请求信息"""
        self.logger.info(
            "请求开始",
            method=method,
            path=path,
            client_ip=ip,
            user_agent=user_agent
        )
    
    def log_response(
        self, 
        method: str, 
        path: str, 
        status_code: int, 
        response_time: float
    ) -> None:
        """记录响应信息"""
        self.logger.info(
            "请求完成",
            method=method,
            path=path,
            status_code=status_code,
            response_time_ms=round(response_time * 1000, 2)
        )


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.logger = get_logger("performance")
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_response_time": 0.0,
            "avg_response_time": 0.0
        }
    
    def record_request(self, response_time: float, success: bool = True) -> None:
        """记录请求性能数据"""
        self.stats["total_requests"] += 1
        self.stats["total_response_time"] += response_time
        
        if success:
            self.stats["successful_requests"] += 1
        else:
            self.stats["failed_requests"] += 1
        
        # 计算平均响应时间
        if self.stats["total_requests"] > 0:
            self.stats["avg_response_time"] = (
                self.stats["total_response_time"] / self.stats["total_requests"]
            )
        
        # 记录性能日志
        self.logger.info(
            "性能数据",
            response_time_ms=round(response_time * 1000, 2),
            success=success,
            total_requests=self.stats["total_requests"],
            avg_response_time_ms=round(self.stats["avg_response_time"] * 1000, 2)
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        return self.stats.copy()


# 全局实例
request_logger = RequestLogger()
performance_monitor = PerformanceMonitor()
