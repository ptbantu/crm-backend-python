"""
通知模型
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models import User
import uuid


class Notification(Base):
    """通知模型"""
    __tablename__ = "notifications"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 用户关联
    user_id = Column(String(36), nullable=False, index=True, comment="用户ID（跨服务引用）")
    
    # 通知信息
    notification_type = Column(String(50), nullable=False, index=True, comment="通知类型：collection_task(催款任务), lead_assigned(线索分配), order_updated(订单更新)")
    title = Column(String(255), nullable=False, comment="通知标题")
    content = Column(Text, nullable=True, comment="通知内容")
    
    # 资源关联
    resource_type = Column(String(50), nullable=True, index=True, comment="资源类型")
    resource_id = Column(String(36), nullable=True, index=True, comment="资源ID")
    
    # 阅读状态
    is_read = Column(Boolean, default=False, nullable=False, index=True, comment="是否已读")
    read_at = Column(DateTime, nullable=True, comment="阅读时间")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True, comment="创建时间")
    
    # 关系（users 表现在在本地定义，可以使用 relationship）
    user = relationship(User, foreign_keys=[user_id], backref="notifications")
    
    # 检查约束
    __table_args__ = (
        CheckConstraint(
            "notification_type IN ('collection_task', 'lead_assigned', 'order_updated', 'lead_created', 'lead_updated')",
            name="chk_notifications_type"
        ),
    )

