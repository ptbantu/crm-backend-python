"""
产品分类模型（共享定义）
所有微服务共享的产品分类表结构定义
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from common.database import Base
import uuid


class ProductCategory(Base):
    """产品分类模型（共享定义）"""
    __tablename__ = "product_categories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    parent_id = Column(String(36), ForeignKey("product_categories.id", ondelete="SET NULL"), nullable=True, index=True)
    display_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 检查约束
    __table_args__ = (
        {'extend_existing': True},
    )

