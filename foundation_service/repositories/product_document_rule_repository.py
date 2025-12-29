"""
产品资料规则仓库
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from common.models.product_document_rule import ProductDocumentRule
from common.utils.repository import BaseRepository


class ProductDocumentRuleRepository(BaseRepository[ProductDocumentRule]):
    """产品资料规则仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ProductDocumentRule)
    
    async def get_by_product_id(
        self,
        product_id: str,
        include_dependencies: bool = True
    ) -> List[ProductDocumentRule]:
        """根据产品ID查询所有资料规则（按排序顺序）"""
        query = (
            select(ProductDocumentRule)
            .where(ProductDocumentRule.product_id == product_id)
            .where(ProductDocumentRule.is_active == True)
        )
        if include_dependencies:
            query = query.options(joinedload(ProductDocumentRule.depends_on_rule))
        
        query = query.order_by(ProductDocumentRule.sort_order.asc())
        result = await self.db.execute(query)
        return list(result.unique().scalars().all()) if include_dependencies else list(result.scalars().all())
    
    async def get_by_rule_code(
        self,
        product_id: str,
        rule_code: str
    ) -> Optional[ProductDocumentRule]:
        """根据规则代码查询"""
        query = (
            select(ProductDocumentRule)
            .where(ProductDocumentRule.product_id == product_id)
            .where(ProductDocumentRule.rule_code == rule_code)
            .where(ProductDocumentRule.is_active == True)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_required_rules(self, product_id: str) -> List[ProductDocumentRule]:
        """获取必填的资料规则"""
        query = (
            select(ProductDocumentRule)
            .where(ProductDocumentRule.product_id == product_id)
            .where(ProductDocumentRule.is_required == True)
            .where(ProductDocumentRule.is_active == True)
            .order_by(ProductDocumentRule.sort_order.asc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_rules_without_dependencies(self, product_id: str) -> List[ProductDocumentRule]:
        """获取没有依赖的资料规则（可以作为起始规则）"""
        query = (
            select(ProductDocumentRule)
            .where(ProductDocumentRule.product_id == product_id)
            .where(ProductDocumentRule.depends_on_rule_id.is_(None))
            .where(ProductDocumentRule.is_active == True)
            .order_by(ProductDocumentRule.sort_order.asc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
