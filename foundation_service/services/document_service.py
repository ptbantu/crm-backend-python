"""
文档服务（主协调器）
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from common.models.crm_document import DocumentTypeEnum, DocumentStatusEnum
from foundation_service.repositories.crm_document_repository import CrmDocumentRepository
from foundation_service.services.document_generation_service import DocumentGenerationService
from foundation_service.services.document_approval_service import DocumentApprovalService
from foundation_service.services.document_seal_service import DocumentSealService
from foundation_service.services.document_conversion_service import DocumentConversionService
from foundation_service.services.document_storage_service import DocumentStorageService
from foundation_service.schemas.crm_document import (
    DocumentGenerateRequest,
    DocumentSubmitRequest,
    DocumentApproveRequest,
    DocumentRejectRequest,
    DocumentSealRequest,
    DocumentFinalizeRequest,
    CrmDocumentResponse,
    CrmDocumentListResponse,
)
from common.utils.logger import get_logger
from common.exceptions import BusinessException

logger = get_logger(__name__)


class DocumentService:
    """文档服务（主协调器）"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.document_repo = CrmDocumentRepository(db)
        self.generation_service = DocumentGenerationService(db)
        self.approval_service = DocumentApprovalService(db)
        self.seal_service = DocumentSealService(db)
        self.conversion_service = DocumentConversionService(db)
        self.storage_service = DocumentStorageService(db)

    async def generate_document(
        self,
        request: DocumentGenerateRequest,
        created_by: Optional[str] = None
    ) -> CrmDocumentResponse:
        """生成文档"""
        return await self.generation_service.generate_document(request, created_by)

    async def get_document(self, document_id: str) -> CrmDocumentResponse:
        """获取文档详情"""
        document = await self.document_repo.get_with_extensions(document_id)
        if not document:
            raise BusinessException(detail="文档不存在", status_code=404)

        return CrmDocumentResponse.model_validate(document)

    async def list_documents(
        self,
        document_type: Optional[DocumentTypeEnum] = None,
        status: Optional[DocumentStatusEnum] = None,
        entity_id: Optional[str] = None,
        opportunity_id: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> CrmDocumentListResponse:
        """查询文档列表"""
        documents, total = await self.document_repo.list_documents(
            document_type=document_type,
            status=status,
            entity_id=entity_id,
            opportunity_id=opportunity_id,
            page=page,
            size=size
        )

        items = [CrmDocumentResponse.model_validate(d) for d in documents]
        return CrmDocumentListResponse(
            items=items,
            total=total,
            page=page,
            size=size
        )

    async def get_documents_by_opportunity(
        self,
        opportunity_id: str,
        document_type: Optional[DocumentTypeEnum] = None
    ) -> List[CrmDocumentResponse]:
        """根据商机ID查询文档"""
        documents = await self.document_repo.get_by_opportunity_id(
            opportunity_id=opportunity_id,
            document_type=document_type
        )

        return [CrmDocumentResponse.model_validate(d) for d in documents]

    async def get_documents_by_group(self, group_id: str) -> List[CrmDocumentResponse]:
        """根据文档组ID查询所有关联文档"""
        documents = await self.document_repo.get_by_group_id(group_id)
        return [CrmDocumentResponse.model_validate(d) for d in documents]

    async def get_pending_approval(
        self,
        page: int = 1,
        size: int = 20
    ) -> CrmDocumentListResponse:
        """查询待审批文档列表"""
        documents, total = await self.document_repo.get_pending_approval(
            page=page,
            size=size
        )

        items = [CrmDocumentResponse.model_validate(d) for d in documents]
        return CrmDocumentListResponse(
            items=items,
            total=total,
            page=page,
            size=size
        )

    async def submit_for_approval(
        self,
        document_id: str,
        request: DocumentSubmitRequest,
        submitted_by: Optional[str] = None
    ) -> CrmDocumentResponse:
        """提交审批"""
        return await self.approval_service.submit_for_approval(
            document_id=document_id,
            request=request,
            submitted_by=submitted_by
        )

    async def approve_document(
        self,
        document_id: str,
        request: DocumentApproveRequest,
        approved_by: Optional[str] = None
    ) -> CrmDocumentResponse:
        """审批通过"""
        return await self.approval_service.approve_document(
            document_id=document_id,
            request=request,
            approved_by=approved_by
        )

    async def reject_document(
        self,
        document_id: str,
        request: DocumentRejectRequest,
        rejected_by: Optional[str] = None
    ) -> CrmDocumentResponse:
        """拒绝文档"""
        return await self.approval_service.reject_document(
            document_id=document_id,
            request=request,
            rejected_by=rejected_by
        )

    async def seal_document(
        self,
        document_id: str,
        request: DocumentSealRequest,
        sealed_by: Optional[str] = None
    ) -> CrmDocumentResponse:
        """盖章文档"""
        return await self.seal_service.seal_document(
            document_id=document_id,
            request=request,
            sealed_by=sealed_by
        )

    async def finalize_document(
        self,
        document_id: str,
        request: DocumentFinalizeRequest
    ) -> CrmDocumentResponse:
        """最终化文档（转换为PDF/A）"""
        return await self.conversion_service.finalize_document(
            document_id=document_id,
            request=request
        )

    async def download_document(self, document_id: str) -> tuple[bytes, str]:
        """下载文档"""
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            raise BusinessException(detail="文档不存在", status_code=404)

        # 优先下载最终版本，否则下载草稿
        oss_key = document.final_oss_key or document.draft_oss_key
        if not oss_key:
            raise BusinessException(detail="文档文件不存在", status_code=404)

        # 从OSS下载文件
        file_content = await self.storage_service.download_from_oss(oss_key)

        # 确定文件名
        file_extension = ".pdf" if document.final_oss_key else ".docx"
        file_name = f"{document.document_no}{file_extension}"

        return file_content, file_name

    async def get_download_url(self, document_id: str, expires: int = 604800) -> str:
        """获取文档下载URL（签名URL，默认7天过期）"""
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            raise BusinessException(detail="文档不存在", status_code=404)

        # 优先使用最终版本
        oss_key = document.final_oss_key or document.draft_oss_key
        if not oss_key:
            raise BusinessException(detail="文档文件不存在", status_code=404)

        # 生成签名URL
        signed_url = await self.storage_service.get_signed_url(oss_key, expires)
        return signed_url
