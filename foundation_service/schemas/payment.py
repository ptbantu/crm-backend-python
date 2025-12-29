"""
收款相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


class PaymentVoucherRequest(BaseModel):
    """收款凭证请求"""
    file_name: str = Field(..., description="凭证文件名")
    file_url: str = Field(..., description="OSS存储路径")
    file_size_kb: Optional[int] = None
    is_primary: bool = Field(default=False, description="是否主要凭证")


class PaymentVoucherResponse(BaseModel):
    """收款凭证响应"""
    id: str
    payment_id: str
    file_name: str
    file_url: str
    file_size_kb: Optional[int] = None
    is_primary: bool
    uploaded_by: Optional[str] = None
    uploaded_at: datetime


class PaymentCreateRequest(BaseModel):
    """创建收款请求"""
    opportunity_id: str = Field(..., description="商机ID")
    contract_id: Optional[str] = Field(None, description="关联合同ID")
    execution_order_id: Optional[str] = Field(None, description="关联执行订单ID")
    entity_id: str = Field(..., description="签约主体ID")
    amount: Decimal = Field(..., description="本次收款金额（含税）")
    currency: str = Field(..., description="币种")
    payment_method: Optional[str] = Field(None, description="付款方式")
    payment_mode: str = Field(..., description="回款模式")
    received_at: Optional[date] = Field(None, description="到账日期")
    is_final_payment: bool = Field(default=False, description="是否尾款")
    vouchers: List[PaymentVoucherRequest] = Field(default=[], description="收款凭证列表")


class PaymentUpdateRequest(BaseModel):
    """更新收款请求"""
    payment_method: Optional[str] = None
    received_at: Optional[date] = None
    review_notes: Optional[str] = None


class PaymentResponse(BaseModel):
    """收款响应"""
    id: str
    payment_no: str
    opportunity_id: str
    contract_id: Optional[str] = None
    execution_order_id: Optional[str] = None
    entity_id: str
    entity_name: Optional[str] = None
    amount: Decimal
    tax_amount: Decimal
    currency: str
    payment_method: Optional[str] = None
    payment_mode: str
    status: str
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    received_at: Optional[date] = None
    is_final_payment: bool
    delivery_verified: bool
    vouchers: List[PaymentVoucherResponse] = Field(default=[], description="收款凭证列表")
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None


class PaymentListResponse(BaseModel):
    """收款列表响应"""
    records: List[PaymentResponse]
    total: int
    size: int
    current: int
    pages: int


class PaymentReviewRequest(BaseModel):
    """收款核对请求"""
    payment_id: str = Field(..., description="收款记录ID")
    status: str = Field(..., description="核对状态：confirmed(已确认), rejected(拒绝)")
    review_notes: Optional[str] = Field(None, description="核对备注")


class CollectionTodoRequest(BaseModel):
    """收款待办事项请求"""
    opportunity_id: str = Field(..., description="商机ID")
    payment_id: Optional[str] = Field(None, description="关联收款ID")
    todo_type: str = Field(..., description="待办类型")
    title: str = Field(..., description="待办标题")
    description: Optional[str] = None
    assigned_to: Optional[str] = Field(None, description="分配人ID")
    due_date: Optional[datetime] = Field(None, description="截止时间")


class CollectionTodoResponse(BaseModel):
    """收款待办事项响应"""
    id: str
    opportunity_id: str
    payment_id: Optional[str] = None
    todo_type: str
    title: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str
    completed_at: Optional[datetime] = None
    completed_by: Optional[str] = None
    notification_sent: bool
    created_at: datetime


class CollectionTodoListResponse(BaseModel):
    """收款待办事项列表响应"""
    records: List[CollectionTodoResponse]
    total: int
