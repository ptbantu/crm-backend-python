"""
产品/服务管理 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from service_management.schemas.product import (
    ProductResponse,
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductListResponse,
)
from service_management.services.product_service import ProductService
from service_management.dependencies import get_db

router = APIRouter()


@router.post("", response_model=Result[ProductResponse])
async def create_product(
    request: ProductCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """创建产品/服务"""
    service = ProductService(db)
    product = await service.create_product(request)
    return Result.success(data=product, message="产品/服务创建成功")


@router.get("/{product_id}", response_model=Result[ProductResponse])
async def get_product(
    product_id: str,
    db: AsyncSession = Depends(get_db)
):
    """查询产品/服务详情"""
    service = ProductService(db)
    product = await service.get_product_by_id(product_id)
    return Result.success(data=product)


@router.put("/{product_id}", response_model=Result[ProductResponse])
async def update_product(
    product_id: str,
    request: ProductUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """更新产品/服务"""
    service = ProductService(db)
    product = await service.update_product(product_id, request)
    return Result.success(data=product, message="产品/服务更新成功")


@router.delete("/{product_id}", response_model=Result[None])
async def delete_product(
    product_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除产品/服务"""
    service = ProductService(db)
    await service.delete_product(product_id)
    return Result.success(message="产品/服务删除成功")


@router.get("", response_model=Result[ProductListResponse])
async def get_product_list(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    name: Optional[str] = None,
    code: Optional[str] = None,
    category_id: Optional[str] = None,
    service_type_id: Optional[str] = None,
    service_type: Optional[str] = None,
    service_subtype: Optional[str] = None,
    status: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """分页查询产品/服务列表"""
    service = ProductService(db)
    result = await service.get_product_list(
        page=page,
        size=size,
        name=name,
        code=code,
        category_id=category_id,
        service_type_id=service_type_id,
        service_type=service_type,
        service_subtype=service_subtype,
        status=status,
        is_active=is_active,
    )
    return Result.success(data=result)


@router.get("/vendors/{vendor_id}", response_model=Result[ProductListResponse])
async def get_products_by_vendor(
    vendor_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    is_available: Optional[bool] = None,
    is_primary: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    查询某个供应商提供的所有产品/服务
    
    - **vendor_id**: 供应商组织ID
    - **page**: 页码，从1开始
    - **size**: 每页数量，最大100
    - **is_available**: 是否可用（可选，true/false）
    - **is_primary**: 是否主要供应商（可选，true/false）
    """
    service = ProductService(db)
    result = await service.get_products_by_vendor(
        vendor_id=vendor_id,
        page=page,
        size=size,
        is_available=is_available,
        is_primary=is_primary,
    )
    return Result.success(data=result)

