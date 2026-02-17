"""
商机流水线管理 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from common.utils.logger import get_logger
from foundation_service.schemas.opportunity_pipeline import (
    StartPipelineRequest,
    CompleteStageRequest,
    ApproveStageRequest,
    AssignStageRequest,
    PipelineProgressResponse,
    PipelineHistoryResponse,
)
from foundation_service.services.opportunity_pipeline_service import OpportunityPipelineService
from foundation_service.dependencies import (
    get_db,
    get_current_user_id,
    get_current_organization_id,
)
from foundation_service.utils import log_audit_operation

logger = get_logger(__name__)
router = APIRouter()


@router.post("/{opportunity_id}/pipeline/start", response_model=Result[PipelineProgressResponse])
async def start_pipeline(
    opportunity_id: str,
    request_body: StartPipelineRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db)
):
    """启动商机流水线"""
    logger.info(f"API: 启动商机流水线: opportunity_id={opportunity_id}, pipeline_id={request_body.pipeline_id}")
    try:
        current_user_id = get_current_user_id(request_obj)
        if not current_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无法获取用户信息"
            )

        service = OpportunityPipelineService(db)
        result = await service.start_pipeline(
            opportunity_id=opportunity_id,
            request=request_body,
            current_user_id=current_user_id
        )

        # 记录审计日志
        await log_audit_operation(
            db=db,
            request=request_obj,
            operation_type="CREATE",
            entity_type="opportunity_pipeline",
            entity_id=opportunity_id,
            status="SUCCESS"
        )

        logger.info(f"API: 商机流水线启动成功: opportunity_id={opportunity_id}")
        return Result.success(data=result, message="流水线启动成功")
    except Exception as e:
        logger.error(f"API: 启动商机流水线失败: {str(e)}", exc_info=True)
        raise


@router.post("/{opportunity_id}/pipeline/stages/{stage_id}/complete", response_model=Result[PipelineProgressResponse])
async def complete_stage(
    opportunity_id: str,
    stage_id: str,
    request_body: CompleteStageRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db)
):
    """完成流水线阶段"""
    logger.info(f"API: 完成流水线阶段: opportunity_id={opportunity_id}, stage_id={stage_id}")
    try:
        current_user_id = get_current_user_id(request_obj)
        if not current_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无法获取用户信息"
            )

        service = OpportunityPipelineService(db)
        result = await service.complete_stage(
            opportunity_id=opportunity_id,
            stage_id=stage_id,
            request=request_body,
            current_user_id=current_user_id
        )

        # 记录审计日志
        await log_audit_operation(
            db=db,
            request=request_obj,
            operation_type="UPDATE",
            entity_type="opportunity_pipeline_stage",
            entity_id=f"{opportunity_id}:{stage_id}",
            status="SUCCESS"
        )

        logger.info(f"API: 流水线阶段完成成功: opportunity_id={opportunity_id}, stage_id={stage_id}")
        return Result.success(data=result, message="阶段完成成功")
    except Exception as e:
        logger.error(f"API: 完成流水线阶段失败: {str(e)}", exc_info=True)
        raise


@router.post("/{opportunity_id}/pipeline/stages/{stage_id}/approve", response_model=Result[PipelineProgressResponse])
async def approve_stage(
    opportunity_id: str,
    stage_id: str,
    request_body: ApproveStageRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db)
):
    """审批流水线阶段"""
    logger.info(f"API: 审批流水线阶段: opportunity_id={opportunity_id}, stage_id={stage_id}, approved={request_body.approved}")
    try:
        current_user_id = get_current_user_id(request_obj)
        if not current_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无法获取用户信息"
            )

        service = OpportunityPipelineService(db)
        result = await service.approve_stage(
            opportunity_id=opportunity_id,
            stage_id=stage_id,
            request=request_body,
            current_user_id=current_user_id
        )

        # 记录审计日志
        await log_audit_operation(
            db=db,
            request=request_obj,
            operation_type="UPDATE",
            entity_type="opportunity_pipeline_approval",
            entity_id=f"{opportunity_id}:{stage_id}",
            status="SUCCESS"
        )

        logger.info(f"API: 流水线阶段审批成功: opportunity_id={opportunity_id}, stage_id={stage_id}")
        return Result.success(data=result, message="阶段审批成功")
    except Exception as e:
        logger.error(f"API: 审批流水线阶段失败: {str(e)}", exc_info=True)
        raise


@router.post("/{opportunity_id}/pipeline/stages/{stage_id}/assign", response_model=Result[PipelineProgressResponse])
async def assign_stage(
    opportunity_id: str,
    stage_id: str,
    request_body: AssignStageRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db)
):
    """分配流水线阶段"""
    logger.info(f"API: 分配流水线阶段: opportunity_id={opportunity_id}, stage_id={stage_id}, assigned_to={request_body.assigned_to}")
    try:
        current_user_id = get_current_user_id(request_obj)
        if not current_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无法获取用户信息"
            )

        service = OpportunityPipelineService(db)
        result = await service.assign_stage(
            opportunity_id=opportunity_id,
            stage_id=stage_id,
            request=request_body,
            current_user_id=current_user_id
        )

        # 记录审计日志
        await log_audit_operation(
            db=db,
            request=request_obj,
            operation_type="UPDATE",
            entity_type="opportunity_pipeline_assignment",
            entity_id=f"{opportunity_id}:{stage_id}",
            status="SUCCESS"
        )

        logger.info(f"API: 流水线阶段分配成功: opportunity_id={opportunity_id}, stage_id={stage_id}")
        return Result.success(data=result, message="阶段分配成功")
    except Exception as e:
        logger.error(f"API: 分配流水线阶段失败: {str(e)}", exc_info=True)
        raise


@router.get("/{opportunity_id}/pipeline/progress", response_model=Result[PipelineProgressResponse])
async def get_pipeline_progress(
    opportunity_id: str,
    request_obj: Request,
    db: AsyncSession = Depends(get_db)
):
    """获取商机流水线进度"""
    logger.info(f"API: 获取商机流水线进度: opportunity_id={opportunity_id}")
    try:
        service = OpportunityPipelineService(db)
        result = await service.get_pipeline_progress(opportunity_id)

        logger.info(f"API: 获取商机流水线进度成功: opportunity_id={opportunity_id}")
        return Result.success(data=result)
    except Exception as e:
        logger.error(f"API: 获取商机流水线进度失败: {str(e)}", exc_info=True)
        raise


@router.get("/{opportunity_id}/pipeline/history", response_model=Result[PipelineHistoryResponse])
async def get_pipeline_history(
    opportunity_id: str,
    request_obj: Request,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """获取商机流水线历史"""
    logger.info(f"API: 获取商机流水线历史: opportunity_id={opportunity_id}, page={page}, size={size}")
    try:
        service = OpportunityPipelineService(db)
        result = await service.get_pipeline_history(
            opportunity_id=opportunity_id,
            page=page,
            size=size
        )

        logger.info(f"API: 获取商机流水线历史成功: opportunity_id={opportunity_id}")
        return Result.success(data=result)
    except Exception as e:
        logger.error(f"API: 获取商机流水线历史失败: {str(e)}", exc_info=True)
        raise
