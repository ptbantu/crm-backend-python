"""
商机阶段历史仓库
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import joinedload
from common.models.opportunity_stage_history import OpportunityStageHistory
from common.models.opportunity_stage_template import OpportunityStageTemplate
from common.utils.repository import BaseRepository


class OpportunityStageHistoryRepository(BaseRepository[OpportunityStageHistory]):
    """商机阶段历史仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, OpportunityStageHistory)
    
    async def get_by_opportunity_id(
        self, 
        opportunity_id: str,
        include_current: bool = True
    ) -> List[OpportunityStageHistory]:
        """根据商机ID查询阶段历史（按进入时间倒序）"""
        query = (
            select(OpportunityStageHistory)
            .options(
                joinedload(OpportunityStageHistory.stage_template),
                joinedload(OpportunityStageHistory.approver)
            )
            .where(OpportunityStageHistory.opportunity_id == opportunity_id)
        )
        if not include_current:
            query = query.where(OpportunityStageHistory.exited_at.isnot(None))
        
        query = query.order_by(desc(OpportunityStageHistory.entered_at))
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_current_stage(self, opportunity_id: str) -> Optional[OpportunityStageHistory]:
        """获取当前阶段历史记录（exited_at为NULL的记录）"""
        query = (
            select(OpportunityStageHistory)
            .options(
                joinedload(OpportunityStageHistory.stage_template),
                joinedload(OpportunityStageHistory.approver)
            )
            .where(OpportunityStageHistory.opportunity_id == opportunity_id)
            .where(OpportunityStageHistory.exited_at.is_(None))
            .order_by(desc(OpportunityStageHistory.entered_at))
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
    
    async def get_by_stage_id(
        self, 
        opportunity_id: str, 
        stage_id: str
    ) -> List[OpportunityStageHistory]:
        """根据阶段ID查询该商机的所有该阶段历史记录"""
        query = (
            select(OpportunityStageHistory)
            .options(
                joinedload(OpportunityStageHistory.stage_template),
                joinedload(OpportunityStageHistory.approver)
            )
            .where(OpportunityStageHistory.opportunity_id == opportunity_id)
            .where(OpportunityStageHistory.stage_id == stage_id)
            .order_by(desc(OpportunityStageHistory.entered_at))
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_pending_approvals(
        self,
        opportunity_id: Optional[str] = None
    ) -> List[OpportunityStageHistory]:
        """获取待审批的阶段历史记录"""
        query = (
            select(OpportunityStageHistory)
            .options(
                joinedload(OpportunityStageHistory.stage_template),
                joinedload(OpportunityStageHistory.opportunity),
                joinedload(OpportunityStageHistory.approver)
            )
            .where(OpportunityStageHistory.requires_approval == True)
            .where(OpportunityStageHistory.approval_status == "pending")
        )
        if opportunity_id:
            query = query.where(OpportunityStageHistory.opportunity_id == opportunity_id)
        
        query = query.order_by(OpportunityStageHistory.entered_at.asc())
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
