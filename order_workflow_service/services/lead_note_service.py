"""
线索备注服务
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from common.models import LeadNote
from order_workflow_service.repositories.lead_note_repository import LeadNoteRepository
from order_workflow_service.repositories.lead_repository import LeadRepository
from order_workflow_service.schemas.lead_note import (
    LeadNoteCreateRequest,
    LeadNoteResponse,
)
from common.utils.logger import get_logger
from common.exceptions import BusinessException
import uuid

logger = get_logger(__name__)


class LeadNoteService:
    """线索备注服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = LeadNoteRepository(db)
        self.lead_repository = LeadRepository(db)
    
    async def create_note(
        self,
        lead_id: str,
        request: LeadNoteCreateRequest,
        created_by: str,
    ) -> LeadNoteResponse:
        """创建备注"""
        # 验证线索存在（需要organization_id，但这里先简化处理）
        from sqlalchemy import select
        from order_workflow_service.models import Lead
        result = await self.db.execute(select(Lead).where(Lead.id == lead_id))
        lead = result.scalar_one_or_none()
        if not lead:
            raise BusinessException(detail="线索不存在", status_code=404)
        
        note = LeadNote(
            id=str(uuid.uuid4()),
            lead_id=lead_id,
            note_type=request.note_type,
            content=request.content,
            is_important=request.is_important,
            created_by=created_by,
        )
        
        await self.repository.create(note)
        await self.db.commit()
        await self.db.refresh(note)
        
        return LeadNoteResponse.model_validate(note)
    
    async def get_notes_by_lead_id(self, lead_id: str) -> List[LeadNoteResponse]:
        """根据线索ID获取所有备注"""
        notes = await self.repository.get_by_lead_id(lead_id)
        return [LeadNoteResponse.model_validate(note) for note in notes]

