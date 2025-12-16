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
    code: Optional[str] = Field(None, description="组织编码（唯一，如果不提供则自动生成：type+序列号+年月日）")
    organization_type: str = Field(..., pattern="^(internal|vendor|agent)$", description="组织类型: internal(BANTU内部组织), vendor(交付组织/做单组织), agent(外部代理/销售组织)")
    # parent_id 字段已废弃，不再支持组织树形结构
    
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
    # parent_id 字段已废弃，不再支持组织树形结构
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None
    # ... 其他字段类似
    is_active: Optional[bool] = None
    is_locked: Optional[bool] = None


class OrganizationDomainInfo(BaseModel):
    """组织领域信息（简化）"""
    id: str
    code: str
    name_zh: str
    name_id: str
    is_primary: bool
    
    class Config:
        from_attributes = True


class OrganizationResponse(BaseModel):
    """组织响应"""
    id: str
    name: str
    code: Optional[str] = None
    external_id: Optional[str] = None
    organization_type: str
    is_locked: bool = Field(False, description="是否锁定：False=合作（默认），True=锁定（断开合作）")
    domains: Optional[List[OrganizationDomainInfo]] = Field(default_factory=list, description="组织领域列表")
    
    # 基本信息
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None
    
    # 地址信息
    street: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country_region: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    
    # 公司属性
    company_size: Optional[str] = None
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
    
    # 状态控制
    is_active: bool = True
    is_verified: bool = False
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    
    # 统计信息
    employees_count: int = 0
    
    # 时间字段
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrganizationListResponse(BaseModel):
    """组织列表响应"""
    records: List[OrganizationResponse]
    total: int
    size: int
    current: int
    pages: int


# OrganizationTreeNode 已废弃，不再支持组织树形结构
# class OrganizationTreeNode(BaseModel):
#     """组织树节点"""
#     id: str
#     name: str
#     code: Optional[str]
#     organization_type: str
#     is_active: bool
#     is_locked: bool
#     employees_count: int = 0
#     children: List["OrganizationTreeNode"] = Field(default_factory=list)
# 
# OrganizationTreeNode.model_rebuild()

