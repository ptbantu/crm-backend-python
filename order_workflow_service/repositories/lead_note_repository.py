"""
线索备注数据访问层
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from common.models import LeadNote
from common.utils.repository import BaseRepository


class LeadNoteRepository(BaseRepository[LeadNote]):
    """线索备注仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, LeadNote)
    
    async def get_by_lead_id(self, lead_id: str) -> List[LeadNote]:
        """根据线索ID查询所有备注"""
        query = select(LeadNote).where(
            LeadNote.lead_id == lead_id
        ).order_by(desc(LeadNote.created_at))
        result = await self.db.execute(query)
        return list(result.scalars().all())

