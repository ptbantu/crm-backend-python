"""
用户数据访问层
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from foundation_service.models.user import User
from foundation_service.models.organization_employee import OrganizationEmployee
from foundation_service.models.user_role import UserRole
from foundation_service.models.role import Role


class UserRepository:
    """用户仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """根据ID查询用户"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱查询用户"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def create(self, user: User) -> User:
        """创建用户"""
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def update(self, user: User) -> User:
        """更新用户"""
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def get_list(
        self,
        page: int = 1,
        size: int = 10,
        email: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> tuple[List[User], int]:
        """分页查询用户列表"""
        query = select(User)
        
        if email:
            query = query.where(User.email == email)
        
        if organization_id:
            # 通过 organization_employees 关联查询
            query = query.join(
                OrganizationEmployee,
                User.id == OrganizationEmployee.user_id
            ).where(
                OrganizationEmployee.organization_id == organization_id,
                OrganizationEmployee.is_active == True
            )
        
        # 获取总数（使用子查询）
        count_subquery = query.subquery()
        count_query = select(func.count()).select_from(count_subquery)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页查询
        query = query.offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        users = result.scalars().all()
        
        return list(users), total
    
    async def get_user_roles(self, user_id: str) -> List[Role]:
        """获取用户角色"""
        result = await self.db.execute(
            select(Role)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user_id)
        )
        return list(result.scalars().all())
