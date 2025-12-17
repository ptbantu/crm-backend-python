"""
订单价格快照模型（共享定义）
所有微服务共享的订单价格快照表结构定义
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Integer, CheckConstraint
from sqlalchemy.sql import func
from common.database import Base
import uuid


class OrderPriceSnapshot(Base):
    """订单价格快照模型（共享定义，用于订单价格追溯）"""
    __tablename__ = "order_price_snapshots"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    order_item_id = Column(String(36), ForeignKey("order_items.id", ondelete="SET NULL"), nullable=True, index=True)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    
    # 价格快照信息
    price_type = Column(String(50), nullable=False, comment="价格类型：cost, channel, direct, list")
    currency = Column(String(10), nullable=False, comment="货币：IDR, CNY, USD, EUR")
    unit_price = Column(Numeric(18, 2), nullable=False, comment="单价快照")
    quantity = Column(Integer, nullable=False, default=1, comment="数量")
    subtotal = Column(Numeric(18, 2), nullable=False, comment="小计")
    discount_amount = Column(Numeric(18, 2), nullable=False, default=0, comment="折扣金额")
    final_amount = Column(Numeric(18, 2), nullable=False, comment="最终金额")
    
    # 汇率快照
    exchange_rate = Column(Numeric(18, 9), nullable=True, comment="汇率快照")
    base_currency = Column(String(10), nullable=False, comment="基准货币")
    converted_currency = Column(String(10), nullable=False, comment="转换后货币")
    
    # 客户等级价格快照
    customer_level_code = Column(String(50), nullable=True, comment="客户等级代码")
    customer_level_price = Column(Numeric(18, 2), nullable=True, comment="客户等级价格")
    
    # 时间戳
    snapshot_at = Column(DateTime, nullable=False, server_default=func.now(), index=True, comment="快照时间")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    
    # 约束
    __table_args__ = (
        CheckConstraint("unit_price >= 0", name="chk_order_price_snapshots_unit_price_nonneg"),
        CheckConstraint("subtotal >= 0", name="chk_order_price_snapshots_subtotal_nonneg"),
        CheckConstraint("final_amount >= 0", name="chk_order_price_snapshots_final_amount_nonneg"),
        CheckConstraint("price_type IN ('cost', 'channel', 'direct', 'list')", name="chk_order_price_snapshots_price_type"),
        CheckConstraint("currency IN ('IDR', 'CNY', 'USD', 'EUR')", name="chk_order_price_snapshots_currency"),
        {'extend_existing': True},
    )
