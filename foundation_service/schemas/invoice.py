"""
发票相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class InvoiceFileRequest(BaseModel):
    """发票文件请求"""
    file_name: str = Field(..., description="文件名")
    file_url: str = Field(..., description="OSS存储路径")
    file_size_kb: Optional[int] = None
    is_primary: bool = Field(default=True, description="是否主要文件")


class InvoiceFileResponse(BaseModel):
    """发票文件响应"""
    id: str
    invoice_id: str
    file_name: str
    file_url: str
    file_size_kb: Optional[int] = None
    is_primary: bool
    uploaded_at: datetime
    uploaded_by: Optional[str] = None


class InvoiceCreateRequest(BaseModel):
    """创建发票请求"""
    contract_id: str = Field(..., description="关联合同ID")
    opportunity_id: str = Field(..., description="商机ID")
    entity_id: str = Field(..., description="签约主体ID")
    customer_name: str = Field(..., description="客户发票抬头")
    customer_bank_account: Optional[str] = Field(None, description="客户银行账户")
    invoice_amount: Decimal = Field(..., description="发票金额（含税）")
    invoice_type: Optional[str] = Field(None, description="发票类型")


class InvoiceUpdateRequest(BaseModel):
    """更新发票请求"""
    customer_name: Optional[str] = None
    customer_bank_account: Optional[str] = None
    invoice_amount: Optional[Decimal] = None
    invoice_type: Optional[str] = None
    status: Optional[str] = None
    issued_at: Optional[datetime] = None
    uploaded_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None


class InvoiceResponse(BaseModel):
    """发票响应"""
    id: str
    contract_id: str
    opportunity_id: str
    invoice_no: str
    entity_id: str
    entity_name: Optional[str] = None
    contract_amount: Decimal
    customer_name: str
    customer_bank_account: Optional[str] = None
    invoice_amount: Decimal
    tax_amount: Decimal
    currency: str
    invoice_type: Optional[str] = None
    status: str
    issued_at: Optional[datetime] = None
    uploaded_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    files: List[InvoiceFileResponse] = Field(default=[], description="发票文件列表")
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None


class InvoiceListResponse(BaseModel):
    """发票列表响应"""
    records: List[InvoiceResponse]
    total: int
    size: int
    current: int
    pages: int
