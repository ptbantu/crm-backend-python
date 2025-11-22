"""
组织管理 API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from foundation_service.schemas.organization import (
    OrganizationResponse, OrganizationCreateRequest, OrganizationUpdateRequest,
    OrganizationListResponse
)
from foundation_service.services.organization_service import OrganizationService
from foundation_service.dependencies import get_db, require_bantu_admin

router = APIRouter()


@router.post("", response_model=Result[OrganizationResponse])
async def create_organization(
    request: OrganizationCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(require_bantu_admin)
):
    """创建组织（仅 BANTU 的 admin 用户可以创建）"""
    service = OrganizationService(db)
    organization = await service.create_organization(request, created_by_user_id=current_user_id)
    return Result.success(data=organization, message="组织创建成功，已自动创建该组织的 admin 用户")


@router.get("/{organization_id}", response_model=Result[OrganizationResponse])
async def get_organization(
    organization_id: str,
    db: AsyncSession = Depends(get_db)
):
    """查询组织详情"""
    service = OrganizationService(db)
    organization = await service.get_organization_by_id(organization_id)
    return Result.success(data=organization)


@router.put("/{organization_id}", response_model=Result[OrganizationResponse])
async def update_organization(
    organization_id: str,
    request: OrganizationUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """更新组织信息"""
    service = OrganizationService(db)
    organization = await service.update_organization(organization_id, request)
    return Result.success(data=organization, message="组织更新成功")


@router.get("", response_model=Result[OrganizationListResponse])
async def get_organization_list(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    name: Optional[str] = None,
    code: Optional[str] = None,
    organization_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """分页查询组织列表"""
    service = OrganizationService(db)
    result = await service.get_organization_list(
        page=page,
        size=size,
        name=name,
        code=code,
        organization_type=organization_type,
        is_active=is_active
    )
    return Result.success(data=result)


@router.post("/{organization_id}/lock", response_model=Result[OrganizationResponse])
async def lock_organization(
    organization_id: str,
    db: AsyncSession = Depends(get_db)
):
    """锁定组织（断开合作）"""
    service = OrganizationService(db)
    organization = await service.lock_organization(organization_id)
    return Result.success(data=organization, message="组织已锁定，该组织所有用户将无法登录")


@router.post("/{organization_id}/unlock", response_model=Result[OrganizationResponse])
async def unlock_organization(
    organization_id: str,
    db: AsyncSession = Depends(get_db)
):
    """解锁组织（恢复合作）"""
    service = OrganizationService(db)
    organization = await service.unlock_organization(organization_id)
    return Result.success(data=organization, message="组织已解锁，该组织用户可以正常登录")

