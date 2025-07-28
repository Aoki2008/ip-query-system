"""
监控和告警系统
"""
import time
import threading
import logging
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import deque, defaultdict

# 邮件相关导入（可选）
try:
    import smtplib
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class MetricData:
    """指标数据"""
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}

@dataclass
class AlertRule:
    """告警规则"""
    name: str
    metric: str
    condition: str  # 'gt', 'lt', 'eq', 'gte', 'lte'
    threshold: float
    duration: int  # 持续时间（秒）
    severity: str  # 'critical', 'warning', 'info'
    enabled: bool = True
    
class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, max_points: int = 1000):
        self.metrics = defaultdict(lambda: deque(maxlen=max_points))
        self.lock = threading.Lock()
    
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """记录指标"""
        metric = MetricData(
            name=name,
            value=value,
            timestamp=time.time(),
            tags=tags or {}
        )
        
        with self.lock:
            self.metrics[name].append(metric)
        
        logger.debug(f"记录指标: {name}={value}")
    
    def get_metric_history(self, name: str, duration: int = 3600) -> List[MetricData]:
        """获取指标历史"""
        cutoff_time = time.time() - duration
        
        with self.lock:
            if name not in self.metrics:
                return []
            
            return [
                metric for metric in self.metrics[name]
                if metric.timestamp >= cutoff_time
            ]
    
    def get_metric_stats(self, name: str, duration: int = 3600) -> Dict[str, float]:
        """获取指标统计"""
        history = self.get_metric_history(name, duration)
        
        if not history:
            return {}
        
        values = [metric.value for metric in history]
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'latest': values[-1] if values else 0
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """获取所有指标"""
        result = {}
        
        with self.lock:
            for name in self.metrics.keys():
                result[name] = self.get_metric_stats(name)
        
        return result

class AlertManager:
    """告警管理器"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.rules: List[AlertRule] = []
        self.active_alerts: Dict[str, Dict] = {}
        self.alert_history: deque = deque(maxlen=1000)
        self.notification_handlers: List[Callable] = []
        self.lock = threading.Lock()
        
        # 启动监控线程
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("告警管理器已启动")
    
    def add_rule(self, rule: AlertRule):
        """添加告警规则"""
        with self.lock:
            self.rules.append(rule)
        logger.info(f"添加告警规则: {rule.name}")
    
    def add_notification_handler(self, handler: Callable):
        """添加通知处理器"""
        self.notification_handlers.append(handler)
    
    def _check_rule(self, rule: AlertRule) -> bool:
        """检查告警规则"""
        if not rule.enabled:
            return False
        
        # 获取指标历史
        history = self.metrics_collector.get_metric_history(rule.metric, rule.duration)
        
        if not history:
            return False
        
        # 检查条件
        latest_value = history[-1].value
        
        conditions = {
            'gt': latest_value > rule.threshold,
            'lt': latest_value < rule.threshold,
            'eq': latest_value == rule.threshold,
            'gte': latest_value >= rule.threshold,
            'lte': latest_value <= rule.threshold
        }
        
        return conditions.get(rule.condition, False)
    
    def _trigger_alert(self, rule: AlertRule, metric_value: float):
        """触发告警"""
        alert_id = f"{rule.name}_{rule.metric}"
        
        alert_data = {
            'id': alert_id,
            'rule': rule.name,
            'metric': rule.metric,
            'value': metric_value,
            'threshold': rule.threshold,
            'condition': rule.condition,
            'severity': rule.severity,
            'timestamp': time.time(),
            'status': 'active'
        }
        
        with self.lock:
            self.active_alerts[alert_id] = alert_data
            self.alert_history.append(alert_data.copy())
        
        # 发送通知
        for handler in self.notification_handlers:
            try:
                handler(alert_data)
            except Exception as e:
                logger.error(f"通知处理器执行失败: {e}")
        
        logger.warning(f"触发告警: {rule.name} - {rule.metric}={metric_value}")
    
    def _resolve_alert(self, rule: AlertRule):
        """解决告警"""
        alert_id = f"{rule.name}_{rule.metric}"
        
        with self.lock:
            if alert_id in self.active_alerts:
                alert_data = self.active_alerts[alert_id]
                alert_data['status'] = 'resolved'
                alert_data['resolved_at'] = time.time()
                
                self.alert_history.append(alert_data.copy())
                del self.active_alerts[alert_id]
                
                logger.info(f"告警已解决: {rule.name}")
    
    def _monitoring_loop(self):
        """监控循环"""
        while True:
            try:
                with self.lock:
                    rules_to_check = self.rules.copy()
                
                for rule in rules_to_check:
                    alert_id = f"{rule.name}_{rule.metric}"
                    is_triggered = self._check_rule(rule)
                    is_active = alert_id in self.active_alerts
                    
                    if is_triggered and not is_active:
                        # 新告警
                        history = self.metrics_collector.get_metric_history(rule.metric, 60)
                        if history:
                            self._trigger_alert(rule, history[-1].value)
                    elif not is_triggered and is_active:
                        # 告警恢复
                        self._resolve_alert(rule)
                
                time.sleep(10)  # 每10秒检查一次
                
            except Exception as e:
                logger.error(f"监控循环异常: {e}")
                time.sleep(30)
    
    def get_active_alerts(self) -> List[Dict]:
        """获取活跃告警"""
        with self.lock:
            return list(self.active_alerts.values())
    
    def get_alert_history(self, limit: int = 100) -> List[Dict]:
        """获取告警历史"""
        with self.lock:
            return list(self.alert_history)[-limit:]

class EmailNotifier:
    """邮件通知器"""

    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str):
        if not EMAIL_AVAILABLE:
            raise ImportError("邮件功能不可用，请检查email模块")

        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    def send_alert(self, alert_data: Dict):
        """发送告警邮件"""
        try:
            subject = f"[{alert_data['severity'].upper()}] {alert_data['rule']}"
            
            body = f"""
