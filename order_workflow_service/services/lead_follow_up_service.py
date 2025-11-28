"""
线索跟进记录服务
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from order_workflow_service.models import LeadFollowUp
from order_workflow_service.repositories.lead_follow_up_repository import LeadFollowUpRepository
from order_workflow_service.repositories.lead_repository import LeadRepository
from order_workflow_service.schemas.lead_follow_up import (
    LeadFollowUpCreateRequest,
    LeadFollowUpResponse,
)
from order_workflow_service.utils.lead_status_validation import (
    validate_status_transition,
    get_status_transition_error_message,
)
from common.utils.logger import get_logger
from common.exceptions import BusinessException
from sqlalchemy.sql import func
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
        # 验证线索存在
        from sqlalchemy import select
        from order_workflow_service.models import Lead
        result = await self.db.execute(select(Lead).where(Lead.id == lead_id))
        lead = result.scalar_one_or_none()
        if not lead:
            raise BusinessException(detail="线索不存在", status_code=404)
        
        # 记录跟进前状态
        status_before = lead.status
        
        # 如果提供了新状态，验证并更新线索状态
        status_after = status_before
        if request.status_after:
            # 验证状态值
            valid_statuses = ['new', 'contacted', 'qualified', 'converted', 'lost']
            if request.status_after not in valid_statuses:
                raise BusinessException(detail="无效的状态值", status_code=400)
            
            # 验证状态流转是否合法（只能向下转化，不能往前转化）
            if not validate_status_transition(status_before, request.status_after):
                error_msg = get_status_transition_error_message(status_before, request.status_after)
                raise BusinessException(
                    detail=error_msg or f"状态流转不合法：不能从 '{status_before}' 转换到 '{request.status_after}'。状态只能向下转化，不能往前转化。",
                    status_code=400
                )
            
            # 更新线索状态
            lead.status = request.status_after
            lead.updated_by = created_by
            lead.updated_at = func.now()
            status_after = request.status_after
        
        # 创建跟进记录
        follow_up = LeadFollowUp(
            id=str(uuid.uuid4()),
            lead_id=lead_id,
            follow_up_type=request.follow_up_type,
            content=request.content,
            follow_up_date=request.follow_up_date,
            status_before=status_before,
            status_after=status_after,
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
        follow_ups_with_names = await self.repository.get_by_lead_id(lead_id)
        responses = []
        for follow_up, created_by_name in follow_ups_with_names:
            response_dict = LeadFollowUpResponse.model_validate(follow_up).model_dump()
            response_dict['created_by_name'] = created_by_name
            responses.append(LeadFollowUpResponse(**response_dict))
        return responses

