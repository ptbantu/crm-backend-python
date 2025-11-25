"""
催款任务数据访问层
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from datetime import date
from order_workflow_service.models.collection_task import CollectionTask
from common.utils.repository import BaseRepository


class CollectionTaskRepository(BaseRepository[CollectionTask]):
    """催款任务仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, CollectionTask)
    
    async def get_by_order_id(self, order_id: str) -> List[CollectionTask]:
        """根据订单ID查询催款任务列表"""
        query = select(CollectionTask).where(
            CollectionTask.order_id == order_id
        ).order_by(desc(CollectionTask.created_at))
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_assigned_user(
        self,
        assigned_to_user_id: str,
        page: int = 1,
        size: int = 20,
        status: Optional[str] = None,
    ) -> Tuple[List[CollectionTask], int]:
        """根据分配用户查询催款任务列表"""
        conditions = [CollectionTask.assigned_to_user_id == assigned_to_user_id]
        
        if status:
            conditions.append(CollectionTask.status == status)
        
        # 查询总数
        count_query = select(func.count(CollectionTask.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = select(CollectionTask).where(and_(*conditions)).order_by(
            desc(CollectionTask.due_date),
            desc(CollectionTask.created_at)
        )
        query = query.offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        tasks = result.scalars().all()
        
        return list(tasks), total
    
    async def get_pending_tasks_by_due_date(self, due_date: date) -> List[CollectionTask]:
        """根据到期日期查询待处理的催款任务"""
        query = select(CollectionTask).where(
            and_(
                CollectionTask.due_date <= due_date,
                CollectionTask.status.in_(["pending", "in_progress"])
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

