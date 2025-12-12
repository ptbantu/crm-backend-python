"""
线索跟进记录相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LeadFollowUpCreateRequest(BaseModel):
    """创建跟进记录请求"""
    follow_up_type: str = Field(..., description="跟进类型：call, meeting, email, note")
    content: Optional[str] = Field(None, description="跟进内容")
    follow_up_date: datetime = Field(..., description="跟进日期")
    status_after: Optional[str] = Field(None, description="跟进后线索状态（可选，如果提供则更新线索状态）")


class LeadFollowUpResponse(BaseModel):
    """跟进记录响应"""
    id: str
    lead_id: str
    follow_up_type: str
    content: Optional[str] = None
    follow_up_date: datetime
    status_before: Optional[str] = None
    status_after: Optional[str] = None
    created_by: Optional[str] = None
    created_by_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

