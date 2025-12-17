"""
产品价格模型（共享定义）
所有微服务共享的产品价格表结构定义
一条记录包含一个产品的所有销售价格（渠道价、直客价、列表价，每种价格支持IDR和CNY）
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Numeric, CheckConstraint
from sqlalchemy.sql import func
from common.database import Base
import uuid


class ProductPrice(Base):
    """产品价格模型（共享定义，一条记录包含所有价格类型和货币）"""
    __tablename__ = "product_prices"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    # 注意：organizations 表在 foundation_service 的数据库中，不能使用外键约束
    organization_id = Column(String(36), nullable=True, index=True)  # NULL 表示通用价格（跨服务，无外键）
    
    # 渠道价（Channel Price）
    price_channel_idr = Column(Numeric(18, 2), nullable=True, comment="渠道价-IDR")
    price_channel_cny = Column(Numeric(18, 2), nullable=True, comment="渠道价-CNY")
    
    # 直客价（Direct Price）
    price_direct_idr = Column(Numeric(18, 2), nullable=True, comment="直客价-IDR")
    price_direct_cny = Column(Numeric(18, 2), nullable=True, comment="直客价-CNY")
    
    # 列表价（List Price）
    price_list_idr = Column(Numeric(18, 2), nullable=True, comment="列表价-IDR")
    price_list_cny = Column(Numeric(18, 2), nullable=True, comment="列表价-CNY")
    
    # 成本价（Cost Price）
    price_cost_idr = Column(Numeric(18, 2), nullable=True, comment="成本价-IDR")
    price_cost_cny = Column(Numeric(18, 2), nullable=True, comment="成本价-CNY")
    
    # 汇率（用于计算）
    exchange_rate = Column(Numeric(18, 9), nullable=True, comment="汇率")
    
    # 价格生效时间
    effective_from = Column(DateTime, nullable=False, server_default=func.now(), index=True, comment="生效时间")
    effective_to = Column(DateTime, nullable=True, index=True, comment="失效时间（NULL表示当前有效）")
    
    # 价格来源和审核
    source = Column(String(50), nullable=True, comment="价格来源：manual, import, contract")
    is_approved = Column(Boolean, default=False, nullable=False, comment="是否已审核")
    approved_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="审核人ID")
    approved_at = Column(DateTime, nullable=True, comment="审核时间")
    
    # 变更信息
    change_reason = Column(Text, nullable=True, comment="变更原因")
    changed_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="变更人ID")
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 约束
    __table_args__ = (
        CheckConstraint("price_channel_idr IS NULL OR price_channel_idr >= 0", name="chk_product_prices_channel_idr_nonneg"),
        CheckConstraint("price_channel_cny IS NULL OR price_channel_cny >= 0", name="chk_product_prices_channel_cny_nonneg"),
        CheckConstraint("price_direct_idr IS NULL OR price_direct_idr >= 0", name="chk_product_prices_direct_idr_nonneg"),
        CheckConstraint("price_direct_cny IS NULL OR price_direct_cny >= 0", name="chk_product_prices_direct_cny_nonneg"),
        CheckConstraint("price_list_idr IS NULL OR price_list_idr >= 0", name="chk_product_prices_list_idr_nonneg"),
        CheckConstraint("price_list_cny IS NULL OR price_list_cny >= 0", name="chk_product_prices_list_cny_nonneg"),
        CheckConstraint("price_cost_idr IS NULL OR price_cost_idr >= 0", name="chk_product_prices_cost_idr_nonneg"),
        CheckConstraint("price_cost_cny IS NULL OR price_cost_cny >= 0", name="chk_product_prices_cost_cny_nonneg"),
        {'extend_existing': True},
    )

