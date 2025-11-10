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
    
    async def get_list(
        self,
        page: int = 1,
        size: int = 10,
        name: Optional[str] = None,
        code: Optional[str] = None,
        organization_type: Optional[str] = None,
        parent_id: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[Organization], int]:
        """分页查询组织列表"""
        query = select(Organization)
        
        if name:
            query = query.where(Organization.name.like(f"%{name}%"))
        if code:
            query = query.where(Organization.code == code)
        if organization_type:
            query = query.where(Organization.organization_type == organization_type)
        if parent_id:
            query = query.where(Organization.parent_id == parent_id)
        if is_active is not None:
            query = query.where(Organization.is_active == is_active)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页查询
        query = query.order_by(Organization.organization_type, Organization.code)
        query = query.offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        organizations = result.scalars().all()
        
        return list(organizations), total

