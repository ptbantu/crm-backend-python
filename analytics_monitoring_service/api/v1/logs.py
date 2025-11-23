"""
日志查询 API
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from datetime import datetime

from common.schemas.response import Result
from common.utils.logger import get_logger
from analytics_monitoring_service.schemas.log import (
    LogQueryRequest,
    LogQueryResponse,
    LogStatisticsResponse,
)
from analytics_monitoring_service.services.log_service import LogService

logger = get_logger(__name__)
router = APIRouter()


@router.post("/query", response_model=Result[LogQueryResponse])
async def query_logs(query: LogQueryRequest):
    """
    查询日志
    
    支持条件查询：
    - 服务名称过滤（services）
    - 日志级别过滤（levels）
    - 时间范围过滤（start_time, end_time）
    - 关键词搜索（keyword，在 message 字段中搜索）
    - 文件名过滤（file，支持部分匹配）
    - 函数名过滤（function，支持部分匹配）
    
    结果按时间戳倒序排列（最新的在前），支持分页。
    """
    logger.info(f"API: 查询日志 - services={query.services}, levels={query.levels}, page={query.page}")
    try:
        service = LogService()
        result = await service.query_logs(query)
        return Result.success(data=result, message="查询日志成功")
    except RuntimeError as e:
        logger.error(f"API: MongoDB 连接失败: {str(e)}", exc_info=True)
        return Result.error(code=503, message=f"MongoDB 连接失败: {str(e)}")
    except Exception as e:
        logger.error(f"API: 查询日志失败: {str(e)}", exc_info=True)
        return Result.error(code=500, message=f"查询日志失败: {str(e)}")


@router.get("/query", response_model=Result[LogQueryResponse])
async def query_logs_get(
    services: Optional[str] = Query(None, description="服务名称列表，逗号分隔（如：foundation-service,order-workflow-service）"),
    levels: Optional[str] = Query(None, description="日志级别列表，逗号分隔（如：ERROR,WARNING）"),
    start_time: Optional[datetime] = Query(None, description="开始时间（ISO 8601 格式）"),
    end_time: Optional[datetime] = Query(None, description="结束时间（ISO 8601 格式）"),
    keyword: Optional[str] = Query(None, description="关键词搜索（在 message 字段中搜索）"),
    file: Optional[str] = Query(None, description="文件名过滤（支持部分匹配）"),
    function: Optional[str] = Query(None, description="函数名过滤（支持部分匹配）"),
    page: int = Query(1, ge=1, description="页码（从1开始）"),
    page_size: int = Query(50, ge=1, le=500, description="每页数量（最大500）"),
):
    """
    查询日志（GET 方式，方便浏览器直接访问）
    
    支持条件查询，参数通过 URL 查询字符串传递。
    结果按时间戳倒序排列（最新的在前），支持分页。
    """
    # 解析逗号分隔的列表
    services_list = None
    if services:
        services_list = [s.strip() for s in services.split(",") if s.strip()]
    
    levels_list = None
    if levels:
        levels_list = [l.strip() for l in levels.split(",") if l.strip()]
    
    query = LogQueryRequest(
        services=services_list,
        levels=levels_list,
        start_time=start_time,
        end_time=end_time,
        keyword=keyword,
        file=file,
        function=function,
        page=page,
        page_size=page_size,
    )
    
    logger.info(f"API: 查询日志（GET）- services={services_list}, levels={levels_list}, page={page}")
    try:
        service = LogService()
        result = await service.query_logs(query)
        return Result.success(data=result, message="查询日志成功")
    except RuntimeError as e:
        logger.error(f"API: MongoDB 连接失败: {str(e)}", exc_info=True)
        return Result.error(code=503, message=f"MongoDB 连接失败: {str(e)}")
    except Exception as e:
        logger.error(f"API: 查询日志失败: {str(e)}", exc_info=True)
        return Result.error(code=500, message=f"查询日志失败: {str(e)}")


@router.get("/statistics", response_model=Result[LogStatisticsResponse])
async def get_log_statistics(
    services: Optional[str] = Query(None, description="服务名称列表，逗号分隔（如：foundation-service,order-workflow-service）"),
    start_time: Optional[datetime] = Query(None, description="开始时间（ISO 8601 格式）"),
    end_time: Optional[datetime] = Query(None, description="结束时间（ISO 8601 格式）"),
):
    """
    获取日志统计信息
    
    统计指定时间范围内的日志数量、按级别统计、按服务统计等。
    """
    # 解析逗号分隔的列表
    services_list = None
    if services:
        services_list = [s.strip() for s in services.split(",") if s.strip()]
    
    logger.info(f"API: 获取日志统计 - services={services_list}, start_time={start_time}, end_time={end_time}")
    try:
        service = LogService()
        result = await service.get_log_statistics(
            services=services_list,
            start_time=start_time,
            end_time=end_time,
        )
        return Result.success(data=result, message="获取日志统计成功")
    except RuntimeError as e:
        logger.error(f"API: MongoDB 连接失败: {str(e)}", exc_info=True)
        return Result.error(code=503, message=f"MongoDB 连接失败: {str(e)}")
    except Exception as e:
        logger.error(f"API: 获取日志统计失败: {str(e)}", exc_info=True)
        return Result.error(code=500, message=f"获取日志统计失败: {str(e)}")

