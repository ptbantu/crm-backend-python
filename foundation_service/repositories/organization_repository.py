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
    
    async def get_by_code(self, code: str) -> Optional[Organization]:
        """根据编码查询组织"""
        result = await self.db.execute(
            select(Organization).where(Organization.code == code)
        )
        return result.scalar_one_or_none()
    
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
    
    async def get_tree(self, root_id: Optional[str] = None) -> List[Organization]:
        """获取组织树（递归查询）"""
        if root_id:
            # 从指定根节点开始
            query = select(Organization).where(Organization.parent_id == root_id)
        else:
            # 获取所有根节点（parent_id 为 NULL）
            query = select(Organization).where(Organization.parent_id.is_(None))
        
        result = await self.db.execute(query)
        roots = list(result.scalars().all())
        
        # 递归获取子节点
        async def get_children(parent_id: str) -> List[Organization]:
            query = select(Organization).where(Organization.parent_id == parent_id)
            result = await self.db.execute(query)
            return list(result.scalars().all())
        
        # 构建树结构（这里只返回扁平列表，树结构在 Service 层构建）
        all_orgs = []
        async def collect_all(orgs: List[Organization]):
            for org in orgs:
                all_orgs.append(org)
                children = await get_children(org.id)
                if children:
                    await collect_all(children)
        
        await collect_all(roots)
        return all_orgs

