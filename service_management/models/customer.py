"""
客户模型
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, JSON, CheckConstraint
from sqlalchemy.sql import func
from service_management.database import Base
import uuid


class Customer(Base):
    """客户模型"""
    __tablename__ = "customers"
    
    # 基础字段
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(100), nullable=True, unique=True, index=True)
    
    # 客户类型和来源
    customer_type = Column(String(50), nullable=False, default="individual", index=True)  # individual, organization
    customer_source_type = Column(String(50), nullable=False, default="own", index=True)  # own, agent
    
    # 层级关系
    parent_customer_id = Column(String(36), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # 关联关系
    owner_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)  # 内部客户所有者
    agent_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # 渠道客户用户
    agent_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)  # 渠道客户组织
    source_id = Column(String(36), ForeignKey("customer_sources.id", ondelete="SET NULL"), nullable=True, index=True)  # 客户来源
    channel_id = Column(String(36), ForeignKey("customer_channels.id", ondelete="SET NULL"), nullable=True, index=True)  # 客户渠道
    
    # 外部系统字段
    id_external = Column(String(255), nullable=True, unique=True)
    owner_id_external = Column(String(255), nullable=True)
    owner_name = Column(String(255), nullable=True)
    created_by_external = Column(String(255), nullable=True)
    created_by_name = Column(String(255), nullable=True)
    updated_by_external = Column(String(255), nullable=True)
    updated_by_name = Column(String(255), nullable=True)
    created_at_src = Column(DateTime, nullable=True)
    updated_at_src = Column(DateTime, nullable=True)
    last_action_at_src = Column(DateTime, nullable=True)
    change_log_at_src = Column(DateTime, nullable=True)
    linked_module = Column(String(100), nullable=True)
    linked_id_external = Column(String(255), nullable=True)
    parent_id_external = Column(String(255), nullable=True)
    parent_name = Column(String(255), nullable=True)
    
    # 业务字段
    level = Column(String(50), nullable=True)  # 客户等级
    industry = Column(String(255), nullable=True)  # 行业
    description = Column(Text, nullable=True)  # 描述
    tags = Column(JSON, nullable=True, default=lambda: [])  # 标签
    is_locked = Column(Boolean, nullable=True, default=False)  # 是否锁定
    last_enriched_at_src = Column(DateTime, nullable=True)  # 最后充实时间
    enrich_status = Column(String(50), nullable=True)  # 充实状态
    channel_name = Column(String(255), nullable=True)  # 渠道名称（冗余字段）
    source_name = Column(String(255), nullable=True)  # 来源名称（冗余字段）
    customer_requirements = Column(Text, nullable=True)  # 客户需求
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 检查约束
    __table_args__ = (
        CheckConstraint("customer_type IN ('individual', 'organization')", name="chk_customer_type"),
        CheckConstraint("customer_source_type IN ('own', 'agent')", name="chk_customer_source_type"),
    )


class CustomerSource(Base):
    """客户来源模型"""
    __tablename__ = "customer_sources"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    display_order = Column(String(36), nullable=True, default="0")
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class CustomerChannel(Base):
    """客户渠道模型"""
    __tablename__ = "customer_channels"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    display_order = Column(String(36), nullable=True, default="0")
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

