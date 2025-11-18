"""
产品分类服务
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from service_management.schemas.product_category import (
    ProductCategoryCreateRequest,
    ProductCategoryUpdateRequest,
    ProductCategoryResponse,
    ProductCategoryListResponse,
)
from service_management.repositories.product_category_repository import ProductCategoryRepository
from service_management.models.product_category import ProductCategory
from common.exceptions import BusinessException


class ProductCategoryService:
    """产品分类服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.category_repo = ProductCategoryRepository(db)
    
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

