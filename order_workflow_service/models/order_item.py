"""
订单项模型
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Numeric, Date, CheckConstraint, UniqueConstraint
from sqlalchemy.sql import func
from order_workflow_service.database import Base
import uuid


class OrderItem(Base):
    """订单项模型"""
    __tablename__ = "order_items"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 订单关联
    order_id = Column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    item_number = Column(Integer, nullable=False, comment="订单项序号（1, 2, 3...）")
    
    # 产品/服务关联
    product_id = Column(String(36), ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    product_name_zh = Column(String(255), nullable=True, comment="产品名称（中文）")
    product_name_id = Column(String(255), nullable=True, comment="产品名称（印尼语）")
    product_code = Column(String(100), nullable=True, comment="产品代码")
    
    # 服务类型关联
    service_type_id = Column(String(36), ForeignKey("service_types.id", ondelete="SET NULL"), nullable=True, index=True)
    service_type_name_zh = Column(String(255), nullable=True, comment="服务类型名称（中文）")
    service_type_name_id = Column(String(255), nullable=True, comment="服务类型名称（印尼语）")
    
    # 数量信息
    quantity = Column(Integer, nullable=False, default=1, comment="数量")
    unit = Column(String(50), nullable=True, comment="单位")
    
    # 价格信息
    unit_price = Column(Numeric(18, 2), nullable=True, comment="单价")
    discount_amount = Column(Numeric(18, 2), nullable=False, default=0, comment="折扣金额")
    item_amount = Column(Numeric(18, 2), nullable=True, comment="订单项金额（quantity * unit_price - discount_amount）")
    currency_code = Column(String(10), nullable=False, default="CNY", comment="货币代码")
    
    # 描述信息（双语）
    description_zh = Column(Text, nullable=True, comment="订单项描述（中文）")
    description_id = Column(Text, nullable=True, comment="订单项描述（印尼语）")
    requirements = Column(Text, nullable=True, comment="需求和要求")
    
    # 时间信息
    expected_start_date = Column(Date, nullable=True, comment="预期开始日期")
    expected_completion_date = Column(Date, nullable=True, comment="预期完成日期")
    
    # 状态
    status = Column(String(50), nullable=False, default="pending", index=True, comment="订单项状态：pending, in_progress, completed, cancelled")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 检查约束和唯一约束
    __table_args__ = (
        CheckConstraint(
            "COALESCE(quantity, 0) >= 0 AND COALESCE(unit_price, 0) >= 0 AND COALESCE(discount_amount, 0) >= 0 AND COALESCE(item_amount, 0) >= 0",
            name="chk_order_items_amounts_nonneg"
        ),
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed', 'cancelled')",
            name="chk_order_items_status"
        ),
        UniqueConstraint("order_id", "item_number", name="ux_order_items_order_item_number"),
    )

