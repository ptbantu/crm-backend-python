"""
财税主体相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class ContractEntityCreateRequest(BaseModel):
    """创建财税主体请求"""
    entity_code: str = Field(..., max_length=50, description="主体代码（唯一，如：BJ_BANTU, HB_BANTU, PT_PUBLIC）")
    entity_name: str = Field(..., max_length=255, description="主体名称（如：北京班兔科技有限公司）")
    short_name: str = Field(..., max_length=100, description="简称（如：北京班兔）")
    legal_representative: Optional[str] = Field(None, max_length=100, description="法定代表人")
    
    # 税务信息
    tax_rate: Decimal = Field(default=0.0000, ge=0, le=1, description="税点（例如：0.0100 = 1%）")
    tax_id: Optional[str] = Field(None, max_length=100, description="税号")
    
    # 银行信息
    bank_name: Optional[str] = Field(None, max_length=200, description="开户行")
    bank_account_no: Optional[str] = Field(None, max_length=100, description="收款账户")
    bank_account_name: Optional[str] = Field(None, max_length=200, description="账户名称")
    swift_code: Optional[str] = Field(None, max_length=50, description="SWIFT代码")
    
    # 货币与联系信息
    currency: str = Field(default="CNY", max_length=10, description="主要收款币种：CNY 或 IDR")
    address: Optional[str] = Field(None, description="公司地址")
    contact_phone: Optional[str] = Field(None, max_length=50, description="联系电话")
    
    # 状态
    is_active: bool = Field(default=True, description="是否启用")


class ContractEntityUpdateRequest(BaseModel):
    """更新财税主体请求"""
    entity_code: Optional[str] = Field(None, max_length=50, description="主体代码")
    entity_name: Optional[str] = Field(None, max_length=255, description="主体名称")
    short_name: Optional[str] = Field(None, max_length=100, description="简称")
    legal_representative: Optional[str] = Field(None, max_length=100, description="法定代表人")
    
    # 税务信息
    tax_rate: Optional[Decimal] = Field(None, ge=0, le=1, description="税点")
    tax_id: Optional[str] = Field(None, max_length=100, description="税号")
    
    # 银行信息
    bank_name: Optional[str] = Field(None, max_length=200, description="开户行")
    bank_account_no: Optional[str] = Field(None, max_length=100, description="收款账户")
    bank_account_name: Optional[str] = Field(None, max_length=200, description="账户名称")
    swift_code: Optional[str] = Field(None, max_length=50, description="SWIFT代码")
    
    # 货币与联系信息
    currency: Optional[str] = Field(None, max_length=10, description="主要收款币种")
    address: Optional[str] = Field(None, description="公司地址")
    contact_phone: Optional[str] = Field(None, max_length=50, description="联系电话")
    
    # 状态
    is_active: Optional[bool] = Field(None, description="是否启用")


class ContractEntityResponse(BaseModel):
    """财税主体响应"""
    id: str
    entity_code: str
    entity_name: str
    short_name: str
    legal_representative: Optional[str] = None
    
    # 税务信息
    tax_rate: Decimal
    tax_id: Optional[str] = None
    
    # 银行信息
    bank_name: Optional[str] = None
    bank_account_no: Optional[str] = None
    bank_account_name: Optional[str] = None
    swift_code: Optional[str] = None
    
    # 货币与联系信息
    currency: str
    address: Optional[str] = None
    contact_phone: Optional[str] = None
    
    # 状态
    is_active: bool
    
    # 审计字段
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    class Config:
        from_attributes = True


class ContractEntityListResponse(BaseModel):
    """财税主体列表响应"""
    records: List[ContractEntityResponse]
    total: int
    size: int
    current: int
    pages: int
