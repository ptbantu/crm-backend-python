"""
组织领域服务
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from foundation_service.schemas.organization_domain import (
    OrganizationDomainCreateRequest, OrganizationDomainUpdateRequest,
    OrganizationDomainResponse, OrganizationDomainRelationResponse
)
from foundation_service.repositories.organization_domain_repository import (
    OrganizationDomainRepository, OrganizationDomainRelationRepository
)
from foundation_service.models.organization_domain import OrganizationDomain, OrganizationDomainRelation
from common.exceptions import BusinessException
from common.utils.logger import get_logger

logger = get_logger(__name__)


class OrganizationDomainService:
    """组织领域服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.domain_repo = OrganizationDomainRepository(db)
        self.relation_repo = OrganizationDomainRelationRepository(db)
    
    async def create_domain(self, request: OrganizationDomainCreateRequest) -> OrganizationDomainResponse:
        """创建组织领域"""
        logger.info(f"开始创建组织领域: code={request.code}, name_zh={request.name_zh}")
        
        # 检查代码是否已存在
        existing = await self.domain_repo.get_by_code(request.code)
        if existing:
            logger.warning(f"组织领域代码已存在: code={request.code}")
            raise BusinessException(detail=f"组织领域代码 {request.code} 已存在")
        
        domain = OrganizationDomain(
            code=request.code,
            name_zh=request.name_zh,
            name_id=request.name_id,
            description_zh=request.description_zh,
            description_id=request.description_id,
            display_order=request.display_order,
            is_active=request.is_active
        )
        
        domain = await self.domain_repo.create(domain)
        logger.info(f"组织领域创建成功: id={domain.id}, code={domain.code}")
        return await self._to_response(domain)
    
    async def get_domain_by_id(self, domain_id: str) -> OrganizationDomainResponse:
        """查询组织领域详情"""
        domain = await self.domain_repo.get_by_id(domain_id)
        if not domain:
            raise BusinessException(detail="组织领域不存在")
        return await self._to_response(domain)
    
    async def update_domain(
        self, 
        domain_id: str, 
        request: OrganizationDomainUpdateRequest
    ) -> OrganizationDomainResponse:
        """更新组织领域"""
        logger.info(f"开始更新组织领域: domain_id={domain_id}")
        domain = await self.domain_repo.get_by_id(domain_id)
        if not domain:
            raise BusinessException(detail="组织领域不存在")
        
        if request.name_zh is not None:
            domain.name_zh = request.name_zh
        if request.name_id is not None:
            domain.name_id = request.name_id
        if request.description_zh is not None:
            domain.description_zh = request.description_zh
        if request.description_id is not None:
            domain.description_id = request.description_id
        if request.display_order is not None:
            domain.display_order = request.display_order
        if request.is_active is not None:
            domain.is_active = request.is_active
        
        domain = await self.domain_repo.update(domain)
        logger.info(f"组织领域更新成功: id={domain.id}, code={domain.code}")
        return await self._to_response(domain)
    
    async def delete_domain(self, domain_id: str) -> None:
        """删除组织领域（逻辑删除）"""
        logger.info(f"开始删除组织领域: domain_id={domain_id}")
        domain = await self.domain_repo.get_by_id(domain_id)
        if not domain:
            raise BusinessException(detail="组织领域不存在")
        
        domain.is_active = False
        await self.domain_repo.update(domain)
        logger.info(f"组织领域删除成功: id={domain.id}, code={domain.code}")
    
    async def get_all_domains(self) -> List[OrganizationDomainResponse]:
        """查询所有激活的组织领域"""
        domains = await self.domain_repo.get_all_active()
        return [await self._to_response(domain) for domain in domains]
    
    async def get_organization_domains(self, organization_id: str) -> List[OrganizationDomainRelationResponse]:
        """查询组织的领域列表"""
        relations = await self.relation_repo.get_by_organization_id(organization_id)
        result = []
        for relation in relations:
            domain = await self.domain_repo.get_by_id(relation.domain_id)
            if domain:
                result.append(OrganizationDomainRelationResponse(
                    id=relation.id,
                    organization_id=relation.organization_id,
                    domain_id=relation.domain_id,
                    domain_code=domain.code,
                    domain_name_zh=domain.name_zh,
                    domain_name_id=domain.name_id,
                    is_primary=relation.is_primary,
                    created_at=relation.created_at
                ))
        return result
    
    async def set_organization_domains(
        self,
        organization_id: str,
        domain_ids: List[str],
        primary_domain_id: Optional[str] = None
    ) -> List[OrganizationDomainRelationResponse]:
        """设置组织的领域关联"""
        logger.info(f"设置组织领域: organization_id={organization_id}, domain_ids={domain_ids}, primary={primary_domain_id}")
        
        # 验证领域是否存在
        for domain_id in domain_ids:
            domain = await self.domain_repo.get_by_id(domain_id)
            if not domain:
                raise BusinessException(detail=f"组织领域不存在: domain_id={domain_id}")
            if not domain.is_active:
                raise BusinessException(detail=f"组织领域未激活: domain_id={domain_id}")
        
        # 如果指定了主要领域，确保它在列表中
        if primary_domain_id and primary_domain_id not in domain_ids:
            raise BusinessException(detail="主要领域必须在领域列表中")
        
        # 设置关联
        await self.relation_repo.set_organization_domains(
            organization_id=organization_id,
            domain_ids=domain_ids,
            primary_domain_id=primary_domain_id
        )
        
        logger.info(f"组织领域设置成功: organization_id={organization_id}")
        return await self.get_organization_domains(organization_id)
    
    async def _to_response(self, domain: OrganizationDomain) -> OrganizationDomainResponse:
        """转换为响应对象"""
        return OrganizationDomainResponse(
            id=domain.id,
            code=domain.code,
            name_zh=domain.name_zh,
            name_id=domain.name_id,
            description_zh=domain.description_zh,
            description_id=domain.description_id,
            display_order=domain.display_order,
            is_active=domain.is_active,
            created_at=domain.created_at,
            updated_at=domain.updated_at
        )

