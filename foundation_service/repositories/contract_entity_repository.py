"""
签约主体仓库
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from common.models.contract_entity import ContractEntity
from common.utils.repository import BaseRepository


class ContractEntityRepository(BaseRepository[ContractEntity]):
    """签约主体仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ContractEntity)
    
    async def get_by_entity_code(self, entity_code: str) -> Optional[ContractEntity]:
        """根据主体代码查询"""
        query = (
            select(ContractEntity)
            .where(ContractEntity.entity_code == entity_code)
            .where(ContractEntity.is_active == True)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all_active(self) -> List[ContractEntity]:
        """获取所有启用的签约主体"""
        query = (
            select(ContractEntity)
            .where(ContractEntity.is_active == True)
            .order_by(ContractEntity.entity_code.asc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_currency(self, currency: str) -> List[ContractEntity]:
        """根据货币查询签约主体"""
        query = (
            select(ContractEntity)
            .where(ContractEntity.currency == currency)
            .where(ContractEntity.is_active == True)
            .order_by(ContractEntity.entity_code.asc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
