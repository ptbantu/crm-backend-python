"""
组织相关模式
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


class OrganizationCreateRequest(BaseModel):
    """创建组织请求"""
    name: str = Field(..., min_length=1, description="组织名称")
    code: Optional[str] = Field(None, description="组织编码（唯一）")
    organization_type: str = Field(..., pattern="^(internal|vendor|agent)$", description="组织类型")
    parent_id: Optional[str] = Field(None, description="父组织ID")
    
    # 基本信息
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None
    
    # 地址信息
    street: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    
    # 公司属性
    company_size: Optional[str] = Field(None, pattern="^(micro|small|medium|large|enterprise)$")
    company_nature: Optional[str] = None
    company_type: Optional[str] = None
    industry: Optional[str] = None
    industry_code: Optional[str] = None
    sub_industry: Optional[str] = None
    business_scope: Optional[str] = None
    
    # 工商信息
    registration_number: Optional[str] = None
    tax_id: Optional[str] = None
    legal_representative: Optional[str] = None
    established_date: Optional[date] = None
    registered_capital: Optional[Decimal] = None
    registered_capital_currency: Optional[str] = Field(default="CNY")
    company_status: Optional[str] = None
    
    # 财务信息
    annual_revenue: Optional[Decimal] = None
    annual_revenue_currency: Optional[str] = Field(default="CNY")
    employee_count: Optional[int] = None
    revenue_year: Optional[int] = None
    
    # 认证信息
    certifications: Optional[List[str]] = Field(default_factory=list)
    business_license_url: Optional[str] = None
    tax_certificate_url: Optional[str] = None
    
    is_active: bool = Field(default=True)


class OrganizationUpdateRequest(BaseModel):
    """更新组织请求"""
    name: Optional[str] = None
    code: Optional[str] = None
    parent_id: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None
    # ... 其他字段类似
    is_active: Optional[bool] = None
    is_locked: Optional[bool] = None


class OrganizationResponse(BaseModel):
    """组织响应"""
    id: str
    name: str
    code: Optional[str]
    organization_type: str
    parent_id: Optional[str]
    parent_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    logo_url: Optional[str]
    description: Optional[str]
    is_active: bool
    is_locked: bool
    is_verified: bool
    children_count: int = 0
    employees_count: int = 0
    created_at: datetime
    updated_at: datetime

