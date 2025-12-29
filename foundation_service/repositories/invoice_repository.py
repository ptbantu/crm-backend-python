"""
发票仓库
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import joinedload
from common.models.invoice import Invoice
from common.utils.repository import BaseRepository


class InvoiceRepository(BaseRepository[Invoice]):
    """发票仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Invoice)
    
    async def get_by_contract_id(
        self,
        contract_id: str,
        include_files: bool = True
    ) -> List[Invoice]:
        """根据合同ID查询所有发票"""
        query = (
            select(Invoice)
            .where(Invoice.contract_id == contract_id)
        )
        if include_files:
            query = query.options(joinedload(Invoice.files))
        
        query = query.order_by(desc(Invoice.created_at))
        result = await self.db.execute(query)
        return list(result.unique().scalars().all()) if include_files else list(result.scalars().all())
    
    async def get_by_opportunity_id(self, opportunity_id: str) -> List[Invoice]:
        """根据商机ID查询所有发票"""
        query = (
            select(Invoice)
            .options(joinedload(Invoice.files))
            .where(Invoice.opportunity_id == opportunity_id)
            .order_by(desc(Invoice.created_at))
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_by_invoice_no(self, invoice_no: str) -> Optional[Invoice]:
        """根据发票编号查询"""
        query = (
            select(Invoice)
            .options(
                joinedload(Invoice.files),
                joinedload(Invoice.entity),
                joinedload(Invoice.contract),
                joinedload(Invoice.opportunity)
            )
            .where(Invoice.invoice_no == invoice_no)
        )
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
    
    async def get_by_status(
        self,
        status: str,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[Invoice], int]:
        """根据状态查询发票列表"""
        conditions = [Invoice.status == status]
        
        # 查询总数
        count_query = select(func.count(Invoice.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (
            select(Invoice)
            .options(joinedload(Invoice.entity))
            .where(and_(*conditions))
            .order_by(desc(Invoice.created_at))
            .offset((page - 1) * size)
            .limit(size)
        )
        result = await self.db.execute(query)
        invoices = list(result.unique().scalars().all())
        
        return invoices, total
    
    async def get_by_entity_id(self, entity_id: str) -> List[Invoice]:
        """根据签约主体ID查询发票"""
        query = (
            select(Invoice)
            .where(Invoice.entity_id == entity_id)
            .order_by(desc(Invoice.created_at))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
