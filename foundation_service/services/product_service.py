"""
产品/服务服务
"""
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, text
import logging
from foundation_service.schemas.product import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
    ProductListResponse,
    ProductDetailAggregatedResponse,
    PriceInfo,
    SupplierInfo,
    ProductStatistics,
    ChangeHistoryItem,
    ProductRules,
)
from foundation_service.repositories.product_repository import ProductRepository
from foundation_service.repositories.product_category_repository import ProductCategoryRepository
from foundation_service.repositories.vendor_product_repository import VendorProductRepository
from foundation_service.repositories.service_type_repository import ServiceTypeRepository
from foundation_service.services.enterprise_service_code_service import EnterpriseServiceCodeService
from foundation_service.services.product_price_sync_service import ProductPriceSyncService
from common.models.product import Product
from common.models.product_price import ProductPrice
from common.exceptions import BusinessException
from datetime import datetime


class ProductService:
    """产品/服务服务"""
    
    def __init__(self, db: AsyncSession, user_id: Optional[str] = None):
        self.db = db
        self.user_id = user_id
        self.product_repo = ProductRepository(db)
        self.category_repo = ProductCategoryRepository(db)
        self.service_type_repo = ServiceTypeRepository(db)
        self.vendor_product_repo = VendorProductRepository(db)
        self.code_service = EnterpriseServiceCodeService(db)
        self.price_sync_service = ProductPriceSyncService(db, user_id=user_id)
    
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
        
        # 如果提供了 category_id 和 service_type_id，自动生成企业服务编码
        enterprise_service_code = None
        if request.category_id and request.service_type_id:
            try:
                enterprise_service_code = await self.code_service.generate_code(
                    category_id=request.category_id,
                    service_type_id=request.service_type_id,
                )
            except BusinessException as e:
                # 如果编码生成失败，记录错误但不阻止产品创建
                # 编码字段可以为空
                pass
        
        # 创建产品
        product = Product(
            name=request.name,
            code=request.code,
            enterprise_service_code=enterprise_service_code,
            category_id=request.category_id,
            service_type_id=request.service_type_id,
            service_type=request.service_type,
            service_subtype=request.service_subtype,
            validity_period=request.validity_period,
            processing_days=request.processing_days,
            processing_time_text=request.processing_time_text,
            is_urgent_available=request.is_urgent_available,
            urgent_processing_days=request.urgent_processing_days,
            urgent_price_surcharge=request.urgent_price_surcharge,
            # 注意：price_cost_idr 和 price_cost_cny 已迁移到 product_prices 表
            # 注意：estimated_cost_idr 和 estimated_cost_cny 已删除
            # 注意：销售价格（渠道价、直客价、列表价）已迁移到 product_prices 表
            # 不再在 products 表中设置这些字段
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
        
        # 同步价格到 product_prices 表（如果提供了价格）
        try:
            await self.price_sync_service.sync_product_prices(
                product_id=product.id,
                price_channel_idr=request.price_channel_idr,
                price_channel_cny=request.price_channel_cny,
                price_direct_idr=request.price_direct_idr,
                price_direct_cny=request.price_direct_cny,
                price_list_idr=request.price_list_idr,
                price_list_cny=request.price_list_cny,
                price_cost_idr=request.price_cost_idr,  # 成本价同步到 product_prices 表
                price_cost_cny=request.price_cost_cny,  # 成本价同步到 product_prices 表
                exchange_rate=request.exchange_rate,
                change_reason="产品创建时设置价格"
            )
        except Exception as e:
            # 价格同步失败不影响产品创建，只记录日志
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"同步产品价格失败: {e}", exc_info=True)
        
        # 获取分类名称
        category_name = None
        if product.category_id:
            category = await self.category_repo.get_by_id(product.category_id)
            if category:
                category_name = category.name
        
        return await self._to_response(product, category_name)
    
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
        
        return await self._to_response(product, category_name)
    
    async def update_product(self, product_id: str, request: ProductUpdateRequest) -> ProductResponse:
        """更新产品"""
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise BusinessException(detail="产品不存在", status_code=404)
        
        # 如果更新分类或服务类型，验证并重新生成编码
        category_changed = request.category_id is not None and request.category_id != product.category_id
        service_type_changed = request.service_type_id is not None and request.service_type_id != product.service_type_id
        
        if category_changed or service_type_changed:
            # 验证分类
            new_category_id = request.category_id if category_changed else product.category_id
            if new_category_id:
                category = await self.category_repo.get_by_id(new_category_id)
                if not category:
                    raise BusinessException(detail="分类不存在")
                if not category.is_active:
                    raise BusinessException(detail="分类未激活")
            
            # 如果分类或服务类型改变，重新生成编码
            new_service_type_id = request.service_type_id if service_type_changed else product.service_type_id
            if new_category_id and new_service_type_id:
                try:
                    enterprise_service_code = await self.code_service.generate_code(
                        category_id=new_category_id,
                        service_type_id=new_service_type_id,
                    )
                    product.enterprise_service_code = enterprise_service_code
                except BusinessException as e:
                    # 如果编码生成失败，记录错误但不阻止更新
                    pass
        
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
        if request.service_type_id is not None:
            product.service_type_id = request.service_type_id
        
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
        
        # 注意：成本价已迁移到 product_prices 表，不再直接更新 products 表
        # 成本价通过 ProductPriceSyncService 同步到 product_prices 表
        # 注意：estimated_cost_idr 和 estimated_cost_cny 已删除
        
        # 同步价格到 product_prices 表（如果请求中包含价格字段）
        # 注意：销售价格和成本价字段已从 products 表移除，现在只通过 product_prices 表管理
        price_updated = any([
            request.price_channel_idr is not None,
            request.price_channel_cny is not None,
            request.price_direct_idr is not None,
            request.price_direct_cny is not None,
            request.price_list_idr is not None,
            request.price_list_cny is not None,
            request.price_cost_idr is not None,  # 成本价也同步到 product_prices 表
            request.price_cost_cny is not None,  # 成本价也同步到 product_prices 表
        ])
        
        if price_updated:
            try:
                # 同步价格到 product_prices 表（只使用请求中的值）
                await self.price_sync_service.sync_product_prices(
                    product_id=product.id,
                    price_channel_idr=request.price_channel_idr,
                    price_channel_cny=request.price_channel_cny,
                    price_direct_idr=request.price_direct_idr,
                    price_direct_cny=request.price_direct_cny,
                    price_list_idr=request.price_list_idr,
                    price_list_cny=request.price_list_cny,
                    price_cost_idr=request.price_cost_idr,  # 成本价同步到 product_prices 表
                    price_cost_cny=request.price_cost_cny,  # 成本价同步到 product_prices 表
                    exchange_rate=request.exchange_rate,
                    change_reason="产品更新时修改价格"
                )
            except Exception as e:
                # 价格同步失败不影响产品更新，只记录日志
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"同步产品价格失败: {e}", exc_info=True)
        
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
        
        return await self._to_response(product, category_name)
    
    async def get_product_detail_aggregated(self, product_id: str) -> ProductDetailAggregatedResponse:
        """获取产品详情聚合数据（包含价格、供应商、统计等信息）"""
        logger = logging.getLogger(__name__)
        
        # 1. 基本信息（必需成功）
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise BusinessException(detail="产品不存在", status_code=404)
        
        # 获取分类名称
        category_name = None
        if product.category_id:
            try:
                category = await self.category_repo.get_by_id(product.category_id)
                if category:
                    category_name = category.name
            except Exception as e:
                logger.warning(f"获取分类信息失败: {e}")
        
        overview = await self._to_response(product, category_name)
        
        # 初始化结果
        result = ProductDetailAggregatedResponse(
            overview=overview,
            prices=[],
            suppliers=[],
            statistics=ProductStatistics(),
            history=[],
            rules=ProductRules(
                required_documents=product.required_documents,
                notes=product.notes
            )
        )
        
        # 2. 价格信息（可选，失败时返回空列表）
        try:
            from foundation_service.repositories.product_price_history_repository import ProductPriceHistoryRepository
            price_repo = ProductPriceHistoryRepository(self.db)
            
            # 查询当前价格和未来价格
            now = datetime.now()
            prices, _ = await price_repo.get_by_product_id(product_id, page=1, size=100)
            
            # 列格式：一条记录包含所有价格类型和货币
            # 只返回当前有效的价格记录
            current_price = None
            for price in prices:
                # 判断价格状态
                if price.effective_from and price.effective_from > now:
                    continue  # 跳过未来价格
                elif price.effective_to and price.effective_to < now:
                    continue  # 跳过已失效价格
                else:
                    # 当前有效价格
                    current_price = price
                    break
            
            # 如果有当前有效价格，转换为 PriceInfo 列表（为了兼容前端）
            # 注意：PriceInfo 仍使用旧的结构，但这里我们只返回一条记录的所有价格字段
            if current_price:
                # 创建一个包含所有价格信息的 PriceInfo
                # 由于 PriceInfo 仍使用旧结构，这里暂时只返回主要价格
                # TODO: 更新 PriceInfo Schema 以适配列格式
                price_list = []
                if current_price.price_channel_idr is not None:
                    price_list.append(PriceInfo(
                        price_type="channel",
                        currency="IDR",
                        price=current_price.price_channel_idr,
                        effective_from=current_price.effective_from,
                        effective_to=current_price.effective_to,
                        updated_at=current_price.updated_at,
                        status="active"
                    ))
                if current_price.price_channel_cny is not None:
                    price_list.append(PriceInfo(
                        price_type="channel",
                        currency="CNY",
                        price=current_price.price_channel_cny,
                        effective_from=current_price.effective_from,
                        effective_to=current_price.effective_to,
                        updated_at=current_price.updated_at,
                        status="active"
                    ))
                if current_price.price_direct_idr is not None:
                    price_list.append(PriceInfo(
                        price_type="direct",
                        currency="IDR",
                        price=current_price.price_direct_idr,
                        effective_from=current_price.effective_from,
                        effective_to=current_price.effective_to,
                        updated_at=current_price.updated_at,
                        status="active"
                    ))
                if current_price.price_direct_cny is not None:
                    price_list.append(PriceInfo(
                        price_type="direct",
                        currency="CNY",
                        price=current_price.price_direct_cny,
                        effective_from=current_price.effective_from,
                        effective_to=current_price.effective_to,
                        updated_at=current_price.updated_at,
                        status="active"
                    ))
                if current_price.price_list_idr is not None:
                    price_list.append(PriceInfo(
                        price_type="list",
                        currency="IDR",
                        price=current_price.price_list_idr,
                        effective_from=current_price.effective_from,
                        effective_to=current_price.effective_to,
                        updated_at=current_price.updated_at,
                        status="active"
                    ))
                if current_price.price_list_cny is not None:
                    price_list.append(PriceInfo(
                        price_type="list",
                        currency="CNY",
                        price=current_price.price_list_cny,
                        effective_from=current_price.effective_from,
                        effective_to=current_price.effective_to,
                        updated_at=current_price.updated_at,
                        status="active"
                    ))
                
                result.prices = price_list
            else:
                result.prices = []
        except Exception as e:
            logger.warning(f"获取产品价格信息失败: {e}", exc_info=True)
        
        # 3. 供应商信息（可选，失败时返回空列表）
        try:
            # 查询该产品的供应商
            vendor_products = await self.vendor_product_repo.get_by_product_id(product_id)
            
            supplier_list = []
            for vp in vendor_products:
                vendor_name = None
                contact_name = None
                contact_phone = None
                contact_email = None
                address = None
                
                # 查询供应商组织信息
                try:
                    org_repo = OrganizationRepository(self.db)
                    org = await org_repo.get_by_id(vp.organization_id)
                    if org:
                        vendor_name = org.name
                        # 可以从组织关联的联系人获取联系信息
                except Exception as e:
                    logger.debug(f"获取供应商组织信息失败: {e}")
                
                supplier_list.append(SupplierInfo(
                    vendor_id=vp.organization_id,
                    vendor_name=vendor_name,
                    is_primary=vp.is_primary or False,
                    is_available=vp.is_available if vp.is_available is not None else True,
                    priority=vp.priority,
                    contact_name=contact_name,
                    contact_phone=contact_phone,
                    contact_email=contact_email,
                    address=address,
                    sla_description=None,  # vendor_product表没有这个字段
                    contract_start=vp.available_from,
                    contract_end=vp.available_to
                ))
            
            result.suppliers = supplier_list
        except Exception as e:
            logger.warning(f"获取供应商信息失败: {e}", exc_info=True)
        
        # 4. 统计信息（可选，失败时返回默认值）
        try:
            from common.models.service_record import ServiceRecord
            from common.models.order import Order
            
            now = datetime.now()
            month_start = datetime(now.year, now.month, 1)
            
            # 查询服务记录统计
            sr_query = select(
                func.count(ServiceRecord.id).label('total'),
                func.sum(ServiceRecord.final_price).label('total_revenue')
            ).where(ServiceRecord.product_id == product_id)
            
            sr_result = await self.db.execute(sr_query)
            sr_row = sr_result.first()
            total_orders = sr_row.total or 0 if sr_row else 0
            total_revenue = sr_row.total_revenue if sr_row and sr_row.total_revenue else Decimal('0')
            
            # 本月订单
            sr_month_query = select(
                func.count(ServiceRecord.id).label('monthly')
            ).where(
                and_(
                    ServiceRecord.product_id == product_id,
                    ServiceRecord.created_at >= month_start
                )
            )
            sr_month_result = await self.db.execute(sr_month_query)
            monthly_orders = sr_month_result.scalar() or 0
            
            # 本月收入
            sr_month_revenue_query = select(
                func.sum(ServiceRecord.final_price).label('monthly_revenue')
            ).where(
                and_(
                    ServiceRecord.product_id == product_id,
                    ServiceRecord.created_at >= month_start
                )
            )
            sr_month_revenue_result = await self.db.execute(sr_month_revenue_query)
            monthly_revenue = sr_month_revenue_result.scalar() or Decimal('0')
            
            # 完成率（已完成订单 / 总订单）
            completed_query = select(
                func.count(ServiceRecord.id).label('completed')
            ).where(
                and_(
                    ServiceRecord.product_id == product_id,
                    ServiceRecord.status == 'completed'
                )
            )
            completed_result = await self.db.execute(completed_query)
            completed_count = completed_result.scalar() or 0
            completion_rate = (Decimal(completed_count) / Decimal(total_orders) * 100) if total_orders > 0 else None
            
            # 平均处理天数（使用MySQL的DATEDIFF函数）
            # MySQL的DATEDIFF(date1, date2)返回date1-date2的天数差
            avg_days_query = text("""
                SELECT AVG(DATEDIFF(actual_completion_date, actual_start_date)) as avg_days
                FROM service_records
                WHERE product_id = :product_id
                  AND status = 'completed'
                  AND actual_start_date IS NOT NULL
                  AND actual_completion_date IS NOT NULL
            """)
            avg_days_result = await self.db.execute(avg_days_query, {"product_id": product_id})
            avg_processing_days = avg_days_result.scalar()
            
            result.statistics = ProductStatistics(
                total_orders=total_orders,
                monthly_orders=monthly_orders,
                total_revenue=total_revenue if total_revenue else None,
                monthly_revenue=monthly_revenue if monthly_revenue else None,
                completion_rate=completion_rate,
                customer_rating=None,  # 需要从评价表查询
                refund_rate=None,  # 需要从退款记录查询
                avg_processing_days=Decimal(str(avg_processing_days)) if avg_processing_days else None
            )
        except Exception as e:
            logger.warning(f"获取统计信息失败: {e}", exc_info=True)
        
        # 5. 变更历史（可选，失败时返回空列表）
        try:
            from common.models.operation_audit_log import OperationAuditLog
            from foundation_service.repositories.organization_repository import OrganizationRepository
            
            history_query = select(OperationAuditLog).where(
                and_(
                    OperationAuditLog.entity_type == 'products',
                    OperationAuditLog.entity_id == product_id
                )
            ).order_by(desc(OperationAuditLog.operated_at)).limit(10)
            
            history_result = await self.db.execute(history_query)
            history_records = history_result.scalars().all()
            
            history_list = []
            for record in history_records:
                # 从changed_fields解析变更字段
                field_name = None
                if record.changed_fields and isinstance(record.changed_fields, list) and len(record.changed_fields) > 0:
                    field_name = record.changed_fields[0]
                
                history_list.append(ChangeHistoryItem(
                    changed_at=record.operated_at,
                    changed_by=record.user_id,
                    changed_by_name=record.username,
                    change_type=record.operation_type or "update",
                    field_name=field_name,
                    old_value=None,  # 可以从data_before解析
                    new_value=None,  # 可以从data_after解析
                    description=f"{record.operation_type} - {record.entity_type}"
                ))
            
            result.history = history_list
        except Exception as e:
            logger.warning(f"获取变更历史失败: {e}", exc_info=True)
        
        return result
    
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
        group_by_category: bool = False,
    ) -> ProductListResponse:
        """分页查询产品列表"""
        if group_by_category:
            # 按分类分组时，获取所有数据（不分页）
            items, total = await self.product_repo.get_list_grouped_by_category(
                name=name,
                code=code,
                category_id=category_id,
                service_type_id=service_type_id,
                service_type=service_type,
                service_subtype=service_subtype,
                status=status,
                is_active=is_active,
            )
        else:
            # 普通分页查询
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
            
            product_responses.append(await self._to_response(product, category_name))
        
        return ProductListResponse(
            items=product_responses,
            total=total,
            page=page if not group_by_category else 1,
            size=size if not group_by_category else total,
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
        from foundation_service.repositories.vendor_product_repository import VendorProductRepository
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
            
            product_responses.append(await self._to_response(product, category_name))
        
        return ProductListResponse(
            items=product_responses,
            total=total,
            page=page,
            size=size,
        )
    
    async def _get_current_price(self, product_id: str) -> Optional[ProductPrice]:
        """从 product_prices 表获取当前有效的价格记录（包含所有价格类型）"""
        now = datetime.now()
        query = select(ProductPrice).where(
            and_(
                ProductPrice.product_id == product_id,
                ProductPrice.organization_id.is_(None),  # 通用价格
                ProductPrice.effective_from <= now,
                or_(
                    ProductPrice.effective_to.is_(None),
                    ProductPrice.effective_to >= now
                )
            )
        ).order_by(ProductPrice.effective_from.desc()).limit(1)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _to_response(self, product: Product, category_name: str = None, service_type_name: str = None) -> ProductResponse:
        """转换为响应格式"""
        # 从 product_prices 表查询当前有效的价格记录（包含所有价格类型）
        price_record = await self._get_current_price(product.id)
        
        return ProductResponse(
            id=product.id,
            name=product.name,
            code=product.code,
            enterprise_service_code=product.enterprise_service_code,
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
            # 注意：所有价格字段已迁移到 product_prices 表
            # 从 product_prices 表查询当前有效的价格（如果存在）
            price_cost_idr=price_record.price_cost_idr if price_record else None,
            price_cost_cny=price_record.price_cost_cny if price_record else None,
            price_channel_idr=price_record.price_channel_idr if price_record else None,
            price_channel_cny=price_record.price_channel_cny if price_record else None,
            price_direct_idr=price_record.price_direct_idr if price_record else None,
            price_direct_cny=price_record.price_direct_cny if price_record else None,
            price_list_idr=price_record.price_list_idr if price_record else None,
            price_list_cny=price_record.price_list_cny if price_record else None,
            exchange_rate=price_record.exchange_rate if price_record else None,
            # 注意：estimated_cost_idr 和 estimated_cost_cny 已删除
            estimated_cost_idr=None,
            estimated_cost_cny=None,
            # 注意：default_currency 已废弃
            default_currency=None,
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

