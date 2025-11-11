"""
Gateway Service 配置
"""
from pydantic_settings import BaseSettings
from typing import List
import json
import os


class Settings(BaseSettings):
    """应用配置"""
    
    # 服务配置
    APP_NAME: str = "gateway-service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # JWT 配置（用于验证）
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    
    # CORS 配置（支持从环境变量读取 JSON 字符串）
    @property
    def CORS_ALLOWED_ORIGINS(self) -> List[str]:
        """CORS 允许的来源"""
        cors_env = os.getenv("CORS_ALLOWED_ORIGINS")
        if cors_env:
            try:
                return json.loads(cors_env)
            except json.JSONDecodeError:
                # 如果不是 JSON，尝试按逗号分割
                return [origin.strip() for origin in cors_env.split(",")]
        # 默认值
        return [
            "https://crmbantu.space",
            "http://crmbantu.space",
            "https://www.crmbantu.space",
            "http://www.crmbantu.space",
            "https://www.bantu.sbs",
            "http://www.bantu.sbs",
            "https://168.231.118.179",
            "http://168.231.118.179",
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8080",
        ]
    
    # 微服务地址
    FOUNDATION_SERVICE_URL: str = "http://crm-foundation-service:8081"
    BUSINESS_SERVICE_URL: str = "http://crm-business-service:8082"
    WORKFLOW_SERVICE_URL: str = "http://crm-workflow-service:8083"
    FINANCE_SERVICE_URL: str = "http://crm-finance-service:8084"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

