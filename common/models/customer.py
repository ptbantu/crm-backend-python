"""
客户模型（共享定义）
所有微服务共享的客户表结构定义
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, JSON, CheckConstraint, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base


class Customer(Base):
    """客户模型（共享定义）"""
    __tablename__ = "customers"
    
    # 基础字段
    id = Column(Integer, primary_key=True, autoincrement=True, comment="客户ID：数据库自增，5位数字")
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(100), nullable=True, unique=True, index=True)
    
    # 客户类型和来源
    customer_type = Column(String(50), nullable=False, default="individual", index=True)  # individual (个人), organization (组织)
    customer_source_type = Column(String(50), nullable=False, default="own", index=True)  # own, agent
    
    # 层级关系
    parent_customer_id = Column(Integer, ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # 关联关系（注意：users 和 organizations 表在其他服务中，但可以通过 common.models 引用）
    owner_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)  # 内部客户所有者
    agent_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # 渠道客户用户
    agent_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)  # 渠道客户组织
    source_id = Column(String(36), ForeignKey("customer_sources.id", ondelete="SET NULL"), nullable=True, index=True)  # 客户来源
    channel_id = Column(String(36), ForeignKey("customer_channels.id", ondelete="SET NULL"), nullable=True, index=True)  # 客户渠道
    
    # 数据隔离字段
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True, comment="组织ID（数据隔离）")
    
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
    level = Column(String(50), ForeignKey("customer_levels.code", ondelete="SET NULL", onupdate="CASCADE"), nullable=True, index=True)  # 客户等级（外键关联customer_levels.code）
    industry_id = Column(String(36), ForeignKey("industries.id", ondelete="SET NULL"), nullable=True, index=True)  # 行业ID（外键关联industries.id）
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
    
    # 跟进时间字段
    last_follow_up_at = Column(DateTime, nullable=True, index=True, comment="最后跟进时间")
    next_follow_up_at = Column(DateTime, nullable=True, index=True, comment="下次跟进时间")
    
    # 关系
    parent_customer = relationship("Customer", foreign_keys=[parent_customer_id], remote_side=[id], primaryjoin="Customer.parent_customer_id == Customer.id", backref="child_customers")
    follow_ups = relationship("CustomerFollowUp", back_populates="customer", cascade="all, delete-orphan")
    notes = relationship("CustomerNote", back_populates="customer", cascade="all, delete-orphan")
    
    # 检查约束
    # 注意：extend_existing 必须作为字典放在最后，用于处理表重复定义的情况
    __table_args__ = (
        CheckConstraint("customer_type IN ('individual', 'organization')", name="chk_customer_type"),
        CheckConstraint("customer_source_type IN ('own', 'agent')", name="chk_customer_source_type"),
        {'extend_existing': True},
    )

