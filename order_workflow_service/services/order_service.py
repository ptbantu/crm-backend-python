"""
订单服务
"""
import time
from typing import Optional, List
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from common.models import Order
from order_workflow_service.repositories.order_repository import OrderRepository
from order_workflow_service.repositories.order_item_repository import OrderItemRepository
from order_workflow_service.schemas.order import (
    OrderCreateRequest,
    OrderUpdateRequest,
    OrderResponse,
    OrderListResponse,
)
from order_workflow_service.services.order_item_service import OrderItemService
from common.utils.logger import get_logger
from common.exceptions import BusinessException
import uuid

logger = get_logger(__name__)


class OrderService:
    """订单服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = OrderRepository(db)
        self.order_item_repository = OrderItemRepository(db)
    
    def _generate_order_number(self) -> str:
        """生成订单号"""
        # 格式: ORD-YYYYMMDD-XXXXXX
        from datetime import datetime
        date_str = datetime.now().strftime("%Y%m%d")
        random_str = str(uuid.uuid4())[:6].upper()
        return f"ORD-{date_str}-{random_str}"
    
    async def _calculate_order_total(self, order_id: str) -> Decimal:
        """计算订单总金额（从订单项汇总）"""
        total = await self.order_item_repository.calculate_order_total(order_id)
        return Decimal(str(total))
    
    async def create_order(
        self,
        request: OrderCreateRequest,
        created_by: Optional[str] = None
    ) -> OrderResponse:
        """
        创建订单
        
        Args:
            request: 创建请求
            created_by: 创建人ID
            
        Returns:
            订单响应
        """
        method_name = "create_order"
        start_time = time.time()
        logger.info(
            f"[Service] {method_name} - 方法调用开始 | "
            f"参数: customer_id={request.customer_id}, title={request.title}, "
            f"order_items_count={len(request.order_items)}"
        )
        
        try:
            # 生成订单号
            order_number = self._generate_order_number()
            
            # 创建订单
            order = Order(
                id=str(uuid.uuid4()),
                order_number=order_number,
                title=request.title,
                customer_id=request.customer_id,
                service_record_id=request.service_record_id,
                sales_user_id=request.sales_user_id,
                entry_city=request.entry_city,
                passport_id=request.passport_id,
                processor=request.processor,
                currency_code=request.currency_code,
                discount_amount=request.discount_amount,
                exchange_rate=request.exchange_rate,
                expected_start_date=request.expected_start_date,
                expected_completion_date=request.expected_completion_date,
                customer_notes=request.customer_notes,
                internal_notes=request.internal_notes,
                requirements=request.requirements,
                status_code="submitted",
                created_by=created_by,
            )
            
            self.db.add(order)
            await self.db.flush()
            
            # 创建订单项
            if request.order_items:
                order_item_service = OrderItemService(self.db)
                for idx, item_data in enumerate(request.order_items, start=1):
                    from order_workflow_service.schemas.order_item import OrderItemCreateRequest
                    item_request = OrderItemCreateRequest(
                        order_id=order.id,
                        item_number=idx,
                        **item_data
                    )
                    await order_item_service.create_order_item(item_request, created_by)
            
            # 计算订单总金额
            total_amount = await self._calculate_order_total(order.id)
            final_amount = total_amount - request.discount_amount
            
            order.total_amount = total_amount
            order.final_amount = final_amount
            await self.db.commit()
            await self.db.refresh(order)
            
            # 构建响应
            response = await self._build_order_response(order)
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"结果: order_id={order.id}, order_number={order.order_number}, "
                f"total_amount={total_amount}, final_amount={final_amount}"
            )
            
            return response
            
        except Exception as e:
            await self.db.rollback()
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise
    
    async def get_order_by_id(
        self,
        order_id: str
    ) -> Optional[OrderResponse]:
        """
        根据ID查询订单
        
        Args:
            order_id: 订单ID
            
        Returns:
            订单响应或 None
        """
        method_name = "get_order_by_id"
        start_time = time.time()
        logger.info(f"[Service] {method_name} - 方法调用开始 | 参数: order_id={order_id}")
        
        try:
            order = await self.repository.get_by_id(order_id)
            
            if order is None:
                elapsed_time = (time.time() - start_time) * 1000
                logger.warning(
                    f"[Service] {method_name} - 订单不存在 | "
                    f"耗时: {elapsed_time:.2f}ms | "
                    f"order_id={order_id}"
                )
                return None
            
            response = await self._build_order_response(order)
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"结果: order_id={order.id}, order_number={order.order_number}"
            )
            
            return response
            
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise
    
    async def update_order(
        self,
        order_id: str,
        request: OrderUpdateRequest,
        updated_by: Optional[str] = None
    ) -> Optional[OrderResponse]:
        """
        更新订单
        
        Args:
            order_id: 订单ID
            request: 更新请求
            updated_by: 更新人ID
            
        Returns:
            订单响应或 None
        """
        method_name = "update_order"
        start_time = time.time()
        logger.info(
            f"[Service] {method_name} - 方法调用开始 | "
            f"参数: order_id={order_id}, "
            f"fields={list(request.model_dump(exclude_unset=True).keys())}"
        )
        
        try:
            order = await self.repository.get_by_id(order_id)
            
            if order is None:
                elapsed_time = (time.time() - start_time) * 1000
                logger.warning(
                    f"[Service] {method_name} - 订单不存在 | "
                    f"耗时: {elapsed_time:.2f}ms | "
                    f"order_id={order_id}"
                )
                return None
            
            # 更新字段
            update_data = request.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(order, key, value)
            
            # 如果更新了订单项，重新计算总金额
            if "discount_amount" in update_data:
                total_amount = await self._calculate_order_total(order_id)
                final_amount = total_amount - order.discount_amount
                order.total_amount = total_amount
                order.final_amount = final_amount
            
            order.updated_by = updated_by
            await self.db.commit()
            await self.db.refresh(order)
            
            response = await self._build_order_response(order)
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"结果: order_id={order.id}, order_number={order.order_number}"
            )
            
            return response
            
        except Exception as e:
            await self.db.rollback()
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise
    
    async def delete_order(
        self,
        order_id: str
    ) -> bool:
        """
        删除订单
        
        Args:
            order_id: 订单ID
            
        Returns:
            是否删除成功
        """
        method_name = "delete_order"
        start_time = time.time()
        logger.info(f"[Service] {method_name} - 方法调用开始 | 参数: order_id={order_id}")
        
        try:
            success = await self.repository.delete(order_id)
            
            if success:
                await self.db.commit()
                elapsed_time = (time.time() - start_time) * 1000
                logger.info(
                    f"[Service] {method_name} - 方法调用成功 | "
                    f"耗时: {elapsed_time:.2f}ms | "
                    f"结果: order_id={order_id} 已删除"
                )
            else:
                elapsed_time = (time.time() - start_time) * 1000
                logger.warning(
                    f"[Service] {method_name} - 订单不存在 | "
                    f"耗时: {elapsed_time:.2f}ms | "
                    f"order_id={order_id}"
                )
            
            return success
            
        except Exception as e:
            await self.db.rollback()
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise
    
    async def list_orders(
        self,
        page: int = 1,
        size: int = 20,
        customer_id: Optional[str] = None,
        sales_user_id: Optional[str] = None,
        status_code: Optional[str] = None,
        order_number: Optional[str] = None,
        title: Optional[str] = None,
    ) -> OrderListResponse:
        """
        查询订单列表
        
        Args:
            page: 页码
            size: 每页数量
            customer_id: 客户ID
            sales_user_id: 销售用户ID
            status_code: 状态代码
            order_number: 订单号（模糊查询）
            title: 订单标题（模糊查询）
            
        Returns:
            订单列表响应
        """
        method_name = "list_orders"
        start_time = time.time()
        logger.info(
            f"[Service] {method_name} - 方法调用开始 | "
            f"参数: page={page}, size={size}, customer_id={customer_id}, "
            f"status_code={status_code}"
        )
        
        try:
            orders, total = await self.repository.list_orders(
                page=page,
                size=size,
                customer_id=customer_id,
                sales_user_id=sales_user_id,
                status_code=status_code,
                order_number=order_number,
                title=title,
            )
            
            # 构建响应列表
            order_responses = []
            for order in orders:
                response = await self._build_order_response(order)
                order_responses.append(response)
            
            result = OrderListResponse(
                orders=order_responses,
                total=total,
                page=page,
                page_size=size
            )
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"结果: total={total}, page={page}, size={size}"
            )
            
            return result
            
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise
    
    async def _build_order_response(self, order: Order) -> OrderResponse:
        """构建订单响应（包含订单项）"""
        # 查询订单项
        order_items, _ = await self.order_item_repository.get_by_order_id(
            order.id, page=1, size=1000
        )
        
        # 构建订单项响应
        from order_workflow_service.services.order_item_service import OrderItemService
        order_item_service = OrderItemService(self.db)
        order_item_responses = []
        for item in order_items:
            item_response = await order_item_service._to_response(item, "zh")
            order_item_responses.append(item_response)
        
        # 查询关联信息（使用原生 SQL 查询，避免跨服务依赖）
        customer_name = None
        sales_username = None
        if order.customer_id:
            from sqlalchemy import text
            customer_query = text("SELECT name FROM customers WHERE id = :customer_id")
            customer_result = await self.db.execute(customer_query, {"customer_id": order.customer_id})
            customer_name = customer_result.scalar()
        
        if order.sales_user_id:
            from sqlalchemy import text
            user_query = text("SELECT username FROM users WHERE id = :user_id")
            user_result = await self.db.execute(user_query, {"user_id": order.sales_user_id})
            sales_username = user_result.scalar()
        
        # 状态名称
        status_name = None
        if order.status_code:
            status_mapping = {
                "draft": "草稿",
                "submitted": "已提交",
                "assigned": "已分配",
                "in_progress": "进行中",
                "pending_review": "待审核",
                "completed": "已完成",
                "cancelled": "已取消",
                "on_hold": "暂停",
            }
            status_name = status_mapping.get(order.status_code, order.status_code)
        
        return OrderResponse(
            id=order.id,
            order_number=order.order_number,
            title=order.title,
            customer_id=order.customer_id,
            customer_name=customer_name,
            service_record_id=order.service_record_id,
            workflow_instance_id=order.workflow_instance_id,
            sales_user_id=order.sales_user_id,
            sales_username=sales_username,
            entry_city=order.entry_city,
            passport_id=order.passport_id,
            processor=order.processor,
            total_amount=order.total_amount,
            discount_amount=order.discount_amount,
            final_amount=order.final_amount,
            currency_code=order.currency_code,
            exchange_rate=order.exchange_rate,
            order_items=order_item_responses,
            expected_start_date=order.expected_start_date,
            expected_completion_date=order.expected_completion_date,
            actual_start_date=order.actual_start_date,
            actual_completion_date=order.actual_completion_date,
            status_code=order.status_code,
            status_name=status_name,
            customer_notes=order.customer_notes,
            internal_notes=order.internal_notes,
            requirements=order.requirements,
            created_by=order.created_by,
            updated_by=order.updated_by,
            created_at=order.created_at.isoformat() if order.created_at else "",
            updated_at=order.updated_at.isoformat() if order.updated_at else "",
        )

