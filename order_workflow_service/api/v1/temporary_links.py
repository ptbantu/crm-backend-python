"""
临时链接 API 路由
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime

from order_workflow_service.dependencies import (
    get_database_session,
    get_current_user_id,
)
from order_workflow_service.services.temporary_link_service import TemporaryLinkService
from order_workflow_service.schemas.temporary_link import (
    TemporaryLinkCreateRequest,
    TemporaryLinkResponse,
    TemporaryLinkAccessResponse,
)
from common.schemas.response import Result
from common.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("", response_model=Result[TemporaryLinkResponse], status_code=201)
async def create_temporary_link(
    request: TemporaryLinkCreateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_database_session),
):
    """生成临时链接"""
    user_id = get_current_user_id(request_obj)
    service = TemporaryLinkService(db)
    link = await service.create_temporary_link(
        resource_type=request.resource_type,
        resource_id=request.resource_id,
        expires_at=request.expires_at,
        max_access_count=request.max_access_count,
        created_by=user_id,
    )
    return Result.success(data=TemporaryLinkResponse.model_validate(link), message="临时链接创建成功")


@router.get("/{token}", response_model=Result[TemporaryLinkAccessResponse])
async def access_temporary_link(
    token: str,
    db: AsyncSession = Depends(get_database_session),
):
    """访问临时链接（公开接口，无需认证）"""
    service = TemporaryLinkService(db)
    result = await service.access_temporary_link(token)
    
    return Result.success(
        data=TemporaryLinkAccessResponse(
            link=TemporaryLinkResponse.model_validate(result["link"]),
            resource_data=result.get("resource_data"),
        ),
        message="链接访问成功"
    )


@router.get("", response_model=Result[List[TemporaryLinkResponse]])
async def get_temporary_link_list(
    request_obj: Request,
    db: AsyncSession = Depends(get_database_session),
):
    """获取链接列表（创建者）"""
    user_id = get_current_user_id(request_obj)
    if not user_id:
        return Result.error(code=401, message="需要认证")
    
    # TODO: 实现根据创建者查询链接列表
    return Result.success(data=[], message="功能待实现")


@router.put("/{link_id}/disable", response_model=Result[TemporaryLinkResponse])
async def disable_temporary_link(
    link_id: str,
    request_obj: Request,
    db: AsyncSession = Depends(get_database_session),
):
    """禁用链接"""
    user_id = get_current_user_id(request_obj)
    if not user_id:
        return Result.error(code=401, message="需要认证")
    
    service = TemporaryLinkService(db)
    link = await service.repository.get_by_id(link_id)
    if not link or link.created_by != user_id:
        return Result.error(code=404, message="链接不存在或无权操作")
    
    link.is_active = False
    await service.db.commit()
    await service.db.refresh(link)
    
    return Result.success(data=TemporaryLinkResponse.model_validate(link), message="链接已禁用")

