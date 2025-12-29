"""
发票 API 路由
"""
from fastapi import APIRouter, Depends, Query, Request, HTTPException, Path
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from foundation_service.database import get_db
from common.auth import (
    get_current_user_id_from_request as get_user_id_from_token,
)
from foundation_service.config import settings
from foundation_service.services.invoice_service import InvoiceService
from foundation_service.schemas.invoice import (
    InvoiceCreateRequest,
    InvoiceUpdateRequest,
    InvoiceResponse,
    InvoiceListResponse,
    InvoiceFileResponse,
)
from common.schemas.response import Result

router = APIRouter(prefix="/invoices", tags=["发票"])


@router.post("", response_model=Result[InvoiceResponse], status_code=201)
async def create_invoice(
    request: InvoiceCreateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """创建发票"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = InvoiceService(db)
    result = await service.create_invoice(request, user_id)
    return Result.success(data=result, message="发票创建成功")


@router.get("", response_model=Result[InvoiceListResponse])
async def get_invoice_list(
    request_obj: Request,
    contract_id: Optional[str] = Query(None, description="合同ID"),
    opportunity_id: Optional[str] = Query(None, description="商机ID"),
    status: Optional[str] = Query(None, description="状态"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取发票列表"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = InvoiceService(db)
    result = await service.get_invoice_list(contract_id, opportunity_id, status, page, size)
    return Result.success(data=result)


@router.get("/{invoice_id}", response_model=Result[InvoiceResponse])
async def get_invoice(
    invoice_id: str = Path(..., description="发票ID"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """获取发票详情"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = InvoiceService(db)
    result = await service.get_invoice(invoice_id)
    return Result.success(data=result)


@router.post("/{invoice_id}/issue", response_model=Result[InvoiceResponse])
async def issue_invoice(
    invoice_id: str = Path(..., description="发票ID"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """开具发票"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = InvoiceService(db)
    result = await service.issue_invoice(invoice_id)
    return Result.success(data=result, message="发票开具成功")


@router.post("/{invoice_id}/upload", response_model=Result[InvoiceFileResponse], status_code=201)
async def upload_invoice_file(
    invoice_id: str = Path(..., description="发票ID"),
    file_name: str = Query(..., description="文件名"),
    file_url: str = Query(..., description="OSS存储路径"),
    file_size_kb: Optional[int] = Query(None, description="文件大小（KB）"),
    is_primary: bool = Query(True, description="是否主要文件"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """上传发票文件"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = InvoiceService(db)
    result = await service.upload_invoice_file(
        invoice_id,
        file_name,
        file_url,
        file_size_kb,
        is_primary,
        user_id,
    )
    return Result.success(data=result, message="发票文件上传成功")


@router.post("/{invoice_id}/send", response_model=Result[InvoiceResponse])
async def send_invoice(
    invoice_id: str = Path(..., description="发票ID"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """发送发票"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = InvoiceService(db)
    result = await service.send_invoice(invoice_id)
    return Result.success(data=result, message="发票发送成功")
