"""
发票文档扩展仓库
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from common.models.doc_invoice_ext import DocInvoiceExt
from common.utils.repository import BaseRepository


class DocInvoiceExtRepository(BaseRepository[DocInvoiceExt]):
    """发票文档扩展仓库"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, DocInvoiceExt)

    async def get_by_document_id(self, document_id: str) -> Optional[DocInvoiceExt]:
        """根据文档ID查询"""
        query = select(DocInvoiceExt).where(DocInvoiceExt.document_id == document_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_invoice_id(self, invoice_id: str) -> Optional[DocInvoiceExt]:
        """根据发票ID查询"""
        query = select(DocInvoiceExt).where(DocInvoiceExt.invoice_id == invoice_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
