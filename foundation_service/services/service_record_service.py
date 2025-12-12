"""
服务记录服务
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from foundation_service.schemas.service_record import (
    ServiceRecordCreateRequest,
    ServiceRecordUpdateRequest,
    ServiceRecordResponse,
    ServiceRecordListResponse,
)
from foundation_service.repositories.service_record_repository import ServiceRecordRepository
from foundation_service.repositories.customer_repository import CustomerRepository
from foundation_service.repositories.contact_repository import ContactRepository
from common.models.service_record import ServiceRecord
from common.exceptions import BusinessException
from common.utils.logger import get_logger

logger = get_logger(__name__)


class ServiceRecordService:
    """服务记录服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.service_record_repo = ServiceRecordRepository(db)
        self.customer_repo = CustomerRepository(db)
        self.contact_repo = ContactRepository(db)
    
    async def create_service_record(self, request: ServiceRecordCreateRequest) -> ServiceRecordResponse:
        """创建服务记录"""
        logger.info(
            f"开始创建服务记录: customer_id={request.customer_id}, "
            f"service_name={request.service_name}, status={request.status}, priority={request.priority}"
        )
        
        # 验证客户是否存在
        customer = await self.customer_repo.get_by_id(request.customer_id)
        if not customer:
            logger.warning(f"客户不存在: customer_id={request.customer_id}")
            raise BusinessException(detail="客户不存在", status_code=404)
        
        # 如果指定了接单人员，验证联系人是否存在
        if request.contact_id:
            contact = await self.contact_repo.get_by_id(request.contact_id)
            if not contact:
                logger.warning(f"接单人员不存在: contact_id={request.contact_id}")
                raise BusinessException(detail="接单人员不存在", status_code=404)
            if contact.customer_id != request.customer_id:
                logger.warning(
                    f"接单人员不属于该客户: contact_id={request.contact_id}, "
                    f"contact.customer_id={contact.customer_id}, service_record.customer_id={request.customer_id}"
                )
                raise BusinessException(detail="接单人员不属于该客户", status_code=400)
            logger.debug(f"验证接单人员成功: contact_id={request.contact_id}, contact_name={contact.full_name}")
        
        # 如果指定了推荐客户，验证推荐客户是否存在
        if request.referral_customer_id:
            referral_customer = await self.customer_repo.get_by_id(request.referral_customer_id)
            if not referral_customer:
                logger.warning(f"推荐客户不存在: referral_customer_id={request.referral_customer_id}")
                raise BusinessException(detail="推荐客户不存在", status_code=404)
            logger.debug(f"验证推荐客户成功: referral_customer_id={request.referral_customer_id}, name={referral_customer.name}")
        
        # 创建服务记录
        service_record = ServiceRecord(
            customer_id=request.customer_id,
            customer_name=customer.name,  # 冗余字段
            service_type_id=request.service_type_id,
            product_id=request.product_id,
            service_name=request.service_name,
            service_description=request.service_description,
            service_code=request.service_code,
            contact_id=request.contact_id,
            sales_user_id=request.sales_user_id,
            referral_customer_id=request.referral_customer_id,
            status=request.status,
            priority=request.priority,
            status_description=request.status_description,
            expected_start_date=request.expected_start_date,
            expected_completion_date=request.expected_completion_date,
            deadline=request.deadline,
            estimated_price=request.estimated_price,
            final_price=request.final_price,
            currency_code=request.currency_code,
            price_notes=request.price_notes,
            quantity=request.quantity,
            unit=request.unit,
            requirements=request.requirements,
            customer_requirements=request.customer_requirements,
            internal_notes=request.internal_notes,
            customer_notes=request.customer_notes,
            required_documents=request.required_documents,
            attachments=request.attachments or [],
            next_follow_up_at=request.next_follow_up_at,
            follow_up_notes=request.follow_up_notes,
            tags=request.tags or [],
            id_external=request.id_external,
        )
        
        # 填充冗余字段
        if request.contact_id:
            contact = await self.contact_repo.get_by_id(request.contact_id)
            if contact:
                service_record.contact_name = contact.full_name or f"{contact.first_name} {contact.last_name}"
        
        service_record = await self.service_record_repo.create(service_record)
        logger.info(
            f"服务记录创建成功: id={service_record.id}, customer_id={request.customer_id}, "
            f"service_name={service_record.service_name}, status={service_record.status}"
        )
        
        return await self._to_response(service_record)
    
    async def get_service_record_by_id(self, service_record_id: str) -> ServiceRecordResponse:
        """查询服务记录详情"""
        logger.debug(f"查询服务记录详情: service_record_id={service_record_id}")
        service_record = await self.service_record_repo.get_by_id(service_record_id)
        if not service_record:
            logger.warning(f"服务记录不存在: service_record_id={service_record_id}")
            raise BusinessException(detail="服务记录不存在", status_code=404)
        
        logger.debug(f"服务记录查询成功: id={service_record.id}, customer_id={service_record.customer_id}")
        return await self._to_response(service_record)
    
    async def update_service_record(self, service_record_id: str, request: ServiceRecordUpdateRequest) -> ServiceRecordResponse:
        """更新服务记录"""
        logger.info(f"开始更新服务记录: service_record_id={service_record_id}, status={request.status}")
        service_record = await self.service_record_repo.get_by_id(service_record_id)
        if not service_record:
            logger.warning(f"服务记录不存在: service_record_id={service_record_id}")
            raise BusinessException(detail="服务记录不存在", status_code=404)
        
        # 记录状态变更
        if request.status is not None and request.status != service_record.status:
            logger.info(
                f"服务记录状态变更: id={service_record_id}, "
                f"old_status={service_record.status}, new_status={request.status}"
            )
        
        # 如果更新接单人员，验证联系人是否存在
        if request.contact_id is not None and request.contact_id != service_record.contact_id:
            if request.contact_id:
                contact = await self.contact_repo.get_by_id(request.contact_id)
                if not contact:
                    logger.warning(f"接单人员不存在: contact_id={request.contact_id}")
                    raise BusinessException(detail="接单人员不存在", status_code=404)
                if contact.customer_id != service_record.customer_id:
                    logger.warning(
                        f"接单人员不属于该客户: contact_id={request.contact_id}, "
                        f"contact.customer_id={contact.customer_id}, service_record.customer_id={service_record.customer_id}"
                    )
                    raise BusinessException(detail="接单人员不属于该客户", status_code=400)
                service_record.contact_name = contact.full_name or f"{contact.first_name} {contact.last_name}"
                logger.debug(f"更新接单人员: contact_id={request.contact_id}, contact_name={service_record.contact_name}")
            else:
                service_record.contact_id = None
                service_record.contact_name = None
                logger.debug(f"清除接单人员: service_record_id={service_record_id}")
        
        # 如果更新推荐客户，验证推荐客户是否存在
        if request.referral_customer_id is not None and request.referral_customer_id != service_record.referral_customer_id:
            if request.referral_customer_id:
                referral_customer = await self.customer_repo.get_by_id(request.referral_customer_id)
                if not referral_customer:
                    raise BusinessException(detail="推荐客户不存在", status_code=404)
                service_record.referral_customer_name = referral_customer.name
            else:
                service_record.referral_customer_id = None
                service_record.referral_customer_name = None
        
        # 更新字段
        if request.service_type_id is not None:
            service_record.service_type_id = request.service_type_id
        if request.product_id is not None:
            service_record.product_id = request.product_id
        if request.service_name is not None:
            service_record.service_name = request.service_name
        if request.service_description is not None:
            service_record.service_description = request.service_description
        if request.service_code is not None:
            service_record.service_code = request.service_code
        if request.sales_user_id is not None:
            service_record.sales_user_id = request.sales_user_id
        if request.status is not None:
            service_record.status = request.status
        if request.priority is not None:
            service_record.priority = request.priority
        if request.status_description is not None:
            service_record.status_description = request.status_description
        if request.expected_start_date is not None:
            service_record.expected_start_date = request.expected_start_date
        if request.expected_completion_date is not None:
            service_record.expected_completion_date = request.expected_completion_date
        if request.actual_start_date is not None:
            service_record.actual_start_date = request.actual_start_date
        if request.actual_completion_date is not None:
            service_record.actual_completion_date = request.actual_completion_date
        if request.deadline is not None:
            service_record.deadline = request.deadline
        if request.estimated_price is not None:
            service_record.estimated_price = request.estimated_price
        if request.final_price is not None:
            service_record.final_price = request.final_price
        if request.currency_code is not None:
            service_record.currency_code = request.currency_code
        if request.price_notes is not None:
            service_record.price_notes = request.price_notes
        if request.quantity is not None:
            service_record.quantity = request.quantity
        if request.unit is not None:
            service_record.unit = request.unit
        if request.requirements is not None:
            service_record.requirements = request.requirements
        if request.customer_requirements is not None:
            service_record.customer_requirements = request.customer_requirements
        if request.internal_notes is not None:
            service_record.internal_notes = request.internal_notes
        if request.customer_notes is not None:
            service_record.customer_notes = request.customer_notes
        if request.required_documents is not None:
            service_record.required_documents = request.required_documents
        if request.attachments is not None:
            service_record.attachments = request.attachments
        if request.last_follow_up_at is not None:
            service_record.last_follow_up_at = request.last_follow_up_at
        if request.next_follow_up_at is not None:
            service_record.next_follow_up_at = request.next_follow_up_at
        if request.follow_up_notes is not None:
            service_record.follow_up_notes = request.follow_up_notes
        if request.tags is not None:
            service_record.tags = request.tags
        
        service_record = await self.service_record_repo.update(service_record)
        
        return await self._to_response(service_record)
    
    async def delete_service_record(self, service_record_id: str) -> None:
        """删除服务记录"""
        service_record = await self.service_record_repo.get_by_id(service_record_id)
        if not service_record:
            raise BusinessException(detail="服务记录不存在", status_code=404)
        
        # TODO: 检查是否有订单或其他关联数据使用此服务记录
        
        await self.service_record_repo.delete(service_record)
    
    async def get_service_record_list(
        self,
        page: int = 1,
        size: int = 10,
        customer_id: str = None,
        service_type_id: str = None,
        product_id: str = None,
        contact_id: str = None,
        sales_user_id: str = None,
        status: str = None,
        priority: str = None,
        referral_customer_id: str = None,
    ) -> ServiceRecordListResponse:
        """分页查询服务记录列表"""
        items, total = await self.service_record_repo.get_list(
            page=page,
            size=size,
            customer_id=customer_id,
            service_type_id=service_type_id,
            product_id=product_id,
            contact_id=contact_id,
            sales_user_id=sales_user_id,
            status=status,
            priority=priority,
            referral_customer_id=referral_customer_id,
        )
        
        # 转换为响应格式
        service_record_responses = []
        for service_record in items:
            service_record_responses.append(await self._to_response(service_record))
        
        return ServiceRecordListResponse(
            items=service_record_responses,
            total=total,
            page=page,
            size=size,
        )
    
    async def _to_response(self, service_record: ServiceRecord) -> ServiceRecordResponse:
        """转换为响应格式"""
        return ServiceRecordResponse(
            id=service_record.id,
            customer_id=service_record.customer_id,
            customer_name=service_record.customer_name,
            service_type_id=service_record.service_type_id,
            service_type_name=service_record.service_type_name,
            product_id=service_record.product_id,
            product_name=service_record.product_name,
            product_code=service_record.product_code,
            service_name=service_record.service_name,
            service_description=service_record.service_description,
            service_code=service_record.service_code,
            contact_id=service_record.contact_id,
            contact_name=service_record.contact_name,
            sales_user_id=service_record.sales_user_id,
            sales_username=service_record.sales_username,
            referral_customer_id=service_record.referral_customer_id,
            referral_customer_name=service_record.referral_customer_name,
            status=service_record.status,
            priority=service_record.priority,
            status_description=service_record.status_description,
            expected_start_date=service_record.expected_start_date,
            expected_completion_date=service_record.expected_completion_date,
            actual_start_date=service_record.actual_start_date,
            actual_completion_date=service_record.actual_completion_date,
            deadline=service_record.deadline,
            estimated_price=service_record.estimated_price,
            final_price=service_record.final_price,
            currency_code=service_record.currency_code,
            price_notes=service_record.price_notes,
            quantity=service_record.quantity,
            unit=service_record.unit,
            requirements=service_record.requirements,
            customer_requirements=service_record.customer_requirements,
            internal_notes=service_record.internal_notes,
            customer_notes=service_record.customer_notes,
            required_documents=service_record.required_documents,
            attachments=service_record.attachments or [],
            last_follow_up_at=service_record.last_follow_up_at,
            next_follow_up_at=service_record.next_follow_up_at,
            follow_up_notes=service_record.follow_up_notes,
            tags=service_record.tags or [],
            created_at=service_record.created_at,
            updated_at=service_record.updated_at,
        )

