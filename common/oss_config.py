"""
OSS 存储配置
敏感信息（access_key_id 和 access_key_secret）硬编码在代码中
"""
from typing import Dict, List


class OSSConfig:
    """OSS 配置类"""
    
    # OSS 端点配置
    ENDPOINT: str = "oss-ap-southeast-5.aliyuncs.com"
    REGION: str = "ap-southeast-5"
    
    # 敏感信息：硬编码在代码中
    ACCESS_KEY_ID: str = "PLACEHOLDER_ACCESS_KEY_ID"
    ACCESS_KEY_SECRET: str = "PLACEHOLDER_ACCESS_KEY_SECRET"
    
    # OSS 连接配置
    USE_HTTPS: bool = True
    BUCKET_NAME: str = "bantuqifu-dev"
    
    # 不同环境的 bucket 配置
    BUCKETS: Dict[str, str] = {
        "prod": "bantuqifu",
        "dev": "bantuqifu-dev"
    }
    
    # CDN 域名配置
    CDN_DOMAIN: str = ""
    
    # 默认路径前缀
    DEFAULT_PATH_PREFIX: str = "uploads"
    
    # 签名过期时间（秒）
    EXPIRES: int = 3600
    
    # 最大文件大小（字节）
    MAX_FILE_SIZE: int = 104857600  # 100MB
    
    # 允许的文件扩展名
    ALLOWED_EXTENSIONS: List[str] = [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".zip",
        ".rar"
    ]
    
    @classmethod
    def get_config(cls) -> Dict:
        """获取完整配置字典"""
        return {
            "endpoint": cls.ENDPOINT,
            "region": cls.REGION,
            "access_key_id": cls.ACCESS_KEY_ID,
            "access_key_secret": cls.ACCESS_KEY_SECRET,
            "use_https": cls.USE_HTTPS,
            "bucket_name": cls.BUCKET_NAME,
            "buckets": cls.BUCKETS,
            "cdn_domain": cls.CDN_DOMAIN,
            "default_path_prefix": cls.DEFAULT_PATH_PREFIX,
            "expires": cls.EXPIRES,
            "max_file_size": cls.MAX_FILE_SIZE,
            "allowed_extensions": cls.ALLOWED_EXTENSIONS,
        }
    
    @classmethod
    def get_bucket_name(cls, environment: str = "dev") -> str:
        """根据环境获取 bucket 名称"""
        return cls.BUCKETS.get(environment, cls.BUCKET_NAME)
