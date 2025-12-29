"""
订单回款服务
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
from decimal import Decimal
import uuid

from common.models.order_payment import OrderPayment
from common.models.order_payment import PaymentTypeEnum, PaymentStatusEnum
from common.models.order import Order
from foundation_service.repositories.order_payment_repository import OrderPaymentRepository
from foundation_service.repositories.order_repository import OrderRepository
from foundation_service.schemas.order_payment import (
    OrderPaymentCreateRequest,
    OrderPaymentResponse,
    PaymentConfirmationRequest,
    OrderPaymentListResponse,
)
from common.utils.logger import get_logger
from common.exceptions import BusinessException

logger = get_logger(__name__)


class OrderPaymentService:
    """订单回款服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_repo = OrderPaymentRepository(db)
        self.order_repo = OrderRepository(db)
    
    async def create_payment(
        self,
        request: OrderPaymentCreateRequest
    ) -> OrderPaymentResponse:
        """创建订单回款记录"""
        # 验证订单是否存在
        order = await self.order_repo.get_by_id(request.order_id)
        if not order:
            raise BusinessException(detail="订单不存在", status_code=404)
        
        try:
            payment = OrderPayment(
                id=str(uuid.uuid4()),
                order_id=request.order_id,
                order_item_id=request.order_item_id,
                payment_amount=request.payment_amount,
                payment_date=request.payment_date,
                payment_type=PaymentTypeEnum(request.payment_type),
                is_excluded_from_full=request.is_excluded_from_full,
                status=PaymentStatusEnum.PENDING,
                notes=request.notes,
            )
            await self.db.add(payment)
            await self.db.commit()
            await self.db.refresh(payment)
            
            return await self._to_response(payment)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"创建订单回款失败: {e}", exc_info=True)
            raise BusinessException(detail=f"创建订单回款失败: {str(e)}")
    
    async def get_payment(
        self,
        payment_id: str
    ) -> OrderPaymentResponse:
        """获取回款记录详情"""
        payment = await self.payment_repo.get_by_id(payment_id)
        if not payment:
            raise BusinessException(detail="回款记录不存在", status_code=404)
        
        return await self._to_response(payment)
    
    async def get_payment_list(
        self,
        order_id: str,
        exclude_long_term: bool = False
    ) -> OrderPaymentListResponse:
        """获取订单的回款列表"""
        payments = await self.payment_repo.get_by_order_id(order_id, include_excluded=not exclude_long_term)
        records = [await self._to_response(p) for p in payments]
        
        return OrderPaymentListResponse(
            records=records,
            total=len(records)
        )
    
    async def confirm_payment(
        self,
        request: PaymentConfirmationRequest,
        confirmed_by: str
    ) -> OrderPaymentResponse:
        """确认回款"""
        payment = await self.payment_repo.get_by_id(request.payment_id)
        if not payment:
            raise BusinessException(detail="回款记录不存在", status_code=404)
        
        if payment.status != PaymentStatusEnum.PENDING:
            raise BusinessException(detail="只能确认待确认的回款记录", status_code=400)
        
        try:
            payment.status = PaymentStatusEnum.CONFIRMED
            payment.confirmed_by = confirmed_by
            payment.confirmed_at = datetime.now()
            payment.notes = request.notes
            
            # 更新订单的回款状态
            await self._update_order_payment_status(payment.order_id)
            
            await self.db.commit()
            await self.db.refresh(payment)
            
            return await self._to_response(payment)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"确认回款失败: {e}", exc_info=True)
            raise BusinessException(detail=f"确认回款失败: {str(e)}")
    
    async def _update_order_payment_status(self, order_id: str) -> None:
        """更新订单的回款状态"""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            return
        
        # 计算已收总金额（排除长周期）
        total_received = await self.payment_repo.calculate_total_received(
            order_id,
            exclude_long_term=True
        )
        
        # 计算一次性服务总金额
        from common.models.order_item import OrderItem
        from sqlalchemy import select, func
        query = select(func.sum(OrderItem.item_amount)).where(
            OrderItem.order_id == order_id,
            OrderItem.item_type == "one_time"
        )
        result = await self.db.execute(query)
        one_time_total = result.scalar() or Decimal("0")
        
        # 更新订单状态
        if total_received >= float(one_time_total):
            order.is_fully_paid_excluding_long = True
    
    async def calculate_revenue_status(
        self,
        order_id: str
    ) -> dict:
        """计算回款状态（用于销售收入确认）"""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise BusinessException(detail="订单不存在", status_code=404)
        
        # 获取已确认的回款（排除长周期）
        confirmed_payments = await self.payment_repo.get_confirmed_payments(
            order_id,
            exclude_long_term=True
        )
        
        total_received = sum(float(p.payment_amount) for p in confirmed_payments)
        
        # 计算一次性服务总金额
        from common.models.order_item import OrderItem
        from sqlalchemy import select, func
        query = select(func.sum(OrderItem.item_amount)).where(
            OrderItem.order_id == order_id,
            OrderItem.item_type == "one_time"
        )
        result = await self.db.execute(query)
        one_time_total = result.scalar() or Decimal("0")
        
        is_fully_paid = total_received >= float(one_time_total)
        
        return {
            "order_id": order_id,
            "one_time_total": float(one_time_total),
            "total_received": total_received,
            "is_fully_paid_excluding_long": is_fully_paid,
            "order_status": order.is_fully_paid_excluding_long,
        }
    
    async def _to_response(self, payment: OrderPayment) -> OrderPaymentResponse:
        """转换为响应对象"""
        return OrderPaymentResponse(
            id=payment.id,
            order_id=payment.order_id,
            order_item_id=payment.order_item_id,
            payment_amount=payment.payment_amount,
            payment_date=payment.payment_date,
            payment_type=payment.payment_type.value if payment.payment_type else None,
            is_excluded_from_full=payment.is_excluded_from_full,
            status=payment.status.value if payment.status else None,
            confirmed_by=payment.confirmed_by,
            confirmed_at=payment.confirmed_at,
            notes=payment.notes,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
        )
