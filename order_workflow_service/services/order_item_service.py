"""
订单项服务
"""
import time
from typing import Optional, List
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from order_workflow_service.models.order_item import OrderItem
from order_workflow_service.repositories.order_item_repository import OrderItemRepository
from order_workflow_service.schemas.order_item import (
    OrderItemCreateRequest,
    OrderItemUpdateRequest,
    OrderItemResponse,
    OrderItemListResponse,
)
from order_workflow_service.utils.i18n import get_localized_field
from common.utils.logger import get_logger
from common.exceptions import BusinessException

logger = get_logger(__name__)


class OrderItemService:
    """订单项服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = OrderItemRepository(db)
    
    def _calculate_item_amount(
        self,
        quantity: int,
        unit_price: Optional[Decimal],
        discount_amount: Decimal
    ) -> Optional[Decimal]:
        """
        计算订单项金额
        
        Args:
            quantity: 数量
            unit_price: 单价
            discount_amount: 折扣金额
            
        Returns:
            订单项金额（quantity * unit_price - discount_amount）
        """
        if unit_price is None:
            return None
        return Decimal(quantity) * unit_price - discount_amount
    
    async def create_order_item(
        self,
        request: OrderItemCreateRequest,
        created_by: Optional[str] = None
    ) -> OrderItemResponse:
        """
        创建订单项
        
        Args:
            request: 创建请求
            created_by: 创建人ID
            
        Returns:
            订单项响应
        """
        method_name = "create_order_item"
        start_time = time.time()
        logger.info(
            f"[Service] {method_name} - 方法调用开始 | "
            f"参数: order_id={request.order_id}, item_number={request.item_number}, "
            f"product_id={request.product_id}, quantity={request.quantity}"
        )
        
        try:
            # 计算订单项金额
            item_amount = self._calculate_item_amount(
                request.quantity,
                request.unit_price,
                request.discount_amount
            )
            
            logger.debug(
                f"[Service] {method_name} - 计算订单项金额 | "
                f"quantity={request.quantity}, unit_price={request.unit_price}, "
                f"discount_amount={request.discount_amount}, item_amount={item_amount}"
            )
            
            # 创建订单项模型
            order_item = OrderItem(
                order_id=request.order_id,
                item_number=request.item_number,
                product_id=request.product_id,
                product_name_zh=request.product_name_zh,
                product_name_id=request.product_name_id,
                product_code=request.product_code,
                service_type_id=request.service_type_id,
                service_type_name_zh=request.service_type_name_zh,
                service_type_name_id=request.service_type_name_id,
                quantity=request.quantity,
                unit=request.unit,
                unit_price=request.unit_price,
                discount_amount=request.discount_amount,
                item_amount=item_amount,
                currency_code=request.currency_code,
                description_zh=request.description_zh,
                description_id=request.description_id,
                requirements=request.requirements,
                expected_start_date=request.expected_start_date,
                expected_completion_date=request.expected_completion_date,
                status=request.status,
            )
            
            # 保存到数据库
            order_item = await self.repository.create(order_item)
            await self.db.commit()
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"结果: order_item_id={order_item.id}, item_amount={item_amount}"
            )
            
            # 转换为响应（默认中文）
            return await self._to_response(order_item, lang="zh")
            
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            await self.db.rollback()
            raise
    
    async def get_order_item_by_id(
        self,
        item_id: str,
        lang: str = "zh"
    ) -> Optional[OrderItemResponse]:
        """
        根据ID查询订单项
        
        Args:
            item_id: 订单项ID
            lang: 语言代码（zh/id）
            
        Returns:
            订单项响应或None
        """
        method_name = "get_order_item_by_id"
        start_time = time.time()
        logger.info(
            f"[Service] {method_name} - 方法调用开始 | "
            f"参数: item_id={item_id}, lang={lang}"
        )
        
        try:
            order_item = await self.repository.get_by_id(item_id)
            
            if order_item is None:
                elapsed_time = (time.time() - start_time) * 1000
                logger.warning(
                    f"[Service] {method_name} - 订单项不存在 | "
                    f"耗时: {elapsed_time:.2f}ms | "
                    f"item_id={item_id}"
                )
                return None
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"结果: order_id={order_item.order_id}, item_number={order_item.item_number}"
            )
            
            return await self._to_response(order_item, lang)
            
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise
    
    async def update_order_item(
        self,
        item_id: str,
        request: OrderItemUpdateRequest,
        updated_by: Optional[str] = None
    ) -> Optional[OrderItemResponse]:
        """
        更新订单项
        
        Args:
            item_id: 订单项ID
            request: 更新请求
            updated_by: 更新人ID
            
        Returns:
            更新后的订单项响应或None
        """
        method_name = "update_order_item"
        start_time = time.time()
        logger.info(
            f"[Service] {method_name} - 方法调用开始 | "
            f"参数: item_id={item_id}, updated_by={updated_by}"
        )
        
        try:
            order_item = await self.repository.get_by_id(item_id)
            
            if order_item is None:
                elapsed_time = (time.time() - start_time) * 1000
                logger.warning(
                    f"[Service] {method_name} - 订单项不存在 | "
                    f"耗时: {elapsed_time:.2f}ms | "
                    f"item_id={item_id}"
                )
                return None
            
            # 更新字段
            update_fields = []
            if request.product_id is not None:
                order_item.product_id = request.product_id
                update_fields.append("product_id")
            if request.product_name_zh is not None:
                order_item.product_name_zh = request.product_name_zh
                update_fields.append("product_name_zh")
            if request.product_name_id is not None:
                order_item.product_name_id = request.product_name_id
                update_fields.append("product_name_id")
            if request.quantity is not None:
                order_item.quantity = request.quantity
                update_fields.append("quantity")
            if request.unit_price is not None:
                order_item.unit_price = request.unit_price
                update_fields.append("unit_price")
            if request.discount_amount is not None:
                order_item.discount_amount = request.discount_amount
                update_fields.append("discount_amount")
            if request.status is not None:
                order_item.status = request.status
                update_fields.append("status")
            
            # 重新计算订单项金额
            if request.quantity is not None or request.unit_price is not None or request.discount_amount is not None:
                order_item.item_amount = self._calculate_item_amount(
                    order_item.quantity,
                    order_item.unit_price,
                    order_item.discount_amount
                )
                update_fields.append("item_amount")
                logger.debug(
                    f"[Service] {method_name} - 重新计算订单项金额 | "
                    f"item_amount={order_item.item_amount}"
                )
            
            # 保存更新
            order_item = await self.repository.update(order_item)
            await self.db.commit()
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"更新字段: {', '.join(update_fields)}"
            )
            
            return await self._to_response(order_item, lang="zh")
            
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            await self.db.rollback()
            raise
    
    async def delete_order_item(self, item_id: str) -> bool:
        """
        删除订单项
        
        Args:
            item_id: 订单项ID
            
        Returns:
            是否删除成功
        """
        method_name = "delete_order_item"
        start_time = time.time()
        logger.info(
            f"[Service] {method_name} - 方法调用开始 | "
            f"参数: item_id={item_id}"
        )
        
        try:
            order_item = await self.repository.get_by_id(item_id)
            
            if order_item is None:
                elapsed_time = (time.time() - start_time) * 1000
                logger.warning(
                    f"[Service] {method_name} - 订单项不存在 | "
                    f"耗时: {elapsed_time:.2f}ms | "
                    f"item_id={item_id}"
                )
                return False
            
            await self.repository.delete(order_item)
            await self.db.commit()
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"已删除订单项: item_id={item_id}, order_id={order_item.order_id}"
            )
            
            return True
            
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            await self.db.rollback()
            raise
    
    async def list_order_items_by_order(
        self,
        order_id: str,
        page: int = 1,
        size: int = 100,
        lang: str = "zh"
    ) -> OrderItemListResponse:
        """
        根据订单ID查询订单项列表
        
        Args:
            order_id: 订单ID
            page: 页码
            size: 每页数量
            lang: 语言代码（zh/id）
            
        Returns:
            订单项列表响应
        """
        method_name = "list_order_items_by_order"
        start_time = time.time()
        logger.info(
            f"[Service] {method_name} - 方法调用开始 | "
            f"参数: order_id={order_id}, page={page}, size={size}, lang={lang}"
        )
        
        try:
            items, total = await self.repository.get_by_order_id(order_id, page, size)
            
            # 转换为响应列表
            item_responses = []
            for item in items:
                item_responses.append(await self._to_response(item, lang))
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"结果: total={total}, items_count={len(item_responses)}"
            )
            
            return OrderItemListResponse(items=item_responses, total=total)
            
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise
    
    async def calculate_order_total(self, order_id: str) -> Decimal:
        """
        计算订单总金额（从订单项汇总）
        
        Args:
            order_id: 订单ID
            
        Returns:
            订单总金额
        """
        method_name = "calculate_order_total"
        start_time = time.time()
        logger.info(
            f"[Service] {method_name} - 方法调用开始 | "
            f"参数: order_id={order_id}"
        )
        
        try:
            total = await self.repository.calculate_order_total(order_id)
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"结果: order_id={order_id}, total_amount={total}"
            )
            
            return Decimal(total)
            
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise
    
    async def _to_response(
        self,
        order_item: OrderItem,
        lang: str = "zh"
    ) -> OrderItemResponse:
        """
        将订单项模型转换为响应（根据语言返回对应字段）
        
        Args:
            order_item: 订单项模型
            lang: 语言代码（zh/id）
            
        Returns:
            订单项响应
        """
        return OrderItemResponse(
            id=order_item.id,
            order_id=order_item.order_id,
            item_number=order_item.item_number,
            product_id=order_item.product_id,
            product_name=get_localized_field(
                order_item.product_name_zh,
                order_item.product_name_id,
                lang
            ),
            product_code=order_item.product_code,
            service_type_id=order_item.service_type_id,
            service_type_name=get_localized_field(
                order_item.service_type_name_zh,
                order_item.service_type_name_id,
                lang
            ),
            quantity=order_item.quantity,
            unit=order_item.unit,
            unit_price=order_item.unit_price,
            discount_amount=order_item.discount_amount,
            item_amount=order_item.item_amount,
            currency_code=order_item.currency_code,
            description=get_localized_field(
                order_item.description_zh,
                order_item.description_id,
                lang
            ),
            requirements=order_item.requirements,
            expected_start_date=order_item.expected_start_date,
            expected_completion_date=order_item.expected_completion_date,
            status=order_item.status,
            created_at=order_item.created_at.isoformat() if order_item.created_at else "",
            updated_at=order_item.updated_at.isoformat() if order_item.updated_at else "",
        )

