"""
收款服务
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
from decimal import Decimal
import uuid

from common.models.payment import Payment, PaymentVoucher, CollectionTodo
from common.models.payment import PaymentModeEnum, PaymentStatusEnum
from common.models.opportunity import Opportunity
from common.models.contract import Contract
from common.models.contract_entity import ContractEntity
from foundation_service.repositories.payment_repository import (
    PaymentRepository,
    PaymentVoucherRepository,
    CollectionTodoRepository,
)
from foundation_service.repositories.opportunity_repository import OpportunityRepository
from foundation_service.repositories.contract_repository import ContractRepository
from foundation_service.repositories.contract_entity_repository import ContractEntityRepository
from foundation_service.repositories.execution_order_repository import ExecutionOrderRepository
from foundation_service.schemas.payment import (
    PaymentCreateRequest,
    PaymentUpdateRequest,
    PaymentResponse,
    PaymentListResponse,
    PaymentReviewRequest,
    PaymentVoucherResponse,
    CollectionTodoRequest,
    CollectionTodoResponse,
    CollectionTodoListResponse,
)
from common.utils.logger import get_logger
from common.utils.id_generator import generate_id
from common.exceptions import BusinessException

logger = get_logger(__name__)


class PaymentService:
    """收款服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_repo = PaymentRepository(db)
        self.voucher_repo = PaymentVoucherRepository(db)
        self.todo_repo = CollectionTodoRepository(db)
        self.opportunity_repo = OpportunityRepository(db)
        self.contract_repo = ContractRepository(db)
        self.contract_entity_repo = ContractEntityRepository(db)
        self.execution_order_repo = ExecutionOrderRepository(db)
    
    async def create_payment(
        self,
        request: PaymentCreateRequest,
        created_by: Optional[str] = None
    ) -> PaymentResponse:
        """创建收款记录"""
        # 验证商机是否存在
        opportunity = await self.opportunity_repo.get_by_id(request.opportunity_id)
        if not opportunity:
            raise BusinessException(detail="商机不存在", status_code=404)
        
        # 验证签约主体是否存在
        entity = await self.contract_entity_repo.get_by_id(request.entity_id)
        if not entity:
            raise BusinessException(detail="签约主体不存在", status_code=404)
        
        # 如果关联了合同，验证合同和主体的税点一致性
        if request.contract_id:
            contract = await self.contract_repo.get_by_id(request.contract_id)
            if not contract:
                raise BusinessException(detail="合同不存在", status_code=404)
            if contract.entity_id != request.entity_id:
                raise BusinessException(detail="签约主体与合同不一致", status_code=400)
        
        try:
            # 生成收款编号
            payment_no = await generate_id(self.db, "Payment")
            
            # 计算税额
            tax_rate = entity.tax_rate or Decimal("0")
            tax_amount = request.amount * tax_rate / (1 + tax_rate)
            
            # 创建收款记录
            payment = Payment(
                id=str(uuid.uuid4()),
                opportunity_id=request.opportunity_id,
                contract_id=request.contract_id,
                execution_order_id=request.execution_order_id,
                payment_no=payment_no,
                entity_id=request.entity_id,
                amount=request.amount,
                tax_amount=tax_amount,
                currency=request.currency,
                payment_method=request.payment_method,
                payment_mode=PaymentModeEnum(request.payment_mode),
                status=PaymentStatusEnum.PENDING_REVIEW,
                received_at=request.received_at,
                is_final_payment=request.is_final_payment,
                created_by=created_by,
            )
            await self.db.add(payment)
            await self.db.flush()
            
            # 创建收款凭证
            for voucher_req in request.vouchers:
                voucher = PaymentVoucher(
                    id=str(uuid.uuid4()),
                    payment_id=payment.id,
                    file_name=voucher_req.file_name,
                    file_url=voucher_req.file_url,
                    file_size_kb=voucher_req.file_size_kb,
                    is_primary=voucher_req.is_primary,
                    uploaded_by=created_by,
                )
                await self.db.add(voucher)
            
            # 创建待办事项（财务核对）
            if not request.is_final_payment:
                todo = CollectionTodo(
                    id=str(uuid.uuid4()),
                    opportunity_id=request.opportunity_id,
                    payment_id=payment.id,
                    todo_type="finance_review",
                    title=f"核对收款：{payment_no}",
                    description=f"收款金额：{request.amount} {request.currency}",
                    assigned_to=None,  # 可以分配给Lulu
                )
                await self.db.add(todo)
            
            await self.db.commit()
            await self.db.refresh(payment)
            
            return await self._to_response(payment)
        except BusinessException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"创建收款记录失败: {e}", exc_info=True)
            raise BusinessException(detail=f"创建收款记录失败: {str(e)}")
    
    async def get_payment(
        self,
        payment_id: str
    ) -> PaymentResponse:
        """获取收款记录详情"""
        payment = await self.payment_repo.get_by_id(payment_id)
        if not payment:
            raise BusinessException(detail="收款记录不存在", status_code=404)
        
        return await self._to_response(payment)
    
    async def get_payment_list(
        self,
        opportunity_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> PaymentListResponse:
        """获取收款列表"""
        if status:
            payments, total = await self.payment_repo.get_by_status(
                PaymentStatusEnum(status),
                page,
                size
            )
        elif opportunity_id:
            payments = await self.payment_repo.get_by_opportunity_id(opportunity_id)
            total = len(payments)
        else:
            raise BusinessException(detail="必须提供opportunity_id或status参数", status_code=400)
        
        records = [await self._to_response(p) for p in payments]
        
        return PaymentListResponse(
            records=records,
            total=total,
            size=size,
            current=page,
            pages=(total + size - 1) // size if size > 0 else 0,
        )
    
    async def review_payment(
        self,
        request: PaymentReviewRequest,
        reviewer_id: str
    ) -> PaymentResponse:
        """财务核对收款"""
        payment = await self.payment_repo.get_by_id(request.payment_id)
        if not payment:
            raise BusinessException(detail="收款记录不存在", status_code=404)
        
        if payment.status != PaymentStatusEnum.PENDING_REVIEW:
            raise BusinessException(detail="只能核对待核对的收款记录", status_code=400)
        
        try:
            payment.status = PaymentStatusEnum(request.status)
            payment.reviewed_by = reviewer_id
            payment.reviewed_at = datetime.now()
            payment.review_notes = request.review_notes
            
            # 如果确认通过，更新商机的收款状态
            if payment.status == PaymentStatusEnum.CONFIRMED:
                await self._update_opportunity_collection_status(payment.opportunity_id)
                
                # 如果是尾款，检查交付验证
                if payment.is_final_payment:
                    await self._verify_delivery(payment.opportunity_id, payment.id)
            
            await self.db.commit()
            await self.db.refresh(payment)
            
            return await self._to_response(payment)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"核对收款失败: {e}", exc_info=True)
            raise BusinessException(detail=f"核对收款失败: {str(e)}")
    
    async def _update_opportunity_collection_status(self, opportunity_id: str) -> None:
        """更新商机的收款状态"""
        opportunity = await self.opportunity_repo.get_by_id(opportunity_id)
        if not opportunity:
            return
        
        # 计算已收总金额
        total_received = await self.payment_repo.calculate_total_received(opportunity_id)
        
        # 获取合同金额
        contract_amount = Decimal("0")
        if opportunity.primary_contract_id:
            contract = await self.contract_repo.get_by_id(opportunity.primary_contract_id)
            if contract:
                contract_amount = contract.total_amount_with_tax
        
        opportunity.total_received_amount = total_received
        
        # 更新收款状态
        if total_received == 0:
            opportunity.collection_status = "not_started"
        elif total_received >= contract_amount:
            opportunity.collection_status = "full"
        else:
            opportunity.collection_status = "partial"
    
    async def _verify_delivery(
        self,
        opportunity_id: str,
        payment_id: str
    ) -> None:
        """验证交付（尾款时检查）"""
        from common.models.execution_order import ExecutionOrderStatusEnum
        # 检查所有执行订单是否完成
        execution_orders = await self.execution_order_repo.get_by_opportunity_id(opportunity_id)
        
        all_completed = all(
            order.status == ExecutionOrderStatusEnum.COMPLETED
            for order in execution_orders
        )
        
        if all_completed:
            payment = await self.payment_repo.get_by_id(payment_id)
            if payment:
                payment.delivery_verified = True
                
                # 创建待办事项：释放新订单
                todo = CollectionTodo(
                    id=str(uuid.uuid4()),
                    opportunity_id=opportunity_id,
                    payment_id=payment_id,
                    todo_type="release_new_order",
                    title="释放新订单",
                    description="所有交付已完成，可以释放新订单",
                )
                await self.db.add(todo)
    
    async def upload_voucher(
        self,
        payment_id: str,
        file_name: str,
        file_url: str,
        file_size_kb: Optional[int] = None,
        is_primary: bool = False,
        uploaded_by: Optional[str] = None
    ) -> PaymentVoucherResponse:
        """上传收款凭证"""
        payment = await self.payment_repo.get_by_id(payment_id)
        if not payment:
            raise BusinessException(detail="收款记录不存在", status_code=404)
        
        try:
            # 如果设置为主要凭证，将其他凭证设为非主要
            if is_primary:
                primary_voucher = await self.voucher_repo.get_primary_voucher(payment_id)
                if primary_voucher:
                    primary_voucher.is_primary = False
            
            voucher = PaymentVoucher(
                id=str(uuid.uuid4()),
                payment_id=payment_id,
                file_name=file_name,
                file_url=file_url,
                file_size_kb=file_size_kb,
                is_primary=is_primary,
                uploaded_by=uploaded_by,
            )
            await self.db.add(voucher)
            await self.db.commit()
            await self.db.refresh(voucher)
            
            return PaymentVoucherResponse(
                id=voucher.id,
                payment_id=voucher.payment_id,
                file_name=voucher.file_name,
                file_url=voucher.file_url,
                file_size_kb=voucher.file_size_kb,
                is_primary=voucher.is_primary,
                uploaded_by=voucher.uploaded_by,
                uploaded_at=voucher.uploaded_at,
            )
        except Exception as e:
            await self.db.rollback()
            logger.error(f"上传收款凭证失败: {e}", exc_info=True)
            raise BusinessException(detail=f"上传收款凭证失败: {str(e)}")
    
    async def create_collection_todo(
        self,
        request: CollectionTodoRequest
    ) -> CollectionTodoResponse:
        """创建收款待办事项"""
        try:
            todo = CollectionTodo(
                id=str(uuid.uuid4()),
                opportunity_id=request.opportunity_id,
                payment_id=request.payment_id,
                todo_type=request.todo_type,
                title=request.title,
                description=request.description,
                assigned_to=request.assigned_to,
                due_date=request.due_date,
                status="pending",
            )
            await self.db.add(todo)
            await self.db.commit()
            await self.db.refresh(todo)
            
            return await self._todo_to_response(todo)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"创建收款待办事项失败: {e}", exc_info=True)
            raise BusinessException(detail=f"创建收款待办事项失败: {str(e)}")
    
    async def get_collection_todos(
        self,
        opportunity_id: Optional[str] = None,
        assigned_to: Optional[str] = None,
        status: Optional[str] = None
    ) -> CollectionTodoListResponse:
        """获取收款待办事项列表"""
        if opportunity_id:
            todos = await self.todo_repo.get_by_opportunity_id(opportunity_id, status)
        elif assigned_to:
            todos = await self.todo_repo.get_by_assigned_to(assigned_to, status)
        else:
            raise BusinessException(detail="必须提供opportunity_id或assigned_to参数", status_code=400)
        
        records = [await self._todo_to_response(todo) for todo in todos]
        
        return CollectionTodoListResponse(
            records=records,
            total=len(records)
        )
    
    async def complete_todo(
        self,
        todo_id: str,
        completed_by: str
    ) -> CollectionTodoResponse:
        """完成待办事项"""
        todo = await self.todo_repo.get_by_id(todo_id)
        if not todo:
            raise BusinessException(detail="待办事项不存在", status_code=404)
        
        try:
            todo.status = "completed"
            todo.completed_by = completed_by
            todo.completed_at = datetime.now()
            
            await self.db.commit()
            await self.db.refresh(todo)
            
            return await self._todo_to_response(todo)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"完成待办事项失败: {e}", exc_info=True)
            raise BusinessException(detail=f"完成待办事项失败: {str(e)}")
    
    async def _to_response(self, payment: Payment) -> PaymentResponse:
        """转换为响应对象"""
        # 加载关联数据
        vouchers = await self.voucher_repo.get_by_payment_id(payment.id)
        entity = await self.contract_entity_repo.get_by_id(payment.entity_id)
        
        return PaymentResponse(
            id=payment.id,
            payment_no=payment.payment_no,
            opportunity_id=payment.opportunity_id,
            contract_id=payment.contract_id,
            execution_order_id=payment.execution_order_id,
            entity_id=payment.entity_id,
            entity_name=entity.entity_name if entity else None,
            amount=payment.amount,
            tax_amount=payment.tax_amount,
            currency=payment.currency,
            payment_method=payment.payment_method,
            payment_mode=payment.payment_mode.value if payment.payment_mode else None,
            status=payment.status.value if payment.status else None,
            reviewed_by=payment.reviewed_by,
            reviewed_at=payment.reviewed_at,
            review_notes=payment.review_notes,
            received_at=payment.received_at,
            is_final_payment=payment.is_final_payment,
            delivery_verified=payment.delivery_verified,
            vouchers=[
                PaymentVoucherResponse(
                    id=v.id,
                    payment_id=v.payment_id,
                    file_name=v.file_name,
                    file_url=v.file_url,
                    file_size_kb=v.file_size_kb,
                    is_primary=v.is_primary,
                    uploaded_by=v.uploaded_by,
                    uploaded_at=v.uploaded_at,
                )
                for v in vouchers
            ],
            created_at=payment.created_at,
            updated_at=payment.updated_at,
            created_by=payment.created_by,
        )
    
    async def _todo_to_response(self, todo: CollectionTodo) -> CollectionTodoResponse:
        """转换为待办事项响应对象"""
        return CollectionTodoResponse(
            id=todo.id,
            opportunity_id=todo.opportunity_id,
            payment_id=todo.payment_id,
            todo_type=todo.todo_type,
            title=todo.title,
            description=todo.description,
            assigned_to=todo.assigned_to,
            due_date=todo.due_date,
            status=todo.status,
            completed_at=todo.completed_at,
            completed_by=todo.completed_by,
            notification_sent=todo.notification_sent,
            created_at=todo.created_at,
        )
