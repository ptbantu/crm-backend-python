"""
公共配置基类
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional
import json
import os
import re


class BaseServiceSettings(BaseSettings):
    """服务配置基类"""
    
    # 服务配置
    APP_NAME: str = "service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库配置
    DB_HOST: str = "mysql"
    DB_PORT: int = 3306
    DB_NAME: str = "bantu_crm"
    DB_USER: str = "bantu_user"
    DB_PASSWORD: str = "bantu_user_password_2024"
    
    @property
    def DATABASE_URL(self) -> str:
        """数据库连接 URL"""
        # 确保包含完整的字符集参数
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4&use_unicode=true"
    
    # Redis 配置
    REDIS_HOST: str = "redis.default.svc.cluster.local"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "bantu_redis_password_2024"
    REDIS_DB: int = 0
    
    @field_validator('REDIS_PORT', mode='before')
    @classmethod
    def parse_redis_port(cls, v) -> int:
        """从 URL 或字符串中提取端口号"""
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            # 如果是 URL 格式（如 tcp://10.43.173.191:6379），提取端口
            match = re.search(r':(\d+)(?:/|$)', v)
            if match:
                return int(match.group(1))
            # 如果是纯数字字符串，直接转换
            try:
                return int(v)
            except ValueError:
                raise ValueError(f"无法从 '{v}' 中解析 REDIS_PORT")
        raise ValueError(f"REDIS_PORT 必须是 int 或 str，收到: {type(v)}")
    
    @property
    def REDIS_URL(self) -> str:
        """Redis 连接 URL"""
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # MongoDB 配置
    MONGO_HOST: str = "mongodb"  # 使用短地址（同一 namespace 内），完整地址：mongodb.default.svc.cluster.local
    MONGO_PORT: int = 27017
    MONGO_DATABASE: str = "bantu_crm"
    MONGO_USERNAME: str = "bantu_mongo_user"
    MONGO_PASSWORD: str = "bantu_mongo_user_password_2024"
    MONGO_AUTH_SOURCE: str = "bantu_crm"
    
    @property
    def MONGO_URL(self) -> str:
        """MongoDB 连接 URL"""
        return f"mongodb://{self.MONGO_USERNAME}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DATABASE}?authSource={self.MONGO_AUTH_SOURCE}"
    
    # MinIO 配置
    MINIO_ENDPOINT: str = "minio.default.svc.cluster.local"
    MINIO_PORT: int = 9000
    MINIO_ACCESS_KEY: str = "bantu_minio_admin"
    MINIO_SECRET_KEY: str = "bantu_minio_password_2024"
    MINIO_BUCKET: str = "bantu-crm"
    MINIO_SECURE: bool = False
    
    @field_validator('MINIO_PORT', mode='before')
    @classmethod
    def parse_minio_port(cls, v) -> int:
        """从 URL 或字符串中提取端口号"""
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            # 如果是 URL 格式（如 tcp://10.43.223.221:9000），提取端口
            match = re.search(r':(\d+)(?:/|$)', v)
            if match:
                return int(match.group(1))
            # 如果是纯数字字符串，直接转换
            try:
                return int(v)
            except ValueError:
                raise ValueError(f"无法从 '{v}' 中解析 MINIO_PORT")
        raise ValueError(f"MINIO_PORT 必须是 int 或 str，收到: {type(v)}")
    
    @field_validator('MINIO_ENDPOINT', mode='before')
    @classmethod
    def parse_minio_endpoint(cls, v):
        """从 URL 中提取端点地址"""
        if isinstance(v, str) and '://' in v:
            # 如果是 URL 格式（如 tcp://10.43.223.221:9000），提取主机
            match = re.search(r'://([^:/]+)', v)
            if match:
                return match.group(1)
        return v
    
    @property
    def MINIO_URL(self) -> str:
        """MinIO API URL"""
        protocol = "https" if self.MINIO_SECURE else "http"
        return f"{protocol}://{self.MINIO_ENDPOINT}:{self.MINIO_PORT}"
    
    # Chroma 配置
    CHROMA_HOST: str = "chroma.default.svc.cluster.local"
    CHROMA_PORT: int = 8000
    
    @field_validator('CHROMA_PORT', mode='before')
    @classmethod
    def parse_chroma_port(cls, v) -> int:
        """从 URL 或字符串中提取端口号"""
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            # 如果是 URL 格式（如 tcp://10.43.160.182:8000），提取端口
            match = re.search(r':(\d+)(?:/|$)', v)
            if match:
                return int(match.group(1))
            # 如果是纯数字字符串，直接转换
            try:
                return int(v)
            except ValueError:
                raise ValueError(f"无法从 '{v}' 中解析 CHROMA_PORT")
        raise ValueError(f"CHROMA_PORT 必须是 int 或 str，收到: {type(v)}")
    
    @field_validator('CHROMA_HOST', mode='before')
    @classmethod
    def parse_chroma_host(cls, v):
        """从 URL 中提取主机地址"""
        if isinstance(v, str) and '://' in v:
            # 如果是 URL 格式（如 tcp://10.43.160.182:8000），提取主机
            match = re.search(r'://([^:/]+)', v)
            if match:
                return match.group(1)
        return v
    
    @property
    def CHROMA_URL(self) -> str:
        """Chroma API URL"""
        return f"http://{self.CHROMA_HOST}:{self.CHROMA_PORT}"
    
    # 邮件配置
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    SMTP_FROM_EMAIL: Optional[str] = None
    SMTP_FROM_NAME: Optional[str] = None
    
    # WeChaty 配置
    WECHATY_NAME: str = "bantu-crm-bot"
    WECHATY_TOKEN: Optional[str] = None
    WECHATY_ENDPOINT: Optional[str] = None
    
    # WhatsApp 配置
    WHATSAPP_API_URL: str = "https://graph.facebook.com/v18.0"
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    WHATSAPP_ACCESS_TOKEN: Optional[str] = None
    WHATSAPP_VERIFY_TOKEN: Optional[str] = None
    WHATSAPP_APP_SECRET: Optional[str] = None
    
    # CORS 配置（支持从环境变量读取 JSON 字符串）
    @property
    def CORS_ALLOWED_ORIGINS(self) -> List[str]:
        """CORS 允许的来源"""
        cors_env = os.getenv("CORS_ALLOWED_ORIGINS")
        if cors_env:
            try:
                parsed = json.loads(cors_env)
                # 如果环境变量设置为 ["*"]，允许所有域名
                if parsed == ["*"] or parsed == "*":
                    return ["*"]
                return parsed
            except json.JSONDecodeError:
                # 如果不是 JSON，尝试按逗号分割
                origins = [origin.strip() for origin in cors_env.split(",")]
                if "*" in origins:
                    return ["*"]
                return origins
        # 临时允许所有域名访问（开发环境）
        return ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

