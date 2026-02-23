"""
文档模板相关的 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from common.models.doc_template import TemplateTypeEnum


class DocTemplateBase(BaseModel):
    """文档模板基础模型"""
    template_code: str = Field(..., description="模板代码")
    template_name: str = Field(..., description="模板名称")
    template_type: TemplateTypeEnum = Field(..., description="模板类型")
    entity_id: Optional[str] = Field(None, description="关联签约主体ID")
    language: str = Field(default="zh", description="模板语言")
    description: Optional[str] = Field(None, description="模板描述")


class DocTemplateCreateRequest(DocTemplateBase):
    """创建文档模板请求"""
    file_oss_key: str = Field(..., description="OSS存储路径")
    file_name: str = Field(..., description="原始文件名")
    file_size_kb: Optional[int] = Field(None, description="文件大小（KB）")
    placeholders: Optional[List[str]] = Field(None, description="占位符列表")


class DocTemplateUpdateRequest(BaseModel):
    """更新文档模板请求"""
    template_name: Optional[str] = Field(None, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    is_active: Optional[bool] = Field(None, description="是否启用")


class DocTemplateResponse(DocTemplateBase):
    """文档模板响应"""
    id: str
    file_oss_key: str
    file_name: str
    file_size_kb: Optional[int]
    placeholders: Optional[List[str]]
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]

    class Config:
        from_attributes = True


class DocTemplateListResponse(BaseModel):
    """文档模板列表响应"""
    items: List[DocTemplateResponse]
    total: int
    page: int
    size: int
