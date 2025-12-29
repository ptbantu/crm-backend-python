"""
报价单明细仓库
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from common.models.quotation import QuotationItem
from common.utils.repository import BaseRepository


class QuotationItemRepository(BaseRepository[QuotationItem]):
    """报价单明细仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, QuotationItem)
    
    async def get_by_quotation_id(
        self,
        quotation_id: str,
        include_product: bool = True
    ) -> List[QuotationItem]:
        """根据报价单ID查询所有明细（按排序顺序）"""
        query = (
            select(QuotationItem)
            .where(QuotationItem.quotation_id == quotation_id)
        )
        if include_product:
            query = query.options(
                joinedload(QuotationItem.product),
                joinedload(QuotationItem.opportunity_item)
            )
        
        query = query.order_by(QuotationItem.sort_order.asc())
        result = await self.db.execute(query)
        return list(result.unique().scalars().all()) if include_product else list(result.scalars().all())
    
    async def get_below_cost_items(self, quotation_id: str) -> List[QuotationItem]:
        """获取低于成本的报价单明细"""
        query = (
            select(QuotationItem)
            .where(QuotationItem.quotation_id == quotation_id)
            .where(QuotationItem.is_below_cost == True)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
