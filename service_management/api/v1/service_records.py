"""
服务记录管理 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from service_management.schemas.service_record import (
    ServiceRecordResponse,
    ServiceRecordCreateRequest,
    ServiceRecordUpdateRequest,
    ServiceRecordListResponse,
)
from service_management.services.service_record_service import ServiceRecordService
from service_management.dependencies import get_db

router = APIRouter()


@router.post("", response_model=Result[ServiceRecordResponse])
async def create_service_record(
    request: ServiceRecordCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """创建服务记录"""
    service = ServiceRecordService(db)
    service_record = await service.create_service_record(request)
    return Result.success(data=service_record, message="服务记录创建成功")


@router.get("/{service_record_id}", response_model=Result[ServiceRecordResponse])
async def get_service_record(
    service_record_id: str,
    db: AsyncSession = Depends(get_db)
):
    """查询服务记录详情"""
    service = ServiceRecordService(db)
    service_record = await service.get_service_record_by_id(service_record_id)
    return Result.success(data=service_record)


@router.put("/{service_record_id}", response_model=Result[ServiceRecordResponse])
async def update_service_record(
    service_record_id: str,
    request: ServiceRecordUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """更新服务记录"""
    service = ServiceRecordService(db)
    service_record = await service.update_service_record(service_record_id, request)
    return Result.success(data=service_record, message="服务记录更新成功")


@router.delete("/{service_record_id}", response_model=Result[None])
async def delete_service_record(
    service_record_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除服务记录"""
    service = ServiceRecordService(db)
    await service.delete_service_record(service_record_id)
    return Result.success(message="服务记录删除成功")


@router.get("", response_model=Result[ServiceRecordListResponse])
async def get_service_record_list(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    customer_id: Optional[str] = None,
    service_type_id: Optional[str] = None,
    product_id: Optional[str] = None,
    contact_id: Optional[str] = None,
    sales_user_id: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    referral_customer_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """分页查询服务记录列表"""
    service = ServiceRecordService(db)
    result = await service.get_service_record_list(
        page=page,
        size=size,
        customer_id=customer_id,
        service_type_id=service_type_id,
        product_id=product_id,
        contact_id=contact_id,
        sales_user_id=sales_user_id,
        status=status,
        priority=priority,
        referral_customer_id=referral_customer_id,
    )
    return Result.success(data=result)


@router.get("/customers/{customer_id}/service-records", response_model=Result[ServiceRecordListResponse])
async def get_service_records_by_customer(
    customer_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """根据客户ID查询服务记录列表"""
    service = ServiceRecordService(db)
    result = await service.get_service_record_list(
        page=page,
        size=size,
        customer_id=customer_id,
        status=status,
        priority=priority,
    )
    return Result.success(data=result)

