"""
客户跟进记录服务
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from sqlalchemy import select, func

from common.models import CustomerFollowUp, Customer
from foundation_service.repositories.customer_follow_up_repository import CustomerFollowUpRepository
from foundation_service.repositories.customer_repository import CustomerRepository
from foundation_service.schemas.customer_follow_up import (
    CustomerFollowUpCreateRequest,
    CustomerFollowUpResponse,
)
from common.utils.logger import get_logger
from common.exceptions import BusinessException
import uuid

logger = get_logger(__name__)


class CustomerFollowUpService:
    """客户跟进记录服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = CustomerFollowUpRepository(db)
        self.customer_repository = CustomerRepository(db)
    
    async def create_follow_up(
        self,
        customer_id: str,
        request: CustomerFollowUpCreateRequest,
        created_by: str,
    ) -> CustomerFollowUpResponse:
        """创建跟进记录"""
        # 验证客户存在
        customer = await self.customer_repository.get_by_id(customer_id)
        if not customer:
            raise BusinessException(detail="客户不存在", status_code=404)
        
        # 创建跟进记录
        follow_up = CustomerFollowUp(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            follow_up_type=request.follow_up_type,
            content=request.content,
            follow_up_date=request.follow_up_date,
            status_before=request.status_before,
            status_after=request.status_after,
            created_by=created_by,
        )
        
        await self.repository.create(follow_up)
        
        # 更新客户的最后跟进时间
        customer.last_follow_up_at = request.follow_up_date
        
        # 如果提供了下次跟进时间，更新客户的 next_follow_up_at
        if request.next_follow_up_at:
            customer.next_follow_up_at = request.next_follow_up_at
        
        await self.db.commit()
        await self.db.refresh(follow_up)
        
        logger.info(f"客户跟进记录创建成功: customer_id={customer_id}, follow_up_id={follow_up.id}")
        
        return CustomerFollowUpResponse.model_validate(follow_up)
    
    async def get_follow_ups_by_customer_id(self, customer_id: str) -> List[CustomerFollowUpResponse]:
        """根据客户ID获取所有跟进记录"""
        follow_ups_with_names = await self.repository.get_by_customer_id(customer_id)
        responses = []
        for follow_up, created_by_name in follow_ups_with_names:
            response_dict = CustomerFollowUpResponse.model_validate(follow_up).model_dump()
            response_dict['created_by_name'] = created_by_name
            responses.append(CustomerFollowUpResponse(**response_dict))
        return responses
    
    async def update_customer_follow_up_times(
        self,
        customer_id: str,
        last_follow_up_at: Optional[datetime] = None,
        next_follow_up_at: Optional[datetime] = None,
    ) -> None:
        """更新客户的跟进时间字段（内部方法）"""
        customer = await self.customer_repository.get_by_id(customer_id)
        if not customer:
            return
        
        if last_follow_up_at is not None:
            customer.last_follow_up_at = last_follow_up_at
        if next_follow_up_at is not None:
            customer.next_follow_up_at = next_follow_up_at
        
        await self.db.commit()

