"""
客户管理 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from common.utils.logger import get_logger
from service_management.schemas.customer import (
    CustomerResponse,
    CustomerCreateRequest,
    CustomerUpdateRequest,
    CustomerListResponse,
)
from service_management.services.customer_service import CustomerService
from service_management.dependencies import get_db

logger = get_logger(__name__)
router = APIRouter()


@router.post("", response_model=Result[CustomerResponse])
async def create_customer(
    request: CustomerCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """创建客户"""
    logger.info(f"API: 创建客户请求: name={request.name}, code={request.code}, type={request.customer_type}")
    try:
        service = CustomerService(db)
        customer = await service.create_customer(request)
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
    db: AsyncSession = Depends(get_db)
):
    """分页查询客户列表"""
    logger.debug(f"API: 查询客户列表: page={page}, size={size}, name={name}, code={code}, type={customer_type}")
    try:
        service = CustomerService(db)
        result = await service.get_customer_list(
            page=page,
            size=size,
            name=name,
            code=code,
            customer_type=customer_type,
            customer_source_type=customer_source_type,
            parent_customer_id=parent_customer_id,
            owner_user_id=owner_user_id,
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

