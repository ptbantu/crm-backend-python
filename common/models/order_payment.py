"""
订单回款模型
"""
from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey, Boolean, Enum, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models.user import User
from common.models.order import Order
from common.models.order_item import OrderItem
import uuid
import enum


class PaymentTypeEnum(str, enum.Enum):
    """回款类型枚举"""
    MONTHLY = "monthly"  # 长周期月付
    FULL = "full"  # 全部
    PARTIAL = "partial"  # 部分


class PaymentStatusEnum(str, enum.Enum):
    """回款状态枚举"""
    PENDING = "pending"  # 待确认
    CONFIRMED = "confirmed"  # 已确认
    OVERDUE = "overdue"  # 逾期


class OrderPayment(Base):
    """订单回款记录表模型"""
    __tablename__ = "order_payments"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    order_id = Column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True, comment="订单ID")
    order_item_id = Column(String(36), ForeignKey("order_items.id", ondelete="SET NULL"), nullable=True, index=True, comment="订单项ID（若针对具体服务）")
    
    # 回款信息
    payment_amount = Column(Numeric(18, 2), nullable=False, comment="本次回款金额")
    payment_date = Column(Date, nullable=False, index=True, comment="回款日期（长周期为每月实际日期）")
    payment_type = Column(Enum(PaymentTypeEnum), nullable=False, default=PaymentTypeEnum.FULL, comment="回款类型")
    is_excluded_from_full = Column(Boolean, nullable=False, default=False, comment="是否排除在全部回款计算中（1=长周期服务）")
    
    # 状态
    status = Column(Enum(PaymentStatusEnum), nullable=False, default=PaymentStatusEnum.PENDING, index=True, comment="回款状态")
    confirmed_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="确认人ID（如Lulu）")
    confirmed_at = Column(DateTime, nullable=True, comment="确认时间")
    notes = Column(Text, nullable=True, comment="回款备注（如财务核对信息）")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    order = relationship("Order", foreign_keys=[order_id], primaryjoin="OrderPayment.order_id == Order.id", back_populates="payments")
    order_item = relationship("OrderItem", foreign_keys=[order_item_id], primaryjoin="OrderPayment.order_item_id == OrderItem.id", back_populates="payments")
    confirmer = relationship("User", foreign_keys=[confirmed_by], primaryjoin="OrderPayment.confirmed_by == User.id", backref="confirmed_order_payments")
    
    # 约束
    __table_args__ = (
        CheckConstraint("payment_amount > 0", name="chk_order_payment_amount"),
    )