告警详情:
- 规则: {alert_data['rule']}
- 指标: {alert_data['metric']}
- 当前值: {alert_data['value']}
- 阈值: {alert_data['threshold']}
- 条件: {alert_data['condition']}
- 严重程度: {alert_data['severity']}
- 时间: {datetime.fromtimestamp(alert_data['timestamp'])}

请及时处理。
"""
            
            msg = MimeMultipart()
            msg['From'] = self.username
            msg['Subject'] = subject
            msg.attach(MimeText(body, 'plain'))
            
            # 这里需要配置收件人列表
            recipients = os.getenv('ALERT_RECIPIENTS', '').split(',')
            recipients = [r.strip() for r in recipients if r.strip()]
            
            if not recipients:
                logger.warning("未配置告警邮件收件人")
                return
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                
                for recipient in recipients:
                    msg['To'] = recipient
                    server.send_message(msg)
                    del msg['To']
            
            logger.info(f"告警邮件已发送: {subject}")
            
        except Exception as e:
            logger.error(f"发送告警邮件失败: {e}")

class HealthChecker:
    """健康检查器"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.checks: Dict[str, Callable] = {}
    
    def register_check(self, name: str, check_func: Callable):
        """注册健康检查"""
        self.checks[name] = check_func
        logger.info(f"注册健康检查: {name}")
    
    def run_checks(self) -> Dict[str, Any]:
        """运行所有健康检查"""
        results = {}
        overall_healthy = True
        
        for name, check_func in self.checks.items():
            try:
                start_time = time.time()
                result = check_func()
                duration = time.time() - start_time
                
                # 记录检查耗时
                self.metrics_collector.record_metric(
                    f"health_check_duration_{name}",
                    duration
                )
                
                if isinstance(result, bool):
                    results[name] = {
                        'healthy': result,
                        'duration': duration
                    }
                else:
                    results[name] = result
                    result = result.get('healthy', True)
                
                if not result:
                    overall_healthy = False
                
                # 记录健康状态
                self.metrics_collector.record_metric(
                    f"health_check_{name}",
                    1 if result else 0
                )
                
            except Exception as e:
                logger.error(f"健康检查失败 {name}: {e}")
                results[name] = {
                    'healthy': False,
                    'error': str(e)
                }
                overall_healthy = False
                
                # 记录检查失败
                self.metrics_collector.record_metric(
                    f"health_check_{name}",
                    0
                )
        
        results['overall'] = {
            'healthy': overall_healthy,
            'timestamp': time.time()
        }
        
        return results

# 创建全局监控实例
metrics_collector = MetricsCollector()
alert_manager = AlertManager(metrics_collector)
health_checker = HealthChecker(metrics_collector)

# 配置邮件通知（如果配置了SMTP且邮件功能可用）
smtp_host = os.getenv('SMTP_HOST')
smtp_port = int(os.getenv('SMTP_PORT', 587))
smtp_username = os.getenv('SMTP_USERNAME')
smtp_password = os.getenv('SMTP_PASSWORD')

if EMAIL_AVAILABLE and all([smtp_host, smtp_username, smtp_password]):
    try:
        email_notifier = EmailNotifier(smtp_host, smtp_port, smtp_username, smtp_password)
        alert_manager.add_notification_handler(email_notifier.send_alert)
        logger.info("邮件通知已配置")
    except Exception as e:
        logger.warning(f"邮件通知配置失败: {e}")
else:
    logger.info("邮件通知未配置或不可用，跳过")

# 添加默认告警规则
default_rules = [
    AlertRule(
        name="高错误率",
        metric="error_rate",
        condition="gt",
        threshold=10.0,  # 错误率超过10%
        duration=300,    # 持续5分钟
        severity="critical"
    ),
    AlertRule(
        name="响应时间过长",
        metric="avg_response_time",
        condition="gt",
        threshold=5.0,   # 平均响应时间超过5秒
        duration=300,
        severity="warning"
    ),
    AlertRule(
        name="请求量异常",
        metric="request_rate",
        condition="lt",
        threshold=1.0,   # 请求率低于1/秒
        duration=600,    # 持续10分钟
        severity="warning"
    )
]

for rule in default_rules:
    alert_manager.add_rule(rule)
