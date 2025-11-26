"""
产品价格历史模型（共享定义）
所有微服务共享的产品价格历史表结构定义
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func
from common.database import Base
import uuid


class ProductPriceHistory(Base):
    """产品价格历史模型（共享定义，审计和趋势分析）"""
    __tablename__ = "product_price_history"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    # 注意：organizations 表在 foundation_service 的数据库中，不能使用外键约束
    organization_id = Column(String(36), nullable=True, index=True)  # 如果是组织特定价格（跨服务，无外键）
    
    # 价格信息
    price_type = Column(String(50), nullable=False, index=True)  # cost, channel, direct, list
    currency = Column(String(10), nullable=False, index=True)  # IDR, CNY
    old_price = Column(Numeric(18, 2), nullable=True)
    new_price = Column(Numeric(18, 2), nullable=True)
    
    # 变更信息
    change_reason = Column(Text, nullable=True)  # 变更原因
    effective_from = Column(DateTime, nullable=False, index=True)  # 生效时间
    effective_to = Column(DateTime, nullable=True, index=True)  # 失效时间（NULL表示当前有效）
    changed_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, server_default=func.now())

