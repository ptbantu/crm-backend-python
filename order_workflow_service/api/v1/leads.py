"""
线索 API 路由
"""
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from order_workflow_service.dependencies import (
    get_database_session,
    get_current_user_id,
    get_current_user_roles,
    get_current_organization_id,
)
from common.auth import (
    get_current_user_id_from_request as get_user_id_from_token,
    get_current_user_roles_from_request as get_user_roles_from_token,
    require_auth
)
from order_workflow_service.config import settings
from order_workflow_service.services.lead_service import LeadService
from order_workflow_service.services.lead_duplicate_check_service import LeadDuplicateCheckService
from order_workflow_service.services.lead_follow_up_service import LeadFollowUpService
from order_workflow_service.services.lead_note_service import LeadNoteService
from order_workflow_service.services.tianyancha_service import TianyanchaService
from order_workflow_service.schemas.lead import (
    LeadCreateRequest,
    LeadUpdateRequest,
    LeadResponse,
    LeadListResponse,
    LeadDuplicateCheckRequest,
    LeadDuplicateCheckResponse,
    LeadMoveToPoolRequest,
    LeadAssignRequest,
)
from order_workflow_service.schemas.lead_follow_up import (
    LeadFollowUpCreateRequest,
    LeadFollowUpResponse,
)
from order_workflow_service.schemas.lead_note import (
    LeadNoteCreateRequest,
    LeadNoteResponse,
)
from common.schemas.response import Result
from common.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("", response_model=Result[LeadResponse], status_code=201)
async def create_lead(
    request: LeadCreateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_database_session),
):
    """创建线索（线索与用户绑定，不需要组织ID）"""
    # 从 JWT token 解析用户ID（必须）
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        logger.warning(f"Order Workflow: JWT 验证失败，路径: {request_obj.url.path}")
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    # 组织ID可选，如果没有则只与用户绑定
    organization_id = get_current_organization_id(request_obj)
    
    service = LeadService(db)
    result = await service.create_lead(request, organization_id, user_id)
    return Result.success(data=result, message="线索创建成功")


@router.get("", response_model=Result[LeadListResponse])
async def get_lead_list(
    request_obj: Request,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=1000),  # 允许更大的 size 用于统计功能
    owner_user_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    is_in_public_pool: Optional[bool] = Query(None),
    customer_id: Optional[str] = Query(None),
    company_name: Optional[str] = Query(None),
    phone: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_database_session),
):
    """获取线索列表（根据用户ID查询，从token解析）"""
    # 从 JWT token 解析用户ID（必须）
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        logger.warning(f"Order Workflow: JWT 验证失败，路径: {request_obj.url.path}")
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    # 从 JWT token 解析用户角色（可选）
    user_roles = get_user_roles_from_token(request_obj, settings)
    
    # 组织ID可选，如果没有则只根据用户ID查询
    organization_id = get_current_organization_id(request_obj)
    
    service = LeadService(db)
    result = await service.get_lead_list(
        organization_id=organization_id,
        page=page,
        size=size,
        owner_user_id=owner_user_id,
        status=status,
        is_in_public_pool=is_in_public_pool,
        customer_id=customer_id,
        company_name=company_name,
        phone=phone,
        email=email,
        current_user_id=user_id,
        current_user_roles=user_roles,
    )
    return Result.success(data=result)


@router.get("/{lead_id}", response_model=Result[LeadResponse])
async def get_lead(
    lead_id: str,
    request_obj: Request,
    db: AsyncSession = Depends(get_database_session),
):
    """获取线索详情（线索与用户绑定，不需要组织ID）"""
    # 从 JWT token 解析用户ID（必须）
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        logger.warning(f"Order Workflow: JWT 验证失败，路径: {request_obj.url.path}")
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    # 从 JWT token 解析用户角色（可选）
    user_roles = get_user_roles_from_token(request_obj, settings)
    
    # 组织ID可选
    organization_id = get_current_organization_id(request_obj)
    
    service = LeadService(db)
    result = await service.get_lead(lead_id, organization_id, user_id, user_roles)
    return Result.success(data=result)


@router.put("/{lead_id}", response_model=Result[LeadResponse])
async def update_lead(
    lead_id: str,
    request: LeadUpdateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_database_session),
):
    """更新线索（线索与用户绑定，不需要组织ID）"""
    # 从 JWT token 解析用户ID（必须）
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        logger.warning(f"Order Workflow: JWT 验证失败，路径: {request_obj.url.path}")
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    # 从 JWT token 解析用户角色（可选）
    user_roles = get_user_roles_from_token(request_obj, settings)
    
    # 组织ID可选
    organization_id = get_current_organization_id(request_obj)
    
    service = LeadService(db)
    result = await service.update_lead(lead_id, request, organization_id, user_id, user_id, user_roles)
    return Result.success(data=result, message="线索更新成功")


