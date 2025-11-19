"""
订单项相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from decimal import Decimal


class OrderItemCreateRequest(BaseModel):
    """创建订单项请求"""
    order_id: str = Field(..., description="订单ID")
    item_number: int = Field(..., ge=1, description="订单项序号")
    
    # 产品/服务关联
    product_id: Optional[str] = Field(None, description="产品/服务ID")
    product_name_zh: Optional[str] = Field(None, max_length=255, description="产品名称（中文）")
    product_name_id: Optional[str] = Field(None, max_length=255, description="产品名称（印尼语）")
    product_code: Optional[str] = Field(None, max_length=100, description="产品代码")
    
    # 服务类型关联
    service_type_id: Optional[str] = Field(None, description="服务类型ID")
    service_type_name_zh: Optional[str] = Field(None, max_length=255, description="服务类型名称（中文）")
    service_type_name_id: Optional[str] = Field(None, max_length=255, description="服务类型名称（印尼语）")
    
    # 数量信息
    quantity: int = Field(default=1, ge=1, description="数量")
    unit: Optional[str] = Field(None, max_length=50, description="单位")
    
    # 价格信息
    unit_price: Optional[Decimal] = Field(None, ge=0, description="单价")
    discount_amount: Decimal = Field(default=0, ge=0, description="折扣金额")
    currency_code: str = Field(default="CNY", max_length=10, description="货币代码")
    
    # 描述信息（双语）
    description_zh: Optional[str] = Field(None, description="订单项描述（中文）")
    description_id: Optional[str] = Field(None, description="订单项描述（印尼语）")
    requirements: Optional[str] = Field(None, description="需求和要求")
    
    # 时间信息
    expected_start_date: Optional[date] = Field(None, description="预期开始日期")
    expected_completion_date: Optional[date] = Field(None, description="预期完成日期")
    
    # 状态
    status: str = Field(default="pending", description="订单项状态：pending, in_progress, completed, cancelled")


class OrderItemUpdateRequest(BaseModel):
    """更新订单项请求"""
    product_id: Optional[str] = None
    product_name_zh: Optional[str] = None
    product_name_id: Optional[str] = None
    product_code: Optional[str] = None
    service_type_id: Optional[str] = None
    service_type_name_zh: Optional[str] = None
    service_type_name_id: Optional[str] = None
    quantity: Optional[int] = Field(None, ge=1)
    unit: Optional[str] = None
    unit_price: Optional[Decimal] = Field(None, ge=0)
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    currency_code: Optional[str] = None
    description_zh: Optional[str] = None
    description_id: Optional[str] = None
    requirements: Optional[str] = None
    expected_start_date: Optional[date] = None
    expected_completion_date: Optional[date] = None
    status: Optional[str] = None


class OrderItemResponse(BaseModel):
    """订单项响应（根据 lang 参数返回对应语言）"""
    id: str
    order_id: str
    item_number: int
    
    # 产品/服务信息
    product_id: Optional[str] = None
    product_name: Optional[str] = None  # 根据 lang 返回 product_name_zh 或 product_name_id
    product_code: Optional[str] = None
    
    # 服务类型信息
    service_type_id: Optional[str] = None
    service_type_name: Optional[str] = None  # 根据 lang 返回 service_type_name_zh 或 service_type_name_id
    
    # 数量信息
    quantity: int
    unit: Optional[str] = None
    
    # 价格信息
    unit_price: Optional[Decimal] = None
    discount_amount: Decimal
    item_amount: Optional[Decimal] = None
    currency_code: str
    
    # 描述信息
    description: Optional[str] = None  # 根据 lang 返回 description_zh 或 description_id
    requirements: Optional[str] = None
    
    # 时间信息
    expected_start_date: Optional[date] = None
    expected_completion_date: Optional[date] = None
    
    # 状态
    status: str
    
    # 审计字段
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class OrderItemListResponse(BaseModel):
    """订单项列表响应"""
    items: list[OrderItemResponse] = Field(default_factory=list)
    total: int = 0

