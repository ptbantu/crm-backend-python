"""
指标收集工具
"""
import psutil
import os
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from common.utils.logger import get_logger

logger = get_logger(__name__)


class MetricsCollector:
    """指标收集器"""
    
    @classmethod
    def collect_system_metrics(cls) -> Dict[str, Any]:
        """
        收集系统资源指标
        
        Returns:
            系统指标字典
        """
        try:
            # CPU 使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            memory_total_mb = memory.total / (1024 * 1024)
            
            # 磁盘使用情况
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            return {
                "cpu_usage_percent": round(cpu_percent, 2),
                "memory_usage_percent": round(memory_percent, 2),
                "memory_used_mb": round(memory_used_mb, 2),
                "memory_total_mb": round(memory_total_mb, 2),
                "disk_usage_percent": round(disk_percent, 2),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"收集系统指标失败: {str(e)}", exc_info=True)
            return {
                "cpu_usage_percent": 0.0,
                "memory_usage_percent": 0.0,
                "memory_used_mb": 0.0,
                "memory_total_mb": 0.0,
                "disk_usage_percent": None,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    @classmethod
    async def collect_database_metrics(cls, db: AsyncSession) -> Dict[str, Any]:
        """
        收集数据库指标
        
        Args:
            db: 数据库会话
        
        Returns:
            数据库指标字典
        """
        try:
            # 获取连接池信息
            pool = db.bind.pool if hasattr(db.bind, 'pool') else None
            active_connections = 0
            idle_connections = 0
            max_connections = 0
            
            if pool:
                active_connections = getattr(pool, 'checkedout', 0)
                idle_connections = getattr(pool, 'checkedin', 0)
                max_connections = getattr(pool, 'size', 0) + getattr(pool, 'max_overflow', 0)
            
            # 查询慢查询数量（需要 MySQL 开启慢查询日志）
            # 这里简化处理，实际应该查询 performance_schema 或慢查询日志
            slow_queries_count = 0
            
            return {
                "active_connections": active_connections,
                "idle_connections": idle_connections,
                "max_connections": max_connections,
                "slow_queries_count": slow_queries_count,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"收集数据库指标失败: {str(e)}", exc_info=True)
            return {
                "active_connections": 0,
                "idle_connections": 0,
                "max_connections": 0,
                "slow_queries_count": 0,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

