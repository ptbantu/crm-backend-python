"""
Foundation Service 配置
"""
from common.config import BaseServiceSettings


class Settings(BaseServiceSettings):
    """Foundation Service 配置"""
    
    # 服务配置
    APP_NAME: str = "foundation-service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # JWT 配置
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 86400000  # 24小时


settings = Settings()

