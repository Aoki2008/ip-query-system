"""
日志配置模块
"""
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional

class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    # 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
        'RESET': '\033[0m'      # 重置
    }
    
    def format(self, record):
        # 添加颜色
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)

class LoggerConfig:
    """日志配置类"""
    
    def __init__(self, 
                 app_name: str = "ip_query_api",
                 log_level: str = "INFO",
                 log_dir: str = "logs",
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5):
        
        self.app_name = app_name
        self.log_level = getattr(logging, log_level.upper())
        self.log_dir = log_dir
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        
        # 创建日志目录
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    def setup_logger(self, logger_name: Optional[str] = None) -> logging.Logger:
        """设置日志器"""
        
        if logger_name is None:
            logger_name = self.app_name
        
        logger = logging.getLogger(logger_name)
        logger.setLevel(self.log_level)
        
        # 避免重复添加处理器
        if logger.handlers:
            return logger
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        
        # 彩色格式化器（仅用于控制台）
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # 文件处理器（应用日志）
        app_log_file = os.path.join(self.log_dir, f"{self.app_name}.log")
        file_handler = logging.handlers.RotatingFileHandler(
            app_log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        
        # 文件格式化器
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        # 错误日志文件处理器
        error_log_file = os.path.join(self.log_dir, f"{self.app_name}_error.log")
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        
        # 添加处理器
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)
        
        return logger

class RequestLogger:
    """请求日志记录器"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_request(self, method: str, path: str, ip: str, user_agent: str = ""):
        """记录请求信息"""
        self.logger.info(f"请求 {method} {path} - IP: {ip} - UA: {user_agent}")
    
    def log_response(self, method: str, path: str, status_code: int, response_time: float):
        """记录响应信息"""
        self.logger.info(f"响应 {method} {path} - 状态: {status_code} - 耗时: {response_time:.3f}s")
    
    def log_error(self, method: str, path: str, error: str, ip: str = ""):
        """记录错误信息"""
        self.logger.error(f"错误 {method} {path} - IP: {ip} - 错误: {error}")

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
    
    def record_request(self, response_time: float, success: bool = True):
        """记录请求性能数据"""
        self.request_count += 1
        self.total_response_time += response_time
        
        if not success:
            self.error_count += 1
        
        # 记录慢请求
        if response_time > 5.0:  # 超过5秒的请求
            self.logger.warning(f"慢请求检测: 响应时间 {response_time:.3f}s")
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        avg_response_time = (
            self.total_response_time / self.request_count 
            if self.request_count > 0 else 0
        )
        
        error_rate = (
            self.error_count / self.request_count * 100 
            if self.request_count > 0 else 0
        )
        
        return {
            'total_requests': self.request_count,
            'total_errors': self.error_count,
            'error_rate': f"{error_rate:.2f}%",
            'avg_response_time': f"{avg_response_time:.3f}s"
        }
    
    def log_stats(self):
        """记录统计信息"""
        stats = self.get_stats()
        self.logger.info(f"性能统计: {stats}")

# 创建全局日志配置
log_config = LoggerConfig(
    app_name="ip_query_api",
    log_level=os.getenv('LOG_LEVEL', 'INFO'),
    log_dir=os.getenv('LOG_DIR', 'logs')
)

# 创建全局日志器
app_logger = log_config.setup_logger()
request_logger = RequestLogger(app_logger)
performance_monitor = PerformanceMonitor(app_logger)

# 导出常用的日志器
def get_logger(name: str = None) -> logging.Logger:
    """获取日志器"""
    if name:
        return log_config.setup_logger(name)
    return app_logger
