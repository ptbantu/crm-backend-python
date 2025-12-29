"""
收款模型
"""
from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey, Boolean, Enum, Text, Integer, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models.user import User
from common.models.opportunity import Opportunity
from common.models.contract import Contract
from common.models.contract_entity import ContractEntity
import uuid
import enum


class PaymentModeEnum(str, enum.Enum):
    """回款模式枚举"""
    FULL = "full"  # 全款
    PARTIAL = "partial"  # 部分
    PREPAYMENT = "prepayment"  # 预付
    FINAL = "final"  # 尾款


class PaymentStatusEnum(str, enum.Enum):
    """收款状态枚举"""
    PENDING_REVIEW = "pending_review"  # 待Lulu核对
    CONFIRMED = "confirmed"  # 已确认
    REJECTED = "rejected"  # 拒绝
    REFUNDED = "refunded"  # 退款


class Payment(Base):
    """收款记录表模型"""
    __tablename__ = "payments"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    opportunity_id = Column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True, comment="商机ID")
    contract_id = Column(String(36), ForeignKey("contracts.id", ondelete="SET NULL"), nullable=True, index=True, comment="关联合同ID")
    execution_order_id = Column(String(36), ForeignKey("execution_orders.id", ondelete="SET NULL"), nullable=True, index=True, comment="关联执行订单ID")
    payment_no = Column(String(50), unique=True, nullable=False, index=True, comment="收款编号（如：PAY-20251228-001）")
    entity_id = Column(String(36), ForeignKey("contract_entities.id", ondelete="RESTRICT"), nullable=False, index=True, comment="签约主体ID")
    
    # 金额信息
    amount = Column(Numeric(18, 2), nullable=False, comment="本次收款金额（含税）")
    tax_amount = Column(Numeric(18, 2), nullable=False, default=0.00, comment="本次税额（冗余，便于核对）")
    currency = Column(String(10), nullable=False, comment="币种：CNY 或 IDR")
    
    # 付款信息
    payment_method = Column(String(100), nullable=True, comment="付款方式（如：银行转账、微信、支付宝）")
    payment_mode = Column(Enum(PaymentModeEnum), nullable=False, comment="回款模式")
    received_at = Column(Date, nullable=True, comment="到账日期")
    
    # 状态与核对
    status = Column(Enum(PaymentStatusEnum), nullable=False, default=PaymentStatusEnum.PENDING_REVIEW, index=True, comment="收款状态")
    reviewed_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="核对人ID（通常Lulu）")
    reviewed_at = Column(DateTime, nullable=True, comment="核对时间")
    review_notes = Column(Text, nullable=True, comment="核对备注")
    
    # 交付验证
    is_final_payment = Column(Boolean, nullable=False, default=False, index=True, comment="是否尾款（1=是，触发最终收款检查）")
    delivery_verified = Column(Boolean, nullable=False, default=False, comment="交付已验证（1=是，所有执行订单及依赖完成）")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="创建人ID（通常销售或客户上传）")
    
    # 关系
    opportunity = relationship("Opportunity", foreign_keys=[opportunity_id], primaryjoin="Payment.opportunity_id == Opportunity.id", back_populates="payments")
    contract = relationship("Contract", foreign_keys=[contract_id], primaryjoin="Payment.contract_id == Contract.id", back_populates="payments")
    execution_order = relationship("ExecutionOrder", foreign_keys=[execution_order_id], primaryjoin="Payment.execution_order_id == ExecutionOrder.id", back_populates="payments")
    entity = relationship("ContractEntity", foreign_keys=[entity_id], primaryjoin="Payment.entity_id == ContractEntity.id", back_populates="payments")
    reviewer = relationship("User", foreign_keys=[reviewed_by], primaryjoin="Payment.reviewed_by == User.id", backref="reviewed_payments")
    creator = relationship("User", foreign_keys=[created_by], primaryjoin="Payment.created_by == User.id", backref="created_payments")
    vouchers = relationship("PaymentVoucher", back_populates="payment", cascade="all, delete-orphan")
    collection_todos = relationship("CollectionTodo", back_populates="payment", cascade="all, delete-orphan")
    
    # 约束
    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_payment_amount"),
    )


class PaymentVoucher(Base):
    """收款凭证上传表模型"""
    __tablename__ = "payment_vouchers"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    payment_id = Column(String(36), ForeignKey("payments.id", ondelete="CASCADE"), nullable=False, index=True, comment="收款记录ID")
    
    # 文件信息
    file_name = Column(String(255), nullable=False, comment="凭证文件名（如：转账截图.jpg）")
    file_url = Column(String(500), nullable=False, comment="OSS存储路径（班兔合同云）")
    file_size_kb = Column(Integer, nullable=True, comment="文件大小")
    is_primary = Column(Boolean, nullable=False, default=False, index=True, comment="是否主要凭证（1=是，用于核对）")
    
    # 审计字段
    uploaded_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="上传人ID（通常销售或客户）")
    uploaded_at = Column(DateTime, nullable=False, server_default=func.now(), comment="上传时间")
    
    # 关系
    payment = relationship("Payment", foreign_keys=[payment_id], primaryjoin="PaymentVoucher.payment_id == Payment.id", back_populates="vouchers")
    uploader = relationship("User", foreign_keys=[uploaded_by], primaryjoin="PaymentVoucher.uploaded_by == User.id", backref="uploaded_payment_vouchers")


class CollectionTodo(Base):
    """收款待办事项表模型"""
    __tablename__ = "collection_todos"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    opportunity_id = Column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True, comment="商机ID")
    payment_id = Column(String(36), ForeignKey("payments.id", ondelete="SET NULL"), nullable=True, index=True, comment="关联收款ID")
    
    # 待办信息
    todo_type = Column(String(50), nullable=False, index=True, comment="待办类型")
    title = Column(String(255), nullable=False, comment="待办标题")
    description = Column(Text, nullable=True, comment="详细描述")
    assigned_to = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="分配人ID（如Lulu核对）")
    due_date = Column(DateTime, nullable=True, comment="截止时间")
    
    # 状态
    status = Column(String(50), nullable=False, default="pending", index=True, comment="待办状态")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    completed_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="完成人ID")
    notification_sent = Column(Boolean, nullable=False, default=False, comment="是否已发送提醒（1=是）")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    
    # 关系
    opportunity = relationship("Opportunity", foreign_keys=[opportunity_id], primaryjoin="CollectionTodo.opportunity_id == Opportunity.id", back_populates="collection_todos")
    payment = relationship("Payment", foreign_keys=[payment_id], primaryjoin="CollectionTodo.payment_id == Payment.id", back_populates="collection_todos")
    assignee = relationship("User", foreign_keys=[assigned_to], primaryjoin="CollectionTodo.assigned_to == User.id", backref="assigned_collection_todos")
    completer = relationship("User", foreign_keys=[completed_by], primaryjoin="CollectionTodo.completed_by == User.id", backref="completed_collection_todos")
