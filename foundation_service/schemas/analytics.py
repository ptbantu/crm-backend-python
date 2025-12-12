"""
数据分析相关模式
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class CustomerSummaryResponse(BaseModel):
    """客户统计摘要"""
    total: int = Field(..., description="客户总数")
    by_type: Dict[str, int] = Field(default_factory=dict, description="按类型统计")
    by_source: Dict[str, int] = Field(default_factory=dict, description="按来源统计")
    active_count: int = Field(default=0, description="活跃客户数（最近30天有服务记录）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 100,
                "by_type": {"individual": 60, "organization": 40},
                "by_source": {"own": 70, "agent": 30},
                "active_count": 45
            }
        }


class TrendDataPoint(BaseModel):
    """趋势数据点"""
    date: str = Field(..., description="日期")
    value: int = Field(..., description="数值")
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2025-01-01",
                "value": 10
            }
        }


class CustomerTrendResponse(BaseModel):
    """客户增长趋势"""
    period: str = Field(..., description="统计周期：day, week, month")
    data: List[TrendDataPoint] = Field(default_factory=list, description="趋势数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "period": "day",
                "data": [
                    {"date": "2025-01-01", "value": 10},
                    {"date": "2025-01-02", "value": 15}
                ]
            }
        }


class OrderSummaryResponse(BaseModel):
    """订单统计摘要"""
    total: int = Field(..., description="订单总数")
    by_status: Dict[str, int] = Field(default_factory=dict, description="按状态统计")
    by_service_type: Dict[str, int] = Field(default_factory=dict, description="按服务类型统计")
    total_revenue: float = Field(default=0.0, description="总收入")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 200,
                "by_status": {"pending": 10, "processing": 50, "completed": 140},
                "by_service_type": {"visa": 100, "company_registration": 100},
                "total_revenue": 50000.0
            }
        }


class RevenueResponse(BaseModel):
    """收入统计"""
    period: str = Field(..., description="统计周期：day, week, month")
    total: float = Field(..., description="总收入")
    data: List[TrendDataPoint] = Field(default_factory=list, description="收入趋势数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "period": "month",
                "total": 50000.0,
                "data": [
                    {"date": "2025-01", "value": 20000},
                    {"date": "2025-02", "value": 30000}
                ]
            }
        }


class ServiceRecordStatisticsResponse(BaseModel):
    """服务记录统计"""
    total: int = Field(..., description="服务记录总数")
    by_status: Dict[str, int] = Field(default_factory=dict, description="按状态统计")
    by_priority: Dict[str, int] = Field(default_factory=dict, description="按优先级统计")
    by_assignee: Dict[str, int] = Field(default_factory=dict, description="按接单人员统计")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 150,
                "by_status": {"pending": 20, "in_progress": 50, "completed": 80},
                "by_priority": {"high": 30, "medium": 70, "low": 50},
                "by_assignee": {"user1": 50, "user2": 100}
            }
        }


class UserActivityResponse(BaseModel):
    """用户活跃度统计"""
    total_users: int = Field(..., description="用户总数")
    active_users: int = Field(..., description="活跃用户数（最近30天登录）")
    by_role: Dict[str, int] = Field(default_factory=dict, description="按角色统计")
    last_login_stats: Dict[str, int] = Field(default_factory=dict, description="最后登录时间统计")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_users": 50,
                "active_users": 35,
                "by_role": {"ADMIN": 5, "SALES": 20, "OPERATION": 25},
                "last_login_stats": {"today": 10, "week": 20, "month": 5}
            }
        }


class OrganizationSummaryResponse(BaseModel):
    """组织统计摘要"""
    total: int = Field(..., description="组织总数")
    total_employees: int = Field(..., description="员工总数")
    by_type: Dict[str, int] = Field(default_factory=dict, description="按类型统计")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 10,
                "total_employees": 50,
                "by_type": {"internal": 1, "agent": 5, "vendor": 4}
            }
        }

