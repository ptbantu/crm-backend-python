"""
客户等级配置数据访问层
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from common.models import CustomerLevel
from common.utils.repository import BaseRepository


class CustomerLevelRepository(BaseRepository[CustomerLevel]):
    """客户等级配置仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, CustomerLevel)
    
    async def get_by_code(self, code: str) -> Optional[CustomerLevel]:
        """根据代码查询客户等级"""
        query = select(CustomerLevel).where(
            and_(
                CustomerLevel.code == code,
                CustomerLevel.is_active == True
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all_active(self) -> List[CustomerLevel]:
        """获取所有激活的客户等级（按排序顺序）"""
        query = select(CustomerLevel).where(
            CustomerLevel.is_active == True
        ).order_by(CustomerLevel.sort_order.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

