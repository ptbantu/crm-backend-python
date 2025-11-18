"""
BANTU CRM 公共模块
提供所有微服务共享的通用功能
"""

__version__ = "1.0.0"

# 导出常用模块
from .utils.logger import Logger, get_logger, default_logger
from .config import BaseServiceSettings
from .database import Base, init_database, get_db, get_async_session_local, init_db

__all__ = [
    "Logger",
    "get_logger",
    "default_logger",
    "BaseServiceSettings",
    "Base",
    "init_database",
    "get_db",
    "get_async_session_local",
    "init_db",
]

