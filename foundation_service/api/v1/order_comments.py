"""
订单评论 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from foundation_service.dependencies import get_db as get_db
from foundation_service.services.order_comment_service import OrderCommentService
from foundation_service.schemas.order_comment import (
    OrderCommentCreateRequest,
    OrderCommentUpdateRequest,
    OrderCommentResponse,
    OrderCommentListResponse,
)
from foundation_service.schemas.common import LanguageEnum
from common.schemas.response import Result
from common.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("", response_model=Result[OrderCommentResponse], status_code=status.HTTP_201_CREATED)
async def create_comment(
    request: OrderCommentCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    创建订单评论
    
    - **order_id**: 订单ID（必填）
    - **content_zh**: 评论内容（中文）
    - **content_id**: 评论内容（印尼语）
    - **comment_type**: 评论类型（general/internal/customer/system）
    - **is_internal**: 是否内部评论（客户不可见）
    - **is_pinned**: 是否置顶
    - **replied_to_comment_id**: 回复的评论ID（可选）
    """
    try:
        service = OrderCommentService(db)
        result = await service.create_comment(request)
        return Result.success(data=result)
    except Exception as e:
        logger.error(f"创建订单评论失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建订单评论失败: {str(e)}"
        )


@router.get("/{comment_id}", response_model=Result[OrderCommentResponse])
async def get_comment(
    comment_id: str,
    lang: LanguageEnum = Query(LanguageEnum.ZH, description="语言代码：zh（中文）或 id（印尼语）"),
    db: AsyncSession = Depends(get_db),
):
    """
    根据ID查询评论
    
    - **comment_id**: 评论ID
    - **lang**: 语言代码（zh/id），默认 zh
    """
    try:
        service = OrderCommentService(db)
        result = await service.get_comment_by_id(comment_id, lang.value)
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评论不存在"
            )
        
        return Result.success(data=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询评论失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询评论失败: {str(e)}"
        )


@router.put("/{comment_id}", response_model=Result[OrderCommentResponse])
async def update_comment(
    comment_id: str,
    request: OrderCommentUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    更新评论
    
    - **comment_id**: 评论ID
    - 支持更新：评论内容、是否内部、是否置顶
    """
    try:
        service = OrderCommentService(db)
        result = await service.update_comment(comment_id, request)
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评论不存在"
            )
        
        return Result.success(data=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新评论失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新评论失败: {str(e)}"
        )


@router.delete("/{comment_id}", response_model=Result[bool])
async def delete_comment(
    comment_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    删除评论
    
    - **comment_id**: 评论ID
    """
    try:
        service = OrderCommentService(db)
        success = await service.delete_comment(comment_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评论不存在"
            )
        
        return Result.success(data=True)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除评论失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除评论失败: {str(e)}"
        )


@router.get("/order/{order_id}/comments", response_model=Result[OrderCommentListResponse])
async def list_comments(
    order_id: str,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    order_stage_id: Optional[str] = Query(None, description="订单阶段ID（可选）"),
    is_internal: Optional[bool] = Query(None, description="是否内部评论（可选）"),
    lang: LanguageEnum = Query(LanguageEnum.ZH, description="语言代码：zh（中文）或 id（印尼语）"),
    db: AsyncSession = Depends(get_db),
):
    """
    根据订单ID查询评论列表
    
    - **order_id**: 订单ID
    - **page**: 页码（默认1）
    - **size**: 每页数量（默认20，最大100）
    - **order_stage_id**: 订单阶段ID（可选）
    - **is_internal**: 是否内部评论（可选）
    - **lang**: 语言代码（zh/id），默认 zh
    """
    try:
        service = OrderCommentService(db)
        result = await service.list_comments_by_order(
            order_id, page, size, order_stage_id, is_internal, lang.value
        )
        return Result.success(data=result)
    except Exception as e:
        logger.error(f"查询评论列表失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询评论列表失败: {str(e)}"
        )


@router.post("/{comment_id}/reply", response_model=Result[OrderCommentResponse], status_code=status.HTTP_201_CREATED)
async def reply_to_comment(
    comment_id: str,
    request: OrderCommentCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    回复评论
    
    - **comment_id**: 被回复的评论ID
    - **content_zh**: 回复内容（中文）
    - **content_id**: 回复内容（印尼语）
    """
    try:
        service = OrderCommentService(db)
        result = await service.reply_to_comment(comment_id, request)
        return Result.success(data=result)
    except Exception as e:
        logger.error(f"回复评论失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"回复评论失败: {str(e)}"
        )

