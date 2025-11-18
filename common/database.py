"""
公共数据库连接和会话管理
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy.orm import declarative_base
from sqlalchemy import event, text
from typing import Optional
from common.utils.logger import get_logger

logger = get_logger(__name__)

# 声明基类（所有服务共享）
Base = declarative_base()

# 全局引擎（单例模式）
_engine: Optional[AsyncEngine] = None
_AsyncSessionLocal: Optional[async_sessionmaker] = None


def init_database(database_url: str, debug: bool = False) -> AsyncEngine:
    """
    初始化数据库连接
    
    Args:
        database_url: 数据库连接 URL（pymysql 格式）
        debug: 是否开启调试模式
    
    Returns:
        AsyncEngine: 异步数据库引擎
    """
    global _engine, _AsyncSessionLocal
    
    if _engine is not None:
        return _engine
    
    # 转换为 aiomysql 格式
    async_database_url = database_url.replace("mysql+pymysql://", "mysql+aiomysql://")
    
    # 确保连接字符串包含正确的字符集参数
    if "charset=" not in async_database_url:
        async_database_url += "&charset=utf8mb4" if "?" in async_database_url else "?charset=utf8mb4"
    if "use_unicode=" not in async_database_url:
        async_database_url += "&use_unicode=true"
    
    # 创建异步引擎
    _engine = create_async_engine(
        async_database_url,
        echo=debug,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        # aiomysql 连接参数，确保使用 UTF-8 编码
        connect_args={
            "charset": "utf8mb4",
            "use_unicode": True,
        } if "aiomysql" in async_database_url else {},
    )
    
    # 在连接建立后执行 SET NAMES 命令，确保字符集正确
    @event.listens_for(_engine.sync_engine, "connect")
    def set_charset(dbapi_conn, connection_record):
        """连接建立后设置字符集"""
        try:
            cursor = dbapi_conn.cursor()
            cursor.execute("SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute("SET character_set_client = utf8mb4")
            cursor.execute("SET character_set_connection = utf8mb4")
            cursor.execute("SET character_set_results = utf8mb4")
            cursor.close()
            logger.debug("数据库连接字符集已设置为 utf8mb4")
        except Exception as e:
            logger.error(f"设置字符集失败: {e}", exc_info=True)
    
    # 创建会话工厂
    _AsyncSessionLocal = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    logger.info(f"数据库连接已初始化: {database_url.split('@')[1] if '@' in database_url else 'unknown'}")
    
    return _engine


def get_async_session_local() -> async_sessionmaker:
    """
    获取异步会话工厂
    
    Returns:
        async_sessionmaker: 异步会话工厂
    
    Raises:
        RuntimeError: 如果数据库未初始化
    """
    if _AsyncSessionLocal is None:
        raise RuntimeError("数据库未初始化，请先调用 init_database()")
    return _AsyncSessionLocal


async def get_db() -> AsyncSession:
    """
    获取数据库会话（依赖注入）
    
    Yields:
        AsyncSession: 数据库会话
    """
    session_local = get_async_session_local()
    async with session_local() as session:
        try:
            # 每次会话开始时设置字符集，确保数据正确编码
            await session.execute(text("SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci"))
            await session.execute(text("SET character_set_client = utf8mb4"))
            await session.execute(text("SET character_set_connection = utf8mb4"))
            await session.execute(text("SET character_set_results = utf8mb4"))
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    初始化数据库（创建表）
    
    Raises:
        RuntimeError: 如果数据库未初始化
    """
    if _engine is None:
        raise RuntimeError("数据库未初始化，请先调用 init_database()")
    
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

