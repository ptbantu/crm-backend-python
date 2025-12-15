"""
催款任务模型
"""
from sqlalchemy import Column, String, Text, Integer, Date, DateTime, ForeignKey, Boolean, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models import User
import uuid


class CollectionTask(Base):
    """催款任务模型"""
    __tablename__ = "collection_tasks"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    order_id = Column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True, comment="订单ID")
    payment_stage_id = Column(String(36), nullable=True, index=True, comment="付款阶段ID（跨服务引用）")
    
    # 任务信息
    task_type = Column(String(50), nullable=False, comment="任务类型：auto(自动), manual(手动)")
    status = Column(String(50), default="pending", nullable=False, index=True, comment="状态：pending(待处理), in_progress(进行中), completed(已完成), cancelled(已取消)")
    
    # 时间信息
    due_date = Column(Date, nullable=True, index=True, comment="到期日期")
    reminder_count = Column(Integer, default=0, nullable=False, comment="提醒次数")
    
    # 备注
    notes = Column(Text, nullable=True, comment="备注")
    
    # 分配信息
    assigned_to_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="分配给的用户ID（销售负责人）")
    
    # 审计字段
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="创建人ID")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    order = relationship("Order", foreign_keys=[order_id], primaryjoin="CollectionTask.order_id == Order.id")
    assigned_to = relationship("User", foreign_keys=[assigned_to_user_id], primaryjoin="CollectionTask.assigned_to_user_id == User.id", backref="assigned_collection_tasks")
    creator = relationship("User", foreign_keys=[created_by], primaryjoin="CollectionTask.created_by == User.id", backref="created_collection_tasks")
    
    # 检查约束
    __table_args__ = (
        CheckConstraint(
            "task_type IN ('auto', 'manual')",
            name="chk_collection_tasks_type"
        ),
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed', 'cancelled')",
            name="chk_collection_tasks_status"
        ),
        CheckConstraint(
            "reminder_count >= 0",
            name="chk_collection_tasks_reminder_count"
        ),
    )

