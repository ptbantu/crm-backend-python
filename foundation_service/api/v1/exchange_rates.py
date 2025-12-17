"""
汇率管理 API
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from foundation_service.schemas.price import (
    ExchangeRateHistoryRequest,
    ExchangeRateHistoryUpdateRequest,
    ExchangeRateHistoryResponse,
    ExchangeRateListResponse,
    CurrencyConvertRequest,
    CurrencyConvertResponse,
)
from foundation_service.services.exchange_rate_service import ExchangeRateService
from foundation_service.dependencies import get_db, get_current_user_id
from fastapi import Request

router = APIRouter()


@router.get("", response_model=Result[List[ExchangeRateHistoryResponse]])
async def get_current_rates(
    from_currency: Optional[str] = Query(None, description="源货币"),
    to_currency: Optional[str] = Query(None, description="目标货币"),
    db: AsyncSession = Depends(get_db)
):
    """获取当前有效汇率列表"""
    service = ExchangeRateService(db)
    rates = await service.get_current_rates(
        from_currency=from_currency,
        to_currency=to_currency
    )
    return Result.success(data=rates)


@router.get("/history", response_model=Result[ExchangeRateListResponse])
async def get_rate_history(
    from_currency: Optional[str] = Query(None, description="源货币"),
    to_currency: Optional[str] = Query(None, description="目标货币"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取汇率历史记录"""
    service = ExchangeRateService(db)
    result = await service.get_rate_history(
        from_currency=from_currency,
        to_currency=to_currency,
        page=page,
        size=size
    )
    return Result.success(data=result)


@router.post("", response_model=Result[ExchangeRateHistoryResponse])
async def create_rate(
    request: ExchangeRateHistoryRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db)
):
    """创建新汇率（立即生效或未来生效）"""
    current_user_id = get_current_user_id(request_obj)
    service = ExchangeRateService(db)
    rate = await service.create_rate(request, changed_by=current_user_id)
    return Result.success(data=rate, message="汇率创建成功")


@router.put("/{rate_id}", response_model=Result[ExchangeRateHistoryResponse])
async def update_rate(
    rate_id: str,
    request: ExchangeRateHistoryUpdateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db)
):
    """更新汇率"""
    current_user_id = get_current_user_id(request_obj)
    service = ExchangeRateService(db)
    rate = await service.update_rate(rate_id, request, changed_by=current_user_id)
    return Result.success(data=rate, message="汇率更新成功")


@router.get("/convert", response_model=Result[CurrencyConvertResponse])
async def convert_currency(
    from_currency: str = Query(..., description="源货币"),
    to_currency: str = Query(..., description="目标货币"),
    amount: float = Query(..., ge=0, description="金额"),
    db: AsyncSession = Depends(get_db)
):
    """汇率换算工具"""
    from foundation_service.schemas.price import CurrencyConvertRequest
    service = ExchangeRateService(db)
    convert_request = CurrencyConvertRequest(
        from_currency=from_currency,
        to_currency=to_currency,
        amount=amount
    )
    result = await service.convert_currency(convert_request)
    return Result.success(data=result)
