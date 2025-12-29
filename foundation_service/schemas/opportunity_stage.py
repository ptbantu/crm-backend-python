"""
商机阶段相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class StageTemplateResponse(BaseModel):
    """阶段模板响应"""
    id: str
    code: str
    name_zh: str
    name_id: str
    description_zh: Optional[str] = None
    description_id: Optional[str] = None
    stage_order: int
    requires_approval: bool
    approval_roles_json: Optional[List[str]] = None
    conditions_json: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class StageHistoryResponse(BaseModel):
    """阶段历史响应"""
    id: str
    opportunity_id: str
    stage_id: str
    stage_code: Optional[str] = None
    stage_name_zh: Optional[str] = None
    entered_at: datetime
    exited_at: Optional[datetime] = None
    duration_days: Optional[int] = None
    conditions_met_json: Optional[Dict[str, Any]] = None
    requires_approval: bool
    approval_status: Optional[str] = None
    approved_by: Optional[str] = None
    approval_at: Optional[datetime] = None
    approval_notes: Optional[str] = None
    created_at: datetime


class StageTransitionRequest(BaseModel):
    """阶段流转请求"""
    opportunity_id: str = Field(..., description="商机ID")
    target_stage_id: Optional[str] = Field(None, description="目标阶段ID（如果为空则推进到下一阶段）")
    conditions_met_json: Optional[Dict[str, Any]] = Field(None, description="满足的条件JSON")
    notes: Optional[str] = Field(None, description="备注")


class StageApprovalRequest(BaseModel):
    """阶段审批请求"""
    stage_history_id: str = Field(..., description="阶段历史ID")
    approval_status: str = Field(..., description="审批状态：approved(通过), rejected(拒绝)")
    approval_notes: Optional[str] = Field(None, description="审批备注")


class StageListResponse(BaseModel):
    """阶段列表响应"""
    records: List[StageTemplateResponse]
    total: int


class StageHistoryListResponse(BaseModel):
    """阶段历史列表响应"""
    records: List[StageHistoryResponse]
    total: int
