"""
产品价格管理 API
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from common.schemas.response import Result
from foundation_service.schemas.price import (
    ProductPriceHistoryRequest,
    ProductPriceHistoryUpdateRequest,
    ProductPriceHistoryResponse,
    ProductPriceListResponse,
    UpcomingPriceChangeResponse,
    BatchPriceUpdateRequest,
    BatchPriceUpdateResponse,
)
from foundation_service.services.product_price_management_service import ProductPriceManagementService
from foundation_service.dependencies import get_db, get_current_user_id
from fastapi import Request

router = APIRouter()


@router.get("", response_model=Result[ProductPriceListResponse])
async def get_product_prices(
    product_id: Optional[str] = Query(None, description="产品ID"),
    organization_id: Optional[str] = Query(None, description="组织ID（NULL表示通用价格）"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取产品价格列表（列格式：一条记录包含所有价格类型和货币）"""
    service = ProductPriceManagementService(db)
    result = await service.get_product_prices(
        product_id=product_id,
        organization_id=organization_id,
        page=page,
        size=size
    )
    return Result.success(data=result)


@router.get("/{price_id}", response_model=Result[ProductPriceHistoryResponse])
async def get_product_price(
    price_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取产品价格详情"""
    service = ProductPriceManagementService(db)
    price = await service.get_product_price_by_id(price_id)
    return Result.success(data=price)


@router.get("/products/{product_id}/history", response_model=Result[ProductPriceListResponse])
async def get_product_price_history(
    product_id: str,
    organization_id: Optional[str] = Query(None, description="组织ID（NULL表示通用价格）"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取价格历史记录（列格式：一条记录包含所有价格类型和货币）"""
    service = ProductPriceManagementService(db)
    result = await service.get_product_price_history(
        product_id=product_id,
        organization_id=organization_id,
        page=page,
        size=size
    )
    return Result.success(data=result)


@router.post("", response_model=Result[ProductPriceHistoryResponse])
async def create_price(
    request: ProductPriceHistoryRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db)
):
    """创建新价格（列格式：一条记录包含所有价格类型和货币，立即生效或未来生效）"""
    current_user_id = get_current_user_id(request_obj)
    service = ProductPriceManagementService(db)
    price = await service.create_price(request, changed_by=current_user_id)
    return Result.success(data=price, message="价格创建成功")


@router.put("/{price_id}", response_model=Result[ProductPriceHistoryResponse])
async def update_price(
    price_id: str,
    request: ProductPriceHistoryUpdateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db)
):
    """更新价格（列格式：一条记录包含所有价格类型和货币）"""
    current_user_id = get_current_user_id(request_obj)
    service = ProductPriceManagementService(db)
    price = await service.update_price(price_id, request, changed_by=current_user_id)
    return Result.success(data=price, message="价格更新成功")


@router.delete("/{price_id}", response_model=Result[None])
async def delete_price(
    price_id: str,
    request_obj: Request,
    db: AsyncSession = Depends(get_db)
):
    """删除/取消未来生效的价格（列格式：一条记录包含所有价格类型和货币）"""
    current_user_id = get_current_user_id(request_obj)
    service = ProductPriceManagementService(db)
    await service.cancel_future_price(price_id, changed_by=current_user_id)
    return Result.success(message="价格删除成功")


@router.get("/upcoming/changes", response_model=Result[List[UpcomingPriceChangeResponse]])
async def get_upcoming_price_changes(
    product_id: Optional[str] = Query(None, description="产品ID"),
    hours_ahead: int = Query(24, ge=1, le=168, description="未来多少小时内"),
    db: AsyncSession = Depends(get_db)
):
    """获取即将生效的价格变更（列格式：一条记录包含所有价格类型和货币）"""
    service = ProductPriceManagementService(db)
    changes = await service.get_upcoming_price_changes(
        product_id=product_id,
        hours_ahead=hours_ahead
    )
    return Result.success(data=changes)


@router.post("/batch", response_model=Result[BatchPriceUpdateResponse])
async def batch_update_prices(
    request: BatchPriceUpdateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db)
):
    """批量更新价格"""
    current_user_id = get_current_user_id(request_obj)
    service = ProductPriceManagementService(db)
    success_count = 0
    failure_count = 0
    errors = []
    
    for price_request in request.prices:
        try:
            await service.create_price(price_request, changed_by=current_user_id)
            success_count += 1
        except Exception as e:
            failure_count += 1
            errors.append({
                "product_id": price_request.product_id,
                "error": str(e)
            })
    
    return Result.success(data=BatchPriceUpdateResponse(
        success_count=success_count,
        failure_count=failure_count,
        errors=errors
    ))
