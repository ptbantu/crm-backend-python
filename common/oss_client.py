"""
阿里云 OSS 对象存储客户端
提供文件上传、下载、删除等功能
"""
import json
import os
from pathlib import Path
from typing import Optional, BinaryIO, Union, List
from io import BytesIO
from datetime import datetime, timedelta
import oss2
from oss2.exceptions import OssError, NoSuchKey, NoSuchBucket
from common.utils.logger import get_logger

logger = get_logger(__name__)

# 全局 OSS 客户端（单例模式）
_oss_client: Optional[oss2.Bucket] = None
_oss_config: dict = {}


def load_oss_config(config_path: Optional[str] = None) -> dict:
    """
    加载 OSS 配置文件
    
    Args:
        config_path: 配置文件路径，默认为 config/oss.json
    
    Returns:
        dict: OSS 配置字典
    """
    if config_path is None:
        # 默认配置文件路径
        project_root = Path(__file__).parent.parent
        config_path = project_root / "config" / "oss.json"
    
    config_path = Path(config_path)
    
    if not config_path.exists():
        logger.warning(f"OSS 配置文件不存在: {config_path}")
        return {}
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        logger.info(f"OSS 配置加载成功: {config_path}")
        return config
    except json.JSONDecodeError as e:
        logger.error(f"OSS 配置文件格式错误: {e}")
        raise
    except Exception as e:
        logger.error(f"加载 OSS 配置失败: {e}")
        raise


def init_oss(
    endpoint: Optional[str] = None,
    access_key_id: Optional[str] = None,
    access_key_secret: Optional[str] = None,
    bucket_name: Optional[str] = None,
    region: Optional[str] = None,
    use_https: bool = True,
    config_path: Optional[str] = None,
    **kwargs
) -> oss2.Bucket:
    """
    初始化阿里云 OSS 连接
    
    Args:
        endpoint: OSS 端点地址（如：oss-cn-hangzhou.aliyuncs.com）
        access_key_id: 访问密钥 ID
        access_key_secret: 访问密钥 Secret
        bucket_name: 存储桶名称
        region: 区域（如：cn-hangzhou）
        use_https: 是否使用 HTTPS
        config_path: 配置文件路径
        **kwargs: 其他 OSS 连接参数
    
    Returns:
        oss2.Bucket: OSS Bucket 实例
    """
    global _oss_client, _oss_config
    
    if _oss_client is not None:
        return _oss_client
    
    # 加载配置文件
    config = load_oss_config(config_path)
    _oss_config = config
    
    # 优先使用参数，其次使用配置文件，最后使用环境变量
    endpoint = endpoint or config.get("endpoint") or os.getenv("OSS_ENDPOINT")
    access_key_id = access_key_id or config.get("access_key_id") or os.getenv("OSS_ACCESS_KEY_ID")
    access_key_secret = access_key_secret or config.get("access_key_secret") or os.getenv("OSS_ACCESS_KEY_SECRET")
    bucket_name = bucket_name or config.get("bucket_name") or os.getenv("OSS_BUCKET_NAME", "bantu-crm")
    region = region or config.get("region") or os.getenv("OSS_REGION", "cn-hangzhou")
    use_https = config.get("use_https", use_https) if "use_https" in config else use_https
    
    # 验证必填参数
    if not endpoint:
        raise ValueError("OSS endpoint 未配置")
    if not access_key_id:
        raise ValueError("OSS access_key_id 未配置")
    if not access_key_secret:
        raise ValueError("OSS access_key_secret 未配置")
    if not bucket_name:
        raise ValueError("OSS bucket_name 未配置")
    
    # 创建认证对象
    auth = oss2.Auth(access_key_id, access_key_secret)
    
    # 构建端点 URL
    protocol = "https" if use_https else "http"
    endpoint_url = f"{protocol}://{endpoint}"
    
    # 创建 Bucket 实例
    _oss_client = oss2.Bucket(auth, endpoint_url, bucket_name, **kwargs)
    
    # 验证连接
    try:
        _oss_client.get_bucket_info()
        logger.info(f"OSS 连接已初始化: {endpoint_url}/{bucket_name}")
    except OssError as e:
        logger.error(f"OSS 连接验证失败: {e}")
        raise
    
    return _oss_client


def get_oss() -> oss2.Bucket:
    """
    获取 OSS 客户端实例
    
    Returns:
        oss2.Bucket: OSS Bucket 实例
    
    Raises:
        RuntimeError: 如果 OSS 未初始化
    """
    if _oss_client is None:
        raise RuntimeError("OSS 未初始化，请先调用 init_oss()")
    return _oss_client


