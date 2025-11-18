"""
Service Management Service 配置
"""
from common.config import BaseServiceSettings


class Settings(BaseServiceSettings):
    """Service Management Service 配置"""
    
    # 服务配置
    APP_NAME: str = "service-management-service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False


settings = Settings()

