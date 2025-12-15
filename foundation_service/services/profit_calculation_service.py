"""
利润计算服务
"""
from typing import Dict, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from common.models.order_item import OrderItem
from common.models.order import Order
from common.exceptions import NotFoundError
from common.utils.logger import get_logger

logger = get_logger(__name__)


class ProfitCalculationService:
    """利润计算服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def calculate_order_item_profit(self, order_item_id: str) -> Dict:
        """
        计算订单项利润
        
        公式：订单项利润 = 销售价格 - 成本价格 - 浮动成本（报销）
        
        Args:
            order_item_id: 订单项ID
            
        Returns:
            {
                "order_item_id": str,
                "sales_price_cny": Decimal,
                "sales_price_idr": Decimal,
                "cost_cny": Decimal,
                "cost_idr": Decimal,
                "expense_cny": Decimal,
                "expense_idr": Decimal,
                "profit_cny": Decimal,
                "profit_idr": Decimal,
                "profit_rate_cny": Decimal,
                "profit_rate_idr": Decimal
            }
        """
        # 1. 查询订单项
        item_result = await self.db.execute(
            select(OrderItem).where(OrderItem.id == order_item_id)
        )
        order_item = item_result.scalar_one_or_none()
        
        if not order_item:
            raise NotFoundError(f"订单项 {order_item_id} 不存在")
        
        # 2. 销售价格（从订单项的快照）
        sales_price_cny = Decimal('0')
        sales_price_idr = Decimal('0')
        
        if order_item.currency_code == "CNY":
            sales_price_cny = order_item.unit_price or Decimal('0')
        elif order_item.currency_code == "IDR":
            sales_price_idr = order_item.unit_price or Decimal('0')
        
        # 3. 成本价格（从快照）
        cost_cny = order_item.snapshot_cost_cny or Decimal('0')
        cost_idr = order_item.snapshot_cost_idr or Decimal('0')
        
        # 4. 浮动成本（报销）
        from sqlalchemy import text
        
        expense_sql = text("""
            SELECT 
                COALESCE(SUM(CASE WHEN currency = 'CNY' THEN amount ELSE 0 END), 0) AS expense_cny,
                COALESCE(SUM(CASE WHEN currency = 'IDR' THEN amount ELSE 0 END), 0) AS expense_idr
            FROM biz_expense_records
            WHERE order_item_id = :order_item_id
              AND cost_attribution = 'EXECUTION'
              AND status = 'PAID'
        """)
        
        expense_result = await self.db.execute(
            expense_sql,
            {"order_item_id": order_item_id}
        )
        expense_row = expense_result.fetchone()
        
        expense_cny = Decimal(str(expense_row.expense_cny)) if expense_row else Decimal('0')
        expense_idr = Decimal(str(expense_row.expense_idr)) if expense_row else Decimal('0')
        
        # 5. 计算利润
        quantity = order_item.quantity or 1
        profit_cny = (sales_price_cny - cost_cny) * quantity - expense_cny
        profit_idr = (sales_price_idr - cost_idr) * quantity - expense_idr
        
        # 6. 计算利润率
        total_sales_cny = sales_price_cny * quantity
        total_sales_idr = sales_price_idr * quantity
        
        profit_rate_cny = (
            profit_cny / total_sales_cny
            if total_sales_cny > 0 else Decimal('0')
        )
        profit_rate_idr = (
            profit_idr / total_sales_idr
            if total_sales_idr > 0 else Decimal('0')
        )
        
        return {
            "order_item_id": order_item_id,
            "sales_price_cny": sales_price_cny,
            "sales_price_idr": sales_price_idr,
            "cost_cny": cost_cny,
            "cost_idr": cost_idr,
            "expense_cny": expense_cny,
            "expense_idr": expense_idr,
            "profit_cny": profit_cny,
            "profit_idr": profit_idr,
            "profit_rate_cny": profit_rate_cny,
            "profit_rate_idr": profit_rate_idr,
            "quantity": quantity
        }
    
    async def calculate_order_profit(self, order_id: str) -> Dict:
        """
        计算订单总利润
        
        公式：订单利润 = Σ(订单项利润) - 订单级浮动成本（报销）
        
        Args:
            order_id: 订单ID
            
        Returns:
            {
                "order_id": str,
                "total_sales_cny": Decimal,
                "total_sales_idr": Decimal,
                "total_profit_cny": Decimal,
                "total_profit_idr": Decimal,
                "profit_rate_cny": Decimal,
                "profit_rate_idr": Decimal,
                "items": [
                    {
                        "order_item_id": str,
                        "profit_cny": Decimal,
                        "profit_idr": Decimal
                    },
                    ...
                ]
            }
        """
        # 1. 查询订单项列表
        items_result = await self.db.execute(
            select(OrderItem).where(OrderItem.order_id == order_id)
        )
        order_items = items_result.scalars().all()
        
        if not order_items:
            raise NotFoundError(f"订单 {order_id} 没有订单项")
        
        # 2. 计算所有订单项的利润
        total_profit_cny = Decimal('0')
        total_profit_idr = Decimal('0')
        total_sales_cny = Decimal('0')
        total_sales_idr = Decimal('0')
        items_profit = []
        
        for item in order_items:
            item_profit = await self.calculate_order_item_profit(item.id)
            
            total_profit_cny += item_profit["profit_cny"]
            total_profit_idr += item_profit["profit_idr"]
            total_sales_cny += item_profit["sales_price_cny"] * item_profit["quantity"]
            total_sales_idr += item_profit["sales_price_idr"] * item_profit["quantity"]
            
            items_profit.append({
                "order_item_id": item.id,
                "profit_cny": item_profit["profit_cny"],
                "profit_idr": item_profit["profit_idr"]
            })
        
        # 3. 订单级浮动成本（报销）
        from sqlalchemy import text
        
        order_expense_sql = text("""
            SELECT 
                COALESCE(SUM(CASE WHEN currency = 'CNY' THEN amount ELSE 0 END), 0) AS expense_cny,
                COALESCE(SUM(CASE WHEN currency = 'IDR' THEN amount ELSE 0 END), 0) AS expense_idr
            FROM biz_expense_records
            WHERE order_id = :order_id
              AND cost_attribution = 'SALES'
              AND status = 'PAID'
        """)
        
        expense_result = await self.db.execute(
            order_expense_sql,
            {"order_id": order_id}
        )
        expense_row = expense_result.fetchone()
        
        order_expense_cny = Decimal(str(expense_row.expense_cny)) if expense_row else Decimal('0')
        order_expense_idr = Decimal(str(expense_row.expense_idr)) if expense_row else Decimal('0')
        
        # 4. 计算最终利润
        final_profit_cny = total_profit_cny - order_expense_cny
        final_profit_idr = total_profit_idr - order_expense_idr
        
        # 5. 计算利润率
        profit_rate_cny = (
            final_profit_cny / total_sales_cny
            if total_sales_cny > 0 else Decimal('0')
        )
        profit_rate_idr = (
            final_profit_idr / total_sales_idr
            if total_sales_idr > 0 else Decimal('0')
        )
        
        return {
            "order_id": order_id,
            "total_sales_cny": total_sales_cny,
            "total_sales_idr": total_sales_idr,
            "total_profit_cny": final_profit_cny,
            "total_profit_idr": final_profit_idr,
            "profit_rate_cny": profit_rate_cny,
            "profit_rate_idr": profit_rate_idr,
            "order_expense_cny": order_expense_cny,
            "order_expense_idr": order_expense_idr,
            "items": items_profit
        }
