"""
用户管理 API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from foundation_service.schemas.user import (
    UserResponse, UserCreateRequest, UserUpdateRequest,
    UserListResponse, UserResetPasswordRequest
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


@router.post("/{user_id}/reset-password", response_model=Result[UserResponse])
async def reset_password(
    user_id: str,
    request: UserResetPasswordRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    重置用户密码（仅组织 admin 可以重置）
    
    权限要求：
    - 当前用户必须是目标用户所属组织的 admin
    - 或者当前用户是 BANTU 内部组织的 admin（可以重置任何用户的密码）
    """
    from foundation_service.dependencies import get_current_user_id
    from foundation_service.repositories.organization_employee_repository import OrganizationEmployeeRepository
    from foundation_service.repositories.organization_repository import OrganizationRepository
    from foundation_service.repositories.user_repository import UserRepository
    from fastapi import HTTPException, status
    
    current_user_id = get_current_user_id(request_obj)
    if not current_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要认证"
        )
    
    # 获取目标用户
    user_repo = UserRepository(db)
    target_user = await user_repo.get_by_id(user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 获取目标用户所属的组织
    employee_repo = OrganizationEmployeeRepository(db)
    target_employee = await employee_repo.get_primary_by_user_id(user_id)
    if not target_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未关联到任何组织"
        )
    
    # 检查权限：
    # 1. 如果当前用户是 BANTU 内部组织的 admin，可以重置任何用户的密码
    # 2. 如果当前用户是目标用户所属组织的 admin，可以重置该用户的密码
    
    org_repo = OrganizationRepository(db)
    bantu_org = await org_repo.get_bantu_organization()
    
    # 获取当前用户的组织
    current_employee = await employee_repo.get_primary_by_user_id(current_user_id)
    if not current_employee:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="当前用户未关联到任何组织"
        )
    
    # 获取当前用户的角色
    current_user_roles = await user_repo.get_user_roles(current_user_id)
    role_codes = [role.code for role in current_user_roles]
    is_admin = "ADMIN" in role_codes
    
    # 权限检查
    has_permission = False
    
    # 情况1：当前用户是 BANTU 内部组织的 admin
    if bantu_org and current_employee.organization_id == bantu_org.id and is_admin:
        has_permission = True
    
    # 情况2：当前用户是目标用户所属组织的 admin
    elif current_employee.organization_id == target_employee.organization_id and is_admin:
        has_permission = True
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有组织 admin 或 BANTU admin 可以重置用户密码"
        )
    
    # 执行重置密码
    service = UserService(db)
    user = await service.reset_password(user_id, request.new_password)
    return Result.success(data=user, message="密码重置成功")

