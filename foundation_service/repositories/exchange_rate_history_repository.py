"""
汇率历史数据访问层
"""
from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from common.models.exchange_rate_history import ExchangeRateHistory
from common.utils.repository import BaseRepository


class ExchangeRateHistoryRepository(BaseRepository[ExchangeRateHistory]):
    """汇率历史仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ExchangeRateHistory)
    
    async def get_current_rate(
        self,
        from_currency: str,
        to_currency: str
    ) -> Optional[ExchangeRateHistory]:
        """获取当前有效的汇率"""
        now = datetime.now()
        query = select(ExchangeRateHistory).where(
            and_(
                ExchangeRateHistory.from_currency == from_currency,
                ExchangeRateHistory.to_currency == to_currency,
                ExchangeRateHistory.is_approved == True,
                ExchangeRateHistory.effective_from <= now,
                or_(
                    ExchangeRateHistory.effective_to.is_(None),
                    ExchangeRateHistory.effective_to > now
                )
            )
        ).order_by(desc(ExchangeRateHistory.effective_from)).limit(1)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_rate_history(
        self,
        from_currency: Optional[str] = None,
        to_currency: Optional[str] = None,
        page: int = 1,
        size: int = 10
    ) -> Tuple[List[ExchangeRateHistory], int]:
        """获取汇率历史记录"""
        query = select(ExchangeRateHistory)
        conditions = []
        
        if from_currency:
            conditions.append(ExchangeRateHistory.from_currency == from_currency)
        if to_currency:
            conditions.append(ExchangeRateHistory.to_currency == to_currency)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 总数查询
        count_query = select(func.count()).select_from(ExchangeRateHistory)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页查询
        query = query.order_by(desc(ExchangeRateHistory.effective_from))
        query = query.offset((page - 1) * size).limit(size)
        
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return list(items), total
    
    async def get_all_current_rates(self) -> List[ExchangeRateHistory]:
        """获取所有当前有效的汇率"""
        now = datetime.now()
        query = select(ExchangeRateHistory).where(
            and_(
                ExchangeRateHistory.is_approved == True,
                ExchangeRateHistory.effective_from <= now,
                or_(
                    ExchangeRateHistory.effective_to.is_(None),
                    ExchangeRateHistory.effective_to > now
                )
            )
        ).order_by(
            ExchangeRateHistory.from_currency,
            ExchangeRateHistory.to_currency
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_upcoming_rates(
        self,
        hours_ahead: int = 24
    ) -> List[ExchangeRateHistory]:
        """获取即将生效的汇率"""
        now = datetime.now()
        future_time = datetime.fromtimestamp(now.timestamp() + hours_ahead * 3600)
        
        query = select(ExchangeRateHistory).where(
            and_(
                ExchangeRateHistory.effective_from > now,
                ExchangeRateHistory.effective_from <= future_time
            )
        ).order_by(ExchangeRateHistory.effective_from)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
