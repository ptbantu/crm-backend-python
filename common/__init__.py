"""
BANTU CRM 公共模块
提供所有微服务共享的通用功能
"""

__version__ = "1.0.0"

# 导出常用模块
from .utils.logger import Logger, get_logger, default_logger

__all__ = [
    "Logger",
    "get_logger",
    "default_logger",
]

