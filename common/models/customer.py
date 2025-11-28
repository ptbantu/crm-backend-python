"""
客户模型（共享定义）
所有微服务共享的客户表结构定义
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, JSON, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base


class Customer(Base):
    """客户模型（共享定义）"""
    __tablename__ = "customers"
    
    # 基础字段
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(100), nullable=True, unique=True, index=True)
    
    # 客户类型和来源
    customer_type = Column(String(50), nullable=False, default="individual", index=True)  # individual, organization
    customer_source_type = Column(String(50), nullable=False, default="own", index=True)  # own, agent
    
    # 层级关系
    parent_customer_id = Column(String(36), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # 关联关系（注意：users 和 organizations 表在其他服务中，但可以通过 common.models 引用）
    owner_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)  # 内部客户所有者
    agent_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # 渠道客户用户
    agent_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)  # 渠道客户组织
    source_id = Column(String(36), ForeignKey("customer_sources.id", ondelete="SET NULL"), nullable=True, index=True)  # 客户来源
    channel_id = Column(String(36), ForeignKey("customer_channels.id", ondelete="SET NULL"), nullable=True, index=True)  # 客户渠道
    
    # 数据隔离字段
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True, comment="组织ID（数据隔离）")
    
    # 业务字段
    level = Column(String(50), nullable=True)  # 客户等级
    industry = Column(String(255), nullable=True)  # 行业
    description = Column(Text, nullable=True)  # 描述
    tags = Column(JSON, nullable=True, default=lambda: [])  # 标签
    is_locked = Column(Boolean, nullable=True, default=False)  # 是否锁定
    customer_requirements = Column(Text, nullable=True)  # 客户需求
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 关系
    parent_customer = relationship("Customer", foreign_keys=[parent_customer_id], remote_side=[id], backref="child_customers")
    
    # 检查约束
    __table_args__ = (
        CheckConstraint("customer_type IN ('individual', 'organization')", name="chk_customer_type"),
        CheckConstraint("customer_source_type IN ('own', 'agent')", name="chk_customer_source_type"),
    )

