"""
客户跟进记录数据访问层
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import joinedload
from common.models import CustomerFollowUp, User
from common.utils.repository import BaseRepository


class CustomerFollowUpRepository(BaseRepository[CustomerFollowUp]):
    """客户跟进记录仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, CustomerFollowUp)
    
    async def get_by_customer_id(self, customer_id: str) -> List[Tuple[CustomerFollowUp, Optional[str]]]:
        """根据客户ID查询所有跟进记录，同时获取创建人名字"""
        query = (
            select(CustomerFollowUp, User.display_name, User.username)
            .outerjoin(User, CustomerFollowUp.created_by == User.id)
            .where(CustomerFollowUp.customer_id == customer_id)
            .order_by(desc(CustomerFollowUp.follow_up_date))
        )
        result = await self.db.execute(query)
        # 返回 (CustomerFollowUp, created_by_name) 元组列表
        records = []
        for row in result.all():
            follow_up = row[0]
            display_name = row[1]
            username = row[2]
            created_by_name = display_name if display_name else username
            records.append((follow_up, created_by_name))
        return records
    
    async def get_latest_by_customer_id(self, customer_id: str) -> Optional[CustomerFollowUp]:
        """获取客户最新的跟进记录"""
        query = (
            select(CustomerFollowUp)
            .where(CustomerFollowUp.customer_id == customer_id)
            .order_by(desc(CustomerFollowUp.follow_up_date))
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

