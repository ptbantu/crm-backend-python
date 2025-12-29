"""
执行订单相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class ExecutionOrderItemRequest(BaseModel):
    """执行订单明细请求"""
    quotation_item_id: Optional[str] = Field(None, description="关联报价单明细ID")
    product_id: Optional[str] = Field(None, description="产品ID")
    item_name: str = Field(..., description="服务名称")
    service_category: str = Field(..., description="服务类别")
    assigned_to: Optional[str] = Field(None, description="分配执行人ID")
    notes: Optional[str] = None


class ExecutionOrderItemResponse(BaseModel):
    """执行订单明细响应"""
    id: str
    execution_order_id: str
    quotation_item_id: Optional[str] = None
    product_id: Optional[str] = None
    item_name: str
    service_category: str
    status: str
    assigned_to: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ExecutionOrderCreateRequest(BaseModel):
    """创建执行订单请求"""
    opportunity_id: str = Field(..., description="商机ID")
    contract_id: Optional[str] = Field(None, description="关联合同ID")
    order_type: str = Field(..., description="订单类型")
    wechat_group_no: Optional[str] = Field(None, description="关联微信群编号")
    requires_company_registration: bool = Field(default=False, description="是否需要公司注册")
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    assigned_to: Optional[str] = Field(None, description="分配执行人ID")
    assigned_team: Optional[str] = Field(None, description="分配团队")
    items: List[ExecutionOrderItemRequest] = Field(default=[], description="执行订单明细列表")


class ExecutionOrderResponse(BaseModel):
    """执行订单响应"""
    id: str
    order_no: str
    opportunity_id: str
    contract_id: Optional[str] = None
    parent_order_id: Optional[str] = None
    order_type: str
    wechat_group_no: Optional[str] = None
    requires_company_registration: bool
    company_registration_order_id: Optional[str] = None
    status: str
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    assigned_to: Optional[str] = None
    assigned_team: Optional[str] = None
    assigned_at: Optional[datetime] = None
    items: List[ExecutionOrderItemResponse] = Field(default=[], description="执行订单明细列表")
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None


class ExecutionOrderListResponse(BaseModel):
    """执行订单列表响应"""
    records: List[ExecutionOrderResponse]
    total: int
    size: int
    current: int
    pages: int


class DependencyCheckRequest(BaseModel):
    """依赖检查请求"""
    execution_order_id: str = Field(..., description="执行订单ID")


class CompanyRegistrationInfoRequest(BaseModel):
    """公司注册信息请求"""
    execution_order_id: str = Field(..., description="公司注册执行订单ID")
    company_name: str = Field(..., description="公司名称")
    nib: Optional[str] = Field(None, description="NIB企业登记证号")
    npwp: Optional[str] = Field(None, description="税卡号")
    izin_lokasi: Optional[str] = Field(None, description="公司户籍")
    akta: Optional[str] = Field(None, description="公司章程")
    sk: Optional[str] = Field(None, description="司法部批文")
    registration_status: str = Field(default="in_progress", description="注册状态")
    notes: Optional[str] = None


class CompanyRegistrationInfoResponse(BaseModel):
    """公司注册信息响应"""
    id: str
    execution_order_id: str
    company_name: str
    nib: Optional[str] = None
    npwp: Optional[str] = None
    izin_lokasi: Optional[str] = None
    akta: Optional[str] = None
    sk: Optional[str] = None
    registration_status: str
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
