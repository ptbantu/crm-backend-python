"""
执行订单 API 路由
"""
from fastapi import APIRouter, Depends, Query, Request, HTTPException, Path
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from foundation_service.database import get_db
from common.auth import (
    get_current_user_id_from_request as get_user_id_from_token,
)
from foundation_service.config import settings
from foundation_service.services.execution_order_service import ExecutionOrderService
from foundation_service.schemas.execution_order import (
    ExecutionOrderCreateRequest,
    ExecutionOrderResponse,
    ExecutionOrderListResponse,
    CompanyRegistrationInfoRequest,
    CompanyRegistrationInfoResponse,
)
from common.schemas.response import Result

router = APIRouter(prefix="/execution-orders", tags=["执行订单"])


@router.post("", response_model=Result[ExecutionOrderResponse], status_code=201)
async def create_execution_order(
    request: ExecutionOrderCreateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """创建执行订单"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = ExecutionOrderService(db)
    result = await service.create_execution_order(request, user_id)
    return Result.success(data=result, message="执行订单创建成功")


@router.get("", response_model=Result[ExecutionOrderListResponse])
async def get_execution_order_list(
    request_obj: Request,
    opportunity_id: Optional[str] = Query(None, description="商机ID"),
    status: Optional[str] = Query(None, description="状态"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取执行订单列表"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = ExecutionOrderService(db)
    result = await service.get_execution_order_list(opportunity_id, status, page, size)
    return Result.success(data=result)


@router.get("/{execution_order_id}", response_model=Result[ExecutionOrderResponse])
async def get_execution_order(
    execution_order_id: str = Path(..., description="执行订单ID"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """获取执行订单详情"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = ExecutionOrderService(db)
    result = await service.get_execution_order(execution_order_id)
    return Result.success(data=result)


@router.put("/{execution_order_id}/assign", response_model=Result[ExecutionOrderResponse])
async def assign_execution_order(
    execution_order_id: str = Path(..., description="执行订单ID"),
    assigned_to: str = Query(..., description="分配执行人ID"),
    assigned_team: Optional[str] = Query(None, description="分配团队"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """分配执行订单"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = ExecutionOrderService(db)
    result = await service.assign_execution_order(execution_order_id, assigned_to, assigned_team)
    return Result.success(data=result, message="执行订单分配成功")


@router.put("/{execution_order_id}/status", response_model=Result[ExecutionOrderResponse])
async def update_execution_status(
    execution_order_id: str = Path(..., description="执行订单ID"),
    status: str = Query(..., description="状态"),
    actual_end_date: Optional[str] = Query(None, description="实际结束日期"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """更新执行订单状态"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    from datetime import datetime
    end_date = datetime.strptime(actual_end_date, "%Y-%m-%d").date() if actual_end_date else None
    
    service = ExecutionOrderService(db)
    result = await service.update_execution_status(execution_order_id, status, end_date)
    return Result.success(data=result, message="执行订单状态更新成功")


@router.get("/{execution_order_id}/dependencies", response_model=Result[dict])
async def check_dependencies(
    execution_order_id: str = Path(..., description="执行订单ID"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """检查依赖关系"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = ExecutionOrderService(db)
    result = await service.check_dependencies(execution_order_id)
    return Result.success(data=result)


@router.post("/company-registration", response_model=Result[CompanyRegistrationInfoResponse], status_code=201)
async def create_company_registration_info(
    request: CompanyRegistrationInfoRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """创建公司注册信息"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = ExecutionOrderService(db)
    result = await service.create_company_registration_info(request)
    return Result.success(data=result, message="公司注册信息创建成功")


@router.post("/company-registration/{execution_order_id}/complete", response_model=Result[CompanyRegistrationInfoResponse])
async def complete_company_registration(
    execution_order_id: str = Path(..., description="执行订单ID"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """完成公司注册"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = ExecutionOrderService(db)
    result = await service.complete_company_registration(execution_order_id)
    return Result.success(data=result, message="公司注册完成成功")
