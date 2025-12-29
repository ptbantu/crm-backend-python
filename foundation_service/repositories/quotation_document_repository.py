"""
报价单资料仓库
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from common.models.quotation import QuotationDocument
from common.utils.repository import BaseRepository


class QuotationDocumentRepository(BaseRepository[QuotationDocument]):
    """报价单资料仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, QuotationDocument)
    
    async def get_by_quotation_id(self, quotation_id: str) -> List[QuotationDocument]:
        """根据报价单ID查询所有资料"""
        query = (
            select(QuotationDocument)
            .options(joinedload(QuotationDocument.uploader))
            .where(QuotationDocument.quotation_id == quotation_id)
            .order_by(QuotationDocument.uploaded_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_by_document_type(
        self,
        quotation_id: str,
        document_type: str
    ) -> List[QuotationDocument]:
        """根据资料类型查询"""
        query = (
            select(QuotationDocument)
            .where(QuotationDocument.quotation_id == quotation_id)
            .where(QuotationDocument.document_type == document_type)
            .order_by(QuotationDocument.uploaded_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_wechat_group_no(self, wechat_group_no: str) -> List[QuotationDocument]:
        """根据群编号查询资料"""
        query = (
            select(QuotationDocument)
            .where(QuotationDocument.wechat_group_no == wechat_group_no)
            .order_by(QuotationDocument.uploaded_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_related_item_id(self, related_item_id: str) -> List[QuotationDocument]:
        """根据关联的报价单明细ID查询资料"""
        query = (
            select(QuotationDocument)
            .where(QuotationDocument.related_item_id == related_item_id)
            .order_by(QuotationDocument.uploaded_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
