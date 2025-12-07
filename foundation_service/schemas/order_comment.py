"""
订单评论相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class OrderCommentCreateRequest(BaseModel):
    """创建订单评论请求"""
    order_id: str = Field(..., description="订单ID")
    order_stage_id: Optional[str] = Field(None, description="关联的订单阶段ID（可选）")
    
    # 评论类型
    comment_type: str = Field(default="general", description="评论类型：general, internal, customer, system")
    
    # 评论内容（双语）
    content_zh: Optional[str] = Field(None, description="评论内容（中文）")
    content_id: Optional[str] = Field(None, description="评论内容（印尼语）")
    
    # 评论属性
    is_internal: bool = Field(default=False, description="是否内部评论（客户不可见）")
    is_pinned: bool = Field(default=False, description="是否置顶")
    
    # 回复关联
    replied_to_comment_id: Optional[str] = Field(None, description="回复的评论ID（支持回复）")


class OrderCommentUpdateRequest(BaseModel):
    """更新订单评论请求"""
    content_zh: Optional[str] = None
    content_id: Optional[str] = None
    is_internal: Optional[bool] = None
    is_pinned: Optional[bool] = None


class OrderCommentResponse(BaseModel):
    """订单评论响应（根据 lang 参数返回对应语言）"""
    id: str
    order_id: str
    order_stage_id: Optional[str] = None
    comment_type: str
    content: Optional[str] = None  # 根据 lang 返回 content_zh 或 content_id
    is_internal: bool
    is_pinned: bool
    replied_to_comment_id: Optional[str] = None
    
    # 创建人信息
    created_by: Optional[str] = None
    created_by_name: Optional[str] = None
    
    # 审计字段
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class OrderCommentListResponse(BaseModel):
    """订单评论列表响应"""
    comments: list[OrderCommentResponse] = Field(default_factory=list)
    total: int = 0

