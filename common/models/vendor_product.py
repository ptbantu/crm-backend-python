"""
供应商产品关联模型（共享定义）
所有微服务共享的供应商产品关联表结构定义
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func
from common.database import Base
import uuid


class VendorProduct(Base):
    """供应商产品关联模型（共享定义，多对多关系）"""
    __tablename__ = "vendor_products"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # 注意：organizations 表在 foundation_service 的数据库中，不能使用外键约束
    organization_id = Column(String(36), nullable=False, index=True)  # 跨服务，无外键
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 供应商属性
    is_primary = Column(Boolean, default=False, nullable=False, index=True)  # 是否主要供应商
    priority = Column(Integer, default=0, nullable=False)  # 优先级（数字越小优先级越高）
    
    # 该组织提供该服务的成本价（多货币）
    cost_price_idr = Column(Numeric(18, 2), nullable=True)
    cost_price_cny = Column(Numeric(18, 2), nullable=True)
    exchange_rate = Column(Numeric(18, 9), default=2000, nullable=True)
    
    # 订购限制
    min_quantity = Column(Integer, default=1, nullable=False)  # 最小订购量
    max_quantity = Column(Integer, nullable=True)  # 最大订购量
    lead_time_days = Column(Integer, nullable=True)  # 交货期（天数）
    processing_days = Column(Integer, nullable=True)  # 该组织处理该服务的天数
    
    # 可用性管理
    is_available = Column(Boolean, default=True, nullable=False, index=True)  # 是否可用
    availability_notes = Column(Text, nullable=True)  # 可用性说明
    available_from = Column(DateTime, nullable=True)  # 可用开始时间
    available_to = Column(DateTime, nullable=True)  # 可用结束时间
    
    # 财务相关（用于报账）
    account_code = Column(String(100), nullable=True)  # 会计科目代码
    cost_center = Column(String(100), nullable=True)  # 成本中心
    expense_category = Column(String(100), nullable=True)  # 费用类别
    
    # 元数据
    notes = Column(Text, nullable=True)  # 备注
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 检查约束
    __table_args__ = (
        {'extend_existing': True},
    )

