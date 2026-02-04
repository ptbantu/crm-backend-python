from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SupplierResponse(BaseModel):
    """供应商响应"""
    id: str
    name: str
    code: Optional[str]
    organization_type: str
    email: Optional[str]
    phone: Optional[str]
    is_active: bool
    is_locked: bool
    service_count: int = 0  # 服务数量
    created_at: Any
    updated_at: Any
    
    class Config:
        from_attributes = True


class SupplierListResponse(BaseModel):
    """供应商列表响应"""
    items: List[SupplierResponse]
    total: int
    page: int
    size: int


class SupplierServiceResponse(BaseModel):
    """供应商服务响应"""
    product_id: str
    product_name: str
    product_code: Optional[str]
    enterprise_service_code: Optional[str]
    category_id: Optional[str]
    category_name: Optional[str]
    service_type_id: Optional[str]
    service_type: Optional[str]
    service_subtype: Optional[str]
    status: str
    is_active: bool
    vendor_product_id: Optional[str]
    is_primary: bool
    is_available: bool
    cost_price_cny: Optional[float]
    cost_price_idr: Optional[float]
    processing_days: Optional[int]
    sales_prices: List[Dict[str, Any]]
    price_history: List[Dict[str, Any]]


class SupplierServiceCategoryGroup(BaseModel):
    """供应商服务分类分组"""
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    items: List[SupplierServiceResponse]


class SupplierServiceListResponse(BaseModel):
    """供应商服务列表响应"""
    items: List[SupplierServiceResponse]
    groups: Optional[List[SupplierServiceCategoryGroup]] = None
    field_labels: Optional[Dict[str, Dict[str, str]]] = None
    total: int
    page: int
    size: int


class BatchAddProductsRequest(BaseModel):
    """批量添加产品请求"""
    product_ids: List[str] = Field(..., min_items=1, description="产品ID列表")
    default_cost_price_cny: Optional[float] = Field(None, description="默认成本价（人民币）")
    default_cost_price_idr: Optional[float] = Field(None, description="默认成本价（印尼盾）")
    is_available: bool = Field(True, description="是否可用")
    is_primary: bool = Field(False, description="是否主要供应商")


class BatchAddProductsResponse(BaseModel):
    """批量添加产品响应"""
    success_count: int
    failed_count: int
    success_product_ids: List[str]
    failed_product_ids: List[str]


class PriceUpdateItem(BaseModel):
    """价格更新项"""
    product_id: str = Field(..., description="产品ID")
    cost_price_cny: Optional[float] = Field(None, description="成本价（人民币）")
    cost_price_idr: Optional[float] = Field(None, description="成本价（印尼盾）")
    processing_days: Optional[int] = Field(None, description="处理天数")
    is_available: Optional[bool] = Field(None, description="是否可用")
    is_primary: Optional[bool] = Field(None, description="是否主要供应商")
    priority: Optional[int] = Field(None, description="优先级")


class BatchUpdatePricesRequest(BaseModel):
    """批量更新价格请求"""
    updates: List[PriceUpdateItem] = Field(..., min_items=1, description="更新列表")


class BatchUpdatePricesResponse(BaseModel):
    """批量更新价格响应"""
    success_count: int
    failed_count: int
    failed_product_ids: List[str]


class UpdatePriceRequest(BaseModel):
    """更新价格请求"""
    cost_price_cny: Optional[float] = Field(None, description="成本价（人民币）")
    cost_price_idr: Optional[float] = Field(None, description="成本价（印尼盾）")
    effective_from: Optional[Any] = Field(None, description="价格生效时间（如果为None则默认为当天+1天）")
