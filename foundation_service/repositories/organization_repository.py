"""
组织数据访问层
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from foundation_service.models.organization import Organization
from foundation_service.models.organization_employee import OrganizationEmployee


class OrganizationRepository:
    """组织仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, organization_id: str) -> Optional[Organization]:
        """根据ID查询组织"""
        result = await self.db.execute(
            select(Organization).where(Organization.id == organization_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_code(self, code: str) -> Optional[Organization]:
        """根据编码查询组织"""
        result = await self.db.execute(
            select(Organization).where(Organization.code == code)
        )
        return result.scalar_one_or_none()
    
    async def create(self, organization: Organization) -> Organization:
        """创建组织"""
        self.db.add(organization)
        await self.db.flush()
        await self.db.refresh(organization)
        return organization
    
    async def update(self, organization: Organization) -> Organization:
        """更新组织"""
        await self.db.flush()
        await self.db.refresh(organization)
        return organization
    
    async def get_children_count(self, organization_id: str) -> int:
        """获取子组织数量"""
        result = await self.db.execute(
            select(func.count(Organization.id))
            .where(Organization.parent_id == organization_id)
        )
        return result.scalar() or 0
    
    async def get_employees_count(self, organization_id: str) -> int:
        """获取员工数量"""
        result = await self.db.execute(
            select(func.count(OrganizationEmployee.id))
            .where(
                OrganizationEmployee.organization_id == organization_id,
                OrganizationEmployee.is_active == True
            )
        )
        return result.scalar() or 0

