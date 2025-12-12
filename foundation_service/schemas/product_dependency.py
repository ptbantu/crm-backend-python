"""
产品依赖关系相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# 产品依赖关系响应
class ProductDependencyResponse(BaseModel):
    """产品依赖关系响应"""
    id: str
    product_id: str
    product_name: Optional[str] = None
    product_code: Optional[str] = None
    depends_on_product_id: str
    depends_on_product_name: Optional[str] = None
    depends_on_product_code: Optional[str] = None
    dependency_type: str  # required, recommended, optional
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# 创建产品依赖关系请求
class ProductDependencyCreateRequest(BaseModel):
    """创建产品依赖关系请求"""
    product_id: str = Field(..., description="产品ID")
    depends_on_product_id: str = Field(..., description="依赖的产品ID")
    dependency_type: str = Field(default="required", description="依赖类型（required, recommended, optional）")
    description: Optional[str] = Field(None, description="依赖说明")


# 更新产品依赖关系请求
class ProductDependencyUpdateRequest(BaseModel):
    """更新产品依赖关系请求"""
    dependency_type: Optional[str] = Field(None, description="依赖类型（required, recommended, optional）")
    description: Optional[str] = Field(None, description="依赖说明")


# 产品依赖关系列表响应
class ProductDependencyListResponse(BaseModel):
    """产品依赖关系列表响应"""
    records: List[ProductDependencyResponse]
    total: int
    size: int
    current: int
    pages: int

