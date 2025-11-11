"""
Foundation Service 配置
"""
from pydantic_settings import BaseSettings
from typing import List
import json
import os


class Settings(BaseSettings):
    """应用配置"""
    
    # 服务配置
    APP_NAME: str = "foundation-service"
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
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
    
    # JWT 配置
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 86400000  # 24小时
    
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


settings = Settings()

