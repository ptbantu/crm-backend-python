"""
工作流定义模型
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, JSON, CheckConstraint
from sqlalchemy.sql import func
from order_workflow_service.database import Base
import uuid


class WorkflowDefinition(Base):
    """工作流定义模型"""
    __tablename__ = "workflow_definitions"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 基本信息（双语）
    name_zh = Column(String(255), nullable=False, comment="工作流名称（中文）")
    name_id = Column(String(255), nullable=False, comment="工作流名称（印尼语）")
    code = Column(String(100), nullable=False, unique=True, index=True, comment="工作流代码（唯一）")
    description_zh = Column(Text, nullable=True, comment="描述（中文）")
    description_id = Column(Text, nullable=True, comment="描述（印尼语）")
    
    # 工作流类型
    workflow_type = Column(String(50), nullable=True, index=True, comment="工作流类型：order_approval, delivery_review, payment_approval")
    
    # 工作流定义（JSON 格式）
    definition_json = Column(JSON, nullable=True, comment="工作流定义（JSON 格式，包含阶段和流转规则）")
    
    # 版本管理
    version = Column(Integer, nullable=False, default=1, comment="版本号")
    is_active = Column(Boolean, nullable=False, default=True, index=True, comment="是否激活")
    
    # 审计字段
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

