"""
组织员工数据访问层
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from common.models.organization_employee import OrganizationEmployee
from common.utils.repository import BaseRepository


class OrganizationEmployeeRepository(BaseRepository[OrganizationEmployee]):
    """组织员工仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, OrganizationEmployee)
    
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
    
    async def get_all_by_user_id(self, user_id: str) -> List[OrganizationEmployee]:
        """获取用户的所有激活的组织员工记录"""
        from typing import List
        result = await self.db.execute(
            select(OrganizationEmployee)
            .where(
                and_(
                    OrganizationEmployee.user_id == user_id,
                    OrganizationEmployee.is_active == True
                )
            )
            .order_by(OrganizationEmployee.is_primary.desc())  # 主要组织排在前面
        )
        return list(result.scalars().all())
    
    # create 方法已从 BaseRepository 继承，无需重复定义

