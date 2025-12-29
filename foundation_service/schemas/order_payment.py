"""
订单回款相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


class OrderPaymentCreateRequest(BaseModel):
    """创建订单回款请求"""
    order_id: str = Field(..., description="订单ID")
    order_item_id: Optional[str] = Field(None, description="订单项ID")
    payment_amount: Decimal = Field(..., description="本次回款金额")
    payment_date: date = Field(..., description="回款日期")
    payment_type: str = Field(default="full", description="回款类型：monthly(长周期月付), full(全部), partial(部分)")
    is_excluded_from_full: bool = Field(default=False, description="是否排除在全部回款计算中")
    notes: Optional[str] = Field(None, description="回款备注")


class OrderPaymentResponse(BaseModel):
    """订单回款响应"""
    id: str
    order_id: str
    order_item_id: Optional[str] = None
    payment_amount: Decimal
    payment_date: date
    payment_type: str
    is_excluded_from_full: bool
    status: str
    confirmed_by: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PaymentConfirmationRequest(BaseModel):
    """回款确认请求"""
    payment_id: str = Field(..., description="回款记录ID")
    notes: Optional[str] = Field(None, description="确认备注")


class OrderPaymentListResponse(BaseModel):
    """订单回款列表响应"""
    records: List[OrderPaymentResponse]
    total: int
