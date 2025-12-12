"""
客户跟进记录模型
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models import User
import uuid


class CustomerFollowUp(Base):
    """客户跟进记录模型"""
    __tablename__ = "customer_follow_ups"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True, comment="客户ID")
    
    # 跟进信息
    follow_up_type = Column(String(50), nullable=False, index=True, comment="跟进类型：call(电话), meeting(会议), email(邮件), note(备注), visit(拜访), wechat(微信), whatsapp(WhatsApp)")
    content = Column(Text, nullable=True, comment="跟进内容")
    follow_up_date = Column(DateTime, nullable=False, index=True, comment="跟进日期")
    status_before = Column(String(50), nullable=True, index=True, comment="跟进前状态（可选）")
    status_after = Column(String(50), nullable=True, index=True, comment="跟进后状态（可选）")
    
    # 审计字段
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="创建人ID")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True, comment="创建时间")
    
    # 关系
    customer = relationship("Customer", back_populates="follow_ups")
    creator = relationship(User, foreign_keys=[created_by], primaryjoin="CustomerFollowUp.created_by == User.id", backref="created_customer_follow_ups")
    
    # 检查约束
    __table_args__ = (
        CheckConstraint(
            "follow_up_type IN ('call', 'meeting', 'email', 'note', 'visit', 'wechat', 'whatsapp')",
            name="chk_customer_follow_ups_type"
        ),
    )

