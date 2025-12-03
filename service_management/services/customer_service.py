"""
客户服务
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from service_management.schemas.customer import (
    CustomerCreateRequest,
    CustomerUpdateRequest,
    CustomerResponse,
    CustomerListResponse,
)
from service_management.repositories.customer_repository import CustomerRepository
from common.models.customer import Customer
from common.models.customer_level import CustomerLevel
from common.models.industry import Industry
from common.models import User
from common.exceptions import BusinessException
from common.utils.logger import get_logger
from service_management.utils.customer_code_generator import generate_customer_code

logger = get_logger(__name__)


class CustomerService:
    """客户服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.customer_repo = CustomerRepository(db)
    
    async def create_customer(
        self, 
        request: CustomerCreateRequest,
        organization_id: str,
        current_user_id: Optional[str] = None
    ) -> CustomerResponse:
        """创建客户"""
        logger.info(f"开始创建客户: name={request.name}, code={request.code}, type={request.customer_type}")
        
        # 如果没有提供编码，自动生成
        code = request.code
        if not code:
            code = await generate_customer_code(
                db=self.db,
                customer_type=request.customer_type,
                organization_id=organization_id
            )
            logger.info(f"自动生成客户编码: code={code}")
        
        # 检查编码是否已存在
        if code:
            existing = await self.customer_repo.get_by_code(code)
            if existing:
                logger.warning(f"客户编码已存在: code={code}")
                raise BusinessException(detail=f"客户编码 {code} 已存在")
        
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
            code=code,
            customer_type=request.customer_type,
            customer_source_type=request.customer_source_type,
            parent_customer_id=request.parent_customer_id,
            owner_user_id=request.owner_user_id or current_user_id,  # 如果没有指定owner，使用当前用户
            agent_user_id=request.agent_user_id,
            agent_id=request.agent_id,
            source_id=request.source_id,
            channel_id=request.channel_id,
            level=request.level,
            industry_id=request.industry_id,
            description=request.description,
            tags=request.tags or [],
            is_locked=request.is_locked,
            id_external=request.id_external,
            customer_requirements=request.customer_requirements,
            organization_id=organization_id,  # 设置组织ID
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
        if request.industry_id is not None:
            customer.industry_id = request.industry_id
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
        organization_id: str,
        current_user_id: Optional[str] = None,
        current_user_roles: Optional[List[str]] = None,
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
        """分页查询客户列表（带权限过滤）"""
        logger.debug(
            f"查询客户列表: page={page}, size={size}, name={name}, code={code}, "
            f"customer_type={customer_type}, customer_source_type={customer_source_type}, "
            f"organization_id={organization_id}, current_user_id={current_user_id}, roles={current_user_roles}"
        )
        
        # 权限过滤逻辑
        # 如果前端明确传递了 owner_user_id（包括 view_type='my' 的情况），使用该值
        # 否则根据角色决定：
        #   - SALES角色：只能看到自己负责的客户
        #   - ADMIN角色：可以看到组织内所有客户（owner_user_id=None 表示不过滤）
        effective_owner_user_id = owner_user_id
        if owner_user_id is None:
            # 如果前端没有传递 owner_user_id，根据角色决定
            if current_user_roles and 'ADMIN' not in current_user_roles:
                # 非ADMIN角色，只能看自己的客户
                if current_user_id:
                    effective_owner_user_id = current_user_id
                else:
                    # 如果没有用户ID，返回空列表
                    logger.warning(f"非ADMIN用户但缺少current_user_id，返回空列表")
                    return CustomerListResponse(
                        items=[],
                        total=0,
                        page=page,
                        size=size,
                    )
            # ADMIN角色且 owner_user_id 为 None，表示查看所有客户（不过滤）
        else:
            # 前端明确传递了 owner_user_id（包括 view_type='my' 的情况），使用该值
            logger.debug(f"使用前端传递的 owner_user_id: {effective_owner_user_id}")
        
        items, total = await self.customer_repo.get_list(
            organization_id=organization_id,  # 必须包含组织ID过滤
            page=page,
            size=size,
            name=name,
            code=code,
            customer_type=customer_type,
            customer_source_type=customer_source_type,
            parent_customer_id=parent_customer_id,
            owner_user_id=effective_owner_user_id,  # 使用有效的owner_user_id
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
        
        # 获取客户等级双语名称
        level_name_zh = None
        level_name_id = None
        if customer.level:
            stmt = select(CustomerLevel).where(CustomerLevel.code == customer.level)
            result = await self.db.execute(stmt)
            level = result.scalar_one_or_none()
            if level:
                level_name_zh = level.name_zh
                level_name_id = level.name_id
        
        # 获取行业双语名称
        industry_name_zh = None
        industry_name_id = None
        if customer.industry_id:
            stmt = select(Industry).where(Industry.id == customer.industry_id)
            result = await self.db.execute(stmt)
            industry = result.scalar_one_or_none()
            if industry:
                industry_name_zh = industry.name_zh
                industry_name_id = industry.name_id
        
        # 获取 owner_user_name
        owner_user_name = None
        if customer.owner_user_id:
            stmt = select(User).where(User.id == customer.owner_user_id)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()
            if user:
                # 优先使用 display_name，如果没有则使用 username
                owner_user_name = user.display_name or user.username
        
        # TODO: 获取 agent_name, source_name, channel_name
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
            owner_user_name=owner_user_name,
            agent_user_id=customer.agent_user_id,
            agent_id=customer.agent_id,
            agent_name=None,  # TODO: 从 organizations 表查询
            source_id=customer.source_id,
            source_name=customer.source_name,
            channel_id=customer.channel_id,
            channel_name=customer.channel_name,
            level=customer.level,
            level_name_zh=level_name_zh,
            level_name_id=level_name_id,
            industry_id=customer.industry_id,
            industry_name_zh=industry_name_zh,
            industry_name_id=industry_name_id,
            description=customer.description,
            tags=customer.tags or [],
            is_locked=customer.is_locked,
            customer_requirements=customer.customer_requirements,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
            last_follow_up_at=customer.last_follow_up_at if hasattr(customer, 'last_follow_up_at') else None,
            next_follow_up_at=customer.next_follow_up_at if hasattr(customer, 'next_follow_up_at') else None,
        )

