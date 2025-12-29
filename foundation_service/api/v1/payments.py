"""
收款 API 路由
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
from foundation_service.services.payment_service import PaymentService
from foundation_service.schemas.payment import (
    PaymentCreateRequest,
    PaymentUpdateRequest,
    PaymentResponse,
    PaymentListResponse,
    PaymentReviewRequest,
    PaymentVoucherResponse,
    CollectionTodoRequest,
    CollectionTodoResponse,
    CollectionTodoListResponse,
)
from common.schemas.response import Result

router = APIRouter(prefix="/payments", tags=["收款"])


@router.post("", response_model=Result[PaymentResponse], status_code=201)
async def create_payment(
    request: PaymentCreateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """创建收款记录"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = PaymentService(db)
    result = await service.create_payment(request, user_id)
    return Result.success(data=result, message="收款记录创建成功")


@router.get("", response_model=Result[PaymentListResponse])
async def get_payment_list(
    request_obj: Request,
    opportunity_id: Optional[str] = Query(None, description="商机ID"),
    status: Optional[str] = Query(None, description="状态"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取收款列表"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = PaymentService(db)
    result = await service.get_payment_list(opportunity_id, status, page, size)
    return Result.success(data=result)


@router.get("/{payment_id}", response_model=Result[PaymentResponse])
async def get_payment(
    payment_id: str = Path(..., description="收款记录ID"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """获取收款记录详情"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = PaymentService(db)
    result = await service.get_payment(payment_id)
    return Result.success(data=result)


@router.post("/{payment_id}/review", response_model=Result[PaymentResponse])
async def review_payment(
    payment_id: str = Path(..., description="收款记录ID"),
    request: PaymentReviewRequest = None,
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """财务核对收款"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    if not request:
        raise HTTPException(status_code=400, detail="请提供核对信息")
    request.payment_id = payment_id
    
    service = PaymentService(db)
    result = await service.review_payment(request, user_id)
    return Result.success(data=result, message="收款核对成功")


@router.post("/{payment_id}/vouchers", response_model=Result[PaymentVoucherResponse], status_code=201)
async def upload_voucher(
    payment_id: str = Path(..., description="收款记录ID"),
    file_name: str = Query(..., description="凭证文件名"),
    file_url: str = Query(..., description="OSS存储路径"),
    file_size_kb: Optional[int] = Query(None, description="文件大小（KB）"),
    is_primary: bool = Query(False, description="是否主要凭证"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """上传收款凭证"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = PaymentService(db)
    result = await service.upload_voucher(
        payment_id,
        file_name,
        file_url,
        file_size_kb,
        is_primary,
        user_id,
    )
    return Result.success(data=result, message="凭证上传成功")


@router.post("/todos", response_model=Result[CollectionTodoResponse], status_code=201)
async def create_collection_todo(
    request: CollectionTodoRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """创建收款待办事项"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = PaymentService(db)
    result = await service.create_collection_todo(request)
    return Result.success(data=result, message="待办事项创建成功")


@router.get("/todos", response_model=Result[CollectionTodoListResponse])
async def get_collection_todos(
    request_obj: Request,
    opportunity_id: Optional[str] = Query(None, description="商机ID"),
    assigned_to: Optional[str] = Query(None, description="分配人ID"),
    status: Optional[str] = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db),
):
    """获取收款待办事项列表"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = PaymentService(db)
    result = await service.get_collection_todos(opportunity_id, assigned_to, status)
    return Result.success(data=result)


@router.post("/todos/{todo_id}/complete", response_model=Result[CollectionTodoResponse])
async def complete_todo(
    todo_id: str = Path(..., description="待办事项ID"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """完成待办事项"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = PaymentService(db)
    result = await service.complete_todo(todo_id, user_id)
    return Result.success(data=result, message="待办事项完成成功")
