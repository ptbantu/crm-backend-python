"""
合同文件仓库
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload
from common.models.contract import ContractDocument
from common.models.contract import ContractDocumentTypeEnum
from common.utils.repository import BaseRepository


class ContractDocumentRepository(BaseRepository[ContractDocument]):
    """合同文件仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ContractDocument)
    
    async def get_by_contract_id(self, contract_id: str) -> List[ContractDocument]:
        """根据合同ID查询所有文件"""
        query = (
            select(ContractDocument)
            .options(joinedload(ContractDocument.creator))
            .where(ContractDocument.contract_id == contract_id)
            .order_by(ContractDocument.document_type.asc(), ContractDocument.version.desc())
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_by_document_type(
        self,
        contract_id: str,
        document_type: ContractDocumentTypeEnum
    ) -> List[ContractDocument]:
        """根据文件类型查询（按版本倒序）"""
        query = (
            select(ContractDocument)
            .where(ContractDocument.contract_id == contract_id)
            .where(ContractDocument.document_type == document_type)
            .order_by(ContractDocument.version.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_latest_by_type(
        self,
        contract_id: str,
        document_type: ContractDocumentTypeEnum
    ) -> Optional[ContractDocument]:
        """获取指定类型的最新版本文件"""
        query = (
            select(ContractDocument)
            .where(ContractDocument.contract_id == contract_id)
            .where(ContractDocument.document_type == document_type)
            .order_by(ContractDocument.version.desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_next_version(
        self,
        contract_id: str,
        document_type: ContractDocumentTypeEnum
    ) -> int:
        """获取下一个版本号"""
        from sqlalchemy import func as sql_func
        query = (
            select(sql_func.max(ContractDocument.version))
            .where(ContractDocument.contract_id == contract_id)
            .where(ContractDocument.document_type == document_type)
        )
        result = await self.db.execute(query)
        max_version = result.scalar() or 0
        return max_version + 1
