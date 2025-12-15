"""
线索备注模型
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models import User
import uuid


class LeadNote(Base):
    """线索备注模型"""
    __tablename__ = "lead_notes"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    lead_id = Column(String(36), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True, comment="线索ID")
    
    # 备注信息
    note_type = Column(String(50), nullable=False, index=True, comment="备注类型：comment(评论), reminder(提醒), task(任务)")
    content = Column(Text, nullable=False, comment="备注内容")
    is_important = Column(Boolean, default=False, nullable=False, index=True, comment="是否重要")
    
    # 审计字段
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="创建人ID")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True, comment="创建时间")
    
    # 关系
    lead = relationship("Lead", back_populates="notes")
    # users 表现在在本地定义，可以使用 relationship
    creator = relationship(User, foreign_keys=[created_by], primaryjoin="LeadNote.created_by == User.id", backref="created_lead_notes")
    
    # 检查约束
    __table_args__ = (
        CheckConstraint(
            "note_type IN ('comment', 'reminder', 'task')",
            name="chk_lead_notes_type"
        ),
    )

