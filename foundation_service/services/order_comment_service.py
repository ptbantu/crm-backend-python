"""
订单评论服务
"""
import time
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from common.models import OrderComment
from foundation_service.repositories.order_comment_repository import OrderCommentRepository
from foundation_service.schemas.order_comment import (
    OrderCommentCreateRequest,
    OrderCommentUpdateRequest,
    OrderCommentResponse,
    OrderCommentListResponse,
)
from foundation_service.utils.i18n import get_localized_field
from common.utils.logger import get_logger
from common.exceptions import BusinessException

logger = get_logger(__name__)


class OrderCommentService:
    """订单评论服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = OrderCommentRepository(db)
    
    async def create_comment(
        self,
        request: OrderCommentCreateRequest,
        created_by: Optional[str] = None
    ) -> OrderCommentResponse:
        """
        创建订单评论
        
        Args:
            request: 创建请求
            created_by: 创建人ID
            
        Returns:
            评论响应
        """
        method_name = "create_comment"
        start_time = time.time()
        logger.info(
            f"[Service] {method_name} - 方法调用开始 | "
            f"参数: order_id={request.order_id}, comment_type={request.comment_type}, "
            f"is_internal={request.is_internal}, created_by={created_by}"
        )
        
        try:
            comment = OrderComment(
                order_id=request.order_id,
                order_stage_id=request.order_stage_id,
                comment_type=request.comment_type,
                content_zh=request.content_zh,
                content_id=request.content_id,
                is_internal=request.is_internal,
                is_pinned=request.is_pinned,
                replied_to_comment_id=request.replied_to_comment_id,
                created_by=created_by,
            )
            
            comment = await self.repository.create(comment)
            await self.db.commit()
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"结果: comment_id={comment.id}, order_id={comment.order_id}"
            )
            
            return await self._to_response(comment, lang="zh")
            
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            await self.db.rollback()
            raise
    
    async def get_comment_by_id(
        self,
        comment_id: str,
        lang: str = "zh"
    ) -> Optional[OrderCommentResponse]:
        """
        根据ID查询评论
        
        Args:
            comment_id: 评论ID
            lang: 语言代码（zh/id）
            
        Returns:
            评论响应或None
        """
        method_name = "get_comment_by_id"
        start_time = time.time()
        logger.info(
            f"[Service] {method_name} - 方法调用开始 | "
            f"参数: comment_id={comment_id}, lang={lang}"
        )
        
        try:
            comment = await self.repository.get_by_id(comment_id)
            
            if comment is None:
                elapsed_time = (time.time() - start_time) * 1000
                logger.warning(
                    f"[Service] {method_name} - 评论不存在 | "
                    f"耗时: {elapsed_time:.2f}ms | "
                    f"comment_id={comment_id}"
                )
                return None
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms"
            )
            
            return await self._to_response(comment, lang)
            
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise
    
    async def update_comment(
        self,
        comment_id: str,
        request: OrderCommentUpdateRequest
    ) -> Optional[OrderCommentResponse]:
        """
        更新评论
        
        Args:
            comment_id: 评论ID
            request: 更新请求
            
        Returns:
            更新后的评论响应或None
        """
        method_name = "update_comment"
        start_time = time.time()
        logger.info(
            f"[Service] {method_name} - 方法调用开始 | "
            f"参数: comment_id={comment_id}"
        )
        
        try:
            comment = await self.repository.get_by_id(comment_id)
            
            if comment is None:
                elapsed_time = (time.time() - start_time) * 1000
                logger.warning(
                    f"[Service] {method_name} - 评论不存在 | "
                    f"耗时: {elapsed_time:.2f}ms | "
                    f"comment_id={comment_id}"
                )
                return None
            
            # 更新字段
            update_fields = []
            if request.content_zh is not None:
                comment.content_zh = request.content_zh
                update_fields.append("content_zh")
            if request.content_id is not None:
                comment.content_id = request.content_id
                update_fields.append("content_id")
            if request.is_internal is not None:
                comment.is_internal = request.is_internal
                update_fields.append("is_internal")
            if request.is_pinned is not None:
                comment.is_pinned = request.is_pinned
                update_fields.append("is_pinned")
            
            comment = await self.repository.update(comment)
            await self.db.commit()
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"更新字段: {', '.join(update_fields)}"
            )
            
            return await self._to_response(comment, lang="zh")
            
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            await self.db.rollback()
            raise
    
    async def delete_comment(self, comment_id: str) -> bool:
        """
        删除评论
        
        Args:
            comment_id: 评论ID
            
        Returns:
            是否删除成功
        """
        method_name = "delete_comment"
        start_time = time.time()
        logger.info(
            f"[Service] {method_name} - 方法调用开始 | "
            f"参数: comment_id={comment_id}"
        )
        
        try:
            comment = await self.repository.get_by_id(comment_id)
            
            if comment is None:
                elapsed_time = (time.time() - start_time) * 1000
                logger.warning(
                    f"[Service] {method_name} - 评论不存在 | "
                    f"耗时: {elapsed_time:.2f}ms | "
                    f"comment_id={comment_id}"
                )
                return False
            
            await self.repository.delete(comment)
            await self.db.commit()
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"已删除评论: comment_id={comment_id}"
            )
            
            return True
            
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            await self.db.rollback()
            raise
    
    async def list_comments_by_order(
        self,
        order_id: str,
        page: int = 1,
        size: int = 20,
        order_stage_id: Optional[str] = None,
        is_internal: Optional[bool] = None,
        lang: str = "zh"
    ) -> OrderCommentListResponse:
        """
        根据订单ID查询评论列表
        
        Args:
            order_id: 订单ID
            page: 页码
            size: 每页数量
            order_stage_id: 订单阶段ID（可选）
            is_internal: 是否内部评论（可选）
            lang: 语言代码（zh/id）
            
        Returns:
            评论列表响应
        """
        method_name = "list_comments_by_order"
        start_time = time.time()
        logger.info(
            f"[Service] {method_name} - 方法调用开始 | "
            f"参数: order_id={order_id}, page={page}, size={size}, "
            f"order_stage_id={order_stage_id}, is_internal={is_internal}, lang={lang}"
        )
        
        try:
            comments, total = await self.repository.get_by_order_id(
                order_id, page, size, order_stage_id, is_internal
            )
            
            # 转换为响应列表
            comment_responses = []
            for comment in comments:
                comment_responses.append(await self._to_response(comment, lang))
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"结果: total={total}, comments_count={len(comment_responses)}"
            )
            
            return OrderCommentListResponse(comments=comment_responses, total=total)
            
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise
    
    async def reply_to_comment(
        self,
        comment_id: str,
        request: OrderCommentCreateRequest,
        created_by: Optional[str] = None
    ) -> OrderCommentResponse:
        """
        回复评论
        
        Args:
            comment_id: 被回复的评论ID
            request: 创建请求
            created_by: 创建人ID
            
        Returns:
            回复评论响应
        """
        method_name = "reply_to_comment"
        start_time = time.time()
        logger.info(
            f"[Service] {method_name} - 方法调用开始 | "
            f"参数: comment_id={comment_id}, created_by={created_by}"
        )
        
        try:
            # 检查被回复的评论是否存在
            parent_comment = await self.repository.get_by_id(comment_id)
            if parent_comment is None:
                elapsed_time = (time.time() - start_time) * 1000
                logger.warning(
                    f"[Service] {method_name} - 被回复的评论不存在 | "
                    f"耗时: {elapsed_time:.2f}ms | "
                    f"comment_id={comment_id}"
                )
                raise BusinessException(status_code=404, detail="被回复的评论不存在")
            
            # 创建回复评论
            reply_request = OrderCommentCreateRequest(
                order_id=request.order_id,
                order_stage_id=request.order_stage_id,
                comment_type=request.comment_type,
                content_zh=request.content_zh,
                content_id=request.content_id,
                is_internal=request.is_internal,
                is_pinned=False,  # 回复不能置顶
                replied_to_comment_id=comment_id,  # 设置回复关联
            )
            
            reply = await self.create_comment(reply_request, created_by)
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"结果: reply_id={reply.id}, parent_comment_id={comment_id}"
            )
            
            return reply
            
        except BusinessException:
            raise
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise
    
    async def _to_response(
        self,
        comment: OrderComment,
        lang: str = "zh"
    ) -> OrderCommentResponse:
        """
        将评论模型转换为响应（根据语言返回对应字段）
        
        Args:
            comment: 评论模型
            lang: 语言代码（zh/id）
            
        Returns:
            评论响应
        """
        return OrderCommentResponse(
            id=comment.id,
            order_id=comment.order_id,
            order_stage_id=comment.order_stage_id,
            comment_type=comment.comment_type,
            content=get_localized_field(
                comment.content_zh,
                comment.content_id,
                lang
            ),
            is_internal=comment.is_internal,
            is_pinned=comment.is_pinned,
            replied_to_comment_id=comment.replied_to_comment_id,
            created_by=comment.created_by,
            created_by_name=None,  # TODO: 从 users 表查询用户名
            created_at=comment.created_at.isoformat() if comment.created_at else "",
            updated_at=comment.updated_at.isoformat() if comment.updated_at else "",
        )

