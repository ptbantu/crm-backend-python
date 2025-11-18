"""
产品分类管理 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from service_management.schemas.product_category import (
    ProductCategoryResponse,
    ProductCategoryCreateRequest,
    ProductCategoryUpdateRequest,
    ProductCategoryListResponse,
)
from service_management.services.product_category_service import ProductCategoryService
from service_management.dependencies import get_db

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
    size: int = Query(10, ge=1, le=100),
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

