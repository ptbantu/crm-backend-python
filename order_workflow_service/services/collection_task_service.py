"""
催款任务服务
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime

from order_workflow_service.models.collection_task import CollectionTask
from order_workflow_service.repositories.collection_task_repository import CollectionTaskRepository
from order_workflow_service.repositories.order_repository import OrderRepository
from order_workflow_service.schemas.collection_task import (
    CollectionTaskCreateRequest,
    CollectionTaskUpdateRequest,
    CollectionTaskResponse,
    CollectionTaskListResponse,
)
from order_workflow_service.services.notification_service import NotificationService
from common.utils.logger import get_logger
from common.exceptions import BusinessException
import uuid

logger = get_logger(__name__)


class CollectionTaskService:
    """催款任务服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = CollectionTaskRepository(db)
        self.order_repository = OrderRepository(db)
        self.notification_service = NotificationService(db)
    
    async def create_collection_task(
        self,
        order_id: str,
        request: CollectionTaskCreateRequest,
        created_by: Optional[str] = None,
    ) -> CollectionTaskResponse:
        """创建催款任务"""
        # 验证订单存在
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise BusinessException(detail="订单不存在", status_code=404)
        
        task = CollectionTask(
            id=str(uuid.uuid4()),
            order_id=order_id,
            payment_stage_id=request.payment_stage_id,
            task_type=request.task_type,
            status="pending",
            due_date=request.due_date,
            notes=request.notes,
            assigned_to_user_id=request.assigned_to_user_id or order.sales_user_id,
            created_by=created_by,
        )
        
        await self.repository.create(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        # 发送通知
        if task.assigned_to_user_id:
            await self.notification_service.create_notification(
                user_id=task.assigned_to_user_id,
                notification_type="collection_task",
                title="新的催款任务",
                content=f"订单 {order.order_number} 有新的催款任务需要处理",
                resource_type="collection_task",
                resource_id=task.id,
            )
        
        return CollectionTaskResponse.model_validate(task)
    
    async def get_collection_task_list(
        self,
        assigned_to_user_id: str,
        page: int = 1,
        size: int = 20,
        status: Optional[str] = None,
    ) -> CollectionTaskListResponse:
        """获取催款任务列表"""
        tasks, total = await self.repository.get_by_assigned_user(
            assigned_to_user_id=assigned_to_user_id,
            page=page,
            size=size,
            status=status,
        )
        
        return CollectionTaskListResponse(
            items=[CollectionTaskResponse.model_validate(task) for task in tasks],
            total=total,
            page=page,
            size=size,
        )
    
    async def complete_collection_task(
        self,
        task_id: str,
        user_id: str,
    ) -> CollectionTaskResponse:
        """完成催款任务"""
        task = await self.repository.get_by_id(task_id)
        if not task:
            raise BusinessException(detail="催款任务不存在", status_code=404)
        
        if task.assigned_to_user_id != user_id:
            raise BusinessException(detail="无权操作该催款任务", status_code=403)
        
        task.status = "completed"
        await self.db.commit()
        await self.db.refresh(task)
        
        return CollectionTaskResponse.model_validate(task)
    
    async def generate_auto_collection_tasks(self) -> int:
        """
        自动生成催款任务（定时任务调用）
        基于payment_stages的due_date和payment_trigger
        """
        from sqlalchemy import select, and_, or_, text
        
        today = date.today()
        
        # 直接查询payment_stages表（因为PaymentStage模型可能不在当前服务中）
        query = text("""
            SELECT id, order_id, stage_name, due_date, payment_trigger, trigger_date, status
            FROM payment_stages
            WHERE status IN ('pending', 'overdue')
            AND (
                (payment_trigger = 'date' AND trigger_date <= :today)
                OR due_date <= :today
            )
        """)
        
        result = await self.db.execute(query, {"today": today})
        payment_stages = result.fetchall()
        
        created_count = 0
        for stage_row in payment_stages:
            stage_id = stage_row[0]
            order_id = stage_row[1]
            stage_name = stage_row[2]
            stage_due_date = stage_row[3]
            
            # 检查是否已有催款任务
            existing_tasks = await self.repository.get_by_order_id(order_id)
            if any(t.payment_stage_id == stage_id for t in existing_tasks):
                continue
            
            # 获取订单信息
            order = await self.order_repository.get_by_id(order_id)
            if not order:
                continue
            
            # 创建催款任务
            task = CollectionTask(
                id=str(uuid.uuid4()),
                order_id=order_id,
                payment_stage_id=stage_id,
                task_type="auto",
                status="pending",
                due_date=stage_due_date or today,
                assigned_to_user_id=order.sales_user_id,
            )
            
            await self.repository.create(task)
            created_count += 1
            
            # 发送通知
            if task.assigned_to_user_id:
                await self.notification_service.create_notification(
                    user_id=task.assigned_to_user_id,
                    notification_type="collection_task",
                    title="新的催款任务（自动生成）",
                    content=f"订单 {order.order_number} 的付款阶段 {stage_name} 已到期，需要催款",
                    resource_type="collection_task",
                    resource_id=task.id,
                )
        
        await self.db.commit()
        return created_count

