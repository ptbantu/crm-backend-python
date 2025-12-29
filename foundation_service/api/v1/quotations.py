"""
报价单 API 路由
"""
from fastapi import APIRouter, Depends, Query, Request, HTTPException, Path
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from foundation_service.dependencies import get_current_organization_id
from foundation_service.database import get_db
from common.auth import (
    get_current_user_id_from_request as get_user_id_from_token,
    get_current_user_roles_from_request as get_user_roles_from_token,
)
from foundation_service.config import settings
from foundation_service.services.quotation_service import QuotationService
from foundation_service.schemas.quotation import (
    QuotationCreateRequest,
    QuotationUpdateRequest,
    QuotationResponse,
    QuotationListResponse,
    QuotationAcceptRequest,
    QuotationRejectRequest,
    QuotationDocumentResponse,
)
from common.schemas.response import Result
from common.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/quotations", tags=["报价单"])


@router.post("", response_model=Result[QuotationResponse], status_code=201)
async def create_quotation(
    request: QuotationCreateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """创建报价单"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = QuotationService(db)
    result = await service.create_quotation(request, user_id)
    return Result.success(data=result, message="报价单创建成功")


@router.get("", response_model=Result[QuotationListResponse])
async def get_quotation_list(
    request_obj: Request,
    opportunity_id: Optional[str] = Query(None, description="商机ID"),
    status: Optional[str] = Query(None, description="状态"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取报价单列表"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = QuotationService(db)
    result = await service.get_quotation_list(opportunity_id, status, page, size)
    return Result.success(data=result)


@router.get("/{quotation_id}", response_model=Result[QuotationResponse])
async def get_quotation(
    quotation_id: str = Path(..., description="报价单ID"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """获取报价单详情"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = QuotationService(db)
    result = await service.get_quotation(quotation_id)
    return Result.success(data=result)


@router.put("/{quotation_id}", response_model=Result[QuotationResponse])
async def update_quotation(
    quotation_id: str = Path(..., description="报价单ID"),
    request: QuotationUpdateRequest = None,
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """更新报价单"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = QuotationService(db)
    result = await service.update_quotation(quotation_id, request)
    return Result.success(data=result, message="报价单更新成功")


@router.post("/{quotation_id}/send", response_model=Result[QuotationResponse])
async def send_quotation(
    quotation_id: str = Path(..., description="报价单ID"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """发送报价单"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = QuotationService(db)
    result = await service.send_quotation(quotation_id, user_id)
    return Result.success(data=result, message="报价单发送成功")


@router.post("/{quotation_id}/accept", response_model=Result[QuotationResponse])
async def accept_quotation(
    quotation_id: str = Path(..., description="报价单ID"),
    request: QuotationAcceptRequest = None,
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """接受报价单"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    if not request:
        request = QuotationAcceptRequest(quotation_id=quotation_id)
    else:
        request.quotation_id = quotation_id
    
    service = QuotationService(db)
    result = await service.accept_quotation(request, user_id)
    return Result.success(data=result, message="报价单接受成功")


@router.post("/{quotation_id}/reject", response_model=Result[QuotationResponse])
async def reject_quotation(
    quotation_id: str = Path(..., description="报价单ID"),
    request: QuotationRejectRequest = None,
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """拒绝报价单"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    if not request:
        request = QuotationRejectRequest(quotation_id=quotation_id)
    else:
        request.quotation_id = quotation_id
    
    service = QuotationService(db)
    result = await service.reject_quotation(request)
    return Result.success(data=result, message="报价单拒绝成功")


@router.post("/{quotation_id}/generate-pdf", response_model=Result[QuotationResponse])
async def generate_quotation_pdf(
    quotation_id: str = Path(..., description="报价单ID"),
    template_id: Optional[str] = Query(None, description="模板ID"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """生成报价单PDF"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = QuotationService(db)
    result = await service.generate_pdf(quotation_id, template_id)
    return Result.success(data=result, message="报价单PDF生成成功")


@router.post("/{quotation_id}/documents", response_model=Result[QuotationDocumentResponse], status_code=201)
async def upload_quotation_document(
    quotation_id: str = Path(..., description="报价单ID"),
    document_type: str = Query(..., description="资料类型"),
    document_name: str = Query(..., description="资料文件名"),
    file_url: str = Query(..., description="存储路径（OSS链接）"),
    related_item_id: Optional[str] = Query(None, description="关联报价单明细行ID"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """上传报价单资料"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = QuotationService(db)
    result = await service.upload_document(
        quotation_id,
        document_type,
        document_name,
        file_url,
        user_id,
        related_item_id,
    )
    return Result.success(data=result, message="资料上传成功")
