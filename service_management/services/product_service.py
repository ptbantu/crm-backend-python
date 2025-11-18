"""
产品/服务服务
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from service_management.schemas.product import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
    ProductListResponse,
)
from service_management.repositories.product_repository import ProductRepository
from service_management.repositories.product_category_repository import ProductCategoryRepository
from service_management.repositories.vendor_product_repository import VendorProductRepository
from service_management.repositories.service_type_repository import ServiceTypeRepository
from service_management.models.product import Product
from common.exceptions import BusinessException


class ProductService:
    """产品/服务服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.product_repo = ProductRepository(db)
        self.category_repo = ProductCategoryRepository(db)
        self.service_type_repo = ServiceTypeRepository(db)
        self.vendor_product_repo = VendorProductRepository(db)
    
    async def create_product(self, request: ProductCreateRequest) -> ProductResponse:
        """创建产品/服务"""
        # 检查编码是否已存在
        if request.code:
            existing = await self.product_repo.get_by_code(request.code)
            if existing:
                raise BusinessException(detail=f"产品编码 {request.code} 已存在")
        
        # 如果指定了分类，验证分类是否存在且激活
        if request.category_id:
            category = await self.category_repo.get_by_id(request.category_id)
            if not category:
                raise BusinessException(detail="分类不存在")
            if not category.is_active:
                raise BusinessException(detail="分类未激活")
        
        # 创建产品
        product = Product(
            name=request.name,
            code=request.code,
            category_id=request.category_id,
            service_type=request.service_type,
            service_subtype=request.service_subtype,
            validity_period=request.validity_period,
            processing_days=request.processing_days,
            processing_time_text=request.processing_time_text,
            is_urgent_available=request.is_urgent_available,
            urgent_processing_days=request.urgent_processing_days,
            urgent_price_surcharge=request.urgent_price_surcharge,
            price_cost_idr=request.price_cost_idr,
            price_cost_cny=request.price_cost_cny,
            price_channel_idr=request.price_channel_idr,
            price_channel_cny=request.price_channel_cny,
            price_direct_idr=request.price_direct_idr,
            price_direct_cny=request.price_direct_cny,
            price_list_idr=request.price_list_idr,
            price_list_cny=request.price_list_cny,
            default_currency=request.default_currency,
            exchange_rate=request.exchange_rate,
            commission_rate=request.commission_rate,
            commission_amount=request.commission_amount,
            equivalent_cny=request.equivalent_cny,
            monthly_orders=request.monthly_orders,
            total_amount=request.total_amount,
            sla_description=request.sla_description,
            service_level=request.service_level,
            status=request.status,
            suspended_reason=request.suspended_reason,
            required_documents=request.required_documents,
            notes=request.notes,
            tags=request.tags,
            is_active=request.is_active,
        )
        product = await self.product_repo.create(product)
        
        # 获取分类名称
        category_name = None
        if product.category_id:
            category = await self.category_repo.get_by_id(product.category_id)
            if category:
                category_name = category.name
        
        return self._to_response(product, category_name)
    
    async def get_product_by_id(self, product_id: str) -> ProductResponse:
        """查询产品详情"""
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise BusinessException(detail="产品不存在", status_code=404)
        
        # 获取分类名称
        category_name = None
        if product.category_id:
            category = await self.category_repo.get_by_id(product.category_id)
            if category:
                category_name = category.name
        
        return self._to_response(product, category_name)
    
    async def update_product(self, product_id: str, request: ProductUpdateRequest) -> ProductResponse:
        """更新产品"""
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise BusinessException(detail="产品不存在", status_code=404)
        
        # 如果更新分类，验证分类是否存在且激活
        if request.category_id is not None and request.category_id != product.category_id:
            if request.category_id:
                category = await self.category_repo.get_by_id(request.category_id)
                if not category:
                    raise BusinessException(detail="分类不存在")
                if not category.is_active:
                    raise BusinessException(detail="分类未激活")
        
        # 更新字段
        if request.name is not None:
            product.name = request.name
        if request.code is not None:
            # 检查编码是否已存在（排除自身）
            if request.code != product.code:
                existing = await self.product_repo.get_by_code(request.code)
                if existing:
                    raise BusinessException(detail=f"产品编码 {request.code} 已存在")
            product.code = request.code
        if request.category_id is not None:
            product.category_id = request.category_id
        
        # 更新服务属性
        if request.service_type is not None:
            product.service_type = request.service_type
        if request.service_subtype is not None:
            product.service_subtype = request.service_subtype
        if request.validity_period is not None:
            product.validity_period = request.validity_period
        if request.processing_days is not None:
            product.processing_days = request.processing_days
        if request.processing_time_text is not None:
            product.processing_time_text = request.processing_time_text
        if request.is_urgent_available is not None:
            product.is_urgent_available = request.is_urgent_available
        if request.urgent_processing_days is not None:
            product.urgent_processing_days = request.urgent_processing_days
        if request.urgent_price_surcharge is not None:
            product.urgent_price_surcharge = request.urgent_price_surcharge
        
        # 更新价格字段
        if request.price_cost_idr is not None:
            product.price_cost_idr = request.price_cost_idr
        if request.price_cost_cny is not None:
            product.price_cost_cny = request.price_cost_cny
        if request.price_channel_idr is not None:
            product.price_channel_idr = request.price_channel_idr
        if request.price_channel_cny is not None:
            product.price_channel_cny = request.price_channel_cny
        if request.price_direct_idr is not None:
            product.price_direct_idr = request.price_direct_idr
        if request.price_direct_cny is not None:
            product.price_direct_cny = request.price_direct_cny
        if request.price_list_idr is not None:
            product.price_list_idr = request.price_list_idr
        if request.price_list_cny is not None:
            product.price_list_cny = request.price_list_cny
        
        # 更新汇率
        if request.default_currency is not None:
            product.default_currency = request.default_currency
        if request.exchange_rate is not None:
            product.exchange_rate = request.exchange_rate
        
        # 更新业务属性
        if request.commission_rate is not None:
            product.commission_rate = request.commission_rate
        if request.commission_amount is not None:
            product.commission_amount = request.commission_amount
        if request.equivalent_cny is not None:
            product.equivalent_cny = request.equivalent_cny
        if request.monthly_orders is not None:
            product.monthly_orders = request.monthly_orders
        if request.total_amount is not None:
            product.total_amount = request.total_amount
        
        # 更新 SLA
        if request.sla_description is not None:
            product.sla_description = request.sla_description
        if request.service_level is not None:
            product.service_level = request.service_level
        
        # 更新状态
        if request.status is not None:
            product.status = request.status
        if request.suspended_reason is not None:
            product.suspended_reason = request.suspended_reason
        if request.discontinued_at is not None:
            product.discontinued_at = request.discontinued_at
        
        # 更新其他字段
        if request.required_documents is not None:
            product.required_documents = request.required_documents
        if request.notes is not None:
            product.notes = request.notes
        if request.tags is not None:
            product.tags = request.tags
        if request.is_active is not None:
            product.is_active = request.is_active
        
        product = await self.product_repo.update(product)
        
        # 获取分类名称
        category_name = None
        if product.category_id:
            category = await self.category_repo.get_by_id(product.category_id)
            if category:
                category_name = category.name
        
        return self._to_response(product, category_name)
    
    async def delete_product(self, product_id: str) -> None:
        """删除产品"""
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise BusinessException(detail="产品不存在", status_code=404)
        
        # TODO: 检查是否有订单或其他关联数据使用此产品
        
        await self.product_repo.delete(product)
    
    async def get_product_list(
        self,
        page: int = 1,
        size: int = 10,
        name: str = None,
        code: str = None,
        category_id: str = None,
        service_type_id: str = None,
        service_type: str = None,
        service_subtype: str = None,
        status: str = None,
        is_active: bool = None,
    ) -> ProductListResponse:
        """分页查询产品列表"""
        items, total = await self.product_repo.get_list(
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
        
        # 转换为响应格式
        product_responses = []
        for product in items:
            # 获取分类名称
            category_name = None
            if product.category_id:
                category = await self.category_repo.get_by_id(product.category_id)
                if category:
                    category_name = category.name
            
            product_responses.append(self._to_response(product, category_name))
        
        return ProductListResponse(
            items=product_responses,
            total=total,
            page=page,
            size=size,
        )
    
    async def get_products_by_vendor(
        self,
        vendor_id: str,
        page: int = 1,
        size: int = 10,
        is_available: bool = None,
        is_primary: bool = None,
    ) -> ProductListResponse:
        """
        查询某个供应商提供的所有产品/服务
        
        Args:
            vendor_id: 供应商组织ID
            page: 页码
            size: 每页数量
            is_available: 是否可用（可选）
            is_primary: 是否主要供应商（可选）
        
        Returns:
            产品列表响应
        """
        from service_management.repositories.vendor_product_repository import VendorProductRepository
        vendor_product_repo = VendorProductRepository(self.db)
        
        # 通过 vendor_products 表查询产品
        items, total = await vendor_product_repo.get_products_by_vendor(
            vendor_id=vendor_id,
            page=page,
            size=size,
            is_available=is_available,
            is_primary=is_primary,
        )
        
        # 转换为响应格式
        product_responses = []
        for product in items:
            # 获取分类名称
            category_name = None
            if product.category_id:
                category = await self.category_repo.get_by_id(product.category_id)
                if category:
                    category_name = category.name
            
            product_responses.append(self._to_response(product, category_name))
        
        return ProductListResponse(
            items=product_responses,
            total=total,
            page=page,
            size=size,
        )
    
    def _to_response(self, product: Product, category_name: str = None, service_type_name: str = None) -> ProductResponse:
        """转换为响应格式"""
        return ProductResponse(
            id=product.id,
            name=product.name,
            code=product.code,
            category_id=product.category_id,
            category_name=category_name,
            service_type_id=product.service_type_id,
            service_type_name=service_type_name,
            service_type=product.service_type,
            service_subtype=product.service_subtype,
            validity_period=product.validity_period,
            processing_days=product.processing_days,
            processing_time_text=product.processing_time_text,
            is_urgent_available=product.is_urgent_available,
            urgent_processing_days=product.urgent_processing_days,
            urgent_price_surcharge=product.urgent_price_surcharge,
            price_cost_idr=product.price_cost_idr,
            price_cost_cny=product.price_cost_cny,
            price_channel_idr=product.price_channel_idr,
            price_channel_cny=product.price_channel_cny,
            price_direct_idr=product.price_direct_idr,
            price_direct_cny=product.price_direct_cny,
            price_list_idr=product.price_list_idr,
            price_list_cny=product.price_list_cny,
            default_currency=product.default_currency,
            exchange_rate=product.exchange_rate,
            channel_profit=product.channel_profit,
            channel_profit_rate=product.channel_profit_rate,
            channel_customer_profit=product.channel_customer_profit,
            channel_customer_profit_rate=product.channel_customer_profit_rate,
            direct_profit=product.direct_profit,
            direct_profit_rate=product.direct_profit_rate,
            commission_rate=product.commission_rate,
            commission_amount=product.commission_amount,
            equivalent_cny=product.equivalent_cny,
            monthly_orders=product.monthly_orders,
            total_amount=product.total_amount,
            sla_description=product.sla_description,
            service_level=product.service_level,
            status=product.status,
            suspended_reason=product.suspended_reason,
            discontinued_at=product.discontinued_at,
            required_documents=product.required_documents,
            notes=product.notes,
            tags=product.tags or [],
            is_active=product.is_active,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )

