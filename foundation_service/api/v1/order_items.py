"""
订单项 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from foundation_service.dependencies import get_db as get_db
from foundation_service.services.order_item_service import OrderItemService
from foundation_service.schemas.order_item import (
    OrderItemCreateRequest,
    OrderItemUpdateRequest,
    OrderItemResponse,
    OrderItemListResponse,
)
from foundation_service.schemas.common import LanguageEnum
from common.schemas.response import Result
from common.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("", response_model=Result[OrderItemResponse], status_code=status.HTTP_201_CREATED)
async def create_order_item(
    request: OrderItemCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    创建订单项
    
    - **order_id**: 订单ID（必填）
    - **item_number**: 订单项序号（必填）
    - **product_id**: 产品/服务ID（可选）
    - **quantity**: 数量（默认1）
    - **unit_price**: 单价（可选）
    - **discount_amount**: 折扣金额（默认0）
    """
    try:
        service = OrderItemService(db)
        result = await service.create_order_item(request)
        return Result.success(data=result)
    except Exception as e:
        logger.error(f"创建订单项失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建订单项失败: {str(e)}"
        )


@router.get("/{item_id}", response_model=Result[OrderItemResponse])
async def get_order_item(
    item_id: str,
    lang: LanguageEnum = Query(LanguageEnum.ZH, description="语言代码：zh（中文）或 id（印尼语）"),
    db: AsyncSession = Depends(get_db),
):
    """
    根据ID查询订单项
    
    - **item_id**: 订单项ID
    - **lang**: 语言代码（zh/id），默认 zh
    """
    try:
        service = OrderItemService(db)
        result = await service.get_order_item_by_id(item_id, lang.value)
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单项不存在"
            )
        
        return Result.success(data=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询订单项失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询订单项失败: {str(e)}"
        )


@router.put("/{item_id}", response_model=Result[OrderItemResponse])
async def update_order_item(
    item_id: str,
    request: OrderItemUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    更新订单项
    
    - **item_id**: 订单项ID
    - 支持更新：产品信息、数量、价格、状态等
    """
    try:
        service = OrderItemService(db)
        result = await service.update_order_item(item_id, request)
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单项不存在"
            )
        
        return Result.success(data=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新订单项失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新订单项失败: {str(e)}"
        )


@router.delete("/{item_id}", response_model=Result[bool])
async def delete_order_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    删除订单项
    
    - **item_id**: 订单项ID
    """
    try:
        service = OrderItemService(db)
        success = await service.delete_order_item(item_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单项不存在"
            )
        
        return Result.success(data=True)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除订单项失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除订单项失败: {str(e)}"
        )


@router.get("/order/{order_id}/items", response_model=Result[OrderItemListResponse])
async def list_order_items(
    order_id: str,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(100, ge=1, le=1000, description="每页数量"),
    lang: LanguageEnum = Query(LanguageEnum.ZH, description="语言代码：zh（中文）或 id（印尼语）"),
    db: AsyncSession = Depends(get_db),
):
    """
    根据订单ID查询订单项列表
    
    - **order_id**: 订单ID
    - **page**: 页码（默认1）
    - **size**: 每页数量（默认100，最大1000）
    - **lang**: 语言代码（zh/id），默认 zh
    """
    try:
        service = OrderItemService(db)
        result = await service.list_order_items_by_order(order_id, page, size, lang.value)
        return Result.success(data=result)
    except Exception as e:
        logger.error(f"查询订单项列表失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询订单项列表失败: {str(e)}"
        )

