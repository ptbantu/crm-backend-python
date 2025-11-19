"""
订单评论数据访问层
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from order_workflow_service.models.order_comment import OrderComment
from common.utils.repository import BaseRepository


class OrderCommentRepository(BaseRepository[OrderComment]):
    """订单评论仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, OrderComment)
    
    async def get_by_order_id(
        self,
        order_id: str,
        page: int = 1,
        size: int = 20,
        order_stage_id: Optional[str] = None,
        is_internal: Optional[bool] = None
    ) -> Tuple[List[OrderComment], int]:
        """根据订单ID查询评论列表"""
        # 构建查询条件
        conditions = [OrderComment.order_id == order_id]
        
        if order_stage_id:
            conditions.append(OrderComment.order_stage_id == order_stage_id)
        if is_internal is not None:
            conditions.append(OrderComment.is_internal == is_internal)
        
        # 查询总数
        count_query = select(func.count(OrderComment.id)).where(*conditions)
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询列表（置顶的在前，然后按创建时间倒序）
        query = (
            select(OrderComment)
            .where(*conditions)
            .order_by(desc(OrderComment.is_pinned), desc(OrderComment.created_at))
            .offset((page - 1) * size)
            .limit(size)
        )
        result = await self.db.execute(query)
        comments = result.scalars().all()
        
        return list(comments), total
    
    async def get_replies(self, comment_id: str) -> List[OrderComment]:
        """获取评论的回复列表"""
        query = (
            select(OrderComment)
            .where(OrderComment.replied_to_comment_id == comment_id)
            .order_by(OrderComment.created_at)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

