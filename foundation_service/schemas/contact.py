"""
联系人相关模式
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ContactCreateRequest(BaseModel):
    """创建联系人请求"""
    customer_id: str = Field(..., description="客户ID")
    first_name: str = Field(..., min_length=1, max_length=255, description="名")
    last_name: str = Field(..., min_length=1, max_length=255, description="姓")
    
    # 联系方式
    email: Optional[str] = Field(None, max_length=255, description="邮箱")
    phone: Optional[str] = Field(None, max_length=50, description="电话")
    mobile: Optional[str] = Field(None, max_length=50, description="手机")
    wechat_id: Optional[str] = Field(None, max_length=100, description="微信ID")
    
    # 职位和角色
    position: Optional[str] = Field(None, max_length=255, description="职位")
    department: Optional[str] = Field(None, max_length=255, description="部门")
    contact_role: Optional[str] = Field(None, max_length=100, description="联系人角色")
    is_primary: bool = Field(default=False, description="是否主要联系人")
    is_decision_maker: bool = Field(default=False, description="是否决策人")
    
    # 地址信息
    address: Optional[str] = Field(None, description="地址")
    city: Optional[str] = Field(None, max_length=100, description="城市")
    province: Optional[str] = Field(None, max_length=100, description="省份")
    country: Optional[str] = Field(None, max_length=100, description="国家")
    postal_code: Optional[str] = Field(None, max_length=20, description="邮编")
    
    # 偏好设置
    preferred_contact_method: Optional[str] = Field(None, max_length=50, description="首选联系方式")
    
    # 状态
    is_active: bool = Field(default=True, description="是否激活")
    
    # 备注
    notes: Optional[str] = Field(None, description="备注")


class ContactUpdateRequest(BaseModel):
    """更新联系人请求"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=255)
    last_name: Optional[str] = Field(None, min_length=1, max_length=255)
    
    # 联系方式
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    wechat_id: Optional[str] = None
    
    # 职位和角色
    position: Optional[str] = None
    department: Optional[str] = None
    contact_role: Optional[str] = None
    is_primary: Optional[bool] = None
    is_decision_maker: Optional[bool] = None
    
    # 地址信息
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    
    # 偏好设置
    preferred_contact_method: Optional[str] = None
    
    # 状态
    is_active: Optional[bool] = None
    
    # 备注
    notes: Optional[str] = None


class ContactResponse(BaseModel):
    """联系人响应"""
    id: str
    customer_id: str
    customer_name: Optional[str] = None
    first_name: str
    last_name: str
    full_name: Optional[str] = None
    
    # 联系方式
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    wechat_id: Optional[str] = None
    
    # 职位和角色
    position: Optional[str] = None
    department: Optional[str] = None
    contact_role: Optional[str] = None
    is_primary: bool
    is_decision_maker: bool
    
    # 地址信息
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    
    # 偏好设置
    preferred_contact_method: Optional[str] = None
    
    # 状态
    is_active: bool
    
    # 备注
    notes: Optional[str] = None
    
    # 时间戳
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ContactListResponse(BaseModel):
    """联系人列表响应"""
    items: List[ContactResponse]
    total: int
    page: int
    size: int

