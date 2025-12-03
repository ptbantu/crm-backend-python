"""
客户管理 API
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from common.utils.logger import get_logger
from common.auth import (
    get_current_user_id_from_request as get_user_id_from_token,
    require_auth
)
from service_management.config import settings
from service_management.schemas.customer import (
    CustomerResponse,
    CustomerCreateRequest,
    CustomerUpdateRequest,
    CustomerListResponse,
)
from service_management.schemas.customer_follow_up import (
    CustomerFollowUpCreateRequest,
    CustomerFollowUpResponse,
)
from service_management.schemas.customer_note import (
    CustomerNoteCreateRequest,
    CustomerNoteResponse,
)
from service_management.services.customer_service import CustomerService
from service_management.services.customer_follow_up_service import CustomerFollowUpService
from service_management.services.customer_note_service import CustomerNoteService
from service_management.dependencies import (
    get_db,
    get_current_user_id,
    get_current_organization_id,
    get_current_user_roles
)

logger = get_logger(__name__)
router = APIRouter()


@router.post("", response_model=Result[CustomerResponse])
async def create_customer(
    request: CustomerCreateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db)
):
    """创建客户"""
    logger.info(f"API: 创建客户请求: name={request.name}, code={request.code}, type={request.customer_type}")
    try:
        # 获取用户和组织信息
        organization_id = get_current_organization_id(request_obj)
        if not organization_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无法获取组织信息"
            )
        current_user_id = get_current_user_id(request_obj)
        
        service = CustomerService(db)
        customer = await service.create_customer(
            request=request,
            organization_id=organization_id,
            current_user_id=current_user_id
        )
        logger.info(f"API: 客户创建成功: id={customer.id}, name={customer.name}")
        return Result.success(data=customer, message="客户创建成功")
    except Exception as e:
        logger.error(f"API: 创建客户失败: {str(e)}", exc_info=True)
        raise


@router.get("/{customer_id}", response_model=Result[CustomerResponse])
async def get_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_db)
):
    """查询客户详情"""
    logger.debug(f"API: 查询客户详情: customer_id={customer_id}")
    try:
        service = CustomerService(db)
        customer = await service.get_customer_by_id(customer_id)
        logger.debug(f"API: 客户查询成功: id={customer.id}, name={customer.name}")
        return Result.success(data=customer)
    except Exception as e:
        logger.error(f"API: 查询客户失败: customer_id={customer_id}, error={str(e)}", exc_info=True)
        raise


@router.put("/{customer_id}", response_model=Result[CustomerResponse])
async def update_customer(
    customer_id: str,
    request: CustomerUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """更新客户"""
    logger.info(f"API: 更新客户请求: customer_id={customer_id}")
    try:
        service = CustomerService(db)
        customer = await service.update_customer(customer_id, request)
        logger.info(f"API: 客户更新成功: id={customer.id}, name={customer.name}")
        return Result.success(data=customer, message="客户更新成功")
    except Exception as e:
        logger.error(f"API: 更新客户失败: customer_id={customer_id}, error={str(e)}", exc_info=True)
        raise


@router.delete("/{customer_id}", response_model=Result[None])
async def delete_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除客户"""
    logger.info(f"API: 删除客户请求: customer_id={customer_id}")
    try:
        service = CustomerService(db)
        await service.delete_customer(customer_id)
        logger.info(f"API: 客户删除成功: customer_id={customer_id}")
        return Result.success(message="客户删除成功")
    except Exception as e:
        logger.error(f"API: 删除客户失败: customer_id={customer_id}, error={str(e)}", exc_info=True)
        raise


