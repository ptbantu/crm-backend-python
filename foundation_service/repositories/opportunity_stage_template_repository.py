"""
商机阶段模板仓库
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload
from common.models.opportunity_stage_template import OpportunityStageTemplate
from common.utils.repository import BaseRepository


class OpportunityStageTemplateRepository(BaseRepository[OpportunityStageTemplate]):
    """商机阶段模板仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, OpportunityStageTemplate)
    
    async def get_by_code(self, code: str) -> Optional[OpportunityStageTemplate]:
        """根据代码查询阶段模板"""
        query = (
            select(OpportunityStageTemplate)
            .where(OpportunityStageTemplate.code == code)
            .where(OpportunityStageTemplate.is_active == True)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_order(self, stage_order: int) -> Optional[OpportunityStageTemplate]:
        """根据顺序查询阶段模板"""
        query = (
            select(OpportunityStageTemplate)
            .where(OpportunityStageTemplate.stage_order == stage_order)
            .where(OpportunityStageTemplate.is_active == True)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all_active(self) -> List[OpportunityStageTemplate]:
        """获取所有启用的阶段模板（按顺序排序）"""
        query = (
            select(OpportunityStageTemplate)
            .where(OpportunityStageTemplate.is_active == True)
            .order_by(OpportunityStageTemplate.stage_order.asc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_next_stage(self, current_stage_order: int) -> Optional[OpportunityStageTemplate]:
        """获取下一个阶段模板"""
        query = (
            select(OpportunityStageTemplate)
            .where(OpportunityStageTemplate.stage_order > current_stage_order)
            .where(OpportunityStageTemplate.is_active == True)
            .order_by(OpportunityStageTemplate.stage_order.asc())
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_previous_stage(self, current_stage_order: int) -> Optional[OpportunityStageTemplate]:
        """获取上一个阶段模板"""
        query = (
            select(OpportunityStageTemplate)
            .where(OpportunityStageTemplate.stage_order < current_stage_order)
            .where(OpportunityStageTemplate.is_active == True)
            .order_by(OpportunityStageTemplate.stage_order.desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
