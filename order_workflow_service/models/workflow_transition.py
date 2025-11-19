"""
工作流流转记录模型
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from order_workflow_service.database import Base
import uuid


class WorkflowTransition(Base):
    """工作流流转记录模型"""
    __tablename__ = "workflow_transitions"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 工作流实例关联
    workflow_instance_id = Column(String(36), ForeignKey("workflow_instances.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 流转信息
    from_stage = Column(String(100), nullable=True, comment="源阶段")
    to_stage = Column(String(100), nullable=True, comment="目标阶段")
    transition_condition = Column(Text, nullable=True, comment="流转条件")
    
    # 触发信息
    triggered_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    triggered_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    notes = Column(Text, nullable=True, comment="备注")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now())

