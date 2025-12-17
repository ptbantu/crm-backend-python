"""
产品价格同步服务
在创建/更新产品时，将 products 表中的价格同步到 product_prices 表
"""
from typing import Optional, Dict
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from common.models.product import Product
from common.models.product_price import ProductPrice
from common.models.price_change_log import PriceChangeLog
from common.exceptions import BusinessException
from common.utils.logger import get_logger
from foundation_service.services.price_validation_service import PriceValidationService

logger = get_logger(__name__)


class ProductPriceSyncService:
    """产品价格同步服务 - 将 products 表的价格同步到 product_prices 表"""
    
    def __init__(self, db: AsyncSession, user_id: Optional[str] = None):
        self.db = db
        self.user_id = user_id
        self.validation_service = PriceValidationService(db)
    
    async def sync_product_prices(
        self,
        product_id: str,
        price_channel_idr: Optional[Decimal] = None,
        price_channel_cny: Optional[Decimal] = None,
        price_direct_idr: Optional[Decimal] = None,
        price_direct_cny: Optional[Decimal] = None,
        price_list_idr: Optional[Decimal] = None,
        price_list_cny: Optional[Decimal] = None,
        price_cost_idr: Optional[Decimal] = None,
        price_cost_cny: Optional[Decimal] = None,
        exchange_rate: Optional[Decimal] = None,
        change_reason: Optional[str] = None,
        effective_from: Optional[datetime] = None,
        organization_id: Optional[str] = None
    ) -> ProductPrice:
        """
        同步产品价格到 product_prices 表（一条记录包含所有价格）
        
        价格生效时间处理逻辑：
        
        规则1: 如果产品没有价格，第一条价格必须立即生效
           - 无论用户设置什么生效时间，第一条价格都强制立即生效
           - effective_from = 当前时间
        
        规则2: 如果产品已有价格（包括未来价格），新的价格没有生效前不能创建更多未来价格
           - 如果已有未来价格，禁止创建新的未来价格（只能立即生效）
           - 如果没有未来价格，允许创建未来价格
        
        规则3: 立即生效价格（effective_from = None 或 <= 当前时间）：
           - 将当前有效价格的 effective_to 设置为当前时间
           - 新价格的 effective_from 设置为当前时间
        
        规则4: 未来生效价格（effective_from > 当前时间，且没有其他未来价格）：
           - 将当前有效价格的 effective_to 设置为新价格生效前1秒
           - 新价格的 effective_from 设置为指定时间
           - 新价格生效前，可以提前公告给销售和相关人员
        
        规则5: 过去生效价格（effective_from < 当前时间）：
           - 检查是否与现有价格冲突
           - 如果冲突，将冲突价格立即失效或删除
           - 将当前有效价格的 effective_to 设置为当前时间
           - 新价格的 effective_from 设置为指定时间（历史修正）
        
        Args:
            product_id: 产品ID
            price_channel_idr: 渠道价-IDR
            price_channel_cny: 渠道价-CNY
            price_direct_idr: 直客价-IDR
            price_direct_cny: 直客价-CNY
            price_list_idr: 列表价-IDR
            price_list_cny: 列表价-CNY
            price_cost_idr: 成本价-IDR
            price_cost_cny: 成本价-CNY
            exchange_rate: 汇率
            change_reason: 变更原因
            effective_from: 生效时间（可选，默认当前时间）
            organization_id: 组织ID（可选，NULL表示通用价格）
        """
        now = datetime.now()
        
        # 0. 价格验证（参考主流CRM系统的验证逻辑）
        # 注意：成本价不参与价格验证（成本价由供应商管理，不需要验证层级关系等）
        validation_result = await self.validation_service.validate_price_update(
            product_id=product_id,
            price_channel_idr=price_channel_idr,
            price_channel_cny=price_channel_cny,
            price_direct_idr=price_direct_idr,
            price_direct_cny=price_direct_cny,
            price_list_idr=price_list_idr,
            price_list_cny=price_list_cny,
            effective_from=effective_from,
            change_reason=change_reason
        )
        
        # 如果有错误，抛出异常
        if validation_result['errors']:
            error_message = "价格验证失败：\n" + "\n".join(f"- {error}" for error in validation_result['errors'])
            raise BusinessException(detail=error_message)
        
        # 如果有警告，记录日志
        if validation_result['warnings']:
            logger.warning(
                f"价格验证警告 | product_id={product_id} | "
                f"warnings={validation_result['warnings']}"
            )
        
        # 1. 检查产品是否已有价格记录（包括未来价格）
        all_prices_query = select(ProductPrice).where(
            and_(
                ProductPrice.product_id == product_id,
                ProductPrice.organization_id.is_(None) if organization_id is None else ProductPrice.organization_id == organization_id
            )
        )
        all_prices_result = await self.db.execute(all_prices_query)
        all_prices = all_prices_result.scalars().all()
        
        # 2. 如果产品没有价格，第一条价格必须立即生效
        if not all_prices:
            if effective_from is None:
                effective_from = datetime.now()
            elif effective_from > now:
                # 第一条价格不能是未来生效的，强制立即生效
                logger.warning(
                    f"产品 {product_id} 没有价格记录，第一条价格强制立即生效 | "
                    f"请求的生效时间: {effective_from}"
                )
                effective_from = datetime.now()
        else:
            # 3. 如果产品已有价格，检查是否有未来价格
            future_prices = [p for p in all_prices if p.effective_from > now]
            
            if future_prices:
                # 如果已有未来价格，禁止创建新的未来价格
                if effective_from is None:
                    effective_from = datetime.now()
                elif effective_from > now:
                    raise BusinessException(
                        f"产品已有未来生效的价格（生效时间: {future_prices[0].effective_from.strftime('%Y-%m-%d %H:%M:%S')}），"
                        f"在新价格生效前不能创建更多未来价格。请先等待现有未来价格生效，或设置立即生效的价格。"
                    )
                # 如果新价格是立即生效的，允许更新
            else:
                # 如果没有未来价格，允许设置未来生效的价格
                if effective_from is None:
                    effective_from = datetime.now()
                # 如果 effective_from > now，允许创建未来价格
        
        # 4. 查询当前有效的价格记录（用于失效）
        # 注意：如果新价格是未来生效的，当前价格应该保持有效直到新价格生效
        # 如果新价格是立即生效或过去生效的，当前价格应该立即失效
        current_price_query = select(ProductPrice).where(
            and_(
                ProductPrice.product_id == product_id,
                ProductPrice.organization_id.is_(None) if organization_id is None else ProductPrice.organization_id == organization_id,
                ProductPrice.effective_from <= now,  # 只查询当前或过去生效的
                or_(
                    ProductPrice.effective_to.is_(None),
                    ProductPrice.effective_to >= now
                )
            )
        ).order_by(ProductPrice.effective_from.desc()).limit(1)
        
        current_price_result = await self.db.execute(current_price_query)
        current_price = current_price_result.scalar_one_or_none()
        
        # 5. 如果新价格是过去生效的，检查是否与现有价格冲突
        if effective_from < now:
            # 查询在 effective_from 时间点有效的价格
            conflicting_price_query = select(ProductPrice).where(
                and_(
                    ProductPrice.product_id == product_id,
                    ProductPrice.organization_id.is_(None) if organization_id is None else ProductPrice.organization_id == organization_id,
                    ProductPrice.effective_from <= effective_from,
                    or_(
                        ProductPrice.effective_to.is_(None),
                        ProductPrice.effective_to >= effective_from
                    )
                )
            )
            conflicting_price_result = await self.db.execute(conflicting_price_query)
            conflicting_price = conflicting_price_result.scalar_one_or_none()
            
            if conflicting_price:
                # 如果冲突的价格是当前有效的，立即失效
                if conflicting_price.effective_from <= now and (
                    conflicting_price.effective_to is None or conflicting_price.effective_to >= now
                ):
                    conflicting_price.effective_to = now
                    await self.db.flush()
                # 如果冲突的价格是未来生效的，删除它（因为新价格更早）
                elif conflicting_price.effective_from > now:
                    await self.db.delete(conflicting_price)
                    await self.db.flush()
        
        # 6. 查询在 effective_from 时间点有效的价格（用于检查变化）
        query = select(ProductPrice).where(
            and_(
                ProductPrice.product_id == product_id,
                ProductPrice.organization_id.is_(None) if organization_id is None else ProductPrice.organization_id == organization_id,
                ProductPrice.effective_from <= effective_from,
                or_(
                    ProductPrice.effective_to.is_(None),
                    ProductPrice.effective_to >= effective_from
                )
            )
        ).order_by(ProductPrice.effective_from.desc()).limit(1)
        
        result = await self.db.execute(query)
        existing_price = result.scalar_one_or_none()
        
        # 7. 检查是否有价格变化
        has_changes = False
        if existing_price:
            # 检查每个价格字段是否有变化
            if price_channel_idr is not None and existing_price.price_channel_idr != price_channel_idr:
                has_changes = True
            if price_channel_cny is not None and existing_price.price_channel_cny != price_channel_cny:
                has_changes = True
            if price_direct_idr is not None and existing_price.price_direct_idr != price_direct_idr:
                has_changes = True
            if price_direct_cny is not None and existing_price.price_direct_cny != price_direct_cny:
                has_changes = True
            if price_list_idr is not None and existing_price.price_list_idr != price_list_idr:
                has_changes = True
            if price_list_cny is not None and existing_price.price_list_cny != price_list_cny:
                has_changes = True
            if price_cost_idr is not None and existing_price.price_cost_idr != price_cost_idr:
                has_changes = True
            if price_cost_cny is not None and existing_price.price_cost_cny != price_cost_cny:
                has_changes = True
            
            if not has_changes:
                logger.debug(f"价格未变化，跳过更新 | product_id={product_id}")
                return existing_price
            
            # 8. 将旧价格失效
            from datetime import timedelta
            if effective_from > now:
                # 未来生效：旧价格在新价格生效前失效（保持有效直到新价格生效）
                # 这样在生效时间之前，销售和相关人员可以看到公告，旧价格仍然有效
                existing_price.effective_to = effective_from - timedelta(seconds=1)
            else:
                # 立即生效或过去生效：旧价格立即失效
                existing_price.effective_to = now
            await self.db.flush()
            
            # 记录价格变更日志（记录所有变更的价格）
            await self._log_price_changes(
                product_id=product_id,
                price_id=existing_price.id,
                old_prices={
                    'channel_idr': existing_price.price_channel_idr,
                    'channel_cny': existing_price.price_channel_cny,
                    'direct_idr': existing_price.price_direct_idr,
                    'direct_cny': existing_price.price_direct_cny,
                    'list_idr': existing_price.price_list_idr,
                    'list_cny': existing_price.price_list_cny,
                    'cost_idr': existing_price.price_cost_idr,
                    'cost_cny': existing_price.price_cost_cny,
                },
                new_prices={
                    'channel_idr': price_channel_idr if price_channel_idr is not None else existing_price.price_channel_idr,
                    'channel_cny': price_channel_cny if price_channel_cny is not None else existing_price.price_channel_cny,
                    'direct_idr': price_direct_idr if price_direct_idr is not None else existing_price.price_direct_idr,
                    'direct_cny': price_direct_cny if price_direct_cny is not None else existing_price.price_direct_cny,
                    'list_idr': price_list_idr if price_list_idr is not None else existing_price.price_list_idr,
                    'list_cny': price_list_cny if price_list_cny is not None else existing_price.price_list_cny,
                    'cost_idr': price_cost_idr if price_cost_idr is not None else existing_price.price_cost_idr,
                    'cost_cny': price_cost_cny if price_cost_cny is not None else existing_price.price_cost_cny,
                },
                change_reason=change_reason
            )
        
        # 获取产品的汇率（如果未提供）
        if exchange_rate is None:
            # 从 product_prices 表获取当前有效价格的汇率
            price_result = await self.db.execute(
                select(ProductPrice).where(
                    and_(
                        ProductPrice.product_id == product_id,
                        ProductPrice.organization_id.is_(None) if organization_id is None else ProductPrice.organization_id == organization_id,
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
            if price_record and price_record.exchange_rate:
                exchange_rate = price_record.exchange_rate
        
        # 如果新价格是未来生效的，检查是否有更晚的未来价格，以确定新价格的 effective_to
        new_price_effective_to = None
        if effective_from > now:
            later_future_prices_query = select(ProductPrice).where(
                and_(
                    ProductPrice.product_id == product_id,
                    ProductPrice.organization_id.is_(None) if organization_id is None else ProductPrice.organization_id == organization_id,
                    ProductPrice.effective_from > effective_from  # 查询在新价格之后的未来价格
                )
            ).order_by(ProductPrice.effective_from.asc()).limit(1)
            
            later_future_prices_result = await self.db.execute(later_future_prices_query)
            next_future_price = later_future_prices_result.scalar_one_or_none()
            
            if next_future_price:
                # 如果存在更晚的未来价格，新价格的 effective_to 设置为下一个未来价格的生效时间前1秒
                from datetime import timedelta
                new_price_effective_to = next_future_price.effective_from - timedelta(seconds=1)
        
        # 创建新价格记录（如果不存在，使用旧记录的值）
        if existing_price:
            new_price = ProductPrice(
                product_id=product_id,
                organization_id=organization_id,
                price_channel_idr=price_channel_idr if price_channel_idr is not None else existing_price.price_channel_idr,
                price_channel_cny=price_channel_cny if price_channel_cny is not None else existing_price.price_channel_cny,
                price_direct_idr=price_direct_idr if price_direct_idr is not None else existing_price.price_direct_idr,
                price_direct_cny=price_direct_cny if price_direct_cny is not None else existing_price.price_direct_cny,
                price_list_idr=price_list_idr if price_list_idr is not None else existing_price.price_list_idr,
                price_list_cny=price_list_cny if price_list_cny is not None else existing_price.price_list_cny,
                price_cost_idr=price_cost_idr if price_cost_idr is not None else existing_price.price_cost_idr,
                price_cost_cny=price_cost_cny if price_cost_cny is not None else existing_price.price_cost_cny,
                exchange_rate=exchange_rate if exchange_rate is not None else existing_price.exchange_rate,
                effective_from=effective_from,
                effective_to=new_price_effective_to,  # 如果有更晚的未来价格，设置为下一个未来价格的生效时间前1秒；否则为None（表示当前有效）
                change_reason=change_reason,
                changed_by=self.user_id
            )
        else:
            new_price = ProductPrice(
                product_id=product_id,
                organization_id=organization_id,
                price_channel_idr=price_channel_idr,
                price_channel_cny=price_channel_cny,
                price_direct_idr=price_direct_idr,
                price_direct_cny=price_direct_cny,
                price_list_idr=price_list_idr,
                price_list_cny=price_list_cny,
                price_cost_idr=price_cost_idr,
                price_cost_cny=price_cost_cny,
                exchange_rate=exchange_rate,
                effective_from=effective_from,
                effective_to=new_price_effective_to,  # 如果有更晚的未来价格，设置为下一个未来价格的生效时间前1秒；否则为None（表示当前有效）
                change_reason=change_reason,
                changed_by=self.user_id
            )
        
        self.db.add(new_price)
        await self.db.flush()
        
        # 如果是新创建的价格，记录日志
        if not existing_price:
            await self._log_price_changes(
                product_id=product_id,
                price_id=new_price.id,
                old_prices={},
                new_prices={
                    'channel_idr': price_channel_idr,
                    'channel_cny': price_channel_cny,
                    'direct_idr': price_direct_idr,
                    'direct_cny': price_direct_cny,
                    'list_idr': price_list_idr,
                    'list_cny': price_list_cny,
                    'cost_idr': price_cost_idr,
                    'cost_cny': price_cost_cny,
                },
                change_reason=change_reason
            )
        
        logger.info(
            f"同步价格到 product_prices 表 | "
            f"product_id={product_id}, effective_from={effective_from}"
        )
        
        return new_price
    
    async def _log_price_changes(
        self,
        product_id: str,
        price_id: str,
        old_prices: Dict[str, Optional[Decimal]],
        new_prices: Dict[str, Optional[Decimal]],
        change_reason: Optional[str] = None
    ) -> None:
        """记录价格变更日志（记录所有变更的价格）"""
        price_mappings = [
            ('channel', 'IDR', 'channel_idr'),
            ('channel', 'CNY', 'channel_cny'),
            ('direct', 'IDR', 'direct_idr'),
            ('direct', 'CNY', 'direct_cny'),
            ('list', 'IDR', 'list_idr'),
            ('list', 'CNY', 'list_cny'),
            ('cost', 'IDR', 'cost_idr'),
            ('cost', 'CNY', 'cost_cny'),
        ]
        
        for price_type, currency, key in price_mappings:
            old_price = old_prices.get(key)
            new_price = new_prices.get(key)
            
            # 只记录有变化的价格
            if old_price != new_price:
                price_change_amount = None
                price_change_percentage = None
                
                if old_price is not None and new_price is not None and old_price > 0:
                    price_change_amount = new_price - old_price
                    price_change_percentage = (price_change_amount / old_price) * 100
                
                change_type = 'create' if old_price is None else 'update'
                
                log = PriceChangeLog(
                    product_id=product_id,
                    price_id=price_id,
                    change_type=change_type,
                    price_type=price_type,
                    currency=currency,
                    old_price=old_price,
                    new_price=new_price,
                    price_change_amount=price_change_amount,
                    price_change_percentage=price_change_percentage,
                    change_reason=change_reason,
                    changed_by=self.user_id
                )
                
                self.db.add(log)
        
        await self.db.flush()
        
        logger.debug(
            f"记录价格变更日志 | "
            f"product_id={product_id}, price_id={price_id}"
        )
