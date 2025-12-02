"""
供应商产品关联数据访问层
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, join, distinct
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
        query = select(Product).join(
            VendorProduct, Product.id == VendorProduct.product_id
        ).where(
            VendorProduct.organization_id == vendor_id
        ).distinct()
        
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
            Product.join(VendorProduct, Product.id == VendorProduct.product_id)
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

