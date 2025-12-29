"""
合同模板仓库
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from common.models.contract import ContractTemplate
from common.utils.repository import BaseRepository


class ContractTemplateRepository(BaseRepository[ContractTemplate]):
    """合同模板仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ContractTemplate)
    
    async def get_by_template_code(self, template_code: str) -> Optional[ContractTemplate]:
        """根据模板代码查询"""
        query = (
            select(ContractTemplate)
            .where(ContractTemplate.template_code == template_code)
            .where(ContractTemplate.is_active == True)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_entity_id(
        self,
        entity_id: str,
        language: Optional[str] = None
    ) -> List[ContractTemplate]:
        """根据签约主体ID查询模板"""
        conditions = [
            ContractTemplate.entity_id == entity_id,
            ContractTemplate.is_active == True
        ]
        if language:
            conditions.append(ContractTemplate.language == language)
        
        query = (
            select(ContractTemplate)
            .where(and_(*conditions))
            .order_by(ContractTemplate.is_default_for_entity.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_default_for_entity(
        self,
        entity_id: str,
        language: Optional[str] = None
    ) -> Optional[ContractTemplate]:
        """获取签约主体的默认模板"""
        conditions = [
            ContractTemplate.entity_id == entity_id,
            ContractTemplate.is_default_for_entity == True,
            ContractTemplate.is_active == True
        ]
        if language:
            conditions.append(ContractTemplate.language == language)
        
        query = (
            select(ContractTemplate)
            .where(and_(*conditions))
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
