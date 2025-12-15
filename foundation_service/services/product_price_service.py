"""
产品价格服务 - 销售价格和成本价格管理
"""
from typing import Optional, Dict, List
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from common.models.product import Product
from common.models.customer import Customer
from common.models.organization import Organization
from common.exceptions import BusinessException, NotFoundError
from common.utils.logger import get_logger

logger = get_logger(__name__)


class ProductPriceService:
    """产品价格服务 - 处理销售价格和成本价格查询"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_sales_price(
        self,
        product_id: str,
        customer_id: str,
        currency: Optional[str] = None
    ) -> Dict:
        """
        查询销售价格（对外售价）
        
        根据客户等级查询产品的销售价格
        
        Args:
            product_id: 产品ID
            customer_id: 客户ID（用于获取客户等级）
            currency: 币种（CNY/IDR），可选，默认返回两种币种
            
        Returns:
            {
                "product_id": str,
                "customer_level": str,
                "price_cny": Decimal,
                "price_idr": Decimal,
                "effective_from": datetime,
                "effective_to": Optional[datetime]
            }
        """
        # 1. 查询客户等级
        customer_result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        customer = customer_result.scalar_one_or_none()
        
        if not customer:
            raise NotFoundError(f"客户 {customer_id} 不存在")
        
        if not customer.level_code:
            raise BusinessException(detail="客户未设置等级，无法查询销售价格")
        
        level_code = customer.level_code  # 例如: '2', '3', '4', '5', '6'
        
        # 2. 查询产品的有效销售价格
        # 注意：这里需要动态查询 product_price_list 表
        # 由于表可能还未创建模型，我们使用原生SQL或先创建模型
        # 暂时使用原生SQL查询
        from sqlalchemy import text
        
        now = datetime.now()
        sql = text("""
            SELECT 
                id,
                product_id,
                price_level2_cny, price_level2_idr,
                price_level3_cny, price_level3_idr,
                price_level4_cny, price_level4_idr,
                price_level5_cny, price_level5_idr,
                price_level6_cny, price_level6_idr,
                is_active,
                effective_from,
                effective_to
            FROM product_price_list
            WHERE product_id = :product_id
              AND is_active = 1
              AND effective_from <= :now
              AND (effective_to IS NULL OR effective_to > :now)
            LIMIT 1
        """)
        
        result = await self.db.execute(
            sql,
            {"product_id": product_id, "now": now}
        )
        price_record = result.fetchone()
        
        if not price_record:
            raise NotFoundError(f"产品 {product_id} 未设置销售价格")
        
        # 3. 根据客户等级和币种返回价格
        level_field_cny = f"price_level{level_code}_cny"
        level_field_idr = f"price_level{level_code}_idr"
        
        price_cny = getattr(price_record, level_field_cny) or Decimal('0')
        price_idr = getattr(price_record, level_field_idr) or Decimal('0')
        
        response = {
            "product_id": product_id,
            "customer_level": level_code,
            "price_cny": price_cny,
            "price_idr": price_idr,
            "effective_from": price_record.effective_from,
            "effective_to": price_record.effective_to
        }
        
        # 如果指定了币种，只返回对应币种
        if currency == "CNY":
            response["price_idr"] = None
        elif currency == "IDR":
            response["price_cny"] = None
        
        return response
    
    async def get_cost_price(
        self,
        product_id: str,
        supplier_id: str,
        delivery_type: Optional[str] = None
    ) -> Dict:
        """
        查询成本价格（服务提供方的成本）
        
        Args:
            product_id: 产品ID
            supplier_id: 服务提供方ID（内部团队或外部供应商）
            delivery_type: 交付类型（INTERNAL/VENDOR），可选，如果不提供则自动判断
            
        Returns:
            {
                "id": str,
                "product_id": str,
                "supplier_id": str,
                "delivery_type": str,
                "version": int,
                "cost_cny": Decimal,
                "cost_idr": Decimal,
                "effective_start_at": datetime,
                "effective_end_at": Optional[datetime]
            }
        """
        # 1. 自动判断交付类型
        if not delivery_type:
            org_result = await self.db.execute(
                select(Organization).where(
                    Organization.id == supplier_id,
                    Organization.is_active == True  # 只查询启用的供应商
                )
            )
            supplier = org_result.scalar_one_or_none()
            
            if not supplier:
                raise NotFoundError(f"服务提供方 {supplier_id} 不存在或已禁用")
            
            if supplier.organization_type == 'internal':
                delivery_type = 'INTERNAL'
            elif supplier.organization_type == 'vendor':
                delivery_type = 'VENDOR'
            else:
                raise BusinessException(
                    detail=f"组织类型 {supplier.organization_type} 不能作为服务提供方"
                )
        
        # 2. 查询当前有效的成本价格
        from sqlalchemy import text
        
        now = datetime.now()
        sql = text("""
            SELECT 
                id,
                product_id,
                supplier_id,
                delivery_type,
                version,
                cost_cny,
                cost_idr,
                effective_start_at,
                effective_end_at,
                is_current
            FROM supplier_cost_history
            WHERE product_id = :product_id
              AND supplier_id = :supplier_id
              AND delivery_type = :delivery_type
              AND is_current = 1
              AND effective_start_at <= :now
              AND (effective_end_at IS NULL OR effective_end_at > :now)
            ORDER BY version DESC
            LIMIT 1
        """)
        
        result = await self.db.execute(
            sql,
            {
                "product_id": product_id,
                "supplier_id": supplier_id,
                "delivery_type": delivery_type,
                "now": now
            }
        )
        cost_record = result.fetchone()
        
        if not cost_record:
            raise NotFoundError(
                f"产品 {product_id} 的服务提供方 {supplier_id} 未设置成本价格"
            )
        
        return {
            "id": cost_record.id,
            "product_id": cost_record.product_id,
            "supplier_id": cost_record.supplier_id,
            "delivery_type": cost_record.delivery_type,
            "version": cost_record.version,
            "cost_cny": cost_record.cost_cny or Decimal('0'),
            "cost_idr": cost_record.cost_idr or Decimal('0'),
            "effective_start_at": cost_record.effective_start_at,
            "effective_end_at": cost_record.effective_end_at
        }
    
    async def get_available_suppliers(self, product_id: str) -> List[Dict]:
        """
        获取可选供应商列表（包括内部团队）
        
        Args:
            product_id: 产品ID
            
        Returns:
            [
                {
                    "supplier_id": str,
                    "supplier_name": str,
                    "organization_type": str,
                    "delivery_type": str,
                    "cost_cny": Decimal,
                    "cost_idr": Decimal,
                    "version": int
                },
                ...
            ]
        """
        from sqlalchemy import text
        
        now = datetime.now()
        sql = text("""
            SELECT 
                sch.supplier_id,
                o.name AS supplier_name,
                o.organization_type,
                sch.delivery_type,
                sch.cost_cny,
                sch.cost_idr,
                sch.version
            FROM supplier_cost_history sch
            INNER JOIN organizations o ON sch.supplier_id = o.id
            WHERE sch.product_id = :product_id
              AND sch.is_current = 1
              AND sch.effective_start_at <= :now
              AND (sch.effective_end_at IS NULL OR sch.effective_end_at > :now)
              AND o.is_active = 1
            ORDER BY sch.cost_cny ASC
        """)
        
        result = await self.db.execute(
            sql,
            {"product_id": product_id, "now": now}
        )
        suppliers = result.fetchall()
        
        return [
            {
                "supplier_id": s.supplier_id,
                "supplier_name": s.supplier_name,
                "organization_type": s.organization_type,
                "delivery_type": s.delivery_type,
                "cost_cny": s.cost_cny or Decimal('0'),
                "cost_idr": s.cost_idr or Decimal('0'),
                "version": s.version
            }
            for s in suppliers
        ]
    
    async def select_supplier(
        self,
        product_id: str,
        preferred_supplier_id: Optional[str] = None
    ) -> Dict:
        """
        选择供应商
        
        规则：
        1. 如果指定了preferred_supplier_id，优先使用
        2. 如果产品不允许多供应商，使用默认供应商
        3. 否则选择成本最低的供应商
        
        Args:
            product_id: 产品ID
            preferred_supplier_id: 首选供应商ID，可选
            
        Returns:
            供应商成本价格信息
        """
        # 1. 查询产品信息
        product_result = await self.db.execute(
            select(Product).where(Product.id == product_id)
        )
        product = product_result.scalar_one_or_none()
        
        if not product:
            raise NotFoundError(f"产品 {product_id} 不存在")
        
        # 2. 如果不允许多供应商，使用默认供应商
        if not product.allow_multi_vendor:
            if product.default_supplier_id:
                return await self.get_cost_price(
                    product_id,
                    product.default_supplier_id
                )
            else:
                raise BusinessException(
                    detail="产品不允许多供应商但未设置默认供应商"
                )
        
        # 3. 获取所有可选供应商
        suppliers = await self.get_available_suppliers(product_id)
        
        if not suppliers:
            raise NotFoundError("没有可用的服务提供方")
        
        # 4. 如果指定了供应商，使用指定的
        if preferred_supplier_id:
            for s in suppliers:
                if s["supplier_id"] == preferred_supplier_id:
                    return await self.get_cost_price(
                        product_id,
                        preferred_supplier_id
                    )
            raise BusinessException(
                detail=f"指定的供应商 {preferred_supplier_id} 不可用"
            )
        
        # 5. 选择成本最低的供应商（CNY）
        suppliers.sort(key=lambda x: x["cost_cny"] or float('inf'))
        return await self.get_cost_price(
            product_id,
            suppliers[0]["supplier_id"]
        )
