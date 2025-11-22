"""
菜单管理 API
"""
from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from foundation_service.database import get_db
from foundation_service.services.permission_service import PermissionService
from foundation_service.schemas.permission import (
    MenuCreateRequest,
    MenuUpdateRequest,
    MenuResponse,
    MenuPermissionAssignRequest,
    UserMenuResponse
)
from common.schemas.response import Result

router = APIRouter(prefix="/menus", tags=["菜单管理"])


@router.post("", response_model=Result[MenuResponse])
async def create_menu(
    request: MenuCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """创建菜单"""
    service = PermissionService(db)
    menu = await service.create_menu(request)
    return Result.success(data=menu, message="菜单创建成功")


@router.get("/{menu_id}", response_model=Result[MenuResponse])
async def get_menu(
    menu_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取菜单详情"""
    service = PermissionService(db)
    menu = await service.get_menu(menu_id)
    return Result.success(data=menu)


@router.put("/{menu_id}", response_model=Result[MenuResponse])
async def update_menu(
    menu_id: str,
    request: MenuUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """更新菜单"""
    service = PermissionService(db)
    menu = await service.update_menu(menu_id, request)
    return Result.success(data=menu, message="菜单更新成功")


@router.get("/tree/list", response_model=Result[List[MenuResponse]])
async def get_menu_tree(
    db: AsyncSession = Depends(get_db)
):
    """获取菜单树"""
    service = PermissionService(db)
    menus = await service.get_menu_tree()
    return Result.success(data=menus)


@router.post("/{menu_id}/permissions/assign", response_model=Result[None])
async def assign_permissions_to_menu(
    menu_id: str,
    request: MenuPermissionAssignRequest,
    db: AsyncSession = Depends(get_db)
):
    """为菜单分配权限"""
    service = PermissionService(db)
    await service.assign_permissions_to_menu(menu_id, request)
    return Result.success(message="菜单权限分配成功")


@router.get("/users/{user_id}/accessible", response_model=Result[List[UserMenuResponse]])
async def get_user_menus(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取用户可访问的菜单"""
    service = PermissionService(db)
    menus = await service.get_user_menus(user_id)
    return Result.success(data=menus)

