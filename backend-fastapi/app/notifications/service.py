"""
告警通知服务
"""
import json
import smtplib
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_

from .models import (
    NotificationChannel, AlertRule, Alert, NotificationLog,
    NotificationChannelCreate, AlertRuleCreate, AlertResponse,
    NotificationChannelResponse, AlertRuleResponse, NotificationLogResponse,
    AlertQuery, AlertStatistics, AlertDashboard, NotificationTest,
    NotificationType, AlertSeverity, AlertStatus,
    EmailConfig, WebhookConfig, SlackConfig, DingTalkConfig
)
from ..database import SessionLocal


class NotificationService:
    """通知服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_channel(self, channel_data: NotificationChannelCreate, created_by: int) -> NotificationChannel:
        """创建通知渠道"""
        channel = NotificationChannel(
            name=channel_data.name,
            type=channel_data.type.value,
            config=channel_data.config,
            is_enabled=channel_data.is_enabled,
            is_default=channel_data.is_default,
            created_by=created_by
        )
        
        self.db.add(channel)
        self.db.commit()
        self.db.refresh(channel)
        
        return channel
    
    def get_channels(self) -> List[NotificationChannelResponse]:
        """获取通知渠道列表"""
        channels = self.db.query(NotificationChannel).order_by(desc(NotificationChannel.created_at)).all()
        return [NotificationChannelResponse.from_orm(channel) for channel in channels]
    
    def create_alert_rule(self, rule_data: AlertRuleCreate, created_by: int) -> AlertRule:
        """创建告警规则"""
        rule = AlertRule(
            name=rule_data.name,
            description=rule_data.description,
            metric_type=rule_data.metric_type,
            condition=rule_data.condition,
            threshold=rule_data.threshold,
            duration=rule_data.duration,
            severity=rule_data.severity.value,
            is_enabled=rule_data.is_enabled,
            notification_channels=rule_data.notification_channels,
            cooldown_period=rule_data.cooldown_period,
            tags=rule_data.tags,
            created_by=created_by
        )
        
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        
        return rule
    
    def get_alert_rules(self) -> List[AlertRuleResponse]:
        """获取告警规则列表"""
        rules = self.db.query(AlertRule).order_by(desc(AlertRule.created_at)).all()
        return [AlertRuleResponse.from_orm(rule) for rule in rules]
    
    def trigger_alert(self, rule_id: int, metric_value: float, extra_data: Dict[str, Any] = None) -> Alert:
        """触发告警"""
        rule = self.db.query(AlertRule).filter(AlertRule.id == rule_id).first()
        if not rule or not rule.is_enabled:
            return None
        
        # 检查是否在冷却期内
        if self._is_in_cooldown(rule_id):
            return None
        
        # 创建告警记录
        alert = Alert(
            rule_id=rule_id,
            rule_name=rule.name,
            title=f"{rule.name} - {rule.metric_type} {rule.condition} {rule.threshold}",
            description=rule.description,
            severity=rule.severity,
            status=AlertStatus.ACTIVE.value,
            metric_value=metric_value,
            threshold=rule.threshold,
            started_at=datetime.utcnow(),
            tags=rule.tags,
            extra_data=extra_data
        )
        
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        # 发送通知
        self._send_alert_notifications(alert, rule)
        
        return alert
    
    def resolve_alert(self, alert_id: int, resolved_by: int = None) -> Alert:
        """解决告警"""
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
        
        alert.status = AlertStatus.RESOLVED.value
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = resolved_by
        
        self.db.commit()
        
        return alert
    
    def acknowledge_alert(self, alert_id: int, acknowledged_by: int) -> Alert:
        """确认告警"""
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
        
        alert.status = AlertStatus.ACKNOWLEDGED.value
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = acknowledged_by
        
        self.db.commit()
        
        return alert
    
    def search_alerts(self, query: AlertQuery) -> List[AlertResponse]:
        """搜索告警"""
        db_query = self.db.query(Alert)
        
        if query.severity:
            db_query = db_query.filter(Alert.severity == query.severity.value)
        
        if query.status:
            db_query = db_query.filter(Alert.status == query.status.value)
        
        if query.rule_id:
            db_query = db_query.filter(Alert.rule_id == query.rule_id)
        
        if query.start_time:
            db_query = db_query.filter(Alert.started_at >= query.start_time)
        
        if query.end_time:
            db_query = db_query.filter(Alert.started_at <= query.end_time)
        
        alerts = db_query.order_by(desc(Alert.started_at)).offset(query.offset).limit(query.limit).all()
        
        return [AlertResponse.from_orm(alert) for alert in alerts]
    
    def get_alert_statistics(self, 
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> AlertStatistics:
        """获取告警统计"""
        if not start_time:
            start_time = datetime.utcnow() - timedelta(hours=24)
        if not end_time:
            end_time = datetime.utcnow()
        
        # 基础统计
        total_alerts = self.db.query(Alert).filter(
            Alert.started_at.between(start_time, end_time)
        ).count()
        
        active_alerts = self.db.query(Alert).filter(
            and_(
                Alert.started_at.between(start_time, end_time),
                Alert.status == AlertStatus.ACTIVE.value
            )
        ).count()
        
        resolved_alerts = self.db.query(Alert).filter(
            and_(
                Alert.started_at.between(start_time, end_time),
                Alert.status == AlertStatus.RESOLVED.value
            )
        ).count()
        
        # 按严重程度统计
        severity_stats = self.db.query(
            Alert.severity,
            func.count(Alert.id).label('count')
        ).filter(
            Alert.started_at.between(start_time, end_time)
        ).group_by(Alert.severity).all()
        
        severity_counts = {severity.value: 0 for severity in AlertSeverity}
        for stat in severity_stats:
            if stat.severity in severity_counts:
                severity_counts[stat.severity] = stat.count
        
        # 按状态统计
        status_stats = self.db.query(
            Alert.status,
            func.count(Alert.id).label('count')
        ).filter(
            Alert.started_at.between(start_time, end_time)
        ).group_by(Alert.status).all()
        
        status_distribution = {stat.status: stat.count for stat in status_stats}
        
        # 热门规则
        top_rules = self.db.query(
            Alert.rule_name,
            func.count(Alert.id).label('count')
        ).filter(
            Alert.started_at.between(start_time, end_time)
        ).group_by(Alert.rule_name).order_by(desc('count')).limit(5).all()
        
        # 计算告警率和平均解决时间
        time_diff_hours = (end_time - start_time).total_seconds() / 3600
        alert_rate = total_alerts / time_diff_hours if time_diff_hours > 0 else 0
        
        # 平均解决时间
        resolved_alerts_with_time = self.db.query(Alert).filter(
            and_(
                Alert.started_at.between(start_time, end_time),
                Alert.status == AlertStatus.RESOLVED.value,
                Alert.resolved_at.isnot(None)
            )
        ).all()
        
        if resolved_alerts_with_time:
            resolution_times = [
                (alert.resolved_at - alert.started_at).total_seconds()
                for alert in resolved_alerts_with_time
            ]
            resolution_time_avg = sum(resolution_times) / len(resolution_times) / 60  # 转换为分钟
        else:
            resolution_time_avg = 0
        
        return AlertStatistics(
            total_alerts=total_alerts,
            active_alerts=active_alerts,
            resolved_alerts=resolved_alerts,
            critical_alerts=severity_counts.get('critical', 0),
            high_alerts=severity_counts.get('high', 0),
            medium_alerts=severity_counts.get('medium', 0),
            low_alerts=severity_counts.get('low', 0),
            alert_rate=alert_rate,
            resolution_time_avg=resolution_time_avg,
            top_rules=[{"name": rule.rule_name, "count": rule.count} for rule in top_rules],
            severity_distribution=severity_counts,
            status_distribution=status_distribution
        )
    
    def get_dashboard_data(self) -> AlertDashboard:
        """获取告警仪表板数据"""
        statistics = self.get_alert_statistics()
        
        # 最近告警
        recent_alerts = self.db.query(Alert).order_by(desc(Alert.started_at)).limit(10).all()
        
        # 活跃规则
        active_rules = self.db.query(AlertRule).filter(AlertRule.is_enabled == True).all()
        
        # 通知渠道
        channels = self.db.query(NotificationChannel).filter(NotificationChannel.is_enabled == True).all()
        
        # 系统健康
        system_health = {
            "alert_system_status": "healthy",
            "notification_success_rate": self._calculate_notification_success_rate(),
            "average_response_time": statistics.resolution_time_avg
        }
        
        return AlertDashboard(
            statistics=statistics,
            recent_alerts=[AlertResponse.from_orm(alert) for alert in recent_alerts],
            active_rules=[AlertRuleResponse.from_orm(rule) for rule in active_rules],
            notification_channels=[NotificationChannelResponse.from_orm(channel) for channel in channels],
            system_health=system_health
        )
    
    def test_notification(self, test_data: NotificationTest) -> bool:
        """测试通知"""
        channel = self.db.query(NotificationChannel).filter(NotificationChannel.id == test_data.channel_id).first()
        if not channel:
            return False
        
        return self._send_notification(
            channel=channel,
            recipient=test_data.recipient,
            subject=test_data.subject,
            content=test_data.content,
            alert_id=0  # 测试通知
        )
    
    # 私有方法
    
    def _is_in_cooldown(self, rule_id: int) -> bool:
        """检查是否在冷却期内"""
        rule = self.db.query(AlertRule).filter(AlertRule.id == rule_id).first()
        if not rule:
            return False
        
        last_alert = self.db.query(Alert).filter(
            Alert.rule_id == rule_id
        ).order_by(desc(Alert.started_at)).first()
        
        if not last_alert:
            return False
        
        cooldown_end = last_alert.started_at + timedelta(seconds=rule.cooldown_period)
        return datetime.utcnow() < cooldown_end
    
    def _send_alert_notifications(self, alert: Alert, rule: AlertRule):
        """发送告警通知"""
        if not rule.notification_channels:
            return
        
        channels = self.db.query(NotificationChannel).filter(
            and_(
                NotificationChannel.id.in_(rule.notification_channels),
                NotificationChannel.is_enabled == True
            )
        ).all()
        
        for channel in channels:
            self._send_notification(
                channel=channel,
                recipient=self._get_default_recipient(channel),
                subject=f"[{alert.severity.upper()}] {alert.title}",
                content=self._format_alert_message(alert),
                alert_id=alert.id
            )
    
    def _send_notification(self, channel: NotificationChannel, recipient: str, 
                          subject: str, content: str, alert_id: int) -> bool:
        """发送通知"""
        try:
            if channel.type == NotificationType.EMAIL.value:
                success = self._send_email(channel.config, recipient, subject, content)
            elif channel.type == NotificationType.WEBHOOK.value:
                success = self._send_webhook(channel.config, subject, content)
            elif channel.type == NotificationType.SLACK.value:
                success = self._send_slack(channel.config, subject, content)
            elif channel.type == NotificationType.DINGTALK.value:
                success = self._send_dingtalk(channel.config, subject, content)
            else:
                success = False
            
            # 记录通知日志
            log = NotificationLog(
                alert_id=alert_id,
                channel_id=channel.id,
                channel_type=channel.type,
                recipient=recipient,
                subject=subject,
                content=content,
                status="sent" if success else "failed",
                error_message=None if success else "发送失败"
            )
            
            self.db.add(log)
            self.db.commit()
            
            return success
            
        except Exception as e:
            # 记录错误日志
            log = NotificationLog(
                alert_id=alert_id,
                channel_id=channel.id,
                channel_type=channel.type,
                recipient=recipient,
                subject=subject,
                content=content,
                status="failed",
                error_message=str(e)
            )
            
            self.db.add(log)
            self.db.commit()
            
            return False
    
    def _send_email(self, config: Dict[str, Any], recipient: str, subject: str, content: str) -> bool:
        """发送邮件"""
        try:
            email_config = EmailConfig(**config)
            
            msg = MIMEMultipart()
            msg['From'] = f"{email_config.from_name} <{email_config.from_email}>"
            msg['To'] = recipient
            msg['Subject'] = subject
            
            msg.attach(MIMEText(content, 'html' if '<' in content else 'plain', 'utf-8'))
            
            server = smtplib.SMTP(email_config.smtp_server, email_config.smtp_port)
            if email_config.use_tls:
                server.starttls()
            server.login(email_config.username, email_config.password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False
    
    def _send_webhook(self, config: Dict[str, Any], subject: str, content: str) -> bool:
        """发送Webhook"""
        try:
            webhook_config = WebhookConfig(**config)
            
            payload = {
                "subject": subject,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = requests.request(
                method=webhook_config.method,
                url=webhook_config.url,
                json=payload,
                headers=webhook_config.headers or {},
                timeout=webhook_config.timeout
            )
            
            return response.status_code < 400
        except Exception as e:
            print(f"Webhook发送失败: {e}")
            return False
    
    def _send_slack(self, config: Dict[str, Any], subject: str, content: str) -> bool:
        """发送Slack消息"""
        try:
            slack_config = SlackConfig(**config)
            
            payload = {
                "channel": slack_config.channel,
                "username": slack_config.username,
                "icon_emoji": slack_config.icon_emoji,
                "text": f"*{subject}*\n{content}"
            }
            
            response = requests.post(slack_config.webhook_url, json=payload, timeout=30)
            return response.status_code == 200
        except Exception as e:
            print(f"Slack发送失败: {e}")
            return False
    
    def _send_dingtalk(self, config: Dict[str, Any], subject: str, content: str) -> bool:
        """发送钉钉消息"""
        try:
            dingtalk_config = DingTalkConfig(**config)
            
            payload = {
                "msgtype": "text",
                "text": {
                    "content": f"{subject}\n{content}"
                }
            }
            
            if dingtalk_config.at_mobiles:
                payload["at"] = {
                    "atMobiles": dingtalk_config.at_mobiles,
                    "isAtAll": dingtalk_config.at_all
                }
            
            response = requests.post(dingtalk_config.webhook_url, json=payload, timeout=30)
            return response.status_code == 200
        except Exception as e:
            print(f"钉钉发送失败: {e}")
            return False
    
    def _get_default_recipient(self, channel: NotificationChannel) -> str:
        """获取默认收件人"""
        config = channel.config
        
        if channel.type == NotificationType.EMAIL.value:
            return config.get('default_recipient', 'admin@example.com')
        elif channel.type == NotificationType.SLACK.value:
            return config.get('channel', '#alerts')
        else:
            return 'default'
    
    def _format_alert_message(self, alert: Alert) -> str:
        """格式化告警消息"""
        return f"""
