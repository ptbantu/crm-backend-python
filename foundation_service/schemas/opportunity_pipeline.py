"""
商机流水线 Schema 定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class StageType(str, Enum):
    """阶段类型"""
    TASK = "TASK"
    APPROVAL = "APPROVAL"
    DECISION = "DECISION"
    NOTIFICATION = "NOTIFICATION"


class StageStatus(str, Enum):
    """阶段状态"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    REJECTED = "REJECTED"


class PipelineStageResponse(BaseModel):
    """流水线阶段响应"""
    id: str
    pipeline_id: str
    name: str
    stage_type: StageType
    order: int
    parent_id: Optional[str] = None
    parallel_group: Optional[str] = None
    approver_role: Optional[str] = None
    description: Optional[str] = None
    auto_proceed: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PipelineLogResponse(BaseModel):
    """流水线日志响应"""
    id: str
    opportunity_id: str
    pipeline_id: str
    stage_id: str
    stage_name: str
    stage_type: StageType
    status: StageStatus
    parallel_group: Optional[str] = None
    entered_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    assigned_to: Optional[str] = None
    approver_id: Optional[str] = None
    approved_at: Optional[datetime] = None
    approval_notes: Optional[str] = None
    notes: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StartPipelineRequest(BaseModel):
    """启动流水线请求"""
    pipeline_id: str = Field(..., description="流水线ID")
    initial_notes: Optional[str] = Field(None, description="初始备注")


class CompleteStageRequest(BaseModel):
    """完成阶段请求"""
    notes: Optional[str] = Field(None, description="完成备注")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="扩展数据")


class ApproveStageRequest(BaseModel):
    """审批阶段请求"""
    approved: bool = Field(..., description="是否通过")
    approval_notes: Optional[str] = Field(None, description="审批意见")


class AssignStageRequest(BaseModel):
    """分配阶段请求"""
    assigned_to: str = Field(..., description="分配给用户ID")
    notes: Optional[str] = Field(None, description="分配备注")


class PipelineProgressResponse(BaseModel):
    """流水线进度响应"""
    opportunity_id: str
    pipeline_id: str
    pipeline_name: str
    current_stages: List[PipelineLogResponse]
    completed_stages: List[PipelineLogResponse]
    pending_stages: List[PipelineStageResponse]
    total_stages: int
    completed_count: int
    progress_percentage: float
    is_completed: bool
    has_parallel_stages: bool

    class Config:
        from_attributes = True


class PipelineHistoryResponse(BaseModel):
    """流水线历史响应"""
    logs: List[PipelineLogResponse]
    total: int

    class Config:
        from_attributes = True