@router.delete("/{lead_id}", response_model=Result[None])
async def delete_lead(
    lead_id: str,
    request_obj: Request,
    db: AsyncSession = Depends(get_database_session),
):
    """删除线索（仅admin）"""
    organization_id = get_current_organization_id(request_obj)
    if not organization_id:
        return Result.error(code=400, message="缺少组织ID")
    
    user_id = get_current_user_id(request_obj)
    user_roles = get_current_user_roles(request_obj)
    
    service = LeadService(db)
    await service.delete_lead(lead_id, organization_id, user_id, user_roles)
    return Result.success(message="线索删除成功")


@router.post("/{lead_id}/move-to-pool", response_model=Result[LeadResponse])
async def move_lead_to_pool(
    lead_id: str,
    request: LeadMoveToPoolRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_database_session),
):
    """移入公海池"""
    organization_id = get_current_organization_id(request_obj)
    if not organization_id:
        return Result.error(code=400, message="缺少组织ID")
    
    user_id = get_current_user_id(request_obj)
    user_roles = get_current_user_roles(request_obj)
    
    service = LeadService(db)
    result = await service.move_to_pool(lead_id, request.pool_id, organization_id, user_id, user_roles)
    return Result.success(data=result, message="线索已移入公海池")


@router.post("/{lead_id}/assign", response_model=Result[LeadResponse])
async def assign_lead(
    lead_id: str,
    request: LeadAssignRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_database_session),
):
    """分配线索"""
    organization_id = get_current_organization_id(request_obj)
    if not organization_id:
        return Result.error(code=400, message="缺少组织ID")
    
    user_id = get_current_user_id(request_obj)
    user_roles = get_current_user_roles(request_obj)
    
    service = LeadService(db)
    result = await service.assign_lead(lead_id, request.owner_user_id, organization_id, user_id, user_roles)
    return Result.success(data=result, message="线索分配成功")


@router.get("/{lead_id}/follow-ups", response_model=Result[List[LeadFollowUpResponse]])
async def get_lead_follow_ups(
    lead_id: str,
    db: AsyncSession = Depends(get_database_session),
):
    """获取线索跟进记录列表"""
    service = LeadFollowUpService(db)
    result = await service.get_follow_ups_by_lead_id(lead_id)
    return Result.success(data=result)


@router.post("/{lead_id}/follow-ups", response_model=Result[LeadFollowUpResponse], status_code=201)
async def create_lead_follow_up(
    lead_id: str,
    request: LeadFollowUpCreateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_database_session),
):
    """创建跟进记录"""
    user_id = get_current_user_id(request_obj)
    service = LeadFollowUpService(db)
    result = await service.create_follow_up(lead_id, request, user_id)
    return Result.success(data=result, message="跟进记录创建成功")


@router.get("/{lead_id}/notes", response_model=Result[List[LeadNoteResponse]])
async def get_lead_notes(
    lead_id: str,
    db: AsyncSession = Depends(get_database_session),
):
    """获取线索备注列表"""
    service = LeadNoteService(db)
    result = await service.get_notes_by_lead_id(lead_id)
    return Result.success(data=result)


@router.post("/{lead_id}/notes", response_model=Result[LeadNoteResponse], status_code=201)
async def create_lead_note(
    lead_id: str,
    request: LeadNoteCreateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_database_session),
):
    """创建备注"""
    user_id = get_current_user_id(request_obj)
    service = LeadNoteService(db)
    result = await service.create_note(lead_id, request, user_id)
    return Result.success(data=result, message="备注创建成功")


@router.post("/check-duplicate", response_model=Result[LeadDuplicateCheckResponse])
async def check_duplicate(
    request: LeadDuplicateCheckRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_database_session),
):
    """线索查重"""
    organization_id = get_current_organization_id(request_obj)
    if not organization_id:
        return Result.error(code=400, message="缺少组织ID")
    
    service = LeadDuplicateCheckService(db)
    result = await service.check_duplicate(request, organization_id)
    return Result.success(data=result)


@router.post("/tianyancha-enrich", response_model=Result[dict])
async def enrich_with_tianyancha(
    lead_id: str,
    company_name: str,
    request_obj: Request,
    db: AsyncSession = Depends(get_database_session),
):
    """天眼查数据填充（预留接口）"""
    organization_id = get_current_organization_id(request_obj)
    if not organization_id:
        return Result.error(code=400, message="缺少组织ID")
    
    service = TianyanchaService(db)
    result = await service.enrich_lead_data(lead_id, company_name, organization_id)
    return Result.success(data=result, message="天眼查数据填充完成（预留接口）")

