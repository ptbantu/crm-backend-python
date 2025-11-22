"""
组织领域相关模式
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class OrganizationDomainCreateRequest(BaseModel):
    """创建组织领域请求"""
    code: str = Field(..., min_length=1, max_length=100, description="领域代码（唯一）")
    name_zh: str = Field(..., min_length=1, description="领域名称（中文）")
    name_id: str = Field(..., min_length=1, description="领域名称（印尼语）")
    description_zh: Optional[str] = Field(None, description="领域描述（中文）")
    description_id: Optional[str] = Field(None, description="领域描述（印尼语）")
    display_order: int = Field(0, description="显示顺序")
    is_active: bool = Field(True, description="是否激活")


class OrganizationDomainUpdateRequest(BaseModel):
    """更新组织领域请求"""
    name_zh: Optional[str] = None
    name_id: Optional[str] = None
    description_zh: Optional[str] = None
    description_id: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class OrganizationDomainResponse(BaseModel):
    """组织领域响应"""
    id: str
    code: str
    name_zh: str
    name_id: str
    description_zh: Optional[str]
    description_id: Optional[str]
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrganizationDomainRelationResponse(BaseModel):
    """组织领域关联响应"""
    id: str
    organization_id: str
    domain_id: str
    domain_code: str
    domain_name_zh: str
    domain_name_id: str
    is_primary: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

