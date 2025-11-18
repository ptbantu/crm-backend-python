"""
Redis 连接客户端
"""
import redis.asyncio as aioredis
from redis.asyncio import Redis
from typing import Optional
from common.utils.logger import get_logger

logger = get_logger(__name__)

# 全局 Redis 客户端（单例模式）
_redis_client: Optional[Redis] = None


def init_redis(
    host: str = "redis.default.svc.cluster.local",
    port: int = 6379,
    password: Optional[str] = None,
    db: int = 0,
    decode_responses: bool = True,
    max_connections: int = 20,
    **kwargs
) -> Redis:
    """
    初始化 Redis 连接
    
    Args:
        host: Redis 主机地址
        port: Redis 端口
        password: Redis 密码
        db: 数据库索引（0-15）
        decode_responses: 是否自动解码响应为字符串
        max_connections: 连接池最大连接数
        **kwargs: 其他 Redis 连接参数
    
    Returns:
        Redis: Redis 客户端实例
    """
    global _redis_client
    
    if _redis_client is not None:
        return _redis_client
    
    # 构建连接 URL
    if password:
        redis_url = f"redis://:{password}@{host}:{port}/{db}"
    else:
        redis_url = f"redis://{host}:{port}/{db}"
    
    # 创建连接池
    pool = aioredis.ConnectionPool.from_url(
        redis_url,
        decode_responses=decode_responses,
        max_connections=max_connections,
        **kwargs
    )
    
    # 创建 Redis 客户端
    _redis_client = aioredis.Redis(connection_pool=pool)
    
    logger.info(f"Redis 连接已初始化: {host}:{port}/{db}")
    
    return _redis_client


def get_redis() -> Redis:
    """
    获取 Redis 客户端实例
    
    Returns:
        Redis: Redis 客户端实例
    
    Raises:
        RuntimeError: 如果 Redis 未初始化
    """
    if _redis_client is None:
        raise RuntimeError("Redis 未初始化，请先调用 init_redis()")
    return _redis_client


async def close_redis():
    """
    关闭 Redis 连接
    """
    global _redis_client
    
    if _redis_client is not None:
        await _redis_client.close()
        await _redis_client.connection_pool.disconnect()
        _redis_client = None
        logger.info("Redis 连接已关闭")


async def ping_redis() -> bool:
    """
    检查 Redis 连接是否正常
    
    Returns:
        bool: 连接是否正常
    """
    try:
        redis = get_redis()
        await redis.ping()
        return True
    except Exception as e:
        logger.error(f"Redis 连接检查失败: {e}")
        return False

