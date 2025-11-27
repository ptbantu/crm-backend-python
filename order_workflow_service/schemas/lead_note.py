"""
线索备注相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LeadNoteCreateRequest(BaseModel):
    """创建备注请求"""
    note_type: str = Field(..., description="备注类型：comment, reminder, task")
    content: str = Field(..., description="备注内容")
    is_important: bool = Field(default=False, description="是否重要")


class LeadNoteResponse(BaseModel):
    """备注响应"""
    id: str
    lead_id: str
    note_type: str
    content: str
    is_important: bool
    created_by: Optional[str] = None
    created_by_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

