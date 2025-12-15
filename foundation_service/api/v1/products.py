"""
产品/服务管理 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from foundation_service.schemas.product import (
    ProductResponse,
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductListResponse,
)
from foundation_service.services.product_service import ProductService
from foundation_service.dependencies import get_db
from foundation_service.utils import log_audit_operation

router = APIRouter()


@router.post("", response_model=Result[ProductResponse])
async def create_product(
    request: ProductCreateRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """创建产品/服务"""
    try:
        service = ProductService(db)
        product = await service.create_product(request)
        
        # 记录审计日志
        await log_audit_operation(
            db=db,
            request=http_request,
            operation_type="CREATE",
            entity_type="products",
            entity_id=product.id,
            data_after=product.dict() if hasattr(product, 'dict') else None,
            status="SUCCESS"
        )
        
        return Result.success(data=product, message="产品/服务创建成功")
    except Exception as e:
        # 记录失败审计日志
        await log_audit_operation(
            db=db,
            request=http_request,
            operation_type="CREATE",
            entity_type="products",
            status="FAILURE",
            error_message=str(e),
            error_code=type(e).__name__
        )
        raise


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
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """更新产品/服务"""
    try:
        service = ProductService(db)
        
        # 查询更新前的数据
        old_product = await service.get_product_by_id(product_id)
        
        # 执行更新
        new_product = await service.update_product(product_id, request)
        
        # 计算变更字段
        changed_fields = []
        if old_product and new_product:
            old_dict = old_product.dict() if hasattr(old_product, 'dict') else {}
            new_dict = new_product.dict() if hasattr(new_product, 'dict') else {}
            changed_fields = [k for k in new_dict.keys() if old_dict.get(k) != new_dict.get(k)]
        
        # 记录审计日志
        await log_audit_operation(
            db=db,
            request=http_request,
            operation_type="UPDATE",
            entity_type="products",
            entity_id=product_id,
            data_before=old_product.dict() if old_product and hasattr(old_product, 'dict') else None,
            data_after=new_product.dict() if hasattr(new_product, 'dict') else None,
            changed_fields=changed_fields,
            status="SUCCESS"
        )
        
        return Result.success(data=new_product, message="产品/服务更新成功")
    except Exception as e:
        # 记录失败审计日志
        await log_audit_operation(
            db=db,
            request=http_request,
            operation_type="UPDATE",
            entity_type="products",
            entity_id=product_id,
            status="FAILURE",
            error_message=str(e),
            error_code=type(e).__name__
        )
        raise


@router.delete("/{product_id}", response_model=Result[None])
async def delete_product(
    product_id: str,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """删除产品/服务"""
    try:
        service = ProductService(db)
        
        # 查询删除前的数据
        product = await service.get_product_by_id(product_id)
        
        # 执行删除
        await service.delete_product(product_id)
        
        # 记录审计日志
        await log_audit_operation(
            db=db,
            request=http_request,
            operation_type="DELETE",
            entity_type="products",
            entity_id=product_id,
            data_before=product.dict() if product and hasattr(product, 'dict') else None,
            status="SUCCESS"
        )
        
        return Result.success(message="产品/服务删除成功")
    except Exception as e:
        # 记录失败审计日志
        await log_audit_operation(
            db=db,
            request=http_request,
            operation_type="DELETE",
            entity_type="products",
            entity_id=product_id,
            status="FAILURE",
            error_message=str(e),
            error_code=type(e).__name__
        )
        raise


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

