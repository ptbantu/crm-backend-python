"""
工作流实例模型
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, CheckConstraint
from sqlalchemy.sql import func
from order_workflow_service.database import Base
import uuid


class WorkflowInstance(Base):
    """工作流实例模型"""
    __tablename__ = "workflow_instances"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 工作流定义关联
    workflow_definition_id = Column(String(36), ForeignKey("workflow_definitions.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # 业务对象关联
    business_type = Column(String(50), nullable=True, index=True, comment="业务类型：order, service_record")
    business_id = Column(String(36), nullable=True, index=True, comment="业务对象ID（订单ID或服务记录ID）")
    
    # 当前状态
    current_stage = Column(String(100), nullable=True, comment="当前阶段")
    status = Column(String(50), nullable=False, default="running", index=True, comment="实例状态：running, completed, cancelled, suspended")
    
    # 启动信息
    started_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # 流程变量
    variables = Column(JSON, nullable=True, comment="流程变量（JSON 格式）")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 检查约束
    __table_args__ = (
        CheckConstraint(
            "status IN ('running', 'completed', 'cancelled', 'suspended')",
            name="chk_workflow_instances_status"
        ),
    )

