"""
线索跟进记录数据访问层
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from order_workflow_service.models import LeadFollowUp
from common.utils.repository import BaseRepository


class LeadFollowUpRepository(BaseRepository[LeadFollowUp]):
    """线索跟进记录仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, LeadFollowUp)
    
    async def get_by_lead_id(self, lead_id: str) -> List[LeadFollowUp]:
        """根据线索ID查询所有跟进记录"""
        query = select(LeadFollowUp).where(
            LeadFollowUp.lead_id == lead_id
        ).order_by(desc(LeadFollowUp.follow_up_date))
        result = await self.db.execute(query)
        return list(result.scalars().all())

