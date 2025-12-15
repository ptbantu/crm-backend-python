"""
产品分类管理 API
"""
from typing import Optional, Dict
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from foundation_service.schemas.product_category import (
    ProductCategoryResponse,
    ProductCategoryCreateRequest,
    ProductCategoryUpdateRequest,
    ProductCategoryListResponse,
)
from foundation_service.services.product_category_service import ProductCategoryService
from foundation_service.dependencies import get_db

router = APIRouter()


@router.post("", response_model=Result[ProductCategoryResponse])
async def create_category(
    request: ProductCategoryCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """创建产品分类"""
    service = ProductCategoryService(db)
    category = await service.create_category(request)
    return Result.success(data=category, message="产品分类创建成功")


@router.get("/tree", response_model=Result[Dict])
async def get_category_tree(
    include_products: bool = Query(True, description="是否包含产品列表"),
    is_active: Optional[bool] = Query(True, description="是否只查询激活的分类"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取分类树（包含产品列表）
    
    GET /api/service-management/categories/tree
    """
    service = ProductCategoryService(db)
    tree = await service.get_category_tree_with_products(
        include_products=include_products,
        is_active=is_active,
    )
    return Result.success(data={'categories': tree})


@router.get("/{category_id}", response_model=Result[ProductCategoryResponse])
async def get_category(
    category_id: str,
    db: AsyncSession = Depends(get_db)
):
    """查询产品分类详情"""
    service = ProductCategoryService(db)
    category = await service.get_category_by_id(category_id)
    return Result.success(data=category)


@router.put("/{category_id}", response_model=Result[ProductCategoryResponse])
async def update_category(
    category_id: str,
    request: ProductCategoryUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """更新产品分类"""
    service = ProductCategoryService(db)
    category = await service.update_category(category_id, request)
    return Result.success(data=category, message="产品分类更新成功")


@router.delete("/{category_id}", response_model=Result[None])
async def delete_category(
    category_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除产品分类"""
    service = ProductCategoryService(db)
    await service.delete_category(category_id)
    return Result.success(message="产品分类删除成功")


@router.get("", response_model=Result[ProductCategoryListResponse])
async def get_category_list(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=1000),
    code: Optional[str] = None,
    name: Optional[str] = None,
    parent_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """分页查询产品分类列表"""
    service = ProductCategoryService(db)
    result = await service.get_category_list(
        page=page,
        size=size,
        code=code,
        name=name,
        parent_id=parent_id,
        is_active=is_active,
    )
    return Result.success(data=result)

