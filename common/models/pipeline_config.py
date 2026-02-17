"""
流水线配置模型
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
import enum


class PipelineConfig(Base):
    """流水线配置表"""
    __tablename__ = "sys_pipeline_configs"

    id = Column(String(36), primary_key=True, comment="流水线ID")
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True, comment="组织ID")
    name = Column(String(100), nullable=False, comment="流水线名称")
    biz_type = Column(String(50), nullable=False, index=True, comment="业务类型（OPPORTUNITY/ORDER/LEAD等）")
    description = Column(Text, nullable=True, comment="描述")
    is_active = Column(Boolean, nullable=False, default=True, comment="是否启用")
    version = Column(Integer, nullable=False, default=1, comment="版本号")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    stages = relationship("PipelineStage", back_populates="pipeline", cascade="all, delete-orphan")

    __table_args__ = (
        {'extend_existing': True},
    )


class StageType(str, enum.Enum):
    """阶段类型枚举"""
    TASK = "TASK"
    APPROVAL = "APPROVAL"
    DECISION = "DECISION"
    NOTIFICATION = "NOTIFICATION"


class PipelineStage(Base):
    """流水线阶段表"""
    __tablename__ = "sys_pipeline_stages"

    id = Column(String(36), primary_key=True, comment="阶段ID")
    pipeline_id = Column(String(36), ForeignKey("sys_pipeline_configs.id", ondelete="CASCADE"), nullable=False, index=True, comment="流水线ID")
    name = Column(String(100), nullable=False, comment="阶段名称")
    description = Column(Text, nullable=True, comment="描述")
    stage_type = Column(SQLEnum(StageType), nullable=False, comment="阶段类型")
    parent_id = Column(String(36), ForeignKey("sys_pipeline_stages.id", ondelete="SET NULL"), nullable=True, index=True, comment="父阶段ID")
    parallel_group = Column(String(50), nullable=True, index=True, comment="并行组标识")
    order = Column(Integer, nullable=False, index=True, comment="排序")
    approver_role = Column(String(50), nullable=True, comment="审批角色")
    time_limit_hours = Column(Integer, nullable=True, comment="时限（小时）")
    auto_proceed = Column(Boolean, nullable=False, default=False, comment="是否自动推进")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    pipeline = relationship("PipelineConfig", back_populates="stages")
    parent_stage = relationship("PipelineStage", foreign_keys=[parent_id], remote_side=[id], backref="child_stages")

    __table_args__ = (
        {'extend_existing': True},
    )
