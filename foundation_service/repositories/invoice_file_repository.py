"""
发票文件仓库
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from common.models.invoice import InvoiceFile
from common.utils.repository import BaseRepository


class InvoiceFileRepository(BaseRepository[InvoiceFile]):
    """发票文件仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, InvoiceFile)
    
    async def get_by_invoice_id(self, invoice_id: str) -> List[InvoiceFile]:
        """根据发票ID查询所有文件"""
        query = (
            select(InvoiceFile)
            .options(joinedload(InvoiceFile.uploader))
            .where(InvoiceFile.invoice_id == invoice_id)
            .order_by(InvoiceFile.is_primary.desc(), InvoiceFile.uploaded_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_primary_file(self, invoice_id: str) -> Optional[InvoiceFile]:
        """获取主要文件"""
        query = (
            select(InvoiceFile)
            .where(InvoiceFile.invoice_id == invoice_id)
            .where(InvoiceFile.is_primary == True)
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
