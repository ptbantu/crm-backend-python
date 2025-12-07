"""
工作流相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class WorkflowDefinitionCreateRequest(BaseModel):
    """创建工作流定义请求"""
    name_zh: str = Field(..., max_length=255, description="工作流名称（中文）")
    name_id: str = Field(..., max_length=255, description="工作流名称（印尼语）")
    code: str = Field(..., max_length=100, description="工作流代码（唯一）")
    description_zh: Optional[str] = Field(None, description="描述（中文）")
    description_id: Optional[str] = Field(None, description="描述（印尼语）")
    workflow_type: Optional[str] = Field(None, description="工作流类型：order_approval, delivery_review, payment_approval")
    definition_json: Optional[Dict[str, Any]] = Field(None, description="工作流定义（JSON 格式）")
    version: int = Field(default=1, description="版本号")
    is_active: bool = Field(default=True, description="是否激活")


class WorkflowDefinitionUpdateRequest(BaseModel):
    """更新工作流定义请求"""
    name_zh: Optional[str] = None
    name_id: Optional[str] = None
    description_zh: Optional[str] = None
    description_id: Optional[str] = None
    workflow_type: Optional[str] = None
    definition_json: Optional[Dict[str, Any]] = None
    version: Optional[int] = None
    is_active: Optional[bool] = None


class WorkflowDefinitionResponse(BaseModel):
    """工作流定义响应（根据 lang 参数返回对应语言）"""
    id: str
    name: str  # 根据 lang 返回 name_zh 或 name_id
    code: str
    description: Optional[str] = None  # 根据 lang 返回 description_zh 或 description_id
    workflow_type: Optional[str] = None
    definition_json: Optional[Dict[str, Any]] = None
    version: int
    is_active: bool
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class WorkflowInstanceCreateRequest(BaseModel):
    """创建工作流实例请求"""
    workflow_definition_id: str = Field(..., description="工作流定义ID")
    business_type: str = Field(..., description="业务类型：order, service_record")
    business_id: str = Field(..., description="业务对象ID（订单ID或服务记录ID）")
    variables: Optional[Dict[str, Any]] = Field(None, description="流程变量（JSON 格式）")


class WorkflowInstanceResponse(BaseModel):
    """工作流实例响应"""
    id: str
    workflow_definition_id: Optional[str] = None
    workflow_definition_name: Optional[str] = None  # 冗余字段
    business_type: Optional[str] = None
    business_id: Optional[str] = None
    current_stage: Optional[str] = None
    status: str
    started_by: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class WorkflowTaskResponse(BaseModel):
    """工作流任务响应（根据 lang 参数返回对应语言）"""
    id: str
    workflow_instance_id: str
    task_name: Optional[str] = None  # 根据 lang 返回 task_name_zh 或 task_name_id
    task_code: Optional[str] = None
    task_type: Optional[str] = None
    assigned_to_user_id: Optional[str] = None
    assigned_to_role_id: Optional[str] = None
    status: str
    due_date: Optional[str] = None
    completed_at: Optional[str] = None
    completed_by: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class WorkflowTransitionRequest(BaseModel):
    """工作流流转请求"""
    workflow_instance_id: str = Field(..., description="工作流实例ID")
    to_stage: str = Field(..., description="目标阶段")
    transition_condition: Optional[str] = Field(None, description="流转条件")
    notes: Optional[str] = Field(None, description="备注")


class WorkflowTransitionResponse(BaseModel):
    """工作流流转记录响应"""
    id: str
    workflow_instance_id: str
    from_stage: Optional[str] = None
    to_stage: Optional[str] = None
    transition_condition: Optional[str] = None
    triggered_by: Optional[str] = None
    triggered_at: str
    notes: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True

