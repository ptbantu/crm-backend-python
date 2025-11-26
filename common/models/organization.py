"""
组织模型（共享定义）
所有微服务共享的组织表结构定义
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, Date, Integer, Numeric, JSON
from sqlalchemy.sql import func
from common.database import Base
import uuid


class Organization(Base):
    """组织模型（共享定义）"""
    __tablename__ = "organizations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(Text, nullable=False)
    code = Column(String(255), unique=True, nullable=True, index=True)
    external_id = Column(String(255), unique=True, nullable=True)
    organization_type = Column(String(50), nullable=False, index=True)  # internal: BANTU内部组织, vendor: 交付组织(做单组织), agent: 外部代理(销售组织)
    # parent_id 字段已废弃，不再支持组织树形结构
    # parent_id = Column(String(36), ForeignKey("organizations.id"), nullable=True, index=True)
    
    # 基本信息
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    logo_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    
    # 地址信息
    street = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state_province = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country_region = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    country_code = Column(String(10), nullable=True)
    
    # 公司属性
    company_size = Column(String(50), nullable=True)  # micro, small, medium, large, enterprise
    company_nature = Column(String(50), nullable=True)  # state_owned, private, foreign, etc.
    company_type = Column(String(50), nullable=True)  # limited, unlimited, partnership, etc.
    industry = Column(String(100), nullable=True)
    industry_code = Column(String(50), nullable=True)
    sub_industry = Column(String(100), nullable=True)
    business_scope = Column(Text, nullable=True)
    
    # 工商信息
    registration_number = Column(String(100), nullable=True)
    tax_id = Column(String(100), nullable=True)
    legal_representative = Column(String(255), nullable=True)
    established_date = Column(Date, nullable=True)
    registered_capital = Column(Numeric(18, 2), nullable=True)
    registered_capital_currency = Column(String(10), nullable=True, default="CNY")
    company_status = Column(String(50), nullable=True)  # normal, cancelled, etc.
    
    # 财务信息
    annual_revenue = Column(Numeric(18, 2), nullable=True)
    annual_revenue_currency = Column(String(10), nullable=True, default="CNY")
    employee_count = Column(Integer, nullable=True)
    revenue_year = Column(Integer, nullable=True)
    
    # 认证信息
    certifications = Column(JSON, nullable=True, default=list)
    business_license_url = Column(String(500), nullable=True)
    tax_certificate_url = Column(String(500), nullable=True)
    
    # 状态控制
    is_active = Column(Boolean, nullable=False, default=True, index=True, comment="是否激活")
    is_locked = Column(Boolean, nullable=False, default=False, index=True, comment="是否锁定：False=合作（默认），True=锁定（断开合作）")
    is_verified = Column(Boolean, nullable=True, default=False)
    verified_at = Column(DateTime, nullable=True)
    verified_by = Column(String(36), nullable=True)
    
    # 时间字段
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

