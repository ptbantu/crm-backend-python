"""
组织领域模型
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer
from sqlalchemy.sql import func
from foundation_service.database import Base
import uuid


class OrganizationDomain(Base):
    """组织领域模型"""
    __tablename__ = "organization_domains"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(100), unique=True, nullable=False, index=True, comment="领域代码（唯一）")
    name_zh = Column(String(255), nullable=False, comment="领域名称（中文）")
    name_id = Column(String(255), nullable=False, comment="领域名称（印尼语）")
    description_zh = Column(Text, nullable=True, comment="领域描述（中文）")
    description_id = Column(Text, nullable=True, comment="领域描述（印尼语）")
    display_order = Column(Integer, default=0, nullable=False, comment="显示顺序")
    is_active = Column(Boolean, nullable=False, default=True, index=True, comment="是否激活")
    
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        {"comment": "组织领域表"},
    )


class OrganizationDomainRelation(Base):
    """组织领域关联模型"""
    __tablename__ = "organization_domain_relations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), nullable=False, index=True, comment="组织ID")
    domain_id = Column(String(36), nullable=False, index=True, comment="领域ID")
    is_primary = Column(Boolean, nullable=False, default=False, comment="是否主要领域")
    
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        {"comment": "组织领域关联表"},
    )

