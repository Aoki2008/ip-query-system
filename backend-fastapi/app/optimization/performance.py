"""
性能优化系统
"""
import time
import psutil
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from functools import wraps
from contextlib import asynccontextmanager
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..database import SessionLocal


class PerformanceMetrics(BaseModel):
    """性能指标模型"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int]
    disk_io: Dict[str, int]
    process_count: int
    load_average: List[float]
    response_time_avg: float
    requests_per_second: float
    error_rate: float
    timestamp: datetime


class DatabasePerformance(BaseModel):
    """数据库性能模型"""
    connection_count: int
    active_queries: int
    slow_queries: int
    query_cache_hit_rate: float
    table_sizes: Dict[str, int]
    index_usage: Dict[str, float]
    lock_waits: int
    deadlocks: int


class APIPerformance(BaseModel):
    """API性能模型"""
    endpoint: str
    method: str
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_count: int
    error_count: int
    error_rate: float
    throughput: float


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.max_history_size = 1000
        self.monitoring_interval = 60  # 秒
        self.is_monitoring = False
    
    def get_current_metrics(self) -> PerformanceMetrics:
        """获取当前性能指标"""
        try:
            # CPU使用率
            cpu_usage = psutil.cpu_percent(interval=1)

            # 内存使用率
            memory = psutil.virtual_memory()
            memory_usage = memory.percent

            # 磁盘使用率
            try:
                disk = psutil.disk_usage('/')
                disk_usage = disk.percent
            except:
                # Windows使用C盘
                disk = psutil.disk_usage('C:')
                disk_usage = disk.percent

            # 网络IO
            try:
                network_io = psutil.net_io_counters()._asdict()
            except:
                network_io = {"bytes_sent": 0, "bytes_recv": 0}

            # 磁盘IO
            try:
                disk_io = psutil.disk_io_counters()._asdict()
            except:
                disk_io = {"read_bytes": 0, "write_bytes": 0}

            # 进程数量
            try:
                process_count = len(psutil.pids())
            except:
                process_count = 0

            # 负载平均值
            try:
                load_average = list(psutil.getloadavg())
            except AttributeError:
                load_average = [0.0, 0.0, 0.0]  # Windows不支持
        except Exception as e:
            print(f"获取性能指标失败: {e}")
            # 返回默认值
            cpu_usage = 0.0
            memory_usage = 0.0
            disk_usage = 0.0
            network_io = {"bytes_sent": 0, "bytes_recv": 0}
            disk_io = {"read_bytes": 0, "write_bytes": 0}
            process_count = 0
            load_average = [0.0, 0.0, 0.0]
        
        return PerformanceMetrics(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            network_io=network_io,
            disk_io=disk_io,
            process_count=process_count,
            load_average=load_average,
            response_time_avg=0.0,  # 需要从其他地方获取
            requests_per_second=0.0,  # 需要从其他地方获取
            error_rate=0.0,  # 需要从其他地方获取
            timestamp=datetime.utcnow()
        )
    
    def start_monitoring(self):
        """开始性能监控"""
        self.is_monitoring = True
        asyncio.create_task(self._monitoring_loop())
    
    def stop_monitoring(self):
        """停止性能监控"""
        self.is_monitoring = False
    
    async def _monitoring_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                metrics = self.get_current_metrics()
                self.metrics_history.append(metrics)
                
                # 保持历史记录大小
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history.pop(0)
                
                await asyncio.sleep(self.monitoring_interval)
            except Exception as e:
                print(f"性能监控错误: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    def get_metrics_history(self, hours: int = 24) -> List[PerformanceMetrics]:
        """获取性能指标历史"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [m for m in self.metrics_history if m.timestamp >= cutoff_time]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = self.get_metrics_history(1)  # 最近1小时
        if not recent_metrics:
            recent_metrics = self.metrics_history[-10:]  # 最近10个记录
        
        # 计算平均值
        avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
        avg_disk = sum(m.disk_usage for m in recent_metrics) / len(recent_metrics)
        
        # 计算峰值
        max_cpu = max(m.cpu_usage for m in recent_metrics)
        max_memory = max(m.memory_usage for m in recent_metrics)
        max_disk = max(m.disk_usage for m in recent_metrics)
        
        return {
            "avg_cpu_usage": round(avg_cpu, 2),
            "avg_memory_usage": round(avg_memory, 2),
            "avg_disk_usage": round(avg_disk, 2),
            "max_cpu_usage": round(max_cpu, 2),
            "max_memory_usage": round(max_memory, 2),
            "max_disk_usage": round(max_disk, 2),
            "total_samples": len(recent_metrics),
            "monitoring_duration_hours": 1
        }


