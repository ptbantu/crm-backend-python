"""
流水线动作配置模型
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
import enum


class ActionType(str, enum.Enum):
    """动作类型枚举"""
    FORM = "FORM"
    FILE = "FILE"
    APPROVAL = "APPROVAL"
    SUB_PIPELINE = "SUB_PIPELINE"
    API_CALL = "API_CALL"


class PipelineActionConfig(Base):
    """流水线阶段原子动作配置表"""
    __tablename__ = "sys_pipeline_action_configs"

    id = Column(String(36), primary_key=True, comment="动作配置ID")
    stage_id = Column(String(36), ForeignKey("sys_pipeline_stages.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联阶段ID")
    action_code = Column(String(50), nullable=False, comment="动作编码")
    name = Column(String(100), nullable=False, comment="动作名称")
    action_type = Column(SQLEnum(ActionType), nullable=False, comment="动作类型")
    is_required = Column(Boolean, nullable=False, default=True, comment="是否必需")
    trigger_condition = Column(String(50), nullable=False, default="DEFAULT", comment="触发条件标签: DEFAULT/VISA/REG/SITE")
    order = Column(Integer, nullable=False, default=1, comment="执行顺序")
    description = Column(Text, nullable=True, comment="动作描述")

    # 配置字段
    validation_rules = Column(JSON, nullable=True, comment="验证规则")
    trigger_config = Column(JSON, nullable=True, comment="触发配置")
    form_schema = Column(JSON, nullable=True, comment="表单结构定义")

    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    stage = relationship("PipelineStage", backref="actions")

    __table_args__ = (
        {'extend_existing': True},
    )
