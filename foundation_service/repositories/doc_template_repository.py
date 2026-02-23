"""
文档模板仓库
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from common.models.doc_template import DocTemplate, TemplateTypeEnum
from common.utils.repository import BaseRepository


class DocTemplateRepository(BaseRepository[DocTemplate]):
    """文档模板仓库"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, DocTemplate)

    async def get_by_code(self, template_code: str) -> Optional[DocTemplate]:
        """根据模板代码查询"""
        query = select(DocTemplate).where(DocTemplate.template_code == template_code)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_active_by_type(
        self,
        template_type: TemplateTypeEnum,
        entity_id: Optional[str] = None
    ) -> List[DocTemplate]:
        """根据类型查询启用的模板"""
        conditions = [
            DocTemplate.template_type == template_type,
            DocTemplate.is_active == True
        ]

        if entity_id:
            conditions.append(DocTemplate.entity_id == entity_id)

        query = (
            select(DocTemplate)
            .where(and_(*conditions))
            .order_by(desc(DocTemplate.created_at))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_entity(
        self,
        entity_id: str,
        is_active: Optional[bool] = None
    ) -> List[DocTemplate]:
        """根据签约主体查询模板"""
        conditions = [DocTemplate.entity_id == entity_id]

        if is_active is not None:
            conditions.append(DocTemplate.is_active == is_active)

        query = (
            select(DocTemplate)
            .where(and_(*conditions))
            .order_by(desc(DocTemplate.created_at))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def list_templates(
        self,
        template_type: Optional[TemplateTypeEnum] = None,
        entity_id: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[DocTemplate], int]:
        """分页查询模板列表"""
        conditions = []

        if template_type:
            conditions.append(DocTemplate.template_type == template_type)
        if entity_id:
            conditions.append(DocTemplate.entity_id == entity_id)
        if is_active is not None:
            conditions.append(DocTemplate.is_active == is_active)

        # 查询总数
        count_query = select(func.count(DocTemplate.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # 查询数据
        query = select(DocTemplate)
        if conditions:
            query = query.where(and_(*conditions))
        query = (
            query
            .order_by(desc(DocTemplate.created_at))
            .offset((page - 1) * size)
            .limit(size)
        )
        result = await self.db.execute(query)
        templates = list(result.scalars().all())

        return templates, total
