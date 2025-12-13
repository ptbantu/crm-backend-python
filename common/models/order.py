"""
订单模型
"""
from sqlalchemy import Column, String, Numeric, Date, Text, ForeignKey, Index, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import DATETIME
from decimal import Decimal

from common.database import Base
# 从共享模型导入 User 和 Customer
from common.models import User, Customer
import uuid


class Order(Base):
    """订单模型"""
    __tablename__ = "orders"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    order_number = Column(String(100), unique=True, nullable=False, index=True, comment="订单号")
    title = Column(String(255), nullable=False, comment="订单标题")
    
    # 关联
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True, comment="客户ID")
    service_record_id = Column(String(36), nullable=True, index=True, comment="服务记录ID（跨服务引用）")
    workflow_instance_id = Column(String(36), ForeignKey("workflow_instances.id", ondelete="SET NULL"), nullable=True, index=True, comment="工作流实例ID")
    product_id = Column(String(36), nullable=True, index=True, comment="产品ID（向后兼容，跨服务引用）")
    sales_user_id = Column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True, comment="销售用户ID")
    
    # EVOA 字段
    entry_city = Column(String(255), nullable=True, comment="入境城市（来自 EVOA）")
    passport_id = Column(String(100), nullable=True, comment="护照ID（来自 EVOA）")
    processor = Column(String(255), nullable=True, comment="处理器（来自 EVOA）")
    
    # 金额信息（从订单项汇总）
    total_amount = Column(Numeric(18, 2), nullable=True, comment="订单总金额（从订单项汇总）")
    discount_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False, comment="订单级折扣金额")
    final_amount = Column(Numeric(18, 2), nullable=True, comment="最终金额（total_amount - discount_amount）")
    currency_code = Column(String(10), default="CNY", nullable=False, comment="货币代码")
    exchange_rate = Column(Numeric(18, 6), nullable=True, comment="汇率")
    
    # 向后兼容字段
    quantity = Column(Integer, default=1, nullable=True, comment="数量（向后兼容）")
    unit_price = Column(Numeric(18, 2), nullable=True, comment="单价（向后兼容）")
    product_name = Column(String(255), nullable=True, comment="产品名称（向后兼容）")
    sales_username = Column(String(255), nullable=True, comment="销售用户名（向后兼容）")
    
    # 状态
    status_id = Column(String(36), nullable=True, index=True, comment="状态ID（跨服务引用）")
    status_code = Column(String(50), nullable=True, index=True, comment="状态代码")
    
    # 时间信息
    expected_start_date = Column(Date, nullable=True, comment="预期开始日期")
    expected_completion_date = Column(Date, nullable=True, comment="预期完成日期")
    actual_start_date = Column(Date, nullable=True, comment="实际开始日期")
    actual_completion_date = Column(Date, nullable=True, comment="实际完成日期")
    
    # 备注
    customer_notes = Column(Text, nullable=True, comment="客户备注")
    internal_notes = Column(Text, nullable=True, comment="内部备注")
    requirements = Column(Text, nullable=True, comment="需求和要求")
    
    # 审计字段
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="创建人ID")
    updated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="更新人ID")
    created_at = Column(DATETIME, nullable=False, server_default=func.now(), index=True, comment="创建时间")
    updated_at = Column(DATETIME, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    customer = relationship(Customer, foreign_keys=[customer_id], backref="orders")
    sales_user = relationship(User, foreign_keys=[sales_user_id], backref="sales_orders")
    creator = relationship(User, foreign_keys=[created_by], backref="created_orders")
    updater = relationship(User, foreign_keys=[updated_by], backref="updated_orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    order_comments = relationship("OrderComment", back_populates="order", cascade="all, delete-orphan")
    order_files = relationship("OrderFile", back_populates="order", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_orders_customer", "customer_id"),
        Index("ix_orders_sales", "sales_user_id"),
        Index("ix_orders_status", "status_code"),
        Index("ix_orders_created", "created_at"),
    )

