"""
线索数据访问层
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import joinedload
from datetime import datetime
from order_workflow_service.models.lead import Lead
from common.utils.repository import BaseRepository


class LeadRepository(BaseRepository[Lead]):
    """线索仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Lead)
    
    async def get_by_id(self, lead_id: str, organization_id: Optional[str] = None) -> Optional[Lead]:
        """根据ID查询线索（organization_id可选，如果没有则只根据lead_id查询）"""
        query = select(Lead).options(joinedload(Lead.owner)).where(Lead.id == lead_id)
        if organization_id:
            query = query.where(Lead.organization_id == organization_id)
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
    
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
        """查询线索列表（支持数据隔离）
        
        查询逻辑：
        1. 如果有组织ID：
           - 如果是公海（is_in_public_pool=True）：查询该组织内的全部公海线索（所有用户丢入公海的线索）
           - 如果是我的线索（is_in_public_pool=False 或 None）：
             - 非admin用户：查询该组织内且该用户创建的线索，且不在公海（is_in_public_pool=False）
             - Admin用户：可以查询该组织内的所有线索（根据其他筛选条件）
        2. 如果没有组织ID：
           - 必须根据用户ID查询（created_by == current_user_id），且不在公海
        """
        # 构建查询条件
        conditions = []
        
        # 如果提供了组织ID，则按组织过滤
        if organization_id:
            conditions.append(Lead.organization_id == organization_id)
            
            # 判断是否是公海查询
            is_public_pool_query = is_in_public_pool is True
            
            if is_public_pool_query:
                # 公海线索：查询该组织内的全部公海线索（所有用户丢入公海的线索，不限制创建人）
                conditions.append(Lead.is_in_public_pool == True)
            else:
                # 我的线索（is_in_public_pool=False 或 None）：根据角色进行数据隔离
                is_admin = current_user_roles and "ADMIN" in current_user_roles
                
                if is_admin:
                    # Admin 可以查询该组织内的所有线索（根据其他筛选条件）
                    # 如果指定了 owner_user_id，则按负责人过滤
                    if owner_user_id:
                        conditions.append(Lead.owner_user_id == owner_user_id)
                    # 如果明确指定了 is_in_public_pool=False，则只查询非公海线索
                    if is_in_public_pool is False:
                        conditions.append(Lead.is_in_public_pool == False)
                    # 如果 is_in_public_pool 为 None，不添加此条件（查询所有线索，包括公海和非公海）
                else:
                    # 非admin用户：查询该组织内且该用户负责的线索（owner_user_id），且不在公海
                    if current_user_id:
                        conditions.append(Lead.owner_user_id == current_user_id)
                        # 我的线索必须排除公海线索
                        conditions.append(Lead.is_in_public_pool == False)
                    else:
                        # 如果没有用户ID，返回空结果
                        return [], 0
        else:
            # 没有组织ID时，必须根据用户ID查询
            # 查询条件：owner_user_id == current_user_id（用户负责的线索），且不在公海
            if current_user_id:
                conditions.append(Lead.owner_user_id == current_user_id)
                # 我的线索必须排除公海线索
                if is_in_public_pool is not True:  # 如果不是明确查询公海，则排除公海线索
                    conditions.append(Lead.is_in_public_pool == False)
            else:
                # 如果没有用户ID，返回空结果
                return [], 0
        
        # 其他筛选条件
        if status:
            conditions.append(Lead.status == status)
        # 注意：is_in_public_pool 的处理已经在上面完成，这里不再重复处理
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
        
        # 查询数据（使用 joinedload 预加载 owner 关系，避免 N+1 查询）
        query = select(Lead).options(joinedload(Lead.owner)).where(and_(*conditions)).order_by(Lead.created_at.desc())
        query = query.offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        leads = result.unique().scalars().all()
        
        return list(leads), total
    
    async def check_duplicate(
        self,
        organization_id: str,
        company_name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        exclude_lead_id: Optional[str] = None,
        exact_match: bool = False,
    ) -> List[Lead]:
        """查重：根据公司名、电话、邮箱查找重复线索
        
        Args:
            organization_id: 组织ID
            company_name: 公司名称
            phone: 电话
            email: 邮箱
            exclude_lead_id: 排除的线索ID（用于编辑时排除自己）
            exact_match: 是否完全匹配公司名（True=精确匹配，False=模糊匹配）
        """
        conditions = [Lead.organization_id == organization_id]
        
        # 构建查重条件（OR关系）
        duplicate_conditions = []
        if company_name:
            if exact_match:
                # 完全匹配：精确相等
                duplicate_conditions.append(Lead.company_name == company_name)
            else:
                # 模糊匹配：使用 LIKE
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

