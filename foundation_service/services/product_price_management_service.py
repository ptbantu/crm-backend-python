"""
产品价格管理服务 - 价格历史、价格变更管理
"""
from typing import Optional, List, Dict
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from common.models.product_price import ProductPrice
from common.models.product import Product
from common.exceptions import BusinessException, NotFoundError
from foundation_service.repositories.product_price_history_repository import ProductPriceHistoryRepository
from foundation_service.repositories.price_change_log_repository import PriceChangeLogRepository
from foundation_service.repositories.product_repository import ProductRepository
from foundation_service.services.product_price_sync_service import ProductPriceSyncService
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
        organization_id: Optional[str] = None,
        page: int = 1,
        size: int = 10
    ) -> ProductPriceListResponse:
        """获取产品价格列表（列格式：一条记录包含所有价格）"""
        if product_id:
            # 查询特定产品的价格历史
            items, total = await self.price_history_repo.get_by_product_id(
                product_id=product_id,
                page=page,
                size=size,
                organization_id=organization_id
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
                and_(
                    ProductPrice.effective_from <= now,
                    or_(
                        ProductPrice.effective_to.is_(None),
                        ProductPrice.effective_to > now
                    )
                )
            )
            
            # 组织ID筛选
            if organization_id is not None:
                query = query.where(ProductPrice.organization_id == organization_id)
            else:
                query = query.where(ProductPrice.organization_id.is_(None))
            
            # 总数查询
            from sqlalchemy import func
            count_query = select(func.count()).select_from(ProductPrice).where(
                and_(
                    ProductPrice.effective_from <= now,
                    or_(
                        ProductPrice.effective_to.is_(None),
                        ProductPrice.effective_to > now
                    )
                )
            )
            if organization_id is not None:
                count_query = count_query.where(ProductPrice.organization_id == organization_id)
            else:
                count_query = count_query.where(ProductPrice.organization_id.is_(None))
            
            total_result = await self.db.execute(count_query)
            total = total_result.scalar() or 0
            
            # 分页查询
            query = query.order_by(ProductPrice.effective_from.desc())
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
        organization_id: Optional[str] = None,
        page: int = 1,
        size: int = 10
    ) -> ProductPriceListResponse:
        """获取产品价格历史记录（列格式：一条记录包含所有价格）"""
        items, total = await self.price_history_repo.get_by_product_id(
            product_id=product_id,
            page=page,
            size=size,
            organization_id=organization_id
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
        """创建新价格（列格式：一条记录包含所有价格）"""
        # 使用 ProductPriceSyncService 来创建价格（包含完整的验证和生效时间逻辑）
        sync_service = ProductPriceSyncService(self.db, user_id=changed_by)
        
        price = await sync_service.sync_product_prices(
            product_id=request.product_id,
            price_channel_idr=request.price_channel_idr,
            price_channel_cny=request.price_channel_cny,
            price_direct_idr=request.price_direct_idr,
            price_direct_cny=request.price_direct_cny,
            price_list_idr=request.price_list_idr,
            price_list_cny=request.price_list_cny,
            exchange_rate=request.exchange_rate,
            change_reason=request.change_reason,
            effective_from=request.effective_from,
            organization_id=request.organization_id
        )
        
        return ProductPriceHistoryResponse.model_validate(price)
    
    async def update_price(
        self,
        price_id: str,
        request: ProductPriceHistoryUpdateRequest,
        changed_by: Optional[str] = None
    ) -> ProductPriceHistoryResponse:
        """更新价格（列格式：一条记录包含所有价格）"""
        # 获取现有价格记录
        existing_price = await self.price_history_repo.get_by_id(price_id)
        if not existing_price:
            raise NotFoundError(f"价格 {price_id} 不存在")
        
        # 验证产品是否存在且未锁定
        product = await self.product_repo.get_by_id(existing_price.product_id)
        if not product:
            raise NotFoundError(f"产品 {existing_price.product_id} 不存在")
        
        if hasattr(product, 'price_locked') and product.price_locked:
            raise BusinessException(detail="产品价格已锁定，无法修改")
        
        # 合并更新字段（保留未更新的字段）
        price_channel_idr = request.price_channel_idr if request.price_channel_idr is not None else existing_price.price_channel_idr
        price_channel_cny = request.price_channel_cny if request.price_channel_cny is not None else existing_price.price_channel_cny
        price_direct_idr = request.price_direct_idr if request.price_direct_idr is not None else existing_price.price_direct_idr
        price_direct_cny = request.price_direct_cny if request.price_direct_cny is not None else existing_price.price_direct_cny
        price_list_idr = request.price_list_idr if request.price_list_idr is not None else existing_price.price_list_idr
        price_list_cny = request.price_list_cny if request.price_list_cny is not None else existing_price.price_list_cny
        exchange_rate = request.exchange_rate if request.exchange_rate is not None else existing_price.exchange_rate
        effective_from = request.effective_from if request.effective_from is not None else existing_price.effective_from
        
        # 使用 ProductPriceSyncService 来更新价格（包含完整的验证和生效时间逻辑）
        sync_service = ProductPriceSyncService(self.db, user_id=changed_by)
        
        price = await sync_service.sync_product_prices(
            product_id=existing_price.product_id,
            price_channel_idr=price_channel_idr,
            price_channel_cny=price_channel_cny,
            price_direct_idr=price_direct_idr,
            price_direct_cny=price_direct_cny,
            price_list_idr=price_list_idr,
            price_list_cny=price_list_cny,
            exchange_rate=exchange_rate,
            change_reason=request.change_reason or existing_price.change_reason,
            effective_from=effective_from,
            organization_id=existing_price.organization_id
        )
        
        return ProductPriceHistoryResponse.model_validate(price)
    
    async def cancel_future_price(
        self,
        price_id: str,
        changed_by: Optional[str] = None
    ) -> None:
        """取消未来生效的价格（列格式：一条记录包含所有价格）"""
        price = await self.price_history_repo.get_by_id(price_id)
        if not price:
            raise NotFoundError(f"价格 {price_id} 不存在")
        
        # 只能取消未来生效的价格
        if price.effective_from <= datetime.now():
            raise BusinessException(detail="只能取消未来生效的价格")
        
        # 删除价格记录
        await self.price_history_repo.delete(price)
        
        # 记录价格变更日志（注意：列格式下，需要记录所有价格字段的变化）
        # 这里简化处理，只记录删除操作
        # TODO: 如果需要详细的价格变更日志，需要记录所有价格字段的变化
    
    async def get_upcoming_price_changes(
        self,
        product_id: Optional[str] = None,
        hours_ahead: int = 24
    ) -> List[UpcomingPriceChangeResponse]:
        """获取即将生效的价格变更（列格式：一条记录包含所有价格）"""
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
                # 价格字段（列格式）
                price_channel_idr=price.price_channel_idr,
                price_channel_cny=price.price_channel_cny,
                price_direct_idr=price.price_direct_idr,
                price_direct_cny=price.price_direct_cny,
                price_list_idr=price.price_list_idr,
                price_list_cny=price.price_list_cny,
                exchange_rate=price.exchange_rate,
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
