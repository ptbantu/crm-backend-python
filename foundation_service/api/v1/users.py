"""
用户管理 API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from foundation_service.schemas.user import (
    UserResponse, UserCreateRequest, UserUpdateRequest,
    UserListResponse
)
from foundation_service.services.user_service import UserService
from foundation_service.dependencies import get_db, require_organization_admin

router = APIRouter()


@router.post("", response_model=Result[UserResponse])
async def create_user(
    request: UserCreateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db)
):
    """创建用户（仅组织 admin 可以创建）"""
    # 权限检查：只有该组织的 admin 可以创建用户
    current_user_id = await require_organization_admin(request_obj, request.organization_id, db)
    
    service = UserService(db)
    user = await service.create_user(request, created_by_user_id=current_user_id)
    return Result.success(data=user, message="用户创建成功")


@router.get("/{user_id}", response_model=Result[UserResponse])
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """查询用户详情"""
    service = UserService(db)
    user = await service.get_user_by_id(user_id)
    return Result.success(data=user)


@router.get("", response_model=Result[UserListResponse])
async def get_user_list(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    email: Optional[str] = None,
    organization_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """分页查询用户列表"""
    service = UserService(db)
    result = await service.get_user_list(page=page, size=size, email=email, organization_id=organization_id)
    return Result.success(data=result)


@router.put("/{user_id}", response_model=Result[UserResponse])
async def update_user(
    user_id: str,
    request: UserUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """更新用户信息"""
    service = UserService(db)
    user = await service.update_user(user_id, request)
    return Result.success(data=user, message="用户更新成功")


@router.post("/{user_id}/lock", response_model=Result[UserResponse])
async def lock_user(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """锁定用户（禁用登录，防止信息丢失）"""
    service = UserService(db)
    user = await service.lock_user(user_id)
    return Result.success(data=user, message="用户已锁定，将无法登录")


@router.post("/{user_id}/unlock", response_model=Result[UserResponse])
async def unlock_user(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """解锁用户（恢复登录）"""
    service = UserService(db)
    user = await service.unlock_user(user_id)
    return Result.success(data=user, message="用户已解锁，可以正常登录")

