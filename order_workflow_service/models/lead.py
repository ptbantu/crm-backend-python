"""
线索模型
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, JSON, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from order_workflow_service.database import Base
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
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True, comment="关联客户ID（可选）")
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True, comment="组织ID")
    owner_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="销售负责人ID")
    
    # 状态管理
    status = Column(String(50), default="new", nullable=False, index=True, comment="状态：new(新建), contacted(已联系), qualified(已确认), converted(已转化), lost(已丢失)")
    level = Column(String(50), nullable=True, comment="客户分级")
    
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
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="创建人ID")
    updated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="更新人ID")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系（注意：Customer和Organization模型可能在其他服务中，这里使用字符串引用）
    # customer = relationship("Customer", foreign_keys=[customer_id], backref="leads")
    # organization = relationship("Organization", foreign_keys=[organization_id])
    # owner = relationship("User", foreign_keys=[owner_user_id])
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

