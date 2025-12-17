"""
客户等级价格数据访问层
"""
from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from common.models.customer_level_price import CustomerLevelPrice
from common.utils.repository import BaseRepository


class CustomerLevelPriceRepository(BaseRepository[CustomerLevelPrice]):
    """客户等级价格仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, CustomerLevelPrice)
    
    async def get_current_price(
        self,
        product_id: str,
        customer_level_code: str,
        currency: str
    ) -> Optional[CustomerLevelPrice]:
        """获取当前有效的客户等级价格"""
        now = datetime.now()
        query = select(CustomerLevelPrice).where(
            and_(
                CustomerLevelPrice.product_id == product_id,
                CustomerLevelPrice.customer_level_code == customer_level_code,
                CustomerLevelPrice.currency == currency,
                CustomerLevelPrice.effective_from <= now,
                or_(
                    CustomerLevelPrice.effective_to.is_(None),
                    CustomerLevelPrice.effective_to > now
                )
            )
        ).order_by(desc(CustomerLevelPrice.effective_from)).limit(1)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_product_prices(
        self,
        product_id: str,
        currency: Optional[str] = None
    ) -> List[CustomerLevelPrice]:
        """获取产品的所有客户等级价格"""
        now = datetime.now()
        query = select(CustomerLevelPrice).where(
            and_(
                CustomerLevelPrice.product_id == product_id,
                CustomerLevelPrice.effective_from <= now,
                or_(
                    CustomerLevelPrice.effective_to.is_(None),
                    CustomerLevelPrice.effective_to > now
                )
            )
        )
        
        if currency:
            query = query.where(CustomerLevelPrice.currency == currency)
        
        query = query.order_by(CustomerLevelPrice.customer_level_code)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_list(
        self,
        product_id: Optional[str] = None,
        customer_level_code: Optional[str] = None,
        currency: Optional[str] = None,
        page: int = 1,
        size: int = 10
    ) -> Tuple[List[CustomerLevelPrice], int]:
        """分页查询客户等级价格列表"""
        query = select(CustomerLevelPrice)
        conditions = []
        
        if product_id:
            conditions.append(CustomerLevelPrice.product_id == product_id)
        if customer_level_code:
            conditions.append(CustomerLevelPrice.customer_level_code == customer_level_code)
        if currency:
            conditions.append(CustomerLevelPrice.currency == currency)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 总数查询
        count_query = select(func.count()).select_from(CustomerLevelPrice)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页查询
        query = query.order_by(desc(CustomerLevelPrice.created_at))
        query = query.offset((page - 1) * size).limit(size)
        
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return list(items), total
