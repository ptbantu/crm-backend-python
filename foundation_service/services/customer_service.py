"""
客户服务
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from foundation_service.schemas.customer import (
    CustomerCreateRequest,
    CustomerUpdateRequest,
    CustomerResponse,
    CustomerListResponse,
)
from foundation_service.schemas.customer_tianyancha import (
    TianyanchaSearchRequest,
    TianyanchaLinkRequest,
    TianyanchaCreateContactRequest,
    TianyanchaRefreshRequest,
    TianyanchaDataResponse,
    TianyanchaLinkResponse,
    TianyanchaUnlinkResponse,
    TianyanchaRefreshResponse,
)
from foundation_service.schemas.contact import ContactCreateRequest, ContactResponse
from foundation_service.repositories.customer_repository import CustomerRepository
from common.models.customer import Customer
from common.models.customer_level import CustomerLevel
from common.models.industry import Industry
from common.models.customer_source import CustomerSource
from common.models.customer_channel import CustomerChannel
from common.models.organization import Organization
from common.models import User
from common.exceptions import BusinessException
from common.utils.logger import get_logger
from foundation_service.utils.customer_code_generator import generate_customer_code

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
        
        # 创建客户（ID由数据库自增生成）
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
        
        # 获取 source_name（客户来源名称）
        source_name = None
        if customer.source_id:
            # 只选择实际存在的列，避免查询不存在的 name_zh 和 name_id 字段
            source_query = select(
                CustomerSource.id,
                CustomerSource.code,
                CustomerSource.name,
                CustomerSource.description,
                CustomerSource.display_order,
                CustomerSource.is_active
            ).where(CustomerSource.id == customer.source_id)
            source_result = await self.db.execute(source_query)
            source_row = source_result.first()
            if source_row:
                # 使用 name 字段（数据库表中实际存在的字段）
                source_name = source_row.name
        
        # 获取 channel_name（客户渠道名称）
        channel_name = None
        if customer.channel_id:
            channel_query = select(CustomerChannel).where(CustomerChannel.id == customer.channel_id)
            channel_result = await self.db.execute(channel_query)
            channel = channel_result.scalar_one_or_none()
            if channel:
                channel_name = channel.name
        
        # 获取 agent_name（渠道组织名称）
        agent_name = None
        if customer.agent_id:
            agent_query = select(Organization).where(Organization.id == customer.agent_id)
            agent_result = await self.db.execute(agent_query)
            agent = agent_result.scalar_one_or_none()
            if agent:
                agent_name = agent.name
        
        return CustomerResponse(
            id=str(customer.id),
            name=customer.name,
            code=customer.code,
            customer_type=customer.customer_type,
            customer_source_type=customer.customer_source_type,
            parent_customer_id=str(customer.parent_customer_id) if customer.parent_customer_id is not None else None,
            parent_customer_name=parent_customer_name,
            owner_user_id=customer.owner_user_id,
            owner_user_name=owner_user_name,
            agent_user_id=customer.agent_user_id,
            agent_id=customer.agent_id,
            agent_name=agent_name,
            source_id=customer.source_id,
            source_name=source_name,
            channel_id=customer.channel_id,
            channel_name=channel_name,
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
            tianyancha_data=customer.tianyancha_data if hasattr(customer, 'tianyancha_data') else None,
            tianyancha_synced_at=customer.tianyancha_synced_at if hasattr(customer, 'tianyancha_synced_at') else None,
        )

    # ==================== 天眼查关联功能 ====================

    async def search_tianyancha_enterprises(
        self,
        request: TianyanchaSearchRequest
    ) -> Dict[str, Any]:
        """
        搜索天眼查企业（第一阶段：返回提示信息）

        Args:
            request: 搜索请求

        Returns:
            搜索结果（第一阶段返回空数据和提示）
        """
        logger.info(f"搜索天眼查企业: keyword={request.keyword}, page={request.page_num}, size={request.page_size}")

        # 第一阶段：天眼查API暂不可用，返回提示
        logger.warning("天眼查API暂不可用，等待代理接口")
        return {
            "total": 0,
            "items": [],
            "page_num": request.page_num,
            "page_size": request.page_size,
            "message": "天眼查API暂不可用，请稍后再试。第二阶段将集成代理接口。"
        }

    async def link_tianyancha_enterprise(
        self,
        customer_id: str,
        request: TianyanchaLinkRequest,
        current_user_id: Optional[str] = None
    ) -> TianyanchaLinkResponse:
        """
        关联天眼查企业到客户

        Args:
            customer_id: 客户ID
            request: 关联请求
            current_user_id: 当前用户ID

        Returns:
            关联响应
        """
        logger.info(
            f"关联天眼查企业: customer_id={customer_id}, enterprise_id={request.enterprise_id}, "
            f"update_info={request.update_customer_info}, create_contact={request.create_contact}"
        )

        # 获取客户
        customer = await self.customer_repo.get_by_id(customer_id)
        if not customer:
            logger.warning(f"客户不存在: customer_id={customer_id}")
            raise BusinessException(detail="客户不存在", status_code=404)

        # 第一阶段：使用前端传入的企业数据
        if not request.enterprise_data:
            raise BusinessException(
                detail="第一阶段需要手动传入企业数据（enterprise_data字段），第二阶段将自动从天眼查获取"
            )

        enterprise_data = request.enterprise_data
        logger.info(f"使用手动传入的企业数据: name={enterprise_data.get('name')}")

        # 更新客户的天眼查关联字段
        customer.linked_module = "tianyancha"
        customer.linked_id_external = request.enterprise_id
        customer.tianyancha_data = enterprise_data
        customer.tianyancha_synced_at = datetime.now()
        customer.enrich_status = "enriched"

        updated_fields = ["linked_module", "linked_id_external", "tianyancha_data", "tianyancha_synced_at", "enrich_status"]

        # 可选：更新客户基础信息
        if request.update_customer_info and enterprise_data.get("name"):
            # 只在客户名称为空或者明确要求更新时才更新
            if not customer.name or customer.name.strip() == "":
                customer.name = enterprise_data.get("name")
                updated_fields.append("name")

            # 更新描述（追加企业信息）
            enterprise_desc = f"企业类型：{enterprise_data.get('company_type', '未知')}\n"
            enterprise_desc += f"注册资本：{enterprise_data.get('registered_capital', '未知')}\n"
            enterprise_desc += f"成立日期：{enterprise_data.get('establishment_date', '未知')}\n"
            enterprise_desc += f"经营状态：{enterprise_data.get('business_status', '未知')}"

            if customer.description:
                customer.description = f"{customer.description}\n\n【天眼查企业信息】\n{enterprise_desc}"
            else:
                customer.description = f"【天眼查企业信息】\n{enterprise_desc}"
            updated_fields.append("description")

        # 保存客户更新
        customer = await self.customer_repo.update(customer)
        logger.info(f"客户天眼查关联成功: customer_id={customer_id}, enterprise_id={request.enterprise_id}")

        # 转换客户为响应格式
        customer_response = await self._to_response(customer)

        # 可选：自动创建法人联系人
        contact_response = None
        if request.create_contact and enterprise_data.get("legal_representative"):
            try:
                from foundation_service.services.contact_service import ContactService
                contact_service = ContactService(self.db)

                legal_rep_name = enterprise_data.get("legal_representative")
                # 解析中文姓名（通常最后一个字是名，前面是姓）
                if len(legal_rep_name) >= 2:
                    last_name = legal_rep_name[0]  # 第一个字作为姓
                    first_name = legal_rep_name[1:]  # 其余作为名
                else:
                    last_name = legal_rep_name
                    first_name = ""

                contact_create_request = ContactCreateRequest(
                    customer_id=int(customer_id),
                    first_name=first_name,
                    last_name=last_name,
                    position="法定代表人",
                    is_primary=True,
                    is_decision_maker=True,
                    is_active=True,
                    notes="来自天眼查数据自动创建"
                )

                contact_response = await contact_service.create_contact(contact_create_request)
                logger.info(f"自动创建法人联系人成功: contact_id={contact_response.id}, name={legal_rep_name}")
            except Exception as e:
                logger.warning(f"创建法人联系人失败: {str(e)}", exc_info=True)
                # 不影响主流程，继续

        return TianyanchaLinkResponse(
            success=True,
            message="关联成功",
            customer=customer_response.model_dump(),
            contact=contact_response.model_dump() if contact_response else None,
            updated_fields=updated_fields
        )

    async def get_tianyancha_data(
        self,
        customer_id: str
    ) -> TianyanchaDataResponse:
        """
        获取客户的天眼查数据

        Args:
            customer_id: 客户ID

        Returns:
            天眼查数据响应
        """
        logger.debug(f"获取客户天眼查数据: customer_id={customer_id}")

        customer = await self.customer_repo.get_by_id(customer_id)
        if not customer:
            logger.warning(f"客户不存在: customer_id={customer_id}")
            raise BusinessException(detail="客户不存在", status_code=404)

        is_linked = (
            customer.linked_module == "tianyancha" and
            customer.linked_id_external is not None
        )

        return TianyanchaDataResponse(
            is_linked=is_linked,
            enterprise_id=customer.linked_id_external if is_linked else None,
            enterprise_data=customer.tianyancha_data if is_linked else None,
            synced_at=customer.tianyancha_synced_at if is_linked else None
        )

    async def unlink_tianyancha_enterprise(
        self,
        customer_id: str
    ) -> TianyanchaUnlinkResponse:
        """
        解除客户的天眼查关联

        Args:
            customer_id: 客户ID

        Returns:
            解除关联响应
        """
        logger.info(f"解除天眼查关联: customer_id={customer_id}")

        customer = await self.customer_repo.get_by_id(customer_id)
        if not customer:
            logger.warning(f"客户不存在: customer_id={customer_id}")
            raise BusinessException(detail="客户不存在", status_code=404)

        # 清除天眼查相关字段
        customer.linked_module = None
        customer.linked_id_external = None
        customer.tianyancha_data = None
        customer.tianyancha_synced_at = None
        customer.enrich_status = None

        await self.customer_repo.update(customer)
        logger.info(f"天眼查关联解除成功: customer_id={customer_id}")

        return TianyanchaUnlinkResponse(
            success=True,
            message="解除关联成功"
        )

    async def refresh_tianyancha_data(
        self,
        customer_id: str,
        request: TianyanchaRefreshRequest
    ) -> TianyanchaRefreshResponse:
        """
        刷新客户的天眼查数据

        Args:
            customer_id: 客户ID
            request: 刷新请求

        Returns:
            刷新响应
        """
        logger.info(f"刷新天眼查数据: customer_id={customer_id}, force={request.force}")

        customer = await self.customer_repo.get_by_id(customer_id)
        if not customer:
            logger.warning(f"客户不存在: customer_id={customer_id}")
            raise BusinessException(detail="客户不存在", status_code=404)

        # 检查是否已关联
        if customer.linked_module != "tianyancha" or not customer.linked_id_external:
            raise BusinessException(detail="客户尚未关联天眼查企业")

        # 检查24小时缓存
        if not request.force and customer.tianyancha_synced_at:
            time_diff = datetime.now() - customer.tianyancha_synced_at
            if time_diff < timedelta(hours=24):
                logger.info(f"天眼查数据在24小时内已同步，跳过刷新: synced_at={customer.tianyancha_synced_at}")
                return TianyanchaRefreshResponse(
                    success=True,
                    message=f"数据已是最新（上次同步: {customer.tianyancha_synced_at.strftime('%Y-%m-%d %H:%M:%S')}）",
                    updated=False,
                    changed_fields=None,
                    enterprise_data=customer.tianyancha_data
                )

        # 第一阶段：暂不调用API，返回提示
        logger.warning("天眼查API暂不可用，无法刷新数据")
        return TianyanchaRefreshResponse(
            success=False,
            message="天眼查API暂不可用，等待第二阶段集成代理接口",
            updated=False,
            changed_fields=None,
            enterprise_data=customer.tianyancha_data
        )

    async def create_contact_from_tianyancha(
        self,
        customer_id: str,
        request: TianyanchaCreateContactRequest
    ) -> ContactResponse:
        """
        从天眼查数据创建联系人

        Args:
            customer_id: 客户ID
            request: 创建联系人请求

        Returns:
            联系人响应
        """
        logger.info(
            f"从天眼查数据创建联系人: customer_id={customer_id}, "
            f"type={request.contact_type}, shareholder={request.shareholder_name}"
        )

        customer = await self.customer_repo.get_by_id(customer_id)
        if not customer:
            logger.warning(f"客户不存在: customer_id={customer_id}")
            raise BusinessException(detail="客户不存在", status_code=404)

        # 检查是否已关联天眼查
        if not customer.tianyancha_data:
            raise BusinessException(detail="客户尚未关联天眼查数据")

        tianyancha_data = customer.tianyancha_data

        # 根据类型提取联系人信息
        contact_name = None
        position = None

        if request.contact_type == "legal_representative":
            contact_name = tianyancha_data.get("legal_representative")
            position = "法定代表人"
            if not contact_name:
                raise BusinessException(detail="天眼查数据中没有法定代表人信息")
        elif request.contact_type == "shareholder":
            if not request.shareholder_name:
                raise BusinessException(detail="创建股东联系人时必须指定 shareholder_name")

            # 从股东列表中查找
            shareholders = tianyancha_data.get("shareholders", [])
            shareholder_found = None
            for shareholder in shareholders:
                if shareholder.get("name") == request.shareholder_name:
                    shareholder_found = shareholder
                    break

            if not shareholder_found:
                raise BusinessException(detail=f"在天眼查数据中找不到股东: {request.shareholder_name}")

            contact_name = shareholder_found.get("name")
            shareholder_type = shareholder_found.get("type", "股东")
            ratio = shareholder_found.get("ratio", "")
            position = f"{shareholder_type}（持股{ratio}）" if ratio else shareholder_type

        # 解析中文姓名
        if len(contact_name) >= 2:
            last_name = contact_name[0]
            first_name = contact_name[1:]
        else:
            last_name = contact_name
            first_name = ""

        # 创建联系人
        from foundation_service.services.contact_service import ContactService
        contact_service = ContactService(self.db)

        contact_create_request = ContactCreateRequest(
            customer_id=int(customer_id),
            first_name=first_name,
            last_name=last_name,
            position=position,
            is_primary=request.is_primary,
            is_decision_maker=request.is_decision_maker,
            is_active=True,
            notes=f"来自天眼查数据（{request.contact_type}）"
        )

        contact_response = await contact_service.create_contact(contact_create_request)
        logger.info(f"从天眼查创建联系人成功: contact_id={contact_response.id}, name={contact_name}")

        return contact_response
