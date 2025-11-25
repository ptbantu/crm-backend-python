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


class LeadFollowUpResponse(BaseModel):
    """跟进记录响应"""
    id: str
    lead_id: str
    follow_up_type: str
    content: Optional[str] = None
    follow_up_date: datetime
    created_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

