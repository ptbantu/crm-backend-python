"""
文档审批服务
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from common.models.crm_document import DocumentStatusEnum
from foundation_service.repositories.crm_document_repository import CrmDocumentRepository
from foundation_service.schemas.crm_document import (
    CrmDocumentResponse,
    DocumentSubmitRequest,
    DocumentApproveRequest,
    DocumentRejectRequest,
)
from common.utils.logger import get_logger
from common.exceptions import BusinessException

logger = get_logger(__name__)


class DocumentApprovalService:
    """文档审批服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.document_repo = CrmDocumentRepository(db)

    async def submit_for_approval(
        self,
        document_id: str,
        request: DocumentSubmitRequest,
        submitted_by: Optional[str] = None
    ) -> CrmDocumentResponse:
        """提交审批"""
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            raise BusinessException(detail="文档不存在", status_code=404)

        # 验证状态
        if document.status != DocumentStatusEnum.DRAFT:
            raise BusinessException(detail="只有草稿状态的文档可以提交审批", status_code=400)

        # 更新状态
        document.status = DocumentStatusEnum.PENDING_APPROVAL
        document.submitted_at = datetime.now()
        document.submitted_by = submitted_by

        await self.document_repo.update(document)
        await self.db.commit()
        await self.db.refresh(document)

        logger.info(f"文档提交审批: {document.document_no}")

        document_with_ext = await self.document_repo.get_with_extensions(document.id)
        return CrmDocumentResponse.model_validate(document_with_ext)

    async def approve_document(
        self,
        document_id: str,
        request: DocumentApproveRequest,
        approved_by: Optional[str] = None
    ) -> CrmDocumentResponse:
        """审批通过"""
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            raise BusinessException(detail="文档不存在", status_code=404)

        # 验证状态
        if document.status != DocumentStatusEnum.PENDING_APPROVAL:
            raise BusinessException(detail="只有待审批状态的文档可以审批", status_code=400)

        # 更新状态
        document.status = DocumentStatusEnum.APPROVED
        document.approved_at = datetime.now()
        document.approved_by = approved_by

        await self.document_repo.update(document)
        await self.db.commit()
        await self.db.refresh(document)

        logger.info(f"文档审批通过: {document.document_no}")

        document_with_ext = await self.document_repo.get_with_extensions(document.id)
        return CrmDocumentResponse.model_validate(document_with_ext)

    async def reject_document(
        self,
        document_id: str,
        request: DocumentRejectRequest,
        rejected_by: Optional[str] = None
    ) -> CrmDocumentResponse:
        """拒绝文档"""
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            raise BusinessException(detail="文档不存在", status_code=404)

        # 验证状态
        if document.status != DocumentStatusEnum.PENDING_APPROVAL:
            raise BusinessException(detail="只有待审批状态的文档可以拒绝", status_code=400)

        # 更新状态
        document.status = DocumentStatusEnum.REJECTED
        document.rejected_at = datetime.now()
        document.rejected_by = rejected_by
        document.rejection_reason = request.rejection_reason

        await self.document_repo.update(document)
        await self.db.commit()
        await self.db.refresh(document)

        logger.info(f"文档被拒绝: {document.document_no}, 原因: {request.rejection_reason}")

        document_with_ext = await self.document_repo.get_with_extensions(document.id)
        return CrmDocumentResponse.model_validate(document_with_ext)
