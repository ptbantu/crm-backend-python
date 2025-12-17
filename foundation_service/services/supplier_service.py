"""
企服供应商服务
提供供应商相关的业务逻辑
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from foundation_service.repositories.organization_repository import OrganizationRepository
from foundation_service.repositories.vendor_product_repository import VendorProductRepository
from foundation_service.repositories.product_repository import ProductRepository
from foundation_service.repositories.product_category_repository import ProductCategoryRepository
from common.models.organization import Organization
from common.models.vendor_product import VendorProduct
from common.models.product import Product
from common.models.product_price import ProductPrice
from common.models.product_price_history import ProductPriceHistory
from common.models.vendor_product_price_history import VendorProductPriceHistory
from common.exceptions import BusinessException


class SupplierService:
    """企服供应商服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.org_repo = OrganizationRepository(db)
        self.vendor_product_repo = VendorProductRepository(db)
        self.product_repo = ProductRepository(db)
        self.category_repo = ProductCategoryRepository(db)
    
    async def get_supplier_list(
        self,
        page: int = 1,
        size: int = 10,
        name: Optional[str] = None,
        code: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_locked: Optional[bool] = None,
    ) -> tuple[List[Organization], int, Dict[str, int]]:
        """
        获取供应商列表（organization_type='vendor'）
        
        Args:
            page: 页码
            size: 每页数量
            name: 供应商名称（模糊搜索）
            code: 供应商代码
            is_active: 是否激活
            is_locked: 是否锁定
        
        Returns:
            (供应商列表, 总数, 服务数量字典)
        """
        items, total = await self.org_repo.get_list(
            page=page,
            size=size,
            name=name,
            code=code,
            organization_type='vendor',
            is_active=is_active,
            is_locked=is_locked,
        )
        
        # 批量获取每个供应商的服务数量
        vendor_ids = [item.id for item in items]
        service_counts = await self.vendor_product_repo.get_service_counts_by_vendors(vendor_ids)
        
        return items, total, service_counts
    
    async def get_supplier_detail(self, supplier_id: str) -> Organization:
        """
        获取供应商详情
        
        Args:
            supplier_id: 供应商ID
        
        Returns:
            供应商组织对象
        
        Raises:
            BusinessException: 如果供应商不存在或不是vendor类型
        """
        supplier = await self.org_repo.get_by_id(supplier_id)
        if not supplier:
            raise BusinessException(detail="供应商不存在", status_code=404)
        
        if supplier.organization_type != 'vendor':
            raise BusinessException(detail="该组织不是供应商", status_code=400)
        
        return supplier
    
    async def get_supplier_services(
        self,
        supplier_id: str,
        page: int = 1,
        size: int = 10,
        is_available: Optional[bool] = None,
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        获取供应商提供的所有服务和价格
        
        通过 vendor_products 表关联查询，返回：
        - 服务信息
        - 成本价格（CNY/IDR）
        - 关联的销售价格（从 product_prices 表查询）
        
        Args:
            supplier_id: 供应商ID
            page: 页码
            size: 每页数量
            is_available: 是否可用
        
        Returns:
            (服务列表, 总数)
        """
        # 验证供应商存在
        await self.get_supplier_detail(supplier_id)
        
        # 获取供应商提供的产品列表
        products, total = await self.vendor_product_repo.get_products_by_vendor(
            vendor_id=supplier_id,
            page=page,
            size=size,
            is_available=is_available,
        )
        
        # 构建返回数据
        service_list = []
        for product in products:
            # 获取供应商产品关联信息（包含成本价）
            vendor_product = await self.vendor_product_repo.get_vendor_product_info(
                vendor_id=supplier_id,
                product_id=product.id,
            )
            
            # 获取分类名称
            category_name = None
            if product.category_id:
                category = await self.category_repo.get_by_id(product.category_id)
                if category:
                    category_name = category.name
            
            # 获取销售价格（从 product_prices 表查询）
            sales_prices = await self._get_product_sales_prices(product.id, supplier_id)
            
            service_data = {
                'product_id': product.id,
                'product_name': product.name,
                'product_code': product.code,
                'enterprise_service_code': product.enterprise_service_code,
                'category_id': product.category_id,
                'category_name': category_name,
                'service_type_id': product.service_type_id,
                'service_type': product.service_type,
                'service_subtype': product.service_subtype,
                'status': product.status,
                'is_active': product.is_active,
                # 供应商特定信息
                'vendor_product_id': vendor_product.id if vendor_product else None,
                'is_primary': vendor_product.is_primary if vendor_product else False,
                'is_available': vendor_product.is_available if vendor_product else False,
                'cost_price_cny': float(vendor_product.cost_price_cny) if vendor_product and vendor_product.cost_price_cny else None,
                'cost_price_idr': float(vendor_product.cost_price_idr) if vendor_product and vendor_product.cost_price_idr else None,
                'processing_days': vendor_product.processing_days if vendor_product else None,
                # 价格历史信息
                'price_history': await self._get_vendor_product_price_history(vendor_product.id) if vendor_product else [],
                # 销售价格（从 product_prices 表）
                'sales_prices': sales_prices,
            }
            
            service_list.append(service_data)
        
        return service_list, total
    
    async def _get_vendor_product_price_history(
        self,
        vendor_product_id: str,
    ) -> List[Dict[str, Any]]:
        """
        获取供应商产品价格历史
        
        Args:
            vendor_product_id: 供应商产品关联ID
        
        Returns:
            价格历史列表（按生效时间排序）
        """
        query = select(VendorProductPriceHistory).where(
            VendorProductPriceHistory.vendor_product_id == vendor_product_id,
        ).order_by(VendorProductPriceHistory.effective_from.desc())
        
        result = await self.db.execute(query)
        history_items = result.scalars().all()
        
        history_list = []
        for item in history_items:
            history_list.append({
                'id': item.id,
                'old_price_cny': float(item.old_price_cny) if item.old_price_cny else None,
                'old_price_idr': float(item.old_price_idr) if item.old_price_idr else None,
                'new_price_cny': float(item.new_price_cny) if item.new_price_cny else None,
                'new_price_idr': float(item.new_price_idr) if item.new_price_idr else None,
                'effective_from': item.effective_from,
                'effective_to': item.effective_to,
                'change_reason': item.change_reason,
                'changed_by': item.changed_by,
                'created_at': item.created_at,
            })
        
        return history_list
    
    async def _get_product_sales_prices(
        self,
        product_id: str,
        organization_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        获取产品的销售价格（从 product_prices 表）
        列格式：一条记录包含所有价格类型和货币
        
        Args:
            product_id: 产品ID
            organization_id: 组织ID（可选，用于查询组织特定价格）
        
        Returns:
            价格列表，每个价格类型和货币组合一个字典
        """
        # 查询当前有效的价格（列格式：一条记录包含所有价格）
        now = datetime.now()
        query = select(ProductPrice).where(
            and_(
                ProductPrice.product_id == product_id,
                ProductPrice.effective_from <= now,
                or_(
                    ProductPrice.effective_to.is_(None),
                    ProductPrice.effective_to >= now,
                ),
            )
        )
        
        # 如果指定了组织ID，优先查询组织特定价格
        if organization_id:
            query = query.where(
                or_(
                    ProductPrice.organization_id == organization_id,
                    ProductPrice.organization_id.is_(None),  # 通用价格
                )
            )
        else:
            # 如果没有指定组织ID，只查询通用价格
            query = query.where(ProductPrice.organization_id.is_(None))
        
        query = query.order_by(
            ProductPrice.organization_id.desc(),  # 组织特定价格优先
            ProductPrice.effective_from.desc(),
        )
        
        result = await self.db.execute(query)
        prices = result.scalars().all()
        
        # 转换为字典列表（列格式：一条记录转换为多个价格字典）
        price_list = []
        for price in prices:
            exchange_rate = float(price.exchange_rate) if price.exchange_rate else None
            is_org_specific = price.organization_id is not None
            
            # 渠道价
            if price.price_channel_idr is not None:
                price_list.append({
                    'price_type': 'channel',
                    'currency': 'IDR',
                    'amount': float(price.price_channel_idr),
                    'exchange_rate': exchange_rate,
                    'effective_from': price.effective_from,
                    'effective_to': price.effective_to,
                    'is_organization_specific': is_org_specific,
                })
            if price.price_channel_cny is not None:
                price_list.append({
                    'price_type': 'channel',
                    'currency': 'CNY',
                    'amount': float(price.price_channel_cny),
                    'exchange_rate': exchange_rate,
                    'effective_from': price.effective_from,
                    'effective_to': price.effective_to,
                    'is_organization_specific': is_org_specific,
                })
            
            # 直客价
            if price.price_direct_idr is not None:
                price_list.append({
                    'price_type': 'direct',
                    'currency': 'IDR',
                    'amount': float(price.price_direct_idr),
                    'exchange_rate': exchange_rate,
                    'effective_from': price.effective_from,
                    'effective_to': price.effective_to,
                    'is_organization_specific': is_org_specific,
                })
            if price.price_direct_cny is not None:
                price_list.append({
                    'price_type': 'direct',
                    'currency': 'CNY',
                    'amount': float(price.price_direct_cny),
                    'exchange_rate': exchange_rate,
                    'effective_from': price.effective_from,
                    'effective_to': price.effective_to,
                    'is_organization_specific': is_org_specific,
                })
            
            # 列表价
            if price.price_list_idr is not None:
                price_list.append({
                    'price_type': 'list',
                    'currency': 'IDR',
                    'amount': float(price.price_list_idr),
                    'exchange_rate': exchange_rate,
                    'effective_from': price.effective_from,
                    'effective_to': price.effective_to,
                    'is_organization_specific': is_org_specific,
                })
            if price.price_list_cny is not None:
                price_list.append({
                    'price_type': 'list',
                    'currency': 'CNY',
                    'amount': float(price.price_list_cny),
                    'exchange_rate': exchange_rate,
                    'effective_from': price.effective_from,
                    'effective_to': price.effective_to,
                    'is_organization_specific': is_org_specific,
                })
        
        return price_list
    
    async def get_supplier_service_prices(
        self,
        supplier_id: str,
        product_id: str,
    ) -> List[Dict[str, Any]]:
        """
        获取特定服务的价格历史
        
        Args:
            supplier_id: 供应商ID
            product_id: 产品ID
        
        Returns:
            价格历史列表
        """
        # 验证供应商和产品
        await self.get_supplier_detail(supplier_id)
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise BusinessException(detail="产品不存在", status_code=404)
        
        # 获取供应商产品关联信息
        vendor_product = await self.vendor_product_repo.get_vendor_product_info(
            vendor_id=supplier_id,
            product_id=product_id,
        )
        
        if not vendor_product:
            return []
        
        # 查询供应商产品价格历史
        query = select(VendorProductPriceHistory).where(
            VendorProductPriceHistory.vendor_product_id == vendor_product.id,
        )
        
        query = query.order_by(VendorProductPriceHistory.effective_from.desc())
        
        result = await self.db.execute(query)
        history_items = result.scalars().all()
        
        # 转换为字典列表
        history_list = []
        for item in history_items:
            history_list.append({
                'id': item.id,
                'old_price_cny': float(item.old_price_cny) if item.old_price_cny else None,
                'old_price_idr': float(item.old_price_idr) if item.old_price_idr else None,
                'new_price_cny': float(item.new_price_cny) if item.new_price_cny else None,
                'new_price_idr': float(item.new_price_idr) if item.new_price_idr else None,
                'change_reason': item.change_reason,
                'effective_from': item.effective_from,
                'effective_to': item.effective_to,
                'changed_by': item.changed_by,
                'created_at': item.created_at,
            })
        
        return history_list
    
    async def batch_add_products(
        self,
        supplier_id: str,
        product_ids: List[str],
        default_cost_price_cny: Optional[float] = None,
        default_cost_price_idr: Optional[float] = None,
        is_available: bool = True,
        is_primary: bool = False,
        current_user_id: Optional[str] = None,
        current_user_roles: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        批量添加供应商产品
        
        Args:
            supplier_id: 供应商ID
            product_ids: 产品ID列表
            default_cost_price_cny: 默认成本价（人民币）
            default_cost_price_idr: 默认成本价（印尼盾）
            is_available: 是否可用
            is_primary: 是否主要供应商
            current_user_id: 当前用户ID（用于权限检查）
            current_user_roles: 当前用户角色列表（用于权限检查）
        
        Returns:
            包含成功和失败信息的字典
        
        Raises:
            BusinessException: 如果用户没有权限
        """
        # 权限检查：只有系统管理员可以修改供应商价格
        if current_user_roles and "ADMIN" not in current_user_roles:
            raise BusinessException(detail="只有系统管理员可以修改供应商价格", status_code=403)
        
        # 验证供应商存在
        await self.get_supplier_detail(supplier_id)
        
        # 验证产品是否存在
        invalid_product_ids = []
        for product_id in product_ids:
            product = await self.product_repo.get_by_id(product_id)
            if not product:
                invalid_product_ids.append(product_id)
        
        # 过滤掉无效的产品ID
        valid_product_ids = [pid for pid in product_ids if pid not in invalid_product_ids]
        
        if not valid_product_ids:
            return {
                'success_count': 0,
                'failed_count': len(product_ids),
                'success_product_ids': [],
                'failed_product_ids': invalid_product_ids,
            }
        
        # 转换价格为Decimal
        cost_price_cny_decimal = Decimal(str(default_cost_price_cny)) if default_cost_price_cny is not None else None
        cost_price_idr_decimal = Decimal(str(default_cost_price_idr)) if default_cost_price_idr is not None else None
        
        # 批量创建
        created_items, existing_product_ids = await self.vendor_product_repo.batch_create(
            vendor_id=supplier_id,
            product_ids=valid_product_ids,
            default_cost_price_cny=cost_price_cny_decimal,
            default_cost_price_idr=cost_price_idr_decimal,
            is_available=is_available,
            is_primary=is_primary,
        )
        
        # 提交事务
        await self.db.commit()
        
        # 返回结果
        success_product_ids = [item.product_id for item in created_items]
        failed_product_ids = invalid_product_ids + existing_product_ids
        
        return {
            'success_count': len(created_items),
            'failed_count': len(failed_product_ids),
            'success_product_ids': success_product_ids,
            'failed_product_ids': failed_product_ids,
        }
    
    async def update_vendor_product_price(
        self,
        supplier_id: str,
        product_id: str,
        cost_price_cny: Optional[float] = None,
        cost_price_idr: Optional[float] = None,
        effective_from: Optional[datetime] = None,
        current_user_id: Optional[str] = None,
        current_user_roles: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        更新供应商产品价格（支持双价格和生效时间）
        
        Args:
            supplier_id: 供应商ID
            product_id: 产品ID
            cost_price_cny: 成本价（人民币）
            cost_price_idr: 成本价（印尼盾）
            effective_from: 价格生效时间（如果为None则默认为当天+1天）
            current_user_id: 当前用户ID（用于权限检查和价格历史记录）
            current_user_roles: 当前用户角色列表（用于权限检查）
        
        Returns:
            更新结果
        
        Raises:
            BusinessException: 如果用户没有权限或产品不存在
        """
        # 权限检查：只有系统管理员可以修改供应商价格
        if current_user_roles and "ADMIN" not in current_user_roles:
            raise BusinessException(detail="只有系统管理员可以修改供应商价格", status_code=403)
        
        # 验证供应商存在
        await self.get_supplier_detail(supplier_id)
        
        # 获取现有的供应商产品信息
        vendor_product = await self.vendor_product_repo.get_vendor_product_info(
            vendor_id=supplier_id,
            product_id=product_id,
        )
        
        if not vendor_product:
            raise BusinessException(detail="供应商产品关联不存在", status_code=404)
        
        # 时区处理：前端使用 UTC+7（印尼时区），后端统一转换为 UTC 存储
        # 印尼时区 UTC+7
        jakarta_tz = timezone(timedelta(hours=7))
        utc_tz = timezone.utc
        
        # 统一时区处理：将前端传来的 datetime 转换为 UTC 存储
        if effective_from is not None:
            if effective_from.tzinfo is None:
                # 如果前端传来的是 naive datetime（来自 datetime-local），假设是 UTC+7 时区
                effective_from = effective_from.replace(tzinfo=jakarta_tz)
            # 转换为 UTC 时区
            effective_from = effective_from.astimezone(utc_tz)
            # 转换为 naive datetime（数据库存储格式）
            effective_from = effective_from.replace(tzinfo=None)
        
        # 如果没有指定生效时间，默认为当天+1天（使用印尼时区）
        if effective_from is None:
            # 获取印尼时区的当前时间
            jakarta_now = datetime.now(jakarta_tz)
            # 加1天
            effective_from = (jakarta_now + timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=0)
            # 转换为 UTC 并移除时区信息
            effective_from = effective_from.astimezone(utc_tz).replace(tzinfo=None)
        
        # 检查是否有价格历史记录
        price_history_count_query = select(func.count(VendorProductPriceHistory.id)).where(
            VendorProductPriceHistory.vendor_product_id == vendor_product.id
        )
        price_history_count_result = await self.db.execute(price_history_count_query)
        price_history_count = price_history_count_result.scalar() or 0
        
        # 检查是否有未生效的价格历史记录
        # 数据库存储的是 UTC 时区的 naive datetime，所以使用 UTC 的 now
        now_utc = datetime.now(utc_tz).replace(tzinfo=None)
        now = now_utc
        future_price_query = select(VendorProductPriceHistory).where(
            and_(
                VendorProductPriceHistory.vendor_product_id == vendor_product.id,
                VendorProductPriceHistory.effective_from > now,
                VendorProductPriceHistory.effective_to.is_(None),
            )
        ).order_by(VendorProductPriceHistory.effective_from.asc()).limit(1)
        
        future_price_result = await self.db.execute(future_price_query)
        future_price = future_price_result.scalar_one_or_none()
        
        # 如果存在未生效的价格，只能修改价格，不能修改生效时间
        if future_price:
            # 只能修改价格，不能修改生效时间
            effective_from = future_price.effective_from
        
        # 转换价格为Decimal
        new_price_cny = Decimal(str(cost_price_cny)) if cost_price_cny is not None else None
        new_price_idr = Decimal(str(cost_price_idr)) if cost_price_idr is not None else None
        
        # 检查价格是否有变化
        old_price_cny = vendor_product.cost_price_cny
        old_price_idr = vendor_product.cost_price_idr
        
        price_changed = (
            (old_price_cny != new_price_cny) or
            (old_price_idr != new_price_idr)
        )
        
        if not price_changed:
            return {'success': True, 'message': '价格未变化'}
        
        # 如果只有一条价格记录（没有价格历史），直接更新价格，不创建历史记录
        if price_history_count == 0:
            # 直接更新供应商产品价格
            vendor_product.cost_price_cny = new_price_cny
            vendor_product.cost_price_idr = new_price_idr
            await self.db.flush()
            await self.db.commit()
            return {'success': True, 'message': '价格更新成功'}
        
        # 如果有价格历史记录，按照正常流程处理
        # 更新旧价格的失效时间
        if future_price:
            # 如果存在未生效的价格，更新其失效时间
            future_price.effective_to = effective_from
        else:
            # 查找当前有效的价格历史记录，设置失效时间
            current_price_query = select(VendorProductPriceHistory).where(
                and_(
                    VendorProductPriceHistory.vendor_product_id == vendor_product.id,
                    VendorProductPriceHistory.effective_from <= now,
                    VendorProductPriceHistory.effective_to.is_(None),
                )
            ).order_by(VendorProductPriceHistory.effective_from.desc()).limit(1)
            
            current_price_result = await self.db.execute(current_price_query)
            current_price = current_price_result.scalar_one_or_none()
            
            if current_price:
                current_price.effective_to = effective_from
        
        # 创建新的价格历史记录
        price_history = VendorProductPriceHistory(
            vendor_product_id=vendor_product.id,
            old_price_cny=old_price_cny,
            old_price_idr=old_price_idr,
            new_price_cny=new_price_cny,
            new_price_idr=new_price_idr,
            effective_from=effective_from,
            changed_by=current_user_id,
        )
        self.db.add(price_history)
        
        # 如果新价格立即生效（effective_from <= now），立即更新供应商产品价格
        if effective_from <= now:
            vendor_product.cost_price_cny = new_price_cny
            vendor_product.cost_price_idr = new_price_idr
        
        await self.db.flush()
        await self.db.commit()
        
        return {'success': True, 'message': '价格更新成功'}
    
    async def batch_update_prices(
        self,
        supplier_id: str,
        updates: List[Dict[str, Any]],
        current_user_id: Optional[str] = None,
        current_user_roles: Optional[List[str]] = None,
        effective_from: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        批量更新供应商产品价格（兼容旧接口，内部调用update_vendor_product_price）
        
        Args:
            supplier_id: 供应商ID
            updates: 更新列表，每个元素包含 product_id 和要更新的字段
            current_user_id: 当前用户ID（用于权限检查和价格历史记录）
            current_user_roles: 当前用户角色列表（用于权限检查）
            effective_from: 价格生效时间（如果为None则使用默认值）
        
        Returns:
            包含成功和失败信息的字典
        
        Raises:
            BusinessException: 如果用户没有权限
        """
        # 权限检查：只有系统管理员可以修改供应商价格
        if current_user_roles and "ADMIN" not in current_user_roles:
            raise BusinessException(detail="只有系统管理员可以修改供应商价格", status_code=403)
        
        # 验证供应商存在
        await self.get_supplier_detail(supplier_id)
        
        success_count = 0
        failed_product_ids = []
        
        for update_data in updates:
            product_id = update_data.get('product_id')
            if not product_id:
                failed_product_ids.append('unknown')
                continue
            
            try:
                # 调用单个价格更新方法
                await self.update_vendor_product_price(
                    supplier_id=supplier_id,
                    product_id=product_id,
                    cost_price_cny=update_data.get('cost_price_cny'),
                    cost_price_idr=update_data.get('cost_price_idr'),
                    effective_from=effective_from,
                    current_user_id=current_user_id,
                    current_user_roles=current_user_roles,
                )
                success_count += 1
            except Exception as e:
                failed_product_ids.append(product_id)
        
        return {
            'success_count': success_count,
            'failed_count': len(failed_product_ids),
            'failed_product_ids': failed_product_ids,
        }
    
    async def get_existing_product_ids(
        self,
        supplier_id: str,
    ) -> List[str]:
        """
        获取供应商已添加的产品ID列表
        
        Args:
            supplier_id: 供应商ID
        
        Returns:
            产品ID列表
        """
        # 验证供应商存在
        await self.get_supplier_detail(supplier_id)
        
        # 获取已存在的产品ID
        product_ids = await self.vendor_product_repo.get_existing_product_ids(supplier_id)
        
        return product_ids
