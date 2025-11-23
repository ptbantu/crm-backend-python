"""
用户相关模式
"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


class UserCreateRequest(BaseModel):
    """创建用户请求（邮箱是唯一标识，用户名可选）"""
    organization_id: str = Field(..., description="组织ID")
    username: Optional[str] = Field(None, max_length=50, description="用户账号（可选，支持中文）")
    email: EmailStr = Field(..., description="邮箱（必填，全局唯一，作为唯一标识）")
    password: str = Field(..., min_length=8, description="密码（至少8位，包含字母和数字）")
    role_ids: List[str] = Field(..., min_length=1, description="角色ID列表（至少一个角色）")


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


class UserResetPasswordRequest(BaseModel):
    """重置密码请求"""
    new_password: str = Field(..., min_length=8, description="新密码（至少8位，包含字母和数字）")


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
    is_locked: bool = Field(False, description="是否锁定：False=正常（默认），True=锁定（禁用登录）")
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

