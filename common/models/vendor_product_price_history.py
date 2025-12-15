"""
供应商产品价格历史模型
记录供应商产品价格的变更历史
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func
from common.database import Base
import uuid


class VendorProductPriceHistory(Base):
    """供应商产品价格历史模型"""
    __tablename__ = "vendor_product_price_history"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vendor_product_id = Column(String(36), ForeignKey("vendor_products.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 价格信息（双价格）
    old_price_cny = Column(Numeric(18, 2), nullable=True)  # 旧价格（人民币）
    old_price_idr = Column(Numeric(18, 2), nullable=True)  # 旧价格（印尼盾）
    new_price_cny = Column(Numeric(18, 2), nullable=True)  # 新价格（人民币）
    new_price_idr = Column(Numeric(18, 2), nullable=True)  # 新价格（印尼盾）
    
    # 生效时间
    effective_from = Column(DateTime, nullable=False, index=True)  # 生效开始时间
    effective_to = Column(DateTime, nullable=True, index=True)  # 生效结束时间（如果为None表示当前有效）
    
    # 变更信息
    change_reason = Column(Text, nullable=True)  # 变更原因
    changed_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # 变更人
    
    # 元数据
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # 检查约束
    __table_args__ = (
        {'extend_existing': True},
    )
