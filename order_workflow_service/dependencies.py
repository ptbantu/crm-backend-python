"""
Order and Workflow Service 依赖注入
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from order_workflow_service.database import get_db
from common.utils.logger import get_logger

logger = get_logger(__name__)


async def get_database_session(
    db: AsyncSession = Depends(get_db)
) -> AsyncSession:
    """
    获取数据库会话
    
    Args:
        db: 数据库会话
        
    Returns:
        数据库会话
    """
    return db


def get_current_user_id() -> Optional[str]:
    """
    获取当前用户ID（从 JWT token 中提取）
    暂时返回 None，后续集成认证服务后实现
    
    Returns:
        用户ID或None
    """
    # TODO: 从 JWT token 中提取用户ID
    return None


async def require_auth(user_id: Optional[str] = Depends(get_current_user_id)) -> str:
    """
    要求认证（必须登录）
    
    Args:
        user_id: 当前用户ID
        
    Returns:
        用户ID
        
    Raises:
        HTTPException: 如果未认证
    """
    if user_id is None:
        logger.warning("未认证的请求")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要认证"
        )
    return user_id

