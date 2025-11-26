"""
订单项数据访问层
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from common.models import OrderItem
from common.utils.repository import BaseRepository


class OrderItemRepository(BaseRepository[OrderItem]):
    """订单项仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, OrderItem)
    
    async def get_by_order_id(
        self,
        order_id: str,
        page: int = 1,
        size: int = 100
    ) -> Tuple[List[OrderItem], int]:
        """根据订单ID查询订单项列表"""
        # 查询总数
        count_query = select(func.count(OrderItem.id)).where(OrderItem.order_id == order_id)
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询列表
        query = (
            select(OrderItem)
            .where(OrderItem.order_id == order_id)
            .order_by(OrderItem.item_number)
            .offset((page - 1) * size)
            .limit(size)
        )
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return list(items), total
    
    async def get_by_order_id_all(self, order_id: str) -> List[OrderItem]:
        """根据订单ID查询所有订单项（不分页）"""
        query = (
            select(OrderItem)
            .where(OrderItem.order_id == order_id)
            .order_by(OrderItem.item_number)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_max_item_number(self, order_id: str) -> int:
        """获取订单的最大订单项序号"""
        query = select(func.max(OrderItem.item_number)).where(OrderItem.order_id == order_id)
        result = await self.db.execute(query)
        max_number = result.scalar()
        return max_number if max_number else 0
    
    async def calculate_order_total(self, order_id: str) -> float:
        """计算订单总金额（从订单项汇总）"""
        query = select(func.sum(OrderItem.item_amount)).where(OrderItem.order_id == order_id)
        result = await self.db.execute(query)
        total = result.scalar()
        return float(total) if total else 0.0

