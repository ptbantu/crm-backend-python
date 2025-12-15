"""
通知数据访问层
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from common.models import Notification
from common.utils.repository import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    """通知仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Notification)
    
    async def get_by_user_id(
        self,
        user_id: str,
        page: int = 1,
        size: int = 20,
        is_read: Optional[bool] = None,
    ) -> Tuple[List[Notification], int]:
        """根据用户ID查询通知列表"""
        conditions = [Notification.user_id == user_id]
        
        if is_read is not None:
            conditions.append(Notification.is_read == is_read)
        
        # 查询总数
        count_query = select(func.count(Notification.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = select(Notification).where(and_(*conditions)).order_by(desc(Notification.created_at))
        query = query.offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        notifications = result.scalars().all()
        
        return list(notifications), total
    
    async def get_unread_count(self, user_id: str) -> int:
        """获取未读通知数量"""
        query = select(func.count(Notification.id)).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def mark_as_read(self, notification_id: str, user_id: str) -> Optional[Notification]:
        """标记通知为已读"""
        notification = await self.get_by_id(notification_id)
        if not notification or notification.user_id != user_id:
            return None
        
        from datetime import datetime
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(notification)
        return notification
    
    async def mark_all_as_read(self, user_id: str) -> int:
        """标记用户所有通知为已读"""
        from datetime import datetime
        from sqlalchemy import update
        
        stmt = update(Notification).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).values(
            is_read=True,
            read_at=datetime.utcnow()
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount or 0

