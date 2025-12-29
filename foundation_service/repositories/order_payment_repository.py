"""
订单回款仓库
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import joinedload
from common.models.order_payment import OrderPayment
from common.models.order_payment import PaymentStatusEnum
from common.utils.repository import BaseRepository


class OrderPaymentRepository(BaseRepository[OrderPayment]):
    """订单回款仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, OrderPayment)
    
    async def get_by_order_id(
        self,
        order_id: str,
        include_excluded: bool = True
    ) -> List[OrderPayment]:
        """根据订单ID查询所有回款记录"""
        query = (
            select(OrderPayment)
            .options(joinedload(OrderPayment.confirmer))
            .where(OrderPayment.order_id == order_id)
        )
        if not include_excluded:
            query = query.where(OrderPayment.is_excluded_from_full == False)
        
        query = query.order_by(OrderPayment.payment_date.desc())
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_by_status(
        self,
        order_id: str,
        status: PaymentStatusEnum
    ) -> List[OrderPayment]:
        """根据状态查询回款记录"""
        query = (
            select(OrderPayment)
            .where(OrderPayment.order_id == order_id)
            .where(OrderPayment.status == status)
            .order_by(OrderPayment.payment_date.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_confirmed_payments(
        self,
        order_id: str,
        exclude_long_term: bool = False
    ) -> List[OrderPayment]:
        """获取已确认的回款记录"""
        query = (
            select(OrderPayment)
            .where(OrderPayment.order_id == order_id)
            .where(OrderPayment.status == PaymentStatusEnum.CONFIRMED)
        )
        if exclude_long_term:
            query = query.where(OrderPayment.is_excluded_from_full == False)
        
        query = query.order_by(OrderPayment.payment_date.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def calculate_total_received(
        self,
        order_id: str,
        exclude_long_term: bool = False
    ) -> float:
        """计算已收总金额"""
        query = (
            select(func.sum(OrderPayment.payment_amount))
            .where(OrderPayment.order_id == order_id)
            .where(OrderPayment.status == PaymentStatusEnum.CONFIRMED)
        )
        if exclude_long_term:
            query = query.where(OrderPayment.is_excluded_from_full == False)
        
        result = await self.db.execute(query)
        total = result.scalar() or 0.0
        return float(total)
    
    async def get_monthly_payments(
        self,
        order_id: str,
        year: int,
        month: int
    ) -> List[OrderPayment]:
        """获取指定年月的月度回款记录"""
        from datetime import date
        query = (
            select(OrderPayment)
            .where(OrderPayment.order_id == order_id)
            .where(func.year(OrderPayment.payment_date) == year)
            .where(func.month(OrderPayment.payment_date) == month)
            .order_by(OrderPayment.payment_date.asc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
