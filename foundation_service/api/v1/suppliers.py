"""
企服供应商 API
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from common.schemas.response import Result
from foundation_service.services.supplier_service import SupplierService
from foundation_service.dependencies import get_db, get_current_user_id, get_current_user_roles
from common.models.organization import Organization

router = APIRouter()


class SupplierResponse(BaseModel):
    """供应商响应"""
    id: str
    name: str
    code: Optional[str]
    organization_type: str
    email: Optional[str]
    phone: Optional[str]
    is_active: bool
    is_locked: bool
    service_count: int = 0  # 服务数量
    created_at: Any
    updated_at: Any
    
    class Config:
        from_attributes = True


class SupplierListResponse(BaseModel):
    """供应商列表响应"""
    items: List[SupplierResponse]
    total: int
    page: int
    size: int


class SupplierServiceResponse(BaseModel):
    """供应商服务响应"""
    product_id: str
    product_name: str
    product_code: Optional[str]
    enterprise_service_code: Optional[str]
    category_id: Optional[str]
    category_name: Optional[str]
    service_type_id: Optional[str]
    service_type: Optional[str]
    service_subtype: Optional[str]
    status: str
    is_active: bool
    vendor_product_id: Optional[str]
    is_primary: bool
    is_available: bool
    cost_price_cny: Optional[float]
    cost_price_idr: Optional[float]
    processing_days: Optional[int]
    sales_prices: List[Dict[str, Any]]
    price_history: List[Dict[str, Any]]


class SupplierServiceListResponse(BaseModel):
    """供应商服务列表响应"""
    items: List[SupplierServiceResponse]
    total: int
    page: int
    size: int


class BatchAddProductsRequest(BaseModel):
    """批量添加产品请求"""
    product_ids: List[str] = Field(..., min_items=1, description="产品ID列表")
    default_cost_price_cny: Optional[float] = Field(None, description="默认成本价（人民币）")
    default_cost_price_idr: Optional[float] = Field(None, description="默认成本价（印尼盾）")
    is_available: bool = Field(True, description="是否可用")
    is_primary: bool = Field(False, description="是否主要供应商")


class BatchAddProductsResponse(BaseModel):
    """批量添加产品响应"""
    success_count: int
    failed_count: int
    success_product_ids: List[str]
    failed_product_ids: List[str]


class PriceUpdateItem(BaseModel):
    """价格更新项"""
    product_id: str = Field(..., description="产品ID")
    cost_price_cny: Optional[float] = Field(None, description="成本价（人民币）")
    cost_price_idr: Optional[float] = Field(None, description="成本价（印尼盾）")
    processing_days: Optional[int] = Field(None, description="处理天数")
    is_available: Optional[bool] = Field(None, description="是否可用")
    is_primary: Optional[bool] = Field(None, description="是否主要供应商")
    priority: Optional[int] = Field(None, description="优先级")


class BatchUpdatePricesRequest(BaseModel):
    """批量更新价格请求"""
    updates: List[PriceUpdateItem] = Field(..., min_items=1, description="更新列表")


class BatchUpdatePricesResponse(BaseModel):
    """批量更新价格响应"""
    success_count: int
    failed_count: int
    failed_product_ids: List[str]


@router.get("", response_model=Result[SupplierListResponse])
async def get_supplier_list(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    name: Optional[str] = None,
    code: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_locked: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    查询供应商列表
    
    GET /api/service-management/suppliers
    """
    service = SupplierService(db)
    items, total, service_counts = await service.get_supplier_list(
        page=page,
        size=size,
        name=name,
        code=code,
        is_active=is_active,
        is_locked=is_locked,
    )
    
    # 转换为响应格式
    supplier_responses = [
        SupplierResponse(
            id=item.id,
            name=item.name,
            code=item.code,
            organization_type=item.organization_type,
            email=item.email,
            phone=item.phone,
            is_active=item.is_active,
            is_locked=item.is_locked,
            service_count=service_counts.get(item.id, 0),
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
        for item in items
    ]
    
    return Result.success(data=SupplierListResponse(
        items=supplier_responses,
        total=total,
        page=page,
        size=size,
    ))


@router.get("/{supplier_id}", response_model=Result[SupplierResponse])
async def get_supplier_detail(
    supplier_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    查询供应商详情
    
    GET /api/service-management/suppliers/{supplier_id}
    """
    service = SupplierService(db)
    supplier = await service.get_supplier_detail(supplier_id)
    
    return Result.success(data=SupplierResponse(
        id=supplier.id,
        name=supplier.name,
        code=supplier.code,
        organization_type=supplier.organization_type,
        email=supplier.email,
        phone=supplier.phone,
        is_active=supplier.is_active,
        is_locked=supplier.is_locked,
        created_at=supplier.created_at,
        updated_at=supplier.updated_at,
    ))


@router.get("/{supplier_id}/services", response_model=Result[SupplierServiceListResponse])
async def get_supplier_services(
    supplier_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    is_available: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    查询供应商提供的所有服务和价格
    
    GET /api/service-management/suppliers/{supplier_id}/services
    """
    service = SupplierService(db)
    items, total = await service.get_supplier_services(
        supplier_id=supplier_id,
        page=page,
        size=size,
        is_available=is_available,
    )
    
    # 转换为响应格式
    service_responses = [
        SupplierServiceResponse(**item)
        for item in items
    ]
    
    return Result.success(data=SupplierServiceListResponse(
        items=service_responses,
        total=total,
        page=page,
        size=size,
    ))


@router.get("/{supplier_id}/services/{product_id}/prices", response_model=Result[List[Dict[str, Any]]])
async def get_supplier_service_prices(
    supplier_id: str,
    product_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    查询价格历史
    
    GET /api/service-management/suppliers/{supplier_id}/services/{product_id}/prices
    """
    service = SupplierService(db)
    prices = await service.get_supplier_service_prices(
        supplier_id=supplier_id,
        product_id=product_id,
    )
    
    return Result.success(data=prices)


@router.post("/{supplier_id}/products/batch", response_model=Result[BatchAddProductsResponse])
async def batch_add_supplier_products(
    supplier_id: str,
    request: BatchAddProductsRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    批量添加供应商产品（仅系统管理员）
    
    POST /api/service-management/suppliers/{supplier_id}/products/batch
    """
    current_user_id = get_current_user_id(request_obj)
    current_user_roles = get_current_user_roles(request_obj)
    
    service = SupplierService(db)
    result = await service.batch_add_products(
        supplier_id=supplier_id,
        product_ids=request.product_ids,
        default_cost_price_cny=request.default_cost_price_cny,
        default_cost_price_idr=request.default_cost_price_idr,
        is_available=request.is_available,
        is_primary=request.is_primary,
        current_user_id=current_user_id,
        current_user_roles=current_user_roles,
    )
    
    return Result.success(data=BatchAddProductsResponse(**result))


@router.put("/{supplier_id}/products/batch-prices", response_model=Result[BatchUpdatePricesResponse])
async def batch_update_supplier_prices(
    supplier_id: str,
    request: BatchUpdatePricesRequest,
    request_obj: Request,
    effective_from: Optional[datetime] = Query(None, description="价格生效时间"),
    db: AsyncSession = Depends(get_db)
):
    """
    批量更新供应商产品价格（仅系统管理员）
    
    PUT /api/service-management/suppliers/{supplier_id}/products/batch-prices
    """
    current_user_id = get_current_user_id(request_obj)
    current_user_roles = get_current_user_roles(request_obj)
    
    service = SupplierService(db)
    
    # 转换请求数据
    updates = [item.dict(exclude_none=True) for item in request.updates]
    
    result = await service.batch_update_prices(
        supplier_id=supplier_id,
        updates=updates,
        current_user_id=current_user_id,
        current_user_roles=current_user_roles,
        effective_from=effective_from,
    )
    
    return Result.success(data=BatchUpdatePricesResponse(**result))


@router.get("/{supplier_id}/products/existing", response_model=Result[List[str]])
async def get_existing_supplier_product_ids(
    supplier_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取供应商已添加的产品ID列表
    
    GET /api/service-management/suppliers/{supplier_id}/products/existing
    """
    service = SupplierService(db)
    product_ids = await service.get_existing_product_ids(supplier_id)
    
    return Result.success(data=product_ids)


class UpdatePriceRequest(BaseModel):
    """更新价格请求"""
    cost_price_cny: Optional[float] = Field(None, description="成本价（人民币）")
    cost_price_idr: Optional[float] = Field(None, description="成本价（印尼盾）")
    effective_from: Optional[datetime] = Field(None, description="价格生效时间（如果为None则默认为当天+1天）")


@router.put("/{supplier_id}/services/{product_id}/price", response_model=Result[Dict[str, Any]])
async def update_vendor_product_price(
    supplier_id: str,
    product_id: str,
    request: UpdatePriceRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    更新供应商产品价格（支持双价格和生效时间）
    
    PUT /api/service-management/suppliers/{supplier_id}/services/{product_id}/price
    """
    current_user_id = get_current_user_id(request_obj)
    current_user_roles = get_current_user_roles(request_obj)
    
    service = SupplierService(db)
    result = await service.update_vendor_product_price(
        supplier_id=supplier_id,
        product_id=product_id,
        cost_price_cny=request.cost_price_cny,
        cost_price_idr=request.cost_price_idr,
        effective_from=request.effective_from,
        current_user_id=current_user_id,
        current_user_roles=current_user_roles,
    )
    
    return Result.success(data=result)
