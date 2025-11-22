"""
角色管理 API
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from foundation_service.schemas.role import RoleResponse, RoleCreateRequest, RoleUpdateRequest
from foundation_service.services.role_service import RoleService
from foundation_service.dependencies import get_db

router = APIRouter()


@router.get("", response_model=Result[List[RoleResponse]])
async def get_role_list(
    db: AsyncSession = Depends(get_db)
):
    """查询角色列表"""
    service = RoleService(db)
    roles = await service.get_role_list()
    return Result.success(data=roles)


@router.get("/{role_id}", response_model=Result[RoleResponse])
async def get_role(
    role_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取角色详情"""
    service = RoleService(db)
    role = await service.get_role(role_id)
    return Result.success(data=role)


@router.post("", response_model=Result[RoleResponse])
async def create_role(
    request: RoleCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """创建角色"""
    service = RoleService(db)
    role = await service.create_role(request)
    return Result.success(data=role, message="角色创建成功")


@router.put("/{role_id}", response_model=Result[RoleResponse])
async def update_role(
    role_id: str,
    request: RoleUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """更新角色"""
    service = RoleService(db)
    role = await service.update_role(role_id, request)
    return Result.success(data=role, message="角色更新成功")


@router.delete("/{role_id}", response_model=Result[None])
async def delete_role(
    role_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除角色"""
    service = RoleService(db)
    await service.delete_role(role_id)
    return Result.success(message="角色删除成功")

