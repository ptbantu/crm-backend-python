"""
价格变更日志 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from common.schemas.response import Result
from foundation_service.schemas.price import (
    PriceChangeLogResponse,
    PriceChangeLogListResponse,
)
from foundation_service.services.price_change_log_service import PriceChangeLogService
from foundation_service.dependencies import get_db

router = APIRouter()


@router.get("", response_model=Result[PriceChangeLogListResponse])
async def get_price_change_logs(
    product_id: Optional[str] = Query(None, description="产品ID"),
    price_id: Optional[str] = Query(None, description="价格ID"),
    change_type: Optional[str] = Query(None, description="变更类型：create, update, delete"),
    price_type: Optional[str] = Query(None, description="价格类型"),
    currency: Optional[str] = Query(None, description="货币"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取价格变更日志（支持筛选、分页）"""
    service = PriceChangeLogService(db)
    result = await service.get_price_change_logs(
        product_id=product_id,
        price_id=price_id,
        change_type=change_type,
        price_type=price_type,
        currency=currency,
        start_date=start_date,
        end_date=end_date,
        page=page,
        size=size
    )
    return Result.success(data=result)
