"""
客户相关模式
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class CustomerSourceResponse(BaseModel):
    """客户来源响应"""
    id: str
    code: Optional[str] = None
    name: Optional[str] = None  # 保留旧字段以兼容
    name_zh: Optional[str] = None  # 中文名称
    name_id: Optional[str] = None  # 印尼语名称
    description: Optional[str] = None
    display_order: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class IndustryResponse(BaseModel):
    """行业响应"""
    id: str
    code: str
    name_zh: str
    name_id: str
    sort_order: int
    is_active: bool
    description_zh: Optional[str] = None
    description_id: Optional[str] = None
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
    code: Optional[str] = Field(None, max_length=100, description="客户编码（唯一，如果不提供则自动生成）")
    customer_type: Literal['individual', 'organization'] = Field(default="individual", description="客户类型：individual (个人), organization (组织)")
    # customer_source_type 已废弃，统一使用 source_id
    customer_source_type: Optional[str] = Field(None, description="客户来源类型（已废弃，请使用 source_id）")
    
    # 关联关系
    parent_customer_id: Optional[str] = Field(None, description="父客户ID")
    owner_user_id: Optional[str] = Field(None, description="内部客户所有者ID")
    agent_user_id: Optional[str] = Field(None, description="渠道客户用户ID")
    agent_id: Optional[str] = Field(None, description="渠道客户组织ID")
    source_id: str = Field(..., description="客户来源ID（必填）")
    channel_id: Optional[str] = Field(None, description="客户渠道ID")
    
    # 业务字段
    level: Optional[str] = Field(None, max_length=50, description="客户等级（关联customer_levels.code）")
    industry_id: Optional[str] = Field(None, description="行业ID（关联industries.id）")
    description: Optional[str] = Field(None, description="描述")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签")
    is_locked: Optional[bool] = Field(default=False, description="是否锁定")
    
    # 外部系统字段
    id_external: Optional[str] = Field(None, max_length=255, description="外部系统ID")
    customer_requirements: Optional[str] = Field(None, description="客户需求")
    
    # 数据隔离字段（由后端自动设置，前端不传）
    organization_id: Optional[str] = Field(None, description="组织ID（数据隔离，由后端自动设置）")


class CustomerUpdateRequest(BaseModel):
    """更新客户请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, max_length=100)
    customer_type: Optional[Literal['individual', 'organization']] = None
    # customer_source_type 已废弃，统一使用 source_id
    customer_source_type: Optional[str] = Field(None, description="客户来源类型（已废弃，请使用 source_id）")
    
    # 关联关系
    parent_customer_id: Optional[str] = None
    owner_user_id: Optional[str] = None
    agent_user_id: Optional[str] = None
    agent_id: Optional[str] = None
    source_id: Optional[str] = Field(None, description="客户来源ID（可选，编辑时可以不修改）")
    channel_id: Optional[str] = None
    
    # 业务字段
    level: Optional[str] = None
    industry_id: Optional[str] = None
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
    level_name_zh: Optional[str] = None  # 客户等级名称（中文）
    level_name_id: Optional[str] = None  # 客户等级名称（印尼语）
    industry_id: Optional[str] = None
    industry_name_zh: Optional[str] = None  # 行业名称（中文）
    industry_name_id: Optional[str] = None  # 行业名称（印尼语）
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_locked: Optional[bool] = None
    customer_requirements: Optional[str] = None
    
    # 时间戳
    created_at: datetime
    updated_at: datetime
    last_follow_up_at: Optional[datetime] = None
    next_follow_up_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    """客户列表响应"""
    items: List[CustomerResponse]
    total: int
    page: int
    size: int

