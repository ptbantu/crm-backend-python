"""
组织领域数据访问层
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from common.models.organization_domain import OrganizationDomain, OrganizationDomainRelation
from common.utils.repository import BaseRepository


class OrganizationDomainRepository(BaseRepository[OrganizationDomain]):
    """组织领域仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, OrganizationDomain)
    
    async def get_by_code(self, code: str) -> Optional[OrganizationDomain]:
        """根据代码查询领域"""
        result = await self.db.execute(
            select(OrganizationDomain).where(OrganizationDomain.code == code)
        )
        return result.scalar_one_or_none()
    
    async def get_all_active(self) -> List[OrganizationDomain]:
        """查询所有激活的领域"""
        result = await self.db.execute(
            select(OrganizationDomain)
            .where(OrganizationDomain.is_active == True)
            .order_by(OrganizationDomain.display_order, OrganizationDomain.name_zh)
        )
        return list(result.scalars().all())
    
    async def get_by_organization_id(self, organization_id: str) -> List[OrganizationDomain]:
        """根据组织ID查询关联的领域"""
        result = await self.db.execute(
            select(OrganizationDomain)
            .join(OrganizationDomainRelation, OrganizationDomain.id == OrganizationDomainRelation.domain_id)
            .where(OrganizationDomainRelation.organization_id == organization_id)
            .order_by(OrganizationDomainRelation.is_primary.desc(), OrganizationDomain.display_order)
        )
        return list(result.scalars().all())


class OrganizationDomainRelationRepository:
    """组织领域关联仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_organization_id(self, organization_id: str) -> List[OrganizationDomainRelation]:
        """根据组织ID查询关联关系"""
        result = await self.db.execute(
            select(OrganizationDomainRelation)
            .where(OrganizationDomainRelation.organization_id == organization_id)
            .order_by(OrganizationDomainRelation.is_primary.desc())
        )
        return list(result.scalars().all())
    
    async def create(self, relation: OrganizationDomainRelation) -> OrganizationDomainRelation:
        """创建关联关系"""
        self.db.add(relation)
        await self.db.flush()
        await self.db.refresh(relation)
        return relation
    
    async def delete_by_organization_id(self, organization_id: str) -> None:
        """删除组织的所有领域关联"""
        from sqlalchemy import delete
        await self.db.execute(
            delete(OrganizationDomainRelation)
            .where(OrganizationDomainRelation.organization_id == organization_id)
        )
        await self.db.flush()
    
    async def set_organization_domains(
        self, 
        organization_id: str, 
        domain_ids: List[str],
        primary_domain_id: Optional[str] = None
    ) -> None:
        """设置组织的领域关联"""
        # 删除旧的关联
        await self.delete_by_organization_id(organization_id)
        
        # 创建新的关联
        for domain_id in domain_ids:
            relation = OrganizationDomainRelation(
                organization_id=organization_id,
                domain_id=domain_id,
                is_primary=(domain_id == primary_domain_id) if primary_domain_id else False
            )
            await self.create(relation)
        
        await self.db.flush()

