"""
日志查询相关模式
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class LogLevel(str, Enum):
    """日志级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogEntryResponse(BaseModel):
    """日志条目响应"""
    id: str = Field(..., description="日志ID（MongoDB ObjectId）")
    timestamp: datetime = Field(..., description="日志时间戳")
    level: str = Field(..., description="日志级别")
    message: str = Field(..., description="日志消息")
    service: Optional[str] = Field(None, description="服务名称")
    name: Optional[str] = Field(None, description="Logger 名称")
    function: Optional[str] = Field(None, description="函数名")
    line: Optional[int] = Field(None, description="行号")
    file: Optional[str] = Field(None, description="文件路径")
    module: Optional[str] = Field(None, description="模块名")
    thread: Optional[int] = Field(None, description="线程ID")
    process: Optional[int] = Field(None, description="进程ID")
    exception: Optional[Dict[str, Any]] = Field(None, description="异常信息")
    extra: Optional[Dict[str, Any]] = Field(None, description="额外字段")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "timestamp": "2025-01-01T12:00:00",
                "level": "INFO",
                "message": "用户登录成功",
                "service": "foundation-service",
                "name": "foundation_service.api.v1.auth",
                "function": "login",
                "line": 45,
                "file": "/app/foundation_service/api/v1/auth.py",
                "module": "auth",
                "thread": 12345,
                "process": 1
            }
        }


class LogQueryRequest(BaseModel):
    """日志查询请求"""
    # 服务名称（可选，支持多个服务）
    services: Optional[List[str]] = Field(None, description="服务名称列表（如：['foundation-service', 'order-workflow-service']）")
    
    # 日志级别（可选，支持多个级别）
    levels: Optional[List[str]] = Field(None, description="日志级别列表（如：['ERROR', 'WARNING']）")
    
    # 时间范围
    start_time: Optional[datetime] = Field(None, description="开始时间（ISO 8601 格式）")
    end_time: Optional[datetime] = Field(None, description="结束时间（ISO 8601 格式）")
    
    # 关键词搜索
    keyword: Optional[str] = Field(None, description="关键词搜索（在 message 字段中搜索）")
    
    # 文件名过滤
    file: Optional[str] = Field(None, description="文件名过滤（支持部分匹配）")
    
    # 函数名过滤
    function: Optional[str] = Field(None, description="函数名过滤（支持部分匹配）")
    
    # 分页参数
    page: int = Field(1, ge=1, description="页码（从1开始）")
    page_size: int = Field(50, ge=1, le=500, description="每页数量（最大500）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "services": ["foundation-service"],
                "levels": ["ERROR", "WARNING"],
                "start_time": "2025-01-01T00:00:00",
                "end_time": "2025-01-01T23:59:59",
                "keyword": "登录失败",
                "page": 1,
                "page_size": 50
            }
        }


class LogQueryResponse(BaseModel):
    """日志查询响应"""
    logs: List[LogEntryResponse] = Field(default_factory=list, description="日志列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")
    
    class Config:
        json_schema_extra = {
            "example": {
                "logs": [
                    {
                        "id": "507f1f77bcf86cd799439011",
                        "timestamp": "2025-01-01T12:00:00",
                        "level": "ERROR",
                        "message": "用户登录失败",
                        "service": "foundation-service"
                    }
                ],
                "total": 100,
                "page": 1,
                "page_size": 50,
                "total_pages": 2
            }
        }


class LogStatisticsResponse(BaseModel):
    """日志统计响应"""
    total_logs: int = Field(..., description="总日志数")
    by_level: Dict[str, int] = Field(default_factory=dict, description="按级别统计")
    by_service: Dict[str, int] = Field(default_factory=dict, description="按服务统计")
    error_count: int = Field(..., description="错误日志数量")
    warning_count: int = Field(..., description="警告日志数量")
    time_range: Dict[str, Optional[datetime]] = Field(default_factory=dict, description="时间范围")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_logs": 1000,
                "by_level": {
                    "INFO": 800,
                    "WARNING": 150,
                    "ERROR": 50
                },
                "by_service": {
                    "foundation-service": 500,
                    "order-workflow-service": 300,
                    "analytics-monitoring-service": 200
                },
                "error_count": 50,
                "warning_count": 150,
                "time_range": {
                    "start": "2025-01-01T00:00:00",
                    "end": "2025-01-01T23:59:59"
                }
            }
        }

