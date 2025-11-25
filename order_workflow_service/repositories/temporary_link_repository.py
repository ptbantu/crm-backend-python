"""
临时链接数据访问层
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from order_workflow_service.models.temporary_link import TemporaryLink
from common.utils.repository import BaseRepository


class TemporaryLinkRepository(BaseRepository[TemporaryLink]):
    """临时链接仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, TemporaryLink)
    
    async def get_by_token(self, link_token: str) -> Optional[TemporaryLink]:
        """根据令牌查询临时链接"""
        query = select(TemporaryLink).where(
            and_(
                TemporaryLink.link_token == link_token,
                TemporaryLink.is_active == True
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def increment_access_count(self, link_id: str) -> Optional[TemporaryLink]:
        """增加访问次数"""
        link = await self.get_by_id(link_id)
        if not link:
            return None
        
        link.current_access_count += 1
        await self.db.commit()
        await self.db.refresh(link)
        return link

