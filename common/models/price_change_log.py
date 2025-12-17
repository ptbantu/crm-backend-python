"""
价格变更日志模型（共享定义）
所有微服务共享的价格变更日志表结构定义
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Numeric, Integer, JSON, CheckConstraint
from sqlalchemy.sql import func
from common.database import Base
import uuid


class PriceChangeLog(Base):
    """价格变更日志模型（共享定义，用于审计和追溯）"""
    __tablename__ = "price_change_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    price_id = Column(String(36), ForeignKey("product_prices.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # 变更信息
    change_type = Column(String(50), nullable=False, index=True, comment="变更类型：create, update, delete, activate, deactivate")
    price_type = Column(String(50), nullable=False, index=True, comment="价格类型：cost, channel, direct, list")
    currency = Column(String(10), nullable=False, comment="货币：IDR, CNY, USD, EUR")
    
    # 价格变更前后
    old_price = Column(Numeric(18, 2), nullable=True, comment="变更前价格")
    new_price = Column(Numeric(18, 2), nullable=True, comment="变更后价格")
    price_change_amount = Column(Numeric(18, 2), nullable=True, comment="价格变动金额")
    price_change_percentage = Column(Numeric(5, 2), nullable=True, comment="价格变动百分比")
    
    # 生效时间变更
    old_effective_from = Column(DateTime, nullable=True, comment="变更前生效时间")
    new_effective_from = Column(DateTime, nullable=True, comment="变更后生效时间")
    old_effective_to = Column(DateTime, nullable=True, comment="变更前失效时间")
    new_effective_to = Column(DateTime, nullable=True, comment="变更后失效时间")
    
    # 变更原因和操作人
    change_reason = Column(Text, nullable=True, comment="变更原因")
    changed_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    changed_at = Column(DateTime, nullable=False, server_default=func.now(), index=True, comment="变更时间")
    
    # 影响分析
    affected_orders_count = Column(Integer, nullable=True, comment="受影响订单数量（预估）")
    impact_analysis = Column(JSON, nullable=True, comment="影响分析（JSON格式）")
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    
    # 约束
    __table_args__ = (
        CheckConstraint("change_type IN ('create', 'update', 'delete', 'activate', 'deactivate')", name="chk_price_change_logs_change_type"),
        CheckConstraint("price_type IN ('cost', 'channel', 'direct', 'list')", name="chk_price_change_logs_price_type"),
        CheckConstraint("currency IN ('IDR', 'CNY', 'USD', 'EUR')", name="chk_price_change_logs_currency"),
        {'extend_existing': True},
    )
