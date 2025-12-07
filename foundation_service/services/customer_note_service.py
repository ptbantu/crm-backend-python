"""
客户备注服务
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from common.models import CustomerNote
from foundation_service.repositories.customer_note_repository import CustomerNoteRepository
from foundation_service.repositories.customer_repository import CustomerRepository
from foundation_service.schemas.customer_note import (
    CustomerNoteCreateRequest,
    CustomerNoteResponse,
)
from common.utils.logger import get_logger
from common.exceptions import BusinessException
import uuid

logger = get_logger(__name__)


class CustomerNoteService:
    """客户备注服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = CustomerNoteRepository(db)
        self.customer_repository = CustomerRepository(db)
    
    async def create_note(
        self,
        customer_id: str,
        request: CustomerNoteCreateRequest,
        created_by: str,
    ) -> CustomerNoteResponse:
        """创建备注"""
        # 验证客户存在
        customer = await self.customer_repository.get_by_id(customer_id)
        if not customer:
            raise BusinessException(detail="客户不存在", status_code=404)
        
        note = CustomerNote(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            note_type=request.note_type,
            content=request.content,
            is_important=request.is_important or False,
            created_by=created_by,
        )
        
        await self.repository.create(note)
        await self.db.commit()
        await self.db.refresh(note)
        
        logger.info(f"客户备注创建成功: customer_id={customer_id}, note_id={note.id}")
        
        return CustomerNoteResponse.model_validate(note)
    
    async def get_notes_by_customer_id(self, customer_id: str) -> List[CustomerNoteResponse]:
        """根据客户ID获取所有备注"""
        notes_with_names = await self.repository.get_by_customer_id(customer_id)
        responses = []
        for note, created_by_name in notes_with_names:
            response_dict = CustomerNoteResponse.model_validate(note).model_dump()
            response_dict['created_by_name'] = created_by_name
            responses.append(CustomerNoteResponse(**response_dict))
        return responses
    
    async def get_important_notes_by_customer_id(self, customer_id: str) -> List[CustomerNoteResponse]:
        """获取客户的重要备注"""
        notes = await self.repository.get_important_by_customer_id(customer_id)
        responses = []
        for note in notes:
            responses.append(CustomerNoteResponse.model_validate(note))
        return responses

