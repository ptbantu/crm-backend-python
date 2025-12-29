"""
商机模型
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Numeric, Date, CheckConstraint, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models.user import User
from common.models.customer import Customer
from common.models.product import Product
import uuid
import enum


class Opportunity(Base):
    """商机模型"""
    __tablename__ = "opportunities"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True, comment="客户ID")
    lead_id = Column(String(36), ForeignKey("leads.id", ondelete="SET NULL"), nullable=True, index=True, comment="来源线索ID（可选，用于追溯）")
    owner_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="负责人（外键 → users.id）")
    organization_id = Column(String(36), nullable=False, index=True, comment="组织ID（数据隔离）")
    
    # 基础信息
    name = Column(String(255), nullable=False, comment="商机名称")
    amount = Column(Numeric(18, 2), nullable=True, comment="商机金额")
    probability = Column(Integer, nullable=True, comment="成交概率（0-100）")
    stage = Column(String(50), nullable=False, default="initial_contact", index=True, comment="商机阶段（initial_contact, needs_analysis, proposal, negotiation, closed_won, closed_lost）")
    status = Column(String(50), nullable=False, default="active", index=True, comment="状态（active, won, lost, cancelled）")
    
    # 阶段工作流（新增）
    current_stage_id = Column(String(36), ForeignKey("opportunity_stage_templates.id", ondelete="SET NULL"), nullable=True, index=True, comment="当前阶段ID")
    workflow_status = Column(String(50), nullable=False, default="active", comment="工作流整体状态：active(进行中), paused(暂停), completed(完成), cancelled(取消)")
    collection_status = Column(String(50), nullable=False, default="not_started", comment="整体收款状态：not_started(未开始), partial(部分回款), full(全额回款), overpaid(超收)")
    total_received_amount = Column(Numeric(18, 2), nullable=False, default=0.00, comment="已收总金额（冗余，自动维护）")
    final_payment_id = Column(String(36), ForeignKey("payments.id", ondelete="SET NULL"), nullable=True, comment="尾款记录ID")
    
    # 服务类型（新增）
    service_type = Column(String(20), nullable=False, default="one_time", comment="服务类型：one_time(一次性), long_term(长周期), mixed(混合)")
    is_split_required = Column(Boolean, nullable=False, default=False, comment="是否需要订单拆分（1=需要，长周期服务标记）")
    split_order_required = Column(Boolean, nullable=False, default=False, comment="是否需要拆分独立订单（1=是，长周期服务将生成独立订单）")
    has_staged_services = Column(Boolean, nullable=False, default=False, comment="是否包含分阶段服务（财税/IT分阶段）")
    tax_service_cycle_months = Column(Integer, nullable=True, comment="财税服务周期（月，6或12）")
    tax_service_start_date = Column(Date, nullable=True, comment="财税服务开始日期")
    
    # 关联报价单和合同（新增）
    primary_quotation_id = Column(String(36), ForeignKey("quotations.id", ondelete="SET NULL"), nullable=True, comment="主报价单ID（客户接受的最终报价单）")
    primary_contract_id = Column(String(36), ForeignKey("contracts.id", ondelete="SET NULL"), nullable=True, comment="主合同ID（签署生效的最终合同）")
    
    # 开发人（新增）
    developed_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="开发人ID（如Lilly开发的客户）")
    
    # 日期信息
    expected_close_date = Column(Date, nullable=True, comment="预期成交日期")
    actual_close_date = Column(Date, nullable=True, comment="实际成交日期")
    last_followup_at = Column(DateTime, nullable=True, comment="最后跟进时间")
    
    # 描述
    description = Column(Text, nullable=True, comment="描述")
    
    # 长久未跟进标记（新增）
    is_stale = Column(Boolean, nullable=False, default=False, comment="是否长久未跟进（1=是）")
    
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
    developer = relationship("User", foreign_keys=[developed_by], primaryjoin="Opportunity.developed_by == User.id", backref="developed_opportunities")
    products = relationship("OpportunityProduct", back_populates="opportunity", cascade="all, delete-orphan", order_by="OpportunityProduct.execution_order")
    payment_stages = relationship("OpportunityPaymentStage", back_populates="opportunity", cascade="all, delete-orphan", order_by="OpportunityPaymentStage.stage_number")
    # 新增关系
    current_stage = relationship("OpportunityStageTemplate", foreign_keys=[current_stage_id], primaryjoin="Opportunity.current_stage_id == OpportunityStageTemplate.id", back_populates="opportunities")
    stage_histories = relationship("OpportunityStageHistory", back_populates="opportunity", cascade="all, delete-orphan", order_by="OpportunityStageHistory.entered_at.desc()")
    primary_quotation = relationship("Quotation", foreign_keys=[primary_quotation_id], primaryjoin="Opportunity.primary_quotation_id == Quotation.id", backref="primary_opportunities")
    primary_contract = relationship("Contract", foreign_keys=[primary_contract_id], primaryjoin="Opportunity.primary_contract_id == Contract.id", backref="primary_opportunities")
    final_payment = relationship("Payment", foreign_keys=[final_payment_id], primaryjoin="Opportunity.final_payment_id == Payment.id", backref="final_opportunities")
    # quotations关系：先定义基本关系，foreign_keys将在文件末尾通过延迟导入配置
    quotations = relationship("Quotation", back_populates="opportunity", cascade="all, delete-orphan")
    # contracts关系：先定义基本关系，foreign_keys将在文件末尾通过延迟导入配置
    contracts = relationship("Contract", back_populates="opportunity", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="opportunity", cascade="all, delete-orphan")
    material_documents = relationship("ContractMaterialDocument", back_populates="opportunity", cascade="all, delete-orphan")
    material_notification_emails = relationship("MaterialNotificationEmail", back_populates="opportunity", cascade="all, delete-orphan")
    execution_orders = relationship("ExecutionOrder", back_populates="opportunity", cascade="all, delete-orphan")
    # payments关系：先定义基本关系，foreign_keys将在文件末尾通过延迟导入配置
    payments = relationship("Payment", back_populates="opportunity", cascade="all, delete-orphan")
    collection_todos = relationship("CollectionTodo", back_populates="opportunity", cascade="all, delete-orphan")
    
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


# 延迟配置quotations和contracts关系，使用实际的Column对象避免多重外键路径问题
# 在文件末尾导入Quotation和Contract后重新定义关系
def _configure_opportunity_relationships():
    """延迟配置Opportunity的关系，明确指定foreign_keys"""
    from common.models.quotation import Quotation
    from common.models.contract import Contract
    from common.models.payment import Payment
    
    # 重新定义quotations关系，使用实际的Column对象
    Opportunity.quotations = relationship(
        "Quotation",
        primaryjoin="Opportunity.id == Quotation.opportunity_id",
        foreign_keys=[Quotation.opportunity_id],
        back_populates="opportunity",
        cascade="all, delete-orphan"
    )
    
    # 重新定义contracts关系，使用实际的Column对象
    Opportunity.contracts = relationship(
        "Contract",
        primaryjoin="Opportunity.id == Contract.opportunity_id",
        foreign_keys=[Contract.opportunity_id],
        back_populates="opportunity",
        cascade="all, delete-orphan"
    )
    
    # 重新定义payments关系，使用实际的Column对象
    Opportunity.payments = relationship(
        "Payment",
        primaryjoin="Opportunity.id == Payment.opportunity_id",
        foreign_keys=[Payment.opportunity_id],
        back_populates="opportunity",
        cascade="all, delete-orphan"
    )

# 尝试立即配置（如果Quotation和Contract已导入）
try:
    _configure_opportunity_relationships()
except ImportError:
    # 如果未导入，使用事件系统延迟配置
    from sqlalchemy import event
    from sqlalchemy.orm import mapper_configured
    
    @event.listens_for(mapper_configured, "before")
    def receive_mapper_configured(mapper, cls):
        if cls == Opportunity:
            try:
                _configure_opportunity_relationships()
            except:
                pass



