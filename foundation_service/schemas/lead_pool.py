"""
线索池相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LeadPoolCreateRequest(BaseModel):
    """创建线索池请求"""
    name: str = Field(..., max_length=255, description="线索池名称")
    description: Optional[str] = Field(None, description="描述")
    is_active: bool = Field(default=True, description="是否激活")


class LeadPoolUpdateRequest(BaseModel):
    """更新线索池请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class LeadPoolResponse(BaseModel):
    """线索池响应"""
    id: str
    name: str
    organization_id: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

