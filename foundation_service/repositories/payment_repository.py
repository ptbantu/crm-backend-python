"""
收款仓库
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import joinedload
from common.models.payment import Payment, PaymentVoucher, CollectionTodo
from common.models.payment import PaymentStatusEnum
from common.utils.repository import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    """收款仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Payment)
    
    async def get_by_opportunity_id(
        self,
        opportunity_id: str,
        include_vouchers: bool = True
    ) -> List[Payment]:
        """根据商机ID查询所有收款记录"""
        query = (
            select(Payment)
            .where(Payment.opportunity_id == opportunity_id)
        )
        if include_vouchers:
            query = query.options(joinedload(Payment.vouchers))
        
        query = query.order_by(desc(Payment.created_at))
        result = await self.db.execute(query)
        return list(result.unique().scalars().all()) if include_vouchers else list(result.scalars().all())
    
    async def get_by_payment_no(self, payment_no: str) -> Optional[Payment]:
        """根据收款编号查询"""
        query = (
            select(Payment)
            .options(
                joinedload(Payment.vouchers),
                joinedload(Payment.entity),
                joinedload(Payment.opportunity),
                joinedload(Payment.contract)
            )
            .where(Payment.payment_no == payment_no)
        )
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
    
    async def get_by_status(
        self,
        status: PaymentStatusEnum,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[Payment], int]:
        """根据状态查询收款列表"""
        conditions = [Payment.status == status]
        
        # 查询总数
        count_query = select(func.count(Payment.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (
            select(Payment)
            .options(joinedload(Payment.entity))
            .where(and_(*conditions))
            .order_by(desc(Payment.created_at))
            .offset((page - 1) * size)
            .limit(size)
        )
        result = await self.db.execute(query)
        payments = list(result.unique().scalars().all())
        
        return payments, total
    
    async def get_pending_review(self) -> List[Payment]:
        """获取待核对的收款记录"""
        query = (
            select(Payment)
            .options(joinedload(Payment.entity), joinedload(Payment.opportunity))
            .where(Payment.status == PaymentStatusEnum.PENDING_REVIEW)
            .order_by(Payment.created_at.asc())
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_final_payments(self, opportunity_id: str) -> List[Payment]:
        """获取尾款记录"""
        query = (
            select(Payment)
            .where(Payment.opportunity_id == opportunity_id)
            .where(Payment.is_final_payment == True)
            .order_by(desc(Payment.created_at))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def calculate_total_received(self, opportunity_id: str) -> float:
        """计算已收总金额"""
        query = (
            select(func.sum(Payment.amount))
            .where(Payment.opportunity_id == opportunity_id)
            .where(Payment.status == PaymentStatusEnum.CONFIRMED)
        )
        result = await self.db.execute(query)
        total = result.scalar() or 0.0
        return float(total)


class PaymentVoucherRepository(BaseRepository[PaymentVoucher]):
    """收款凭证仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, PaymentVoucher)
    
    async def get_by_payment_id(self, payment_id: str) -> List[PaymentVoucher]:
        """根据收款ID查询所有凭证"""
        query = (
            select(PaymentVoucher)
            .options(joinedload(PaymentVoucher.uploader))
            .where(PaymentVoucher.payment_id == payment_id)
            .order_by(PaymentVoucher.is_primary.desc(), PaymentVoucher.uploaded_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_primary_voucher(self, payment_id: str) -> Optional[PaymentVoucher]:
        """获取主要凭证"""
        query = (
            select(PaymentVoucher)
            .where(PaymentVoucher.payment_id == payment_id)
            .where(PaymentVoucher.is_primary == True)
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()


class CollectionTodoRepository(BaseRepository[CollectionTodo]):
    """收款待办事项仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, CollectionTodo)
    
    async def get_by_opportunity_id(
        self,
        opportunity_id: str,
        status: Optional[str] = None
    ) -> List[CollectionTodo]:
        """根据商机ID查询待办事项"""
        query = (
            select(CollectionTodo)
            .options(
                joinedload(CollectionTodo.assignee),
                joinedload(CollectionTodo.completer)
            )
            .where(CollectionTodo.opportunity_id == opportunity_id)
        )
        if status:
            query = query.where(CollectionTodo.status == status)
        
        query = query.order_by(CollectionTodo.due_date.asc(), CollectionTodo.created_at.asc())
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_by_assigned_to(
        self,
        assigned_to: str,
        status: Optional[str] = None
    ) -> List[CollectionTodo]:
        """根据分配人查询待办事项"""
        query = (
            select(CollectionTodo)
            .options(joinedload(CollectionTodo.opportunity))
            .where(CollectionTodo.assigned_to == assigned_to)
        )
        if status:
            query = query.where(CollectionTodo.status == status)
        else:
            query = query.where(CollectionTodo.status.in_(["pending", "in_progress"]))
        
        query = query.order_by(CollectionTodo.due_date.asc())
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_by_todo_type(
        self,
        opportunity_id: str,
        todo_type: str
    ) -> List[CollectionTodo]:
        """根据待办类型查询"""
        query = (
            select(CollectionTodo)
            .where(CollectionTodo.opportunity_id == opportunity_id)
            .where(CollectionTodo.todo_type == todo_type)
            .order_by(CollectionTodo.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