class DatabaseOptimizer:
    """数据库优化器"""
    
    def __init__(self):
        self.slow_query_threshold = 1000  # 毫秒
    
    def analyze_database_performance(self) -> DatabasePerformance:
        """分析数据库性能"""
        db = SessionLocal()
        try:
            # 获取连接数（简化）
            connection_count = 1  # 当前连接
            
            # 获取表大小
            table_sizes = self._get_table_sizes(db)
            
            # 简化的性能指标
            return DatabasePerformance(
                connection_count=connection_count,
                active_queries=0,
                slow_queries=0,
                query_cache_hit_rate=95.0,  # 模拟数据
                table_sizes=table_sizes,
                index_usage={},
                lock_waits=0,
                deadlocks=0
            )
        finally:
            db.close()
    
    def _get_table_sizes(self, db: Session) -> Dict[str, int]:
        """获取表大小"""
        try:
            # PostgreSQL查询表大小
            result = db.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_total_relation_size(schemaname||'.'||tablename) as size
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY size DESC
                LIMIT 10
            """))
            
            table_sizes = {}
            for row in result:
                table_name = f"{row.schemaname}.{row.tablename}"
                table_sizes[table_name] = row.size
            
            return table_sizes
        except Exception as e:
            print(f"获取表大小失败: {e}")
            return {}
    
    def optimize_database(self) -> Dict[str, Any]:
        """优化数据库"""
        optimizations = []
        
        db = SessionLocal()
        try:
            # 分析表统计信息
            db.execute(text("ANALYZE"))
            optimizations.append("更新表统计信息")
            
            # 清理临时文件（如果支持）
            try:
                db.execute(text("VACUUM"))
                optimizations.append("执行VACUUM清理")
            except:
                pass
            
            db.commit()
            
        except Exception as e:
            print(f"数据库优化失败: {e}")
        finally:
            db.close()
        
        return {
            "optimizations_applied": optimizations,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取慢查询"""
        # 这里应该从数据库日志或性能表中获取慢查询
        # 简化实现
        return [
            {
                "query": "SELECT * FROM large_table WHERE condition",
                "duration_ms": 2500,
                "timestamp": datetime.utcnow().isoformat(),
                "database": "main"
            }
        ]


class APIOptimizer:
    """API优化器"""
    
    def __init__(self):
        self.performance_data: Dict[str, List[float]] = {}
    
    def record_api_performance(self, endpoint: str, method: str, response_time: float, status_code: int):
        """记录API性能"""
        key = f"{method}:{endpoint}"
        if key not in self.performance_data:
            self.performance_data[key] = []
        
        self.performance_data[key].append(response_time)
        
        # 保持最近1000个记录
        if len(self.performance_data[key]) > 1000:
            self.performance_data[key] = self.performance_data[key][-1000:]
    
    def get_api_performance(self, endpoint: str = None) -> List[APIPerformance]:
        """获取API性能统计"""
        results = []
        
        for key, response_times in self.performance_data.items():
            if endpoint and endpoint not in key:
                continue
            
            method, ep = key.split(":", 1)
            
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                min_time = min(response_times)
                max_time = max(response_times)
                
                # 计算百分位数
                sorted_times = sorted(response_times)
                p95_index = int(len(sorted_times) * 0.95)
                p99_index = int(len(sorted_times) * 0.99)
                p95_time = sorted_times[p95_index] if p95_index < len(sorted_times) else max_time
                p99_time = sorted_times[p99_index] if p99_index < len(sorted_times) else max_time
                
                results.append(APIPerformance(
                    endpoint=ep,
                    method=method,
                    avg_response_time=avg_time,
                    min_response_time=min_time,
                    max_response_time=max_time,
                    p95_response_time=p95_time,
                    p99_response_time=p99_time,
                    requests_count=len(response_times),
                    error_count=0,  # 简化
                    error_rate=0.0,  # 简化
                    throughput=len(response_times) / 3600  # 简化：假设1小时内的数据
                ))
        
        return sorted(results, key=lambda x: x.avg_response_time, reverse=True)
    
    def get_optimization_recommendations(self) -> List[str]:
        """获取优化建议"""
        recommendations = []
        
        api_performance = self.get_api_performance()
        
        for api in api_performance:
            if api.avg_response_time > 2000:  # 2秒
                recommendations.append(f"API {api.method} {api.endpoint} 响应时间过长({api.avg_response_time:.0f}ms)，建议优化")
            
            if api.p99_response_time > 5000:  # 5秒
                recommendations.append(f"API {api.method} {api.endpoint} P99响应时间过长，存在性能瓶颈")
        
        return recommendations


