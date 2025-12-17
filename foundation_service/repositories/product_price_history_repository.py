"""
产品价格历史数据访问层
"""
from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from common.models.product_price_history import ProductPriceHistory
from common.models.product_price import ProductPrice
from common.utils.repository import BaseRepository


class ProductPriceHistoryRepository(BaseRepository[ProductPrice]):
    """产品价格历史仓库（使用 ProductPrice 模型）"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ProductPrice)
    
    async def get_by_product_id(
        self,
        product_id: str,
        page: int = 1,
        size: int = 10,
        organization_id: Optional[str] = None
    ) -> Tuple[List[ProductPrice], int]:
        """根据产品ID查询价格历史（列格式：一条记录包含所有价格）"""
        query = select(ProductPrice).where(
            ProductPrice.product_id == product_id
        )
        
        # 组织ID筛选
        if organization_id is not None:
            query = query.where(ProductPrice.organization_id == organization_id)
        else:
            # 如果 organization_id 为 None，查询通用价格（organization_id 为 NULL）
            query = query.where(ProductPrice.organization_id.is_(None))
        
        # 总数查询
        count_query = select(func.count()).select_from(ProductPrice).where(
            ProductPrice.product_id == product_id
        )
        if organization_id is not None:
            count_query = count_query.where(ProductPrice.organization_id == organization_id)
        else:
            count_query = count_query.where(ProductPrice.organization_id.is_(None))
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页查询
        query = query.order_by(desc(ProductPrice.created_at))
        query = query.offset((page - 1) * size).limit(size)
        
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return list(items), total
    
    async def get_current_price(
        self,
        product_id: str,
        organization_id: Optional[str] = None
    ) -> Optional[ProductPrice]:
        """获取当前有效的价格（列格式：一条记录包含所有价格）"""
        now = datetime.now()
        query = select(ProductPrice).where(
            and_(
                ProductPrice.product_id == product_id,
                ProductPrice.effective_from <= now,
                or_(
                    ProductPrice.effective_to.is_(None),
                    ProductPrice.effective_to > now
                )
            )
        )
        
        # 组织ID筛选
        if organization_id is not None:
            query = query.where(ProductPrice.organization_id == organization_id)
        else:
            query = query.where(ProductPrice.organization_id.is_(None))
        
        query = query.order_by(desc(ProductPrice.effective_from)).limit(1)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_upcoming_prices(
        self,
        product_id: Optional[str] = None,
        hours_ahead: int = 24
    ) -> List[ProductPrice]:
        """获取即将生效的价格"""
        now = datetime.now()
        future_time = datetime.fromtimestamp(now.timestamp() + hours_ahead * 3600)
        
        query = select(ProductPrice).where(
            and_(
                ProductPrice.effective_from > now,
                ProductPrice.effective_from <= future_time
            )
        )
        
        if product_id:
            query = query.where(ProductPrice.product_id == product_id)
        
        query = query.order_by(ProductPrice.effective_from)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
