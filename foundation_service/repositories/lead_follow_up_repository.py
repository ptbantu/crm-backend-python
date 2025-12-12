"""
线索跟进记录数据访问层
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import joinedload
from common.models import LeadFollowUp
from common.models import User
from common.utils.repository import BaseRepository


class LeadFollowUpRepository(BaseRepository[LeadFollowUp]):
    """线索跟进记录仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, LeadFollowUp)
    
    async def get_by_lead_id(self, lead_id: str) -> List[Tuple[LeadFollowUp, Optional[str]]]:
        """根据线索ID查询所有跟进记录，同时获取创建人名字"""
        query = (
            select(LeadFollowUp, User.display_name, User.username)
            .outerjoin(User, LeadFollowUp.created_by == User.id)
            .where(LeadFollowUp.lead_id == lead_id)
            .order_by(desc(LeadFollowUp.follow_up_date))
        )
        result = await self.db.execute(query)
        # 返回 (LeadFollowUp, created_by_name) 元组列表
        records = []
        for row in result.all():
            follow_up = row[0]
            display_name = row[1]
            username = row[2]
            created_by_name = display_name if display_name else username
            records.append((follow_up, created_by_name))
        return records

