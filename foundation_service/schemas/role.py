"""
角色相关模式
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RoleCreateRequest(BaseModel):
    """创建角色请求"""
    code: str = Field(..., min_length=1, max_length=50, description="角色编码（唯一）")
    name: str = Field(..., min_length=1, max_length=255, description="角色名称")
    description: Optional[str] = Field(None, description="角色描述")


class RoleUpdateRequest(BaseModel):
    """更新角色请求"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class RoleResponse(BaseModel):
    """角色响应"""
    id: str
    code: str
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

