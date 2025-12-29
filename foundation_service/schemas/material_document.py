"""
办理资料相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProductDocumentRuleRequest(BaseModel):
    """产品资料规则请求"""
    product_id: str = Field(..., description="产品ID")
    rule_code: str = Field(..., description="规则代码")
    document_name_zh: str = Field(..., description="资料名称（中文）")
    document_name_id: Optional[str] = Field(None, description="资料名称（印尼文）")
    document_type: str = Field(..., description="资料类型")
    is_required: bool = Field(default=True, description="是否必填")
    max_size_kb: Optional[int] = None
    allowed_extensions: Optional[str] = None
    validation_rules_json: Optional[dict] = None
    depends_on_rule_id: Optional[str] = Field(None, description="依赖的前置资料规则ID")
    sort_order: int = Field(default=0, description="显示排序")
    description: Optional[str] = None
    is_active: bool = Field(default=True, description="是否启用")


class ProductDocumentRuleResponse(BaseModel):
    """产品资料规则响应"""
    id: str
    product_id: str
    rule_code: str
    document_name_zh: str
    document_name_id: Optional[str] = None
    document_type: str
    is_required: bool
    max_size_kb: Optional[int] = None
    allowed_extensions: Optional[str] = None
    validation_rules_json: Optional[dict] = None
    depends_on_rule_id: Optional[str] = None
    sort_order: int
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class MaterialDocumentUploadRequest(BaseModel):
    """资料上传请求"""
    contract_id: str = Field(..., description="合同ID")
    opportunity_id: str = Field(..., description="商机ID")
    rule_id: str = Field(..., description="资料规则ID")
    quotation_item_id: Optional[str] = Field(None, description="关联报价单明细ID")
    document_name: str = Field(..., description="上传文件名")
    file_url: str = Field(..., description="OSS存储路径")
    file_size_kb: Optional[int] = None
    file_type: Optional[str] = None
    wechat_group_no: Optional[str] = Field(None, description="关联微信群编号")


class MaterialDocumentResponse(BaseModel):
    """资料响应"""
    id: str
    contract_id: str
    opportunity_id: str
    quotation_item_id: Optional[str] = None
    product_id: Optional[str] = None
    rule_id: str
    rule_code: Optional[str] = None
    document_name_zh: Optional[str] = None
    wechat_group_no: Optional[str] = None
    document_name: str
    file_url: str
    file_size_kb: Optional[int] = None
    file_type: Optional[str] = None
    validation_status: str
    validation_message: Optional[str] = None
    status: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    approval_notes: Optional[str] = None
    uploaded_by: Optional[str] = None
    uploaded_at: datetime


class MaterialDocumentApprovalRequest(BaseModel):
    """资料审批请求"""
    material_document_id: str = Field(..., description="资料记录ID")
    status: str = Field(..., description="审批状态：approved(通过), rejected(拒绝)")
    approval_notes: Optional[str] = Field(None, description="审批备注")


class MaterialDocumentListResponse(BaseModel):
    """资料列表响应"""
    records: List[MaterialDocumentResponse]
    total: int
