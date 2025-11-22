"""
组织服务
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from foundation_service.schemas.organization import (
    OrganizationCreateRequest, OrganizationUpdateRequest, OrganizationResponse,
    OrganizationTreeNode
)
from foundation_service.repositories.organization_repository import OrganizationRepository
from foundation_service.models.organization import Organization
from common.exceptions import OrganizationNotFoundError, BusinessException
from common.utils.logger import get_logger
from sqlalchemy import select

logger = get_logger(__name__)


class OrganizationService:
    """组织服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.org_repo = OrganizationRepository(db)
    
    async def create_organization(self, request: OrganizationCreateRequest) -> OrganizationResponse:
        """创建组织"""
        logger.info(f"开始创建组织: name={request.name}, code={request.code}, type={request.organization_type}, parent_id={request.parent_id}")
        
        # 检查编码是否已存在
        if request.code:
            existing = await self.org_repo.get_by_code(request.code)
            if existing:
                logger.warning(f"组织编码已存在: code={request.code}")
                raise BusinessException(detail=f"组织编码 {request.code} 已存在")
        
        # 验证父组织（如果指定）
        if request.parent_id:
            parent_org = await self.org_repo.get_by_id(request.parent_id)
            if not parent_org:
                logger.warning(f"父组织不存在: parent_id={request.parent_id}")
                raise OrganizationNotFoundError()
            
            if not parent_org.is_active:
                logger.warning(f"父组织未激活: parent_id={request.parent_id}")
                raise BusinessException(detail="父组织未激活")
            
            # 检查循环引用（防止父组织是自己的子组织）
            if await self._check_circular_reference(request.parent_id, None):
                logger.warning(f"检测到循环引用: parent_id={request.parent_id}")
                raise BusinessException(detail="不能将组织设置为自己的子组织")
        
        organization = Organization(
            name=request.name,
            code=request.code,
            organization_type=request.organization_type,
            parent_id=request.parent_id,
            email=request.email,
            phone=request.phone,
            website=request.website,
            logo_url=request.logo_url,
            description=request.description,
            street=request.street,
            city=request.city,
            state_province=request.state_province,
            postal_code=request.postal_code,
            country=request.country,
            country_code=request.country_code,
            company_size=request.company_size,
            company_nature=request.company_nature,
            company_type=request.company_type,
            industry=request.industry,
            industry_code=request.industry_code,
            sub_industry=request.sub_industry,
            business_scope=request.business_scope,
            registration_number=request.registration_number,
            tax_id=request.tax_id,
            legal_representative=request.legal_representative,
            established_date=request.established_date,
            registered_capital=request.registered_capital,
            registered_capital_currency=request.registered_capital_currency,
            company_status=request.company_status,
            annual_revenue=request.annual_revenue,
            annual_revenue_currency=request.annual_revenue_currency,
            employee_count=request.employee_count,
            revenue_year=request.revenue_year,
            certifications=request.certifications or [],
            business_license_url=request.business_license_url,
            tax_certificate_url=request.tax_certificate_url,
            is_active=request.is_active
        )
        
        organization = await self.org_repo.create(organization)
        logger.info(f"组织创建成功: id={organization.id}, name={organization.name}, code={organization.code}")
        return await self._to_response(organization)
    
    async def get_organization_by_id(self, organization_id: str) -> OrganizationResponse:
        """查询组织详情"""
        logger.debug(f"查询组织详情: organization_id={organization_id}")
        organization = await self.org_repo.get_by_id(organization_id)
        if not organization:
            logger.warning(f"组织不存在: organization_id={organization_id}")
            raise OrganizationNotFoundError()
        
        logger.debug(f"组织查询成功: id={organization.id}, name={organization.name}")
        return await self._to_response(organization)
    
    async def update_organization(
        self,
        organization_id: str,
        request: OrganizationUpdateRequest
    ) -> OrganizationResponse:
        """更新组织信息"""
        logger.info(f"开始更新组织: organization_id={organization_id}")
        organization = await self.org_repo.get_by_id(organization_id)
        if not organization:
            logger.warning(f"组织不存在: organization_id={organization_id}")
            raise OrganizationNotFoundError()
        
        # 更新字段（简化处理，实际应该逐个字段判断）
        if request.name is not None:
            organization.name = request.name
        if request.code is not None:
            if request.code != organization.code:
                existing = await self.org_repo.get_by_code(request.code)
                if existing:
                    logger.warning(f"组织编码已存在: code={request.code}, organization_id={organization_id}")
                    raise BusinessException(detail=f"组织编码 {request.code} 已存在")
                logger.debug(f"更新组织编码: organization_id={organization_id}, old_code={organization.code}, new_code={request.code}")
            organization.code = request.code
        
        # 更新父组织（如果指定）
        if hasattr(request, 'parent_id') and request.parent_id is not None:
            if request.parent_id == organization_id:
                logger.warning(f"不能将组织设置为自己的父组织: organization_id={organization_id}")
                raise BusinessException(detail="不能将组织设置为自己的父组织")
            
            # 检查循环引用
            if await self._check_circular_reference(request.parent_id, organization_id):
                logger.warning(f"检测到循环引用: organization_id={organization_id}, parent_id={request.parent_id}")
                raise BusinessException(detail="不能将组织设置为自己的子组织")
            
            # 验证父组织存在且激活
            parent_org = await self.org_repo.get_by_id(request.parent_id)
            if not parent_org:
                logger.warning(f"父组织不存在: parent_id={request.parent_id}")
                raise OrganizationNotFoundError()
            if not parent_org.is_active:
                logger.warning(f"父组织未激活: parent_id={request.parent_id}")
                raise BusinessException(detail="父组织未激活")
            
            organization.parent_id = request.parent_id
        
        if request.is_active is not None:
            organization.is_active = request.is_active
        if request.is_locked is not None:
            organization.is_locked = request.is_locked
        
        organization = await self.org_repo.update(organization)
        logger.info(f"组织更新成功: id={organization.id}, name={organization.name}")
        return await self._to_response(organization)
    
    async def delete_organization(self, organization_id: str) -> None:
        """Block 组织（逻辑删除）"""
        logger.info(f"开始删除组织: organization_id={organization_id}")
        organization = await self.org_repo.get_by_id(organization_id)
        if not organization:
            logger.warning(f"组织不存在: organization_id={organization_id}")
            raise OrganizationNotFoundError()
        
        # 检查是否有子组织（仅提示，不阻止删除）
        from sqlalchemy import select
        from foundation_service.models.organization import Organization
        children_result = await self.db.execute(
            select(Organization).where(Organization.parent_id == organization_id)
        )
        children = list(children_result.scalars().all())
        if children:
            active_children = [c for c in children if c.is_active]
            if active_children:
                logger.warning(f"组织存在活跃的子组织: organization_id={organization_id}, children_count={len(active_children)}")
                # 仅记录警告，不阻止删除（业务规则允许）
        
        organization.is_locked = True
        organization.is_active = False
        await self.org_repo.update(organization)
        logger.info(f"组织删除成功: id={organization.id}, name={organization.name}")
    
    async def _check_circular_reference(
        self, 
        parent_id: str, 
        current_id: Optional[str] = None
    ) -> bool:
        """检查循环引用（递归检查父组织链）"""
        if current_id and parent_id == current_id:
            return True  # 发现循环引用
        
        if not parent_id:
            return False
        
        parent_org = await self.org_repo.get_by_id(parent_id)
        if not parent_org:
            return False
        
        # 如果父组织没有父级，则没有循环引用
        if not parent_org.parent_id:
            return False
        
        # 如果父组织的父级是当前组织，则发现循环引用
        if current_id and parent_org.parent_id == current_id:
            return True
        
        # 递归检查父组织的父级链
        return await self._check_circular_reference(parent_org.parent_id, current_id)
    
    async def get_organization_list(
        self,
        page: int = 1,
        size: int = 10,
        name: Optional[str] = None,
        code: Optional[str] = None,
        organization_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> dict:
        """分页查询组织列表"""
        logger.debug(f"查询组织列表: page={page}, size={size}, name={name}, code={code}, type={organization_type}")
        organizations, total = await self.org_repo.get_list(
            page=page,
            size=size,
            name=name,
            code=code,
            organization_type=organization_type,
            is_active=is_active
        )
        
        # 转换为响应对象
        records = []
        for org in organizations:
            records.append(await self._to_response(org))
        
        logger.debug(f"组织列表查询成功: total={total}, returned={len(records)}")
        return {
            "records": records,
            "total": total,
            "size": size,
            "current": page,
            "pages": (total + size - 1) // size if total > 0 else 0
        }
    
    async def _to_response(self, organization: Organization) -> OrganizationResponse:
        """转换为响应对象"""
        # 获取统计信息
        employees_count = await self.org_repo.get_employees_count(organization.id)
        
        return OrganizationResponse(
            id=organization.id,
            name=organization.name,
            code=organization.code,
            organization_type=organization.organization_type,
            email=organization.email,
            phone=organization.phone,
            website=organization.website,
            logo_url=organization.logo_url,
            description=organization.description,
            is_active=organization.is_active,
            is_locked=organization.is_locked or False,
            is_verified=organization.is_verified or False,
            employees_count=employees_count,
            created_at=organization.created_at,
            updated_at=organization.updated_at
        )
    
    async def get_organization_tree(
        self,
        root_id: Optional[str] = None,
        organization_type: Optional[str] = None
    ) -> List[OrganizationTreeNode]:
        """获取组织树结构"""
        logger.debug(f"查询组织树: root_id={root_id}, type={organization_type}")
        
        # 获取所有组织
        all_orgs = await self.org_repo.get_tree(root_id)
        
        # 如果指定了组织类型，进行过滤
        if organization_type:
            all_orgs = [org for org in all_orgs if org.organization_type == organization_type]
        
        # 构建树结构
        org_dict: dict[str, OrganizationTreeNode] = {}
        for org in all_orgs:
            employees_count = await self.org_repo.get_employees_count(org.id)
            org_dict[org.id] = OrganizationTreeNode(
                id=org.id,
                name=org.name,
                code=org.code,
                organization_type=org.organization_type,
                is_active=org.is_active,
                is_locked=org.is_locked or False,
                employees_count=employees_count,
                children=[]
            )
        
        # 构建父子关系
        root_nodes = []
        for org in all_orgs:
            node = org_dict[org.id]
            if org.parent_id and org.parent_id in org_dict:
                org_dict[org.parent_id].children.append(node)
            else:
                root_nodes.append(node)
        
        logger.debug(f"组织树查询成功: root_count={len(root_nodes)}")
        return root_nodes

