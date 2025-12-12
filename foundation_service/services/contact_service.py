"""
联系人服务
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from foundation_service.schemas.contact import (
    ContactCreateRequest,
    ContactUpdateRequest,
    ContactResponse,
    ContactListResponse,
)
from foundation_service.repositories.contact_repository import ContactRepository
from foundation_service.repositories.customer_repository import CustomerRepository
from common.models.contact import Contact
from common.exceptions import BusinessException
from common.utils.logger import get_logger

logger = get_logger(__name__)


class ContactService:
    """联系人服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.contact_repo = ContactRepository(db)
        self.customer_repo = CustomerRepository(db)
    
    async def create_contact(self, request: ContactCreateRequest) -> ContactResponse:
        """创建联系人"""
        logger.info(
            f"开始创建联系人: customer_id={request.customer_id}, "
            f"name={request.first_name} {request.last_name}, is_primary={request.is_primary}"
        )
        
        # 验证客户是否存在
        customer = await self.customer_repo.get_by_id(request.customer_id)
        if not customer:
            logger.warning(f"客户不存在: customer_id={request.customer_id}")
            raise BusinessException(detail="客户不存在", status_code=404)
        
        # 如果设置为主要联系人，取消其他主要联系人
        if request.is_primary:
            logger.debug(f"设置主要联系人，取消其他主要联系人: customer_id={request.customer_id}")
            await self.contact_repo.set_primary_contact("", request.customer_id)  # 先取消所有
        
        # 合并 first_name 和 last_name 为 name
        name = f"{request.first_name} {request.last_name}".strip()
        
        # 从客户信息中获取 organization_id 和 owner_user_id（用于数据隔离）
        organization_id = customer.organization_id
        owner_user_id = customer.owner_user_id
        
        # 创建联系人
        contact = Contact(
            customer_id=request.customer_id,
            organization_id=organization_id,
            owner_user_id=owner_user_id,
            name=name,
            email=request.email,
            phone=request.phone,
            mobile=request.mobile,
            wechat_id=request.wechat_id,
            position=request.position,
            department=request.department,
            contact_role=request.contact_role,
            is_primary=request.is_primary,
            is_decision_maker=request.is_decision_maker,
            address=request.address,
            city=request.city,
            province=request.province,
            country=request.country,
            postal_code=request.postal_code,
            preferred_contact_method=request.preferred_contact_method,
            is_active=request.is_active,
            notes=request.notes,
        )
        contact = await self.contact_repo.create(contact)
        
        # 如果设置为主要联系人，确保设置成功
        if request.is_primary:
            await self.contact_repo.set_primary_contact(contact.id, request.customer_id)
            await self.db.refresh(contact)
            logger.debug(f"主要联系人设置成功: contact_id={contact.id}, customer_id={request.customer_id}")
        
        logger.info(f"联系人创建成功: id={contact.id}, customer_id={request.customer_id}, name={contact.name}")
        return await self._to_response(contact)
    
    async def get_contact_by_id(self, contact_id: str) -> ContactResponse:
        """查询联系人详情"""
        logger.debug(f"查询联系人详情: contact_id={contact_id}")
        contact = await self.contact_repo.get_by_id(contact_id)
        if not contact:
            logger.warning(f"联系人不存在: contact_id={contact_id}")
            raise BusinessException(detail="联系人不存在", status_code=404)
        
        logger.debug(f"联系人查询成功: id={contact.id}, name={contact.name}")
        return await self._to_response(contact)
    
    async def update_contact(self, contact_id: str, request: ContactUpdateRequest) -> ContactResponse:
        """更新联系人"""
        logger.info(f"开始更新联系人: contact_id={contact_id}")
        contact = await self.contact_repo.get_by_id(contact_id)
        if not contact:
            logger.warning(f"联系人不存在: contact_id={contact_id}")
            raise BusinessException(detail="联系人不存在", status_code=404)
        
        # 如果设置为主要联系人，取消其他主要联系人
        if request.is_primary is not None and request.is_primary and not contact.is_primary:
            logger.debug(f"设置主要联系人: contact_id={contact_id}, customer_id={contact.customer_id}")
            await self.contact_repo.set_primary_contact(contact_id, contact.customer_id)
        
        # 更新字段
        # 如果 first_name 或 last_name 有更新，合并为 name
        if request.first_name is not None or request.last_name is not None:
            first_name = request.first_name if request.first_name is not None else (contact.name.split(' ', 1)[0] if contact.name else '')
            last_name = request.last_name if request.last_name is not None else (contact.name.split(' ', 1)[1] if ' ' in (contact.name or '') else '')
            contact.name = f"{first_name} {last_name}".strip()
        if request.email is not None:
            contact.email = request.email
        if request.phone is not None:
            contact.phone = request.phone
        if request.mobile is not None:
            contact.mobile = request.mobile
        if request.wechat_id is not None:
            contact.wechat_id = request.wechat_id
        if request.position is not None:
            contact.position = request.position
        if request.department is not None:
            contact.department = request.department
        if request.contact_role is not None:
            contact.contact_role = request.contact_role
        if request.is_primary is not None:
            contact.is_primary = request.is_primary
        if request.is_decision_maker is not None:
            contact.is_decision_maker = request.is_decision_maker
        if request.address is not None:
            contact.address = request.address
        if request.city is not None:
            contact.city = request.city
        if request.province is not None:
            contact.province = request.province
        if request.country is not None:
            contact.country = request.country
        if request.postal_code is not None:
            contact.postal_code = request.postal_code
        if request.preferred_contact_method is not None:
            contact.preferred_contact_method = request.preferred_contact_method
        if request.is_active is not None:
            contact.is_active = request.is_active
        if request.notes is not None:
            contact.notes = request.notes
        
        contact = await self.contact_repo.update(contact)
        logger.info(f"联系人更新成功: id={contact.id}, name={contact.name}")
        
        return await self._to_response(contact)
    
    async def delete_contact(self, contact_id: str) -> None:
        """删除联系人"""
        logger.info(f"开始删除联系人: contact_id={contact_id}")
        contact = await self.contact_repo.get_by_id(contact_id)
        if not contact:
            logger.warning(f"联系人不存在: contact_id={contact_id}")
            raise BusinessException(detail="联系人不存在", status_code=404)
        
        await self.contact_repo.delete(contact)
        logger.info(f"联系人删除成功: id={contact.id}, name={contact.name}, customer_id={contact.customer_id}")
    
    async def get_contact_list_by_customer(
        self,
        customer_id: str,
        page: int = 1,
        size: int = 10,
        is_primary: bool = None,
        is_active: bool = None,
    ) -> ContactListResponse:
        """根据客户ID查询联系人列表"""
        logger.debug(
            f"查询客户联系人列表: customer_id={customer_id}, page={page}, size={size}, "
            f"is_primary={is_primary}, is_active={is_active}"
        )
        
        # 验证客户是否存在
        customer = await self.customer_repo.get_by_id(customer_id)
        if not customer:
            logger.warning(f"客户不存在: customer_id={customer_id}")
            raise BusinessException(detail="客户不存在", status_code=404)
        
        items, total = await self.contact_repo.get_by_customer_id(
            customer_id=customer_id,
            page=page,
            size=size,
            is_primary=is_primary,
            is_active=is_active,
        )
        
        # 转换为响应格式
        contact_responses = []
        for contact in items:
            contact_responses.append(await self._to_response(contact))
        
        logger.debug(f"联系人列表查询成功: customer_id={customer_id}, total={total}, returned={len(contact_responses)}")
        return ContactListResponse(
            items=contact_responses,
            total=total,
            page=page,
            size=size,
        )
    
    async def _to_response(self, contact: Contact) -> ContactResponse:
        """转换为响应格式"""
        # 获取客户名称
        customer_name = None
        if contact.customer_id:
            customer = await self.customer_repo.get_by_id(contact.customer_id)
            if customer:
                customer_name = customer.name
        
        # 从 name 字段解析 first_name 和 last_name（如果 name 包含空格，则分割）
        # 否则将整个 name 作为 first_name
        name_parts = contact.name.split(' ', 1) if contact.name else ['', '']
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        full_name = contact.name
        
        return ContactResponse(
            id=contact.id,
            customer_id=contact.customer_id,
            customer_name=customer_name,
            first_name=first_name,
            last_name=last_name,
            full_name=full_name,
            email=contact.email,
            phone=contact.phone,
            mobile=contact.mobile,
            wechat_id=contact.wechat_id,
            position=contact.position,
            department=contact.department,
            contact_role=contact.contact_role,
            is_primary=contact.is_primary,
            is_decision_maker=contact.is_decision_maker,
            address=contact.address,
            city=contact.city,
            province=contact.province,
            country=contact.country,
            postal_code=contact.postal_code,
            preferred_contact_method=contact.preferred_contact_method,
            is_active=contact.is_active,
            notes=contact.notes,
            created_at=contact.created_at,
            updated_at=contact.updated_at,
        )

