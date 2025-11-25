"""
Order and Workflow Service 依赖注入
"""
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

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


def get_current_user_id(request: Request) -> Optional[str]:
    """
    从请求中获取当前用户ID（由 Gateway Service 通过 HTTP 头传递）
    
    Args:
        request: FastAPI Request 对象
        
    Returns:
        用户ID或None
    """
    # 优先从 HTTP 头获取（Gateway Service 转发时设置）
    user_id = request.headers.get("X-User-Id")
    if user_id:
        return user_id
    # 兼容从 request.state 获取（直接访问时）
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return user_id
    return None


def get_current_user_roles(request: Request) -> List[str]:
    """
    从请求中获取当前用户角色（由 Gateway Service 通过 HTTP 头传递）
    
    Args:
        request: FastAPI Request 对象
        
    Returns:
        角色列表
    """
    # 优先从 HTTP 头获取（Gateway Service 转发时设置）
    roles_header = request.headers.get("X-User-Roles")
    if roles_header:
        return [role.strip() for role in roles_header.split(",") if role.strip()]
    # 兼容从 request.state 获取（直接访问时）
    roles = getattr(request.state, "roles", [])
    return roles if isinstance(roles, list) else []


def get_current_organization_id(request: Request) -> Optional[str]:
    """
    从请求中获取当前组织ID（由 Gateway Service 通过 HTTP 头传递）
    
    Args:
        request: FastAPI Request 对象
        
    Returns:
        组织ID或None
    """
    # 优先从 HTTP 头获取
    org_id = request.headers.get("X-Organization-Id") or request.headers.get("Organization-Id")
    if org_id:
        return org_id
    # 兼容从 request.state 获取
    org_id = getattr(request.state, "organization_id", None)
    if org_id:
        return org_id
    return None


async def require_auth(request: Request) -> str:
    """
    要求认证（必须登录）
    
    Args:
        request: FastAPI Request 对象
        
    Returns:
        用户ID
        
    Raises:
        HTTPException: 如果未认证
    """
    user_id = get_current_user_id(request)
    if user_id is None:
        logger.warning("未认证的请求")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要认证"
        )
    return user_id

