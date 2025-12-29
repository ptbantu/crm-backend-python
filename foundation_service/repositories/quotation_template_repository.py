"""
报价单模板仓库
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from common.models.quotation_template import QuotationTemplate
from common.utils.repository import BaseRepository


class QuotationTemplateRepository(BaseRepository[QuotationTemplate]):
    """报价单模板仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, QuotationTemplate)
    
    async def get_by_template_code(self, template_code: str) -> Optional[QuotationTemplate]:
        """根据模板代码查询"""
        query = (
            select(QuotationTemplate)
            .where(QuotationTemplate.template_code == template_code)
            .where(QuotationTemplate.is_active == True)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_currency_and_language(
        self,
        currency: str,
        language: str
    ) -> List[QuotationTemplate]:
        """根据货币和语言查询模板"""
        query = (
            select(QuotationTemplate)
            .where(QuotationTemplate.primary_currency == currency)
            .where(QuotationTemplate.language == language)
            .where(QuotationTemplate.is_active == True)
            .order_by(QuotationTemplate.is_default.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_default_template(
        self,
        currency: str,
        language: str
    ) -> Optional[QuotationTemplate]:
        """获取默认模板"""
        query = (
            select(QuotationTemplate)
            .where(QuotationTemplate.primary_currency == currency)
            .where(QuotationTemplate.language == language)
            .where(QuotationTemplate.is_default == True)
            .where(QuotationTemplate.is_active == True)
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all_active(self) -> List[QuotationTemplate]:
        """获取所有启用的模板"""
        query = (
            select(QuotationTemplate)
            .where(QuotationTemplate.is_active == True)
            .order_by(QuotationTemplate.template_code.asc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