def performance_monitor(func: Callable):
    """性能监控装饰器"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            duration = (end_time - start_time) * 1000  # 毫秒
            print(f"函数 {func.__name__} 执行时间: {duration:.2f}ms")
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            duration = (end_time - start_time) * 1000  # 毫秒
            print(f"函数 {func.__name__} 执行时间: {duration:.2f}ms")
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


@asynccontextmanager
async def performance_context(operation_name: str):
    """性能监控上下文管理器"""
    start_time = time.time()
    try:
        yield
    finally:
        end_time = time.time()
        duration = (end_time - start_time) * 1000
        print(f"操作 {operation_name} 执行时间: {duration:.2f}ms")


class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self):
        self.monitor = PerformanceMonitor()
        self.db_optimizer = DatabaseOptimizer()
        self.api_optimizer = APIOptimizer()
    
    def get_system_performance_report(self) -> Dict[str, Any]:
        """获取系统性能报告"""
        # 系统性能
        system_metrics = self.monitor.get_current_metrics()
        system_summary = self.monitor.get_performance_summary()
        
        # 数据库性能
        db_performance = self.db_optimizer.analyze_database_performance()
        
        # API性能
        api_performance = self.api_optimizer.get_api_performance()
        
        # 优化建议
        recommendations = []
        recommendations.extend(self.api_optimizer.get_optimization_recommendations())
        
        if system_metrics.cpu_usage > 80:
            recommendations.append(f"CPU使用率过高({system_metrics.cpu_usage:.1f}%)，建议优化或扩容")
        
        if system_metrics.memory_usage > 85:
            recommendations.append(f"内存使用率过高({system_metrics.memory_usage:.1f}%)，建议优化内存使用")
        
        return {
            "system_metrics": system_metrics.dict(),
            "system_summary": system_summary,
            "database_performance": db_performance.dict(),
            "api_performance": [api.dict() for api in api_performance[:10]],
            "recommendations": recommendations,
            "report_generated_at": datetime.utcnow().isoformat()
        }
    
    def optimize_system(self) -> Dict[str, Any]:
        """优化系统"""
        optimizations = []
        
        # 数据库优化
        db_result = self.db_optimizer.optimize_database()
        optimizations.extend(db_result.get("optimizations_applied", []))
        
        # 系统优化
        system_metrics = self.monitor.get_current_metrics()
        
        if system_metrics.memory_usage > 80:
            # 触发垃圾回收
            import gc
            gc.collect()
            optimizations.append("执行垃圾回收")
        
        return {
            "optimizations_applied": optimizations,
            "optimization_time": datetime.utcnow().isoformat(),
            "next_optimization_recommended": (datetime.utcnow() + timedelta(hours=6)).isoformat()
        }
    
    def get_performance_alerts(self) -> List[Dict[str, Any]]:
        """获取性能告警"""
        alerts = []
        
        system_metrics = self.monitor.get_current_metrics()
        
        if system_metrics.cpu_usage > 90:
            alerts.append({
                "type": "cpu_high",
                "severity": "critical",
                "message": f"CPU使用率过高: {system_metrics.cpu_usage:.1f}%",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        if system_metrics.memory_usage > 95:
            alerts.append({
                "type": "memory_high",
                "severity": "critical",
                "message": f"内存使用率过高: {system_metrics.memory_usage:.1f}%",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        if system_metrics.disk_usage > 90:
            alerts.append({
                "type": "disk_high",
                "severity": "warning",
                "message": f"磁盘使用率过高: {system_metrics.disk_usage:.1f}%",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return alerts


# 全局性能优化器实例
performance_optimizer = PerformanceOptimizer()
