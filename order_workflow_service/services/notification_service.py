"""
通知服务
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from common.models import Notification
from order_workflow_service.repositories.notification_repository import NotificationRepository
from order_workflow_service.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    NotificationUnreadCountResponse,
)
from common.utils.logger import get_logger
from common.exceptions import BusinessException
import uuid

logger = get_logger(__name__)


class NotificationService:
    """通知服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = NotificationRepository(db)
    
    async def create_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        content: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
    ) -> Notification:
        """创建通知"""
        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            content=content,
            resource_type=resource_type,
            resource_id=resource_id,
            is_read=False,
        )
        
        await self.repository.create(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        
        return notification
    
    async def get_notification_list(
        self,
        user_id: str,
        page: int = 1,
        size: int = 20,
        is_read: Optional[bool] = None,
    ) -> NotificationListResponse:
        """获取通知列表"""
        notifications, total = await self.repository.get_by_user_id(
            user_id=user_id,
            page=page,
            size=size,
            is_read=is_read,
        )
        
        return NotificationListResponse(
            items=[NotificationResponse.model_validate(n) for n in notifications],
            total=total,
            page=page,
            size=size,
        )
    
    async def get_unread_count(self, user_id: str) -> NotificationUnreadCountResponse:
        """获取未读通知数量"""
        count = await self.repository.get_unread_count(user_id)
        return NotificationUnreadCountResponse(unread_count=count)
    
    async def mark_as_read(
        self,
        notification_id: str,
        user_id: str,
    ) -> NotificationResponse:
        """标记通知为已读"""
        notification = await self.repository.mark_as_read(notification_id, user_id)
        if not notification:
            raise BusinessException(detail="通知不存在或无权访问", status_code=404)
        
        return NotificationResponse.model_validate(notification)
    
    async def mark_all_as_read(self, user_id: str) -> int:
        """标记所有通知为已读"""
        count = await self.repository.mark_all_as_read(user_id)
        return count

