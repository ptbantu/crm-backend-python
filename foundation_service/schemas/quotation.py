"""
报价单相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


class QuotationItemRequest(BaseModel):
    """报价单明细请求"""
    opportunity_item_id: Optional[str] = Field(None, description="关联商机明细ID")
    product_id: Optional[str] = Field(None, description="产品ID")
    item_name: str = Field(..., description="服务名称")
    quantity: Decimal = Field(..., description="数量")
    unit_price_primary: Decimal = Field(..., description="主货币单价")
    unit_cost: Decimal = Field(default=Decimal("0"), description="成本单价")
    service_category: str = Field(..., description="服务类别：one_time(一次性), long_term(长周期)")
    sort_order: int = Field(default=0, description="显示排序")
    description: Optional[str] = Field(None, description="描述")


class QuotationItemResponse(BaseModel):
    """报价单明细响应"""
    id: str
    quotation_id: str
    opportunity_item_id: Optional[str] = None
    product_id: Optional[str] = None
    item_name: str
    quantity: Decimal
    unit_price_primary: Decimal
    unit_cost: Decimal
    is_below_cost: bool
    total_price_primary: Decimal
    service_category: str
    sort_order: int
    description: Optional[str] = None


class QuotationDocumentRequest(BaseModel):
    """报价单资料请求"""
    document_type: str = Field(..., description="资料类型")
    document_name: str = Field(..., description="资料文件名")
    file_url: str = Field(..., description="存储路径（OSS链接）")
    related_item_id: Optional[str] = Field(None, description="关联报价单明细行ID")


class QuotationDocumentResponse(BaseModel):
    """报价单资料响应"""
    id: str
    quotation_id: str
    wechat_group_no: Optional[str] = None
    document_type: str
    document_name: str
    file_url: str
    related_item_id: Optional[str] = None
    uploaded_by: Optional[str] = None
    uploaded_at: datetime


class QuotationCreateRequest(BaseModel):
    """创建报价单请求"""
    opportunity_id: str = Field(..., description="商机ID")
    currency_primary: str = Field(default="IDR", description="主货币：IDR 或 CNY")
    exchange_rate: Optional[Decimal] = Field(None, description="汇率")
    payment_terms: str = Field(..., description="付款方式")
    discount_rate: Decimal = Field(default=Decimal("0"), description="折扣比例（%）")
    valid_until: Optional[date] = Field(None, description="报价有效期至")
    template_id: Optional[str] = Field(None, description="使用的PDF模板ID")
    wechat_group_no: Optional[str] = Field(None, description="关联微信群编号")
    items: List[QuotationItemRequest] = Field(default=[], description="报价单明细列表")


class QuotationUpdateRequest(BaseModel):
    """更新报价单请求"""
    currency_primary: Optional[str] = None
    exchange_rate: Optional[Decimal] = None
    payment_terms: Optional[str] = None
    discount_rate: Optional[Decimal] = None
    valid_until: Optional[date] = None
    status: Optional[str] = None


class QuotationResponse(BaseModel):
    """报价单响应"""
    id: str
    opportunity_id: str
    quotation_no: str
    version: int
    currency_primary: str
    exchange_rate: Optional[Decimal] = None
    payment_terms: str
    discount_rate: Decimal
    total_amount_primary: Decimal
    total_amount_secondary: Optional[Decimal] = None
    valid_until: Optional[date] = None
    status: str
    wechat_group_no: Optional[str] = None
    template_id: Optional[str] = None
    template_code_at_generation: Optional[str] = None
    pdf_generated_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    items: List[QuotationItemResponse] = Field(default=[], description="报价单明细列表")
    documents: List[QuotationDocumentResponse] = Field(default=[], description="资料列表")
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None


class QuotationListResponse(BaseModel):
    """报价单列表响应"""
    records: List[QuotationResponse]
    total: int
    size: int
    current: int
    pages: int


class QuotationTemplateRequest(BaseModel):
    """报价单模板请求"""
    template_code: str = Field(..., description="模板代码")
    template_name: str = Field(..., description="模板名称")
    description: Optional[str] = None
    primary_currency: str = Field(..., description="主货币")
    language: str = Field(..., description="模板语言")
    file_url: str = Field(..., description="模板文件存储路径")
    file_type: str = Field(..., description="模板文件类型")
    header_logo_url: Optional[str] = None
    footer_text: Optional[str] = None
    bank_account_info_json: Optional[dict] = None
    tax_info_json: Optional[dict] = None
    is_default: bool = Field(default=False, description="是否为默认模板")
    is_active: bool = Field(default=True, description="是否启用")


class QuotationTemplateResponse(BaseModel):
    """报价单模板响应"""
    id: str
    template_code: str
    template_name: str
    description: Optional[str] = None
    primary_currency: str
    language: str
    file_url: str
    file_type: str
    header_logo_url: Optional[str] = None
    footer_text: Optional[str] = None
    bank_account_info_json: Optional[dict] = None
    tax_info_json: Optional[dict] = None
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class QuotationAcceptRequest(BaseModel):
    """接受报价单请求"""
    quotation_id: str = Field(..., description="报价单ID")
    notes: Optional[str] = Field(None, description="备注")


class QuotationRejectRequest(BaseModel):
    """拒绝报价单请求"""
    quotation_id: str = Field(..., description="报价单ID")
    reason: Optional[str] = Field(None, description="拒绝原因")
