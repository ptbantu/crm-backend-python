"""
通知 API 路由
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from foundation_service.dependencies import (
    get_database_session,
    get_current_user_id,
)
from foundation_service.services.notification_service import NotificationService
from foundation_service.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    NotificationUnreadCountResponse,
)
from common.schemas.response import Result
from common.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("", response_model=Result[NotificationListResponse])
async def get_notification_list(
    request_obj: Request,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    is_read: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """获取通知列表"""
    user_id = get_current_user_id(request_obj)
    if not user_id:
        return Result.error(code=401, message="需要认证")
    
    service = NotificationService(db)
    result = await service.get_notification_list(user_id, page, size, is_read)
    return Result.success(data=result)


@router.put("/{notification_id}/read", response_model=Result[NotificationResponse])
async def mark_notification_as_read(
    notification_id: str,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """标记通知为已读"""
    user_id = get_current_user_id(request_obj)
    if not user_id:
        return Result.error(code=401, message="需要认证")
    
    service = NotificationService(db)
    result = await service.mark_as_read(notification_id, user_id)
    return Result.success(data=result, message="通知已标记为已读")


@router.put("/read-all", response_model=Result[dict])
async def mark_all_notifications_as_read(
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """全部标记为已读"""
    user_id = get_current_user_id(request_obj)
    if not user_id:
        return Result.error(code=401, message="需要认证")
    
    service = NotificationService(db)
    count = await service.mark_all_as_read(user_id)
    return Result.success(data={"updated_count": count}, message=f"已标记 {count} 条通知为已读")


@router.get("/unread-count", response_model=Result[NotificationUnreadCountResponse])
async def get_unread_count(
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """获取未读通知数量"""
    user_id = get_current_user_id(request_obj)
    if not user_id:
        return Result.error(code=401, message="需要认证")
    
    service = NotificationService(db)
    result = await service.get_unread_count(user_id)
    return Result.success(data=result)

