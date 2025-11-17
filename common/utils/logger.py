"""
BANTU CRM 统一日志模块
基于 loguru 提供统一的日志记录功能
"""
import sys
import os
from pathlib import Path
from typing import Optional
from loguru import logger


class Logger:
    """统一日志管理器"""
    
    _initialized = False
    
    @classmethod
    def initialize(
        cls,
        service_name: str = "crm-service",
        log_level: str = "INFO",
        log_dir: Optional[str] = None,
        enable_file_logging: bool = True,
        enable_console_logging: bool = True,
        log_format: Optional[str] = None,
    ):
        """
        初始化日志配置
        
        Args:
            service_name: 服务名称，用于日志文件命名
            log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: 日志文件目录，默认为项目根目录下的 logs 目录
            enable_file_logging: 是否启用文件日志
            enable_console_logging: 是否启用控制台日志
            log_format: 自定义日志格式
        """
        if cls._initialized:
            logger.warning("Logger 已经初始化，跳过重复初始化")
            return
        
        # 移除默认的 handler
        logger.remove()
        
        # 默认日志格式
        if log_format is None:
            log_format = (
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            )
        
        # 控制台日志
        if enable_console_logging:
            logger.add(
                sys.stderr,
                format=log_format,
                level=log_level,
                colorize=True,
                backtrace=True,
                diagnose=True,
            )
        
        # 文件日志
        if enable_file_logging:
            # 确定日志目录
            if log_dir is None:
                # 默认使用项目根目录下的 logs 目录
                project_root = Path(__file__).parent.parent.parent
                log_dir = project_root / "logs"
            else:
                log_dir = Path(log_dir)
            
            # 创建日志目录
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # 所有日志文件
            logger.add(
                log_dir / f"{service_name}.log",
                format=log_format,
                level=log_level,
                rotation="100 MB",  # 日志文件大小达到 100MB 时轮转
                retention="30 days",  # 保留 30 天的日志
                compression="zip",  # 压缩旧日志
                encoding="utf-8",
                backtrace=True,
                diagnose=True,
            )
            
            # 错误日志单独文件
            logger.add(
                log_dir / f"{service_name}.error.log",
                format=log_format,
                level="ERROR",
                rotation="50 MB",
                retention="90 days",  # 错误日志保留更长时间
                compression="zip",
                encoding="utf-8",
                backtrace=True,
                diagnose=True,
            )
        
        cls._initialized = True
        logger.info(f"Logger 初始化完成 - 服务: {service_name}, 级别: {log_level}")
    
    @classmethod
    def get_logger(cls, name: Optional[str] = None):
        """
        获取 logger 实例
        
        Args:
            name: logger 名称，通常使用模块名
        
        Returns:
            logger 实例
        """
        if not cls._initialized:
            # 如果未初始化，使用默认配置初始化
            cls.initialize()
        
        if name:
            return logger.bind(name=name)
        return logger


# 创建默认 logger 实例
def get_logger(name: Optional[str] = None):
    """
    便捷函数：获取 logger 实例
    
    Args:
        name: logger 名称，通常使用模块名
    
    Returns:
        logger 实例
    
    Example:
        from common.utils.logger import get_logger
        
        logger = get_logger(__name__)
        logger.info("这是一条日志")
    """
    return Logger.get_logger(name)


# 导出默认 logger
default_logger = Logger.get_logger()

