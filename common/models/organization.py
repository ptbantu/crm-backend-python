"""
组织模型（共享定义）
所有微服务共享的组织表结构定义
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from common.database import Base


class Organization(Base):
    """组织模型（共享定义）"""
    __tablename__ = "organizations"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(100), nullable=True, unique=True, index=True)
    organization_type = Column(String(50), nullable=False, index=True, comment="组织类型: internal(BANTU内部组织), vendor(交付组织/做单组织), agent(外部代理/销售组织)")
    description = Column(Text, nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_locked = Column(Boolean, nullable=False, default=False, index=True, comment="是否锁定：False=合作（默认），True=锁定（断开合作）")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

