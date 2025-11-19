"""
订单相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from decimal import Decimal

from order_workflow_service.schemas.order_item import OrderItemResponse


class OrderCreateRequest(BaseModel):
    """创建订单请求"""
    title: str = Field(..., max_length=255, description="订单标题")
    customer_id: str = Field(..., description="客户ID")
    service_record_id: Optional[str] = Field(None, description="关联的服务记录ID（可选）")
    sales_user_id: str = Field(..., description="销售用户ID")
    
    # EVOA 字段
    entry_city: Optional[str] = Field(None, max_length=255, description="入境城市（来自 EVOA）")
    passport_id: Optional[str] = Field(None, max_length=100, description="护照ID（来自 EVOA）")
    processor: Optional[str] = Field(None, max_length=255, description="处理器（来自 EVOA）")
    
    # 订单项列表（一个订单可以包含多个订单项）
    order_items: List[dict] = Field(default_factory=list, description="订单项列表")
    
    # 订单级信息
    currency_code: str = Field(default="CNY", max_length=10, description="货币代码")
    discount_amount: Decimal = Field(default=0, ge=0, description="订单级折扣金额")
    exchange_rate: Optional[Decimal] = Field(None, gt=0, description="汇率")
    
    # 时间信息
    expected_start_date: Optional[date] = Field(None, description="预期开始日期")
    expected_completion_date: Optional[date] = Field(None, description="预期完成日期")
    
    # 备注
    customer_notes: Optional[str] = Field(None, description="客户备注")
    internal_notes: Optional[str] = Field(None, description="内部备注")
    requirements: Optional[str] = Field(None, description="需求和要求")


class OrderUpdateRequest(BaseModel):
    """更新订单请求"""
    title: Optional[str] = None
    service_record_id: Optional[str] = None
    entry_city: Optional[str] = None
    passport_id: Optional[str] = None
    processor: Optional[str] = None
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    exchange_rate: Optional[Decimal] = Field(None, gt=0)
    expected_start_date: Optional[date] = None
    expected_completion_date: Optional[date] = None
    customer_notes: Optional[str] = None
    internal_notes: Optional[str] = None
    requirements: Optional[str] = None
    status_code: Optional[str] = None


class OrderResponse(BaseModel):
    """订单响应（包含订单项列表）"""
    id: str
    order_number: str
    title: str
    customer_id: str
    customer_name: Optional[str] = None
    service_record_id: Optional[str] = None
    workflow_instance_id: Optional[str] = None
    sales_user_id: str
    sales_username: Optional[str] = None
    
    # EVOA 字段
    entry_city: Optional[str] = None
    passport_id: Optional[str] = None
    processor: Optional[str] = None
    
    # 金额信息（从订单项汇总）
    total_amount: Optional[Decimal] = None
    discount_amount: Decimal
    final_amount: Optional[Decimal] = None
    currency_code: str
    exchange_rate: Optional[Decimal] = None
    
    # 订单项列表
    order_items: List[OrderItemResponse] = Field(default_factory=list)
    
    # 时间信息
    expected_start_date: Optional[date] = None
    expected_completion_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_completion_date: Optional[date] = None
    
    # 状态
    status_code: Optional[str] = None
    status_name: Optional[str] = None
    
    # 备注
    customer_notes: Optional[str] = None
    internal_notes: Optional[str] = None
    requirements: Optional[str] = None
    
    # 审计字段
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """订单列表响应"""
    orders: List[OrderResponse] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20

