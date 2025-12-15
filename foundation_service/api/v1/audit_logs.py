"""
操作审计日志 API
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from foundation_service.services.audit_service import AuditService
from foundation_service.dependencies import get_db
from common.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("", response_model=Result[dict])
async def get_audit_logs(
    http_request: Request,
    user_id: Optional[str] = Query(None, description="用户ID（可选）"),
    organization_id: Optional[str] = Query(None, description="组织ID（可选）"),
    operation_type: Optional[str] = Query(None, description="操作类型（可选）"),
    entity_type: Optional[str] = Query(None, description="实体类型（可选）"),
    entity_id: Optional[str] = Query(None, description="实体ID（可选）"),
    status: Optional[str] = Query(None, description="操作状态（SUCCESS/FAILURE，可选）"),
    start_date: Optional[datetime] = Query(None, description="开始时间（可选）"),
    end_date: Optional[datetime] = Query(None, description="结束时间（可选）"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    查询审计日志
    
    - **user_id**: 用户ID（可选）
    - **organization_id**: 组织ID（可选）
    - **operation_type**: 操作类型（CREATE/UPDATE/DELETE等，可选）
    - **entity_type**: 实体类型（表名，可选）
    - **entity_id**: 实体ID（可选）
    - **status**: 操作状态（SUCCESS/FAILURE，可选）
    - **start_date**: 开始时间（可选）
    - **end_date**: 结束时间（可选）
    - **page**: 页码（默认1）
    - **size**: 每页数量（默认20，最大100）
    """
    try:
        audit_service = AuditService(db)
        result = await audit_service.get_audit_logs(
            user_id=user_id,
            organization_id=organization_id,
            operation_type=operation_type,
            entity_type=entity_type,
            entity_id=entity_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            page=page,
            size=size
        )
        return Result.success(data=result)
    except Exception as e:
        logger.error(f"查询审计日志失败: {str(e)}", exc_info=True)
        raise


@router.get("/entity/{entity_type}/{entity_id}", response_model=Result[dict])
async def get_entity_history(
    entity_type: str,
    entity_id: str,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    查询某个实体的变更历史
    
    - **entity_type**: 实体类型（表名）
    - **entity_id**: 实体ID
    - **page**: 页码（默认1）
    - **size**: 每页数量（默认20，最大100）
    """
    try:
        audit_service = AuditService(db)
        result = await audit_service.get_entity_history(
            entity_type=entity_type,
            entity_id=entity_id,
            page=page,
            size=size
        )
        return Result.success(data=result)
    except Exception as e:
        logger.error(f"查询实体变更历史失败: {str(e)}", exc_info=True)
        raise


@router.get("/user/{user_id}", response_model=Result[dict])
async def get_user_audit_logs(
    user_id: str,
    start_date: Optional[datetime] = Query(None, description="开始时间（可选）"),
    end_date: Optional[datetime] = Query(None, description="结束时间（可选）"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    查询某个用户的操作记录
    
    - **user_id**: 用户ID
    - **start_date**: 开始时间（可选）
    - **end_date**: 结束时间（可选）
    - **page**: 页码（默认1）
    - **size**: 每页数量（默认20，最大100）
    """
    try:
        audit_service = AuditService(db)
        result = await audit_service.get_audit_logs(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            size=size
        )
        return Result.success(data=result)
    except Exception as e:
        logger.error(f"查询用户操作记录失败: {str(e)}", exc_info=True)
        raise
