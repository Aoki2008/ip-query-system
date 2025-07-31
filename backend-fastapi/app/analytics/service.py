"""
API性能统计分析服务
"""
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, text
from collections import defaultdict, Counter

from .models import (
    APICallLog, APIPerformanceMetric, UserActivityLog,
    APICallLogCreate, APIPerformanceStats, APITrendData,
    TopEndpointsStats, ErrorAnalysis, UserActivityStats,
    PerformanceSummary, APIAnalyticsDashboard, TimeRange,
    RealTimeMetrics, PerformanceReport
)
from ..database import SessionLocal


class APIAnalyticsService:
    """API分析服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_api_call(self, log_data: APICallLogCreate) -> APICallLog:
        """记录API调用"""
        api_log = APICallLog(
            endpoint=log_data.endpoint,
            method=log_data.method,
            status_code=log_data.status_code,
            response_time_ms=log_data.response_time_ms,
            request_size=log_data.request_size,
            response_size=log_data.response_size,
            user_agent=log_data.user_agent,
            ip_address=log_data.ip_address,
            user_id=log_data.user_id,
            error_message=log_data.error_message,
            request_data=log_data.request_data
        )
        self.db.add(api_log)
        self.db.commit()
        self.db.refresh(api_log)
        return api_log
    
    def get_performance_stats(self, 
                            time_range: TimeRange = TimeRange.LAST_24_HOURS,
                            endpoint: Optional[str] = None,
                            method: Optional[str] = None) -> List[APIPerformanceStats]:
        """获取API性能统计"""
        start_time = self._get_start_time(time_range)
        
        query = self.db.query(
            APICallLog.endpoint,
            APICallLog.method,
            func.count(APICallLog.id).label('total_calls'),
            func.sum(func.case([(APICallLog.status_code < 400, 1)], else_=0)).label('success_calls'),
            func.sum(func.case([(APICallLog.status_code >= 400, 1)], else_=0)).label('error_calls'),
            func.avg(APICallLog.response_time_ms).label('avg_response_time'),
            func.min(APICallLog.response_time_ms).label('min_response_time'),
            func.max(APICallLog.response_time_ms).label('max_response_time'),
            func.avg(APICallLog.request_size).label('avg_request_size'),
            func.avg(APICallLog.response_size).label('avg_response_size')
        ).filter(APICallLog.timestamp >= start_time)
        
        if endpoint:
            query = query.filter(APICallLog.endpoint == endpoint)
        if method:
            query = query.filter(APICallLog.method == method)
        
        query = query.group_by(APICallLog.endpoint, APICallLog.method)
        results = query.all()
        
        stats = []
        for result in results:
            # 计算百分位数
            p95, p99 = self._calculate_percentiles(
                result.endpoint, result.method, start_time
            )
            
            error_rate = (result.error_calls / result.total_calls * 100) if result.total_calls > 0 else 0
            time_diff_hours = (datetime.utcnow() - start_time).total_seconds() / 3600
            calls_per_hour = result.total_calls / time_diff_hours if time_diff_hours > 0 else 0
            
            stats.append(APIPerformanceStats(
                endpoint=result.endpoint,
                method=result.method,
                total_calls=result.total_calls,
                success_calls=result.success_calls,
                error_calls=result.error_calls,
                error_rate=error_rate,
                avg_response_time=result.avg_response_time or 0,
                min_response_time=result.min_response_time or 0,
                max_response_time=result.max_response_time or 0,
                p95_response_time=p95,
                p99_response_time=p99,
                calls_per_hour=calls_per_hour,
                avg_request_size=result.avg_request_size or 0,
                avg_response_size=result.avg_response_size or 0
            ))
        
        return sorted(stats, key=lambda x: x.total_calls, reverse=True)
    
    def get_trend_data(self, 
                      time_range: TimeRange = TimeRange.LAST_24_HOURS,
                      interval_minutes: int = 60) -> List[APITrendData]:
        """获取API趋势数据"""
        start_time = self._get_start_time(time_range)
        
        # 按时间间隔分组统计
        time_format = self._get_time_format(interval_minutes)
        
        query = self.db.query(
            func.date_trunc('hour', APICallLog.timestamp).label('time_bucket'),
            func.count(APICallLog.id).label('total_calls'),
            func.avg(APICallLog.response_time_ms).label('avg_response_time'),
            func.sum(func.case([(APICallLog.status_code >= 400, 1)], else_=0)).label('error_count')
        ).filter(
            APICallLog.timestamp >= start_time
        ).group_by('time_bucket').order_by('time_bucket')
        
        results = query.all()
        
        trend_data = []
        for result in results:
            error_rate = (result.error_count / result.total_calls * 100) if result.total_calls > 0 else 0
            success_rate = 100 - error_rate
            
            trend_data.append(APITrendData(
                timestamp=result.time_bucket,
                total_calls=result.total_calls,
                avg_response_time=result.avg_response_time or 0,
                error_rate=error_rate,
                success_rate=success_rate
            ))
        
        return trend_data
    
    def get_top_endpoints(self, 
                         time_range: TimeRange = TimeRange.LAST_24_HOURS,
                         limit: int = 10) -> List[TopEndpointsStats]:
        """获取热门端点统计"""
        start_time = self._get_start_time(time_range)
        
        query = self.db.query(
            APICallLog.endpoint,
            APICallLog.method,
            func.count(APICallLog.id).label('total_calls'),
            func.avg(APICallLog.response_time_ms).label('avg_response_time'),
            func.sum(func.case([(APICallLog.status_code >= 400, 1)], else_=0)).label('error_count'),
            func.max(APICallLog.timestamp).label('last_called')
        ).filter(
            APICallLog.timestamp >= start_time
        ).group_by(
            APICallLog.endpoint, APICallLog.method
        ).order_by(
            desc('total_calls')
        ).limit(limit)
        
        results = query.all()
        
        top_endpoints = []
        for result in results:
            error_rate = (result.error_count / result.total_calls * 100) if result.total_calls > 0 else 0
            
            top_endpoints.append(TopEndpointsStats(
                endpoint=result.endpoint,
                method=result.method,
                total_calls=result.total_calls,
                avg_response_time=result.avg_response_time or 0,
                error_rate=error_rate,
                last_called=result.last_called
            ))
        
        return top_endpoints
    
    def get_error_analysis(self, 
                          time_range: TimeRange = TimeRange.LAST_24_HOURS) -> List[ErrorAnalysis]:
        """获取错误分析"""
        start_time = self._get_start_time(time_range)
        
        # 获取错误统计
        error_query = self.db.query(
            APICallLog.status_code,
            func.count(APICallLog.id).label('count'),
            func.array_agg(APICallLog.endpoint.distinct()).label('endpoints'),
            func.array_agg(APICallLog.error_message).label('error_messages')
        ).filter(
            and_(
                APICallLog.timestamp >= start_time,
                APICallLog.status_code >= 400
            )
        ).group_by(APICallLog.status_code).order_by(desc('count'))
        
        total_errors = self.db.query(func.count(APICallLog.id)).filter(
            and_(
                APICallLog.timestamp >= start_time,
                APICallLog.status_code >= 400
            )
        ).scalar() or 0
        
        results = error_query.all()
        
        error_analysis = []
        for result in results:
            percentage = (result.count / total_errors * 100) if total_errors > 0 else 0
            
            # 获取最近的错误信息
            recent_errors = [msg for msg in (result.error_messages or []) if msg][:5]
            
            error_analysis.append(ErrorAnalysis(
                status_code=result.status_code,
                count=result.count,
                percentage=percentage,
                endpoints=list(set(result.endpoints or [])),
                recent_errors=recent_errors
            ))
        
        return error_analysis
    
    def get_user_activity_stats(self, 
                               time_range: TimeRange = TimeRange.LAST_24_HOURS,
                               limit: int = 10) -> List[UserActivityStats]:
        """获取用户活动统计"""
        start_time = self._get_start_time(time_range)
        
        # 从API调用日志中统计用户活动
        query = self.db.query(
            APICallLog.user_id,
            func.count(APICallLog.id).label('total_actions'),
            func.count(APICallLog.endpoint.distinct()).label('unique_resources'),
            func.sum(func.case([(APICallLog.status_code < 400, 1)], else_=0)).label('success_count'),
            func.max(APICallLog.timestamp).label('last_activity')
        ).filter(
            and_(
                APICallLog.timestamp >= start_time,
                APICallLog.user_id.isnot(None)
            )
        ).group_by(APICallLog.user_id).order_by(desc('total_actions')).limit(limit)
        
        results = query.all()
        
        user_stats = []
        for result in results:
            success_rate = (result.success_count / result.total_actions * 100) if result.total_actions > 0 else 0
            
            # 获取用户名（这里简化处理）
            username = f"user_{result.user_id}"
            
            # 获取用户热门操作
            top_actions = self._get_user_top_actions(result.user_id, start_time)
            
            user_stats.append(UserActivityStats(
                user_id=result.user_id,
                username=username,
                total_actions=result.total_actions,
                unique_resources=result.unique_resources,
                success_rate=success_rate,
                last_activity=result.last_activity,
                top_actions=top_actions
            ))
        
        return user_stats
    
    def get_performance_summary(self, 
                               time_range: TimeRange = TimeRange.LAST_24_HOURS) -> PerformanceSummary:
        """获取性能摘要"""
        start_time = self._get_start_time(time_range)
        
        # 基础统计
        basic_stats = self.db.query(
            func.count(APICallLog.id).label('total_requests'),
            func.sum(func.case([(APICallLog.status_code >= 400, 1)], else_=0)).label('total_errors'),
            func.avg(APICallLog.response_time_ms).label('avg_response_time')
        ).filter(APICallLog.timestamp >= start_time).first()
        
        # 计算每分钟请求数
        time_diff_minutes = (datetime.utcnow() - start_time).total_seconds() / 60
        requests_per_minute = basic_stats.total_requests / time_diff_minutes if time_diff_minutes > 0 else 0
        
        # 错误率
        error_rate = (basic_stats.total_errors / basic_stats.total_requests * 100) if basic_stats.total_requests > 0 else 0
        
        # 运行时间百分比（简化计算）
        uptime_percentage = max(0, 100 - error_rate)
        
        # 获取峰值小时
        peak_hour = self._get_peak_hour(start_time)
        
        # 获取最慢端点
        slowest_endpoint = self._get_slowest_endpoint(start_time)
        
        # 获取最活跃用户
        most_active_user = self._get_most_active_user(start_time)
        
        return PerformanceSummary(
            total_requests=basic_stats.total_requests,
            total_errors=basic_stats.total_errors,
            avg_response_time=basic_stats.avg_response_time or 0,
            requests_per_minute=requests_per_minute,
            error_rate=error_rate,
            uptime_percentage=uptime_percentage,
            peak_hour=peak_hour,
            slowest_endpoint=slowest_endpoint,
            most_active_user=most_active_user
        )
    
    def get_analytics_dashboard(self, 
                               time_range: TimeRange = TimeRange.LAST_24_HOURS) -> APIAnalyticsDashboard:
        """获取分析仪表板数据"""
        summary = self.get_performance_summary(time_range)
        top_endpoints = self.get_top_endpoints(time_range, limit=5)
        error_analysis = self.get_error_analysis(time_range)
        trend_data = self.get_trend_data(time_range)
        user_activity = self.get_user_activity_stats(time_range, limit=5)
        
        # 生成性能告警
        performance_alerts = self._generate_performance_alerts(summary)
        
        return APIAnalyticsDashboard(
            summary=summary,
            top_endpoints=top_endpoints,
            error_analysis=error_analysis,
            trend_data=trend_data,
            user_activity=user_activity,
            performance_alerts=performance_alerts
        )
    
    def get_real_time_metrics(self) -> RealTimeMetrics:
        """获取实时指标"""
        now = datetime.utcnow()
        one_minute_ago = now - timedelta(minutes=1)
        
        # 1分钟内的统计
        recent_stats = self.db.query(
            func.count(APICallLog.id).label('total_requests'),
            func.sum(func.case([(APICallLog.status_code >= 400, 1)], else_=0)).label('error_count'),
            func.avg(APICallLog.response_time_ms).label('avg_response_time')
        ).filter(APICallLog.timestamp >= one_minute_ago).first()
        
        current_rps = recent_stats.total_requests / 60.0 if recent_stats.total_requests else 0
        current_error_rate = (recent_stats.error_count / recent_stats.total_requests * 100) if recent_stats.total_requests > 0 else 0
        
        # 获取系统指标（简化）
        import psutil
        memory_usage = psutil.virtual_memory().percent
        cpu_usage = psutil.cpu_percent()
        
        return RealTimeMetrics(
            current_rps=current_rps,
            current_error_rate=current_error_rate,
            avg_response_time_1min=recent_stats.avg_response_time or 0,
            active_connections=0,  # 简化处理
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            timestamp=now
        )
    
    # 辅助方法
    
    def _get_start_time(self, time_range: TimeRange) -> datetime:
        """根据时间范围获取开始时间"""
        now = datetime.utcnow()
        if time_range == TimeRange.LAST_HOUR:
            return now - timedelta(hours=1)
        elif time_range == TimeRange.LAST_6_HOURS:
            return now - timedelta(hours=6)
        elif time_range == TimeRange.LAST_24_HOURS:
            return now - timedelta(hours=24)
        elif time_range == TimeRange.LAST_7_DAYS:
            return now - timedelta(days=7)
        elif time_range == TimeRange.LAST_30_DAYS:
            return now - timedelta(days=30)
        else:
            return now - timedelta(hours=24)
    
    def _calculate_percentiles(self, endpoint: str, method: str, start_time: datetime) -> Tuple[float, float]:
        """计算响应时间百分位数"""
        response_times = self.db.query(APICallLog.response_time_ms).filter(
            and_(
                APICallLog.endpoint == endpoint,
                APICallLog.method == method,
                APICallLog.timestamp >= start_time
            )
        ).all()
        
        if not response_times:
            return 0.0, 0.0
        
        times = [rt[0] for rt in response_times]
        p95 = np.percentile(times, 95)
        p99 = np.percentile(times, 99)
        
        return float(p95), float(p99)
    
    def _get_time_format(self, interval_minutes: int) -> str:
        """获取时间格式"""
        if interval_minutes <= 60:
            return 'hour'
        elif interval_minutes <= 1440:  # 24小时
            return 'day'
        else:
            return 'week'
    
    def _get_user_top_actions(self, user_id: int, start_time: datetime) -> List[Dict[str, Any]]:
        """获取用户热门操作"""
        actions = self.db.query(
            APICallLog.endpoint,
            APICallLog.method,
            func.count(APICallLog.id).label('count')
        ).filter(
            and_(
                APICallLog.user_id == user_id,
                APICallLog.timestamp >= start_time
            )
        ).group_by(APICallLog.endpoint, APICallLog.method).order_by(desc('count')).limit(3).all()
        
        return [
            {
                "action": f"{action.method} {action.endpoint}",
                "count": action.count
            }
            for action in actions
        ]
    
    def _get_peak_hour(self, start_time: datetime) -> str:
        """获取峰值小时"""
        peak = self.db.query(
            func.extract('hour', APICallLog.timestamp).label('hour'),
            func.count(APICallLog.id).label('count')
        ).filter(
            APICallLog.timestamp >= start_time
        ).group_by('hour').order_by(desc('count')).first()
        
        return f"{int(peak.hour):02d}:00" if peak else "00:00"
    
    def _get_slowest_endpoint(self, start_time: datetime) -> str:
        """获取最慢端点"""
        slowest = self.db.query(
            APICallLog.endpoint,
            APICallLog.method,
            func.avg(APICallLog.response_time_ms).label('avg_time')
        ).filter(
            APICallLog.timestamp >= start_time
        ).group_by(APICallLog.endpoint, APICallLog.method).order_by(desc('avg_time')).first()
        
        return f"{slowest.method} {slowest.endpoint}" if slowest else "N/A"
    
    def _get_most_active_user(self, start_time: datetime) -> str:
        """获取最活跃用户"""
        active_user = self.db.query(
            APICallLog.user_id,
            func.count(APICallLog.id).label('count')
        ).filter(
            and_(
                APICallLog.timestamp >= start_time,
                APICallLog.user_id.isnot(None)
            )
        ).group_by(APICallLog.user_id).order_by(desc('count')).first()
        
        return f"user_{active_user.user_id}" if active_user else "N/A"
    
    def _generate_performance_alerts(self, summary: PerformanceSummary) -> List[str]:
        """生成性能告警"""
        alerts = []
        
        if summary.error_rate > 10:
            alerts.append(f"高错误率警告: {summary.error_rate:.1f}%")
        
        if summary.avg_response_time > 2000:
            alerts.append(f"响应时间过慢: {summary.avg_response_time:.0f}ms")
        
        if summary.requests_per_minute > 1000:
            alerts.append(f"高负载警告: {summary.requests_per_minute:.0f} req/min")
        
        return alerts


class APIMetricsCollector:
    """API指标收集器"""

    @staticmethod
    def collect_api_metrics(endpoint: str, method: str, status_code: int,
                           response_time_ms: float, request_size: int = 0,
                           response_size: int = 0, user_agent: str = "",
                           ip_address: str = "", user_id: Optional[int] = None,
                           error_message: Optional[str] = None):
        """收集API指标"""
        try:
            db = SessionLocal()
            analytics_service = APIAnalyticsService(db)

            log_data = APICallLogCreate(
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time_ms=response_time_ms,
                request_size=request_size,
                response_size=response_size,
                user_agent=user_agent,
                ip_address=ip_address,
                user_id=user_id,
                error_message=error_message
            )

            analytics_service.log_api_call(log_data)
            db.close()

        except Exception as e:
            print(f"收集API指标失败: {e}")

    @staticmethod
    def log_user_activity(user_id: int, username: str, action: str,
                         resource: str, ip_address: str = "",
                         user_agent: str = "", details: Optional[Dict[str, Any]] = None,
                         success: bool = True):
        """记录用户活动"""
        try:
            db = SessionLocal()

            activity_log = UserActivityLog(
                user_id=user_id,
                username=username,
                action=action,
                resource=resource,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details,
                success=success
            )

            db.add(activity_log)
            db.commit()
            db.close()

        except Exception as e:
            print(f"记录用户活动失败: {e}")