def get_oss_config() -> dict:
    """
    获取 OSS 配置
    
    Returns:
        dict: OSS 配置字典
    """
    return _oss_config.copy()


def get_bucket_name(env: Optional[str] = None) -> str:
    """
    根据环境获取 bucket 名称
    
    Args:
        env: 环境类型 ('prod' 或 'dev')，如果不指定则使用配置中的默认值
    
    Returns:
        str: bucket 名称
    """
    config = get_oss_config()
    
    if env:
        buckets = config.get("buckets", {})
        bucket_name = buckets.get(env)
        if bucket_name:
            return bucket_name
    
    # 使用默认 bucket_name
    return config.get("bucket_name", "bantuqifu-dev")


def upload_file(
    object_name: str,
    data: Union[BinaryIO, bytes, str],
    content_type: Optional[str] = None,
    metadata: Optional[dict] = None,
    bucket_name: Optional[str] = None,
    headers: Optional[dict] = None
) -> str:
    """
    上传文件到 OSS
    
    Args:
        object_name: 对象名称（文件路径）
        data: 文件数据（可以是文件流、字节数据或文件路径）
        content_type: 内容类型（MIME 类型）
        metadata: 元数据
        bucket_name: 存储桶名称（可选，默认使用初始化时的 bucket）
        headers: 自定义 HTTP 头
    
    Returns:
        str: 对象名称（文件路径）
    
    Raises:
        ValueError: 如果数据无效
        OssError: 如果上传失败
    """
    client = get_oss()
    
    # 如果指定了 bucket_name，需要重新创建客户端（OSS 不支持动态切换 bucket）
    if bucket_name and bucket_name != client.bucket_name:
        logger.warning(f"指定的 bucket_name ({bucket_name}) 与初始化时的不同，将使用初始化时的 bucket")
    
    # 处理数据
    if isinstance(data, str):
        # 如果是文件路径，读取文件
        file_path = Path(data)
        if not file_path.exists():
            raise ValueError(f"文件不存在: {data}")
        with open(file_path, "rb") as f:
            file_data = f.read()
        data = file_data
    
    if isinstance(data, bytes):
        data = BytesIO(data)
    
    if not hasattr(data, "read"):
        raise ValueError("data 必须是文件流、字节数据或文件路径")
    
    # 获取文件大小
    if hasattr(data, "seek") and hasattr(data, "tell"):
        current_pos = data.tell()
        data.seek(0, 2)  # 移动到文件末尾
        length = data.tell()
        data.seek(current_pos)  # 恢复原位置
    else:
        length = None
    
    # 设置内容类型
    if content_type is None:
        # 根据文件扩展名推断
        ext = Path(object_name).suffix.lower()
        content_type_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".zip": "application/zip",
            ".rar": "application/x-rar-compressed",
        }
        content_type = content_type_map.get(ext, "application/octet-stream")
    
    # 构建请求头
    request_headers = headers or {}
    if metadata:
        # OSS 元数据需要以 x-oss-meta- 开头
        for key, value in metadata.items():
            request_headers[f"x-oss-meta-{key}"] = str(value)
    
    try:
        # 上传文件
        if length is not None:
            result = client.put_object(
                object_name,
                data,
                headers=request_headers
            )
        else:
            result = client.put_object(
                object_name,
                data.read() if hasattr(data, "read") else data,
                headers=request_headers
            )
        
        logger.info(f"文件上传成功: {client.bucket_name}/{object_name}")
        return object_name
    except OssError as e:
        logger.error(f"文件上传失败: {e}")
        raise


def download_file(
    object_name: str,
    bucket_name: Optional[str] = None
) -> BytesIO:
    """
    从 OSS 下载文件
    
    Args:
        object_name: 对象名称（文件路径）
        bucket_name: 存储桶名称（可选，默认使用初始化时的 bucket）
    
    Returns:
        BytesIO: 文件数据流
    
    Raises:
        NoSuchKey: 如果文件不存在
        OssError: 如果下载失败
    """
    client = get_oss()
    
    try:
        result = client.get_object(object_name)
        data = BytesIO(result.read())
        result.close()
        logger.info(f"文件下载成功: {client.bucket_name}/{object_name}")
        return data
    except NoSuchKey:
        logger.error(f"文件不存在: {client.bucket_name}/{object_name}")
        raise
    except OssError as e:
        logger.error(f"文件下载失败: {e}")
        raise


