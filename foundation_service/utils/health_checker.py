"""
健康检查工具
"""
import httpx
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from common.utils.logger import get_logger

logger = get_logger(__name__)


class HealthChecker:
    """健康检查器"""
    
    # 服务地址配置（从环境变量或配置读取）
    SERVICE_URLS = {
        "foundation-service": "http://crm-foundation-service:8081",
        "gateway-service": "http://crm-gateway-service:8080",
        "service-management-service": "http://crm-service-management-service:8082",
    }
    
    @classmethod
    async def check_service_health(
        cls,
        service_name: str,
        service_url: Optional[str] = None
    ) -> Dict:
        """
        检查服务健康状态
        
        Args:
            service_name: 服务名称
            service_url: 服务地址（可选，如果不提供则从配置读取）
        
        Returns:
            健康状态字典
        """
        url = service_url or cls.SERVICE_URLS.get(service_name)
        if not url:
            return {
                "service_name": service_name,
                "status": "unknown",
                "response_time_ms": None,
                "last_check": datetime.now().isoformat(),
                "error_message": f"服务地址未配置: {service_name}"
            }
        
        health_url = f"{url}/health"
        start_time = datetime.now()
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(health_url)
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds() * 1000
                
                if response.status_code == 200:
                    return {
                        "service_name": service_name,
                        "status": "healthy",
                        "response_time_ms": round(response_time, 2),
                        "last_check": datetime.now().isoformat(),
                        "error_message": None
                    }
                else:
                    return {
                        "service_name": service_name,
                        "status": "unhealthy",
                        "response_time_ms": round(response_time, 2),
                        "last_check": datetime.now().isoformat(),
                        "error_message": f"HTTP {response.status_code}"
                    }
        except httpx.TimeoutException:
            return {
                "service_name": service_name,
                "status": "unhealthy",
                "response_time_ms": None,
                "last_check": datetime.now().isoformat(),
                "error_message": "请求超时"
            }
        except Exception as e:
            logger.error(f"检查服务健康状态失败: {service_name}, 错误: {str(e)}", exc_info=True)
            return {
                "service_name": service_name,
                "status": "unhealthy",
                "response_time_ms": None,
                "last_check": datetime.now().isoformat(),
                "error_message": str(e)
            }
    
    @classmethod
    async def check_all_services_health(cls) -> List[Dict]:
        """
        检查所有服务健康状态
        
        Returns:
            服务健康状态列表
        """
        tasks = [
            cls.check_service_health(service_name)
            for service_name in cls.SERVICE_URLS.keys()
        ]
        results = await asyncio.gather(*tasks)
        return list(results)
    
    @classmethod
    async def check_database_health(cls, db: AsyncSession) -> Dict:
        """
        检查数据库健康状态
        
        Args:
            db: 数据库会话
        
        Returns:
            数据库健康状态字典
        """
        try:
            start_time = datetime.now()
            
            # 执行简单查询检查连接
            result = await db.execute(text("SELECT 1"))
            result.scalar()
            
            # 获取连接池信息
            pool = db.bind.pool if hasattr(db.bind, 'pool') else None
            pool_info = {}
            if pool:
                pool_info = {
                    "active": getattr(pool, 'checkedout', 0),
                    "idle": getattr(pool, 'checkedin', 0),
                    "max": getattr(pool, 'size', 0) + getattr(pool, 'max_overflow', 0)
                }
            
            # 获取数据库版本
            version_result = await db.execute(text("SELECT VERSION()"))
            version = version_result.scalar()
            
            return {
                "status": "healthy",
                "connection_pool": pool_info,
                "version": version,
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"检查数据库健康状态失败: {str(e)}", exc_info=True)
            return {
                "status": "unhealthy",
                "connection_pool": {},
                "version": None,
                "last_check": datetime.now().isoformat(),
                "error_message": str(e)
            }

