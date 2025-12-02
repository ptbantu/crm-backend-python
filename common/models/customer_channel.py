"""
客户渠道模型（共享定义）
所有微服务共享的客户渠道表结构定义
注意：实际表在 service_management 服务中，这里仅作为占位符模型
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from common.database import Base
import uuid


class CustomerChannel(Base):
    """客户渠道模型（占位符，不定义外键关系）"""
    __tablename__ = "customer_channels"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    display_order = Column(String(36), nullable=True, default="0")
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 检查约束
    __table_args__ = (
        {'extend_existing': True},
    )

