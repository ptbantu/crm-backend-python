"""
价格验证服务
参考市面上主流CRM系统的价格管理验证逻辑，提供全面的价格变更验证
"""
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from common.models.product import Product
from common.models.product_price import ProductPrice
from common.models.vendor_product import VendorProduct
from common.exceptions import BusinessException
from common.utils.logger import get_logger

logger = get_logger(__name__)


class PriceValidationService:
    """价格验证服务 - 提供全面的价格变更验证逻辑"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def validate_price_update(
        self,
        product_id: str,
        price_channel_idr: Optional[Decimal] = None,
        price_channel_cny: Optional[Decimal] = None,
        price_direct_idr: Optional[Decimal] = None,
        price_direct_cny: Optional[Decimal] = None,
        price_list_idr: Optional[Decimal] = None,
        price_list_cny: Optional[Decimal] = None,
        effective_from: Optional[datetime] = None,
        change_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        验证价格更新
        
        Returns:
            {
                "is_valid": bool,
                "warnings": List[str],
                "errors": List[str],
                "validation_details": Dict
            }
        """
        errors = []
        warnings = []
        validation_details = {}
        
        # 1. 基础验证
        product = await self._validate_product_exists(product_id, errors)
        if not product:
            return {"is_valid": False, "errors": errors, "warnings": warnings, "validation_details": {}}
        
        # 2. 产品状态验证
        await self._validate_product_status(product, errors)
        
        # 3. 价格值验证
        prices = {
            'channel_idr': price_channel_idr,
            'channel_cny': price_channel_cny,
            'direct_idr': price_direct_idr,
            'direct_cny': price_direct_cny,
            'list_idr': price_list_idr,
            'list_cny': price_list_cny,
        }
        await self._validate_price_values(prices, errors, warnings)
        
        # 4. 价格合理性验证（不能低于成本价）
        await self._validate_price_vs_cost(product_id, prices, warnings)
        
        # 5. 价格变动幅度验证
        await self._validate_price_change_percentage(product_id, prices, warnings, validation_details)
        
        # 6. 生效时间验证
        await self._validate_effective_time(effective_from, errors, warnings)
        
        # 7. 价格修改频率验证
        await self._validate_price_change_frequency(product_id, warnings)
        
        # 8. 变更原因验证
        await self._validate_change_reason(change_reason, warnings)
        
        # 9. 价格层级关系验证（列表价 >= 直客价 >= 渠道价）
        await self._validate_price_hierarchy(prices, warnings)
        
        # 10. 汇率一致性验证
        await self._validate_exchange_rate_consistency(product_id, prices, warnings)
        
        is_valid = len(errors) == 0
        
        return {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "validation_details": validation_details
        }
    
    async def _validate_product_exists(self, product_id: str, errors: List[str]) -> Optional[Product]:
        """验证产品是否存在"""
        result = await self.db.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        
        if not product:
            errors.append(f"产品 {product_id} 不存在")
        
        return product
    
    async def _validate_product_status(self, product: Product, errors: List[str]) -> None:
        """验证产品状态"""
        if product.status == "discontinued":
            errors.append("产品已停用，无法修改价格")
        elif product.status == "suspended":
            errors.append("产品已暂停，无法修改价格")
        
        # 检查产品价格是否锁定（如果有这个字段）
        if hasattr(product, 'price_locked') and product.price_locked:
            errors.append("产品价格已锁定，无法修改")
    
    async def _validate_price_values(self, prices: Dict[str, Optional[Decimal]], errors: List[str], warnings: List[str]) -> None:
        """验证价格值"""
        for price_type, price_value in prices.items():
            if price_value is not None:
                # 价格不能为负数
                if price_value < 0:
                    errors.append(f"{price_type} 价格不能为负数")
                
                # 价格不能为0（除非是特殊业务场景）
                if price_value == 0:
                    warnings.append(f"{price_type} 价格为0，请确认是否正确")
                
                # 价格精度验证（不能超过18位，小数点后2位）
                if price_value.as_tuple().exponent < -2:
                    warnings.append(f"{price_type} 价格精度超过2位小数，将四舍五入")
    
    async def _validate_price_vs_cost(self, product_id: str, prices: Dict[str, Optional[Decimal]], warnings: List[str]) -> None:
        """验证价格不能低于成本价"""
        # 从 product_prices 表查询当前有效的成本价
        now = datetime.now()
        price_result = await self.db.execute(
            select(ProductPrice).where(
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
        )
        price_record = price_result.scalar_one_or_none()
        
        # 从 product_prices 表获取成本价
        if price_record:
            cost_idr = price_record.price_cost_idr
            cost_cny = price_record.price_cost_cny
        else:
            # 如果没有成本价，跳过验证
            return
        
        # 如果成本价为 None，跳过验证
        if not cost_idr and not cost_cny:
            return
        
        if cost_idr:
            if prices.get('channel_idr') and prices['channel_idr'] < cost_idr:
                warnings.append(f"渠道价-IDR ({prices['channel_idr']}) 低于成本价 ({cost_idr})，可能导致亏损")
            if prices.get('direct_idr') and prices['direct_idr'] < cost_idr:
                warnings.append(f"直客价-IDR ({prices['direct_idr']}) 低于成本价 ({cost_idr})，可能导致亏损")
            if prices.get('list_idr') and prices['list_idr'] < cost_idr:
                warnings.append(f"列表价-IDR ({prices['list_idr']}) 低于成本价 ({cost_idr})，可能导致亏损")
        
        if cost_cny:
            if prices.get('channel_cny') and prices['channel_cny'] < cost_cny:
                warnings.append(f"渠道价-CNY ({prices['channel_cny']}) 低于成本价 ({cost_cny})，可能导致亏损")
            if prices.get('direct_cny') and prices['direct_cny'] < cost_cny:
                warnings.append(f"直客价-CNY ({prices['direct_cny']}) 低于成本价 ({cost_cny})，可能导致亏损")
            if prices.get('list_cny') and prices['list_cny'] < cost_cny:
                warnings.append(f"列表价-CNY ({prices['list_cny']}) 低于成本价 ({cost_cny})，可能导致亏损")
    
    async def _validate_price_change_percentage(
        self,
        product_id: str,
        prices: Dict[str, Optional[Decimal]],
        warnings: List[str],
        validation_details: Dict
    ) -> None:
        """验证价格变动幅度"""
        # 查询当前有效价格
        now = datetime.now()
        current_price_query = select(ProductPrice).where(
            and_(
                ProductPrice.product_id == product_id,
                ProductPrice.organization_id.is_(None),
                ProductPrice.effective_from <= now,
                or_(
                    ProductPrice.effective_to.is_(None),
                    ProductPrice.effective_to >= now
                )
            )
        ).order_by(ProductPrice.effective_from.desc()).limit(1)
        
        result = await self.db.execute(current_price_query)
        current_price = result.scalar_one_or_none()
        
        if not current_price:
            return
        
        # 价格变动幅度阈值（可配置）
        WARNING_THRESHOLD = 10  # 10% 变动警告
        ERROR_THRESHOLD = 50    # 50% 变动错误（可配置为需要特殊审批）
        
        price_changes = {}
        
        # 检查每个价格字段的变动幅度
        price_mappings = {
            'channel_idr': ('price_channel_idr', '渠道价-IDR'),
            'channel_cny': ('price_channel_cny', '渠道价-CNY'),
            'direct_idr': ('price_direct_idr', '直客价-IDR'),
            'direct_cny': ('price_direct_cny', '直客价-CNY'),
            'list_idr': ('price_list_idr', '列表价-IDR'),
            'list_cny': ('price_list_cny', '列表价-CNY'),
        }
        
        for key, (field_name, display_name) in price_mappings.items():
            new_price = prices.get(key)
            old_price = getattr(current_price, field_name, None)
            
            if new_price is not None and old_price is not None and old_price > 0:
                change_percentage = abs((new_price - old_price) / old_price * 100)
                price_changes[key] = {
                    'old_price': float(old_price),
                    'new_price': float(new_price),
                    'change_percentage': float(change_percentage)
                }
                
                if change_percentage >= ERROR_THRESHOLD:
                    warnings.append(
                        f"{display_name} 变动幅度过大 ({change_percentage:.2f}%)，"
                        f"从 {old_price} 变更为 {new_price}，请确认是否正确"
                    )
                elif change_percentage >= WARNING_THRESHOLD:
                    warnings.append(
                        f"{display_name} 变动幅度较大 ({change_percentage:.2f}%)，"
                        f"从 {old_price} 变更为 {new_price}"
                    )
        
        validation_details['price_changes'] = price_changes
    
    async def _validate_effective_time(
        self,
        effective_from: Optional[datetime],
        errors: List[str],
        warnings: List[str]
    ) -> None:
        """验证生效时间"""
        if effective_from is None:
            return
        
        now = datetime.now()
        
        # 生效时间不能太早（不能早于1年前）
        one_year_ago = now - timedelta(days=365)
        if effective_from < one_year_ago:
            errors.append(f"生效时间不能早于1年前：{effective_from.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 生效时间不能太晚（不能晚于1年后）
        one_year_later = now + timedelta(days=365)
        if effective_from > one_year_later:
            warnings.append(f"生效时间较晚（{effective_from.strftime('%Y-%m-%d %H:%M:%S')}），请确认是否需要提前公告")
        
        # 未来生效时间建议至少提前1天（便于公告）
        if effective_from > now:
            days_ahead = (effective_from - now).days
            if days_ahead < 1:
                warnings.append("未来生效价格建议至少提前1天设置，以便提前公告给销售和相关人员")
    
    async def _validate_price_change_frequency(self, product_id: str, warnings: List[str]) -> None:
        """验证价格修改频率"""
        # 查询最近7天的价格修改次数
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        recent_changes_query = select(func.count(ProductPrice.id)).where(
            and_(
                ProductPrice.product_id == product_id,
                ProductPrice.created_at >= seven_days_ago
            )
        )
        
        result = await self.db.execute(recent_changes_query)
        recent_changes_count = result.scalar() or 0
        
        if recent_changes_count >= 5:
            warnings.append(f"该产品在最近7天内已修改价格 {recent_changes_count} 次，频繁修改可能影响业务稳定性")
    
    async def _validate_change_reason(self, change_reason: Optional[str], warnings: List[str]) -> None:
        """验证变更原因"""
        if not change_reason or len(change_reason.strip()) == 0:
            warnings.append("建议填写价格变更原因，便于追溯和审计")
        elif len(change_reason.strip()) < 5:
            warnings.append("价格变更原因过短，建议提供更详细的说明")
    
    async def _validate_price_hierarchy(self, prices: Dict[str, Optional[Decimal]], warnings: List[str]) -> None:
        """验证价格层级关系：列表价 >= 直客价 >= 渠道价"""
        # IDR价格层级验证
        if prices.get('list_idr') and prices.get('direct_idr') and prices.get('channel_idr'):
            if prices['list_idr'] < prices['direct_idr']:
                warnings.append("列表价-IDR 应大于等于直客价-IDR")
            if prices['direct_idr'] < prices['channel_idr']:
                warnings.append("直客价-IDR 应大于等于渠道价-IDR")
            if prices['list_idr'] < prices['channel_idr']:
                warnings.append("列表价-IDR 应大于等于渠道价-IDR")
        
        # CNY价格层级验证
        if prices.get('list_cny') and prices.get('direct_cny') and prices.get('channel_cny'):
            if prices['list_cny'] < prices['direct_cny']:
                warnings.append("列表价-CNY 应大于等于直客价-CNY")
            if prices['direct_cny'] < prices['channel_cny']:
                warnings.append("直客价-CNY 应大于等于渠道价-CNY")
            if prices['list_cny'] < prices['channel_cny']:
                warnings.append("列表价-CNY 应大于等于渠道价-CNY")
    
    async def _validate_exchange_rate_consistency(
        self,
        product_id: str,
        prices: Dict[str, Optional[Decimal]],
        warnings: List[str]
    ) -> None:
        """验证汇率一致性（IDR和CNY价格之间的汇率关系）"""
        # 从 product_prices 表获取当前有效价格的汇率
        from common.models.product_price import ProductPrice
        from sqlalchemy import and_
        from datetime import datetime
        
        now = datetime.now()
        price_result = await self.db.execute(
            select(ProductPrice).where(
                and_(
                    ProductPrice.product_id == product_id,
                    ProductPrice.organization_id.is_(None),  # 通用价格
                    ProductPrice.effective_from <= now,
                    or_(
                        ProductPrice.effective_to.is_(None),
                        ProductPrice.effective_to >= now
                    )
                )
            ).order_by(ProductPrice.effective_from.desc())
            .limit(1)
        )
        price_record = price_result.scalar_one_or_none()
        
        if not price_record or not price_record.exchange_rate:
            return
        
        exchange_rate = price_record.exchange_rate
        
        # 验证渠道价的汇率一致性
        if prices.get('channel_idr') and prices.get('channel_cny'):
            calculated_cny = prices['channel_idr'] / exchange_rate
            difference = abs(prices['channel_cny'] - calculated_cny)
            if difference > calculated_cny * 0.05:  # 5% 容差
                warnings.append(
                    f"渠道价汇率不一致：IDR {prices['channel_idr']} / CNY {prices['channel_cny']} "
                    f"≈ {prices['channel_idr'] / prices['channel_cny']:.2f}，"
                    f"产品汇率：{exchange_rate}"
                )
        
        # 验证直客价的汇率一致性
        if prices.get('direct_idr') and prices.get('direct_cny'):
            calculated_cny = prices['direct_idr'] / exchange_rate
            difference = abs(prices['direct_cny'] - calculated_cny)
            if difference > calculated_cny * 0.05:  # 5% 容差
                warnings.append(
                    f"直客价汇率不一致：IDR {prices['direct_idr']} / CNY {prices['direct_cny']} "
                    f"≈ {prices['direct_idr'] / prices['direct_cny']:.2f}，"
                    f"产品汇率：{exchange_rate}"
                )
        
        # 验证列表价的汇率一致性
        if prices.get('list_idr') and prices.get('list_cny'):
            calculated_cny = prices['list_idr'] / exchange_rate
            difference = abs(prices['list_cny'] - calculated_cny)
            if difference > calculated_cny * 0.05:  # 5% 容差
                warnings.append(
                    f"列表价汇率不一致：IDR {prices['list_idr']} / CNY {prices['list_cny']} "
                    f"≈ {prices['list_idr'] / prices['list_cny']:.2f}，"
                    f"产品汇率：{exchange_rate}"
                )
