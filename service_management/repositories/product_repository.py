"""
产品/服务数据访问层
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from service_management.models.product import Product
from service_management.models.service_type import ServiceType
from service_management.models.product_category import ProductCategory
from common.utils.repository import BaseRepository


class ProductRepository(BaseRepository[Product]):
    """产品/服务仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Product)
    
    async def get_list(
        self,
        page: int = 1,
        size: int = 10,
        name: Optional[str] = None,
        code: Optional[str] = None,
        category_id: Optional[str] = None,
        service_type_id: Optional[str] = None,
        service_type: Optional[str] = None,
        service_subtype: Optional[str] = None,
        status: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[List[Product], int]:
        """分页查询产品列表"""
        query = select(Product)
        
        # 构建查询条件
        conditions = []
        if name:
            conditions.append(Product.name.ilike(f"%{name}%"))
        if code:
            conditions.append(Product.code.ilike(f"%{code}%"))
        if category_id:
            conditions.append(Product.category_id == category_id)
        if service_type_id:
            conditions.append(Product.service_type_id == service_type_id)
        if service_type:
            conditions.append(Product.service_type == service_type)
        if service_subtype:
            conditions.append(Product.service_subtype == service_subtype)
        if status:
            conditions.append(Product.status == status)
        if is_active is not None:
            conditions.append(Product.is_active == is_active)
        
        if conditions:
            query = query.where(or_(*conditions))
        
        # 排序
        query = query.order_by(Product.created_at.desc())
        
        # 计算总数
        count_query = select(func.count()).select_from(Product)
        if conditions:
            count_query = count_query.where(or_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页
        query = query.offset((page - 1) * size).limit(size)
        
        # 执行查询
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return list(items), total