def delete_file(
    object_name: str,
    bucket_name: Optional[str] = None
) -> bool:
    """
    从 OSS 删除文件
    
    Args:
        object_name: 对象名称（文件路径）
        bucket_name: 存储桶名称（可选，默认使用初始化时的 bucket）
    
    Returns:
        bool: 是否删除成功
    
    Raises:
        OssError: 如果删除失败
    """
    client = get_oss()
    
    try:
        client.delete_object(object_name)
        logger.info(f"文件删除成功: {client.bucket_name}/{object_name}")
        return True
    except OssError as e:
        logger.error(f"文件删除失败: {e}")
        raise


def batch_delete_files(
    object_names: List[str],
    bucket_name: Optional[str] = None
) -> List[str]:
    """
    批量删除文件
    
    Args:
        object_names: 对象名称列表
        bucket_name: 存储桶名称（可选，默认使用初始化时的 bucket）
    
    Returns:
        list[str]: 成功删除的对象名称列表
    
    Raises:
        OssError: 如果删除失败
    """
    if not object_names:
        return []
    
    client = get_oss()
    
    try:
        # OSS 支持批量删除，最多一次删除 1000 个对象
        result = client.batch_delete_objects(object_names)
        deleted = result.deleted_keys
        logger.info(f"批量删除成功: {len(deleted)}/{len(object_names)} 个文件")
        return deleted
    except OssError as e:
        logger.error(f"批量删除失败: {e}")
        raise


def get_file_url(
    object_name: str,
    expires: Optional[int] = None,
    bucket_name: Optional[str] = None,
    cdn_domain: Optional[str] = None
) -> str:
    """
    获取文件的访问 URL
    
    Args:
        object_name: 对象名称（文件路径）
        expires: URL 过期时间（秒），默认使用配置中的值
        bucket_name: 存储桶名称（可选，默认使用初始化时的 bucket）
        cdn_domain: CDN 域名（可选，如果配置了 CDN）
    
    Returns:
        str: 文件访问 URL
    
    Raises:
        OssError: 如果获取 URL 失败
    """
    client = get_oss()
    config = get_oss_config()
    
    # 使用 CDN 域名或构建标准 URL
    if cdn_domain or config.get("cdn_domain"):
        cdn = cdn_domain or config.get("cdn_domain")
        # CDN URL 不需要签名
        url = f"https://{cdn}/{object_name}"
        return url
    
    # 使用预签名 URL
    expires = expires or config.get("expires", 3600)
    
    try:
        url = client.sign_url("GET", object_name, expires)
        return url
    except OssError as e:
        logger.error(f"获取文件 URL 失败: {e}")
        raise


def get_upload_url(
    object_name: str,
    expires: Optional[int] = None,
    max_size: Optional[int] = None,
    content_type: Optional[str] = None,
    bucket_name: Optional[str] = None
) -> str:
    """
    获取文件上传的预签名 URL（用于前端直传）
    
    Args:
        object_name: 对象名称（文件路径）
        expires: URL 过期时间（秒），默认 3600 秒
        max_size: 最大文件大小（字节），默认不限制
        content_type: 内容类型限制（可选）
        bucket_name: 存储桶名称（可选，默认使用初始化时的 bucket）
    
    Returns:
        str: 上传预签名 URL
    """
    client = get_oss()
    
    expires = expires or 3600
    
    # 构建 POST Policy
    policy = {
        "expiration": (datetime.utcnow() + timedelta(seconds=expires)).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "conditions": [
            ["content-length-range", 0, max_size or 104857600]  # 默认 100MB
        ]
    }
    
    if content_type:
        policy["conditions"].append(["eq", "$Content-Type", content_type])
    
    try:
        # 生成 POST 预签名 URL
        url = client.sign_url("POST", object_name, expires)
        return url
    except OssError as e:
        logger.error(f"获取上传 URL 失败: {e}")
        raise


def file_exists(
    object_name: str,
    bucket_name: Optional[str] = None
) -> bool:
    """
    检查文件是否存在
    
    Args:
        object_name: 对象名称（文件路径）
        bucket_name: 存储桶名称（可选，默认使用初始化时的 bucket）
    
    Returns:
        bool: 文件是否存在
    """
    client = get_oss()
    
    try:
        return client.object_exists(object_name)
    except OssError as e:
        logger.error(f"检查文件是否存在失败: {e}")
        return False


