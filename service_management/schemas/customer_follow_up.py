"""
客户跟进记录相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CustomerFollowUpCreateRequest(BaseModel):
    """创建跟进记录请求"""
    follow_up_type: str = Field(..., description="跟进类型：call, meeting, email, note, visit, wechat, whatsapp")
    content: Optional[str] = Field(None, description="跟进内容")
    follow_up_date: datetime = Field(..., description="跟进日期")
    status_before: Optional[str] = Field(None, description="跟进前状态（可选）")
    status_after: Optional[str] = Field(None, description="跟进后状态（可选）")
    next_follow_up_at: Optional[datetime] = Field(None, description="下次跟进时间（可选）")


class CustomerFollowUpResponse(BaseModel):
    """跟进记录响应"""
    id: str
    customer_id: str
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

