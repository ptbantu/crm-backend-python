"""
组织管理 API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from foundation_service.schemas.organization import (
    OrganizationResponse, OrganizationCreateRequest, OrganizationUpdateRequest,
    OrganizationListResponse, OrganizationTreeNode
)
from foundation_service.services.organization_service import OrganizationService
from foundation_service.dependencies import get_db

router = APIRouter()


@router.post("", response_model=Result[OrganizationResponse])
async def create_organization(
    request: OrganizationCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """创建组织"""
    service = OrganizationService(db)
    organization = await service.create_organization(request)
    return Result.success(data=organization, message="组织创建成功")


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


@router.delete("/{organization_id}", response_model=Result[None])
async def delete_organization(
    organization_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Block 组织（逻辑删除）"""
    service = OrganizationService(db)
    await service.delete_organization(organization_id)
    return Result.success(message="组织已锁定")

