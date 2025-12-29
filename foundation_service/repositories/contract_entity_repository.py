"""
财税主体数据访问层
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from common.models.contract_entity import ContractEntity
from common.utils.repository import BaseRepository


class ContractEntityRepository(BaseRepository[ContractEntity]):
    """财税主体仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ContractEntity)
    
    async def get_by_code(self, code: str) -> Optional[ContractEntity]:
        """根据编码查询财税主体"""
        result = await self.db.execute(
            select(ContractEntity).where(ContractEntity.entity_code == code)
        )
        return result.scalar_one_or_none()
    
    async def get_list(
        self,
        page: int = 1,
        size: int = 10,
        entity_code: Optional[str] = None,
        entity_name: Optional[str] = None,
        short_name: Optional[str] = None,
        currency: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[ContractEntity], int]:
        """分页查询财税主体列表"""
        query = select(ContractEntity)
        
        # 构建查询条件
        if entity_code:
            query = query.where(ContractEntity.entity_code.like(f"%{entity_code}%"))
        if entity_name:
            query = query.where(ContractEntity.entity_name.like(f"%{entity_name}%"))
        if short_name:
            query = query.where(ContractEntity.short_name.like(f"%{short_name}%"))
        if currency:
            query = query.where(ContractEntity.currency == currency)
        if is_active is not None:
            query = query.where(ContractEntity.is_active == is_active)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页查询
        query = query.order_by(ContractEntity.created_at.desc())
        query = query.offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        entities = result.scalars().all()
        
        return list(entities), total
