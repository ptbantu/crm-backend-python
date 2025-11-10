"""
组织员工数据访问层
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from foundation_service.models.organization_employee import OrganizationEmployee


class OrganizationEmployeeRepository:
    """组织员工仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_primary_by_user_id(self, user_id: str) -> Optional[OrganizationEmployee]:
        """获取用户的主要组织员工记录"""
        result = await self.db.execute(
            select(OrganizationEmployee)
            .where(
                and_(
                    OrganizationEmployee.user_id == user_id,
                    OrganizationEmployee.is_primary == True,
                    OrganizationEmployee.is_active == True
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def create(self, employee: OrganizationEmployee) -> OrganizationEmployee:
        """创建组织员工记录"""
        self.db.add(employee)
        await self.db.flush()
        await self.db.refresh(employee)
        return employee

