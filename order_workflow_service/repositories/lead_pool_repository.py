"""
线索池数据访问层
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from order_workflow_service.models.lead_pool import LeadPool
from common.utils.repository import BaseRepository


class LeadPoolRepository(BaseRepository[LeadPool]):
    """线索池仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, LeadPool)
    
    async def get_by_organization_id(self, organization_id: str, is_active: Optional[bool] = None) -> List[LeadPool]:
        """根据组织ID查询线索池列表"""
        conditions = [LeadPool.organization_id == organization_id]
        if is_active is not None:
            conditions.append(LeadPool.is_active == is_active)
        
        query = select(LeadPool).where(and_(*conditions))
        result = await self.db.execute(query)
        return list(result.scalars().all())

