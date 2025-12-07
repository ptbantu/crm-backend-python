"""
服务类型 Schema
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ServiceTypeCreateRequest(BaseModel):
    """创建服务类型请求"""
    code: str = Field(..., max_length=50, description="类型代码")
    name: str = Field(..., max_length=255, description="类型名称（中文）")
    name_en: Optional[str] = Field(None, max_length=255, description="类型名称（英文）")
    description: Optional[str] = Field(None, description="类型描述")
    display_order: int = Field(0, ge=0, description="显示顺序")
    is_active: bool = Field(True, description="是否激活")


class ServiceTypeUpdateRequest(BaseModel):
    """更新服务类型请求"""
    name: Optional[str] = Field(None, max_length=255, description="类型名称（中文）")
    name_en: Optional[str] = Field(None, max_length=255, description="类型名称（英文）")
    description: Optional[str] = Field(None, description="类型描述")
    display_order: Optional[int] = Field(None, ge=0, description="显示顺序")
    is_active: Optional[bool] = Field(None, description="是否激活")


class ServiceTypeResponse(BaseModel):
    """服务类型响应"""
    id: str
    code: str
    name: str
    name_en: Optional[str] = None
    description: Optional[str] = None
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ServiceTypeListResponse(BaseModel):
    """服务类型列表响应"""
    items: list[ServiceTypeResponse]
    total: int
    page: int
    size: int



