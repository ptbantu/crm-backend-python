"""
商机相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal


# 商机阶段枚举
class OpportunityStage:
    INITIAL_CONTACT = "initial_contact"
    NEEDS_ANALYSIS = "needs_analysis"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


# 商机状态枚举
class OpportunityStatus:
    ACTIVE = "active"
    WON = "won"
    LOST = "lost"
    CANCELLED = "cancelled"


# 商机产品请求
class OpportunityProductRequest(BaseModel):
    """商机产品请求"""
    product_id: str = Field(..., description="产品ID")
    quantity: int = Field(default=1, ge=1, description="数量")
    unit_price: Optional[Decimal] = Field(None, description="单价")
    execution_order: Optional[int] = Field(None, ge=1, description="执行顺序（可选，如果为空则自动计算）")


# 商机付款阶段请求
class OpportunityPaymentStageRequest(BaseModel):
    """商机付款阶段请求"""
    stage_number: int = Field(..., ge=1, description="阶段序号（1, 2, 3...）")
    stage_name: str = Field(..., max_length=255, description="阶段名称（如：首付款、中期款、尾款）")
    amount: Decimal = Field(..., ge=0, description="应付金额")
    due_date: Optional[date] = Field(None, description="到期日期")
    payment_trigger: str = Field(default="manual", description="付款触发条件（manual, milestone, date, completion）")


# 创建商机请求
class CreateOpportunityRequest(BaseModel):
    """创建商机请求"""
    customer_id: str = Field(..., description="客户ID")
    lead_id: Optional[str] = Field(None, description="来源线索ID（可选）")
    name: str = Field(..., max_length=255, description="商机名称")
    amount: Optional[Decimal] = Field(None, description="商机金额")
    probability: Optional[int] = Field(None, ge=0, le=100, description="成交概率（0-100）")
    stage: str = Field(default="initial_contact", description="商机阶段")
    status: str = Field(default="active", description="状态")
    owner_user_id: Optional[str] = Field(None, description="负责人ID")
    expected_close_date: Optional[date] = Field(None, description="预期成交日期")
    description: Optional[str] = Field(None, description="描述")
    products: Optional[List[OpportunityProductRequest]] = Field(default=[], description="产品列表")
    payment_stages: Optional[List[OpportunityPaymentStageRequest]] = Field(default=[], description="付款阶段列表")
    auto_calculate_order: bool = Field(default=True, description="是否自动计算执行顺序")


# 更新商机请求
class UpdateOpportunityRequest(BaseModel):
    """更新商机请求"""
    name: Optional[str] = Field(None, max_length=255, description="商机名称")
    amount: Optional[Decimal] = Field(None, description="商机金额")
    probability: Optional[int] = Field(None, ge=0, le=100, description="成交概率（0-100）")
    stage: Optional[str] = Field(None, description="商机阶段")
    status: Optional[str] = Field(None, description="状态")
    owner_user_id: Optional[str] = Field(None, description="负责人ID")
    expected_close_date: Optional[date] = Field(None, description="预期成交日期")
    actual_close_date: Optional[date] = Field(None, description="实际成交日期")
    description: Optional[str] = Field(None, description="描述")


# 商机产品响应
class OpportunityProductResponse(BaseModel):
    """商机产品响应"""
    id: str
    opportunity_id: str
    product_id: str
    product_name: Optional[str] = None
    product_code: Optional[str] = None
    quantity: int
    unit_price: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    execution_order: int
    status: str
    start_date: Optional[date] = None
    expected_completion_date: Optional[date] = None
    actual_completion_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# 商机付款阶段响应
class OpportunityPaymentStageResponse(BaseModel):
    """商机付款阶段响应"""
    id: str
    opportunity_id: str
    stage_number: int
    stage_name: str
    amount: Decimal
    due_date: Optional[date] = None
    payment_trigger: str
    status: str
    created_at: datetime
    updated_at: datetime


# 商机响应
class OpportunityResponse(BaseModel):
    """商机响应"""
    id: str
    customer_id: str
    customer_name: Optional[str] = None
    lead_id: Optional[str] = None
    lead_name: Optional[str] = None
    name: str
    amount: Optional[Decimal] = None
    probability: Optional[int] = None
    stage: str
    status: str
    owner_user_id: Optional[str] = None
    owner_username: Optional[str] = None
    organization_id: str
    expected_close_date: Optional[date] = None
    actual_close_date: Optional[date] = None
    description: Optional[str] = None
    # 新增字段
    current_stage_id: Optional[str] = None
    current_stage_code: Optional[str] = None
    current_stage_name_zh: Optional[str] = None
    workflow_status: str = Field(default="active", description="工作流整体状态")
    collection_status: str = Field(default="not_started", description="整体收款状态")
    total_received_amount: Decimal = Field(default=Decimal("0"), description="已收总金额")
    service_type: str = Field(default="one_time", description="服务类型")
    is_split_required: bool = Field(default=False, description="是否需要订单拆分")
    split_order_required: bool = Field(default=False, description="是否需要拆分独立订单")
    has_staged_services: bool = Field(default=False, description="是否包含分阶段服务")
    tax_service_cycle_months: Optional[int] = None
    tax_service_start_date: Optional[date] = None
    primary_quotation_id: Optional[str] = None
    primary_contract_id: Optional[str] = None
    developed_by: Optional[str] = None
    last_followup_at: Optional[datetime] = None
    is_stale: bool = Field(default=False, description="是否长久未跟进")
    products: List[OpportunityProductResponse] = Field(default=[], description="产品列表")
    payment_stages: List[OpportunityPaymentStageResponse] = Field(default=[], description="付款阶段列表")
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# 商机列表响应
class OpportunityListResponse(BaseModel):
    """商机列表响应"""
    records: List[OpportunityResponse]
    total: int
    size: int
    current: int
    pages: int


# 线索转化商机请求
class LeadConvertToOpportunityRequest(BaseModel):
    """线索转化商机请求"""
    customer_id: Optional[str] = Field(None, description="客户ID（如果已有客户，可选）")
    name: str = Field(..., max_length=255, description="商机名称")
    stage: str = Field(default="initial_contact", description="商机阶段")
    owner_user_id: Optional[str] = Field(None, description="负责人ID")
    description: Optional[str] = Field(None, description="描述")
    products: List[OpportunityProductRequest] = Field(default=[], description="产品列表（可选）")
    payment_stages: Optional[List[OpportunityPaymentStageRequest]] = Field(default=[], description="付款阶段列表")


# 商机转化订单请求
class OpportunityConvertToOrderRequest(BaseModel):
    """商机转化订单请求"""
    order_number: Optional[str] = Field(None, description="订单编号（可选，系统自动生成）")
    title: Optional[str] = Field(None, description="订单标题（可选，默认使用商机名称）")
    expected_start_date: Optional[date] = Field(None, description="预期开始日期")
    expected_completion_date: Optional[date] = Field(None, description="预期完成日期")
    customer_notes: Optional[str] = Field(None, description="客户备注")
    internal_notes: Optional[str] = Field(None, description="内部备注")
    requirements: Optional[str] = Field(None, description="需求说明")


# 产品依赖关系验证响应
class ProductDependencyValidationResponse(BaseModel):
    """产品依赖关系验证响应"""
    is_valid: bool = Field(..., description="是否有效")
    missing_dependencies: List[str] = Field(default=[], description="缺失的必需依赖（格式：['产品A需要产品B', ...]）")
    warnings: List[str] = Field(default=[], description="警告信息（推荐依赖等）")
    suggested_order: List[Dict[str, Any]] = Field(default=[], description="建议的执行顺序")


# 商机分配请求
class OpportunityAssignRequest(BaseModel):
    """商机分配请求"""
    owner_user_id: str = Field(..., description="负责人ID")


# 商机阶段更新请求
class OpportunityStageUpdateRequest(BaseModel):
    """商机阶段更新请求"""
    stage: str = Field(..., description="商机阶段")


# 商机工作流状态更新请求
class OpportunityWorkflowStatusUpdateRequest(BaseModel):
    """商机工作流状态更新请求"""
    workflow_status: str = Field(..., description="工作流状态：active, paused, completed, cancelled")


# 商机服务类型更新请求
class OpportunityServiceTypeUpdateRequest(BaseModel):
    """商机服务类型更新请求"""
    service_type: str = Field(..., description="服务类型：one_time, long_term, mixed")
    is_split_required: Optional[bool] = Field(None, description="是否需要订单拆分")
    tax_service_cycle_months: Optional[int] = Field(None, description="财税服务周期（月）")
    tax_service_start_date: Optional[date] = Field(None, description="财税服务开始日期")


# 商机转化请求
class OpportunityConvertRequest(BaseModel):
    """商机转化请求（已废弃，使用 OpportunityConvertToOrderRequest）"""
    pass

