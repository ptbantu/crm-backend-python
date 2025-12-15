"""
供应商产品关联数据访问层
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, join, distinct, and_
from decimal import Decimal
from common.models.vendor_product import VendorProduct
from common.models.product import Product
from common.utils.repository import BaseRepository


class VendorProductRepository(BaseRepository[VendorProduct]):
    """供应商产品关联仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, VendorProduct)
    
    async def get_products_by_vendor(
        self,
        vendor_id: str,
        page: int = 1,
        size: int = 10,
        is_available: Optional[bool] = None,
        is_primary: Optional[bool] = None,
    ) -> tuple[List[Product], int]:
        """
        查询某个供应商提供的所有产品
        
        Args:
            vendor_id: 供应商组织ID
            page: 页码
            size: 每页数量
            is_available: 是否可用（可选）
            is_primary: 是否主要供应商（可选）
        
        Returns:
            (产品列表, 总数)
        """
        # 构建查询：通过 vendor_products 表关联查询 products
        # 注意：不需要使用 distinct()，因为 vendor_products 表有唯一约束 uk_organization_product
        # 确保同一供应商不会重复添加同一产品
        query = select(Product).join(
            VendorProduct, Product.id == VendorProduct.product_id
        ).where(
            VendorProduct.organization_id == vendor_id
        )
        
        # 添加过滤条件
        conditions = []
        if is_available is not None:
            conditions.append(VendorProduct.is_available == is_available)
        if is_primary is not None:
            conditions.append(VendorProduct.is_primary == is_primary)
        
        if conditions:
            query = query.where(or_(*conditions))
        
        # 排序：按优先级和创建时间
        query = query.order_by(
            VendorProduct.is_primary.desc(),  # 主要供应商优先
            VendorProduct.priority.asc(),  # 优先级数字越小越优先
            Product.created_at.desc()
        )
        
        # 计算总数（使用 distinct 避免重复计数）
        count_query = select(func.count(distinct(Product.id))).select_from(
            join(Product, VendorProduct, Product.id == VendorProduct.product_id)
        ).where(
            VendorProduct.organization_id == vendor_id
        )
        if conditions:
            count_query = count_query.where(or_(*conditions))
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页
        query = query.offset((page - 1) * size).limit(size)
        
        # 执行查询
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return list(items), total
    
    async def get_vendor_product_info(
        self,
        vendor_id: str,
        product_id: str,
    ) -> Optional[VendorProduct]:
        """
        获取供应商产品关联信息
        
        Args:
            vendor_id: 供应商组织ID
            product_id: 产品ID
        
        Returns:
            供应商产品关联信息，如果不存在则返回 None
        """
        query = select(VendorProduct).where(
            VendorProduct.organization_id == vendor_id,
            VendorProduct.product_id == product_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def batch_create(
        self,
        vendor_id: str,
        product_ids: List[str],
        default_cost_price_cny: Optional[Decimal] = None,
        default_cost_price_idr: Optional[Decimal] = None,
        is_available: bool = True,
        is_primary: bool = False,
    ) -> tuple[List[VendorProduct], List[str]]:
        """
        批量创建供应商产品关联
        
        Args:
            vendor_id: 供应商组织ID
            product_ids: 产品ID列表
            default_cost_price_cny: 默认成本价（人民币）
            default_cost_price_idr: 默认成本价（印尼盾）
            is_available: 是否可用
            is_primary: 是否主要供应商
        
        Returns:
            (成功创建的对象列表, 失败的产品ID列表)
        """
        # 查询已存在的关联，避免重复
        existing_query = select(VendorProduct.product_id).where(
            and_(
                VendorProduct.organization_id == vendor_id,
                VendorProduct.product_id.in_(product_ids)
            )
        )
        existing_result = await self.db.execute(existing_query)
        existing_product_ids = set(existing_result.scalars().all())
        
        # 过滤出需要创建的产品ID
        new_product_ids = [pid for pid in product_ids if pid not in existing_product_ids]
        
        if not new_product_ids:
            return [], list(existing_product_ids)
        
        # 批量创建
        created_items = []
        for product_id in new_product_ids:
            vendor_product = VendorProduct(
                organization_id=vendor_id,
                product_id=product_id,
                cost_price_cny=default_cost_price_cny,
                cost_price_idr=default_cost_price_idr,
                is_available=is_available,
                is_primary=is_primary,
            )
            created_items.append(vendor_product)
        
        # 批量保存
        self.db.add_all(created_items)
        await self.db.flush()
        
        return created_items, list(existing_product_ids)
    
    async def batch_update(
        self,
        vendor_id: str,
        updates: List[Dict[str, Any]],
    ) -> tuple[int, List[str]]:
        """
        批量更新供应商产品价格和属性
        
        Args:
            vendor_id: 供应商组织ID
            updates: 更新列表，每个元素包含 product_id 和要更新的字段
        
        Returns:
            (成功更新的数量, 失败的产品ID列表)
        """
        failed_product_ids = []
        updated_count = 0
        
        for update_data in updates:
            product_id = update_data.get('product_id')
            if not product_id:
                failed_product_ids.append('unknown')
                continue
            
            # 查询现有的关联
            vendor_product = await self.get_vendor_product_info(vendor_id, product_id)
            if not vendor_product:
                failed_product_ids.append(product_id)
                continue
            
            # 更新字段（只更新提供的字段）
            if 'cost_price_cny' in update_data:
                vendor_product.cost_price_cny = update_data['cost_price_cny']
            if 'cost_price_idr' in update_data:
                vendor_product.cost_price_idr = update_data['cost_price_idr']
            if 'processing_days' in update_data:
                vendor_product.processing_days = update_data['processing_days']
            if 'is_available' in update_data:
                vendor_product.is_available = update_data['is_available']
            if 'is_primary' in update_data:
                vendor_product.is_primary = update_data['is_primary']
            if 'priority' in update_data:
                vendor_product.priority = update_data['priority']
            
            updated_count += 1
        
        await self.db.flush()
        
        return updated_count, failed_product_ids
    
    async def get_existing_product_ids(
        self,
        vendor_id: str,
    ) -> List[str]:
        """
        获取供应商已添加的产品ID列表
        
        Args:
            vendor_id: 供应商组织ID
        
        Returns:
            产品ID列表
        """
        query = select(VendorProduct.product_id).where(
            VendorProduct.organization_id == vendor_id
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_service_counts_by_vendors(
        self,
        vendor_ids: List[str],
    ) -> Dict[str, int]:
        """
        批量获取多个供应商的服务数量
        
        Args:
            vendor_ids: 供应商组织ID列表
        
        Returns:
            字典，key为供应商ID，value为服务数量
        """
        if not vendor_ids:
            return {}
        
        # 使用 group_by 和 count 统计每个供应商的服务数量
        query = select(
            VendorProduct.organization_id,
            func.count(distinct(VendorProduct.product_id)).label('service_count')
        ).where(
            VendorProduct.organization_id.in_(vendor_ids)
        ).group_by(VendorProduct.organization_id)
        
        result = await self.db.execute(query)
        rows = result.all()
        
        # 构建字典，默认值为0
        service_counts = {vendor_id: 0 for vendor_id in vendor_ids}
        for row in rows:
            service_counts[row.organization_id] = row.service_count or 0
        
        return service_counts

