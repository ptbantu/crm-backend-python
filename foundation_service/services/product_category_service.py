"""
产品分类服务
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from foundation_service.schemas.product_category import (
    ProductCategoryCreateRequest,
    ProductCategoryUpdateRequest,
    ProductCategoryResponse,
    ProductCategoryListResponse,
)
from foundation_service.repositories.product_category_repository import ProductCategoryRepository
from foundation_service.repositories.product_repository import ProductRepository
from common.models.product_category import ProductCategory
from common.models.product import Product
from common.exceptions import BusinessException


class ProductCategoryService:
    """产品分类服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.category_repo = ProductCategoryRepository(db)
        self.product_repo = ProductRepository(db)
    
    async def create_category(self, request: ProductCategoryCreateRequest) -> ProductCategoryResponse:
        """创建产品分类"""
        # 检查编码是否已存在
        existing = await self.category_repo.get_by_code(request.code)
        if existing:
            raise BusinessException(detail=f"分类编码 {request.code} 已存在")
        
        # 如果指定了父分类，验证父分类是否存在且激活
        if request.parent_id:
            parent = await self.category_repo.get_by_id(request.parent_id)
            if not parent:
                raise BusinessException(detail="父分类不存在")
            if not parent.is_active:
                raise BusinessException(detail="父分类未激活")
            
            # 检查循环引用
            if await self.category_repo.check_circular_reference("", request.parent_id):
                raise BusinessException(detail="不能创建循环引用")
        
        # 创建分类
        category = ProductCategory(
            code=request.code,
            name=request.name,
            description=request.description,
            parent_id=request.parent_id,
            display_order=request.display_order,
            is_active=request.is_active,
        )
        category = await self.category_repo.create(category)
        
        # 获取父分类名称
        parent_name = None
        if category.parent_id:
            parent = await self.category_repo.get_by_id(category.parent_id)
            if parent:
                parent_name = parent.name
        
        return ProductCategoryResponse(
            id=category.id,
            code=category.code,
            name=category.name,
            description=category.description,
            parent_id=category.parent_id,
            parent_name=parent_name,
            display_order=category.display_order,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )
    
    async def get_category_by_id(self, category_id: str) -> ProductCategoryResponse:
        """查询分类详情"""
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise BusinessException(detail="分类不存在", status_code=404)
        
        # 获取父分类名称
        parent_name = None
        if category.parent_id:
            parent = await self.category_repo.get_by_id(category.parent_id)
            if parent:
                parent_name = parent.name
        
        return ProductCategoryResponse(
            id=category.id,
            code=category.code,
            name=category.name,
            description=category.description,
            parent_id=category.parent_id,
            parent_name=parent_name,
            display_order=category.display_order,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )
    
    async def update_category(self, category_id: str, request: ProductCategoryUpdateRequest) -> ProductCategoryResponse:
        """更新分类"""
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise BusinessException(detail="分类不存在", status_code=404)
        
        # 如果更新父分类，检查循环引用
        if request.parent_id is not None and request.parent_id != category.parent_id:
            if request.parent_id == category.id:
                raise BusinessException(detail="不能将自身设置为父分类")
            
            if request.parent_id:
                parent = await self.category_repo.get_by_id(request.parent_id)
                if not parent:
                    raise BusinessException(detail="父分类不存在")
                if not parent.is_active:
                    raise BusinessException(detail="父分类未激活")
                
                # 检查循环引用
                if await self.category_repo.check_circular_reference(category_id, request.parent_id):
                    raise BusinessException(detail="不能创建循环引用")
        
        # 更新字段
        if request.name is not None:
            category.name = request.name
        if request.description is not None:
            category.description = request.description
        if request.parent_id is not None:
            category.parent_id = request.parent_id if request.parent_id else None
        if request.display_order is not None:
            category.display_order = request.display_order
        if request.is_active is not None:
            category.is_active = request.is_active
        
        category = await self.category_repo.update(category)
        
        # 获取父分类名称
        parent_name = None
        if category.parent_id:
            parent = await self.category_repo.get_by_id(category.parent_id)
            if parent:
                parent_name = parent.name
        
        return ProductCategoryResponse(
            id=category.id,
            code=category.code,
            name=category.name,
            description=category.description,
            parent_id=category.parent_id,
            parent_name=parent_name,
            display_order=category.display_order,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )
    
    async def delete_category(self, category_id: str) -> None:
        """删除分类"""
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise BusinessException(detail="分类不存在", status_code=404)
        
        # TODO: 检查是否有子分类或产品使用此分类
        # 这里可以添加业务逻辑检查
        
        await self.category_repo.delete(category)
    
    async def get_category_list(
        self,
        page: int = 1,
        size: int = 10,
        code: str = None,
        name: str = None,
        parent_id: str = None,
        is_active: bool = None,
    ) -> ProductCategoryListResponse:
        """分页查询分类列表"""
        items, total = await self.category_repo.get_list(
            page=page,
            size=size,
            code=code,
            name=name,
            parent_id=parent_id,
            is_active=is_active,
        )
        
        # 转换为响应格式
        category_responses = []
        for category in items:
            # 获取父分类名称
            parent_name = None
            if category.parent_id:
                parent = await self.category_repo.get_by_id(category.parent_id)
                if parent:
                    parent_name = parent.name
            
            category_responses.append(ProductCategoryResponse(
                id=category.id,
                code=category.code,
                name=category.name,
                description=category.description,
                parent_id=category.parent_id,
                parent_name=parent_name,
                display_order=category.display_order,
                is_active=category.is_active,
                created_at=category.created_at,
                updated_at=category.updated_at,
            ))
        
        return ProductCategoryListResponse(
            items=category_responses,
            total=total,
            page=page,
            size=size,
        )
    
    async def get_category_tree_with_products(
        self,
        include_products: bool = True,
        is_active: Optional[bool] = True,
    ) -> List[Dict[str, Any]]:
        """
        获取分类树结构（包含产品列表）
        
        Args:
            include_products: 是否包含产品列表
            is_active: 是否只查询激活的分类
        
        Returns:
            分类树列表
        """
        # 查询所有分类
        query = select(ProductCategory)
        if is_active is not None:
            query = query.where(ProductCategory.is_active == is_active)
        query = query.order_by(ProductCategory.display_order, ProductCategory.created_at)
        
        result = await self.db.execute(query)
        all_categories = list(result.scalars().all())
        
        # 构建分类字典（便于查找）
        category_dict = {cat.id: cat for cat in all_categories}
        
        # 如果包含产品，查询每个分类的产品数量
        category_product_counts = {}
        category_products = {}
        
        if include_products:
            # 查询所有激活的产品
            product_query = select(Product)
            if is_active is not None:
                product_query = product_query.where(Product.is_active == is_active)
            
            product_result = await self.db.execute(product_query)
            all_products = list(product_result.scalars().all())
            
            # 按分类分组产品
            for product in all_products:
                if product.category_id:
                    if product.category_id not in category_product_counts:
                        category_product_counts[product.category_id] = 0
                        category_products[product.category_id] = []
                    category_product_counts[product.category_id] += 1
                    category_products[product.category_id].append({
                        'id': product.id,
                        'name': product.name,
                        'code': product.code,
                        'enterprise_service_code': product.enterprise_service_code,
                        'is_active': product.is_active,
                    })
        
        # 递归构建树结构
        def build_tree(parent_id: Optional[str] = None) -> List[Dict[str, Any]]:
            children = []
            for category in all_categories:
                if (parent_id is None and category.parent_id is None) or \
                   (parent_id is not None and category.parent_id == parent_id):
                    # 获取产品数量（包括子分类的产品）
                    product_count = category_product_counts.get(category.id, 0)
                    
                    # 递归获取子分类
                    sub_children = build_tree(category.id)
                    
                    # 累加子分类的产品数量
                    for sub_child in sub_children:
                        product_count += sub_child.get('product_count', 0)
                    
                    category_data = {
                        'id': category.id,
                        'code': category.code,
                        'name': category.name,
                        'description': category.description,
                        'parent_id': category.parent_id,
                        'display_order': category.display_order,
                        'is_active': category.is_active,
                        'product_count': product_count,
                        'children': sub_children,
                    }
                    
                    # 如果包含产品，添加产品列表
                    if include_products:
                        category_data['products'] = category_products.get(category.id, [])
                    
                    children.append(category_data)
            
            return children
        
        return build_tree()

