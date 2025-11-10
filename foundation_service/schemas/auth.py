"""
认证相关模式
"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """登录请求"""
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=1, description="密码")


class LoginResponse(BaseModel):
    """登录响应"""
    token: str
    refresh_token: str
    user: "UserInfo"
    expires_in: int = Field(default=86400000, description="过期时间（毫秒）")


class UserInfo(BaseModel):
    """用户信息"""
    id: str
    username: str
    email: Optional[str]
    display_name: Optional[str]
    primary_organization_id: Optional[str]
    primary_organization_name: Optional[str]
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)


LoginResponse.model_rebuild()

