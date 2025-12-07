"""
产品分类数据访问层
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from common.models.product_category import ProductCategory
from common.utils.repository import BaseRepository


class ProductCategoryRepository(BaseRepository[ProductCategory]):
    """产品分类仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ProductCategory)
    
    async def get_list(
        self,
        page: int = 1,
        size: int = 10,
        code: Optional[str] = None,
        name: Optional[str] = None,
        parent_id: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[List[ProductCategory], int]:
        """分页查询分类列表"""
        query = select(ProductCategory)
        
        # 构建查询条件
        conditions = []
        if code:
            conditions.append(ProductCategory.code.ilike(f"%{code}%"))
        if name:
            conditions.append(ProductCategory.name.ilike(f"%{name}%"))
        if parent_id is not None:
            if parent_id == "":
                conditions.append(ProductCategory.parent_id.is_(None))
            else:
                conditions.append(ProductCategory.parent_id == parent_id)
        if is_active is not None:
            conditions.append(ProductCategory.is_active == is_active)
        
        if conditions:
            query = query.where(or_(*conditions))
        
        # 排序
        query = query.order_by(ProductCategory.display_order, ProductCategory.created_at)
        
        # 计算总数
        count_query = select(func.count()).select_from(ProductCategory)
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
    
    async def get_children(self, parent_id: str) -> List[ProductCategory]:
        """获取子分类列表"""
        result = await self.db.execute(
            select(ProductCategory)
            .where(ProductCategory.parent_id == parent_id)
            .order_by(ProductCategory.display_order, ProductCategory.created_at)
        )
        return list(result.scalars().all())
    
    async def check_circular_reference(self, category_id: str, parent_id: str) -> bool:
        """检查循环引用（parent_id 不能指向自身或子分类）"""
        if category_id == parent_id:
            return True  # 不能指向自身
        
        # 检查 parent_id 是否是 category_id 的子分类
        current = await self.get_by_id(parent_id)
        if not current:
            return False  # parent_id 不存在，不是循环引用
        
        # 递归检查父级链
        visited = {category_id}
        while current and current.parent_id:
            if current.parent_id in visited:
                return True  # 发现循环
            if current.parent_id == category_id:
                return True  # parent_id 的父级链包含 category_id
            visited.add(current.parent_id)
            current = await self.get_by_id(current.parent_id)
        
        return False

