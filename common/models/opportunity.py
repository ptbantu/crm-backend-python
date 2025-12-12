"""
商机模型
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Numeric, Date, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models import User, Customer
from common.models.product import Product
import uuid


class Opportunity(Base):
    """商机模型"""
    __tablename__ = "opportunities"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True, comment="客户ID")
    lead_id = Column(String(36), ForeignKey("leads.id", ondelete="SET NULL"), nullable=True, index=True, comment="来源线索ID（可选，用于追溯）")
    owner_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="负责人（外键 → users.id）")
    organization_id = Column(String(36), nullable=False, index=True, comment="组织ID（数据隔离）")
    
    # 基础信息
    name = Column(String(255), nullable=False, comment="商机名称")
    amount = Column(Numeric(18, 2), nullable=True, comment="商机金额")
    probability = Column(Integer, nullable=True, comment="成交概率（0-100）")
    stage = Column(String(50), nullable=False, default="initial_contact", index=True, comment="商机阶段（initial_contact, needs_analysis, proposal, negotiation, closed_won, closed_lost）")
    status = Column(String(50), nullable=False, default="active", index=True, comment="状态（active, won, lost, cancelled）")
    
    # 日期信息
    expected_close_date = Column(Date, nullable=True, comment="预期成交日期")
    actual_close_date = Column(Date, nullable=True, comment="实际成交日期")
    
    # 描述
    description = Column(Text, nullable=True, comment="描述")
    
    # 审计字段
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="创建人ID")
    updated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="更新人ID")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    customer = relationship("Customer", foreign_keys=[customer_id], primaryjoin="Opportunity.customer_id == Customer.id", backref="opportunities")
    lead = relationship("Lead", foreign_keys=[lead_id], primaryjoin="Opportunity.lead_id == Lead.id", backref="opportunities")
    owner = relationship("User", foreign_keys=[owner_user_id], primaryjoin="Opportunity.owner_user_id == User.id", backref="owned_opportunities")
    creator = relationship("User", foreign_keys=[created_by], primaryjoin="Opportunity.created_by == User.id", backref="created_opportunities")
    updater = relationship("User", foreign_keys=[updated_by], primaryjoin="Opportunity.updated_by == User.id", backref="updated_opportunities")
    products = relationship("OpportunityProduct", back_populates="opportunity", cascade="all, delete-orphan", order_by="OpportunityProduct.execution_order")
    payment_stages = relationship("OpportunityPaymentStage", back_populates="opportunity", cascade="all, delete-orphan", order_by="OpportunityPaymentStage.stage_number")
    
    # 约束
    __table_args__ = (
        CheckConstraint("stage IN ('initial_contact', 'needs_analysis', 'proposal', 'negotiation', 'closed_won', 'closed_lost')", name="chk_opportunities_stage"),
        CheckConstraint("status IN ('active', 'won', 'lost', 'cancelled')", name="chk_opportunities_status"),
        CheckConstraint("probability >= 0 AND probability <= 100", name="chk_opportunities_probability"),
    )


class OpportunityProduct(Base):
    """商机产品关联模型"""
    __tablename__ = "opportunity_products"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    opportunity_id = Column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True, comment="商机ID")
    product_id = Column(String(36), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True, comment="产品ID")
    
    # 产品信息
    quantity = Column(Integer, nullable=False, default=1, comment="数量")
    unit_price = Column(Numeric(18, 2), nullable=True, comment="单价")
    total_amount = Column(Numeric(18, 2), nullable=True, comment="总金额")
    
    # 执行顺序和状态
    execution_order = Column(Integer, nullable=False, default=1, comment="执行顺序（1, 2, 3...）")
    status = Column(String(50), nullable=False, default="pending", index=True, comment="状态（pending: 待执行, in_progress: 进行中, completed: 已完成, cancelled: 已取消）")
    
    # 日期信息
    start_date = Column(Date, nullable=True, comment="开始日期")
    expected_completion_date = Column(Date, nullable=True, comment="预期完成日期")
    actual_completion_date = Column(Date, nullable=True, comment="实际完成日期")
    
    # 备注
    notes = Column(Text, nullable=True, comment="备注")
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    opportunity = relationship("Opportunity", foreign_keys=[opportunity_id], primaryjoin="OpportunityProduct.opportunity_id == Opportunity.id", back_populates="products")
    product = relationship("Product", foreign_keys=[product_id], primaryjoin="OpportunityProduct.product_id == Product.id", backref="opportunity_products")
    
    # 约束
    __table_args__ = (
        CheckConstraint("opportunity_id IS NOT NULL AND product_id IS NOT NULL", name="chk_opportunity_products_not_null"),
        CheckConstraint("quantity > 0", name="chk_opportunity_products_quantity"),
        CheckConstraint("execution_order > 0", name="chk_opportunity_products_execution_order"),
        CheckConstraint("status IN ('pending', 'in_progress', 'completed', 'cancelled')", name="chk_opportunity_products_status"),
    )


class OpportunityPaymentStage(Base):
    """商机付款阶段模型"""
    __tablename__ = "opportunity_payment_stages"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    opportunity_id = Column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True, comment="商机ID")
    
    # 阶段信息
    stage_number = Column(Integer, nullable=False, comment="阶段序号（1, 2, 3...）")
    stage_name = Column(String(255), nullable=False, comment="阶段名称（如：首付款、中期款、尾款）")
    amount = Column(Numeric(18, 2), nullable=False, comment="应付金额")
    due_date = Column(Date, nullable=True, index=True, comment="到期日期")
    payment_trigger = Column(String(50), nullable=True, default="manual", comment="付款触发条件（manual, milestone, date, completion）")
    status = Column(String(50), nullable=False, default="pending", index=True, comment="状态（pending, paid, overdue, cancelled）")
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    opportunity = relationship("Opportunity", foreign_keys=[opportunity_id], primaryjoin="OpportunityPaymentStage.opportunity_id == Opportunity.id", back_populates="payment_stages")
    
    # 约束
    __table_args__ = (
        CheckConstraint("stage_number > 0", name="chk_opportunity_payment_stages_stage_number"),
        CheckConstraint("amount >= 0", name="chk_opportunity_payment_stages_amount"),
        CheckConstraint("payment_trigger IN ('manual', 'milestone', 'date', 'completion')", name="chk_opportunity_payment_stages_trigger"),
        CheckConstraint("status IN ('pending', 'paid', 'overdue', 'cancelled')", name="chk_opportunity_payment_stages_status"),
    )

