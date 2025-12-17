"""
价格和汇率相关模式
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ==================== 价格管理 Schema ====================

class ProductPriceHistoryRequest(BaseModel):
    """创建价格请求（列格式：一条记录包含所有价格类型和货币）"""
    product_id: str = Field(..., description="产品ID")
    organization_id: Optional[str] = Field(None, description="组织ID（NULL表示通用价格）")
    # 渠道价
    price_channel_idr: Optional[Decimal] = Field(None, ge=0, description="渠道价-IDR")
    price_channel_cny: Optional[Decimal] = Field(None, ge=0, description="渠道价-CNY")
    # 直客价
    price_direct_idr: Optional[Decimal] = Field(None, ge=0, description="直客价-IDR")
    price_direct_cny: Optional[Decimal] = Field(None, ge=0, description="直客价-CNY")
    # 列表价
    price_list_idr: Optional[Decimal] = Field(None, ge=0, description="列表价-IDR")
    price_list_cny: Optional[Decimal] = Field(None, ge=0, description="列表价-CNY")
    # 汇率
    exchange_rate: Optional[Decimal] = Field(None, gt=0, description="汇率")
    # 生效时间
    effective_from: Optional[datetime] = Field(None, description="生效时间（默认立即生效）")
    effective_to: Optional[datetime] = Field(None, description="失效时间（NULL表示当前有效）")
    # 其他字段
    source: Optional[str] = Field(None, description="价格来源：manual, import, contract")
    change_reason: Optional[str] = Field(None, description="变更原因")


class ProductPriceHistoryUpdateRequest(BaseModel):
    """更新价格请求（列格式：一条记录包含所有价格类型和货币）"""
    # 渠道价
    price_channel_idr: Optional[Decimal] = Field(None, ge=0, description="渠道价-IDR")
    price_channel_cny: Optional[Decimal] = Field(None, ge=0, description="渠道价-CNY")
    # 直客价
    price_direct_idr: Optional[Decimal] = Field(None, ge=0, description="直客价-IDR")
    price_direct_cny: Optional[Decimal] = Field(None, ge=0, description="直客价-CNY")
    # 列表价
    price_list_idr: Optional[Decimal] = Field(None, ge=0, description="列表价-IDR")
    price_list_cny: Optional[Decimal] = Field(None, ge=0, description="列表价-CNY")
    # 成本价
    price_cost_idr: Optional[Decimal] = Field(None, ge=0, description="成本价-IDR")
    price_cost_cny: Optional[Decimal] = Field(None, ge=0, description="成本价-CNY")
    # 汇率
    exchange_rate: Optional[Decimal] = Field(None, gt=0, description="汇率")
    # 生效时间
    effective_from: Optional[datetime] = Field(None, description="生效时间")
    effective_to: Optional[datetime] = Field(None, description="失效时间")
    # 其他字段
    change_reason: Optional[str] = Field(None, description="变更原因")


class ProductPriceHistoryResponse(BaseModel):
    """价格响应（列格式：一条记录包含所有价格类型和货币）"""
    id: str
    product_id: str
    organization_id: Optional[str]
    # 渠道价
    price_channel_idr: Optional[Decimal]
    price_channel_cny: Optional[Decimal]
    # 直客价
    price_direct_idr: Optional[Decimal]
    price_direct_cny: Optional[Decimal]
    # 列表价
    price_list_idr: Optional[Decimal]
    price_list_cny: Optional[Decimal]
    # 成本价
    price_cost_idr: Optional[Decimal]
    price_cost_cny: Optional[Decimal]
    # 汇率
    exchange_rate: Optional[Decimal]
    # 生效时间
    effective_from: datetime
    effective_to: Optional[datetime]
    # 其他字段
    source: Optional[str]
    change_reason: Optional[str]
    changed_by: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProductPriceListResponse(BaseModel):
    """价格列表响应"""
    items: List[ProductPriceHistoryResponse]
    total: int
    page: int
    size: int


class UpcomingPriceChangeResponse(BaseModel):
    """即将生效的价格变更响应（列格式：一条记录包含所有价格）"""
    id: str
    product_id: str
    product_name: Optional[str]
    product_code: Optional[str]
    # 价格字段（列格式）
    price_channel_idr: Optional[Decimal]
    price_channel_cny: Optional[Decimal]
    price_direct_idr: Optional[Decimal]
    price_direct_cny: Optional[Decimal]
    price_list_idr: Optional[Decimal]
    price_list_cny: Optional[Decimal]
    exchange_rate: Optional[Decimal]
    # 生效时间
    effective_from: datetime
    hours_until_effective: Optional[int]
    
    class Config:
        from_attributes = True


# ==================== 汇率管理 Schema ====================

class ExchangeRateHistoryRequest(BaseModel):
    """创建汇率请求"""
    from_currency: str = Field(..., description="源货币：IDR, CNY, USD, EUR")
    to_currency: str = Field(..., description="目标货币：IDR, CNY, USD, EUR")
    rate: Decimal = Field(..., gt=0, description="汇率")
    effective_from: Optional[datetime] = Field(None, description="生效时间（默认立即生效）")
    effective_to: Optional[datetime] = Field(None, description="失效时间（NULL表示当前有效）")
    source: Optional[str] = Field(None, description="汇率来源：manual, api, import")
    source_reference: Optional[str] = Field(None, description="来源参考（如API提供商）")
    change_reason: Optional[str] = Field(None, description="变更原因")


class ExchangeRateHistoryUpdateRequest(BaseModel):
    """更新汇率请求"""
    rate: Optional[Decimal] = Field(None, gt=0, description="汇率")
    effective_from: Optional[datetime] = Field(None, description="生效时间")
    effective_to: Optional[datetime] = Field(None, description="失效时间")
    change_reason: Optional[str] = Field(None, description="变更原因")


class ExchangeRateHistoryResponse(BaseModel):
    """汇率响应"""
    id: str
    from_currency: str
    to_currency: str
    rate: Decimal
    effective_from: datetime
    effective_to: Optional[datetime]
    source: Optional[str]
    source_reference: Optional[str]
    is_approved: bool
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    change_reason: Optional[str]
    changed_by: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ExchangeRateListResponse(BaseModel):
    """汇率列表响应"""
    items: List[ExchangeRateHistoryResponse]
    total: int
    page: int
    size: int


class CurrencyConvertRequest(BaseModel):
    """货币换算请求"""
    from_currency: str = Field(..., description="源货币")
    to_currency: str = Field(..., description="目标货币")
    amount: Decimal = Field(..., ge=0, description="金额")


class CurrencyConvertResponse(BaseModel):
    """货币换算响应"""
    from_currency: str
    to_currency: str
    from_amount: Decimal
    to_amount: Decimal
    rate: Decimal
    rate_effective_from: datetime


# ==================== 价格变更日志 Schema ====================

class PriceChangeLogResponse(BaseModel):
    """价格变更日志响应"""
    id: str
    product_id: str
    price_id: Optional[str]
    change_type: str
    price_type: str
    currency: str
    old_price: Optional[Decimal]
    new_price: Optional[Decimal]
    price_change_amount: Optional[Decimal]
    price_change_percentage: Optional[Decimal]
    old_effective_from: Optional[datetime]
    new_effective_from: Optional[datetime]
    old_effective_to: Optional[datetime]
    new_effective_to: Optional[datetime]
    change_reason: Optional[str]
    changed_by: Optional[str]
    changed_at: datetime
    affected_orders_count: Optional[int]
    impact_analysis: Optional[dict]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PriceChangeLogListResponse(BaseModel):
    """价格变更日志列表响应"""
    items: List[PriceChangeLogResponse]
    total: int
    page: int
    size: int


# ==================== 批量操作 Schema ====================

class BatchPriceUpdateRequest(BaseModel):
    """批量更新价格请求"""
    prices: List[ProductPriceHistoryRequest] = Field(..., description="价格列表")


class BatchPriceUpdateResponse(BaseModel):
    """批量更新价格响应"""
    success_count: int
    failure_count: int
    errors: List[dict] = Field(default_factory=list)
