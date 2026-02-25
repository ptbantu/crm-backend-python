"""
Foundation Service 配置
合并了所有微服务的配置
"""
from common.config import BaseServiceSettings


class Settings(BaseServiceSettings):
    """Foundation Service 配置（单体服务）"""
    
    # 服务配置
    APP_NAME: str = "foundation-service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # JWT 配置（从环境变量读取）
    # 继承自 BaseServiceSettings，不需要重复定义
    # JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION 已在父类中定义
    
    # Order Workflow Service 配置
    WORKFLOW_AUTO_TRANSITION: bool = True  # 是否自动流转工作流
    WORKFLOW_TASK_TIMEOUT: int = 86400  # 任务超时时间（秒），默认24小时
    ORDER_NUMBER_PREFIX: str = "ORD"  # 订单号前缀
    ORDER_AUTO_APPROVE: bool = False  # 是否自动审批订单
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 最大文件大小（10MB）
    ALLOWED_FILE_TYPES: list = [".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx", ".xls", ".xlsx"]
    
    # Analytics and Monitoring Service 配置
    METRICS_COLLECTION_INTERVAL: int = 60  # 指标收集间隔（秒）
    ALERT_CHECK_INTERVAL: int = 30  # 预警检查间隔（秒）
    CPU_THRESHOLD_WARNING: float = 70.0  # CPU 警告阈值（%）
    CPU_THRESHOLD_CRITICAL: float = 85.0  # CPU 严重阈值（%）
    MEMORY_THRESHOLD_WARNING: float = 75.0  # 内存警告阈值（%）
    MEMORY_THRESHOLD_CRITICAL: float = 90.0  # 内存严重阈值（%）
    ERROR_RATE_THRESHOLD_WARNING: float = 3.0  # 错误率警告阈值（%）
    ERROR_RATE_THRESHOLD_CRITICAL: float = 5.0  # 错误率严重阈值（%）
    ALERT_EMAIL_ENABLED: bool = False
    ALERT_WECHAT_ENABLED: bool = False
    ALERT_WHATSAPP_ENABLED: bool = False
    ALERT_EMAIL_RECIPIENTS: str = ""
    CACHE_ENABLED: bool = True  # 是否启用缓存
    CACHE_TTL: int = 300  # 缓存过期时间（秒），5分钟
    CACHE_KEY_PREFIX: str = "analytics:"  # 缓存键前缀
    
    # 天眼查 API 配置
    TIANYANCHA_API_URL: str = "http://open.api.tianyancha.com"  # 天眼查API地址（开放平台）
    TIANYANCHA_API_KEY: str = ""  # 天眼查API密钥（从环境变量 TIANYANCHA_API_KEY 读取）
    TIANYANCHA_TIMEOUT: int = 30  # 请求超时时间（秒）


settings = Settings()

