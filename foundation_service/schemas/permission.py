"""
权限相关模式
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PermissionCreateRequest(BaseModel):
    """创建权限请求"""
    code: str = Field(..., min_length=1, max_length=100, description="权限编码（唯一，如：user.create）")
    name_zh: str = Field(..., min_length=1, max_length=255, description="权限名称（中文）")
    name_id: str = Field(..., min_length=1, max_length=255, description="权限名称（印尼语）")
    description_zh: Optional[str] = Field(None, description="权限描述（中文）")
    description_id: Optional[str] = Field(None, description="权限描述（印尼语）")
    resource_type: str = Field(..., min_length=1, max_length=50, description="资源类型（如：user, organization, order等）")
    action: str = Field(..., min_length=1, max_length=50, description="操作类型（如：create, view, update, delete, list等）")
    display_order: Optional[int] = Field(0, description="显示顺序")
    is_active: bool = Field(True, description="是否激活")


class PermissionUpdateRequest(BaseModel):
    """更新权限请求"""
    name_zh: Optional[str] = None
    name_id: Optional[str] = None
    description_zh: Optional[str] = None
    description_id: Optional[str] = None
    resource_type: Optional[str] = None
    action: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class PermissionResponse(BaseModel):
    """权限响应"""
    id: str
    code: str
    name_zh: str
    name_id: str
    description_zh: Optional[str]
    description_id: Optional[str]
    resource_type: str
    action: str
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PermissionInfo(BaseModel):
    """权限信息（简化）"""
    id: str
    code: str
    name_zh: str
    name_id: str
    resource_type: str
    action: str

    class Config:
        from_attributes = True


class RolePermissionAssignRequest(BaseModel):
    """分配角色权限请求"""
    permission_ids: List[str] = Field(..., description="权限ID列表")


class RolePermissionResponse(BaseModel):
    """角色权限响应"""
    role_id: str
    permission_id: str
    permission: PermissionInfo
    created_at: datetime

    class Config:
        from_attributes = True


class MenuCreateRequest(BaseModel):
    """创建菜单请求"""
    code: str = Field(..., min_length=1, max_length=100, description="菜单编码（唯一）")
    name_zh: str = Field(..., min_length=1, max_length=255, description="菜单名称（中文）")
    name_id: str = Field(..., min_length=1, max_length=255, description="菜单名称（印尼语）")
    description_zh: Optional[str] = Field(None, description="菜单描述（中文）")
    description_id: Optional[str] = Field(None, description="菜单描述（印尼语）")
    parent_id: Optional[str] = Field(None, description="父菜单ID（支持树形结构）")
    path: Optional[str] = Field(None, max_length=255, description="路由路径（如：/users）")
    component: Optional[str] = Field(None, max_length=255, description="前端组件路径")
    icon: Optional[str] = Field(None, max_length=100, description="图标名称")
    display_order: Optional[int] = Field(0, description="显示顺序")
    is_active: bool = Field(True, description="是否激活")
    is_visible: bool = Field(True, description="是否可见")


class MenuUpdateRequest(BaseModel):
    """更新菜单请求"""
    name_zh: Optional[str] = None
    name_id: Optional[str] = None
    description_zh: Optional[str] = None
    description_id: Optional[str] = None
    parent_id: Optional[str] = None
    path: Optional[str] = None
    component: Optional[str] = None
    icon: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None
    is_visible: Optional[bool] = None


class MenuResponse(BaseModel):
    """菜单响应"""
    id: str
    code: str
    name_zh: str
    name_id: str
    description_zh: Optional[str]
    description_id: Optional[str]
    parent_id: Optional[str]
    path: Optional[str]
    component: Optional[str]
    icon: Optional[str]
    display_order: int
    is_active: bool
    is_visible: bool
    children: List["MenuResponse"] = Field(default_factory=list, description="子菜单列表")
    permissions: List[PermissionInfo] = Field(default_factory=list, description="关联的权限列表")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MenuPermissionAssignRequest(BaseModel):
    """分配菜单权限请求"""
    permission_ids: List[str] = Field(..., description="权限ID列表")


class UserMenuResponse(BaseModel):
    """用户菜单响应（根据用户权限过滤）"""
    id: str
    code: str
    name_zh: str
    name_id: str
    path: Optional[str]
    component: Optional[str]
    icon: Optional[str]
    display_order: int
    children: List["UserMenuResponse"] = Field(default_factory=list)

    class Config:
        from_attributes = True


class UserPermissionResponse(BaseModel):
    """用户权限响应"""
    permissions: List[PermissionInfo] = Field(default_factory=list, description="用户拥有的权限列表")
    menus: List[UserMenuResponse] = Field(default_factory=list, description="用户可访问的菜单列表")

