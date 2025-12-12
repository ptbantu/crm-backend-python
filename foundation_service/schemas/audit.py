"""
审计日志相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class AuditLogCreateRequest(BaseModel):
    """创建审计日志请求"""
    organization_id: str = Field(..., description="组织ID")
    user_id: Optional[str] = Field(None, description="操作用户ID")
    user_name: Optional[str] = Field(None, description="操作用户名称")
    action: str = Field(..., description="操作类型：CREATE, UPDATE, DELETE, VIEW, LOGIN, LOGOUT 等")
    resource_type: Optional[str] = Field(None, description="资源类型：user, organization, order, lead, customer 等")
    resource_id: Optional[str] = Field(None, description="资源ID")
    resource_name: Optional[str] = Field(None, description="资源名称")
    category: Optional[str] = Field(None, description="操作分类：user_management, order_management, customer_management 等")
    ip_address: Optional[str] = Field(None, description="IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理")
    request_method: Optional[str] = Field(None, description="HTTP方法：GET, POST, PUT, DELETE 等")
    request_path: Optional[str] = Field(None, description="请求路径")
    request_params: Optional[Dict[str, Any]] = Field(None, description="请求参数")
    old_values: Optional[Dict[str, Any]] = Field(None, description="修改前的值")
    new_values: Optional[Dict[str, Any]] = Field(None, description="修改后的值")
    status: str = Field(default="success", description="操作状态：success, failed")
    error_message: Optional[str] = Field(None, description="错误信息")
    duration_ms: Optional[int] = Field(None, description="操作耗时（毫秒）")


class AuditLogResponse(BaseModel):
    """审计日志响应"""
    id: str
    organization_id: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    category: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_method: Optional[str] = None
    request_path: Optional[str] = None
    request_params: Optional[Dict[str, Any]] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    status: str
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditLogQueryRequest(BaseModel):
    """查询审计日志请求"""
    page: int = Field(default=1, ge=1, description="页码（从1开始）")
    size: int = Field(default=10, ge=1, le=100, description="每页数量（最大100）")
    organization_id: Optional[str] = Field(None, description="组织ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    action: Optional[str] = Field(None, description="操作类型")
    resource_type: Optional[str] = Field(None, description="资源类型")
    resource_id: Optional[str] = Field(None, description="资源ID")
    category: Optional[str] = Field(None, description="操作分类")
    status: Optional[str] = Field(None, description="操作状态")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    order_by: str = Field(default="created_at", description="排序字段")
    order_desc: bool = Field(default=True, description="是否降序")


class AuditLogListResponse(BaseModel):
    """审计日志列表响应"""
    records: List[AuditLogResponse]
    total: int
    size: int
    page: int
    pages: int


class AuditLogExportRequest(BaseModel):
    """导出审计日志请求"""
    organization_id: Optional[str] = Field(None, description="组织ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    action: Optional[str] = Field(None, description="操作类型")
    resource_type: Optional[str] = Field(None, description="资源类型")
    resource_id: Optional[str] = Field(None, description="资源ID")
    category: Optional[str] = Field(None, description="操作分类")
    status: Optional[str] = Field(None, description="操作状态")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    format: str = Field(default="json", pattern="^(json|csv)$", description="导出格式：json 或 csv")
