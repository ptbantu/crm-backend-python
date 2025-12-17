"""
价格变更日志数据访问层
"""
from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from common.models.price_change_log import PriceChangeLog
from common.utils.repository import BaseRepository


class PriceChangeLogRepository(BaseRepository[PriceChangeLog]):
    """价格变更日志仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, PriceChangeLog)
    
    async def get_logs(
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
    ) -> Tuple[List[PriceChangeLog], int]:
        """获取价格变更日志"""
        query = select(PriceChangeLog)
        conditions = []
        
        if product_id:
            conditions.append(PriceChangeLog.product_id == product_id)
        if price_id:
            conditions.append(PriceChangeLog.price_id == price_id)
        if change_type:
            conditions.append(PriceChangeLog.change_type == change_type)
        if price_type:
            conditions.append(PriceChangeLog.price_type == price_type)
        if currency:
            conditions.append(PriceChangeLog.currency == currency)
        if start_date:
            conditions.append(PriceChangeLog.changed_at >= start_date)
        if end_date:
            conditions.append(PriceChangeLog.changed_at <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 总数查询
        count_query = select(func.count()).select_from(PriceChangeLog)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页查询
        query = query.order_by(desc(PriceChangeLog.changed_at))
        query = query.offset((page - 1) * size).limit(size)
        
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return list(items), total
    
    async def create_log(
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
    ) -> PriceChangeLog:
        """创建价格变更日志"""
        log = PriceChangeLog(
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
        
        # 计算价格变动
        if old_price is not None and new_price is not None:
            log.price_change_amount = new_price - old_price
            if old_price > 0:
                log.price_change_percentage = ((new_price - old_price) / old_price) * 100
        
        return await self.create(log)
