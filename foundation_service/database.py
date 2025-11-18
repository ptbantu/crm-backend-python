"""
Foundation Service 数据库连接
使用公共数据库模块
"""
from sqlalchemy.ext.asyncio import AsyncSession
from foundation_service.config import settings
from common.database import (
    Base,
    init_database,
    get_db as common_get_db,
    get_async_session_local,
    init_db as common_init_db,
)

# 初始化数据库连接
init_database(settings.DATABASE_URL, settings.DEBUG)

# 获取会话工厂（用于依赖注入）
AsyncSessionLocal = get_async_session_local()

# 导出 get_db 和 init_db（保持向后兼容）
get_db = common_get_db
init_db = common_init_db

