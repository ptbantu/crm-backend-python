"""
测试 MongoDB 日志记录
"""
import sys
from common.utils.logger import Logger, get_logger
from analytics_monitoring_service.config import settings

# 初始化日志（启用 MongoDB）
Logger.initialize(
    service_name="test-service",
    log_level="DEBUG",
    enable_file_logging=True,
    enable_console_logging=True,
    enable_mongodb_logging=True,
    mongodb_host=settings.MONGO_HOST,
    mongodb_port=settings.MONGO_PORT,
    mongodb_database=settings.MONGO_DATABASE,
    mongodb_username=settings.MONGO_USERNAME,
    mongodb_password=settings.MONGO_PASSWORD,
    mongodb_auth_source=settings.MONGO_AUTH_SOURCE,
)

# 获取 logger
logger = get_logger(__name__)

# 测试日志记录
logger.info("测试 MongoDB 日志记录 - INFO 级别")
logger.warning("测试 MongoDB 日志记录 - WARNING 级别")
logger.error("测试 MongoDB 日志记录 - ERROR 级别")

print("日志已发送，请检查 MongoDB 中的 logs_test-service 集合")

