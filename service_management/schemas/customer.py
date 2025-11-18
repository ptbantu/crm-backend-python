"""
客户相关模式
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CustomerSourceResponse(BaseModel):
    """客户来源响应"""
    id: str
    code: str
    name: str
    description: Optional[str] = None
    display_order: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CustomerChannelResponse(BaseModel):
    """客户渠道响应"""
    id: str
    code: str
    name: str
    description: Optional[str] = None
    display_order: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CustomerCreateRequest(BaseModel):
    """创建客户请求"""
    name: str = Field(..., min_length=1, max_length=255, description="客户名称")
    code: Optional[str] = Field(None, max_length=100, description="客户编码（唯一）")
    customer_type: str = Field(default="individual", description="客户类型：individual, organization")
    customer_source_type: str = Field(default="own", description="客户来源类型：own, agent")
    
    # 关联关系
    parent_customer_id: Optional[str] = Field(None, description="父客户ID")
    owner_user_id: Optional[str] = Field(None, description="内部客户所有者ID")
    agent_user_id: Optional[str] = Field(None, description="渠道客户用户ID")
    agent_id: Optional[str] = Field(None, description="渠道客户组织ID")
    source_id: Optional[str] = Field(None, description="客户来源ID")
    channel_id: Optional[str] = Field(None, description="客户渠道ID")
    
    # 业务字段
    level: Optional[str] = Field(None, max_length=50, description="客户等级")
    industry: Optional[str] = Field(None, max_length=255, description="行业")
    description: Optional[str] = Field(None, description="描述")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签")
    is_locked: Optional[bool] = Field(default=False, description="是否锁定")
    
    # 外部系统字段
    id_external: Optional[str] = Field(None, max_length=255, description="外部系统ID")
    customer_requirements: Optional[str] = Field(None, description="客户需求")


class CustomerUpdateRequest(BaseModel):
    """更新客户请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, max_length=100)
    customer_type: Optional[str] = None
    customer_source_type: Optional[str] = None
    
    # 关联关系
    parent_customer_id: Optional[str] = None
    owner_user_id: Optional[str] = None
    agent_user_id: Optional[str] = None
    agent_id: Optional[str] = None
    source_id: Optional[str] = None
    channel_id: Optional[str] = None
    
    # 业务字段
    level: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_locked: Optional[bool] = None
    customer_requirements: Optional[str] = None


class CustomerResponse(BaseModel):
    """客户响应"""
    id: str
    name: str
    code: Optional[str] = None
    customer_type: str
    customer_source_type: str
    
    # 关联关系
    parent_customer_id: Optional[str] = None
    parent_customer_name: Optional[str] = None
    owner_user_id: Optional[str] = None
    owner_user_name: Optional[str] = None
    agent_user_id: Optional[str] = None
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    source_id: Optional[str] = None
    source_name: Optional[str] = None
    channel_id: Optional[str] = None
    channel_name: Optional[str] = None
    
    # 业务字段
    level: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_locked: Optional[bool] = None
    customer_requirements: Optional[str] = None
    
    # 时间戳
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    """客户列表响应"""
    items: List[CustomerResponse]
    total: int
    page: int
    size: int

