"""
商机数据访问层
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import joinedload
from datetime import datetime
from common.models.opportunity import Opportunity, OpportunityProduct, OpportunityPaymentStage
from common.utils.repository import BaseRepository


class OpportunityRepository(BaseRepository[Opportunity]):
    """商机仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Opportunity)
    
    async def get_by_id(
        self, 
        opportunity_id: str, 
        organization_id: Optional[str] = None
    ) -> Optional[Opportunity]:
        """根据ID查询商机详情（预加载关联数据）"""
        query = (
            select(Opportunity)
            .options(
                joinedload(Opportunity.customer),
                joinedload(Opportunity.owner),
                joinedload(Opportunity.lead),
                joinedload(Opportunity.products).joinedload(OpportunityProduct.product),
                joinedload(Opportunity.payment_stages)
            )
            .where(Opportunity.id == opportunity_id)
        )
        if organization_id:
            query = query.where(Opportunity.organization_id == organization_id)
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
    
    async def get_list(
        self,
        organization_id: Optional[str] = None,
        page: int = 1,
        size: int = 20,
        owner_user_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        stage: Optional[str] = None,
        status: Optional[str] = None,
        name: Optional[str] = None,
        current_user_id: Optional[str] = None,
        current_user_roles: Optional[List[str]] = None,
    ) -> Tuple[List[Opportunity], int]:
        """查询商机列表（支持数据隔离）"""
        conditions = []
        
        # 组织隔离
        if organization_id:
            conditions.append(Opportunity.organization_id == organization_id)
        
        # 权限控制：非ADMIN用户只能查看自己负责的商机
        is_admin = current_user_roles and "ADMIN" in current_user_roles
        if not is_admin and current_user_id:
            conditions.append(Opportunity.owner_user_id == current_user_id)
        elif owner_user_id:
            conditions.append(Opportunity.owner_user_id == owner_user_id)
        
        # 其他筛选条件
        if customer_id:
            conditions.append(Opportunity.customer_id == customer_id)
        if stage:
            conditions.append(Opportunity.stage == stage)
        if status:
            conditions.append(Opportunity.status == status)
        if name:
            conditions.append(Opportunity.name.like(f"%{name}%"))
        
        # 查询总数
        count_query = select(func.count(Opportunity.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据（预加载关联数据）
        query = (
            select(Opportunity)
            .options(
                joinedload(Opportunity.customer),
                joinedload(Opportunity.owner),
                joinedload(Opportunity.lead),
                joinedload(Opportunity.products).joinedload(OpportunityProduct.product),
                joinedload(Opportunity.payment_stages)
            )
            .where(and_(*conditions))
            .order_by(Opportunity.created_at.desc())
        )
        query = query.offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        opportunities = result.unique().scalars().all()
        
        return list(opportunities), total
    
    async def get_products(
        self, 
        opportunity_id: str
    ) -> List[OpportunityProduct]:
        """查询商机关联的产品（按执行顺序排序）"""
        query = (
            select(OpportunityProduct)
            .options(joinedload(OpportunityProduct.product))
            .where(OpportunityProduct.opportunity_id == opportunity_id)
            .order_by(OpportunityProduct.execution_order.asc())
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_payment_stages(
        self, 
        opportunity_id: str
    ) -> List[OpportunityPaymentStage]:
        """查询商机付款阶段（按阶段序号排序）"""
        query = (
            select(OpportunityPaymentStage)
            .where(OpportunityPaymentStage.opportunity_id == opportunity_id)
            .order_by(OpportunityPaymentStage.stage_number.asc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())


class OpportunityProductRepository(BaseRepository[OpportunityProduct]):
    """商机产品关联仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, OpportunityProduct)
    
    async def get_by_opportunity_id(
        self, 
        opportunity_id: str
    ) -> List[OpportunityProduct]:
        """根据商机ID查询所有关联产品（按执行顺序排序）"""
        query = (
            select(OpportunityProduct)
            .options(joinedload(OpportunityProduct.product))
            .where(OpportunityProduct.opportunity_id == opportunity_id)
            .order_by(OpportunityProduct.execution_order.asc())
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_by_product_id(
        self, 
        product_id: str
    ) -> List[OpportunityProduct]:
        """根据产品ID查询所有关联的商机产品"""
        query = (
            select(OpportunityProduct)
            .options(joinedload(OpportunityProduct.opportunity))
            .where(OpportunityProduct.product_id == product_id)
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())


class OpportunityPaymentStageRepository(BaseRepository[OpportunityPaymentStage]):
    """商机付款阶段仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, OpportunityPaymentStage)
    
    async def get_by_opportunity_id(
        self, 
        opportunity_id: str
    ) -> List[OpportunityPaymentStage]:
        """根据商机ID查询所有付款阶段（按阶段序号排序）"""
        query = (
            select(OpportunityPaymentStage)
            .where(OpportunityPaymentStage.opportunity_id == opportunity_id)
            .order_by(OpportunityPaymentStage.stage_number.asc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

