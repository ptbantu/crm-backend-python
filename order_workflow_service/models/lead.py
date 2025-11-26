"""
线索模型
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, JSON, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base  # 使用 common.database.Base 确保与共享模型使用同一个 Base
# 从共享模型导入 User 和 Customer
from common.models import User, Customer
import uuid


class Lead(Base):
    """线索模型"""
    __tablename__ = "leads"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 基础信息
    name = Column(String(255), nullable=False, comment="线索名称")
    company_name = Column(String(255), nullable=True, comment="公司名称")
    contact_name = Column(String(255), nullable=True, comment="联系人姓名")
    phone = Column(String(50), nullable=True, comment="联系电话")
    email = Column(String(255), nullable=True, comment="邮箱")
    address = Column(Text, nullable=True, comment="地址")
    
    # 关联信息
    # 注意：customers 表现在在本地定义，可以使用外键约束
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True, comment="关联客户ID（可选）")
    # 注意：organizations 表在 foundation_service 的数据库中，不能使用外键约束，只保留索引
    # organization_id 必须为 NOT NULL，创建时从用户的 organization_employees 表自动获取
    organization_id = Column(String(36), nullable=False, index=True, comment="组织ID（必填，从创建用户的组织自动获取，用于数据隔离）")
    # 注意：users 表现在在本地定义，可以使用外键约束
    owner_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="销售负责人ID")
    
    # 状态管理
    status = Column(String(50), default="new", nullable=False, index=True, comment="状态：new(新建), contacted(已联系), qualified(已确认), converted(已转化), lost(已丢失)")
    # 客户分级（通过外键关联到 customer_levels.code）
    level = Column(String(50), ForeignKey("customer_levels.code", ondelete="SET NULL"), nullable=True, index=True, comment="客户分级代码（外键关联到 customer_levels.code）")
    
    # 公海池
    is_in_public_pool = Column(Boolean, default=False, nullable=False, index=True, comment="是否在公海池")
    pool_id = Column(String(36), ForeignKey("lead_pools.id", ondelete="SET NULL"), nullable=True, index=True, comment="线索池ID")
    moved_to_pool_at = Column(DateTime, nullable=True, comment="移入公海池时间")
    
    # 天眼查
    tianyancha_data = Column(JSON, nullable=True, comment="天眼查数据（JSON格式）")
    tianyancha_synced_at = Column(DateTime, nullable=True, comment="天眼查同步时间")
    
    # 时间字段
    last_follow_up_at = Column(DateTime, nullable=True, comment="最后跟进时间")
    next_follow_up_at = Column(DateTime, nullable=True, comment="下次跟进时间")
    
    # 审计字段
    # 注意：users 表现在在本地定义，可以使用外键约束
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="创建人ID")
    updated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="更新人ID")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系（从共享模型导入，支持 relationship）
    # 明确指定 primaryjoin 确保 SQLAlchemy 能正确识别外键关系
    customer = relationship(
        Customer,
        foreign_keys=[customer_id],
        primaryjoin="Lead.customer_id == Customer.id",
        backref="leads"
    )
    # organization = relationship("Organization", foreign_keys=[organization_id])  # 跨服务引用，不使用 relationship
    owner = relationship(User, foreign_keys=[owner_user_id], backref="owned_leads")
    creator = relationship(User, foreign_keys=[created_by], backref="created_leads")
    updater = relationship(User, foreign_keys=[updated_by], backref="updated_leads")
    # 客户分级关系（通过 code 关联）
    customer_level = relationship(
        "CustomerLevel",
        foreign_keys=[level],
        primaryjoin="Lead.level == CustomerLevel.code",
        backref="leads"
    )
    pool = relationship("LeadPool", foreign_keys=[pool_id], backref="pool_leads")
    follow_ups = relationship("LeadFollowUp", back_populates="lead", cascade="all, delete-orphan")
    notes = relationship("LeadNote", back_populates="lead", cascade="all, delete-orphan")
    
    # 检查约束
    __table_args__ = (
        CheckConstraint(
            "status IN ('new', 'contacted', 'qualified', 'converted', 'lost')",
            name="chk_leads_status"
        ),
    )

