"""
商机 API 路由
"""
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from foundation_service.dependencies import (
    get_database_session,
    get_current_user_id,
    get_current_user_roles,
    get_current_organization_id,
)
from foundation_service.database import get_db
from common.auth import (
    get_current_user_id_from_request as get_user_id_from_token,
    get_current_user_roles_from_request as get_user_roles_from_token,
    require_auth
)
from foundation_service.config import settings
from foundation_service.services.opportunity_service import OpportunityService
from foundation_service.services.opportunity_stage_service import OpportunityStageService
from foundation_service.schemas.opportunity import (
    CreateOpportunityRequest,
    UpdateOpportunityRequest,
    OpportunityResponse,
    OpportunityListResponse,
    LeadConvertToOpportunityRequest,
    OpportunityConvertToOrderRequest,
    ProductDependencyValidationResponse,
    OpportunityAssignRequest,
    OpportunityStageUpdateRequest,
    OpportunityWorkflowStatusUpdateRequest,
    OpportunityServiceTypeUpdateRequest,
)
from foundation_service.schemas.opportunity_stage import (
    StageTemplateResponse,
    StageHistoryResponse,
    StageTransitionRequest,
    StageApprovalRequest,
    StageListResponse,
    StageHistoryListResponse,
)
from common.schemas.response import Result
from common.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("", response_model=Result[OpportunityResponse], status_code=201)
async def create_opportunity(
    request: CreateOpportunityRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """创建商机"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    organization_id = get_current_organization_id(request_obj)
    
    service = OpportunityService(db)
    result = await service.create_opportunity(request, organization_id, user_id)
    return Result.success(data=result, message="商机创建成功")


@router.get("", response_model=Result[OpportunityListResponse])
async def get_opportunity_list(
    request_obj: Request,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    owner_user_id: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """获取商机列表"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    user_roles = get_user_roles_from_token(request_obj, settings)
    organization_id = get_current_organization_id(request_obj)
    
    service = OpportunityService(db)
    result = await service.get_opportunity_list(
        organization_id=organization_id,
        page=page,
        size=size,
        owner_user_id=owner_user_id,
        customer_id=customer_id,
        stage=stage,
        status=status,
        name=name,
        current_user_id=user_id,
        current_user_roles=user_roles,
    )
    return Result.success(data=result)


@router.get("/{opportunity_id}", response_model=Result[OpportunityResponse])
async def get_opportunity(
    opportunity_id: str,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """获取商机详情"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    user_roles = get_user_roles_from_token(request_obj, settings)
    organization_id = get_current_organization_id(request_obj)
    
    service = OpportunityService(db)
    result = await service.get_opportunity(
        opportunity_id,
        organization_id,
        user_id,
        user_roles,
    )
    return Result.success(data=result)


@router.put("/{opportunity_id}", response_model=Result[OpportunityResponse])
async def update_opportunity(
    opportunity_id: str,
    request: UpdateOpportunityRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """更新商机"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    user_roles = get_user_roles_from_token(request_obj, settings)
    organization_id = get_current_organization_id(request_obj)
    
    service = OpportunityService(db)
    result = await service.update_opportunity(
        opportunity_id,
        request,
        organization_id,
        user_id,
        user_roles,
        user_id,
    )
    return Result.success(data=result, message="商机更新成功")


@router.delete("/{opportunity_id}", response_model=Result[None])
async def delete_opportunity(
    opportunity_id: str,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """删除商机"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    user_roles = get_user_roles_from_token(request_obj, settings)
    organization_id = get_current_organization_id(request_obj)
    
    service = OpportunityService(db)
    await service.delete_opportunity(
        opportunity_id,
        organization_id,
        user_id,
        user_roles,
    )
    return Result.success(message="商机删除成功")


@router.post("/{opportunity_id}/products/validate-dependencies", response_model=Result[ProductDependencyValidationResponse])
async def validate_product_dependencies(
    opportunity_id: str,
    product_ids: List[str],
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """验证产品依赖关系"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = OpportunityService(db)
    result = await service.validate_product_dependencies(product_ids)
    return Result.success(data=result)


@router.post("/products/calculate-order", response_model=Result[List[dict]])
async def calculate_execution_order(
    product_ids: List[str],
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """计算产品执行顺序"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = OpportunityService(db)
    result = await service.calculate_execution_order(product_ids)
    return Result.success(data=result)


@router.put("/{opportunity_id}/stage", response_model=Result[OpportunityResponse])
async def update_opportunity_stage(
    opportunity_id: str,
    request: OpportunityStageUpdateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """更新商机阶段"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    user_roles = get_user_roles_from_token(request_obj, settings)
    organization_id = get_current_organization_id(request_obj)
    
    update_request = UpdateOpportunityRequest(stage=request.stage)
    service = OpportunityService(db)
    result = await service.update_opportunity(
        opportunity_id,
        update_request,
        organization_id,
        user_id,
        user_roles,
        user_id,
    )
    return Result.success(data=result, message="商机阶段更新成功")


@router.post("/{opportunity_id}/assign", response_model=Result[OpportunityResponse])
async def assign_opportunity(
    opportunity_id: str,
    request: OpportunityAssignRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """分配商机"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    user_roles = get_user_roles_from_token(request_obj, settings)
    organization_id = get_current_organization_id(request_obj)
    
    update_request = UpdateOpportunityRequest(owner_user_id=request.owner_user_id)
    service = OpportunityService(db)
    result = await service.update_opportunity(
        opportunity_id,
        update_request,
        organization_id,
        user_id,
        user_roles,
        user_id,
    )
    return Result.success(data=result, message="商机分配成功")


@router.post("/convert-from-lead/{lead_id}", response_model=Result[OpportunityResponse], status_code=201)
async def convert_lead_to_opportunity(
    lead_id: str,
    request: LeadConvertToOpportunityRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """线索转化商机"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    organization_id = get_current_organization_id(request_obj)
    
    service = OpportunityService(db)
    result = await service.convert_lead_to_opportunity(
        lead_id,
        request,
        organization_id,
        user_id,
    )
    return Result.success(data=result, message="线索转化商机成功")


@router.post("/{opportunity_id}/convert-to-order", response_model=Result[dict], status_code=201)
async def convert_opportunity_to_order(
    opportunity_id: str,
    request: OpportunityConvertToOrderRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """商机转化订单"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    organization_id = get_current_organization_id(request_obj)
    
    service = OpportunityService(db)
    result = await service.convert_opportunity_to_order(
        opportunity_id,
        request,
        organization_id,
        user_id,
    )
    # result是OrderResponse对象，可以直接使用
    return Result.success(data=result, message="商机转化订单成功")


# ==================== 阶段流转相关API ====================

@router.get("/stages/templates", response_model=Result[StageListResponse])
async def get_stage_templates(
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """获取所有阶段模板"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = OpportunityStageService(db)
    templates = await service.get_all_stage_templates()
    return Result.success(data=StageListResponse(records=templates, total=len(templates)))


@router.get("/stages/templates/{code}", response_model=Result[StageTemplateResponse])
async def get_stage_template_by_code(
    code: str,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """根据代码获取阶段模板"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = OpportunityStageService(db)
    template = await service.get_stage_template_by_code(code)
    if not template:
        raise HTTPException(status_code=404, detail="阶段模板不存在")
    return Result.success(data=template)


@router.get("/{opportunity_id}/stages/history", response_model=Result[StageHistoryListResponse])
async def get_stage_history(
    opportunity_id: str,
    include_current: bool = Query(True, description="是否包含当前阶段"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """获取商机阶段历史"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = OpportunityStageService(db)
    histories = await service.get_stage_history(opportunity_id, include_current)
    return Result.success(data=StageHistoryListResponse(records=histories, total=len(histories)))


@router.get("/{opportunity_id}/stages/current", response_model=Result[StageHistoryResponse])
async def get_current_stage(
    opportunity_id: str,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """获取当前阶段"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = OpportunityStageService(db)
    stage = await service.get_current_stage(opportunity_id)
    if not stage:
        raise HTTPException(status_code=404, detail="当前没有阶段")
    return Result.success(data=stage)


@router.post("/{opportunity_id}/stages/transition", response_model=Result[StageHistoryResponse])
async def transition_stage(
    opportunity_id: str,
    request: StageTransitionRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """推进阶段"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    request.opportunity_id = opportunity_id
    service = OpportunityStageService(db)
    result = await service.transition_stage(request, user_id)
    return Result.success(data=result, message="阶段推进成功")


@router.post("/stages/approve", response_model=Result[StageHistoryResponse])
async def approve_stage(
    request: StageApprovalRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """审批阶段"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = OpportunityStageService(db)
    result = await service.approve_stage(request, user_id)
    return Result.success(data=result, message="阶段审批成功")


@router.get("/stages/pending-approvals", response_model=Result[StageHistoryListResponse])
async def get_pending_approvals(
    opportunity_id: Optional[str] = Query(None, description="商机ID（可选）"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """获取待审批的阶段历史记录"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = OpportunityStageService(db)
    histories = await service.get_pending_approvals(opportunity_id)
    return Result.success(data=StageHistoryListResponse(records=histories, total=len(histories)))


@router.put("/{opportunity_id}/workflow-status", response_model=Result[OpportunityResponse])
async def update_workflow_status(
    opportunity_id: str,
    request: OpportunityWorkflowStatusUpdateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """更新工作流状态"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    organization_id = get_current_organization_id(request_obj)
    service = OpportunityService(db)
    result = await service.update_workflow_status(
        opportunity_id,
        request,
        organization_id,
        user_id,
    )
    return Result.success(data=result, message="工作流状态更新成功")


@router.put("/{opportunity_id}/service-type", response_model=Result[OpportunityResponse])
async def update_service_type(
    opportunity_id: str,
    request: OpportunityServiceTypeUpdateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """更新服务类型"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    organization_id = get_current_organization_id(request_obj)
    service = OpportunityService(db)
    result = await service.update_service_type(
        opportunity_id,
        request,
        organization_id,
        user_id,
    )
    return Result.success(data=result, message="服务类型更新成功")

