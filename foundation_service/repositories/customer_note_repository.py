"""
客户备注数据访问层
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import joinedload
from common.models import CustomerNote, User
from common.utils.repository import BaseRepository


class CustomerNoteRepository(BaseRepository[CustomerNote]):
    """客户备注仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, CustomerNote)
    
    async def get_by_customer_id(self, customer_id: str) -> List[Tuple[CustomerNote, Optional[str]]]:
        """根据客户ID查询所有备注，同时获取创建人名字"""
        query = (
            select(CustomerNote, User.display_name, User.username)
            .outerjoin(User, CustomerNote.created_by == User.id)
            .where(CustomerNote.customer_id == customer_id)
            .order_by(desc(CustomerNote.created_at))
        )
        result = await self.db.execute(query)
        # 返回 (CustomerNote, created_by_name) 元组列表
        records = []
        for row in result.all():
            note = row[0]
            display_name = row[1]
            username = row[2]
            created_by_name = display_name if display_name else username
            records.append((note, created_by_name))
        return records
    
    async def get_important_by_customer_id(self, customer_id: str) -> List[CustomerNote]:
        """获取客户的重要备注"""
        query = (
            select(CustomerNote)
            .where(
                CustomerNote.customer_id == customer_id,
                CustomerNote.is_important == True
            )
            .order_by(desc(CustomerNote.created_at))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

