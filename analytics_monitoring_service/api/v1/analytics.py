"""
数据分析 API
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from common.utils.logger import get_logger
from analytics_monitoring_service.schemas.analytics import (
    CustomerSummaryResponse,
    CustomerTrendResponse,
    OrderSummaryResponse,
    RevenueResponse,
    ServiceRecordStatisticsResponse,
    UserActivityResponse,
    OrganizationSummaryResponse,
)
from analytics_monitoring_service.services.analytics_service import AnalyticsService
from analytics_monitoring_service.dependencies import get_db

logger = get_logger(__name__)
router = APIRouter()


@router.get("/customers/summary", response_model=Result[CustomerSummaryResponse])
async def get_customer_summary(
    db: AsyncSession = Depends(get_db)
):
    """获取客户统计摘要"""
    logger.info("API: 获取客户统计摘要")
    try:
        service = AnalyticsService(db)
        summary = await service.get_customer_summary()
        return Result.success(data=summary, message="获取客户统计摘要成功")
    except Exception as e:
        logger.error(f"API: 获取客户统计摘要失败: {str(e)}", exc_info=True)
        raise


@router.get("/customers/trend", response_model=Result[CustomerTrendResponse])
async def get_customer_trend(
    period: str = Query(default="day", description="统计周期：day, week, month"),
    db: AsyncSession = Depends(get_db)
):
    """获取客户增长趋势"""
    logger.info(f"API: 获取客户增长趋势: period={period}")
    try:
        service = AnalyticsService(db)
        trend = await service.get_customer_trend(period)
        return Result.success(data=trend, message="获取客户增长趋势成功")
    except Exception as e:
        logger.error(f"API: 获取客户增长趋势失败: {str(e)}", exc_info=True)
        raise


@router.get("/orders/summary", response_model=Result[OrderSummaryResponse])
async def get_order_summary(
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    db: AsyncSession = Depends(get_db)
):
    """获取订单统计摘要"""
    logger.info(f"API: 获取订单统计摘要: start_date={start_date}, end_date={end_date}")
    try:
        service = AnalyticsService(db)
        summary = await service.get_order_summary(start_date, end_date)
        return Result.success(data=summary, message="获取订单统计摘要成功")
    except Exception as e:
        logger.error(f"API: 获取订单统计摘要失败: {str(e)}", exc_info=True)
        raise


@router.get("/orders/revenue", response_model=Result[RevenueResponse])
async def get_revenue(
    period: str = Query(default="month", description="统计周期：day, week, month"),
    db: AsyncSession = Depends(get_db)
):
    """获取收入统计"""
    logger.info(f"API: 获取收入统计: period={period}")
    try:
        service = AnalyticsService(db)
        revenue = await service.get_revenue(period)
        return Result.success(data=revenue, message="获取收入统计成功")
    except Exception as e:
        logger.error(f"API: 获取收入统计失败: {str(e)}", exc_info=True)
        raise


@router.get("/service-records/statistics", response_model=Result[ServiceRecordStatisticsResponse])
async def get_service_record_statistics(
    db: AsyncSession = Depends(get_db)
):
    """获取服务记录统计"""
    logger.info("API: 获取服务记录统计")
    try:
        service = AnalyticsService(db)
        statistics = await service.get_service_record_statistics()
        return Result.success(data=statistics, message="获取服务记录统计成功")
    except Exception as e:
        logger.error(f"API: 获取服务记录统计失败: {str(e)}", exc_info=True)
        raise


@router.get("/users/activity", response_model=Result[UserActivityResponse])
async def get_user_activity(
    db: AsyncSession = Depends(get_db)
):
    """获取用户活跃度统计"""
    logger.info("API: 获取用户活跃度统计")
    try:
        service = AnalyticsService(db)
        activity = await service.get_user_activity()
        return Result.success(data=activity, message="获取用户活跃度统计成功")
    except Exception as e:
        logger.error(f"API: 获取用户活跃度统计失败: {str(e)}", exc_info=True)
        raise


@router.get("/organizations/summary", response_model=Result[OrganizationSummaryResponse])
async def get_organization_summary(
    db: AsyncSession = Depends(get_db)
):
    """获取组织统计摘要"""
    logger.info("API: 获取组织统计摘要")
    try:
        service = AnalyticsService(db)
        summary = await service.get_organization_summary()
        return Result.success(data=summary, message="获取组织统计摘要成功")
    except Exception as e:
        logger.error(f"API: 获取组织统计摘要失败: {str(e)}", exc_info=True)
        raise

