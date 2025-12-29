"""
财税主体管理 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from foundation_service.schemas.contract_entity_schema import (
    ContractEntityResponse,
    ContractEntityCreateRequest,
    ContractEntityUpdateRequest,
    ContractEntityListResponse,
)
from foundation_service.services.contract_entity_service import ContractEntityService
from foundation_service.dependencies import get_db, get_current_user_id

router = APIRouter()


@router.post("", response_model=Result[ContractEntityResponse])
async def create_contract_entity(
    request: ContractEntityCreateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """创建财税主体"""
    current_user_id = get_current_user_id(request_obj)
    service = ContractEntityService(db, user_id=current_user_id)
    entity = await service.create_contract_entity(request, created_by_user_id=current_user_id)
    return Result.success(data=entity, message="财税主体创建成功")


@router.get("/{entity_id}", response_model=Result[ContractEntityResponse])
async def get_contract_entity(
    entity_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取财税主体详情"""
    service = ContractEntityService(db)
    entity = await service.get_contract_entity(entity_id)
    return Result.success(data=entity)


@router.put("/{entity_id}", response_model=Result[ContractEntityResponse])
async def update_contract_entity(
    entity_id: str,
    request: ContractEntityUpdateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """更新财税主体"""
    current_user_id = get_current_user_id(request_obj)
    service = ContractEntityService(db, user_id=current_user_id)
    entity = await service.update_contract_entity(entity_id, request, updated_by_user_id=current_user_id)
    return Result.success(data=entity, message="财税主体更新成功")


@router.delete("/{entity_id}", response_model=Result[None])
async def delete_contract_entity(
    entity_id: str,
    db: AsyncSession = Depends(get_db),
):
    """删除财税主体（软删除）"""
    service = ContractEntityService(db)
    await service.delete_contract_entity(entity_id)
    return Result.success(message="财税主体删除成功")


@router.get("", response_model=Result[ContractEntityListResponse])
async def get_contract_entity_list(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=1000),
    entity_code: Optional[str] = None,
    entity_name: Optional[str] = None,
    short_name: Optional[str] = None,
    currency: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    """分页查询财税主体列表"""
    service = ContractEntityService(db)
    result = await service.get_contract_entity_list(
        page=page,
        size=size,
        entity_code=entity_code,
        entity_name=entity_name,
        short_name=short_name,
        currency=currency,
        is_active=is_active,
    )
    return Result.success(data=result)
