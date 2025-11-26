"""
组织相关辅助函数
用于从用户ID获取组织ID
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, text
from common.utils.logger import get_logger

logger = get_logger(__name__)


async def get_user_organization_id(db: AsyncSession, user_id: str) -> Optional[str]:
    """
    从 organization_employees 表获取用户的主要组织ID
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        
    Returns:
        组织ID，如果用户没有主要组织则返回 None
    """
    try:
        # 直接使用 SQL 查询，避免跨服务模型依赖
        # 查询用户的主要组织（is_primary = true 且 is_active = true）
        query = text("""
            SELECT organization_id 
            FROM organization_employees 
            WHERE user_id = :user_id 
              AND is_primary = 1 
              AND is_active = 1 
            LIMIT 1
        """)
        result = await db.execute(query, {"user_id": user_id})
        row = result.fetchone()
        if row:
            return row[0]
        
        # 如果没有主要组织，尝试获取任意激活的组织
        query = text("""
            SELECT organization_id 
            FROM organization_employees 
            WHERE user_id = :user_id 
              AND is_active = 1 
            LIMIT 1
        """)
        result = await db.execute(query, {"user_id": user_id})
        row = result.fetchone()
        if row:
            logger.warning(f"用户 {user_id} 没有主要组织，使用第一个激活的组织: {row[0]}")
            return row[0]
        
        logger.warning(f"用户 {user_id} 没有找到任何组织")
        return None
    except Exception as e:
        logger.error(f"获取用户组织ID失败: {e}", exc_info=True)
        return None

