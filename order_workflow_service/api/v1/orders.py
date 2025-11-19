"""
订单 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from order_workflow_service.dependencies import get_database_session
from order_workflow_service.services.order_service import OrderService
from order_workflow_service.schemas.order import (
    OrderCreateRequest,
    OrderUpdateRequest,
    OrderResponse,
    OrderListResponse,
)
from common.schemas.response import Result
from common.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("", response_model=Result[OrderResponse], status_code=status.HTTP_201_CREATED)
async def create_order(
    request: OrderCreateRequest,
    db: AsyncSession = Depends(get_database_session),
):
    """
    创建订单
    
    - **title**: 订单标题（必填）
    - **customer_id**: 客户ID（必填）
    - **sales_user_id**: 销售用户ID（必填）
    - **order_items**: 订单项列表（可选，一个订单可以包含多个订单项）
    - **entry_city**: 入境城市（可选，来自 EVOA）
    - **passport_id**: 护照ID（可选，来自 EVOA）
    - **processor**: 处理器（可选，来自 EVOA）
    """
    try:
        service = OrderService(db)
        result = await service.create_order(request)
        return Result.success(data=result, message="订单创建成功")
    except Exception as e:
        logger.error(f"创建订单失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建订单失败: {str(e)}"
        )


@router.get("/{order_id}", response_model=Result[OrderResponse])
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_database_session),
):
    """
    根据ID查询订单
    
    - **order_id**: 订单ID
    """
    try:
        service = OrderService(db)
        result = await service.get_order_by_id(order_id)
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        return Result.success(data=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询订单失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询订单失败: {str(e)}"
        )


@router.put("/{order_id}", response_model=Result[OrderResponse])
async def update_order(
    order_id: str,
    request: OrderUpdateRequest,
    db: AsyncSession = Depends(get_database_session),
):
    """
    更新订单
    
    - **order_id**: 订单ID
    - 支持更新：标题、状态、备注、EVOA字段等
    """
    try:
        service = OrderService(db)
        result = await service.update_order(order_id, request)
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        return Result.success(data=result, message="订单更新成功")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新订单失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新订单失败: {str(e)}"
        )


@router.delete("/{order_id}", response_model=Result[bool])
async def delete_order(
    order_id: str,
    db: AsyncSession = Depends(get_database_session),
):
    """
    删除订单
    
    - **order_id**: 订单ID
    
    注意: 删除订单会级联删除所有订单项、评论和文件
    """
    try:
        service = OrderService(db)
        success = await service.delete_order(order_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        return Result.success(data=True, message="订单删除成功")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除订单失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除订单失败: {str(e)}"
        )


@router.get("", response_model=Result[OrderListResponse])
async def list_orders(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    customer_id: Optional[str] = Query(None, description="客户ID（可选）"),
    sales_user_id: Optional[str] = Query(None, description="销售用户ID（可选）"),
    status_code: Optional[str] = Query(None, description="状态代码（可选）"),
    order_number: Optional[str] = Query(None, description="订单号（模糊查询，可选）"),
    title: Optional[str] = Query(None, description="订单标题（模糊查询，可选）"),
    db: AsyncSession = Depends(get_database_session),
):
    """
    查询订单列表
    
    - **page**: 页码（默认: 1）
    - **size**: 每页数量（默认: 20，最大: 100）
    - **customer_id**: 客户ID（可选）
    - **sales_user_id**: 销售用户ID（可选）
    - **status_code**: 状态代码（可选）
    - **order_number**: 订单号（模糊查询，可选）
    - **title**: 订单标题（模糊查询，可选）
    """
    try:
        service = OrderService(db)
        result = await service.list_orders(
            page=page,
            size=size,
            customer_id=customer_id,
            sales_user_id=sales_user_id,
            status_code=status_code,
            order_number=order_number,
            title=title,
        )
        return Result.success(data=result)
    except Exception as e:
        logger.error(f"查询订单列表失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询订单列表失败: {str(e)}"
        )


