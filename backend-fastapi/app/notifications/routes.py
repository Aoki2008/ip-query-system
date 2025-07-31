"""
告警通知路由
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session

from .models import (
    NotificationChannelCreate, NotificationChannelResponse,
    AlertRuleCreate, AlertRuleResponse, AlertResponse,
    NotificationLogResponse, AlertQuery, AlertStatistics,
    AlertDashboard, NotificationTest, AlertSeverity, AlertStatus
)
from .service import NotificationService, AlertManager
from ..admin.models import AdminUser
from ..admin.auth.dependencies import get_current_active_user, require_super_admin
from ..database import get_db

router = APIRouter(prefix="/api/admin/notifications", tags=["告警通知"])


@router.get("/dashboard", response_model=AlertDashboard)
async def get_alert_dashboard(
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取告警仪表板"""
    notification_service = NotificationService(db)
    return notification_service.get_dashboard_data()


@router.get("/channels", response_model=List[NotificationChannelResponse])
async def get_notification_channels(
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取通知渠道列表"""
    notification_service = NotificationService(db)
    return notification_service.get_channels()


@router.post("/channels", response_model=NotificationChannelResponse)
async def create_notification_channel(
    channel_data: NotificationChannelCreate,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """创建通知渠道"""
    notification_service = NotificationService(db)
    channel = notification_service.create_channel(channel_data, current_user.id)
    return NotificationChannelResponse.from_orm(channel)


@router.get("/rules", response_model=List[AlertRuleResponse])
async def get_alert_rules(
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取告警规则列表"""
    notification_service = NotificationService(db)
    return notification_service.get_alert_rules()


@router.post("/rules", response_model=AlertRuleResponse)
async def create_alert_rule(
    rule_data: AlertRuleCreate,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """创建告警规则"""
    notification_service = NotificationService(db)
    rule = notification_service.create_alert_rule(rule_data, current_user.id)
    return AlertRuleResponse.from_orm(rule)


@router.post("/alerts/search", response_model=List[AlertResponse])
async def search_alerts(
    query: AlertQuery,
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """搜索告警"""
    notification_service = NotificationService(db)
    return notification_service.search_alerts(query)


@router.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    severity: Optional[AlertSeverity] = Query(None, description="告警严重程度"),
    status: Optional[AlertStatus] = Query(None, description="告警状态"),
    hours: int = Query(24, ge=1, le=168, description="时间范围(小时)"),
    limit: int = Query(50, ge=1, le=200, description="返回数量"),
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取告警列表"""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    query = AlertQuery(
        severity=severity,
        status=status,
        start_time=start_time,
        limit=limit,
        offset=0
    )
    
    notification_service = NotificationService(db)
    return notification_service.search_alerts(query)


@router.get("/statistics", response_model=AlertStatistics)
async def get_alert_statistics(
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取告警统计"""
    notification_service = NotificationService(db)
    return notification_service.get_alert_statistics(start_time, end_time)


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """解决告警"""
    notification_service = NotificationService(db)
    alert = notification_service.resolve_alert(alert_id, current_user.id)
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="告警不存在"
        )
    
    return {"message": "告警已解决", "alert_id": alert_id}


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """确认告警"""
    notification_service = NotificationService(db)
    alert = notification_service.acknowledge_alert(alert_id, current_user.id)
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="告警不存在"
        )
    
    return {"message": "告警已确认", "alert_id": alert_id}


@router.post("/test")
async def test_notification(
    test_data: NotificationTest,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """测试通知"""
    notification_service = NotificationService(db)
    success = notification_service.test_notification(test_data)
    
    return {
        "success": success,
        "message": "测试通知发送成功" if success else "测试通知发送失败"
    }


@router.post("/trigger")
async def trigger_test_alert(
    rule_id: int,
    metric_value: float,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """触发测试告警"""
    notification_service = NotificationService(db)
    alert = notification_service.trigger_alert(
        rule_id=rule_id,
        metric_value=metric_value,
        extra_data={"test": True, "triggered_by": current_user.id}
    )
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法触发告警，请检查规则配置"
        )
    
    return {
        "message": "测试告警已触发",
        "alert_id": alert.id
    }


@router.post("/check-metrics")
async def check_system_metrics(
    background_tasks: BackgroundTasks,
    current_user: AdminUser = Depends(require_super_admin)
):
    """检查系统指标"""
    background_tasks.add_task(AlertManager.check_system_metrics)
    
    return {"message": "系统指标检查任务已启动"}


@router.get("/logs", response_model=List[NotificationLogResponse])
async def get_notification_logs(
    alert_id: Optional[int] = Query(None, description="告警ID"),
    channel_id: Optional[int] = Query(None, description="渠道ID"),
    hours: int = Query(24, ge=1, le=168, description="时间范围(小时)"),
    limit: int = Query(100, ge=1, le=500, description="返回数量"),
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取通知日志"""
    from .models import NotificationLog
    from sqlalchemy import and_, desc
    
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    query = db.query(NotificationLog).filter(
        NotificationLog.sent_at >= start_time
    )
    
    if alert_id:
        query = query.filter(NotificationLog.alert_id == alert_id)
    
    if channel_id:
        query = query.filter(NotificationLog.channel_id == channel_id)
    
    logs = query.order_by(desc(NotificationLog.sent_at)).limit(limit).all()
    
    return [NotificationLogResponse.from_orm(log) for log in logs]


@router.get("/health")
async def notification_system_health(
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """通知系统健康检查"""
    from .models import NotificationChannel, AlertRule, Alert
    
    try:
        # 检查通知渠道
        total_channels = db.query(NotificationChannel).count()
        enabled_channels = db.query(NotificationChannel).filter(
            NotificationChannel.is_enabled == True
        ).count()
        
        # 检查告警规则
        total_rules = db.query(AlertRule).count()
        enabled_rules = db.query(AlertRule).filter(
            AlertRule.is_enabled == True
        ).count()
        
        # 检查活跃告警
        active_alerts = db.query(Alert).filter(
            Alert.status == AlertStatus.ACTIVE.value
        ).count()
        
        # 检查最近通知成功率
        notification_service = NotificationService(db)
        success_rate = notification_service._calculate_notification_success_rate()
        
        return {
            "status": "healthy",
            "total_channels": total_channels,
            "enabled_channels": enabled_channels,
            "total_rules": total_rules,
            "enabled_rules": enabled_rules,
            "active_alerts": active_alerts,
            "notification_success_rate": success_rate,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"通知系统健康检查失败: {str(e)}"
        )


@router.post("/channels/{channel_id}/enable")
async def enable_notification_channel(
    channel_id: int,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """启用通知渠道"""
    from .models import NotificationChannel
    
    channel = db.query(NotificationChannel).filter(NotificationChannel.id == channel_id).first()
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知渠道不存在"
        )
    
    channel.is_enabled = True
    channel.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "通知渠道已启用", "channel_id": channel_id}


@router.post("/channels/{channel_id}/disable")
async def disable_notification_channel(
    channel_id: int,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """禁用通知渠道"""
    from .models import NotificationChannel
    
    channel = db.query(NotificationChannel).filter(NotificationChannel.id == channel_id).first()
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知渠道不存在"
        )
    
    channel.is_enabled = False
    channel.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "通知渠道已禁用", "channel_id": channel_id}


@router.post("/rules/{rule_id}/enable")
async def enable_alert_rule(
    rule_id: int,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """启用告警规则"""
    from .models import AlertRule
    
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="告警规则不存在"
        )
    
    rule.is_enabled = True
    rule.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "告警规则已启用", "rule_id": rule_id}


@router.post("/rules/{rule_id}/disable")
async def disable_alert_rule(
    rule_id: int,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """禁用告警规则"""
    from .models import AlertRule
    
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="告警规则不存在"
        )
    
    rule.is_enabled = False
    rule.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "告警规则已禁用", "rule_id": rule_id}
