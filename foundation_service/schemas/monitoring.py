"""
监控相关模式
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AlertLevel(str, Enum):
    """预警级别"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertStatus(str, Enum):
    """预警状态"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class ServiceHealthResponse(BaseModel):
    """服务健康状态"""
    service_name: str = Field(..., description="服务名称")
    status: str = Field(..., description="状态：healthy, unhealthy, unknown")
    response_time_ms: Optional[float] = Field(None, description="响应时间（毫秒）")
    last_check: datetime = Field(..., description="最后检查时间")
    error_message: Optional[str] = Field(None, description="错误信息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "service_name": "foundation-service",
                "status": "healthy",
                "response_time_ms": 45.2,
                "last_check": "2025-01-01T12:00:00",
                "error_message": None
            }
        }


class ServicesHealthResponse(BaseModel):
    """所有服务健康状态"""
    services: List[ServiceHealthResponse] = Field(default_factory=list, description="服务列表")
    overall_status: str = Field(..., description="整体状态：healthy, degraded, down")
    
    class Config:
        json_schema_extra = {
            "example": {
                "services": [
                    {
                        "service_name": "foundation-service",
                        "status": "healthy",
                        "response_time_ms": 45.2,
                        "last_check": "2025-01-01T12:00:00"
                    }
                ],
                "overall_status": "healthy"
            }
        }


class DatabaseHealthResponse(BaseModel):
    """数据库健康状态"""
    status: str = Field(..., description="状态：healthy, unhealthy")
    connection_pool: Dict[str, Any] = Field(default_factory=dict, description="连接池信息")
    version: Optional[str] = Field(None, description="数据库版本")
    last_check: datetime = Field(..., description="最后检查时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "connection_pool": {
                    "active": 5,
                    "idle": 10,
                    "max": 20
                },
                "version": "8.0.35",
                "last_check": "2025-01-01T12:00:00"
            }
        }


class SystemMetricsResponse(BaseModel):
    """系统指标"""
    cpu_usage_percent: float = Field(..., description="CPU 使用率（%）")
    memory_usage_percent: float = Field(..., description="内存使用率（%）")
    memory_used_mb: float = Field(..., description="已使用内存（MB）")
    memory_total_mb: float = Field(..., description="总内存（MB）")
    disk_usage_percent: Optional[float] = Field(None, description="磁盘使用率（%）")
    timestamp: datetime = Field(..., description="采集时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "cpu_usage_percent": 45.2,
                "memory_usage_percent": 60.5,
                "memory_used_mb": 2048,
                "memory_total_mb": 4096,
                "disk_usage_percent": 75.0,
                "timestamp": "2025-01-01T12:00:00"
            }
        }


class DatabaseMetricsResponse(BaseModel):
    """数据库指标"""
    active_connections: int = Field(..., description="活跃连接数")
    idle_connections: int = Field(..., description="空闲连接数")
    max_connections: int = Field(..., description="最大连接数")
    slow_queries_count: int = Field(default=0, description="慢查询数量")
    timestamp: datetime = Field(..., description="采集时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "active_connections": 5,
                "idle_connections": 10,
                "max_connections": 20,
                "slow_queries_count": 2,
                "timestamp": "2025-01-01T12:00:00"
            }
        }


class AlertResponse(BaseModel):
    """预警响应"""
    id: str = Field(..., description="预警ID")
    level: AlertLevel = Field(..., description="预警级别")
    title: str = Field(..., description="预警标题")
    message: str = Field(..., description="预警消息")
    status: AlertStatus = Field(..., description="预警状态")
    created_at: datetime = Field(..., description="创建时间")
    acknowledged_at: Optional[datetime] = Field(None, description="确认时间")
    resolved_at: Optional[datetime] = Field(None, description="解决时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "alert-001",
                "level": "WARNING",
                "title": "CPU 使用率过高",
                "message": "CPU 使用率达到 85%",
                "status": "active",
                "created_at": "2025-01-01T12:00:00"
            }
        }


class ActiveAlertsResponse(BaseModel):
    """活跃预警列表"""
    alerts: List[AlertResponse] = Field(default_factory=list, description="预警列表")
    total: int = Field(..., description="总数")
    by_level: Dict[str, int] = Field(default_factory=dict, description="按级别统计")
    
    class Config:
        json_schema_extra = {
            "example": {
                "alerts": [
                    {
                        "id": "alert-001",
                        "level": "WARNING",
                        "title": "CPU 使用率过高",
                        "status": "active",
                        "created_at": "2025-01-01T12:00:00"
                    }
                ],
                "total": 1,
                "by_level": {"WARNING": 1}
            }
        }