@router.get("", response_model=Result[CustomerListResponse])
async def get_customer_list(
    request_obj: Request,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    name: Optional[str] = None,
    code: Optional[str] = None,
    customer_type: Optional[str] = None,
    customer_source_type: Optional[str] = None,
    parent_customer_id: Optional[str] = None,
    owner_user_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    source_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    is_locked: Optional[bool] = None,
    view_type: Optional[str] = None,  # 'my' 或 'global'
    db: AsyncSession = Depends(get_db)
):
    """分页查询客户列表（带权限过滤）"""
    logger.debug(f"API: 查询客户列表: page={page}, size={size}, name={name}, code={code}, type={customer_type}")
    try:
        # 获取用户和组织信息
        organization_id = get_current_organization_id(request_obj)
        if not organization_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无法获取组织信息"
            )
        current_user_id = get_current_user_id(request_obj)
        current_user_roles = get_current_user_roles(request_obj)
        
        # 如果 view_type 是 'my'，强制设置 owner_user_id 为当前用户 ID
        # 如果 view_type 是 'global' 或 None，且用户是 ADMIN，则 owner_user_id 为 None（显示所有客户）
        effective_owner_user_id = owner_user_id
        if view_type == 'my':
            if current_user_id:
                effective_owner_user_id = current_user_id
                logger.info(f"我的客户视图：强制设置 owner_user_id={current_user_id}, view_type={view_type}")
            else:
                logger.warning(f"我的客户视图：但缺少 current_user_id，无法过滤")
        elif view_type == 'global':
            # 全局客户视图：ADMIN 可以看到所有客户（owner_user_id=None），SALES 只能看自己的
            if current_user_roles and 'ADMIN' in current_user_roles:
                effective_owner_user_id = None  # ADMIN 查看所有客户
                logger.info(f"全局客户视图（ADMIN）：显示所有客户，view_type={view_type}")
            else:
                # 非 ADMIN 用户，即使选择全局视图，也只能看自己的客户
                effective_owner_user_id = current_user_id if current_user_id else None
                logger.info(f"全局客户视图（非ADMIN）：只能看自己的客户，owner_user_id={effective_owner_user_id}")
        else:
            # view_type 为 None 的情况，根据角色决定
            logger.debug(f"未指定 view_type，使用默认权限过滤逻辑")
        
        service = CustomerService(db)
        result = await service.get_customer_list(
            organization_id=organization_id,
            current_user_id=current_user_id,
            current_user_roles=current_user_roles,
            page=page,
            size=size,
            name=name,
            code=code,
            customer_type=customer_type,
            customer_source_type=customer_source_type,
            parent_customer_id=parent_customer_id,
            owner_user_id=effective_owner_user_id,
            agent_id=agent_id,
            source_id=source_id,
            channel_id=channel_id,
            is_locked=is_locked,
        )
        logger.debug(f"API: 客户列表查询成功: total={result.total}, returned={len(result.items)}")
        return Result.success(data=result)
    except Exception as e:
        logger.error(f"API: 查询客户列表失败: error={str(e)}", exc_info=True)
        raise


@router.get("/{customer_id}/follow-ups", response_model=Result[List[CustomerFollowUpResponse]])
async def get_customer_follow_ups(
    customer_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取客户跟进记录列表"""
    logger.debug(f"API: 查询客户跟进记录: customer_id={customer_id}")
    try:
        service = CustomerFollowUpService(db)
        result = await service.get_follow_ups_by_customer_id(customer_id)
        logger.debug(f"API: 客户跟进记录查询成功: customer_id={customer_id}, count={len(result)}")
        return Result.success(data=result)
    except Exception as e:
        logger.error(f"API: 查询客户跟进记录失败: customer_id={customer_id}, error={str(e)}", exc_info=True)
        raise


@router.post("/{customer_id}/follow-ups", response_model=Result[CustomerFollowUpResponse], status_code=201)
async def create_customer_follow_up(
    customer_id: str,
    request: CustomerFollowUpCreateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db)
):
    """创建客户跟进记录"""
    logger.info(f"API: 创建客户跟进记录: customer_id={customer_id}")
    try:
        # 从 JWT token 解析用户ID
        user_id = get_user_id_from_token(request_obj, settings)
        if not user_id:
            logger.warning(f"Service Management: JWT 验证失败，路径: {request_obj.url.path}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="需要认证，请提供有效的 JWT token"
            )
        
        service = CustomerFollowUpService(db)
        result = await service.create_follow_up(customer_id, request, user_id)
        logger.info(f"API: 客户跟进记录创建成功: customer_id={customer_id}, follow_up_id={result.id}")
        return Result.success(data=result, message="跟进记录创建成功")
    except Exception as e:
        logger.error(f"API: 创建客户跟进记录失败: customer_id={customer_id}, error={str(e)}", exc_info=True)
        raise


@router.get("/{customer_id}/notes", response_model=Result[List[CustomerNoteResponse]])
async def get_customer_notes(
    customer_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取客户备注列表"""
    logger.debug(f"API: 查询客户备注: customer_id={customer_id}")
    try:
        service = CustomerNoteService(db)
        result = await service.get_notes_by_customer_id(customer_id)
        logger.debug(f"API: 客户备注查询成功: customer_id={customer_id}, count={len(result)}")
        return Result.success(data=result)
    except Exception as e:
        logger.error(f"API: 查询客户备注失败: customer_id={customer_id}, error={str(e)}", exc_info=True)
        raise


@router.post("/{customer_id}/notes", response_model=Result[CustomerNoteResponse], status_code=201)
async def create_customer_note(
    customer_id: str,
    request: CustomerNoteCreateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db)
):
    """创建客户备注"""
    logger.info(f"API: 创建客户备注: customer_id={customer_id}")
    try:
        # 从 JWT token 解析用户ID
        user_id = get_user_id_from_token(request_obj, settings)
        if not user_id:
            logger.warning(f"Service Management: JWT 验证失败，路径: {request_obj.url.path}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="需要认证，请提供有效的 JWT token"
            )
        
        service = CustomerNoteService(db)
        result = await service.create_note(customer_id, request, user_id)
        logger.info(f"API: 客户备注创建成功: customer_id={customer_id}, note_id={result.id}")
        return Result.success(data=result, message="备注创建成功")
    except Exception as e:
        logger.error(f"API: 创建客户备注失败: customer_id={customer_id}, error={str(e)}", exc_info=True)
        raise

