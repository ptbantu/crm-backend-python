"""
CRM文档仓库
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, or_
from sqlalchemy.orm import joinedload
from common.models.crm_document import CrmDocument, DocumentTypeEnum, DocumentStatusEnum
from common.utils.repository import BaseRepository


class CrmDocumentRepository(BaseRepository[CrmDocument]):
    """CRM文档仓库"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, CrmDocument)

    async def get_by_document_no(self, document_no: str) -> Optional[CrmDocument]:
        """根据文档编号查询"""
        query = (
            select(CrmDocument)
            .options(
                joinedload(CrmDocument.entity),
                joinedload(CrmDocument.template),
                joinedload(CrmDocument.opportunity),
                joinedload(CrmDocument.contract),
                joinedload(CrmDocument.invoice)
            )
            .where(CrmDocument.document_no == document_no)
        )
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_by_opportunity_id(
        self,
        opportunity_id: str,
        document_type: Optional[DocumentTypeEnum] = None
    ) -> List[CrmDocument]:
        """根据商机ID查询文档"""
        conditions = [CrmDocument.opportunity_id == opportunity_id]

        if document_type:
            conditions.append(CrmDocument.document_type == document_type)

        query = (
            select(CrmDocument)
            .options(
                joinedload(CrmDocument.entity),
                joinedload(CrmDocument.template)
            )
            .where(and_(*conditions))
            .order_by(desc(CrmDocument.created_at))
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())

    async def get_by_group_id(self, group_id: str) -> List[CrmDocument]:
        """根据文档组ID查询所有关联文档"""
        query = (
            select(CrmDocument)
            .options(
                joinedload(CrmDocument.entity),
                joinedload(CrmDocument.template)
            )
            .where(CrmDocument.group_id == group_id)
            .order_by(CrmDocument.created_at)
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())

    async def get_pending_approval(
        self,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[CrmDocument], int]:
        """查询待审批文档列表"""
        conditions = [CrmDocument.status == DocumentStatusEnum.PENDING_APPROVAL]

        # 查询总数
        count_query = select(func.count(CrmDocument.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # 查询数据
        query = (
            select(CrmDocument)
            .options(
                joinedload(CrmDocument.entity),
                joinedload(CrmDocument.opportunity),
                joinedload(CrmDocument.submitter)
            )
            .where(and_(*conditions))
            .order_by(desc(CrmDocument.submitted_at))
            .offset((page - 1) * size)
            .limit(size)
        )
        result = await self.db.execute(query)
        documents = list(result.unique().scalars().all())

        return documents, total

    async def list_documents(
        self,
        document_type: Optional[DocumentTypeEnum] = None,
        status: Optional[DocumentStatusEnum] = None,
        entity_id: Optional[str] = None,
        opportunity_id: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[CrmDocument], int]:
        """分页查询文档列表"""
        conditions = []

        if document_type:
            conditions.append(CrmDocument.document_type == document_type)
        if status:
            conditions.append(CrmDocument.status == status)
        if entity_id:
            conditions.append(CrmDocument.entity_id == entity_id)
        if opportunity_id:
            conditions.append(CrmDocument.opportunity_id == opportunity_id)

        # 查询总数
        count_query = select(func.count(CrmDocument.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # 查询数据
        query = (
            select(CrmDocument)
            .options(
                joinedload(CrmDocument.entity),
                joinedload(CrmDocument.opportunity)
            )
        )
        if conditions:
            query = query.where(and_(*conditions))
        query = (
            query
            .order_by(desc(CrmDocument.created_at))
            .offset((page - 1) * size)
            .limit(size)
        )
        result = await self.db.execute(query)
        documents = list(result.unique().scalars().all())

        return documents, total

    async def get_with_extensions(self, document_id: str) -> Optional[CrmDocument]:
        """查询文档及其扩展信息"""
        query = (
            select(CrmDocument)
            .options(
                joinedload(CrmDocument.entity),
                joinedload(CrmDocument.template),
                joinedload(CrmDocument.opportunity),
                joinedload(CrmDocument.contract),
                joinedload(CrmDocument.invoice),
                joinedload(CrmDocument.contract_ext),
                joinedload(CrmDocument.invoice_ext),
                joinedload(CrmDocument.submitter),
                joinedload(CrmDocument.approver),
                joinedload(CrmDocument.sealer)
            )
            .where(CrmDocument.id == document_id)
        )
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
