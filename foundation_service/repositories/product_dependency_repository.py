"""
产品依赖关系数据访问层
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import joinedload
from common.models.product_dependency import ProductDependency
from common.utils.repository import BaseRepository


class ProductDependencyRepository(BaseRepository[ProductDependency]):
    """产品依赖关系仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ProductDependency)
    
    async def get_dependencies_by_product(
        self, 
        product_id: str,
        dependency_type: Optional[str] = None
    ) -> List[ProductDependency]:
        """获取产品的依赖关系（该产品依赖哪些其他产品）"""
        query = (
            select(ProductDependency)
            .options(
                joinedload(ProductDependency.depends_on_product)
            )
            .where(ProductDependency.product_id == product_id)
        )
        if dependency_type:
            query = query.where(ProductDependency.dependency_type == dependency_type)
        query = query.order_by(ProductDependency.dependency_type.desc(), ProductDependency.created_at.asc())
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_dependent_products(
        self, 
        product_id: str
    ) -> List[ProductDependency]:
        """获取依赖该产品的产品列表（哪些产品依赖该产品）"""
        query = (
            select(ProductDependency)
            .options(
                joinedload(ProductDependency.product)
            )
            .where(ProductDependency.depends_on_product_id == product_id)
            .order_by(ProductDependency.dependency_type.desc(), ProductDependency.created_at.asc())
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_list(
        self,
        page: int = 1,
        size: int = 20,
        product_id: Optional[str] = None,
        depends_on_product_id: Optional[str] = None,
        dependency_type: Optional[str] = None,
    ) -> Tuple[List[ProductDependency], int]:
        """查询产品依赖关系列表（用于管理页面）"""
        conditions = []
        
        if product_id:
            conditions.append(ProductDependency.product_id == product_id)
        if depends_on_product_id:
            conditions.append(ProductDependency.depends_on_product_id == depends_on_product_id)
        if dependency_type:
            conditions.append(ProductDependency.dependency_type == dependency_type)
        
        # 查询总数
        count_query = select(func.count(ProductDependency.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据（预加载关联产品）
        query = (
            select(ProductDependency)
            .options(
                joinedload(ProductDependency.product),
                joinedload(ProductDependency.depends_on_product)
            )
        )
        if conditions:
            query = query.where(and_(*conditions))
        query = query.order_by(ProductDependency.created_at.desc())
        query = query.offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        dependencies = result.unique().scalars().all()
        
        return list(dependencies), total
    
    async def check_circular_dependency(
        self, 
        product_id: str, 
        depends_on_product_id: str
    ) -> bool:
        """检查是否存在循环依赖
        
        检查逻辑：
        1. 如果 A 依赖 B，则不能创建 B 依赖 A（直接循环）
        2. 如果 A 依赖 B，B 依赖 C，则不能创建 C 依赖 A（间接循环）
        """
        # 检查直接循环：如果 depends_on_product_id 已经依赖 product_id，则存在循环
        reverse_query = select(ProductDependency).where(
            and_(
                ProductDependency.product_id == depends_on_product_id,
                ProductDependency.depends_on_product_id == product_id
            )
        )
        reverse_result = await self.db.execute(reverse_query)
        if reverse_result.scalar_one_or_none():
            return True
        
        # 检查间接循环：使用递归查询检查依赖链
        # 如果 depends_on_product_id 的任何依赖（直接或间接）包含 product_id，则存在循环
        visited = set()
        to_check = [depends_on_product_id]
        
        while to_check:
            current_product_id = to_check.pop(0)
            if current_product_id == product_id:
                return True
            if current_product_id in visited:
                continue
            visited.add(current_product_id)
            
            # 查询当前产品依赖的所有产品
            deps_query = select(ProductDependency).where(
                ProductDependency.product_id == current_product_id
            )
            deps_result = await self.db.execute(deps_query)
            deps = deps_result.scalars().all()
            
            for dep in deps:
                if dep.depends_on_product_id not in visited:
                    to_check.append(dep.depends_on_product_id)
        
        return False
    
    async def get_by_product_pair(
        self,
        product_id: str,
        depends_on_product_id: str
    ) -> Optional[ProductDependency]:
        """根据产品对查询依赖关系"""
        query = select(ProductDependency).where(
            and_(
                ProductDependency.product_id == product_id,
                ProductDependency.depends_on_product_id == depends_on_product_id
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

