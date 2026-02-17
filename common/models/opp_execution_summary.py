"""
商机流转执行快照模型
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, DECIMAL, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base


class OppExecutionSummary(Base):
    """商机流转执行快照表（实时对齐）"""
    __tablename__ = "crm_opp_execution_summary"

    opportunity_id = Column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), primary_key=True, comment="商机ID")
    current_stage_id = Column(String(36), ForeignKey("sys_pipeline_stages.id", ondelete="SET NULL"), nullable=True, index=True, comment="当前阶段ID（外键 → sys_pipeline_stages.id）")
    current_stage_code = Column(String(50), nullable=True, comment="阶段编码，如 ST_OPP_05")
    current_stage_name = Column(String(100), nullable=True, comment="阶段名称")
    total_progress = Column(DECIMAL(5, 2), nullable=False, default=0.00, comment="整体进度 0-100%")
    pending_required_count = Column(Integer, nullable=False, default=0, comment="当前阶段剩余未完成必需 Action 数")
    total_required_count = Column(Integer, nullable=False, default=0, comment="当前阶段必需 Action 总数")
    health_status = Column(SQLEnum("GREEN", "YELLOW", "RED", name="health_status_enum"), nullable=False, default="GREEN", comment="健康状态")
    last_action_at = Column(DateTime, nullable=True, comment="最后一次 Action 操作时间")
    last_action_desc = Column(String(255), nullable=True, comment="最后一次操作摘要")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    opportunity = relationship("Opportunity", backref="execution_summary")
    current_stage = relationship("PipelineStage")

    __table_args__ = (
        {'extend_existing': True},
    )
