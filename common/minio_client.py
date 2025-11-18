"""
MinIO 对象存储客户端
"""
from minio import Minio
from minio.error import S3Error
from typing import Optional, BinaryIO
from io import BytesIO
from common.utils.logger import get_logger

logger = get_logger(__name__)

# 全局 MinIO 客户端（单例模式）
_minio_client: Optional[Minio] = None
_default_bucket: str = "bantu-crm"


def init_minio(
    endpoint: str = "minio.default.svc.cluster.local",
    port: int = 9000,
    access_key: str = "bantu_minio_admin",
    secret_key: str = "bantu_minio_password_2024",
    secure: bool = False,
    region: str = "us-east-1",
    default_bucket: str = "bantu-crm",
    **kwargs
) -> Minio:
    """
    初始化 MinIO 连接
    
    Args:
        endpoint: MinIO 端点地址
        port: MinIO 端口
        access_key: 访问密钥
        secret_key: 秘密密钥
        secure: 是否使用 HTTPS
        region: 区域
        default_bucket: 默认存储桶
        **kwargs: 其他 MinIO 连接参数
    
    Returns:
        Minio: MinIO 客户端实例
    """
    global _minio_client, _default_bucket
    
    if _minio_client is not None:
        return _minio_client
    
    # 构建端点 URL（MinIO 需要 host:port 格式）
    endpoint_url = f"{endpoint}:{port}"
    
    # 创建 MinIO 客户端
    _minio_client = Minio(
        endpoint_url,
        access_key=access_key,
        secret_key=secret_key,
        secure=secure,
        region=region,
        **kwargs
    )
    
    _default_bucket = default_bucket
    
    # 确保默认存储桶存在
    try:
        if not _minio_client.bucket_exists(default_bucket):
            _minio_client.make_bucket(default_bucket, region=region)
            logger.info(f"创建默认存储桶: {default_bucket}")
    except S3Error as e:
        logger.warning(f"检查/创建存储桶失败: {e}")
    
    logger.info(f"MinIO 连接已初始化: {endpoint_url}")
    
    return _minio_client


def get_minio() -> Minio:
    """
    获取 MinIO 客户端实例
    
    Returns:
        Minio: MinIO 客户端实例
    
    Raises:
        RuntimeError: 如果 MinIO 未初始化
    """
    if _minio_client is None:
        raise RuntimeError("MinIO 未初始化，请先调用 init_minio()")
    return _minio_client


def get_default_bucket() -> str:
    """
    获取默认存储桶名称
    
    Returns:
        str: 默认存储桶名称
    """
    return _default_bucket


def upload_file(
    bucket_name: str,
    object_name: str,
    data: BinaryIO,
    length: int,
    content_type: str = "application/octet-stream",
    metadata: Optional[dict] = None
) -> str:
    """
    上传文件到 MinIO
    
    Args:
        bucket_name: 存储桶名称
        object_name: 对象名称（文件路径）
        data: 文件数据流
        length: 数据长度
        content_type: 内容类型
        metadata: 元数据
    
    Returns:
        str: 对象名称
    """
    client = get_minio()
    
    try:
        client.put_object(
            bucket_name,
            object_name,
            data,
            length,
            content_type=content_type,
            metadata=metadata
        )
        logger.info(f"文件上传成功: {bucket_name}/{object_name}")
        return object_name
    except S3Error as e:
        logger.error(f"文件上传失败: {e}")
        raise


def download_file(bucket_name: str, object_name: str) -> BytesIO:
    """
    从 MinIO 下载文件
    
    Args:
        bucket_name: 存储桶名称
        object_name: 对象名称（文件路径）
    
    Returns:
        BytesIO: 文件数据流
    """
    client = get_minio()
    
    try:
        response = client.get_object(bucket_name, object_name)
        data = BytesIO(response.read())
        response.close()
        response.release_conn()
        logger.info(f"文件下载成功: {bucket_name}/{object_name}")
        return data
    except S3Error as e:
        logger.error(f"文件下载失败: {e}")
        raise


def delete_file(bucket_name: str, object_name: str):
    """
    从 MinIO 删除文件
    
    Args:
        bucket_name: 存储桶名称
        object_name: 对象名称（文件路径）
    """
    client = get_minio()
    
    try:
        client.remove_object(bucket_name, object_name)
        logger.info(f"文件删除成功: {bucket_name}/{object_name}")
    except S3Error as e:
        logger.error(f"文件删除失败: {e}")
        raise


def get_file_url(bucket_name: str, object_name: str, expires: int = 3600) -> str:
    """
    获取文件的预签名 URL
    
    Args:
        bucket_name: 存储桶名称
        object_name: 对象名称（文件路径）
        expires: URL 过期时间（秒）
    
    Returns:
        str: 预签名 URL
    """
    client = get_minio()
    
    try:
        url = client.presigned_get_object(bucket_name, object_name, expires=expires)
        return url
    except S3Error as e:
        logger.error(f"获取文件 URL 失败: {e}")
        raise


def ping_minio() -> bool:
    """
    检查 MinIO 连接是否正常
    
    Returns:
        bool: 连接是否正常
    """
    try:
        client = get_minio()
        # 列出存储桶来检查连接
        buckets = client.list_buckets()
        return True
    except Exception as e:
        logger.error(f"MinIO 连接检查失败: {e}")
        return False

