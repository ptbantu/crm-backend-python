"""
跟进状态配置数据访问层
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from order_workflow_service.models.follow_up_status import FollowUpStatus
from common.utils.repository import BaseRepository


class FollowUpStatusRepository(BaseRepository[FollowUpStatus]):
    """跟进状态配置仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, FollowUpStatus)
    
    async def get_by_code(self, code: str) -> Optional[FollowUpStatus]:
        """根据代码查询跟进状态"""
        query = select(FollowUpStatus).where(
            and_(
                FollowUpStatus.code == code,
                FollowUpStatus.is_active == True
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all_active(self) -> List[FollowUpStatus]:
        """获取所有激活的跟进状态（按排序顺序）"""
        query = select(FollowUpStatus).where(
            FollowUpStatus.is_active == True
        ).order_by(FollowUpStatus.sort_order.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

