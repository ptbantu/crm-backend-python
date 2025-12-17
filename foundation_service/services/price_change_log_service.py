"""
价格变更日志服务
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from foundation_service.repositories.price_change_log_repository import PriceChangeLogRepository
from foundation_service.schemas.price import (
    PriceChangeLogResponse,
    PriceChangeLogListResponse,
)
from common.utils.logger import get_logger

logger = get_logger(__name__)


class PriceChangeLogService:
    """价格变更日志服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.log_repo = PriceChangeLogRepository(db)
    
    async def get_price_change_logs(
        self,
        product_id: Optional[str] = None,
        price_id: Optional[str] = None,
        change_type: Optional[str] = None,
        price_type: Optional[str] = None,
        currency: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        size: int = 10
    ) -> PriceChangeLogListResponse:
        """获取价格变更日志"""
        items, total = await self.log_repo.get_logs(
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
        
        return PriceChangeLogListResponse(
            items=[PriceChangeLogResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            size=size
        )
    
    async def log_price_change(
        self,
        product_id: str,
        price_id: Optional[str],
        change_type: str,
        price_type: str,
        currency: str,
        old_price: Optional[float] = None,
        new_price: Optional[float] = None,
        old_effective_from: Optional[datetime] = None,
        new_effective_from: Optional[datetime] = None,
        old_effective_to: Optional[datetime] = None,
        new_effective_to: Optional[datetime] = None,
        change_reason: Optional[str] = None,
        changed_by: Optional[str] = None
    ) -> PriceChangeLogResponse:
        """记录价格变更"""
        log = await self.log_repo.create_log(
            product_id=product_id,
            price_id=price_id,
            change_type=change_type,
            price_type=price_type,
            currency=currency,
            old_price=old_price,
            new_price=new_price,
            old_effective_from=old_effective_from,
            new_effective_from=new_effective_from,
            old_effective_to=old_effective_to,
            new_effective_to=new_effective_to,
            change_reason=change_reason,
            changed_by=changed_by
        )
        
        return PriceChangeLogResponse.model_validate(log)
