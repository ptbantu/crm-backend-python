"""
汇率管理服务
"""
from typing import Optional, List, Dict
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from common.exceptions import BusinessException, NotFoundError
from foundation_service.repositories.exchange_rate_history_repository import ExchangeRateHistoryRepository
from foundation_service.schemas.price import (
    ExchangeRateHistoryRequest,
    ExchangeRateHistoryUpdateRequest,
    ExchangeRateHistoryResponse,
    ExchangeRateListResponse,
    CurrencyConvertRequest,
    CurrencyConvertResponse,
)
from common.utils.logger import get_logger

logger = get_logger(__name__)


class ExchangeRateService:
    """汇率管理服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rate_repo = ExchangeRateHistoryRepository(db)
    
    async def get_current_rates(
        self,
        from_currency: Optional[str] = None,
        to_currency: Optional[str] = None
    ) -> List[ExchangeRateHistoryResponse]:
        """获取当前有效汇率列表"""
        if from_currency and to_currency:
            # 查询特定货币对的汇率
            rate = await self.rate_repo.get_current_rate(from_currency, to_currency)
            if rate:
                return [ExchangeRateHistoryResponse.model_validate(rate)]
            return []
        else:
            # 查询所有当前有效汇率
            rates = await self.rate_repo.get_all_current_rates()
            return [ExchangeRateHistoryResponse.model_validate(rate) for rate in rates]
    
    async def get_rate_history(
        self,
        from_currency: Optional[str] = None,
        to_currency: Optional[str] = None,
        page: int = 1,
        size: int = 10
    ) -> ExchangeRateListResponse:
        """获取汇率历史记录"""
        items, total = await self.rate_repo.get_rate_history(
            from_currency=from_currency,
            to_currency=to_currency,
            page=page,
            size=size
        )
        return ExchangeRateListResponse(
            items=[ExchangeRateHistoryResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            size=size
        )
    
    async def create_rate(
        self,
        request: ExchangeRateHistoryRequest,
        changed_by: Optional[str] = None
    ) -> ExchangeRateHistoryResponse:
        """创建新汇率"""
        # 验证货币对
        if request.from_currency == request.to_currency:
            raise BusinessException(detail="源货币和目标货币不能相同")
        
        # 设置生效时间（默认为当前时间）
        effective_from = request.effective_from or datetime.now()
        
        # 创建汇率记录
        from common.models.exchange_rate_history import ExchangeRateHistory
        
        rate = ExchangeRateHistory(
            from_currency=request.from_currency,
            to_currency=request.to_currency,
            rate=request.rate,
            effective_from=effective_from,
            effective_to=request.effective_to,
            source=request.source,
            source_reference=request.source_reference,
            change_reason=request.change_reason,
            changed_by=changed_by
        )
        
        rate = await self.rate_repo.create(rate)
        
        return ExchangeRateHistoryResponse.model_validate(rate)
    
    async def update_rate(
        self,
        rate_id: str,
        request: ExchangeRateHistoryUpdateRequest,
        changed_by: Optional[str] = None
    ) -> ExchangeRateHistoryResponse:
        """更新汇率"""
        rate = await self.rate_repo.get_by_id(rate_id)
        if not rate:
            raise NotFoundError(f"汇率 {rate_id} 不存在")
        
        now = datetime.now()
        effective_from = request.effective_from
        if effective_from is None:
            effective_from = datetime.now()
        
        # 如果当前汇率已生效，且新汇率也是立即生效，则创建新记录并结束旧记录
        if rate.effective_from <= now and effective_from <= now:
            # 结束当前汇率记录
            rate.effective_to = now
            await self.rate_repo.update(rate)
            
            # 创建新的汇率记录
            from common.models.exchange_rate_history import ExchangeRateHistory
            
            new_rate = ExchangeRateHistory(
                from_currency=rate.from_currency,
                to_currency=rate.to_currency,
                rate=request.rate if request.rate is not None else rate.rate,
                effective_from=effective_from,
                effective_to=request.effective_to,
                source=rate.source,
                source_reference=rate.source_reference,
                change_reason=request.change_reason,
                changed_by=changed_by
            )
            
            new_rate = await self.rate_repo.create(new_rate)
            return ExchangeRateHistoryResponse.model_validate(new_rate)
        
        # 如果当前汇率还未生效（未来生效），可以直接更新
        if rate.effective_from > now:
            # 更新未来生效的汇率
            if request.rate is not None:
                rate.rate = request.rate
            if request.effective_from is not None:
                rate.effective_from = request.effective_from
            if request.effective_to is not None:
                rate.effective_to = request.effective_to
            if request.change_reason is not None:
                rate.change_reason = request.change_reason
            
            rate.changed_by = changed_by
            rate = await self.rate_repo.update(rate)
            return ExchangeRateHistoryResponse.model_validate(rate)
        
        # 其他情况：创建新记录
        from common.models.exchange_rate_history import ExchangeRateHistory
        
        # 如果新汇率是未来生效，保持当前汇率不变
        # 如果新汇率是立即生效，结束当前汇率
        if effective_from <= now:
            rate.effective_to = now
            await self.rate_repo.update(rate)
        
        new_rate = ExchangeRateHistory(
            from_currency=rate.from_currency,
            to_currency=rate.to_currency,
            rate=request.rate if request.rate is not None else rate.rate,
            effective_from=effective_from,
            effective_to=request.effective_to,
            source=rate.source,
            source_reference=rate.source_reference,
            change_reason=request.change_reason,
            changed_by=changed_by
        )
        
        new_rate = await self.rate_repo.create(new_rate)
        return ExchangeRateHistoryResponse.model_validate(new_rate)
    
    async def convert_currency(
        self,
        request: CurrencyConvertRequest
    ) -> CurrencyConvertResponse:
        """货币换算"""
        # 获取当前有效汇率
        rate = await self.rate_repo.get_current_rate(
            request.from_currency,
            request.to_currency
        )
        
        if not rate:
            raise NotFoundError(
                f"未找到 {request.from_currency} 到 {request.to_currency} 的汇率"
            )
        
        # 计算换算金额
        converted_amount = request.amount * rate.rate
        
        return CurrencyConvertResponse(
            from_currency=request.from_currency,
            to_currency=request.to_currency,
            from_amount=request.amount,
            to_amount=converted_amount,
            rate=rate.rate,
            rate_effective_from=rate.effective_from
        )
    
    async def calculate_rate_impact(
        self,
        rate_id: str
    ) -> Dict:
        """计算汇率变更影响"""
        rate = await self.rate_repo.get_by_id(rate_id)
        if not rate:
            raise NotFoundError(f"汇率 {rate_id} 不存在")
        
        # 这里可以添加更复杂的逻辑来计算影响
        # 例如：查询使用该汇率的订单数量、预计影响金额等
        
        return {
            "rate_id": rate_id,
            "from_currency": rate.from_currency,
            "to_currency": rate.to_currency,
            "estimated_affected_orders": 0,  # 需要实际查询
            "impact_analysis": {}
        }
