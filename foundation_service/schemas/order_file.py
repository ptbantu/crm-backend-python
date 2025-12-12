"""
订单文件相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class OrderFileCreateRequest(BaseModel):
    """创建订单文件请求"""
    order_id: str = Field(..., description="订单ID")
    order_item_id: Optional[str] = Field(None, description="关联的订单项ID（可选）")
    order_stage_id: Optional[str] = Field(None, description="关联的订单阶段ID（可选）")
    
    # 文件分类
    file_category: Optional[str] = Field(None, description="文件分类：passport, visa, document, other")
    
    # 文件名称（双语）
    file_name_zh: Optional[str] = Field(None, max_length=255, description="文件名称（中文）")
    file_name_id: Optional[str] = Field(None, max_length=255, description="文件名称（印尼语）")
    
    # 文件类型
    file_type: Optional[str] = Field(None, description="文件类型：image, pdf, doc, excel, other")
    
    # 文件存储
    file_path: Optional[str] = Field(None, description="文件存储路径（相对路径）")
    file_url: Optional[str] = Field(None, description="文件访问URL（完整路径）")
    file_size: Optional[int] = Field(None, ge=0, description="文件大小（字节）")
    mime_type: Optional[str] = Field(None, max_length=100, description="MIME类型")
    
    # 文件描述（双语）
    description_zh: Optional[str] = Field(None, description="文件描述（中文）")
    description_id: Optional[str] = Field(None, description="文件描述（印尼语）")
    
    # 文件属性
    is_required: bool = Field(default=False, description="是否必需文件")
    is_verified: bool = Field(default=False, description="是否已验证")


class OrderFileUpdateRequest(BaseModel):
    """更新订单文件请求"""
    file_name_zh: Optional[str] = None
    file_name_id: Optional[str] = None
    file_category: Optional[str] = None
    file_type: Optional[str] = None
    description_zh: Optional[str] = None
    description_id: Optional[str] = None
    is_required: Optional[bool] = None
    is_verified: Optional[bool] = None


class OrderFileUploadRequest(BaseModel):
    """文件上传请求"""
    order_id: str = Field(..., description="订单ID")
    order_item_id: Optional[str] = Field(None, description="关联的订单项ID（可选）")
    order_stage_id: Optional[str] = Field(None, description="关联的订单阶段ID（可选）")
    file_category: Optional[str] = Field(None, description="文件分类：passport, visa, document, other")
    file_name_zh: Optional[str] = Field(None, description="文件名称（中文）")
    file_name_id: Optional[str] = Field(None, description="文件名称（印尼语）")
    description_zh: Optional[str] = Field(None, description="文件描述（中文）")
    description_id: Optional[str] = Field(None, description="文件描述（印尼语）")
    is_required: bool = Field(default=False, description="是否必需文件")


class OrderFileResponse(BaseModel):
    """订单文件响应（根据 lang 参数返回对应语言）"""
    id: str
    order_id: str
    order_item_id: Optional[str] = None
    order_stage_id: Optional[str] = None
    file_category: Optional[str] = None
    file_name: Optional[str] = None  # 根据 lang 返回 file_name_zh 或 file_name_id
    file_type: Optional[str] = None
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    description: Optional[str] = None  # 根据 lang 返回 description_zh 或 description_id
    is_required: bool
    is_verified: bool
    verified_by: Optional[str] = None
    verified_at: Optional[str] = None
    uploaded_by: Optional[str] = None
    
    # 审计字段
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class OrderFileListResponse(BaseModel):
    """订单文件列表响应"""
    files: list[OrderFileResponse] = Field(default_factory=list)
    total: int = 0

