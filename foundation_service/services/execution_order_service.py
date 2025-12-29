"""
执行订单服务
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
import uuid

from common.models.execution_order import (
    ExecutionOrder,
    ExecutionOrderItem,
    ExecutionOrderDependency,
    CompanyRegistrationInfo,
)
from common.models.execution_order import (
    ExecutionOrderStatusEnum,
    ExecutionOrderTypeEnum,
    ExecutionOrderItemStatusEnum,
    DependencyStatusEnum,
)
from common.models.opportunity import Opportunity
from common.models.contract import Contract
from foundation_service.repositories.execution_order_repository import (
    ExecutionOrderRepository,
    ExecutionOrderItemRepository,
    ExecutionOrderDependencyRepository,
    CompanyRegistrationInfoRepository,
)
from foundation_service.repositories.opportunity_repository import OpportunityRepository
from foundation_service.repositories.contract_repository import ContractRepository
from foundation_service.repositories.quotation_repository import QuotationRepository
from foundation_service.schemas.execution_order import (
    ExecutionOrderCreateRequest,
    ExecutionOrderResponse,
    ExecutionOrderListResponse,
    ExecutionOrderItemResponse,
    CompanyRegistrationInfoRequest,
    CompanyRegistrationInfoResponse,
)
from common.utils.logger import get_logger
from common.utils.id_generator import generate_id
from common.exceptions import BusinessException

logger = get_logger(__name__)


class ExecutionOrderService:
    """执行订单服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.execution_order_repo = ExecutionOrderRepository(db)
        self.execution_order_item_repo = ExecutionOrderItemRepository(db)
        self.dependency_repo = ExecutionOrderDependencyRepository(db)
        self.company_reg_repo = CompanyRegistrationInfoRepository(db)
        self.opportunity_repo = OpportunityRepository(db)
        self.contract_repo = ContractRepository(db)
        self.quotation_repo = QuotationRepository(db)
    
    async def create_execution_order(
        self,
        request: ExecutionOrderCreateRequest,
        created_by: Optional[str] = None
    ) -> ExecutionOrderResponse:
        """创建执行订单"""
        # 验证商机是否存在
        opportunity = await self.opportunity_repo.get_by_id(request.opportunity_id)
        if not opportunity:
            raise BusinessException(detail="商机不存在", status_code=404)
        
        # 如果关联了合同，验证合同是否存在
        if request.contract_id:
            contract = await self.contract_repo.get_by_id(request.contract_id)
            if not contract:
                raise BusinessException(detail="合同不存在", status_code=404)
        
        try:
            # 生成执行订单编号
            order_no = await generate_id(self.db, "ExecutionOrder")
            
            # 创建执行订单
            execution_order = ExecutionOrder(
                id=str(uuid.uuid4()),
                order_no=order_no,
                opportunity_id=request.opportunity_id,
                contract_id=request.contract_id,
                order_type=ExecutionOrderTypeEnum(request.order_type),
                wechat_group_no=request.wechat_group_no,
                requires_company_registration=request.requires_company_registration,
                status=ExecutionOrderStatusEnum.PENDING,
                planned_start_date=request.planned_start_date,
                planned_end_date=request.planned_end_date,
                assigned_to=request.assigned_to,
                assigned_team=request.assigned_team,
                created_by=created_by,
            )
            await self.db.add(execution_order)
            await self.db.flush()
            
            # 创建执行订单明细
            for item_req in request.items:
                item = ExecutionOrderItem(
                    id=str(uuid.uuid4()),
                    execution_order_id=execution_order.id,
                    quotation_item_id=item_req.quotation_item_id,
                    product_id=item_req.product_id,
                    item_name=item_req.item_name,
                    service_category=item_req.service_category,
                    status=ExecutionOrderItemStatusEnum.PENDING,
                    assigned_to=item_req.assigned_to or request.assigned_to,
                    notes=item_req.notes,
                )
                await self.db.add(item)
            
            # 如果需要公司注册，创建依赖关系
            if request.requires_company_registration:
                company_reg_order = await self.execution_order_repo.get_company_registration_order(
                    request.opportunity_id
                )
                if company_reg_order:
                    execution_order.company_registration_order_id = company_reg_order.id
                    # 创建依赖关系
                    dependency = ExecutionOrderDependency(
                        id=str(uuid.uuid4()),
                        execution_order_id=execution_order.id,
                        prerequisite_order_id=company_reg_order.id,
                        dependency_type="company_registration",
                        status=DependencyStatusEnum.PENDING,
                    )
                    await self.db.add(dependency)
                    execution_order.status = ExecutionOrderStatusEnum.BLOCKED
            
            await self.db.commit()
            await self.db.refresh(execution_order)
            
            return await self._to_response(execution_order)
        except BusinessException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"创建执行订单失败: {e}", exc_info=True)
            raise BusinessException(detail=f"创建执行订单失败: {str(e)}")
    
    async def get_execution_order(
        self,
        execution_order_id: str
    ) -> ExecutionOrderResponse:
        """获取执行订单详情"""
        execution_order = await self.execution_order_repo.get_by_id(execution_order_id)
        if not execution_order:
            raise BusinessException(detail="执行订单不存在", status_code=404)
        
        return await self._to_response(execution_order)
    
    async def get_execution_order_list(
        self,
        opportunity_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> ExecutionOrderListResponse:
        """获取执行订单列表"""
        if status:
            orders, total = await self.execution_order_repo.get_by_status(
                ExecutionOrderStatusEnum(status),
                page,
                size
            )
        elif opportunity_id:
            orders = await self.execution_order_repo.get_by_opportunity_id(opportunity_id)
            total = len(orders)
        else:
            raise BusinessException(detail="必须提供opportunity_id或status参数", status_code=400)
        
        records = [await self._to_response(order) for order in orders]
        
        return ExecutionOrderListResponse(
            records=records,
            total=total,
            size=size,
            current=page,
            pages=(total + size - 1) // size if size > 0 else 0,
        )
    
    async def assign_execution_order(
        self,
        execution_order_id: str,
        assigned_to: str,
        assigned_team: Optional[str] = None
    ) -> ExecutionOrderResponse:
        """分配执行订单"""
        execution_order = await self.execution_order_repo.get_by_id(execution_order_id)
        if not execution_order:
            raise BusinessException(detail="执行订单不存在", status_code=404)
        
        if execution_order.status == ExecutionOrderStatusEnum.BLOCKED:
            # 检查依赖是否满足
            all_satisfied = await self.dependency_repo.check_all_dependencies_satisfied(execution_order_id)
            if not all_satisfied:
                raise BusinessException(detail="依赖关系未满足，无法分配", status_code=400)
        
        try:
            execution_order.assigned_to = assigned_to
            execution_order.assigned_team = assigned_team
            execution_order.assigned_at = datetime.now()
            
            if execution_order.status == ExecutionOrderStatusEnum.PENDING:
                execution_order.status = ExecutionOrderStatusEnum.IN_PROGRESS
                execution_order.actual_start_date = date.today()
            
            await self.db.commit()
            await self.db.refresh(execution_order)
            
            return await self._to_response(execution_order)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"分配执行订单失败: {e}", exc_info=True)
            raise BusinessException(detail=f"分配执行订单失败: {str(e)}")
    
    async def update_execution_status(
        self,
        execution_order_id: str,
        status: str,
        actual_end_date: Optional[date] = None
    ) -> ExecutionOrderResponse:
        """更新执行订单状态"""
        execution_order = await self.execution_order_repo.get_by_id(execution_order_id)
        if not execution_order:
            raise BusinessException(detail="执行订单不存在", status_code=404)
        
        try:
            execution_order.status = ExecutionOrderStatusEnum(status)
            if status == "completed" and actual_end_date:
                execution_order.actual_end_date = actual_end_date
            
            # 如果订单完成，释放依赖的订单
            if status == "completed":
                await self._release_dependent_orders(execution_order_id)
            
            await self.db.commit()
            await self.db.refresh(execution_order)
            
            return await self._to_response(execution_order)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"更新执行订单状态失败: {e}", exc_info=True)
            raise BusinessException(detail=f"更新执行订单状态失败: {str(e)}")
    
    async def _release_dependent_orders(self, execution_order_id: str) -> None:
        """释放依赖的订单"""
        # 查找所有依赖此订单的订单
        dependent_deps = await self.dependency_repo.get_by_prerequisite_order_id(execution_order_id)
        
        for dep in dependent_deps:
            dep.status = DependencyStatusEnum.SATISFIED
            dep.satisfied_at = datetime.now()
            
            # 检查该订单的所有依赖是否都满足
            all_satisfied = await self.dependency_repo.check_all_dependencies_satisfied(
                dep.execution_order_id
            )
            
            if all_satisfied:
                # 如果所有依赖都满足，将订单状态从BLOCKED改为PENDING
                order = await self.execution_order_repo.get_by_id(dep.execution_order_id)
                if order and order.status == ExecutionOrderStatusEnum.BLOCKED:
                    order.status = ExecutionOrderStatusEnum.PENDING
    
    async def create_company_registration_info(
        self,
        request: CompanyRegistrationInfoRequest
    ) -> CompanyRegistrationInfoResponse:
        """创建公司注册信息"""
        # 验证执行订单是否存在
        execution_order = await self.execution_order_repo.get_by_id(request.execution_order_id)
        if not execution_order:
            raise BusinessException(detail="执行订单不存在", status_code=404)
        
        if execution_order.order_type != ExecutionOrderTypeEnum.COMPANY_REGISTRATION:
            raise BusinessException(detail="该订单不是公司注册订单", status_code=400)
        
        # 检查是否已经创建过
        existing = await self.company_reg_repo.get_by_execution_order_id(request.execution_order_id)
        if existing:
            raise BusinessException(detail="公司注册信息已存在", status_code=400)
        
        try:
            company_reg = CompanyRegistrationInfo(
                id=str(uuid.uuid4()),
                execution_order_id=request.execution_order_id,
                company_name=request.company_name,
                nib=request.nib,
                npwp=request.npwp,
                izin_lokasi=request.izin_lokasi,
                akta=request.akta,
                sk=request.sk,
                registration_status=request.registration_status,
                notes=request.notes,
            )
            await self.db.add(company_reg)
            await self.db.flush()
            
            await self.db.commit()
            await self.db.refresh(company_reg)
            
            return await self._company_reg_to_response(company_reg)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"创建公司注册信息失败: {e}", exc_info=True)
            raise BusinessException(detail=f"创建公司注册信息失败: {str(e)}")
    
    async def complete_company_registration(
        self,
        execution_order_id: str
    ) -> CompanyRegistrationInfoResponse:
        """完成公司注册"""
        company_reg = await self.company_reg_repo.get_by_execution_order_id(execution_order_id)
        if not company_reg:
            raise BusinessException(detail="公司注册信息不存在", status_code=404)
        
        try:
            company_reg.registration_status = "completed"
            company_reg.completed_at = datetime.now()
            
            # 更新执行订单状态
            execution_order = await self.execution_order_repo.get_by_id(execution_order_id)
            if execution_order:
                execution_order.status = ExecutionOrderStatusEnum.COMPLETED
                execution_order.actual_end_date = date.today()
            
            # 释放依赖的订单
            await self._release_dependent_orders(execution_order_id)
            
            await self.db.commit()
            await self.db.refresh(company_reg)
            
            return await self._company_reg_to_response(company_reg)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"完成公司注册失败: {e}", exc_info=True)
            raise BusinessException(detail=f"完成公司注册失败: {str(e)}")
    
    async def check_dependencies(
        self,
        execution_order_id: str
    ) -> dict:
        """检查依赖关系"""
        dependencies = await self.dependency_repo.get_by_execution_order_id(execution_order_id)
        pending_deps = await self.dependency_repo.get_pending_dependencies(execution_order_id)
        all_satisfied = await self.dependency_repo.check_all_dependencies_satisfied(execution_order_id)
        
        return {
            "execution_order_id": execution_order_id,
            "total_dependencies": len(dependencies),
            "pending_dependencies": len(pending_deps),
            "all_satisfied": all_satisfied,
            "dependencies": [
                {
                    "id": dep.id,
                    "prerequisite_order_id": dep.prerequisite_order_id,
                    "dependency_type": dep.dependency_type.value if dep.dependency_type else None,
                    "status": dep.status.value if dep.status else None,
                    "satisfied_at": dep.satisfied_at,
                }
                for dep in dependencies
            ],
        }
    
    async def _to_response(self, execution_order: ExecutionOrder) -> ExecutionOrderResponse:
        """转换为响应对象"""
        # 加载关联数据
        items = await self.execution_order_item_repo.get_by_execution_order_id(execution_order.id)
        
        return ExecutionOrderResponse(
            id=execution_order.id,
            order_no=execution_order.order_no,
            opportunity_id=execution_order.opportunity_id,
            contract_id=execution_order.contract_id,
            parent_order_id=execution_order.parent_order_id,
            order_type=execution_order.order_type.value if execution_order.order_type else None,
            wechat_group_no=execution_order.wechat_group_no,
            requires_company_registration=execution_order.requires_company_registration,
            company_registration_order_id=execution_order.company_registration_order_id,
            status=execution_order.status.value if execution_order.status else None,
            planned_start_date=execution_order.planned_start_date,
            planned_end_date=execution_order.planned_end_date,
            actual_start_date=execution_order.actual_start_date,
            actual_end_date=execution_order.actual_end_date,
            assigned_to=execution_order.assigned_to,
            assigned_team=execution_order.assigned_team,
            assigned_at=execution_order.assigned_at,
            items=[
                ExecutionOrderItemResponse(
                    id=item.id,
                    execution_order_id=item.execution_order_id,
                    quotation_item_id=item.quotation_item_id,
                    product_id=item.product_id,
                    item_name=item.item_name,
                    service_category=item.service_category,
                    status=item.status.value if item.status else None,
                    assigned_to=item.assigned_to,
                    notes=item.notes,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                )
                for item in items
            ],
            created_at=execution_order.created_at,
            updated_at=execution_order.updated_at,
            created_by=execution_order.created_by,
        )
    
    async def _company_reg_to_response(
        self,
        company_reg: CompanyRegistrationInfo
    ) -> CompanyRegistrationInfoResponse:
        """转换为公司注册信息响应对象"""
        return CompanyRegistrationInfoResponse(
            id=company_reg.id,
            execution_order_id=company_reg.execution_order_id,
            company_name=company_reg.company_name,
            nib=company_reg.nib,
            npwp=company_reg.npwp,
            izin_lokasi=company_reg.izin_lokasi,
            akta=company_reg.akta,
            sk=company_reg.sk,
            registration_status=company_reg.registration_status,
            completed_at=company_reg.completed_at,
            notes=company_reg.notes,
            created_at=company_reg.created_at,
            updated_at=company_reg.updated_at,
        )
