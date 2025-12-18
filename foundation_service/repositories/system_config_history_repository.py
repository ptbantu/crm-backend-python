"""
系统配置历史数据访问层
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from common.models.system_config_history import SystemConfigHistory
from common.utils.repository import BaseRepository


class SystemConfigHistoryRepository(BaseRepository[SystemConfigHistory]):
    """系统配置历史仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, SystemConfigHistory)
    
    async def get_by_config_id(
        self, 
        config_id: str, 
        page: int = 1, 
        size: int = 20
    ) -> tuple[List[SystemConfigHistory], int]:
        """根据配置ID查询历史记录（分页）"""
        # 查询总数
        count_query = select(SystemConfigHistory).where(
            SystemConfigHistory.config_id == config_id
        )
        total_result = await self.db.execute(
            select(func.count()).select_from(count_query.subquery())
        )
        total = total_result.scalar() or 0
        
        # 分页查询
        query = select(SystemConfigHistory).where(
            SystemConfigHistory.config_id == config_id
        ).order_by(desc(SystemConfigHistory.changed_at)).offset(
            (page - 1) * size
        ).limit(size)
        
        result = await self.db.execute(query)
        records = list(result.scalars().all())
        
        return records, total
    
    async def get_all_by_config_id(self, config_id: str) -> List[SystemConfigHistory]:
        """根据配置ID查询所有历史记录"""
        result = await self.db.execute(
            select(SystemConfigHistory)
            .where(SystemConfigHistory.config_id == config_id)
            .order_by(desc(SystemConfigHistory.changed_at))
        )
        return list(result.scalars().all())
