"""
汇率历史模型（共享定义）
所有微服务共享的汇率历史表结构定义
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Numeric, CheckConstraint
from sqlalchemy.sql import func
from common.database import Base
import uuid


class ExchangeRateHistory(Base):
    """汇率历史模型（共享定义，支持多货币汇率管理）"""
    __tablename__ = "exchange_rate_history"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 汇率信息
    from_currency = Column(String(10), nullable=False, index=True, comment="源货币：IDR, CNY, USD, EUR")
    to_currency = Column(String(10), nullable=False, index=True, comment="目标货币：IDR, CNY, USD, EUR")
    rate = Column(Numeric(18, 9), nullable=False, comment="汇率")
    
    # 生效时间
    effective_from = Column(DateTime, nullable=False, server_default=func.now(), index=True, comment="生效时间")
    effective_to = Column(DateTime, nullable=True, index=True, comment="失效时间（NULL表示当前有效）")
    
    # 汇率来源和审核
    source = Column(String(50), nullable=True, comment="汇率来源：manual, api, import")
    source_reference = Column(String(255), nullable=True, comment="来源参考（如API提供商）")
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
        CheckConstraint("rate > 0", name="chk_exchange_rate_history_rate_positive"),
        CheckConstraint("from_currency != to_currency", name="chk_exchange_rate_history_currencies_different"),
        CheckConstraint("from_currency IN ('IDR', 'CNY', 'USD', 'EUR')", name="chk_exchange_rate_history_from_currency"),
        CheckConstraint("to_currency IN ('IDR', 'CNY', 'USD', 'EUR')", name="chk_exchange_rate_history_to_currency"),
        {'extend_existing': True},
    )
