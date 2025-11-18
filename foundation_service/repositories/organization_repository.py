"""
组织数据访问层
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from foundation_service.models.organization import Organization
from foundation_service.models.organization_employee import OrganizationEmployee
from common.utils.repository import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    """组织仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Organization)
    
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

