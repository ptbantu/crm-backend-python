"""
通知相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class NotificationResponse(BaseModel):
    """通知响应"""
    id: str
    user_id: str
    notification_type: str
    title: str
    content: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """通知列表响应"""
    items: List[NotificationResponse]
    total: int
    page: int
    size: int


class NotificationUnreadCountResponse(BaseModel):
    """未读通知数量响应"""
    unread_count: int

