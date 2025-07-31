"""
系统监控服务
"""
import psutil
import time
import platform
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from .models import (
    SystemMetric, APIMetric, SystemAlert,
    SystemStatus, ServiceStatus, APIStats, EndpointStats,
    AlertCreate, MetricCreate, MonitoringDashboard,
    PerformanceMetrics, SystemHealth, AlertLevel
)
from ..database import SessionLocal


class SystemMonitorService:
    """系统监控服务"""
    
    def __init__(self):
        self.start_time = time.time()
    
    def get_system_status(self) -> SystemStatus:
        """获取系统状态"""
        # CPU信息
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存信息
        memory = psutil.virtual_memory()
        memory_used_mb = memory.used // (1024 * 1024)
        memory_total_mb = memory.total // (1024 * 1024)
        
        # 磁盘信息
        disk = psutil.disk_usage('/')
        disk_used_gb = disk.used // (1024 * 1024 * 1024)
        disk_total_gb = disk.total // (1024 * 1024 * 1024)
        
        # 网络信息
        network = psutil.net_io_counters()
        network_sent_mb = network.bytes_sent // (1024 * 1024)
        network_recv_mb = network.bytes_recv // (1024 * 1024)
        
        # 系统运行时间
        uptime = int(time.time() - psutil.boot_time())
        
        # 负载平均值 (仅Unix系统)
        try:
            load_avg = list(psutil.getloadavg())
        except AttributeError:
            # Windows系统没有getloadavg
            load_avg = [0.0, 0.0, 0.0]
        
        # 进程数量
        process_count = len(psutil.pids())
        
        return SystemStatus(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used=memory_used_mb,
            memory_total=memory_total_mb,
            disk_percent=disk.percent,
            disk_used=disk_used_gb,
            disk_total=disk_total_gb,
            network_sent=network_sent_mb,
            network_recv=network_recv_mb,
            uptime=uptime,
            load_average=load_avg,
            process_count=process_count,
            timestamp=datetime.utcnow()
        )
    
    def get_service_status(self) -> List[ServiceStatus]:
        """获取服务状态"""
        services = []
        
        # 获取当前Python进程信息
        current_process = psutil.Process()
        
        services.append(ServiceStatus(
            name="FastAPI Server",
            status="running",
            pid=current_process.pid,
            cpu_percent=current_process.cpu_percent(),
            memory_percent=current_process.memory_percent(),
            memory_mb=current_process.memory_info().rss / (1024 * 1024),
            uptime=int(time.time() - current_process.create_time())
        ))
        
        # 查找其他相关进程
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                proc_info = proc.info
                proc_name = proc_info['name'].lower()
                
                # 检查是否是相关服务
                if any(service in proc_name for service in ['nginx', 'redis', 'postgres', 'mysql']):
                    services.append(ServiceStatus(
                        name=proc_info['name'],
                        status="running",
                        pid=proc_info['pid'],
                        cpu_percent=proc_info['cpu_percent'] or 0.0,
                        memory_percent=proc_info['memory_percent'] or 0.0,
                        memory_mb=proc.memory_info().rss / (1024 * 1024),
                        uptime=int(time.time() - proc.create_time())
                    ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return services
    
    def get_system_health(self) -> SystemHealth:
        """获取系统健康状态"""
        status = self.get_system_status()
        issues = []
        recommendations = []
        score = 100
        
        # CPU检查
        cpu_status = "healthy"
        if status.cpu_percent > 90:
            cpu_status = "critical"
            issues.append(f"CPU使用率过高: {status.cpu_percent:.1f}%")
            recommendations.append("检查CPU密集型进程，考虑优化或扩容")
            score -= 30
        elif status.cpu_percent > 70:
            cpu_status = "warning"
            issues.append(f"CPU使用率较高: {status.cpu_percent:.1f}%")
            recommendations.append("监控CPU使用情况，准备扩容计划")
            score -= 15
        
        # 内存检查
        memory_status = "healthy"
        if status.memory_percent > 90:
            memory_status = "critical"
            issues.append(f"内存使用率过高: {status.memory_percent:.1f}%")
            recommendations.append("释放内存或增加内存容量")
            score -= 25
        elif status.memory_percent > 80:
            memory_status = "warning"
            issues.append(f"内存使用率较高: {status.memory_percent:.1f}%")
            recommendations.append("监控内存使用，考虑内存优化")
            score -= 10
        
        # 磁盘检查
        disk_status = "healthy"
        if status.disk_percent > 95:
            disk_status = "critical"
            issues.append(f"磁盘使用率过高: {status.disk_percent:.1f}%")
            recommendations.append("清理磁盘空间或扩容存储")
            score -= 20
        elif status.disk_percent > 85:
            disk_status = "warning"
            issues.append(f"磁盘使用率较高: {status.disk_percent:.1f}%")
            recommendations.append("定期清理日志和临时文件")
            score -= 10
        
        # 网络和服务状态
        network_status = "healthy"
        service_status = "healthy"
        
        # 总体状态
        if score >= 90:
            overall_status = "excellent"
        elif score >= 75:
            overall_status = "good"
        elif score >= 60:
            overall_status = "warning"
        else:
            overall_status = "critical"
        
        return SystemHealth(
            overall_status=overall_status,
            cpu_status=cpu_status,
            memory_status=memory_status,
            disk_status=disk_status,
            network_status=network_status,
            service_status=service_status,
            score=max(0, score),
            issues=issues,
            recommendations=recommendations
        )


class MetricService:
    """指标服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save_metric(self, metric: MetricCreate) -> SystemMetric:
        """保存指标"""
        db_metric = SystemMetric(
            metric_type=metric.metric_type.value,
            metric_name=metric.metric_name,
            metric_value=metric.metric_value,
            metric_unit=metric.metric_unit,
            extra_data=metric.extra_data
        )
        self.db.add(db_metric)
        self.db.commit()
        self.db.refresh(db_metric)
        return db_metric
    
    def get_metrics(self, metric_type: Optional[str] = None,
                   metric_name: Optional[str] = None,
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   limit: int = 1000) -> List[SystemMetric]:
        """获取指标"""
        query = self.db.query(SystemMetric)
        
        if metric_type:
            query = query.filter(SystemMetric.metric_type == metric_type)
        if metric_name:
            query = query.filter(SystemMetric.metric_name == metric_name)
        if start_time:
            query = query.filter(SystemMetric.timestamp >= start_time)
        if end_time:
            query = query.filter(SystemMetric.timestamp <= end_time)
        
        return query.order_by(desc(SystemMetric.timestamp)).limit(limit).all()
    
    def get_latest_metrics(self, metric_names: List[str]) -> Dict[str, float]:
        """获取最新指标值"""
        result = {}
        for metric_name in metric_names:
            latest = self.db.query(SystemMetric).filter(
                SystemMetric.metric_name == metric_name
            ).order_by(desc(SystemMetric.timestamp)).first()
            
            if latest:
                result[metric_name] = latest.metric_value
            else:
                result[metric_name] = 0.0
        
        return result


class APIMetricService:
    """API指标服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def record_api_call(self, endpoint: str, method: str, status_code: int,
                       response_time: float, request_size: int = 0,
                       response_size: int = 0, user_agent: str = "",
                       ip_address: str = ""):
        """记录API调用"""
        api_metric = APIMetric(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time=response_time,
            request_size=request_size,
            response_size=response_size,
            user_agent=user_agent,
            ip_address=ip_address
        )
        self.db.add(api_metric)
        self.db.commit()
    
    def get_api_stats(self, start_time: Optional[datetime] = None,
                     end_time: Optional[datetime] = None) -> APIStats:
        """获取API统计"""
        if not start_time:
            start_time = datetime.utcnow() - timedelta(hours=24)
        if not end_time:
            end_time = datetime.utcnow()
        
        query = self.db.query(APIMetric).filter(
            APIMetric.timestamp >= start_time,
            APIMetric.timestamp <= end_time
        )
        
        total_requests = query.count()
        success_requests = query.filter(APIMetric.status_code < 400).count()
        error_requests = total_requests - success_requests
        
        if total_requests > 0:
            avg_response_time = query.with_entities(
                func.avg(APIMetric.response_time)
            ).scalar() or 0.0
            
            max_response_time = query.with_entities(
                func.max(APIMetric.response_time)
            ).scalar() or 0.0
            
            min_response_time = query.with_entities(
                func.min(APIMetric.response_time)
            ).scalar() or 0.0
            
            # 计算每分钟请求数
            time_diff = (end_time - start_time).total_seconds() / 60
            requests_per_minute = total_requests / time_diff if time_diff > 0 else 0
            
            error_rate = (error_requests / total_requests) * 100
        else:
            avg_response_time = 0.0
            max_response_time = 0.0
            min_response_time = 0.0
            requests_per_minute = 0.0
            error_rate = 0.0
        
        return APIStats(
            total_requests=total_requests,
            success_requests=success_requests,
            error_requests=error_requests,
            avg_response_time=avg_response_time,
            max_response_time=max_response_time,
            min_response_time=min_response_time,
            requests_per_minute=requests_per_minute,
            error_rate=error_rate
        )
    
    def get_endpoint_stats(self, limit: int = 10) -> List[EndpointStats]:
        """获取端点统计"""
        # 获取过去24小时的数据
        start_time = datetime.utcnow() - timedelta(hours=24)
        
        # 按端点和方法分组统计
        stats = self.db.query(
            APIMetric.endpoint,
            APIMetric.method,
            func.count(APIMetric.id).label('request_count'),
            func.avg(APIMetric.response_time).label('avg_response_time'),
            func.sum(func.case([(APIMetric.status_code >= 400, 1)], else_=0)).label('error_count'),
            func.max(APIMetric.timestamp).label('last_request')
        ).filter(
            APIMetric.timestamp >= start_time
        ).group_by(
            APIMetric.endpoint, APIMetric.method
        ).order_by(
            desc('request_count')
        ).limit(limit).all()
        
        result = []
        for stat in stats:
            error_rate = (stat.error_count / stat.request_count) * 100 if stat.request_count > 0 else 0
            
            result.append(EndpointStats(
                endpoint=stat.endpoint,
                method=stat.method,
                request_count=stat.request_count,
                avg_response_time=stat.avg_response_time or 0.0,
                error_count=stat.error_count,
                error_rate=error_rate,
                last_request=stat.last_request
            ))
        
        return result


class AlertService:
    """告警服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_alert(self, alert: AlertCreate) -> SystemAlert:
        """创建告警"""
        db_alert = SystemAlert(
            alert_type=alert.alert_type,
            level=alert.level.value,
            title=alert.title,
            message=alert.message,
            metric_name=alert.metric_name,
            metric_value=alert.metric_value,
            threshold_value=alert.threshold_value
        )
        self.db.add(db_alert)
        self.db.commit()
        self.db.refresh(db_alert)
        return db_alert
    
    def get_recent_alerts(self, limit: int = 10) -> List[SystemAlert]:
        """获取最近告警"""
        return self.db.query(SystemAlert).order_by(
            desc(SystemAlert.created_at)
        ).limit(limit).all()
    
    def resolve_alert(self, alert_id: int) -> bool:
        """解决告警"""
        alert = self.db.query(SystemAlert).filter(SystemAlert.id == alert_id).first()
        if alert:
            alert.is_resolved = True
            alert.resolved_at = datetime.utcnow()
            self.db.commit()
            return True
        return False


class MonitoringService:
    """监控服务聚合"""

    def __init__(self, db: Session):
        self.db = db
        self.system_monitor = SystemMonitorService()
        self.metric_service = MetricService(db)
        self.api_metric_service = APIMetricService(db)
        self.alert_service = AlertService(db)

    def get_dashboard_data(self) -> MonitoringDashboard:
        """获取监控仪表板数据"""
        system_status = self.system_monitor.get_system_status()
        service_status = self.system_monitor.get_service_status()
        api_stats = self.api_metric_service.get_api_stats()
        recent_alerts = self.alert_service.get_recent_alerts(5)
        top_endpoints = self.api_metric_service.get_endpoint_stats(5)

        return MonitoringDashboard(
            system_status=system_status,
            service_status=service_status,
            api_stats=api_stats,
            recent_alerts=recent_alerts,
            top_endpoints=top_endpoints
        )

    def collect_system_metrics(self):
        """收集系统指标"""
        status = self.system_monitor.get_system_status()

        # 保存系统指标
        metrics = [
            MetricCreate(
                metric_type="system",
                metric_name="cpu_percent",
                metric_value=status.cpu_percent,
                metric_unit="%"
            ),
            MetricCreate(
                metric_type="system",
                metric_name="memory_percent",
                metric_value=status.memory_percent,
                metric_unit="%"
            ),
            MetricCreate(
                metric_type="system",
                metric_name="disk_percent",
                metric_value=status.disk_percent,
                metric_unit="%"
            ),
            MetricCreate(
                metric_type="system",
                metric_name="process_count",
                metric_value=status.process_count,
                metric_unit="count"
            )
        ]

        for metric in metrics:
            self.metric_service.save_metric(metric)

        # 检查告警条件
        self._check_alert_conditions(status)

    def _check_alert_conditions(self, status: SystemStatus):
        """检查告警条件"""
        alerts = []

        # CPU告警
        if status.cpu_percent > 90:
            alerts.append(AlertCreate(
                alert_type="system",
                level=AlertLevel.CRITICAL,
                title="CPU使用率过高",
                message=f"CPU使用率达到 {status.cpu_percent:.1f}%，超过90%阈值",
                metric_name="cpu_percent",
                metric_value=status.cpu_percent,
                threshold_value=90.0
            ))
        elif status.cpu_percent > 80:
            alerts.append(AlertCreate(
                alert_type="system",
                level=AlertLevel.WARNING,
                title="CPU使用率较高",
                message=f"CPU使用率达到 {status.cpu_percent:.1f}%，超过80%阈值",
                metric_name="cpu_percent",
                metric_value=status.cpu_percent,
                threshold_value=80.0
            ))

        # 内存告警
        if status.memory_percent > 90:
            alerts.append(AlertCreate(
                alert_type="system",
                level=AlertLevel.CRITICAL,
                title="内存使用率过高",
                message=f"内存使用率达到 {status.memory_percent:.1f}%，超过90%阈值",
                metric_name="memory_percent",
                metric_value=status.memory_percent,
                threshold_value=90.0
            ))
        elif status.memory_percent > 85:
            alerts.append(AlertCreate(
                alert_type="system",
                level=AlertLevel.WARNING,
                title="内存使用率较高",
                message=f"内存使用率达到 {status.memory_percent:.1f}%，超过85%阈值",
                metric_name="memory_percent",
                metric_value=status.memory_percent,
                threshold_value=85.0
            ))

        # 磁盘告警
        if status.disk_percent > 95:
            alerts.append(AlertCreate(
                alert_type="system",
                level=AlertLevel.CRITICAL,
                title="磁盘空间不足",
                message=f"磁盘使用率达到 {status.disk_percent:.1f}%，超过95%阈值",
                metric_name="disk_percent",
                metric_value=status.disk_percent,
                threshold_value=95.0
            ))
        elif status.disk_percent > 90:
            alerts.append(AlertCreate(
                alert_type="system",
                level=AlertLevel.WARNING,
                title="磁盘空间较少",
                message=f"磁盘使用率达到 {status.disk_percent:.1f}%，超过90%阈值",
                metric_name="disk_percent",
                metric_value=status.disk_percent,
                threshold_value=90.0
            ))

        # 创建告警
        for alert in alerts:
            self.alert_service.create_alert(alert)
