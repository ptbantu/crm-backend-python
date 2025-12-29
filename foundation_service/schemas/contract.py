"""
合同相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


class ContractEntityRequest(BaseModel):
    """签约主体请求"""
    entity_code: str = Field(..., description="主体代码")
    entity_name: str = Field(..., description="主体名称")
    short_name: str = Field(..., description="简称")
    legal_representative: Optional[str] = None
    tax_rate: Decimal = Field(default=Decimal("0"), description="税点")
    tax_id: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account_no: Optional[str] = None
    bank_account_name: Optional[str] = None
    currency: str = Field(default="CNY", description="主要收款币种")
    address: Optional[str] = None
    contact_phone: Optional[str] = None
    is_active: bool = Field(default=True, description="是否启用")


class ContractEntityResponse(BaseModel):
    """签约主体响应"""
    id: str
    entity_code: str
    entity_name: str
    short_name: str
    legal_representative: Optional[str] = None
    tax_rate: Decimal
    tax_id: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account_no: Optional[str] = None
    bank_account_name: Optional[str] = None
    currency: str
    address: Optional[str] = None
    contact_phone: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class ContractCreateRequest(BaseModel):
    """创建合同请求"""
    opportunity_id: str = Field(..., description="商机ID")
    quotation_id: Optional[str] = Field(None, description="关联报价单ID")
    entity_id: str = Field(..., description="乙方签约主体ID")
    party_a_name: str = Field(..., description="甲方名称")
    party_a_contact: Optional[str] = None
    party_a_phone: Optional[str] = None
    party_a_email: Optional[str] = None
    party_a_address: Optional[str] = None
    template_id: Optional[str] = Field(None, description="使用的合同模板ID")
    wechat_group_no: Optional[str] = Field(None, description="关联微信群编号")


class ContractUpdateRequest(BaseModel):
    """更新合同请求"""
    party_a_name: Optional[str] = None
    party_a_contact: Optional[str] = None
    party_a_phone: Optional[str] = None
    party_a_email: Optional[str] = None
    party_a_address: Optional[str] = None
    status: Optional[str] = None
    signed_at: Optional[datetime] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None


class ContractResponse(BaseModel):
    """合同响应"""
    id: str
    opportunity_id: str
    quotation_id: Optional[str] = None
    contract_no: str
    entity_id: str
    entity_name: Optional[str] = None
    party_a_name: str
    party_a_contact: Optional[str] = None
    party_a_phone: Optional[str] = None
    party_a_email: Optional[str] = None
    party_a_address: Optional[str] = None
    total_amount_with_tax: Decimal
    tax_amount: Decimal
    tax_rate: Decimal
    status: str
    signed_at: Optional[datetime] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    template_id: Optional[str] = None
    wechat_group_no: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None


class ContractListResponse(BaseModel):
    """合同列表响应"""
    records: List[ContractResponse]
    total: int
    size: int
    current: int
    pages: int


class ContractTemplateRequest(BaseModel):
    """合同模板请求"""
    template_code: str = Field(..., description="模板代码")
    template_name: str = Field(..., description="模板名称")
    entity_id: str = Field(..., description="关联签约主体ID")
    language: str = Field(..., description="模板语言")
    file_url: str = Field(..., description="模板文件路径")
    file_type: str = Field(..., description="模板类型")
    header_logo_url: Optional[str] = None
    footer_text: Optional[str] = None
    is_default_for_entity: bool = Field(default=False, description="是否为该主体默认模板")
    is_active: bool = Field(default=True, description="是否启用")


class ContractTemplateResponse(BaseModel):
    """合同模板响应"""
    id: str
    template_code: str
    template_name: str
    entity_id: str
    entity_name: Optional[str] = None
    language: str
    file_url: str
    file_type: str
    header_logo_url: Optional[str] = None
    footer_text: Optional[str] = None
    is_default_for_entity: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class ContractDocumentRequest(BaseModel):
    """合同文件请求"""
    document_type: str = Field(..., description="文件类型")
    file_name: str = Field(..., description="文件名")
    file_url: str = Field(..., description="OSS存储路径")
    file_size_kb: Optional[int] = None
    generated_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None


class ContractDocumentResponse(BaseModel):
    """合同文件响应"""
    id: str
    contract_id: str
    document_type: str
    file_name: str
    file_url: str
    file_size_kb: Optional[int] = None
    version: int
    generated_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    created_at: datetime
    created_by: Optional[str] = None


class ContractSignRequest(BaseModel):
    """签署合同请求"""
    contract_id: str = Field(..., description="合同ID")
    signed_at: Optional[datetime] = Field(None, description="签署时间")
    effective_from: Optional[date] = Field(None, description="合同生效日期")
    effective_to: Optional[date] = Field(None, description="合同到期日期")
