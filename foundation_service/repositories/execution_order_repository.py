"""
执行订单仓库
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import joinedload
from common.models.execution_order import ExecutionOrder, ExecutionOrderItem, ExecutionOrderDependency, CompanyRegistrationInfo
from common.models.execution_order import ExecutionOrderStatusEnum, ExecutionOrderTypeEnum
from common.utils.repository import BaseRepository


class ExecutionOrderRepository(BaseRepository[ExecutionOrder]):
    """执行订单仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ExecutionOrder)
    
    async def get_by_opportunity_id(
        self,
        opportunity_id: str,
        include_items: bool = True
    ) -> List[ExecutionOrder]:
        """根据商机ID查询所有执行订单"""
        query = (
            select(ExecutionOrder)
            .where(ExecutionOrder.opportunity_id == opportunity_id)
        )
        if include_items:
            query = query.options(joinedload(ExecutionOrder.items))
        
        query = query.order_by(desc(ExecutionOrder.created_at))
        result = await self.db.execute(query)
        return list(result.unique().scalars().all()) if include_items else list(result.scalars().all())
    
    async def get_by_order_no(self, order_no: str) -> Optional[ExecutionOrder]:
        """根据订单编号查询"""
        query = (
            select(ExecutionOrder)
            .options(
                joinedload(ExecutionOrder.items),
                joinedload(ExecutionOrder.dependencies),
                joinedload(ExecutionOrder.opportunity),
                joinedload(ExecutionOrder.contract)
            )
            .where(ExecutionOrder.order_no == order_no)
        )
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
    
    async def get_by_status(
        self,
        status: ExecutionOrderStatusEnum,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[ExecutionOrder], int]:
        """根据状态查询执行订单列表"""
        conditions = [ExecutionOrder.status == status]
        
        # 查询总数
        count_query = select(func.count(ExecutionOrder.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (
            select(ExecutionOrder)
            .options(joinedload(ExecutionOrder.assignee))
            .where(and_(*conditions))
            .order_by(desc(ExecutionOrder.created_at))
            .offset((page - 1) * size)
            .limit(size)
        )
        result = await self.db.execute(query)
        orders = list(result.unique().scalars().all())
        
        return orders, total
    
    async def get_by_type(
        self,
        opportunity_id: str,
        order_type: ExecutionOrderTypeEnum
    ) -> List[ExecutionOrder]:
        """根据订单类型查询"""
        query = (
            select(ExecutionOrder)
            .where(ExecutionOrder.opportunity_id == opportunity_id)
            .where(ExecutionOrder.order_type == order_type)
            .order_by(desc(ExecutionOrder.created_at))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_wechat_group_no(self, wechat_group_no: str) -> List[ExecutionOrder]:
        """根据群编号查询执行订单"""
        query = (
            select(ExecutionOrder)
            .options(joinedload(ExecutionOrder.items))
            .where(ExecutionOrder.wechat_group_no == wechat_group_no)
            .order_by(desc(ExecutionOrder.created_at))
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_by_assigned_to(
        self,
        assigned_to: str,
        status: Optional[ExecutionOrderStatusEnum] = None
    ) -> List[ExecutionOrder]:
        """根据分配人查询执行订单"""
        query = (
            select(ExecutionOrder)
            .options(joinedload(ExecutionOrder.items))
            .where(ExecutionOrder.assigned_to == assigned_to)
        )
        if status:
            query = query.where(ExecutionOrder.status == status)
        else:
            query = query.where(ExecutionOrder.status.in_([
                ExecutionOrderStatusEnum.PENDING,
                ExecutionOrderStatusEnum.IN_PROGRESS
            ]))
        
        query = query.order_by(ExecutionOrder.planned_start_date.asc())
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_blocked_orders(self, opportunity_id: str) -> List[ExecutionOrder]:
        """获取被阻塞的执行订单"""
        query = (
            select(ExecutionOrder)
            .options(joinedload(ExecutionOrder.dependencies))
            .where(ExecutionOrder.opportunity_id == opportunity_id)
            .where(ExecutionOrder.status == ExecutionOrderStatusEnum.BLOCKED)
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_company_registration_order(
        self,
        opportunity_id: str
    ) -> Optional[ExecutionOrder]:
        """获取公司注册执行订单"""
        query = (
            select(ExecutionOrder)
            .where(ExecutionOrder.opportunity_id == opportunity_id)
            .where(ExecutionOrder.order_type == ExecutionOrderTypeEnum.COMPANY_REGISTRATION)
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()


class ExecutionOrderItemRepository(BaseRepository[ExecutionOrderItem]):
    """执行订单明细仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ExecutionOrderItem)
    
    async def get_by_execution_order_id(
        self,
        execution_order_id: str
    ) -> List[ExecutionOrderItem]:
        """根据执行订单ID查询所有明细"""
        query = (
            select(ExecutionOrderItem)
            .options(
                joinedload(ExecutionOrderItem.product),
                joinedload(ExecutionOrderItem.quotation_item)
            )
            .where(ExecutionOrderItem.execution_order_id == execution_order_id)
            .order_by(ExecutionOrderItem.created_at.asc())
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_by_status(
        self,
        execution_order_id: str,
        status: str
    ) -> List[ExecutionOrderItem]:
        """根据状态查询明细"""
        query = (
            select(ExecutionOrderItem)
            .where(ExecutionOrderItem.execution_order_id == execution_order_id)
            .where(ExecutionOrderItem.status == status)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())


class ExecutionOrderDependencyRepository(BaseRepository[ExecutionOrderDependency]):
    """执行订单依赖关系仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ExecutionOrderDependency)
    
    async def get_by_execution_order_id(
        self,
        execution_order_id: str
    ) -> List[ExecutionOrderDependency]:
        """根据执行订单ID查询所有依赖关系"""
        query = (
            select(ExecutionOrderDependency)
            .options(
                joinedload(ExecutionOrderDependency.prerequisite_order)
            )
            .where(ExecutionOrderDependency.execution_order_id == execution_order_id)
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_by_prerequisite_order_id(
        self,
        prerequisite_order_id: str
    ) -> List[ExecutionOrderDependency]:
        """根据前置依赖订单ID查询依赖关系"""
        query = (
            select(ExecutionOrderDependency)
            .options(
                joinedload(ExecutionOrderDependency.execution_order)
            )
            .where(ExecutionOrderDependency.prerequisite_order_id == prerequisite_order_id)
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_pending_dependencies(
        self,
        execution_order_id: str
    ) -> List[ExecutionOrderDependency]:
        """获取待满足的依赖关系"""
        from common.models.execution_order import DependencyStatusEnum
        query = (
            select(ExecutionOrderDependency)
            .options(joinedload(ExecutionOrderDependency.prerequisite_order))
            .where(ExecutionOrderDependency.execution_order_id == execution_order_id)
            .where(ExecutionOrderDependency.status == DependencyStatusEnum.PENDING)
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def check_all_dependencies_satisfied(
        self,
        execution_order_id: str
    ) -> bool:
        """检查所有依赖是否已满足"""
        from common.models.execution_order import DependencyStatusEnum
        query = (
            select(func.count(ExecutionOrderDependency.id))
            .where(ExecutionOrderDependency.execution_order_id == execution_order_id)
            .where(ExecutionOrderDependency.status != DependencyStatusEnum.SATISFIED)
        )
        result = await self.db.execute(query)
        count = result.scalar() or 0
        return count == 0


class CompanyRegistrationInfoRepository(BaseRepository[CompanyRegistrationInfo]):
    """公司注册信息仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, CompanyRegistrationInfo)
    
    async def get_by_execution_order_id(
        self,
        execution_order_id: str
    ) -> Optional[CompanyRegistrationInfo]:
        """根据执行订单ID查询公司注册信息（一对一关系）"""
        query = (
            select(CompanyRegistrationInfo)
            .options(joinedload(CompanyRegistrationInfo.execution_order))
            .where(CompanyRegistrationInfo.execution_order_id == execution_order_id)
        )
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
    
    async def get_completed_registrations(self) -> List[CompanyRegistrationInfo]:
        """获取已完成的公司注册信息"""
        query = (
            select(CompanyRegistrationInfo)
            .options(joinedload(CompanyRegistrationInfo.execution_order))
            .where(CompanyRegistrationInfo.registration_status == "completed")
            .order_by(CompanyRegistrationInfo.completed_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
