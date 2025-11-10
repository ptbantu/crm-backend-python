"""
用户管理 API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from foundation_service.schemas.user import (
    UserResponse, UserCreateRequest, UserUpdateRequest,
    UserListResponse
)
from foundation_service.services.user_service import UserService
from foundation_service.dependencies import get_db

router = APIRouter()


@router.post("", response_model=Result[UserResponse])
async def create_user(
    request: UserCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """创建用户"""
    service = UserService(db)
    user = await service.create_user(request)
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


@router.delete("/{user_id}", response_model=Result[None])
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Block 用户（逻辑删除）"""
    service = UserService(db)
    await service.delete_user(user_id)
    return Result.success(message="用户已禁用")

