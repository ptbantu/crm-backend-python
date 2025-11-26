"""
线索跟进记录服务
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from common.models import LeadFollowUp
from order_workflow_service.repositories.lead_follow_up_repository import LeadFollowUpRepository
from order_workflow_service.repositories.lead_repository import LeadRepository
from order_workflow_service.schemas.lead_follow_up import (
    LeadFollowUpCreateRequest,
    LeadFollowUpResponse,
)
from common.utils.logger import get_logger
from common.exceptions import BusinessException
import uuid

logger = get_logger(__name__)


class LeadFollowUpService:
    """线索跟进记录服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = LeadFollowUpRepository(db)
        self.lead_repository = LeadRepository(db)
    
    async def create_follow_up(
        self,
        lead_id: str,
        request: LeadFollowUpCreateRequest,
        created_by: str,
    ) -> LeadFollowUpResponse:
        """创建跟进记录"""
        # 验证线索存在（需要organization_id，但这里先简化处理）
        # 注意：这里应该从上下文获取organization_id，暂时先查询
        from sqlalchemy import select
        from common.models import Lead
        result = await self.db.execute(select(Lead).where(Lead.id == lead_id))
        lead = result.scalar_one_or_none()
        if not lead:
            raise BusinessException(detail="线索不存在", status_code=404)
        
        follow_up = LeadFollowUp(
            id=str(uuid.uuid4()),
            lead_id=lead_id,
            follow_up_type=request.follow_up_type,
            content=request.content,
            follow_up_date=request.follow_up_date,
            created_by=created_by,
        )
        
        await self.repository.create(follow_up)
        
        # 更新线索的最后跟进时间
        lead.last_follow_up_at = request.follow_up_date
        await self.db.commit()
        await self.db.refresh(follow_up)
        
        return LeadFollowUpResponse.model_validate(follow_up)
    
    async def get_follow_ups_by_lead_id(self, lead_id: str) -> List[LeadFollowUpResponse]:
        """根据线索ID获取所有跟进记录"""
        follow_ups = await self.repository.get_by_lead_id(lead_id)
        return [LeadFollowUpResponse.model_validate(fu) for fu in follow_ups]

