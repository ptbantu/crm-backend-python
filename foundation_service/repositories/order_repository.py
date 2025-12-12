"""
订单数据访问层
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from datetime import date
from common.models import Order
from common.utils.repository import BaseRepository


class OrderRepository(BaseRepository[Order]):
    """订单仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Order)
    
    async def get_by_order_number(self, order_number: str) -> Optional[Order]:
        """根据订单号查询订单"""
        query = select(Order).where(Order.order_number == order_number)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def list_orders(
        self,
        page: int = 1,
        size: int = 20,
        customer_id: Optional[str] = None,
        sales_user_id: Optional[str] = None,
        status_code: Optional[str] = None,
        order_number: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Tuple[List[Order], int]:
        """查询订单列表"""
        # 构建查询条件
        conditions = []
        if customer_id:
            conditions.append(Order.customer_id == customer_id)
        if sales_user_id:
            conditions.append(Order.sales_user_id == sales_user_id)
        if status_code:
            conditions.append(Order.status_code == status_code)
        if order_number:
            conditions.append(Order.order_number.like(f"%{order_number}%"))
        if title:
            conditions.append(Order.title.like(f"%{title}%"))
        
        # 查询总数
        count_query = select(func.count(Order.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询列表
        query = (
            select(Order)
            .order_by(Order.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        if conditions:
            query = query.where(and_(*conditions))
        
        result = await self.db.execute(query)
        orders = result.scalars().all()
        
        return list(orders), total
    
    async def get_by_customer_id(
        self,
        customer_id: str,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[Order], int]:
        """根据客户ID查询订单列表"""
        return await self.list_orders(page=page, size=size, customer_id=customer_id)


