"""
角色数据访问层
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from common.models.role import Role
from common.utils.repository import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """角色仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Role)
    
    async def get_all(self) -> List[Role]:
        """查询所有角色"""
        return await super().get_all()

