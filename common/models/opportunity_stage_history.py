"""
商机阶段历史模型
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, JSON, CheckConstraint, Integer, Computed
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
from common.database import Base
from common.models.user import User
import uuid


class OpportunityStageHistory(Base):
    """商机阶段历史模型"""
    __tablename__ = "opportunity_stage_history"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    opportunity_id = Column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True, comment="商机ID")
    stage_id = Column(String(36), ForeignKey("opportunity_stage_templates.id", ondelete="RESTRICT"), nullable=False, index=True, comment="阶段ID")
    
    # 时间信息
    entered_at = Column(DateTime, nullable=False, server_default=func.now(), index=True, comment="进入该阶段的时间")
    exited_at = Column(DateTime, nullable=True, comment="退出该阶段的时间（NULL表示当前阶段）")
    duration_days = Column(Integer, Computed(
        text("IF(exited_at IS NULL, NULL, DATEDIFF(exited_at, entered_at))")
    ), comment="该阶段持续天数")
    
    # 条件与审批
    conditions_met_json = Column(JSON, nullable=True, comment="满足的推进条件详情JSON")
    requires_approval = Column(Boolean, nullable=False, default=False, comment="该阶段是否需要审批（冗余自模板，便于查询）")
    approval_status = Column(String(50), nullable=True, default="pending", index=True, comment="审批状态：pending(待审批), approved(通过), rejected(拒绝)")
    approved_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="审批人ID")
    approval_at = Column(DateTime, nullable=True, comment="审批时间")
    approval_notes = Column(Text, nullable=True, comment="审批备注")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="记录创建时间")
    
    # 关系
    opportunity = relationship("Opportunity", foreign_keys=[opportunity_id], primaryjoin="OpportunityStageHistory.opportunity_id == Opportunity.id", back_populates="stage_histories")
    stage_template = relationship("OpportunityStageTemplate", foreign_keys=[stage_id], primaryjoin="OpportunityStageHistory.stage_id == OpportunityStageTemplate.id", back_populates="stage_histories")
    approver = relationship("User", foreign_keys=[approved_by], primaryjoin="OpportunityStageHistory.approved_by == User.id", backref="approved_stage_histories")
    
    # 约束
    __table_args__ = (
        CheckConstraint("approval_status IN ('pending', 'approved', 'rejected')", name="chk_stage_history_approval_status"),
    )
