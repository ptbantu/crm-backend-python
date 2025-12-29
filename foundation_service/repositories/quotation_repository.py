"""
报价单仓库
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import joinedload
from common.models.quotation import Quotation
from common.utils.repository import BaseRepository


class QuotationRepository(BaseRepository[Quotation]):
    """报价单仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Quotation)
    
    async def get_by_opportunity_id(
        self,
        opportunity_id: str,
        include_items: bool = True
    ) -> List[Quotation]:
        """根据商机ID查询所有报价单（按版本倒序）"""
        query = (
            select(Quotation)
            .where(Quotation.opportunity_id == opportunity_id)
        )
        if include_items:
            query = query.options(joinedload(Quotation.items))
        
        query = query.order_by(desc(Quotation.version))
        result = await self.db.execute(query)
        return list(result.unique().scalars().all()) if include_items else list(result.scalars().all())
    
    async def get_by_quotation_no(self, quotation_no: str) -> Optional[Quotation]:
        """根据报价单编号查询"""
        query = (
            select(Quotation)
            .options(
                joinedload(Quotation.items),
                joinedload(Quotation.documents),
                joinedload(Quotation.opportunity),
                joinedload(Quotation.creator)
            )
            .where(Quotation.quotation_no == quotation_no)
        )
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
    
    async def get_latest_version(self, opportunity_id: str) -> Optional[Quotation]:
        """获取最新版本的报价单"""
        query = (
            select(Quotation)
            .options(joinedload(Quotation.items))
            .where(Quotation.opportunity_id == opportunity_id)
            .order_by(desc(Quotation.version))
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
    
    async def get_next_version(self, opportunity_id: int) -> int:
        """获取下一个版本号"""
        query = (
            select(func.max(Quotation.version))
            .where(Quotation.opportunity_id == opportunity_id)
        )
        result = await self.db.execute(query)
        max_version = result.scalar() or 0
        return max_version + 1
    
    async def get_by_status(
        self,
        status: str,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[Quotation], int]:
        """根据状态查询报价单列表"""
        conditions = [Quotation.status == status]
        
        # 查询总数
        count_query = select(func.count(Quotation.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (
            select(Quotation)
            .options(
                joinedload(Quotation.opportunity),
                joinedload(Quotation.creator)
            )
            .where(and_(*conditions))
            .order_by(desc(Quotation.created_at))
            .offset((page - 1) * size)
            .limit(size)
        )
        result = await self.db.execute(query)
        quotations = list(result.unique().scalars().all())
        
        return quotations, total
    
    async def get_by_wechat_group_no(self, wechat_group_no: str) -> List[Quotation]:
        """根据群编号查询报价单"""
        query = (
            select(Quotation)
            .options(joinedload(Quotation.items))
            .where(Quotation.wechat_group_no == wechat_group_no)
            .order_by(desc(Quotation.created_at))
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
