"""
产品价格模型（共享定义）
所有微服务共享的产品价格表结构定义
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Numeric, CheckConstraint
from sqlalchemy.sql import func
from common.database import Base
import uuid


class ProductPrice(Base):
    """产品价格模型（共享定义，支持多价格类型和多货币）"""
    __tablename__ = "product_prices"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    # 注意：organizations 表在 foundation_service 的数据库中，不能使用外键约束
    organization_id = Column(String(36), nullable=True, index=True)  # NULL 表示通用价格（跨服务，无外键）
    
    # 价格信息
    price_type = Column(String(50), nullable=False, index=True)  # cost, channel, direct, list
    currency = Column(String(10), nullable=False, index=True)  # IDR, CNY, USD, EUR
    amount = Column(Numeric(18, 2), nullable=False)
    exchange_rate = Column(Numeric(18, 9), nullable=True)  # 汇率（用于计算）
    
    # 价格生效时间
    effective_from = Column(DateTime, nullable=False, server_default=func.now(), index=True)  # 生效时间
    effective_to = Column(DateTime, nullable=True, index=True)  # 失效时间（NULL表示当前有效）
    
    # 价格来源和审核
    source = Column(String(50), nullable=True)  # 价格来源：manual, import, contract
    is_approved = Column(Boolean, default=False, nullable=False)  # 是否已审核
    approved_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime, nullable=True)  # 审核时间
    
    # 变更信息
    change_reason = Column(Text, nullable=True)  # 变更原因
    changed_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 约束
    __table_args__ = (
        CheckConstraint("amount >= 0", name="chk_product_prices_amount_nonneg"),
        CheckConstraint("price_type IN ('cost', 'channel', 'direct', 'list')", name="chk_product_prices_price_type"),
        CheckConstraint("currency IN ('IDR', 'CNY', 'USD', 'EUR')", name="chk_product_prices_currency"),
        {'extend_existing': True},
    )

