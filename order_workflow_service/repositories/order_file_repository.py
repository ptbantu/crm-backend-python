"""
订单文件数据访问层
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from order_workflow_service.models.order_file import OrderFile
from common.utils.repository import BaseRepository


class OrderFileRepository(BaseRepository[OrderFile]):
    """订单文件仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, OrderFile)
    
    async def get_by_order_id(
        self,
        order_id: str,
        page: int = 1,
        size: int = 50,
        order_item_id: Optional[str] = None,
        order_stage_id: Optional[str] = None,
        file_category: Optional[str] = None
    ) -> Tuple[List[OrderFile], int]:
        """根据订单ID查询文件列表"""
        # 构建查询条件
        conditions = [OrderFile.order_id == order_id]
        
        if order_item_id:
            conditions.append(OrderFile.order_item_id == order_item_id)
        if order_stage_id:
            conditions.append(OrderFile.order_stage_id == order_stage_id)
        if file_category:
            conditions.append(OrderFile.file_category == file_category)
        
        # 查询总数
        count_query = select(func.count(OrderFile.id)).where(*conditions)
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询列表（按创建时间倒序）
        query = (
            select(OrderFile)
            .where(*conditions)
            .order_by(desc(OrderFile.created_at))
            .offset((page - 1) * size)
            .limit(size)
        )
        result = await self.db.execute(query)
        files = result.scalars().all()
        
        return list(files), total
    
    async def get_by_order_id_all(
        self,
        order_id: str,
        order_item_id: Optional[str] = None,
        order_stage_id: Optional[str] = None
    ) -> List[OrderFile]:
        """根据订单ID查询所有文件（不分页）"""
        conditions = [OrderFile.order_id == order_id]
        
        if order_item_id:
            conditions.append(OrderFile.order_item_id == order_item_id)
        if order_stage_id:
            conditions.append(OrderFile.order_stage_id == order_stage_id)
        
        query = (
            select(OrderFile)
            .where(*conditions)
            .order_by(desc(OrderFile.created_at))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

