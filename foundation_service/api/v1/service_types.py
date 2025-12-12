"""
服务类型管理 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from foundation_service.schemas.service_type import (
    ServiceTypeResponse,
    ServiceTypeCreateRequest,
    ServiceTypeUpdateRequest,
    ServiceTypeListResponse,
)
from foundation_service.services.service_type_service import ServiceTypeService
from foundation_service.dependencies import get_db

router = APIRouter()


@router.post("", response_model=Result[ServiceTypeResponse])
async def create_service_type(
    request: ServiceTypeCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """创建服务类型"""
    service = ServiceTypeService(db)
    service_type = await service.create_service_type(request)
    return Result.success(data=service_type, message="服务类型创建成功")


@router.get("/{service_type_id}", response_model=Result[ServiceTypeResponse])
async def get_service_type(
    service_type_id: str,
    db: AsyncSession = Depends(get_db)
):
    """查询服务类型详情"""
    service = ServiceTypeService(db)
    service_type = await service.get_service_type_by_id(service_type_id)
    return Result.success(data=service_type)


@router.get("/code/{code}", response_model=Result[ServiceTypeResponse])
async def get_service_type_by_code(
    code: str,
    db: AsyncSession = Depends(get_db)
):
    """根据代码查询服务类型"""
    service = ServiceTypeService(db)
    service_type = await service.get_service_type_by_code(code)
    return Result.success(data=service_type)


@router.put("/{service_type_id}", response_model=Result[ServiceTypeResponse])
async def update_service_type(
    service_type_id: str,
    request: ServiceTypeUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """更新服务类型"""
    service = ServiceTypeService(db)
    service_type = await service.update_service_type(service_type_id, request)
    return Result.success(data=service_type, message="服务类型更新成功")


@router.delete("/{service_type_id}", response_model=Result[None])
async def delete_service_type(
    service_type_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除服务类型"""
    service = ServiceTypeService(db)
    await service.delete_service_type(service_type_id)
    return Result.success(message="服务类型删除成功")


@router.get("", response_model=Result[ServiceTypeListResponse])
async def get_service_type_list(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=1000),
    code: Optional[str] = None,
    name: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """分页查询服务类型列表"""
    service = ServiceTypeService(db)
    result = await service.get_service_type_list(
        page=page,
        size=size,
        code=code,
        name=name,
        is_active=is_active,
    )
    return Result.success(data=result)


