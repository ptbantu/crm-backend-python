"""
用户相关模式
"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


class UserCreateRequest(BaseModel):
    """创建用户请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱（全局唯一）")
    phone: Optional[str] = Field(None, description="手机号")
    display_name: Optional[str] = Field(None, description="显示名称")
    password: str = Field(..., min_length=8, description="密码（至少8位）")
    avatar_url: Optional[str] = Field(None, description="头像地址")
    bio: Optional[str] = Field(None, description="个人简介")
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$", description="性别")
    address: Optional[str] = Field(None, description="住址")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    whatsapp: Optional[str] = Field(None, description="WhatsApp 号码")
    wechat: Optional[str] = Field(None, description="微信号")
    organization_id: str = Field(..., description="主要组织ID")
    role_ids: List[str] = Field(default_factory=list, description="角色ID列表")
    is_active: bool = Field(default=True, description="是否激活")


class UserUpdateRequest(BaseModel):
    """更新用户请求"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    address: Optional[str] = None
    contact_phone: Optional[str] = None
    whatsapp: Optional[str] = None
    wechat: Optional[str] = None
    role_ids: Optional[List[str]] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """用户响应"""
    id: str
    username: str
    email: Optional[str]
    phone: Optional[str]
    display_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    gender: Optional[str]
    address: Optional[str]
    contact_phone: Optional[str]
    whatsapp: Optional[str]
    wechat: Optional[str]
    primary_organization_id: Optional[str]
    primary_organization_name: Optional[str]
    is_active: bool
    last_login_at: Optional[datetime]
    roles: List["RoleInfo"] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class RoleInfo(BaseModel):
    """角色信息"""
    id: str
    code: str
    name: str


class UserListResponse(BaseModel):
    """用户列表响应"""
    records: List[UserResponse]
    total: int
    size: int
    current: int
    pages: int


UserResponse.model_rebuild()

