"""
组织领域管理 API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from foundation_service.schemas.organization_domain import (
    OrganizationDomainResponse, OrganizationDomainCreateRequest,
    OrganizationDomainUpdateRequest, OrganizationDomainRelationResponse
)
from foundation_service.services.organization_domain_service import OrganizationDomainService
from foundation_service.dependencies import get_db

router = APIRouter()


@router.post("", response_model=Result[OrganizationDomainResponse])
async def create_domain(
    request: OrganizationDomainCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """创建组织领域"""
    service = OrganizationDomainService(db)
    domain = await service.create_domain(request)
    return Result.success(data=domain, message="组织领域创建成功")


@router.get("", response_model=Result[List[OrganizationDomainResponse]])
async def get_all_domains(
    db: AsyncSession = Depends(get_db)
):
    """查询所有激活的组织领域"""
    service = OrganizationDomainService(db)
    domains = await service.get_all_domains()
    return Result.success(data=domains)


@router.get("/{domain_id}", response_model=Result[OrganizationDomainResponse])
async def get_domain(
    domain_id: str = Path(..., description="领域ID"),
    db: AsyncSession = Depends(get_db)
):
    """查询组织领域详情"""
    service = OrganizationDomainService(db)
    domain = await service.get_domain_by_id(domain_id)
    return Result.success(data=domain)


@router.put("/{domain_id}", response_model=Result[OrganizationDomainResponse])
async def update_domain(
    domain_id: str = Path(..., description="领域ID"),
    request: OrganizationDomainUpdateRequest = ...,
    db: AsyncSession = Depends(get_db)
):
    """更新组织领域"""
    service = OrganizationDomainService(db)
    domain = await service.update_domain(domain_id, request)
    return Result.success(data=domain, message="组织领域更新成功")


@router.delete("/{domain_id}", response_model=Result[None])
async def delete_domain(
    domain_id: str = Path(..., description="领域ID"),
    db: AsyncSession = Depends(get_db)
):
    """删除组织领域（逻辑删除）"""
    service = OrganizationDomainService(db)
    await service.delete_domain(domain_id)
    return Result.success(message="组织领域已删除")


@router.get("/organizations/{organization_id}/domains", response_model=Result[List[OrganizationDomainRelationResponse]])
async def get_organization_domains(
    organization_id: str = Path(..., description="组织ID"),
    db: AsyncSession = Depends(get_db)
):
    """查询组织的领域列表"""
    service = OrganizationDomainService(db)
    domains = await service.get_organization_domains(organization_id)
    return Result.success(data=domains)


@router.post("/organizations/{organization_id}/domains", response_model=Result[List[OrganizationDomainRelationResponse]])
async def set_organization_domains(
    organization_id: str = Path(..., description="组织ID"),
    domain_ids: List[str] = Body(..., description="领域ID列表"),
    primary_domain_id: Optional[str] = Body(None, description="主要领域ID"),
    db: AsyncSession = Depends(get_db)
):
    """设置组织的领域关联"""
    service = OrganizationDomainService(db)
    domains = await service.set_organization_domains(organization_id, domain_ids, primary_domain_id)
    return Result.success(data=domains, message="组织领域设置成功")

