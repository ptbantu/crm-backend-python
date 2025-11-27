"""
用户管理 API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from common.utils.logger import get_logger
from foundation_service.schemas.user import (
    UserResponse, UserCreateRequest, UserUpdateRequest,
    UserListResponse, UserResetPasswordRequest
)
from foundation_service.services.user_service import UserService
from foundation_service.dependencies import get_db, require_organization_admin

logger = get_logger(__name__)

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
    重置用户密码（仅 ADMIN 角色可以重置）
    
    权限要求：
    - 当前用户必须拥有 ADMIN 角色
    - 当前用户必须是目标用户所属组织的 admin，或者是 BANTU 内部组织的 admin
    """
    from foundation_service.dependencies import get_current_user_id, get_current_user_roles
    from foundation_service.repositories.organization_employee_repository import OrganizationEmployeeRepository
    from foundation_service.repositories.organization_repository import OrganizationRepository
    from foundation_service.repositories.user_repository import UserRepository
    from fastapi import HTTPException, status
    
    # 1. 验证当前用户身份
    current_user_id = get_current_user_id(request_obj)
    if not current_user_id:
        # 记录详细的错误信息，便于调试
        logger.warning(f"[reset_password] 未获取到用户ID，请求头: {dict(request_obj.headers)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请重新登录"
        )
    
    # 2. 验证 ADMIN 角色
    # 优先从请求头获取（Gateway 传递）
    current_user_roles = get_current_user_roles(request_obj)
    # 如果请求头中没有角色信息，从数据库查询（兼容直接访问 Foundation Service 的情况）
    if not current_user_roles:
        user_repo = UserRepository(db)
        user_roles = await user_repo.get_user_roles(current_user_id)
        current_user_roles = [role.code for role in user_roles]
    
    if "ADMIN" not in current_user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有 ADMIN 角色可以重置用户密码"
        )
    
    # 3. 验证目标用户存在
    user_repo = UserRepository(db)
    target_user = await user_repo.get_by_id(user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 4. 获取目标用户所属的组织
    employee_repo = OrganizationEmployeeRepository(db)
    target_employee = await employee_repo.get_primary_by_user_id(user_id)
    if not target_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未关联到任何组织"
        )
    
    # 5. 验证组织权限
    org_repo = OrganizationRepository(db)
    bantu_org = await org_repo.get_bantu_organization()
    
    # 获取当前用户的组织
    current_employee = await employee_repo.get_primary_by_user_id(current_user_id)
    if not current_employee:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="当前用户未关联到任何组织"
        )
    
    # 权限检查：
    # - BANTU admin 可以重置任何用户的密码
    # - 组织 admin 只能重置同组织用户的密码
    has_permission = False
    if bantu_org and current_employee.organization_id == bantu_org.id:
        # BANTU admin 可以重置任何用户的密码
        has_permission = True
    elif current_employee.organization_id == target_employee.organization_id:
        # 同组织的 admin 可以重置该组织用户的密码
        has_permission = True
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有组织 admin 或 BANTU admin 可以重置用户密码"
        )
    
    # 6. 执行重置密码
    service = UserService(db)
    user = await service.reset_password(user_id, request.new_password)
    return Result.success(data=user, message="密码重置成功")

