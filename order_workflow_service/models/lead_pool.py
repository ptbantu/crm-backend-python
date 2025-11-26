"""
线索池模型
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from order_workflow_service.database import Base
import uuid


class LeadPool(Base):
    """线索池模型"""
    __tablename__ = "lead_pools"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 基本信息
    name = Column(String(255), nullable=False, comment="线索池名称")
    # 注意：organizations 表在其他服务的数据库中，不能使用外键约束，只保留索引
    organization_id = Column(String(36), nullable=False, index=True, comment="组织ID（跨服务引用，通过 API 验证）")
    description = Column(Text, nullable=True, comment="描述")
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment="是否激活")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系（注意：Organization模型可能在其他服务中）
    # organization = relationship("Organization", foreign_keys=[organization_id])
    # leads关系通过Lead模型的pool关系反向定义

