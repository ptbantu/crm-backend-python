"""
合同仓库
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import joinedload
from common.models.contract import Contract
from common.utils.repository import BaseRepository


class ContractRepository(BaseRepository[Contract]):
    """合同仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Contract)
    
    async def get_by_opportunity_id(
        self,
        opportunity_id: str,
        include_documents: bool = True
    ) -> List[Contract]:
        """根据商机ID查询所有合同"""
        query = (
            select(Contract)
            .where(Contract.opportunity_id == opportunity_id)
        )
        if include_documents:
            query = query.options(
                joinedload(Contract.documents),
                joinedload(Contract.entity)
            )
        
        query = query.order_by(desc(Contract.created_at))
        result = await self.db.execute(query)
        return list(result.unique().scalars().all()) if include_documents else list(result.scalars().all())
    
    async def get_by_contract_no(self, contract_no: str) -> Optional[Contract]:
        """根据合同编号查询"""
        query = (
            select(Contract)
            .options(
                joinedload(Contract.entity),
                joinedload(Contract.documents),
                joinedload(Contract.opportunity),
                joinedload(Contract.quotation)
            )
            .where(Contract.contract_no == contract_no)
        )
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
    
    async def get_by_status(
        self,
        status: str,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[Contract], int]:
        """根据状态查询合同列表"""
        conditions = [Contract.status == status]
        
        # 查询总数
        count_query = select(func.count(Contract.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (
            select(Contract)
            .options(
                joinedload(Contract.entity),
                joinedload(Contract.opportunity)
            )
            .where(and_(*conditions))
            .order_by(desc(Contract.created_at))
            .offset((page - 1) * size)
            .limit(size)
        )
        result = await self.db.execute(query)
        contracts = list(result.unique().scalars().all())
        
        return contracts, total
    
    async def get_by_wechat_group_no(self, wechat_group_no: str) -> List[Contract]:
        """根据群编号查询合同"""
        query = (
            select(Contract)
            .options(joinedload(Contract.entity))
            .where(Contract.wechat_group_no == wechat_group_no)
            .order_by(desc(Contract.created_at))
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_by_entity_id(self, entity_id: str) -> List[Contract]:
        """根据签约主体ID查询合同"""
        query = (
            select(Contract)
            .where(Contract.entity_id == entity_id)
            .order_by(desc(Contract.created_at))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
