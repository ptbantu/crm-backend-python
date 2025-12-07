"""
工作流数据访问层
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from common.models import (
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowTask,
    WorkflowTransition,
)
from common.utils.repository import BaseRepository


class WorkflowDefinitionRepository(BaseRepository[WorkflowDefinition]):
    """工作流定义仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, WorkflowDefinition)
    
    async def get_by_code(self, code: str) -> Optional[WorkflowDefinition]:
        """根据代码查询工作流定义"""
        query = select(WorkflowDefinition).where(WorkflowDefinition.code == code)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_active_list(self) -> List[WorkflowDefinition]:
        """获取所有激活的工作流定义"""
        query = (
            select(WorkflowDefinition)
            .where(WorkflowDefinition.is_active == True)
            .order_by(WorkflowDefinition.created_at)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())


class WorkflowInstanceRepository(BaseRepository[WorkflowInstance]):
    """工作流实例仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, WorkflowInstance)
    
    async def get_by_business(
        self,
        business_type: str,
        business_id: str
    ) -> Optional[WorkflowInstance]:
        """根据业务对象查询工作流实例"""
        query = (
            select(WorkflowInstance)
            .where(
                WorkflowInstance.business_type == business_type,
                WorkflowInstance.business_id == business_id
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_list(
        self,
        page: int = 1,
        size: int = 20,
        workflow_definition_id: Optional[str] = None,
        business_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> Tuple[List[WorkflowInstance], int]:
        """分页查询工作流实例列表"""
        conditions = []
        
        if workflow_definition_id:
            conditions.append(WorkflowInstance.workflow_definition_id == workflow_definition_id)
        if business_type:
            conditions.append(WorkflowInstance.business_type == business_type)
        if status:
            conditions.append(WorkflowInstance.status == status)
        
        # 查询总数
        count_query = select(func.count(WorkflowInstance.id))
        if conditions:
            count_query = count_query.where(*conditions)
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询列表
        query = select(WorkflowInstance)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(desc(WorkflowInstance.created_at)).offset((page - 1) * size).limit(size)
        
        result = await self.db.execute(query)
        instances = result.scalars().all()
        
        return list(instances), total


class WorkflowTaskRepository(BaseRepository[WorkflowTask]):
    """工作流任务仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, WorkflowTask)
    
    async def get_by_instance_id(
        self,
        workflow_instance_id: str,
        status: Optional[str] = None
    ) -> List[WorkflowTask]:
        """根据工作流实例ID查询任务列表"""
        conditions = [WorkflowTask.workflow_instance_id == workflow_instance_id]
        
        if status:
            conditions.append(WorkflowTask.status == status)
        
        query = (
            select(WorkflowTask)
            .where(*conditions)
            .order_by(WorkflowTask.created_at)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_assigned_user(
        self,
        user_id: str,
        status: Optional[str] = None
    ) -> List[WorkflowTask]:
        """根据分配用户查询任务列表"""
        conditions = [WorkflowTask.assigned_to_user_id == user_id]
        
        if status:
            conditions.append(WorkflowTask.status == status)
        
        query = (
            select(WorkflowTask)
            .where(*conditions)
            .order_by(WorkflowTask.due_date, WorkflowTask.created_at)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())


class WorkflowTransitionRepository(BaseRepository[WorkflowTransition]):
    """工作流流转记录仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, WorkflowTransition)
    
    async def get_by_instance_id(
        self,
        workflow_instance_id: str
    ) -> List[WorkflowTransition]:
        """根据工作流实例ID查询流转记录"""
        query = (
            select(WorkflowTransition)
            .where(WorkflowTransition.workflow_instance_id == workflow_instance_id)
            .order_by(WorkflowTransition.triggered_at)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

