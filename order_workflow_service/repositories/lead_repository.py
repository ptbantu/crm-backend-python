"""
线索数据访问层
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from datetime import datetime
from order_workflow_service.models.lead import Lead
from common.utils.repository import BaseRepository


class LeadRepository(BaseRepository[Lead]):
    """线索仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Lead)
    
    async def get_by_id(self, lead_id: str, organization_id: Optional[str] = None) -> Optional[Lead]:
        """根据ID查询线索（organization_id可选，如果没有则只根据lead_id查询）"""
        query = select(Lead).where(Lead.id == lead_id)
        if organization_id:
            query = query.where(Lead.organization_id == organization_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_list(
        self,
        organization_id: Optional[str] = None,
        page: int = 1,
        size: int = 20,
        owner_user_id: Optional[str] = None,
        status: Optional[str] = None,
        is_in_public_pool: Optional[bool] = None,
        customer_id: Optional[str] = None,
        company_name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        current_user_id: Optional[str] = None,
        current_user_roles: Optional[List[str]] = None,
    ) -> Tuple[List[Lead], int]:
        """查询线索列表（支持数据隔离，organization_id可选）"""
        # 构建查询条件
        conditions = []
        
        # 如果提供了组织ID，则按组织过滤
        if organization_id:
            conditions.append(Lead.organization_id == organization_id)
        
        # 用户级隔离：根据用户ID查询属于该用户的线索
        # 如果没有组织ID，则必须根据用户ID查询
        if not organization_id:
            # 没有组织ID时，必须根据用户ID查询
            # 查询条件：owner_user_id == current_user_id 或 created_by == current_user_id
            # （用户可以看到自己负责的线索，或者自己创建的线索）
            if current_user_id:
                conditions.append(
                    or_(
                        Lead.owner_user_id == current_user_id,
                        Lead.created_by == current_user_id
                    )
                )
            else:
                # 如果没有用户ID，返回空结果
                return [], 0
        else:
            # 有组织ID时，按角色进行数据隔离
            # 组织内部隔离：非admin用户只能看自己的
            if current_user_roles and "ADMIN" not in current_user_roles:
                if current_user_id:
                    conditions.append(Lead.owner_user_id == current_user_id)
            elif owner_user_id:
                conditions.append(Lead.owner_user_id == owner_user_id)
        
        # 其他筛选条件
        if status:
            conditions.append(Lead.status == status)
        if is_in_public_pool is not None:
            conditions.append(Lead.is_in_public_pool == is_in_public_pool)
        if customer_id:
            conditions.append(Lead.customer_id == customer_id)
        if company_name:
            conditions.append(Lead.company_name.like(f"%{company_name}%"))
        if phone:
            conditions.append(Lead.phone == phone)
        if email:
            conditions.append(Lead.email == email)
        
        # 查询总数
        count_query = select(func.count(Lead.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = select(Lead).where(and_(*conditions)).order_by(Lead.created_at.desc())
        query = query.offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        leads = result.scalars().all()
        
        return list(leads), total
    
    async def check_duplicate(
        self,
        organization_id: str,
        company_name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        exclude_lead_id: Optional[str] = None,
    ) -> List[Lead]:
        """查重：根据公司名、电话、邮箱查找重复线索"""
        conditions = [Lead.organization_id == organization_id]
        
        # 构建查重条件（OR关系）
        duplicate_conditions = []
        if company_name:
            duplicate_conditions.append(Lead.company_name.like(f"%{company_name}%"))
        if phone:
            duplicate_conditions.append(Lead.phone == phone)
        if email:
            duplicate_conditions.append(Lead.email == email)
        
        if not duplicate_conditions:
            return []
        
        conditions.append(or_(*duplicate_conditions))
        
        if exclude_lead_id:
            conditions.append(Lead.id != exclude_lead_id)
        
        query = select(Lead).where(and_(*conditions))
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def move_to_pool(self, lead_id: str, organization_id: str, pool_id: Optional[str] = None) -> Optional[Lead]:
        """移入公海池"""
        lead = await self.get_by_id(lead_id, organization_id)
        if not lead:
            return None
        
        lead.is_in_public_pool = True
        lead.pool_id = pool_id
        lead.moved_to_pool_at = datetime.utcnow()
        lead.owner_user_id = None  # 移入公海池后清空负责人
        
        await self.db.commit()
        await self.db.refresh(lead)
        return lead
    
    async def assign(self, lead_id: str, organization_id: str, owner_user_id: str) -> Optional[Lead]:
        """分配线索给销售"""
        lead = await self.get_by_id(lead_id, organization_id)
        if not lead:
            return None
        
        lead.owner_user_id = owner_user_id
        lead.is_in_public_pool = False
        lead.moved_to_pool_at = None
        
        await self.db.commit()
        await self.db.refresh(lead)
        return lead

