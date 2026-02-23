"""
合同文档扩展仓库
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from common.models.doc_contract_ext import DocContractExt
from common.utils.repository import BaseRepository


class DocContractExtRepository(BaseRepository[DocContractExt]):
    """合同文档扩展仓库"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, DocContractExt)

    async def get_by_document_id(self, document_id: str) -> Optional[DocContractExt]:
        """根据文档ID查询"""
        query = select(DocContractExt).where(DocContractExt.document_id == document_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_contract_id(self, contract_id: str) -> Optional[DocContractExt]:
        """根据合同ID查询"""
        query = select(DocContractExt).where(DocContractExt.contract_id == contract_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
