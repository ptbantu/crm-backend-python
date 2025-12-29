"""
订单回款 API 路由
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
from foundation_service.services.order_payment_service import OrderPaymentService
from foundation_service.schemas.order_payment import (
    OrderPaymentCreateRequest,
    OrderPaymentResponse,
    PaymentConfirmationRequest,
    OrderPaymentListResponse,
)
from common.schemas.response import Result

router = APIRouter(prefix="/order-payments", tags=["订单回款"])


@router.post("", response_model=Result[OrderPaymentResponse], status_code=201)
async def create_order_payment(
    request: OrderPaymentCreateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """创建订单回款记录"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = OrderPaymentService(db)
    result = await service.create_payment(request)
    return Result.success(data=result, message="回款记录创建成功")


@router.get("/order/{order_id}", response_model=Result[OrderPaymentListResponse])
async def get_order_payments(
    order_id: str = Path(..., description="订单ID"),
    exclude_long_term: bool = Query(False, description="是否排除长周期"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """获取订单的回款列表"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = OrderPaymentService(db)
    result = await service.get_payment_list(order_id, exclude_long_term)
    return Result.success(data=result)


@router.post("/{payment_id}/confirm", response_model=Result[OrderPaymentResponse])
async def confirm_payment(
    payment_id: str = Path(..., description="回款记录ID"),
    request: PaymentConfirmationRequest = None,
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """确认回款"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    if not request:
        request = PaymentConfirmationRequest(payment_id=payment_id)
    else:
        request.payment_id = payment_id
    
    service = OrderPaymentService(db)
    result = await service.confirm_payment(request, user_id)
    return Result.success(data=result, message="回款确认成功")


@router.get("/order/{order_id}/revenue-status", response_model=Result[dict])
async def get_revenue_status(
    order_id: str = Path(..., description="订单ID"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """计算回款状态（用于销售收入确认）"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = OrderPaymentService(db)
    result = await service.calculate_revenue_status(order_id)
    return Result.success(data=result)