告警详情:
- 规则: {alert.rule_name}
- 严重程度: {alert.severity}
- 当前值: {alert.metric_value}
- 阈值: {alert.threshold}
- 开始时间: {alert.started_at.strftime('%Y-%m-%d %H:%M:%S')}
- 描述: {alert.description or '无'}

请及时处理此告警。
        """.strip()
    
    def _calculate_notification_success_rate(self) -> float:
        """计算通知成功率"""
        total_notifications = self.db.query(NotificationLog).filter(
            NotificationLog.sent_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        if total_notifications == 0:
            return 100.0
        
        successful_notifications = self.db.query(NotificationLog).filter(
            and_(
                NotificationLog.sent_at >= datetime.utcnow() - timedelta(hours=24),
                NotificationLog.status == 'sent'
            )
        ).count()
        
        return (successful_notifications / total_notifications) * 100


class AlertManager:
    """告警管理器"""
    
    @staticmethod
    def check_system_metrics():
        """检查系统指标"""
        try:
            import psutil
            
            db = SessionLocal()
            notification_service = NotificationService(db)
            
            # 检查CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            AlertManager._check_metric("cpu_usage", cpu_percent, notification_service)
            
            # 检查内存使用率
            memory_percent = psutil.virtual_memory().percent
            AlertManager._check_metric("memory_usage", memory_percent, notification_service)
            
            # 检查磁盘使用率
            disk_percent = psutil.disk_usage('/').percent
            AlertManager._check_metric("disk_usage", disk_percent, notification_service)
            
            db.close()
            
        except Exception as e:
            print(f"系统指标检查失败: {e}")
    
    @staticmethod
    def _check_metric(metric_type: str, value: float, notification_service: NotificationService):
        """检查指标"""
        rules = notification_service.db.query(AlertRule).filter(
            and_(
                AlertRule.metric_type == metric_type,
                AlertRule.is_enabled == True
            )
        ).all()
        
        for rule in rules:
            should_trigger = False
            
            if rule.condition == ">":
                should_trigger = value > rule.threshold
            elif rule.condition == ">=":
                should_trigger = value >= rule.threshold
            elif rule.condition == "<":
                should_trigger = value < rule.threshold
            elif rule.condition == "<=":
                should_trigger = value <= rule.threshold
            elif rule.condition == "==":
                should_trigger = abs(value - rule.threshold) < 0.01
            
            if should_trigger:
                notification_service.trigger_alert(
                    rule_id=rule.id,
                    metric_value=value,
                    extra_data={"metric_type": metric_type, "check_time": datetime.utcnow().isoformat()}
                )
