"""
商机动作执行日志模型
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
import enum


class ActionStatus(str, enum.Enum):
    """动作执行状态枚举"""
    TODO = "TODO"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"


class OpportunityActionLog(Base):
    """商机流水线动作执行日志表"""
    __tablename__ = "opportunity_action_logs"

    id = Column(String(36), primary_key=True, comment="日志ID")
    opportunity_id = Column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True, comment="商机ID")
    pipeline_log_id = Column(String(36), ForeignKey("opportunity_pipeline_logs.id", ondelete="CASCADE"), nullable=False, index=True, comment="流水线日志ID")
    action_config_id = Column(String(36), ForeignKey("sys_pipeline_action_configs.id", ondelete="RESTRICT"), nullable=False, index=True, comment="动作配置ID")
    action_code = Column(String(50), nullable=False, comment="动作编码")
    action_name = Column(String(100), nullable=False, comment="动作名称")
    action_type = Column(String(50), nullable=False, comment="动作类型")

    # 执行状态
    status = Column(SQLEnum(ActionStatus), nullable=False, default=ActionStatus.TODO, comment="执行状态")
    operator_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="操作人ID")
    started_at = Column(DateTime, nullable=True, comment="开始时间")
    finished_at = Column(DateTime, nullable=True, comment="完成时间")
    duration_minutes = Column(Integer, nullable=True, comment="耗时（分钟）")

    # 数据捕获
    captured_data = Column(JSON, nullable=True, comment="捕获的数据")
    error_message = Column(Text, nullable=True, comment="错误信息")
    notes = Column(Text, nullable=True, comment="备注")

    # 审计字段
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="创建人ID")
    updated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="更新人ID")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    opportunity = relationship("Opportunity", backref="action_logs")
    pipeline_log = relationship("OpportunityPipelineLog", backref="action_logs")
    action_config = relationship("PipelineActionConfig", backref="execution_logs")

    __table_args__ = (
        {'extend_existing': True},
    )