def get_file_info(
    object_name: str,
    bucket_name: Optional[str] = None
) -> Optional[dict]:
    """
    获取文件信息
    
    Args:
        object_name: 对象名称（文件路径）
        bucket_name: 存储桶名称（可选，默认使用初始化时的 bucket）
    
    Returns:
        dict: 文件信息（大小、最后修改时间等），如果文件不存在返回 None
    """
    client = get_oss()
    
    try:
        meta = client.head_object(object_name)
        return {
            "size": meta.content_length,
            "content_type": meta.content_type,
            "last_modified": meta.last_modified,
            "etag": meta.etag,
            "metadata": meta.headers
        }
    except NoSuchKey:
        return None
    except OssError as e:
        logger.error(f"获取文件信息失败: {e}")
        return None


def list_files(
    prefix: str = "",
    max_keys: int = 100,
    marker: Optional[str] = None,
    bucket_name: Optional[str] = None
) -> List[dict]:
    """
    列出文件
    
    Args:
        prefix: 对象名称前缀（用于过滤）
        max_keys: 最多返回的对象数量
        marker: 分页标记（用于获取下一页）
        bucket_name: 存储桶名称（可选，默认使用初始化时的 bucket）
    
    Returns:
        list[dict]: 文件列表，每个文件包含 key、size、last_modified 等信息
    """
    client = get_oss()
    
    try:
        result = client.list_objects_v2(
            prefix=prefix,
            max_keys=max_keys,
            continuation_token=marker
        )
        
        files = []
        for obj in result.object_list:
            files.append({
                "key": obj.key,
                "size": obj.size,
                "last_modified": obj.last_modified,
                "etag": obj.etag,
                "storage_class": obj.storage_class
            })
        
        return files
    except OssError as e:
        logger.error(f"列出文件失败: {e}")
        raise


def copy_file(
    source_object_name: str,
    target_object_name: str,
    source_bucket_name: Optional[str] = None,
    target_bucket_name: Optional[str] = None
) -> bool:
    """
    复制文件（在同一 bucket 内或跨 bucket）
    
    Args:
        source_object_name: 源对象名称
        target_object_name: 目标对象名称
        source_bucket_name: 源存储桶名称（可选，默认使用初始化时的 bucket）
        target_bucket_name: 目标存储桶名称（可选，默认使用初始化时的 bucket）
    
    Returns:
        bool: 是否复制成功
    """
    client = get_oss()
    
    source_bucket = source_bucket_name or client.bucket_name
    target_bucket = target_bucket_name or client.bucket_name
    
    try:
        # 构建源对象路径
        source_path = f"{source_bucket}/{source_object_name}" if source_bucket != client.bucket_name else source_object_name
        
        # 复制文件
        client.copy_object(source_path, target_object_name)
        logger.info(f"文件复制成功: {source_path} -> {target_object_name}")
        return True
    except OssError as e:
        logger.error(f"文件复制失败: {e}")
        raise


def ping_oss() -> bool:
    """
    检查 OSS 连接是否正常
    
    Returns:
        bool: 连接是否正常
    """
    try:
        client = get_oss()
        # 获取 bucket 信息来检查连接
        client.get_bucket_info()
        return True
    except Exception as e:
        logger.error(f"OSS 连接检查失败: {e}")
        return False


def generate_object_name(
    prefix: Optional[str] = None,
    filename: Optional[str] = None,
    organization_id: Optional[str] = None,
    user_id: Optional[str] = None,
    file_type: Optional[str] = None
) -> str:
    """
    生成对象名称（文件路径）
    
    格式: {prefix}/{organization_id}/{user_id}/{date}/{timestamp}_{filename}
    
    Args:
        prefix: 路径前缀（如：uploads, documents）
        filename: 原始文件名
        organization_id: 组织ID
        user_id: 用户ID
        file_type: 文件类型（如：avatar, document, image）
    
    Returns:
        str: 对象名称（文件路径）
    """
    config = get_oss_config()
    default_prefix = config.get("default_path_prefix", "uploads")
    prefix = prefix or default_prefix
    
    # 构建路径
    parts = [prefix]
    
    if file_type:
        parts.append(file_type)
    
    if organization_id:
        parts.append(organization_id)
    
    if user_id:
        parts.append(user_id)
    
    # 添加日期目录
    date_str = datetime.now().strftime("%Y%m%d")
    parts.append(date_str)
    
    # 添加文件名
    if filename:
        # 生成唯一文件名（时间戳 + 原始文件名）
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        ext = Path(filename).suffix
        name_without_ext = Path(filename).stem
        # 清理文件名中的特殊字符
        safe_name = "".join(c for c in name_without_ext if c.isalnum() or c in ("-", "_", "."))
        filename = f"{timestamp}_{safe_name}{ext}"
        parts.append(filename)
    else:
        # 如果没有文件名，生成一个唯一ID
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        parts.append(f"{timestamp}.bin")
    
    return "/".join(parts)
