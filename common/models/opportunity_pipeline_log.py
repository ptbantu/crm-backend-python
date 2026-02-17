"""
商机流水线日志模型
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
import enum


class StageStatus(str, enum.Enum):
    """阶段状态枚举"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    REJECTED = "REJECTED"


class OpportunityPipelineLog(Base):
    """商机流水线执行日志表"""
    __tablename__ = "opportunity_pipeline_logs"

    id = Column(String(36), primary_key=True, comment="日志ID")
    opportunity_id = Column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True, comment="商机ID")
    pipeline_id = Column(String(36), ForeignKey("sys_pipeline_configs.id", ondelete="RESTRICT"), nullable=False, index=True, comment="流水线ID")
    stage_id = Column(String(36), ForeignKey("sys_pipeline_stages.id", ondelete="RESTRICT"), nullable=False, index=True, comment="阶段ID")
    stage_name = Column(String(100), nullable=False, comment="阶段名称（冗余）")
    stage_type = Column(String(50), nullable=False, comment="阶段类型")
    status = Column(SQLEnum(StageStatus), nullable=False, default=StageStatus.PENDING, comment="状态")
    parallel_group = Column(String(50), nullable=True, index=True, comment="并行组标识（冗余）")

    # 时间字段
    entered_at = Column(DateTime, nullable=False, server_default=func.now(), comment="进入阶段时间")
    started_at = Column(DateTime, nullable=True, comment="开始处理时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    duration_minutes = Column(Integer, nullable=True, comment="耗时（分钟）")

    # 审批字段
    assigned_to = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="分配给")
    approver_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="审批人ID")
    approved_at = Column(DateTime, nullable=True, comment="审批时间")
    approval_notes = Column(Text, nullable=True, comment="审批意见")

    # 元数据
    notes = Column(Text, nullable=True, comment="备注")
    extra_data = Column(JSON, nullable=True, comment="扩展数据（JSON格式）")

    # 审计字段
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="创建人ID")
    updated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="更新人ID")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    opportunity = relationship("Opportunity", backref="pipeline_logs")

    __table_args__ = (
        {'extend_existing': True},
    )
