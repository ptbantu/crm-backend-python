"""
Analytics and Monitoring Service 配置
"""
from common.config import BaseServiceSettings


class Settings(BaseServiceSettings):
    """Analytics and Monitoring Service 配置"""
    
    # 服务配置
    APP_NAME: str = "analytics-monitoring-service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 监控配置
    METRICS_COLLECTION_INTERVAL: int = 60  # 指标收集间隔（秒）
    ALERT_CHECK_INTERVAL: int = 30  # 预警检查间隔（秒）
    
    # 预警阈值配置
    CPU_THRESHOLD_WARNING: float = 70.0  # CPU 警告阈值（%）
    CPU_THRESHOLD_CRITICAL: float = 85.0  # CPU 严重阈值（%）
    MEMORY_THRESHOLD_WARNING: float = 75.0  # 内存警告阈值（%）
    MEMORY_THRESHOLD_CRITICAL: float = 90.0  # 内存严重阈值（%）
    ERROR_RATE_THRESHOLD_WARNING: float = 3.0  # 错误率警告阈值（%）
    ERROR_RATE_THRESHOLD_CRITICAL: float = 5.0  # 错误率严重阈值（%）
    
    # 预警通知配置（暂时注释，等待配置完成）
    # ALERT_EMAIL_ENABLED: bool = True
    # ALERT_WECHAT_ENABLED: bool = False
    # ALERT_WHATSAPP_ENABLED: bool = False
    # ALERT_EMAIL_RECIPIENTS: str = ""  # 逗号分隔的邮箱地址
    
    # 临时禁用通知功能
    ALERT_EMAIL_ENABLED: bool = False
    ALERT_WECHAT_ENABLED: bool = False
    ALERT_WHATSAPP_ENABLED: bool = False
    ALERT_EMAIL_RECIPIENTS: str = ""
    
    # 缓存配置
    CACHE_ENABLED: bool = True  # 是否启用缓存
    CACHE_TTL: int = 300  # 缓存过期时间（秒），5分钟
    CACHE_KEY_PREFIX: str = "analytics:"  # 缓存键前缀
    
    # MongoDB 配置（继承自 BaseServiceSettings，这里可以覆盖）
    # MONGODB_HOST, MONGODB_PORT, MONGODB_DATABASE, MONGODB_USERNAME, MONGODB_PASSWORD, MONGODB_AUTH_SOURCE
    # 已从 BaseServiceSettings 继承，无需重复定义


settings = Settings()

