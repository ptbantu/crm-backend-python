"""
销售价格查询服务
从 product_prices 表查询销售价格（渠道价、直客价、列表价）
注意：products 表中的销售价格字段已删除，所有价格都从 product_prices 表查询
"""
from typing import Optional, Dict, List
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from common.models.product import Product
from common.models.product_price import ProductPrice
from common.models.product_price_list import ProductPriceList
from common.exceptions import BusinessException, NotFoundError
from common.utils.logger import get_logger

logger = get_logger(__name__)


class SalesPriceService:
    """销售价格查询服务 - 实现价格独立设计后的查询逻辑"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_product_price(
        self,
        product_id: str,
        price_type: str,  # channel, direct, list
        currency: str,  # IDR, CNY
        organization_id: Optional[str] = None,
        effective_date: Optional[datetime] = None
    ) -> Optional[Decimal]:
        """
        查询产品价格（优先从 product_prices 表查询，兼容 products 表）
        
        Args:
            product_id: 产品ID
            price_type: 价格类型（channel, direct, list）
            currency: 货币类型（IDR, CNY）
            organization_id: 组织ID（可选，用于查询特定组织价格）
            effective_date: 生效日期（可选，默认当前时间）
            
        Returns:
            价格金额，如果不存在返回 None
        """
        if effective_date is None:
            effective_date = datetime.now()
        
        # 1. 优先从 product_prices 表查询（一条记录包含所有价格）
        query = select(ProductPrice).where(
            and_(
                ProductPrice.product_id == product_id,
                ProductPrice.effective_from <= effective_date,
                or_(
                    ProductPrice.effective_to.is_(None),
                    ProductPrice.effective_to >= effective_date
                )
            )
        )
        
        # 优先使用特定组织价格
        if organization_id:
            query = query.where(
                or_(
                    ProductPrice.organization_id == organization_id,
                    ProductPrice.organization_id.is_(None)
                )
            ).order_by(
                # 特定组织价格优先
                func.nullif(ProductPrice.organization_id, organization_id).desc(),
                ProductPrice.effective_from.desc()
            )
        else:
            # 只查询通用价格
            query = query.where(
                ProductPrice.organization_id.is_(None)
            ).order_by(ProductPrice.effective_from.desc())
        
        query = query.limit(1)
        
        result = await self.db.execute(query)
        price_record = result.scalar_one_or_none()
        
        if price_record:
            # 根据价格类型和货币获取对应的字段
            price_field_map = {
                ('channel', 'IDR'): 'price_channel_idr',
                ('channel', 'CNY'): 'price_channel_cny',
                ('direct', 'IDR'): 'price_direct_idr',
                ('direct', 'CNY'): 'price_direct_cny',
                ('list', 'IDR'): 'price_list_idr',
                ('list', 'CNY'): 'price_list_cny',
            }
            
            price_field = price_field_map.get((price_type, currency))
            if price_field:
                price_value = getattr(price_record, price_field, None)
                if price_value is not None:
                    logger.debug(
                        f"从 product_prices 表查询到价格 | "
                        f"product_id={product_id}, price_type={price_type}, currency={currency}, "
                        f"amount={price_value}"
                    )
                    return price_value
        
        # 2. 如果 product_prices 表中没有，从 products 表查询（兼容旧数据）
        product_result = await self.db.execute(
            select(Product).where(Product.id == product_id)
        )
        product = product_result.scalar_one_or_none()
        
        if not product:
            return None
        
        # 根据价格类型和货币获取对应的字段
        price_field_map = {
            ('channel', 'IDR'): 'price_channel_idr',
            ('channel', 'CNY'): 'price_channel_cny',
            ('direct', 'IDR'): 'price_direct_idr',
            ('direct', 'CNY'): 'price_direct_cny',
            ('list', 'IDR'): 'price_list_idr',
            ('list', 'CNY'): 'price_list_cny',
        }
        
        price_field = price_field_map.get((price_type, currency))
        if price_field:
            price_value = getattr(product, price_field, None)
            if price_value is not None:
                logger.debug(
                    f"从 products 表查询到价格（兼容旧数据） | "
                    f"product_id={product_id}, price_type={price_type}, currency={currency}, "
                    f"amount={price_value}"
                )
                return price_value
        
        return None
    
    async def get_all_product_prices(
        self,
        product_id: str,
        organization_id: Optional[str] = None,
        effective_date: Optional[datetime] = None
    ) -> Dict[str, Dict[str, Optional[Decimal]]]:
        """
        查询产品的所有销售价格（渠道价、直客价、列表价）
        
        Args:
            product_id: 产品ID
            organization_id: 组织ID（可选）
            effective_date: 生效日期（可选）
            
        Returns:
            {
                "channel": {"IDR": Decimal, "CNY": Decimal},
                "direct": {"IDR": Decimal, "CNY": Decimal},
                "list": {"IDR": Decimal, "CNY": Decimal}
            }
        """
        if effective_date is None:
            effective_date = datetime.now()
        
        # 从 product_prices 表查询（一条记录包含所有价格）
        query = select(ProductPrice).where(
            and_(
                ProductPrice.product_id == product_id,
                ProductPrice.effective_from <= effective_date,
                or_(
                    ProductPrice.effective_to.is_(None),
                    ProductPrice.effective_to >= effective_date
                )
            )
        )
        
        if organization_id:
            query = query.where(
                or_(
                    ProductPrice.organization_id == organization_id,
                    ProductPrice.organization_id.is_(None)
                )
            ).order_by(
                func.nullif(ProductPrice.organization_id, organization_id).desc(),
                ProductPrice.effective_from.desc()
            )
        else:
            query = query.where(
                ProductPrice.organization_id.is_(None)
            ).order_by(ProductPrice.effective_from.desc())
        
        query = query.limit(1)
        
        result = await self.db.execute(query)
        price_record = result.scalar_one_or_none()
        
        if price_record:
            return {
                "channel": {
                    "IDR": price_record.price_channel_idr,
                    "CNY": price_record.price_channel_cny
                },
                "direct": {
                    "IDR": price_record.price_direct_idr,
                    "CNY": price_record.price_direct_cny
                },
                "list": {
                    "IDR": price_record.price_list_idr,
                    "CNY": price_record.price_list_cny
                }
            }
        
        # 注意：products 表中的销售价格字段已删除，所有价格都从 product_prices 表查询
        # 如果 product_prices 表中没有，返回空价格
        
        return {
            "channel": {"IDR": None, "CNY": None},
            "direct": {"IDR": None, "CNY": None},
            "list": {"IDR": None, "CNY": None}
        }
    
    async def get_customer_level_price(
        self,
        product_id: str,
        customer_level_code: str,  # '2', '3', '4', '5', '6'
        currency: str,  # IDR, CNY
        effective_date: Optional[datetime] = None
    ) -> Optional[Decimal]:
        """
        查询客户等级价格（从 product_price_list 表查询）
        
        Args:
            product_id: 产品ID
            customer_level_code: 客户等级代码（'2', '3', '4', '5', '6'）
            currency: 货币类型（IDR, CNY）
            effective_date: 生效日期（可选）
            
        Returns:
            价格金额，如果不存在返回 None
        """
        if effective_date is None:
            effective_date = datetime.now()
        
        # 查询 product_price_list 表
        query = select(ProductPriceList).where(
            and_(
                ProductPriceList.product_id == product_id,
                ProductPriceList.is_active == True,
                ProductPriceList.effective_from <= effective_date,
                or_(
                    ProductPriceList.effective_to.is_(None),
                    ProductPriceList.effective_to >= effective_date
                )
            )
        ).order_by(ProductPriceList.effective_from.desc()).limit(1)
        
        result = await self.db.execute(query)
        price_list = result.scalar_one_or_none()
        
        if not price_list:
            return None
        
        # 根据客户等级和货币获取对应的字段
        level_field_map = {
            ('2', 'CNY'): 'price_level2_cny',
            ('2', 'IDR'): 'price_level2_idr',
            ('3', 'CNY'): 'price_level3_cny',
            ('3', 'IDR'): 'price_level3_idr',
            ('4', 'CNY'): 'price_level4_cny',
            ('4', 'IDR'): 'price_level4_idr',
            ('5', 'CNY'): 'price_level5_cny',
            ('5', 'IDR'): 'price_level5_idr',
            ('6', 'CNY'): 'price_level6_cny',
            ('6', 'IDR'): 'price_level6_idr',
        }
        
        field_name = level_field_map.get((customer_level_code, currency))
        if field_name:
            price_value = getattr(price_list, field_name, None)
            return price_value
        
        return None
