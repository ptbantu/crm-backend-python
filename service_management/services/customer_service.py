"""
客户服务
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from service_management.schemas.customer import (
    CustomerCreateRequest,
    CustomerUpdateRequest,
    CustomerResponse,
    CustomerListResponse,
)
from service_management.repositories.customer_repository import CustomerRepository
from service_management.models.customer import Customer
from common.exceptions import BusinessException
from common.utils.logger import get_logger

logger = get_logger(__name__)


class CustomerService:
    """客户服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.customer_repo = CustomerRepository(db)
    
    async def create_customer(self, request: CustomerCreateRequest) -> CustomerResponse:
        """创建客户"""
        logger.info(f"开始创建客户: name={request.name}, code={request.code}, type={request.customer_type}")
        
        # 检查编码是否已存在
        if request.code:
            existing = await self.customer_repo.get_by_code(request.code)
            if existing:
                logger.warning(f"客户编码已存在: code={request.code}")
                raise BusinessException(detail=f"客户编码 {request.code} 已存在")
        
        # 如果指定了父客户，验证父客户是否存在
        if request.parent_customer_id:
            parent = await self.customer_repo.get_by_id(request.parent_customer_id)
            if not parent:
                logger.warning(f"父客户不存在: parent_customer_id={request.parent_customer_id}")
                raise BusinessException(detail="父客户不存在")
            logger.debug(f"验证父客户成功: parent_id={request.parent_customer_id}, parent_name={parent.name}")
        
        # 创建客户
        customer = Customer(
            name=request.name,
            code=request.code,
            customer_type=request.customer_type,
            customer_source_type=request.customer_source_type,
            parent_customer_id=request.parent_customer_id,
            owner_user_id=request.owner_user_id,
            agent_user_id=request.agent_user_id,
            agent_id=request.agent_id,
            source_id=request.source_id,
            channel_id=request.channel_id,
            level=request.level,
            industry=request.industry,
            description=request.description,
            tags=request.tags or [],
            is_locked=request.is_locked,
            id_external=request.id_external,
            customer_requirements=request.customer_requirements,
        )
        customer = await self.customer_repo.create(customer)
        logger.info(f"客户创建成功: id={customer.id}, name={customer.name}, code={customer.code}")
        
        return await self._to_response(customer)
    
    async def get_customer_by_id(self, customer_id: str) -> CustomerResponse:
        """查询客户详情"""
        logger.debug(f"查询客户详情: customer_id={customer_id}")
        customer = await self.customer_repo.get_by_id(customer_id)
        if not customer:
            logger.warning(f"客户不存在: customer_id={customer_id}")
            raise BusinessException(detail="客户不存在", status_code=404)
        
        logger.debug(f"客户查询成功: id={customer.id}, name={customer.name}")
        return await self._to_response(customer)
    
    async def update_customer(self, customer_id: str, request: CustomerUpdateRequest) -> CustomerResponse:
        """更新客户"""
        logger.info(f"开始更新客户: customer_id={customer_id}")
        customer = await self.customer_repo.get_by_id(customer_id)
        if not customer:
            logger.warning(f"客户不存在: customer_id={customer_id}")
            raise BusinessException(detail="客户不存在", status_code=404)
        
        # 如果更新编码，检查是否已存在（排除自身）
        if request.code is not None and request.code != customer.code:
            existing = await self.customer_repo.get_by_code(request.code)
            if existing:
                logger.warning(f"客户编码已存在: code={request.code}, customer_id={customer_id}")
                raise BusinessException(detail=f"客户编码 {request.code} 已存在")
        
        # 如果更新父客户，验证父客户是否存在
        if request.parent_customer_id is not None and request.parent_customer_id != customer.parent_customer_id:
            if request.parent_customer_id:
                parent = await self.customer_repo.get_by_id(request.parent_customer_id)
                if not parent:
                    logger.warning(f"父客户不存在: parent_customer_id={request.parent_customer_id}")
                    raise BusinessException(detail="父客户不存在")
                # 防止循环引用
                if request.parent_customer_id == customer_id:
                    logger.warning(f"检测到循环引用: customer_id={customer_id}, parent_customer_id={request.parent_customer_id}")
                    raise BusinessException(detail="不能将客户设置为自己的父客户")
                logger.debug(f"验证父客户成功: parent_id={request.parent_customer_id}, parent_name={parent.name}")
        
        # 更新字段
        if request.name is not None:
            customer.name = request.name
        if request.code is not None:
            customer.code = request.code
        if request.customer_type is not None:
            customer.customer_type = request.customer_type
        if request.customer_source_type is not None:
            customer.customer_source_type = request.customer_source_type
        if request.parent_customer_id is not None:
            customer.parent_customer_id = request.parent_customer_id
        if request.owner_user_id is not None:
            customer.owner_user_id = request.owner_user_id
        if request.agent_user_id is not None:
            customer.agent_user_id = request.agent_user_id
        if request.agent_id is not None:
            customer.agent_id = request.agent_id
        if request.source_id is not None:
            customer.source_id = request.source_id
        if request.channel_id is not None:
            customer.channel_id = request.channel_id
        if request.level is not None:
            customer.level = request.level
        if request.industry is not None:
            customer.industry = request.industry
        if request.description is not None:
            customer.description = request.description
        if request.tags is not None:
            customer.tags = request.tags
        if request.is_locked is not None:
            customer.is_locked = request.is_locked
        if request.customer_requirements is not None:
            customer.customer_requirements = request.customer_requirements
        
        customer = await self.customer_repo.update(customer)
        logger.info(f"客户更新成功: id={customer.id}, name={customer.name}")
        
        return await self._to_response(customer)
    
    async def delete_customer(self, customer_id: str) -> None:
        """删除客户"""
        logger.info(f"开始删除客户: customer_id={customer_id}")
        customer = await self.customer_repo.get_by_id(customer_id)
        if not customer:
            logger.warning(f"客户不存在: customer_id={customer_id}")
            raise BusinessException(detail="客户不存在", status_code=404)
        
        # TODO: 检查是否有订单或其他关联数据使用此客户
        logger.debug(f"检查客户关联数据: customer_id={customer_id}, name={customer.name}")
        
        await self.customer_repo.delete(customer)
        logger.info(f"客户删除成功: id={customer.id}, name={customer.name}")
    
    async def get_customer_list(
        self,
        page: int = 1,
        size: int = 10,
        name: str = None,
        code: str = None,
        customer_type: str = None,
        customer_source_type: str = None,
        parent_customer_id: str = None,
        owner_user_id: str = None,
        agent_id: str = None,
        source_id: str = None,
        channel_id: str = None,
        is_locked: bool = None,
    ) -> CustomerListResponse:
        """分页查询客户列表"""
        logger.debug(
            f"查询客户列表: page={page}, size={size}, name={name}, code={code}, "
            f"customer_type={customer_type}, customer_source_type={customer_source_type}"
        )
        items, total = await self.customer_repo.get_list(
            page=page,
            size=size,
            name=name,
            code=code,
            customer_type=customer_type,
            customer_source_type=customer_source_type,
            parent_customer_id=parent_customer_id,
            owner_user_id=owner_user_id,
            agent_id=agent_id,
            source_id=source_id,
            channel_id=channel_id,
            is_locked=is_locked,
        )
        
        # 转换为响应格式
        customer_responses = []
        for customer in items:
            customer_responses.append(await self._to_response(customer))
        
        logger.debug(f"客户列表查询成功: total={total}, page={page}, size={size}, returned={len(customer_responses)}")
        return CustomerListResponse(
            items=customer_responses,
            total=total,
            page=page,
            size=size,
        )
    
    async def _to_response(self, customer: Customer) -> CustomerResponse:
        """转换为响应格式"""
        # 获取关联数据
        parent_customer_name = None
        if customer.parent_customer_id:
            parent = await self.customer_repo.get_by_id(customer.parent_customer_id)
            if parent:
                parent_customer_name = parent.name
        
        # TODO: 获取 owner_user_name, agent_name, source_name, channel_name
        # 这些需要从其他表查询，暂时设为 None
        
        return CustomerResponse(
            id=customer.id,
            name=customer.name,
            code=customer.code,
            customer_type=customer.customer_type,
            customer_source_type=customer.customer_source_type,
            parent_customer_id=customer.parent_customer_id,
            parent_customer_name=parent_customer_name,
            owner_user_id=customer.owner_user_id,
            owner_user_name=None,  # TODO: 从 users 表查询
            agent_user_id=customer.agent_user_id,
            agent_id=customer.agent_id,
            agent_name=None,  # TODO: 从 organizations 表查询
            source_id=customer.source_id,
            source_name=customer.source_name,
            channel_id=customer.channel_id,
            channel_name=customer.channel_name,
            level=customer.level,
            industry=customer.industry,
            description=customer.description,
            tags=customer.tags or [],
            is_locked=customer.is_locked,
            customer_requirements=customer.customer_requirements,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
        )

