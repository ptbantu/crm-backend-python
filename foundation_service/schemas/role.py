"""
角色相关模式
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from foundation_service.schemas.permission import PermissionInfo


class RoleCreateRequest(BaseModel):
    """创建角色请求"""
    code: str = Field(..., min_length=1, max_length=50, description="角色编码（唯一）")
    name: str = Field(..., min_length=1, max_length=255, description="角色名称（英文，保留兼容）")
    name_zh: Optional[str] = Field(None, min_length=1, max_length=255, description="角色名称（中文）")
    name_id: Optional[str] = Field(None, min_length=1, max_length=255, description="角色名称（印尼语）")
    description: Optional[str] = Field(None, description="角色描述（英文，保留兼容）")
    description_zh: Optional[str] = Field(None, description="角色描述（中文）")
    description_id: Optional[str] = Field(None, description="角色描述（印尼语）")


class RoleUpdateRequest(BaseModel):
    """更新角色请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="角色名称（英文，保留兼容）")
    name_zh: Optional[str] = Field(None, min_length=1, max_length=255, description="角色名称（中文）")
    name_id: Optional[str] = Field(None, min_length=1, max_length=255, description="角色名称（印尼语）")
    description: Optional[str] = Field(None, description="角色描述（英文，保留兼容）")
    description_zh: Optional[str] = Field(None, description="角色描述（中文）")
    description_id: Optional[str] = Field(None, description="角色描述（印尼语）")


class RoleResponse(BaseModel):
    """角色响应"""
    id: str
    code: str
    name: str
    name_zh: Optional[str]
    name_id: Optional[str]
    description: Optional[str]
    description_zh: Optional[str]
    description_id: Optional[str]
    permissions: List[PermissionInfo] = Field(default_factory=list, description="角色拥有的权限列表")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

