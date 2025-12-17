"""
客户等级价格模型（共享定义）
所有微服务共享的客户等级价格表结构定义
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Numeric, CheckConstraint
from sqlalchemy.sql import func
from common.database import Base
import uuid


class CustomerLevelPrice(Base):
    """客户等级价格模型（共享定义，支持不同客户等级的价格）"""
    __tablename__ = "customer_level_prices"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_level_code = Column(String(50), ForeignKey("customer_levels.code", ondelete="RESTRICT"), nullable=False, index=True)
    
    # 价格信息
    currency = Column(String(10), nullable=False, index=True, comment="货币：IDR, CNY, USD, EUR")
    amount = Column(Numeric(18, 2), nullable=False, comment="价格金额")
    
    # 生效时间
    effective_from = Column(DateTime, nullable=False, server_default=func.now(), index=True, comment="生效时间")
    effective_to = Column(DateTime, nullable=True, index=True, comment="失效时间（NULL表示当前有效）")
    
    # 价格来源和审核
    source = Column(String(50), nullable=True, comment="价格来源：manual, import, contract")
    is_approved = Column(Boolean, default=False, nullable=False, comment="是否已审核")
    approved_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime, nullable=True, comment="审核时间")
    
    # 变更信息
    change_reason = Column(Text, nullable=True, comment="变更原因")
    changed_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 约束
    __table_args__ = (
        CheckConstraint("amount >= 0", name="chk_customer_level_prices_amount_nonneg"),
        CheckConstraint("currency IN ('IDR', 'CNY', 'USD', 'EUR')", name="chk_customer_level_prices_currency"),
        {'extend_existing': True},
    )
