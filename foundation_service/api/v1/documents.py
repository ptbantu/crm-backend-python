"""
文档管理 API 端点
"""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import io

from common.database import get_db
from common.models.crm_document import DocumentTypeEnum, DocumentStatusEnum
from foundation_service.services.document_service import DocumentService
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

logger = get_logger(__name__)
router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/generate", response_model=CrmDocumentResponse)
async def generate_document(
    request: DocumentGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """生成文档"""
    service = DocumentService(db)
    return await service.generate_document(request, created_by=None)


@router.get("", response_model=CrmDocumentListResponse)
async def list_documents(
    document_type: Optional[DocumentTypeEnum] = Query(None, description="文档类型"),
    status: Optional[DocumentStatusEnum] = Query(None, description="文档状态"),
    entity_id: Optional[str] = Query(None, description="签约主体ID"),
    opportunity_id: Optional[str] = Query(None, description="商机ID"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """查询文档列表"""
    service = DocumentService(db)
    return await service.list_documents(
        document_type=document_type,
        status=status,
        entity_id=entity_id,
        opportunity_id=opportunity_id,
        page=page,
        size=size
    )


@router.get("/pending-approval", response_model=CrmDocumentListResponse)
async def get_pending_approval(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """查询待审批文档列表"""
    service = DocumentService(db)
    return await service.get_pending_approval(page=page, size=size)


@router.get("/by-opportunity/{opportunity_id}", response_model=list[CrmDocumentResponse])
async def get_documents_by_opportunity(
    opportunity_id: str,
    document_type: Optional[DocumentTypeEnum] = Query(None, description="文档类型"),
    db: AsyncSession = Depends(get_db)
):
    """根据商机ID查询文档"""
    service = DocumentService(db)
    return await service.get_documents_by_opportunity(
        opportunity_id=opportunity_id,
        document_type=document_type
    )


@router.get("/by-group/{group_id}", response_model=list[CrmDocumentResponse])
async def get_documents_by_group(
    group_id: str,
    db: AsyncSession = Depends(get_db)
):
    """根据文档组ID查询所有关联文档"""
    service = DocumentService(db)
    return await service.get_documents_by_group(group_id)


@router.get("/{document_id}", response_model=CrmDocumentResponse)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取文档详情"""
    service = DocumentService(db)
    return await service.get_document(document_id)


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """下载文档"""
    service = DocumentService(db)
    file_content, file_name = await service.download_document(document_id)

    return StreamingResponse(
        io.BytesIO(file_content),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
    )


@router.get("/{document_id}/preview")
async def get_download_url(
    document_id: str,
    expires: int = Query(604800, description="过期时间（秒），默认7天"),
    db: AsyncSession = Depends(get_db)
):
    """获取文档预览/下载URL"""
    service = DocumentService(db)
    signed_url = await service.get_download_url(document_id, expires)
    return {"url": signed_url}


@router.post("/{document_id}/submit", response_model=CrmDocumentResponse)
async def submit_for_approval(
    document_id: str,
    request: DocumentSubmitRequest,
    db: AsyncSession = Depends(get_db)
):
    """提交审批"""
    service = DocumentService(db)
    return await service.submit_for_approval(
        document_id=document_id,
        request=request,
        submitted_by=None
    )


@router.post("/{document_id}/approve", response_model=CrmDocumentResponse)
async def approve_document(
    document_id: str,
    request: DocumentApproveRequest,
    db: AsyncSession = Depends(get_db)
):
    """审批通过"""
    service = DocumentService(db)
    return await service.approve_document(
        document_id=document_id,
        request=request,
        approved_by=None
    )


@router.post("/{document_id}/reject", response_model=CrmDocumentResponse)
async def reject_document(
    document_id: str,
    request: DocumentRejectRequest,
    db: AsyncSession = Depends(get_db)
):
    """拒绝文档"""
    service = DocumentService(db)
    return await service.reject_document(
        document_id=document_id,
        request=request,
        rejected_by=None
    )


@router.post("/{document_id}/seal", response_model=CrmDocumentResponse)
async def seal_document(
    document_id: str,
    request: DocumentSealRequest,
    db: AsyncSession = Depends(get_db)
):
    """盖章文档"""
    service = DocumentService(db)
    return await service.seal_document(
        document_id=document_id,
        request=request,
        sealed_by=None
    )


@router.post("/{document_id}/finalize", response_model=CrmDocumentResponse)
async def finalize_document(
    document_id: str,
    request: DocumentFinalizeRequest,
    db: AsyncSession = Depends(get_db)
):
    """最终化文档（转换为PDF/A）"""
    service = DocumentService(db)
    return await service.finalize_document(
        document_id=document_id,
        request=request
    )
