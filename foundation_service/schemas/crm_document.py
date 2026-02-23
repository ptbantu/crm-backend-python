"""
CRM文档相关的 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from common.models.crm_document import DocumentTypeEnum, DocumentStatusEnum
from common.models.doc_invoice_ext import InvoiceTypeEnum


# ============ 合同扩展 ============
class DocContractExtBase(BaseModel):
    """合同文档扩展基础模型"""
    contract_number: Optional[str] = Field(None, description="合同编号")
    party_a_name: str = Field(..., description="甲方名称")
    party_a_contact: Optional[str] = Field(None, description="甲方联系人")
    party_a_address: Optional[str] = Field(None, description="甲方地址")
    party_b_name: str = Field(..., description="乙方名称")
    total_amount: Decimal = Field(..., description="合同总金额")
    currency: str = Field(default="CNY", description="币种")
    tax_rate: Optional[Decimal] = Field(None, description="税率")
    effective_from: Optional[date] = Field(None, description="生效日期")
    effective_to: Optional[date] = Field(None, description="到期日期")
    payment_terms: Optional[str] = Field(None, description="付款条款")


class DocContractExtResponse(DocContractExtBase):
    """合同文档扩展响应"""
    id: str
    document_id: str
    contract_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ 发票扩展 ============
class DocInvoiceExtBase(BaseModel):
    """发票文档扩展基础模型"""
    invoice_number: Optional[str] = Field(None, description="发票编号")
    invoice_type: InvoiceTypeEnum = Field(..., description="发票类型")
    total_amount: Decimal = Field(..., description="发票金额")
    tax_amount: Optional[Decimal] = Field(None, description="税额")
    amount_before_tax: Optional[Decimal] = Field(None, description="税前金额")
    currency: str = Field(default="CNY", description="币种")
    tax_rate: Optional[Decimal] = Field(None, description="税率")
    tax_id: Optional[str] = Field(None, description="纳税人识别号")
    invoice_date: Optional[date] = Field(None, description="开票日期")


class DocInvoiceExtResponse(DocInvoiceExtBase):
    """发票文档扩展响应"""
    id: str
    document_id: str
    invoice_id: Optional[str]
    contract_document_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ CRM文档 ============
class CrmDocumentBase(BaseModel):
    """CRM文档基础模型"""
    document_type: DocumentTypeEnum = Field(..., description="文档类型")
    title: str = Field(..., description="文档标题")
    description: Optional[str] = Field(None, description="文档描述")
    opportunity_id: Optional[str] = Field(None, description="关联商机ID")
    contract_id: Optional[str] = Field(None, description="关联合同ID")
    invoice_id: Optional[str] = Field(None, description="关联发票ID")
    template_id: Optional[str] = Field(None, description="使用的模板ID")
    entity_id: str = Field(..., description="签约主体ID")
    group_id: Optional[str] = Field(None, description="文档组ID")


class DocumentGenerateRequest(BaseModel):
    """生成文档请求"""
    template_id: str = Field(..., description="模板ID")
    opportunity_id: str = Field(..., description="商机ID")
    entity_id: str = Field(..., description="签约主体ID")
    document_type: DocumentTypeEnum = Field(..., description="文档类型")
    title: str = Field(..., description="文档标题")
    group_id: Optional[str] = Field(None, description="文档组ID（用于关联）")

    # 合同扩展数据（当document_type为contract时必填）
    contract_ext: Optional[DocContractExtBase] = Field(None, description="合同扩展数据")

    # 发票扩展数据（当document_type为invoice时必填）
    invoice_ext: Optional[DocInvoiceExtBase] = Field(None, description="发票扩展数据")

    # 自定义数据绑定（用于替换模板占位符）
    custom_data: Optional[dict] = Field(None, description="自定义数据")


class DocumentSubmitRequest(BaseModel):
    """提交审批请求"""
    pass


class DocumentApproveRequest(BaseModel):
    """审批通过请求"""
    pass


class DocumentRejectRequest(BaseModel):
    """拒绝请求"""
    rejection_reason: str = Field(..., description="拒绝原因")


class DocumentSealRequest(BaseModel):
    """盖章请求"""
    pass


class DocumentFinalizeRequest(BaseModel):
    """最终化请求（转换为PDF/A）"""
    pass


class CrmDocumentResponse(CrmDocumentBase):
    """CRM文档响应"""
    id: str
    document_no: str
    draft_oss_key: Optional[str]
    final_oss_key: Optional[str]
    file_size_kb: Optional[int]
    file_hash: Optional[str]
    status: DocumentStatusEnum

    # 审批信息
    submitted_at: Optional[datetime]
    submitted_by: Optional[str]
    approved_at: Optional[datetime]
    approved_by: Optional[str]
    rejected_at: Optional[datetime]
    rejected_by: Optional[str]
    rejection_reason: Optional[str]

    # 盖章信息
    sealed_at: Optional[datetime]
    sealed_by: Optional[str]

    # 最终化
    finalized_at: Optional[datetime]

    # 审计字段
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    # 扩展信息
    contract_ext: Optional[DocContractExtResponse] = None
    invoice_ext: Optional[DocInvoiceExtResponse] = None

    class Config:
        from_attributes = True


class CrmDocumentListResponse(BaseModel):
    """CRM文档列表响应"""
    items: List[CrmDocumentResponse]
    total: int
    page: int
    size: int
