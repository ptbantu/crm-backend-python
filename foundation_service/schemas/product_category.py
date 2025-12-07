"""
产品分类相关模式
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProductCategoryCreateRequest(BaseModel):
    """创建产品分类请求"""
    code: str = Field(..., min_length=1, max_length=100, description="分类编码（全局唯一）")
    name: str = Field(..., min_length=1, max_length=255, description="分类名称")
    description: Optional[str] = Field(None, description="分类描述")
    parent_id: Optional[str] = Field(None, description="父分类ID（支持分类层级）")
    display_order: int = Field(default=0, ge=0, description="显示顺序")
    is_active: bool = Field(default=True, description="是否激活")


class ProductCategoryUpdateRequest(BaseModel):
    """更新产品分类请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    parent_id: Optional[str] = None
    display_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ProductCategoryResponse(BaseModel):
    """产品分类响应"""
    id: str
    code: str
    name: str
    description: Optional[str]
    parent_id: Optional[str]
    parent_name: Optional[str] = None  # 父分类名称（需要关联查询）
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProductCategoryListResponse(BaseModel):
    """产品分类列表响应"""
    items: List[ProductCategoryResponse]
    total: int
    page: int
    size: int

