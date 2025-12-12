"""
审计日志 API 路由
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from foundation_service.dependencies import (
    get_database_session,
    get_current_user_id,
    get_current_organization_id,
    require_auth,
)
from foundation_service.services.audit_service import AuditService
from foundation_service.schemas.audit import (
    AuditLogResponse,
    AuditLogQueryRequest,
    AuditLogListResponse,
    AuditLogExportRequest,
)
from common.schemas.response import Result
from common.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("", response_model=Result[AuditLogListResponse])
async def get_audit_logs(
    page: int = Query(1, ge=1, description="页码（从1开始）"),
    size: int = Query(10, ge=1, le=100, description="每页数量（最大100）"),
    organization_id: Optional[str] = Query(None, description="组织ID"),
    user_id: Optional[str] = Query(None, description="用户ID"),
    action: Optional[str] = Query(None, description="操作类型"),
    resource_type: Optional[str] = Query(None, description="资源类型"),
    resource_id: Optional[str] = Query(None, description="资源ID"),
    category: Optional[str] = Query(None, description="操作分类"),
    status_filter: Optional[str] = Query(None, alias="status", description="操作状态"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    order_by: str = Query("created_at", description="排序字段"),
    order_desc: bool = Query(True, description="是否降序"),
    db: AsyncSession = Depends(get_database_session),
    current_user_id: str = Depends(require_auth),
    current_org_id: Optional[str] = Depends(get_current_organization_id),
):
    """
    查询审计日志列表
    
    支持筛选：组织ID、用户ID、资源类型、操作类型、时间范围等
    支持分页和排序
    """
    try:
        # 如果没有指定组织ID，使用当前用户的组织ID
        if not organization_id:
            organization_id = current_org_id
        
        # 构建查询请求
        query = AuditLogQueryRequest(
            page=page,
            size=size,
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            category=category,
            status=status_filter,
            start_time=start_time,
            end_time=end_time,
            order_by=order_by,
            order_desc=order_desc,
        )
        
        audit_service = AuditService(db)
        result = await audit_service.get_audit_logs(query)
        
        return Result.success(data=result)
    except Exception as e:
        logger.error(f"查询审计日志失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询审计日志失败: {str(e)}"
        )


@router.get("/{audit_log_id}", response_model=Result[AuditLogResponse])
async def get_audit_log(
    audit_log_id: str,
    db: AsyncSession = Depends(get_database_session),
    current_user_id: str = Depends(require_auth),
):
    """
    查询审计日志详情
    
    Args:
        audit_log_id: 审计日志ID
    """
    try:
        audit_service = AuditService(db)
        audit_log = await audit_service.get_audit_log_by_id(audit_log_id)
        
        return Result.success(data=audit_log)
    except Exception as e:
        logger.error(f"查询审计日志详情失败: {str(e)}", exc_info=True)
        if "不存在" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询审计日志详情失败: {str(e)}"
        )


@router.get("/users/{user_id}", response_model=Result[AuditLogListResponse])
async def get_user_audit_logs(
    user_id: str,
    page: int = Query(1, ge=1, description="页码（从1开始）"),
    size: int = Query(10, ge=1, le=100, description="每页数量（最大100）"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    db: AsyncSession = Depends(get_database_session),
    current_user_id: str = Depends(require_auth),
):
    """
    查询指定用户的审计日志
    
    Args:
        user_id: 用户ID
    """
    try:
        audit_service = AuditService(db)
        result = await audit_service.get_user_audit_logs(
            user_id=user_id,
            page=page,
            size=size,
            start_time=start_time,
            end_time=end_time,
        )
        
        return Result.success(data=result)
    except Exception as e:
        logger.error(f"查询用户审计日志失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询用户审计日志失败: {str(e)}"
        )


@router.get("/resources/{resource_type}/{resource_id}", response_model=Result[AuditLogListResponse])
async def get_resource_audit_logs(
    resource_type: str,
    resource_id: str,
    page: int = Query(1, ge=1, description="页码（从1开始）"),
    size: int = Query(10, ge=1, le=100, description="每页数量（最大100）"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    db: AsyncSession = Depends(get_database_session),
    current_user_id: str = Depends(require_auth),
):
    """
    查询指定资源的审计日志
    
    Args:
        resource_type: 资源类型
        resource_id: 资源ID
    """
    try:
        audit_service = AuditService(db)
        result = await audit_service.get_resource_audit_logs(
            resource_type=resource_type,
            resource_id=resource_id,
            page=page,
            size=size,
            start_time=start_time,
            end_time=end_time,
        )
        
        return Result.success(data=result)
    except Exception as e:
        logger.error(f"查询资源审计日志失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询资源审计日志失败: {str(e)}"
        )


@router.post("/export", response_model=Result[dict])
async def export_audit_logs(
    export_request: AuditLogExportRequest,
    db: AsyncSession = Depends(get_database_session),
    current_user_id: str = Depends(require_auth),
    current_org_id: Optional[str] = Depends(get_current_organization_id),
):
    """
    导出审计日志
    
    支持导出为 JSON 或 CSV 格式
    """
    try:
        # 如果没有指定组织ID，使用当前用户的组织ID
        if not export_request.organization_id:
            export_request.organization_id = current_org_id
        
        audit_service = AuditService(db)
        content, mime_type = await audit_service.export_audit_logs(export_request)
        
        return Result.success(data={
            "content": content,
            "mime_type": mime_type,
            "format": export_request.format,
        })
    except Exception as e:
        logger.error(f"导出审计日志失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出审计日志失败: {str(e)}"
        )
