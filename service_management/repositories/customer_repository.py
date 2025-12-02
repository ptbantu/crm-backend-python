"""
客户数据访问层
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from common.models.customer import Customer
from common.utils.repository import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    """客户仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Customer)
    
    async def get_by_code(self, code: str) -> Optional[Customer]:
        """根据编码查询客户"""
        query = select(Customer).where(Customer.code == code)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_list(
        self,
        organization_id: str,  # 必须参数，用于数据隔离
        page: int = 1,
        size: int = 10,
        name: Optional[str] = None,
        code: Optional[str] = None,
        customer_type: Optional[str] = None,
        customer_source_type: Optional[str] = None,
        parent_customer_id: Optional[str] = None,
        owner_user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        source_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        is_locked: Optional[bool] = None,
    ) -> Tuple[List[Customer], int]:
        """分页查询客户列表（必须包含organization_id过滤）"""
        query = select(Customer)
        conditions = []
        
        # 必须包含组织ID过滤（数据隔离）
        conditions.append(Customer.organization_id == organization_id)
        
        if name:
            conditions.append(Customer.name.ilike(f"%{name}%"))
        if code:
            conditions.append(Customer.code.ilike(f"%{code}%"))
        if customer_type:
            conditions.append(Customer.customer_type == customer_type)
        if customer_source_type:
            conditions.append(Customer.customer_source_type == customer_source_type)
        if parent_customer_id:
            conditions.append(Customer.parent_customer_id == parent_customer_id)
        if owner_user_id:
            conditions.append(Customer.owner_user_id == owner_user_id)
        if agent_id:
            conditions.append(Customer.agent_id == agent_id)
        if source_id:
            conditions.append(Customer.source_id == source_id)
        if channel_id:
            conditions.append(Customer.channel_id == channel_id)
        if is_locked is not None:
            conditions.append(Customer.is_locked == is_locked)
        
        if conditions:
            from sqlalchemy import and_
            query = query.where(and_(*conditions))
        
        # 排序
        query = query.order_by(Customer.created_at.desc())
        
        # 计算总数
        count_query = select(func.count()).select_from(Customer)
        if conditions:
            from sqlalchemy import and_
            count_query = count_query.where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页
        query = query.offset((page - 1) * size).limit(size)
        
        # 执行查询
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return list(items), total

