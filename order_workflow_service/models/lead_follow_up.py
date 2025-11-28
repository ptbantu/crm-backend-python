"""
线索跟进记录模型
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base  # 使用 common.database.Base 确保与共享模型使用同一个 Base
from common.models import User
import uuid


class LeadFollowUp(Base):
    """线索跟进记录模型"""
    __tablename__ = "lead_follow_ups"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    lead_id = Column(String(36), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True, comment="线索ID")
    
    # 跟进信息
    follow_up_type = Column(String(50), nullable=False, index=True, comment="跟进类型：call(电话), meeting(会议), email(邮件), note(备注)")
    content = Column(Text, nullable=True, comment="跟进内容")
    follow_up_date = Column(DateTime, nullable=False, index=True, comment="跟进日期")
    
    # 状态关联字段
    status_before = Column(String(50), nullable=True, index=True, comment="跟进前线索状态")
    status_after = Column(String(50), nullable=True, index=True, comment="跟进后线索状态")
    
    # 审计字段
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="创建人ID")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True, comment="创建时间")
    
    # 关系（明确指定 primaryjoin 确保 SQLAlchemy 能正确识别外键关系）
    lead = relationship("Lead", back_populates="follow_ups")
    creator = relationship(
        User,
        foreign_keys=[created_by],
        primaryjoin="LeadFollowUp.created_by == User.id",
        backref="created_lead_follow_ups"
    )
    
    # 检查约束
    __table_args__ = (
        CheckConstraint(
            "follow_up_type IN ('call', 'meeting', 'email', 'note')",
            name="chk_lead_follow_ups_type"
        ),
        CheckConstraint(
            "status_before IN ('new', 'contacted', 'qualified', 'converted', 'lost') OR status_before IS NULL",
            name="chk_lead_follow_ups_status_before"
        ),
        CheckConstraint(
            "status_after IN ('new', 'contacted', 'qualified', 'converted', 'lost') OR status_after IS NULL",
            name="chk_lead_follow_ups_status_after"
        ),
    )

