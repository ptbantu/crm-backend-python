"""
联系人管理 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from common.utils.logger import get_logger
from foundation_service.schemas.contact import (
    ContactResponse,
    ContactCreateRequest,
    ContactUpdateRequest,
    ContactListResponse,
)
from foundation_service.services.contact_service import ContactService
from foundation_service.dependencies import get_db

logger = get_logger(__name__)
router = APIRouter()


@router.post("", response_model=Result[ContactResponse])
async def create_contact(
    request: ContactCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """创建联系人"""
    logger.info(f"API: 创建联系人请求: customer_id={request.customer_id}, name={request.first_name} {request.last_name}")
    try:
        service = ContactService(db)
        contact = await service.create_contact(request)
        logger.info(f"API: 联系人创建成功: id={contact.id}, customer_id={request.customer_id}")
        return Result.success(data=contact, message="联系人创建成功")
    except Exception as e:
        logger.error(f"API: 创建联系人失败: error={str(e)}", exc_info=True)
        raise


@router.get("/{contact_id}", response_model=Result[ContactResponse])
async def get_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db)
):
    """查询联系人详情"""
    logger.debug(f"API: 查询联系人详情: contact_id={contact_id}")
    try:
        service = ContactService(db)
        contact = await service.get_contact_by_id(contact_id)
        logger.debug(f"API: 联系人查询成功: id={contact.id}")
        return Result.success(data=contact)
    except Exception as e:
        logger.error(f"API: 查询联系人失败: contact_id={contact_id}, error={str(e)}", exc_info=True)
        raise


@router.put("/{contact_id}", response_model=Result[ContactResponse])
async def update_contact(
    contact_id: str,
    request: ContactUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """更新联系人"""
    service = ContactService(db)
    contact = await service.update_contact(contact_id, request)
    return Result.success(data=contact, message="联系人更新成功")


@router.delete("/{contact_id}", response_model=Result[None])
async def delete_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除联系人"""
    service = ContactService(db)
    await service.delete_contact(contact_id)
    return Result.success(message="联系人删除成功")


@router.get("/customers/{customer_id}/contacts", response_model=Result[ContactListResponse])
async def get_contacts_by_customer(
    customer_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    is_primary: Optional[bool] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """根据客户ID查询联系人列表"""
    service = ContactService(db)
    result = await service.get_contact_list_by_customer(
        customer_id=customer_id,
        page=page,
        size=size,
        is_primary=is_primary,
        is_active=is_active,
    )
    return Result.success(data=result)

