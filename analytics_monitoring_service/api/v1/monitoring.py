"""
监控 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from common.utils.logger import get_logger
from analytics_monitoring_service.schemas.monitoring import (
    ServicesHealthResponse,
    DatabaseHealthResponse,
    SystemMetricsResponse,
    DatabaseMetricsResponse,
    ActiveAlertsResponse,
)
from analytics_monitoring_service.services.monitoring_service import MonitoringService
from analytics_monitoring_service.dependencies import get_db

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health/services", response_model=Result[ServicesHealthResponse])
async def get_services_health(
    db: AsyncSession = Depends(get_db)
):
    """获取所有服务健康状态"""
    logger.info("API: 获取所有服务健康状态")
    try:
        service = MonitoringService(db)
        health = await service.get_services_health()
        return Result.success(data=health, message="获取服务健康状态成功")
    except Exception as e:
        logger.error(f"API: 获取服务健康状态失败: {str(e)}", exc_info=True)
        raise


@router.get("/health/database", response_model=Result[DatabaseHealthResponse])
async def get_database_health(
    db: AsyncSession = Depends(get_db)
):
    """获取数据库健康状态"""
    logger.info("API: 获取数据库健康状态")
    try:
        service = MonitoringService(db)
        health = await service.get_database_health()
        return Result.success(data=health, message="获取数据库健康状态成功")
    except Exception as e:
        logger.error(f"API: 获取数据库健康状态失败: {str(e)}", exc_info=True)
        raise


@router.get("/metrics/system", response_model=Result[SystemMetricsResponse])
async def get_system_metrics(
    db: AsyncSession = Depends(get_db)
):
    """获取系统指标"""
    logger.info("API: 获取系统指标")
    try:
        service = MonitoringService(db)
        metrics = await service.get_system_metrics()
        return Result.success(data=metrics, message="获取系统指标成功")
    except Exception as e:
        logger.error(f"API: 获取系统指标失败: {str(e)}", exc_info=True)
        raise


@router.get("/metrics/database", response_model=Result[DatabaseMetricsResponse])
async def get_database_metrics(
    db: AsyncSession = Depends(get_db)
):
    """获取数据库指标"""
    logger.info("API: 获取数据库指标")
    try:
        service = MonitoringService(db)
        metrics = await service.get_database_metrics()
        return Result.success(data=metrics, message="获取数据库指标成功")
    except Exception as e:
        logger.error(f"API: 获取数据库指标失败: {str(e)}", exc_info=True)
        raise


@router.get("/alerts/active", response_model=Result[ActiveAlertsResponse])
async def get_active_alerts(
    db: AsyncSession = Depends(get_db)
):
    """获取活跃预警列表"""
    logger.info("API: 获取活跃预警列表")
    try:
        service = MonitoringService(db)
        alerts = await service.get_active_alerts()
        return Result.success(data=alerts, message="获取活跃预警列表成功")
    except Exception as e:
        logger.error(f"API: 获取活跃预警列表失败: {str(e)}", exc_info=True)
        raise


@router.post("/alerts/{alert_id}/acknowledge", response_model=Result[bool])
async def acknowledge_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db)
):
    """确认预警"""
    logger.info(f"API: 确认预警: alert_id={alert_id}")
    try:
        service = MonitoringService(db)
        success = await service.acknowledge_alert(alert_id)
        if success:
            return Result.success(data=True, message="预警确认成功")
        else:
            return Result.error(code=404, message="预警不存在")
    except Exception as e:
        logger.error(f"API: 确认预警失败: {str(e)}", exc_info=True)
        raise

