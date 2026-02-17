"""
资料提交相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RequirementSubmissionCreateRequest(BaseModel):
    """创建提交记录请求"""
    product_id: str = Field(..., description="产品ID")
    rule_id: str = Field(..., description="资料规则ID")
    order_id: Optional[str] = Field(None, description="订单ID（可选）")
    service_record_id: Optional[str] = Field(None, description="服务记录ID（可选）")
    opportunity_id: Optional[str] = Field(None, description="商机ID（可选）")
    contract_id: Optional[str] = Field(None, description="合同ID（可选）")


class RequirementAttachmentDetailResponse(BaseModel):
    """附件详情响应"""
    id: str
    submission_record_id: str
    parent_attachment_id: Optional[str] = None
    file_name: str
    file_url: str
    file_size_kb: Optional[int] = None
    file_type: str
    mime_type: Optional[str] = None
    file_extension: Optional[str] = None
    is_zip: bool
    is_extracted: bool
    extracted_file_count: Optional[int] = None
    zip_extract_path: Optional[str] = None
    validation_status: str
    validation_message: Optional[str] = None
    validated_at: Optional[datetime] = None
    validated_by: Optional[str] = None
    uploaded_by: Optional[str] = None
    uploaded_at: datetime
    deleted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RequirementSubmissionRecordResponse(BaseModel):
    """提交记录响应"""
    id: str
    product_id: str
    rule_id: str
    order_id: Optional[str] = None
    service_record_id: Optional[str] = None
    opportunity_id: Optional[str] = None
    contract_id: Optional[str] = None
    status: str
    submitted_file_count: int
    required_file_count: int
    validation_passed: bool
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    attachments: List[RequirementAttachmentDetailResponse] = []
    
    class Config:
        from_attributes = True


class RequirementSubmissionListResponse(BaseModel):
    """提交记录列表响应"""
    items: List[RequirementSubmissionRecordResponse]
    total: int
    page: int
    size: int


class RequirementAttachmentValidateRequest(BaseModel):
    """附件校验请求"""
    validation_status: str = Field(..., description="校验状态：passed(通过), failed(失败)")
    validation_message: Optional[str] = Field(None, description="校验消息")


class ProductRequirementsStatusResponse(BaseModel):
    """产品依赖项状态响应"""
    product_id: str
    submissions: List[RequirementSubmissionRecordResponse]
    all_ready: bool
