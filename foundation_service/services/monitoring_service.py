"""
监控服务
"""
import time
from typing import List, Dict
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from foundation_service.schemas.monitoring import (
    ServicesHealthResponse,
    ServiceHealthResponse,
    DatabaseHealthResponse,
    SystemMetricsResponse,
    DatabaseMetricsResponse,
    ActiveAlertsResponse,
    AlertResponse,
)
from foundation_service.utils.health_checker import HealthChecker
from foundation_service.utils.metrics_collector import MetricsCollector
from foundation_service.utils.alert_manager import alert_manager, AlertLevel, AlertStatus
from common.utils.logger import get_logger

logger = get_logger(__name__)


class MonitoringService:
    """监控服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.health_checker = HealthChecker()
        self.metrics_collector = MetricsCollector()
    
    async def get_services_health(self) -> ServicesHealthResponse:
        """获取所有服务健康状态"""
        method_name = "get_services_health"
        start_time = time.time()
        # Health check 不记录日志，避免影响 debug
        # logger.info(f"[Service] {method_name} - 方法调用开始")
        
        try:
            services_data = await self.health_checker.check_all_services_health()
            services = [
                ServiceHealthResponse(**service_data)
                for service_data in services_data
            ]
            
            # 计算整体状态
            unhealthy_count = sum(1 for s in services if s.status != "healthy")
            if unhealthy_count == 0:
                overall_status = "healthy"
            elif unhealthy_count < len(services) / 2:
                overall_status = "degraded"
            else:
                overall_status = "down"
            
            result = ServicesHealthResponse(
                services=services,
                overall_status=overall_status
            )
            
            elapsed_time = (time.time() - start_time) * 1000
            # Health check 成功不记录日志，避免影响 debug
            # logger.info(
            #     f"[Service] {method_name} - 方法调用成功 | "
            #     f"耗时: {elapsed_time:.2f}ms | "
            #     f"结果: overall_status={result.overall_status}, services_count={len(result.services)}"
            # )
            
            return result
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise
    
    async def get_database_health(self) -> DatabaseHealthResponse:
        """获取数据库健康状态"""
        method_name = "get_database_health"
        start_time = time.time()
        # Health check 不记录日志，避免影响 debug
        # logger.info(f"[Service] {method_name} - 方法调用开始")
        
        try:
            health_data = await self.health_checker.check_database_health(self.db)
            result = DatabaseHealthResponse(**health_data)
            
            elapsed_time = (time.time() - start_time) * 1000
            # Health check 成功不记录日志，避免影响 debug
            # logger.info(
            #     f"[Service] {method_name} - 方法调用成功 | "
            #     f"耗时: {elapsed_time:.2f}ms | "
            #     f"结果: status={result.status}"
            # )
            
            return result
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise
    
    async def get_system_metrics(self) -> SystemMetricsResponse:
        """获取系统指标"""
        method_name = "get_system_metrics"
        start_time = time.time()
        logger.info(f"[Service] {method_name} - 方法调用开始")
        
        try:
            metrics = self.metrics_collector.collect_system_metrics()
            
            # 检查阈值并生成预警
            alerts = alert_manager.check_thresholds(metrics)
            if alerts:
                logger.info(f"检测到 {len(alerts)} 个预警")
            
            result = SystemMetricsResponse(**metrics)
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"结果: cpu={result.cpu_usage_percent}%, memory={result.memory_usage_percent}%"
            )
            
            return result
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise
    
    async def get_database_metrics(self) -> DatabaseMetricsResponse:
        """获取数据库指标"""
        method_name = "get_database_metrics"
        start_time = time.time()
        logger.info(f"[Service] {method_name} - 方法调用开始")
        
        try:
            metrics = await self.metrics_collector.collect_database_metrics(self.db)
            result = DatabaseMetricsResponse(**metrics)
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"结果: active_connections={result.active_connections}, idle_connections={result.idle_connections}"
            )
            
            return result
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise
    
    async def get_active_alerts(self) -> ActiveAlertsResponse:
        """获取活跃预警列表"""
        method_name = "get_active_alerts"
        start_time = time.time()
        logger.info(f"[Service] {method_name} - 方法调用开始")
        
        try:
            alerts = alert_manager.get_active_alerts()
            alert_responses = [
                AlertResponse(
                    id=alert.id,
                    level=AlertLevel(alert.level.value),
                    title=alert.title,
                    message=alert.message,
                    status=AlertStatus(alert.status.value),
                    created_at=alert.created_at,
                    acknowledged_at=alert.acknowledged_at,
                    resolved_at=alert.resolved_at
                )
                for alert in alerts
            ]
            
            # 按级别统计
            by_level = {}
            for alert in alerts:
                level = alert.level.value
                by_level[level] = by_level.get(level, 0) + 1
            
            result = ActiveAlertsResponse(
                alerts=alert_responses,
                total=len(alert_responses),
                by_level=by_level
            )
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"结果: total={result.total}, by_level={result.by_level}"
            )
            
            return result
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """确认预警"""
        method_name = "acknowledge_alert"
        start_time = time.time()
        logger.info(f"[Service] {method_name} - 方法调用开始 | 参数: alert_id={alert_id}")
        
        try:
            result = alert_manager.acknowledge_alert(alert_id)
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"结果: success={result}"
            )
            
            return result
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise

