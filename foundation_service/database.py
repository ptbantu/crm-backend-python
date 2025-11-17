"""
数据库连接和会话管理
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import event, text
from sqlalchemy.pool import Pool
from foundation_service.config import settings
from common.utils.logger import get_logger

logger = get_logger(__name__)

# 创建异步引擎
# 注意：SQLAlchemy 2.0 异步需要使用 aiomysql
database_url = settings.DATABASE_URL.replace("mysql+pymysql://", "mysql+aiomysql://")
# 确保连接字符串包含正确的字符集参数
if "charset=" not in database_url:
    database_url += "&charset=utf8mb4" if "?" in database_url else "?charset=utf8mb4"
if "use_unicode=" not in database_url:
    database_url += "&use_unicode=true"

engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    # aiomysql 连接参数，确保使用 UTF-8 编码
    connect_args={
        "charset": "utf8mb4",
        "use_unicode": True,
    } if "aiomysql" in database_url else {},
)


# 在连接建立后执行 SET NAMES 命令，确保字符集正确
@event.listens_for(engine.sync_engine, "connect")
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
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 声明基类
Base = declarative_base()


async def get_db() -> AsyncSession:
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
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
    """初始化数据库（创建表）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

