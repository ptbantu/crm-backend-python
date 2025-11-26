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
    
    # JWT 配置（从环境变量读取，如果没有则使用默认值）
    # 环境变量优先级：JWT_SECRET > 默认值
    # 环境变量优先级：JWT_ALGORITHM > 默认值
    JWT_SECRET: str = "bantucrm-key-20251101-jwt"  # 默认值，会被环境变量覆盖
    JWT_ALGORITHM: str = "HS256"  # 默认值，会被环境变量覆盖
    JWT_EXPIRATION: int = 86400000  # 24小时


settings = Settings()

