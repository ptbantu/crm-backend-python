"""
流水线动作 Schema 定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ActionType(str, Enum):
    """动作类型"""
    FORM = "FORM"
    FILE = "FILE"
    APPROVAL = "APPROVAL"
    SUB_PIPELINE = "SUB_PIPELINE"
    API_CALL = "API_CALL"


class ActionStatus(str, Enum):
    """动作状态"""
    TODO = "TODO"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"


class ActionConfigResponse(BaseModel):
    """动作配置响应"""
    id: str
    stage_id: str
    action_code: str
    name: str
    action_type: ActionType
    is_required: bool
    order: int
    description: Optional[str] = None
    validation_rules: Optional[Dict[str, Any]] = None
    trigger_config: Optional[Dict[str, Any]] = None
    form_schema: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActionLogResponse(BaseModel):
    """动作执行日志响应"""
    id: str
    opportunity_id: str
    pipeline_log_id: str
    action_config_id: str
    action_code: str
    action_name: str
    action_type: str
    status: ActionStatus
    operator_id: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    captured_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExecuteActionRequest(BaseModel):
    """执行动作请求"""
    captured_data: Optional[Dict[str, Any]] = Field(None, description="捕获的数据")
    notes: Optional[str] = Field(None, description="备注")


class ApproveActionRequest(BaseModel):
    """审批动作请求"""
    approved: bool = Field(..., description="是否通过")
    approval_notes: Optional[str] = Field(None, description="审批意见")
    captured_data: Optional[Dict[str, Any]] = Field(None, description="额外数据")


class SkipActionRequest(BaseModel):
    """跳过动作请求"""
    reason: str = Field(..., description="跳过原因")


class StageActionsResponse(BaseModel):
    """阶段动作列表响应"""
    stage_id: str
    stage_name: str
    actions: List[ActionLogResponse]
    total_actions: int
    completed_actions: int
    required_actions: int
    can_complete_stage: bool

    class Config:
        from_attributes = True
