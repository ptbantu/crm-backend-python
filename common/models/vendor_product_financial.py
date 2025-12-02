"""
供应商产品财务记录模型（共享定义）
所有微服务共享的供应商产品财务记录表结构定义
"""
from sqlalchemy import Column, String, Text, Date, Boolean, DateTime, ForeignKey, Numeric, CheckConstraint
from sqlalchemy.sql import func
from common.database import Base
import uuid


class VendorProductFinancial(Base):
    """供应商产品财务记录模型（共享定义，用于报账）"""
    __tablename__ = "vendor_product_financials"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vendor_product_id = Column(String(36), ForeignKey("vendor_products.id", ondelete="CASCADE"), nullable=False, index=True)
    # 注意：orders 表在 order_workflow_service 的数据库中，不能使用外键约束
    order_id = Column(String(36), nullable=True, index=True)  # 关联订单ID（如果有）（跨服务，无外键）
    
    # 财务信息
    cost_amount_idr = Column(Numeric(18, 2), nullable=True)  # 成本金额（IDR）
    cost_amount_cny = Column(Numeric(18, 2), nullable=True)  # 成本金额（CNY）
    exchange_rate = Column(Numeric(18, 9), nullable=True)  # 汇率
    
    # 会计信息
    account_code = Column(String(100), nullable=True)  # 会计科目代码
    cost_center = Column(String(100), nullable=True)  # 成本中心
    expense_category = Column(String(100), nullable=True)  # 费用类别
    department = Column(String(100), nullable=True)  # 部门
    
    # 报账信息
    invoice_number = Column(String(255), nullable=True, index=True)  # 发票号
    invoice_date = Column(Date, nullable=True)  # 发票日期
    payment_status = Column(String(50), default="pending", nullable=False, index=True)  # 付款状态：pending, paid, cancelled
    # 注意：payments 表在 order_workflow_service 的数据库中，不能使用外键约束
    payment_id = Column(String(36), nullable=True, index=True)  # 关联付款记录ID（跨服务，无外键）
    
    # 审核信息
    is_approved = Column(Boolean, default=False, nullable=False, index=True)  # 是否已审核
    approved_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime, nullable=True)  # 审核时间
    approval_notes = Column(Text, nullable=True)  # 审核备注
    
    # 元数据
    notes = Column(Text, nullable=True)  # 备注
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 约束
    __table_args__ = (
        CheckConstraint(
            "COALESCE(cost_amount_idr,0) >= 0 AND COALESCE(cost_amount_cny,0) >= 0",
            name="chk_vendor_product_financials_amount_nonneg"
        ),
        CheckConstraint(
            "payment_status IN ('pending', 'paid', 'cancelled', 'refunded')",
            name="chk_vendor_product_financials_payment_status"
        ),
        {'extend_existing': True},
    )

