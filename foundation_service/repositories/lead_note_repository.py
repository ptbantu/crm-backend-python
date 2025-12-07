"""
线索备注数据访问层
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import joinedload
from common.models.lead_note import LeadNote
from common.models import User
from common.utils.repository import BaseRepository


class LeadNoteRepository(BaseRepository[LeadNote]):
    """线索备注仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, LeadNote)
    
    async def get_by_lead_id(self, lead_id: str) -> List[Tuple[LeadNote, Optional[str]]]:
        """根据线索ID查询所有备注，同时获取创建人名字"""
        query = (
            select(LeadNote, User.display_name, User.username)
            .outerjoin(User, LeadNote.created_by == User.id)
            .where(LeadNote.lead_id == lead_id)
            .order_by(desc(LeadNote.created_at))
        )
        result = await self.db.execute(query)
        # 返回 (LeadNote, created_by_name) 元组列表
        records = []
        for row in result.all():
            note = row[0]
            display_name = row[1]
            username = row[2]
            created_by_name = display_name if display_name else username
            records.append((note, created_by_name))
        return records

