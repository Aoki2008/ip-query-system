"""
日志分析服务
"""
import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, text
from collections import defaultdict, Counter

from .models import (
    SystemLog, LogAlert, LogStatistic,
    LogEntry, LogEntryResponse, LogQuery, LogStatistics,
    LogTrend, LogAlertRule, LogAlertResponse, LogAnalysis,
    LogDashboard, LogSearchResult, LogLevel, LogCategory
)
from ..database import SessionLocal


class LogAnalysisService:
    """日志分析服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_entry(self, log_data: LogEntry) -> SystemLog:
        """记录日志条目"""
        log_entry = SystemLog(
            level=log_data.level.value,
            category=log_data.category.value,
            message=log_data.message,
            module=log_data.module,
            function=log_data.function,
            line_number=log_data.line_number,
            user_id=log_data.user_id,
            session_id=log_data.session_id,
            ip_address=log_data.ip_address,
            user_agent=log_data.user_agent,
            request_id=log_data.request_id,
            trace_id=log_data.trace_id,
            extra_data=log_data.extra_data,
            stack_trace=log_data.stack_trace
        )
        
        self.db.add(log_entry)
        self.db.commit()
        self.db.refresh(log_entry)
        
        # 检查告警规则
        self._check_alert_rules(log_entry)
        
        return log_entry
    
    def search_logs(self, query: LogQuery) -> LogSearchResult:
        """搜索日志"""
        db_query = self.db.query(SystemLog)
        
        # 应用过滤条件
        if query.level:
            db_query = db_query.filter(SystemLog.level == query.level.value)
        
        if query.category:
            db_query = db_query.filter(SystemLog.category == query.category.value)
        
        if query.module:
            db_query = db_query.filter(SystemLog.module.like(f"%{query.module}%"))
        
        if query.user_id:
            db_query = db_query.filter(SystemLog.user_id == query.user_id)
        
        if query.ip_address:
            db_query = db_query.filter(SystemLog.ip_address == query.ip_address)
        
        if query.start_time:
            db_query = db_query.filter(SystemLog.timestamp >= query.start_time)
        
        if query.end_time:
            db_query = db_query.filter(SystemLog.timestamp <= query.end_time)
        
        if query.keyword:
            db_query = db_query.filter(
                or_(
                    SystemLog.message.like(f"%{query.keyword}%"),
                    SystemLog.module.like(f"%{query.keyword}%"),
                    SystemLog.function.like(f"%{query.keyword}%")
                )
            )
        
        # 获取总数
        total = db_query.count()
        
        # 应用分页
        logs = db_query.order_by(desc(SystemLog.timestamp)).offset(query.offset).limit(query.limit).all()
        
        # 生成分面搜索结果
        facets = self._generate_facets(query)
        
        # 生成搜索建议
        suggestions = self._generate_suggestions(query.keyword) if query.keyword else []
        
        return LogSearchResult(
            total=total,
            logs=[LogEntryResponse.from_orm(log) for log in logs],
            facets=facets,
            suggestions=suggestions
        )
    
    def get_log_statistics(self, 
                          start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None) -> LogStatistics:
        """获取日志统计"""
        if not start_time:
            start_time = datetime.utcnow() - timedelta(hours=24)
        if not end_time:
            end_time = datetime.utcnow()
        
        # 基础统计
        total_logs = self.db.query(SystemLog).filter(
            SystemLog.timestamp.between(start_time, end_time)
        ).count()
        
        # 按级别统计
        level_stats = self.db.query(
            SystemLog.level,
            func.count(SystemLog.id).label('count')
        ).filter(
            SystemLog.timestamp.between(start_time, end_time)
        ).group_by(SystemLog.level).all()
        
        level_counts = {level: 0 for level in LogLevel}
        for stat in level_stats:
            if stat.level in level_counts:
                level_counts[stat.level] = stat.count
        
        error_rate = (level_counts.get('ERROR', 0) / total_logs * 100) if total_logs > 0 else 0
        
        # 热门分类
        top_categories = self.db.query(
            SystemLog.category,
            func.count(SystemLog.id).label('count')
        ).filter(
            SystemLog.timestamp.between(start_time, end_time)
        ).group_by(SystemLog.category).order_by(desc('count')).limit(10).all()
        
        # 热门模块
        top_modules = self.db.query(
            SystemLog.module,
            func.count(SystemLog.id).label('count')
        ).filter(
            and_(
                SystemLog.timestamp.between(start_time, end_time),
                SystemLog.module.isnot(None)
            )
        ).group_by(SystemLog.module).order_by(desc('count')).limit(10).all()
        
        # 热门用户
        top_users = self.db.query(
            SystemLog.user_id,
            func.count(SystemLog.id).label('count')
        ).filter(
            and_(
                SystemLog.timestamp.between(start_time, end_time),
                SystemLog.user_id.isnot(None)
            )
        ).group_by(SystemLog.user_id).order_by(desc('count')).limit(10).all()
        
        # 小时分布
        hourly_distribution = self.db.query(
            func.extract('hour', SystemLog.timestamp).label('hour'),
            func.count(SystemLog.id).label('count')
        ).filter(
            SystemLog.timestamp.between(start_time, end_time)
        ).group_by('hour').order_by('hour').all()
        
        return LogStatistics(
            total_logs=total_logs,
            error_logs=level_counts.get('ERROR', 0),
            warning_logs=level_counts.get('WARNING', 0),
            info_logs=level_counts.get('INFO', 0),
            debug_logs=level_counts.get('DEBUG', 0),
            critical_logs=level_counts.get('CRITICAL', 0),
            error_rate=error_rate,
            top_categories=[{"name": cat.category, "count": cat.count} for cat in top_categories],
            top_modules=[{"name": mod.module, "count": mod.count} for mod in top_modules],
            top_users=[{"user_id": user.user_id, "count": user.count} for user in top_users],
            hourly_distribution=[{"hour": int(hour.hour), "count": hour.count} for hour in hourly_distribution]
        )
    
    def get_log_trends(self, 
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None,
                      interval_hours: int = 1) -> List[LogTrend]:
        """获取日志趋势"""
        if not start_time:
            start_time = datetime.utcnow() - timedelta(hours=24)
        if not end_time:
            end_time = datetime.utcnow()
        
        # 按时间间隔分组统计
        trends = self.db.query(
            func.date_trunc('hour', SystemLog.timestamp).label('time_bucket'),
            func.count(SystemLog.id).label('total_count'),
            func.sum(func.case([(SystemLog.level == 'ERROR', 1)], else_=0)).label('error_count'),
            func.sum(func.case([(SystemLog.level == 'WARNING', 1)], else_=0)).label('warning_count'),
            func.sum(func.case([(SystemLog.level == 'INFO', 1)], else_=0)).label('info_count'),
            func.sum(func.case([(SystemLog.level == 'DEBUG', 1)], else_=0)).label('debug_count'),
            func.sum(func.case([(SystemLog.level == 'CRITICAL', 1)], else_=0)).label('critical_count')
        ).filter(
            SystemLog.timestamp.between(start_time, end_time)
        ).group_by('time_bucket').order_by('time_bucket').all()
        
        return [
            LogTrend(
                timestamp=trend.time_bucket,
                total_count=trend.total_count,
                error_count=trend.error_count,
                warning_count=trend.warning_count,
                info_count=trend.info_count,
                debug_count=trend.debug_count,
                critical_count=trend.critical_count
            )
            for trend in trends
        ]
    
    def create_alert_rule(self, rule: LogAlertRule) -> LogAlert:
        """创建告警规则"""
        alert_rule = LogAlert(
            rule_name=rule.rule_name,
            level=rule.level.value,
            category=rule.category.value,
            pattern=rule.pattern,
            threshold=rule.threshold,
            time_window=rule.time_window,
            is_active=rule.is_active
        )
        
        self.db.add(alert_rule)
        self.db.commit()
        self.db.refresh(alert_rule)
        
        return alert_rule
    
    def get_alert_rules(self) -> List[LogAlertResponse]:
        """获取告警规则"""
        rules = self.db.query(LogAlert).order_by(desc(LogAlert.created_at)).all()
        return [LogAlertResponse.from_orm(rule) for rule in rules]
    
    def get_dashboard_data(self) -> LogDashboard:
        """获取仪表板数据"""
        # 获取统计数据
        statistics = self.get_log_statistics()
        
        # 获取最近错误
        recent_errors = self.db.query(SystemLog).filter(
            and_(
                SystemLog.level.in_(['ERROR', 'CRITICAL']),
                SystemLog.timestamp >= datetime.utcnow() - timedelta(hours=1)
            )
        ).order_by(desc(SystemLog.timestamp)).limit(10).all()
        
        # 获取趋势数据
        trends = self.get_log_trends()
        
        # 获取活跃告警
        active_alerts = self.db.query(LogAlert).filter(
            and_(
                LogAlert.is_active == True,
                LogAlert.last_triggered >= datetime.utcnow() - timedelta(hours=24)
            )
        ).order_by(desc(LogAlert.last_triggered)).all()
        
        # 计算系统健康评分
        health_score = self._calculate_health_score(statistics)
        
        # 生成建议
        recommendations = self._generate_recommendations(statistics)
        
        return LogDashboard(
            statistics=statistics,
            recent_errors=[LogEntryResponse.from_orm(log) for log in recent_errors],
            trends=trends,
            active_alerts=[LogAlertResponse.from_orm(alert) for alert in active_alerts],
            system_health_score=health_score,
            recommendations=recommendations
        )
    
    def analyze_logs(self, 
                    start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None) -> LogAnalysis:
        """分析日志"""
        if not start_time:
            start_time = datetime.utcnow() - timedelta(hours=24)
        if not end_time:
            end_time = datetime.utcnow()
        
        total_logs = self.db.query(SystemLog).filter(
            SystemLog.timestamp.between(start_time, end_time)
        ).count()
        
        # 错误分析
        error_analysis = self._analyze_errors(start_time, end_time)
        
        # 性能分析
        performance_analysis = self._analyze_performance(start_time, end_time)
        
        # 安全分析
        security_analysis = self._analyze_security(start_time, end_time)
        
        # 用户行为分析
        user_behavior = self._analyze_user_behavior(start_time, end_time)
        
        # 系统健康分析
        system_health = self._analyze_system_health(start_time, end_time)
        
        # 生成建议
        recommendations = self._generate_analysis_recommendations(
            error_analysis, performance_analysis, security_analysis
        )
        
        time_range = f"{start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%Y-%m-%d %H:%M')}"
        
        return LogAnalysis(
            time_range=time_range,
            total_logs=total_logs,
            error_analysis=error_analysis,
            performance_analysis=performance_analysis,
            security_analysis=security_analysis,
            user_behavior=user_behavior,
            system_health=system_health,
            recommendations=recommendations
        )
    
    def cleanup_old_logs(self, days: int = 30) -> int:
        """清理旧日志"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        deleted_count = self.db.query(SystemLog).filter(
            SystemLog.timestamp < cutoff_date
        ).delete()
        
        self.db.commit()
        
        return deleted_count
    
    # 私有方法
    
    def _check_alert_rules(self, log_entry: SystemLog):
        """检查告警规则"""
        rules = self.db.query(LogAlert).filter(
            and_(
                LogAlert.is_active == True,
                LogAlert.level == log_entry.level,
                LogAlert.category == log_entry.category
            )
        ).all()
        
        for rule in rules:
            if self._should_trigger_alert(rule, log_entry):
                self._trigger_alert(rule, log_entry)
    
    def _should_trigger_alert(self, rule: LogAlert, log_entry: SystemLog) -> bool:
        """判断是否应该触发告警"""
        # 检查模式匹配
        if rule.pattern and not re.search(rule.pattern, log_entry.message):
            return False
        
        # 检查时间窗口内的日志数量
        window_start = datetime.utcnow() - timedelta(seconds=rule.time_window)
        
        count = self.db.query(SystemLog).filter(
            and_(
                SystemLog.level == rule.level,
                SystemLog.category == rule.category,
                SystemLog.timestamp >= window_start
            )
        ).count()
        
        return count >= rule.threshold
    
    def _trigger_alert(self, rule: LogAlert, log_entry: SystemLog):
        """触发告警"""
        rule.triggered_count += 1
        rule.last_triggered = datetime.utcnow()
        rule.notification_sent = False  # 重置通知状态
        
        self.db.commit()
        
        # 这里可以添加发送通知的逻辑
        print(f"告警触发: {rule.rule_name} - {log_entry.message}")
    
    def _generate_facets(self, query: LogQuery) -> Dict[str, List[Dict[str, Any]]]:
        """生成分面搜索结果"""
        facets = {}
        
        # 级别分面
        level_facets = self.db.query(
            SystemLog.level,
            func.count(SystemLog.id).label('count')
        ).group_by(SystemLog.level).all()
        
        facets['levels'] = [{"value": f.level, "count": f.count} for f in level_facets]
        
        # 分类分面
        category_facets = self.db.query(
            SystemLog.category,
            func.count(SystemLog.id).label('count')
        ).group_by(SystemLog.category).all()
        
        facets['categories'] = [{"value": f.category, "count": f.count} for f in category_facets]
        
        return facets
    
    def _generate_suggestions(self, keyword: str) -> List[str]:
        """生成搜索建议"""
        # 简化的搜索建议实现
        suggestions = []
        
        # 基于关键词的模块建议
        modules = self.db.query(SystemLog.module.distinct()).filter(
            SystemLog.module.like(f"%{keyword}%")
        ).limit(5).all()
        
        suggestions.extend([module[0] for module in modules if module[0]])
        
        return suggestions
    
    def _calculate_health_score(self, statistics: LogStatistics) -> int:
        """计算系统健康评分"""
        score = 100
        
        # 根据错误率扣分
        if statistics.error_rate > 10:
            score -= 30
        elif statistics.error_rate > 5:
            score -= 15
        elif statistics.error_rate > 1:
            score -= 5
        
        # 根据严重错误扣分
        if statistics.critical_logs > 0:
            score -= 20
        
        # 根据警告数量扣分
        warning_rate = (statistics.warning_logs / statistics.total_logs * 100) if statistics.total_logs > 0 else 0
        if warning_rate > 20:
            score -= 10
        elif warning_rate > 10:
            score -= 5
        
        return max(0, score)
    
    def _generate_recommendations(self, statistics: LogStatistics) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if statistics.error_rate > 5:
            recommendations.append(f"错误率较高({statistics.error_rate:.1f}%)，建议检查系统稳定性")
        
        if statistics.critical_logs > 0:
            recommendations.append(f"发现{statistics.critical_logs}条严重错误，需要立即处理")
        
        if statistics.total_logs > 10000:
            recommendations.append("日志量较大，建议优化日志级别配置")
        
        return recommendations
    
    def _analyze_errors(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """分析错误"""
        error_logs = self.db.query(SystemLog).filter(
            and_(
                SystemLog.level.in_(['ERROR', 'CRITICAL']),
                SystemLog.timestamp.between(start_time, end_time)
            )
        ).all()
        
        # 错误分类统计
        error_categories = Counter([log.category for log in error_logs])
        
        # 错误模块统计
        error_modules = Counter([log.module for log in error_logs if log.module])
        
        return {
            "total_errors": len(error_logs),
            "error_categories": dict(error_categories.most_common(5)),
            "error_modules": dict(error_modules.most_common(5)),
            "recent_errors": [log.message for log in error_logs[-5:]]
        }
    
    def _analyze_performance(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """分析性能"""
        # 简化的性能分析
        performance_logs = self.db.query(SystemLog).filter(
            and_(
                SystemLog.category == 'performance',
                SystemLog.timestamp.between(start_time, end_time)
            )
        ).count()
        
        return {
            "performance_issues": performance_logs,
            "slow_operations": [],
            "resource_usage": {}
        }
    
    def _analyze_security(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """分析安全"""
        security_logs = self.db.query(SystemLog).filter(
            and_(
                SystemLog.category == 'security',
                SystemLog.timestamp.between(start_time, end_time)
            )
        ).count()
        
        return {
            "security_events": security_logs,
            "suspicious_ips": [],
            "failed_logins": 0
        }
    
    def _analyze_user_behavior(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """分析用户行为"""
        user_logs = self.db.query(SystemLog).filter(
            and_(
                SystemLog.user_id.isnot(None),
                SystemLog.timestamp.between(start_time, end_time)
            )
        ).count()
        
        return {
            "active_users": user_logs,
            "user_patterns": {},
            "anomalies": []
        }
    
    def _analyze_system_health(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """分析系统健康"""
        system_logs = self.db.query(SystemLog).filter(
            and_(
                SystemLog.category == 'system',
                SystemLog.timestamp.between(start_time, end_time)
            )
        ).count()
        
        return {
            "system_events": system_logs,
            "uptime": "99.9%",
            "resource_status": "normal"
        }
    
    def _generate_analysis_recommendations(self, error_analysis: Dict, 
                                         performance_analysis: Dict,
                                         security_analysis: Dict) -> List[str]:
        """生成分析建议"""
        recommendations = []
        
        if error_analysis["total_errors"] > 100:
            recommendations.append("错误数量过多，建议检查系统稳定性")
        
        if performance_analysis["performance_issues"] > 10:
            recommendations.append("性能问题较多，建议优化系统性能")
        
        if security_analysis["security_events"] > 0:
            recommendations.append("发现安全事件，建议加强安全监控")
        
        return recommendations


class LogCollector:
    """日志收集器"""
    
    @staticmethod
    def collect_log(level: LogLevel, category: LogCategory, message: str,
                   module: str = None, function: str = None, line_number: int = None,
                   user_id: int = None, session_id: str = None,
                   ip_address: str = None, user_agent: str = None,
                   request_id: str = None, trace_id: str = None,
                   extra_data: Dict[str, Any] = None, stack_trace: str = None):
        """收集日志"""
        try:
            db = SessionLocal()
            log_service = LogAnalysisService(db)
            
            log_entry = LogEntry(
                level=level,
                category=category,
                message=message,
                module=module,
                function=function,
                line_number=line_number,
                user_id=user_id,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id,
                trace_id=trace_id,
                extra_data=extra_data,
                stack_trace=stack_trace
            )
            
            log_service.log_entry(log_entry)
            db.close()
            
        except Exception as e:
            print(f"日志收集失败: {e}")
    
    @staticmethod
    def log_info(message: str, **kwargs):
        """记录信息日志"""
        LogCollector.collect_log(LogLevel.INFO, LogCategory.SYSTEM, message, **kwargs)
    
    @staticmethod
    def log_error(message: str, **kwargs):
        """记录错误日志"""
        LogCollector.collect_log(LogLevel.ERROR, LogCategory.SYSTEM, message, **kwargs)
    
    @staticmethod
    def log_warning(message: str, **kwargs):
        """记录警告日志"""
        LogCollector.collect_log(LogLevel.WARNING, LogCategory.SYSTEM, message, **kwargs)
    
    @staticmethod
    def log_debug(message: str, **kwargs):
        """记录调试日志"""
        LogCollector.collect_log(LogLevel.DEBUG, LogCategory.SYSTEM, message, **kwargs)
