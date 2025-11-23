"""
MongoDB 连接客户端
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from common.utils.logger import get_logger

logger = get_logger(__name__)

# 全局 MongoDB 客户端（单例模式）
_mongodb_client: Optional[AsyncIOMotorClient] = None
_mongodb_database: Optional[AsyncIOMotorDatabase] = None


def init_mongodb(
    host: str = "mongodb",  # 使用短地址（同一 namespace 内），完整地址：mongodb.default.svc.cluster.local
    port: int = 27017,
    database: str = "bantu_crm",
    username: Optional[str] = None,
    password: Optional[str] = None,
    auth_source: str = "bantu_crm",
    max_pool_size: int = 20,
    min_pool_size: int = 5,
    **kwargs
) -> AsyncIOMotorDatabase:
    """
    初始化 MongoDB 连接
    
    Args:
        host: MongoDB 主机地址
        port: MongoDB 端口
        database: 数据库名称
        username: 用户名
        password: 密码
        auth_source: 认证数据库
        max_pool_size: 连接池最大连接数
        min_pool_size: 连接池最小连接数
        **kwargs: 其他 MongoDB 连接参数
    
    Returns:
        AsyncIOMotorDatabase: MongoDB 数据库实例
    """
    global _mongodb_client, _mongodb_database
    
    if _mongodb_client is not None:
        return _mongodb_database
    
    # 构建连接 URI
    if username and password:
        mongodb_uri = f"mongodb://{username}:{password}@{host}:{port}/{database}?authSource={auth_source}"
    else:
        mongodb_uri = f"mongodb://{host}:{port}/{database}"
    
    # 创建 MongoDB 客户端
    _mongodb_client = AsyncIOMotorClient(
        mongodb_uri,
        maxPoolSize=max_pool_size,
        minPoolSize=min_pool_size,
        **kwargs
    )
    
    # 获取数据库实例
    _mongodb_database = _mongodb_client[database]
    
    logger.info(f"MongoDB 连接已初始化: {host}:{port}/{database}")
    
    return _mongodb_database


def get_mongodb() -> AsyncIOMotorDatabase:
    """
    获取 MongoDB 数据库实例
    
    Returns:
        AsyncIOMotorDatabase: MongoDB 数据库实例
    
    Raises:
        RuntimeError: 如果 MongoDB 未初始化
    """
    if _mongodb_database is None:
        raise RuntimeError("MongoDB 未初始化，请先调用 init_mongodb()")
    return _mongodb_database


def get_mongodb_client() -> AsyncIOMotorClient:
    """
    获取 MongoDB 客户端实例
    
    Returns:
        AsyncIOMotorClient: MongoDB 客户端实例
    
    Raises:
        RuntimeError: 如果 MongoDB 未初始化
    """
    if _mongodb_client is None:
        raise RuntimeError("MongoDB 未初始化，请先调用 init_mongodb()")
    return _mongodb_client


async def close_mongodb():
    """
    关闭 MongoDB 连接
    """
    global _mongodb_client, _mongodb_database
    
    if _mongodb_client is not None:
        _mongodb_client.close()
        _mongodb_client = None
        _mongodb_database = None
        logger.info("MongoDB 连接已关闭")


async def ping_mongodb() -> bool:
    """
    检查 MongoDB 连接是否正常
    
    Returns:
        bool: 连接是否正常
    """
    try:
        client = get_mongodb_client()
        await client.admin.command('ping')
        return True
    except Exception as e:
        logger.error(f"MongoDB 连接检查失败: {e}")
        return False

