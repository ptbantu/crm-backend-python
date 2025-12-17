"""
产品价格管理服务 - 价格历史、价格变更管理
"""
from typing import Optional, List, Dict
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from common.models.product_price import ProductPrice
from common.models.product import Product
from common.exceptions import BusinessException, NotFoundError
from foundation_service.repositories.product_price_history_repository import ProductPriceHistoryRepository
from foundation_service.repositories.price_change_log_repository import PriceChangeLogRepository
from foundation_service.repositories.product_repository import ProductRepository
from foundation_service.schemas.price import (
    ProductPriceHistoryRequest,
    ProductPriceHistoryUpdateRequest,
    ProductPriceHistoryResponse,
    ProductPriceListResponse,
    UpcomingPriceChangeResponse,
)
from common.utils.logger import get_logger

logger = get_logger(__name__)


class ProductPriceManagementService:
    """产品价格管理服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.price_history_repo = ProductPriceHistoryRepository(db)
        self.price_log_repo = PriceChangeLogRepository(db)
        self.product_repo = ProductRepository(db)
    
    async def get_product_prices(
        self,
        product_id: Optional[str] = None,
        price_type: Optional[str] = None,
        currency: Optional[str] = None,
        organization_id: Optional[str] = None,
        page: int = 1,
        size: int = 10
    ) -> ProductPriceListResponse:
        """获取产品价格列表"""
        if product_id:
            # 查询特定产品的价格历史
            items, total = await self.price_history_repo.get_by_product_id(
                product_id=product_id,
                page=page,
                size=size,
                price_type=price_type,
                currency=currency
            )
            return ProductPriceListResponse(
                items=[ProductPriceHistoryResponse.model_validate(item) for item in items],
                total=total,
                page=page,
                size=size
            )
        else:
            # 查询所有产品的当前有效价格
            now = datetime.now()
            query = select(ProductPrice).where(
                ProductPrice.effective_from <= now
            ).where(
                (ProductPrice.effective_to.is_(None)) | (ProductPrice.effective_to > now)
            )
            
            if price_type:
                query = query.where(ProductPrice.price_type == price_type)
            if currency:
                query = query.where(ProductPrice.currency == currency)
            if organization_id:
                query = query.where(ProductPrice.organization_id == organization_id)
            
            # 总数查询
            from sqlalchemy import func
            count_query = select(func.count()).select_from(ProductPrice).where(
                ProductPrice.effective_from <= now
            ).where(
                (ProductPrice.effective_to.is_(None)) | (ProductPrice.effective_to > now)
            )
            if price_type:
                count_query = count_query.where(ProductPrice.price_type == price_type)
            if currency:
                count_query = count_query.where(ProductPrice.currency == currency)
            if organization_id:
                count_query = count_query.where(ProductPrice.organization_id == organization_id)
            
            total_result = await self.db.execute(count_query)
            total = total_result.scalar() or 0
            
            # 分页查询
            query = query.offset((page - 1) * size).limit(size)
            result = await self.db.execute(query)
            items = result.scalars().all()
            
            return ProductPriceListResponse(
                items=[ProductPriceHistoryResponse.model_validate(item) for item in items],
                total=total,
                page=page,
                size=size
            )
    
    async def get_product_price_by_id(self, price_id: str) -> ProductPriceHistoryResponse:
        """获取价格详情"""
        price = await self.price_history_repo.get_by_id(price_id)
        if not price:
            raise NotFoundError(f"价格 {price_id} 不存在")
        return ProductPriceHistoryResponse.model_validate(price)
    
    async def get_product_price_history(
        self,
        product_id: str,
        price_type: Optional[str] = None,
        currency: Optional[str] = None,
        page: int = 1,
        size: int = 10
    ) -> ProductPriceListResponse:
        """获取产品价格历史记录"""
        items, total = await self.price_history_repo.get_by_product_id(
            product_id=product_id,
            page=page,
            size=size,
            price_type=price_type,
            currency=currency
        )
        return ProductPriceListResponse(
            items=[ProductPriceHistoryResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            size=size
        )
    
    async def create_price(
        self,
        request: ProductPriceHistoryRequest,
        changed_by: Optional[str] = None
    ) -> ProductPriceHistoryResponse:
        """创建新价格"""
        # 验证产品是否存在
        product = await self.product_repo.get_by_id(request.product_id)
        if not product:
            raise NotFoundError(f"产品 {request.product_id} 不存在")
        
        # 检查产品价格是否锁定
        if hasattr(product, 'price_locked') and product.price_locked:
            raise BusinessException(detail="产品价格已锁定，无法修改")
        
        # 设置生效时间（默认为当前时间）
        effective_from = request.effective_from or datetime.now()
        
        # 如果是未来生效的价格，需要检查是否有冲突
        if effective_from > datetime.now():
            # 检查是否有重叠的未来价格
            existing = await self.price_history_repo.get_upcoming_prices(
                product_id=request.product_id
            )
            for existing_price in existing:
                if (existing_price.price_type == request.price_type and
                    existing_price.currency == request.currency and
                    existing_price.effective_from == effective_from):
                    raise BusinessException(
                        detail=f"已存在相同类型和货币的未来价格，生效时间为 {effective_from}"
                    )
        
        # 创建价格记录
        price = ProductPrice(
            product_id=request.product_id,
            organization_id=request.organization_id,
            price_type=request.price_type,
            currency=request.currency,
            amount=request.amount,
            exchange_rate=request.exchange_rate,
            effective_from=effective_from,
            effective_to=request.effective_to,
            source=request.source,
            change_reason=request.change_reason,
            changed_by=changed_by
        )
        
        price = await self.price_history_repo.create(price)
        
        # 记录价格变更日志
        await self.price_log_repo.create_log(
            product_id=request.product_id,
            price_id=price.id,
            change_type='create',
            price_type=request.price_type,
            currency=request.currency,
            new_price=float(request.amount),
            new_effective_from=effective_from,
            new_effective_to=request.effective_to,
            change_reason=request.change_reason,
            changed_by=changed_by
        )
        
        return ProductPriceHistoryResponse.model_validate(price)
    
    async def update_price(
        self,
        price_id: str,
        request: ProductPriceHistoryUpdateRequest,
        changed_by: Optional[str] = None
    ) -> ProductPriceHistoryResponse:
        """更新价格"""
        price = await self.price_history_repo.get_by_id(price_id)
        if not price:
            raise NotFoundError(f"价格 {price_id} 不存在")
        
        # 验证产品是否存在且未锁定
        product = await self.product_repo.get_by_id(price.product_id)
        if not product:
            raise NotFoundError(f"产品 {price.product_id} 不存在")
        
        if hasattr(product, 'price_locked') and product.price_locked:
            raise BusinessException(detail="产品价格已锁定，无法修改")
        
        # 保存旧值用于日志
        old_price = price.amount
        old_effective_from = price.effective_from
        old_effective_to = price.effective_to
        
        # 更新价格
        if request.amount is not None:
            price.amount = request.amount
        if request.exchange_rate is not None:
            price.exchange_rate = request.exchange_rate
        if request.effective_from is not None:
            price.effective_from = request.effective_from
        if request.effective_to is not None:
            price.effective_to = request.effective_to
        if request.change_reason is not None:
            price.change_reason = request.change_reason
        
        price.changed_by = changed_by
        price = await self.price_history_repo.update(price)
        
        # 记录价格变更日志
        await self.price_log_repo.create_log(
            product_id=price.product_id,
            price_id=price.id,
            change_type='update',
            price_type=price.price_type,
            currency=price.currency,
            old_price=float(old_price) if old_price else None,
            new_price=float(price.amount) if price.amount else None,
            old_effective_from=old_effective_from,
            new_effective_from=price.effective_from,
            old_effective_to=old_effective_to,
            new_effective_to=price.effective_to,
            change_reason=request.change_reason,
            changed_by=changed_by
        )
        
        return ProductPriceHistoryResponse.model_validate(price)
    
    async def cancel_future_price(
        self,
        price_id: str,
        changed_by: Optional[str] = None
    ) -> None:
        """取消未来生效的价格"""
        price = await self.price_history_repo.get_by_id(price_id)
        if not price:
            raise NotFoundError(f"价格 {price_id} 不存在")
        
        # 只能取消未来生效的价格
        if price.effective_from <= datetime.now():
            raise BusinessException(detail="只能取消未来生效的价格")
        
        # 删除价格记录
        await self.price_history_repo.delete(price)
        
        # 记录价格变更日志
        await self.price_log_repo.create_log(
            product_id=price.product_id,
            price_id=price.id,
            change_type='delete',
            price_type=price.price_type,
            currency=price.currency,
            old_price=float(price.amount) if price.amount else None,
            old_effective_from=price.effective_from,
            old_effective_to=price.effective_to,
            change_reason="取消未来生效的价格",
            changed_by=changed_by
        )
    
    async def get_upcoming_price_changes(
        self,
        product_id: Optional[str] = None,
        hours_ahead: int = 24
    ) -> List[UpcomingPriceChangeResponse]:
        """获取即将生效的价格变更"""
        upcoming_prices = await self.price_history_repo.get_upcoming_prices(
            product_id=product_id,
            hours_ahead=hours_ahead
        )
        
        result = []
        for price in upcoming_prices:
            # 获取产品信息
            product = await self.product_repo.get_by_id(price.product_id)
            
            # 计算小时数
            hours_until = None
            if price.effective_from:
                delta = price.effective_from - datetime.now()
                hours_until = int(delta.total_seconds() / 3600)
            
            result.append(UpcomingPriceChangeResponse(
                id=price.id,
                product_id=price.product_id,
                product_name=product.name if product else None,
                product_code=product.code if product else None,
                price_type=price.price_type,
                currency=price.currency,
                amount=price.amount,
                effective_from=price.effective_from,
                hours_until_effective=hours_until
            ))
        
        return result
    
    async def calculate_price_impact(
        self,
        price_id: str
    ) -> Dict:
        """计算价格变更影响"""
        price = await self.price_history_repo.get_by_id(price_id)
        if not price:
            raise NotFoundError(f"价格 {price_id} 不存在")
        
        # 这里可以添加更复杂的逻辑来计算影响
        # 例如：查询使用该价格的订单数量、预计影响金额等
        
        return {
            "price_id": price_id,
            "product_id": price.product_id,
            "estimated_affected_orders": 0,  # 需要实际查询
            "impact_analysis": {}
        }
