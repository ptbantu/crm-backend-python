"""
临时链接相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TemporaryLinkCreateRequest(BaseModel):
    """创建临时链接请求"""
    resource_type: str = Field(..., description="资源类型：service_account, order, customer")
    resource_id: str = Field(..., description="资源ID")
    expires_at: Optional[datetime] = Field(None, description="过期时间")
    max_access_count: int = Field(default=1, gt=0, description="最大访问次数")


class TemporaryLinkResponse(BaseModel):
    """临时链接响应"""
    id: str
    link_token: str
    resource_type: str
    resource_id: str
    expires_at: Optional[datetime] = None
    max_access_count: int
    current_access_count: int
    is_active: bool
    created_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TemporaryLinkAccessResponse(BaseModel):
    """临时链接访问响应"""
    link: TemporaryLinkResponse
    resource_data: Optional[dict] = None

