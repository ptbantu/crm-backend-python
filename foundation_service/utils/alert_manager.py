"""
预警管理器
"""
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
from foundation_service.config import settings
from common.utils.logger import get_logger
# 暂时注释邮件通知功能，等待配置完成
# from common.email_client import send_email

logger = get_logger(__name__)


class AlertLevel(str, Enum):
    """预警级别"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertStatus(str, Enum):
    """预警状态"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class Alert:
    """预警对象"""
    
    def __init__(
        self,
        level: AlertLevel,
        title: str,
        message: str,
        alert_id: Optional[str] = None
    ):
        self.id = alert_id or f"alert-{datetime.now().timestamp()}"
        self.level = level
        self.title = title
        self.message = message
        self.status = AlertStatus.ACTIVE
        self.created_at = datetime.now()
        self.acknowledged_at: Optional[datetime] = None
        self.resolved_at: Optional[datetime] = None
    
    def acknowledge(self):
        """确认预警"""
        if self.status == AlertStatus.ACTIVE:
            self.status = AlertStatus.ACKNOWLEDGED
            self.acknowledged_at = datetime.now()
    
    def resolve(self):
        """解决预警"""
        self.status = AlertStatus.RESOLVED
        self.resolved_at = datetime.now()


class AlertManager:
    """预警管理器"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
    
    def check_thresholds(self, metrics: Dict) -> List[Alert]:
        """
        检查指标阈值并生成预警
        
        Args:
            metrics: 指标字典（包含 cpu_usage_percent, memory_usage_percent 等）
        
        Returns:
            预警列表
        """
        alerts = []
        
        # 检查 CPU 使用率
        cpu_usage = metrics.get("cpu_usage_percent", 0)
        if cpu_usage >= settings.CPU_THRESHOLD_CRITICAL:
            alert = self.create_alert(
                AlertLevel.CRITICAL,
                "CPU 使用率过高",
                f"CPU 使用率达到 {cpu_usage}%，超过严重阈值 {settings.CPU_THRESHOLD_CRITICAL}%"
            )
            alerts.append(alert)
        elif cpu_usage >= settings.CPU_THRESHOLD_WARNING:
            alert = self.create_alert(
                AlertLevel.WARNING,
                "CPU 使用率较高",
                f"CPU 使用率达到 {cpu_usage}%，超过警告阈值 {settings.CPU_THRESHOLD_WARNING}%"
            )
            alerts.append(alert)
        
        # 检查内存使用率
        memory_usage = metrics.get("memory_usage_percent", 0)
        if memory_usage >= settings.MEMORY_THRESHOLD_CRITICAL:
            alert = self.create_alert(
                AlertLevel.CRITICAL,
                "内存使用率过高",
                f"内存使用率达到 {memory_usage}%，超过严重阈值 {settings.MEMORY_THRESHOLD_CRITICAL}%"
            )
            alerts.append(alert)
        elif memory_usage >= settings.MEMORY_THRESHOLD_WARNING:
            alert = self.create_alert(
                AlertLevel.WARNING,
                "内存使用率较高",
                f"内存使用率达到 {memory_usage}%，超过警告阈值 {settings.MEMORY_THRESHOLD_WARNING}%"
            )
            alerts.append(alert)
        
        return alerts
    
    def create_alert(
        self,
        level: AlertLevel,
        title: str,
        message: str
    ) -> Alert:
        """
        创建预警
        
        Args:
            level: 预警级别
            title: 预警标题
            message: 预警消息
        
        Returns:
            预警对象
        """
        alert = Alert(level, title, message)
        self.alerts[alert.id] = alert
        
        # 记录日志
        logger.warning(f"预警创建: {level.value} - {title}: {message}")
        
        # 发送通知
        self.send_notifications(alert)
        
        return alert
    
    def send_notifications(self, alert: Alert):
        """
        发送预警通知
        
        Args:
            alert: 预警对象
        """
        # 邮件通知（暂时注释，等待配置完成）
        # if settings.ALERT_EMAIL_ENABLED and settings.ALERT_EMAIL_RECIPIENTS:
        #     try:
        #         recipients = [
        #             email.strip()
        #             for email in settings.ALERT_EMAIL_RECIPIENTS.split(",")
        #             if email.strip()
        #         ]
        #         if recipients:
        #             subject = f"[{alert.level.value}] {alert.title}"
        #             body = f"""
        # 预警级别: {alert.level.value}
        # 标题: {alert.title}
        # 消息: {alert.message}
        # 时间: {alert.created_at.isoformat()}
        #                     """
        #             # 异步发送邮件（这里简化处理，实际应该异步执行）
        #             logger.info(f"发送预警邮件到: {recipients}")
        #             # 注意：send_email 是异步函数，需要在实际使用时 await
        #             # 这里只记录日志，实际发送应该在异步上下文中执行
        #     except Exception as e:
        #         logger.error(f"发送预警邮件失败: {str(e)}", exc_info=True)
        
        # 暂时只记录日志，不发送实际通知
        logger.info(f"预警通知（邮件/微信功能暂未启用）: {alert.level.value} - {alert.title}: {alert.message}")
    
    def get_active_alerts(self) -> List[Alert]:
        """
        获取活跃预警列表
        
        Returns:
            活跃预警列表
        """
        return [
            alert for alert in self.alerts.values()
            if alert.status == AlertStatus.ACTIVE
        ]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        确认预警
        
        Args:
            alert_id: 预警ID
        
        Returns:
            是否成功
        """
        alert = self.alerts.get(alert_id)
        if alert:
            alert.acknowledge()
            logger.info(f"预警已确认: {alert_id}")
            return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """
        解决预警
        
        Args:
            alert_id: 预警ID
        
        Returns:
            是否成功
        """
        alert = self.alerts.get(alert_id)
        if alert:
            alert.resolve()
            logger.info(f"预警已解决: {alert_id}")
            return True
        return False
    
    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """
        获取预警
        
        Args:
            alert_id: 预警ID
        
        Returns:
            预警对象或 None
        """
        return self.alerts.get(alert_id)


# 全局预警管理器实例
alert_manager = AlertManager()

