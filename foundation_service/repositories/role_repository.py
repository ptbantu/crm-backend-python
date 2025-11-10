"""
角色数据访问层
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from foundation_service.models.role import Role


class RoleRepository:
    """角色仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, role_id: str) -> Optional[Role]:
        """根据ID查询角色"""
        result = await self.db.execute(
            select(Role).where(Role.id == role_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_code(self, code: str) -> Optional[Role]:
        """根据编码查询角色"""
        result = await self.db.execute(
            select(Role).where(Role.code == code)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[Role]:
        """查询所有角色"""
        result = await self.db.execute(select(Role))
        return list(result.scalars().all())
    
    async def create(self, role: Role) -> Role:
        """创建角色"""
        self.db.add(role)
        await self.db.flush()
        await self.db.refresh(role)
        return role
    
    async def update(self, role: Role) -> Role:
        """更新角色"""
        await self.db.flush()
        await self.db.refresh(role)
        return role
    
    async def delete(self, role: Role) -> None:
        """删除角色"""
        await self.db.delete(role)
        await self.db.flush()

