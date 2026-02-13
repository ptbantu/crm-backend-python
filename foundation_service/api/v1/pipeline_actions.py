"""
流水线动作 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from common.schemas.response import Result
from common.exceptions import BusinessException
from foundation_service.dependencies import get_db
from foundation_service.services.pipeline_action_service import PipelineActionService
from foundation_service.schemas.pipeline_action import (
    ActionLogResponse,
    StageActionsResponse,
    ExecuteActionRequest,
    ApproveActionRequest,
    SkipActionRequest
)

router = APIRouter()


@router.get(
    "/{opportunity_id}/pipeline/stages/{stage_id}/actions",
    summary="获取阶段动作列表",
    description="获取指定阶段的所有动作及其执行状态"
)
async def get_stage_actions(
    opportunity_id: str,
    stage_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取阶段动作列表"""
    try:
        service = PipelineActionService(db)
        result = await service.get_stage_actions(opportunity_id, stage_id)
        return Result.success(data=result)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取阶段动作失败: {str(e)}")


@router.post(
    "/{opportunity_id}/pipeline/actions/{action_id}/execute",
    summary="执行动作",
    description="执行文件上传或表单填写类型的动作"
)
async def execute_action(
    opportunity_id: str,
    action_id: str,
    request: ExecuteActionRequest,
    db: AsyncSession = Depends(get_db),
    # current_user_id: str = Depends(get_current_user_id)  # TODO: 添加认证
):
    """执行动作"""
    try:
        # TODO: 从认证中获取用户ID
        current_user_id = "system"

        service = PipelineActionService(db)
        result = await service.execute_action(action_id, request, current_user_id)
        return Result.success(message="动作执行成功", data=result)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行动作失败: {str(e)}")


@router.post(
    "/{opportunity_id}/pipeline/actions/{action_id}/approve",
    summary="审批动作",
    description="审批类型的动作，支持通过或拒绝"
)
async def approve_action(
    opportunity_id: str,
    action_id: str,
    request: ApproveActionRequest,
    db: AsyncSession = Depends(get_db),
    # current_user_id: str = Depends(get_current_user_id)  # TODO: 添加认证
):
    """审批动作"""
    try:
        # TODO: 从认证中获取用户ID
        current_user_id = "system"

        service = PipelineActionService(db)
        result = await service.approve_action(action_id, request, current_user_id)
        return Result.success(message="审批成功", data=result)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"审批动作失败: {str(e)}")


@router.post(
    "/{opportunity_id}/pipeline/actions/{action_id}/skip",
    summary="跳过动作",
    description="跳过非必需的动作"
)
async def skip_action(
    opportunity_id: str,
    action_id: str,
    request: SkipActionRequest,
    db: AsyncSession = Depends(get_db),
    # current_user_id: str = Depends(get_current_user_id)  # TODO: 添加认证
):
    """跳过动作"""
    try:
        # TODO: 从认证中获取用户ID
        current_user_id = "system"

        service = PipelineActionService(db)
        result = await service.skip_action(action_id, request, current_user_id)
        return Result.success(message="动作已跳过", data=result)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"跳过动作失败: {str(e)}")


@router.get(
    "/{opportunity_id}/pipeline/actions/{action_id}",
    summary="获取动作详情",
    description="获取指定动作的详细信息"
)
async def get_action_detail(
    opportunity_id: str,
    action_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取动作详情"""
    try:
        service = PipelineActionService(db)
        result = await service.get_action_detail(action_id)
        return Result.success(data=result)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取动作详情失败: {str(e)}")


@router.get(
    "/{opportunity_id}/pipeline/actions",
    summary="获取商机所有动作",
    description="获取指定商机的所有动作执行记录"
)
async def get_opportunity_actions(
    opportunity_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取商机所有动作"""
    try:
        service = PipelineActionService(db)
        result = await service.get_opportunity_actions(opportunity_id)
        return Result.success(data=result)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取商机动作失败: {str(e)}")


@router.post(
    "/{opportunity_id}/pipeline/actions/{action_id}/trigger-sub-pipeline",
    summary="触发子流水线",
    description="触发子流水线类型的动作"
)
async def trigger_sub_pipeline(
    opportunity_id: str,
    action_id: str,
    db: AsyncSession = Depends(get_db),
    # current_user_id: str = Depends(get_current_user_id)  # TODO: 添加认证
):
    """触发子流水线"""
    try:
        # TODO: 从认证中获取用户ID
        current_user_id = "system"

        service = PipelineActionService(db)
        result = await service.trigger_sub_pipeline(action_id, current_user_id)
        return Result.success(message="子流水线已触发", data=result)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"触发子流水线失败: {str(e)}")
