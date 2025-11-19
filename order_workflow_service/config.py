"""
Order and Workflow Service 配置
"""
from common.config import BaseServiceSettings


class Settings(BaseServiceSettings):
    """Order and Workflow Service 配置"""
    
    # 服务配置
    APP_NAME: str = "order-workflow-service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 工作流配置
    WORKFLOW_AUTO_TRANSITION: bool = True  # 是否自动流转工作流
    WORKFLOW_TASK_TIMEOUT: int = 86400  # 任务超时时间（秒），默认24小时
    
    # 订单配置
    ORDER_NUMBER_PREFIX: str = "ORD"  # 订单号前缀
    ORDER_AUTO_APPROVE: bool = False  # 是否自动审批订单
    
    # 文件上传配置
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 最大文件大小（10MB）
    ALLOWED_FILE_TYPES: list = [".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx", ".xls", ".xlsx"]
    
    # MinIO 配置（使用公共配置）
    # MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY 从环境变量获取


settings = Settings()

