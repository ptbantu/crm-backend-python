"""
催款任务相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class CollectionTaskCreateRequest(BaseModel):
    """创建催款任务请求"""
    payment_stage_id: Optional[str] = Field(None, description="付款阶段ID")
    task_type: str = Field(default="manual", description="任务类型：auto, manual")
    due_date: Optional[date] = Field(None, description="到期日期")
    notes: Optional[str] = Field(None, description="备注")
    assigned_to_user_id: Optional[str] = Field(None, description="分配给的用户ID")


class CollectionTaskUpdateRequest(BaseModel):
    """更新催款任务请求"""
    status: Optional[str] = Field(None, description="状态：pending, in_progress, completed, cancelled")
    due_date: Optional[date] = None
    notes: Optional[str] = None
    assigned_to_user_id: Optional[str] = None


class CollectionTaskResponse(BaseModel):
    """催款任务响应"""
    id: str
    order_id: str
    payment_stage_id: Optional[str] = None
    task_type: str
    status: str
    due_date: Optional[date] = None
    reminder_count: int
    notes: Optional[str] = None
    assigned_to_user_id: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CollectionTaskListResponse(BaseModel):
    """催款任务列表响应"""
    items: List[CollectionTaskResponse]
    total: int
    page: int
    size: int

