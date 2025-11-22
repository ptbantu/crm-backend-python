"""
权限管理 API
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from foundation_service.database import get_db
from foundation_service.services.permission_service import PermissionService
from foundation_service.schemas.permission import (
    PermissionCreateRequest,
    PermissionUpdateRequest,
    PermissionResponse,
    RolePermissionAssignRequest,
    UserPermissionResponse
)
from common.schemas.response import Result

router = APIRouter(prefix="/permissions", tags=["权限管理"])


@router.post("", response_model=Result[PermissionResponse])
async def create_permission(
    request: PermissionCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """创建权限"""
    service = PermissionService(db)
    permission = await service.create_permission(request)
    return Result.success(data=permission, message="权限创建成功")


@router.get("/{permission_id}", response_model=Result[PermissionResponse])
async def get_permission(
    permission_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取权限详情"""
    service = PermissionService(db)
    permission = await service.get_permission(permission_id)
    return Result.success(data=permission)


@router.put("/{permission_id}", response_model=Result[PermissionResponse])
async def update_permission(
    permission_id: str,
    request: PermissionUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """更新权限"""
    service = PermissionService(db)
    permission = await service.update_permission(permission_id, request)
    return Result.success(data=permission, message="权限更新成功")


@router.get("", response_model=Result[List[PermissionResponse]])
async def get_permission_list(
    resource_type: Optional[str] = Query(None, description="资源类型"),
    is_active: Optional[bool] = Query(None, description="是否激活"),
    db: AsyncSession = Depends(get_db)
):
    """获取权限列表"""
    service = PermissionService(db)
    permissions = await service.get_permission_list(resource_type=resource_type, is_active=is_active)
    return Result.success(data=permissions)


@router.post("/roles/{role_id}/assign", response_model=Result[None])
async def assign_permissions_to_role(
    role_id: str,
    request: RolePermissionAssignRequest,
    db: AsyncSession = Depends(get_db)
):
    """为角色分配权限"""
    service = PermissionService(db)
    await service.assign_permissions_to_role(role_id, request)
    return Result.success(message="角色权限分配成功")


@router.get("/roles/{role_id}", response_model=Result[List[PermissionResponse]])
async def get_role_permissions(
    role_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取角色的权限列表"""
    service = PermissionService(db)
    permissions = await service.get_role_permissions(role_id)
    return Result.success(data=permissions)


@router.get("/users/{user_id}/info", response_model=Result[UserPermissionResponse])
async def get_user_permission_info(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取用户的权限和菜单信息"""
    service = PermissionService(db)
    info = await service.get_user_permission_info(user_id)
    return Result.success(data=info)

