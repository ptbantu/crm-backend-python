"""
用户服务
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from foundation_service.schemas.user import (
    UserCreateRequest, UserUpdateRequest, UserResponse, UserListResponse, RoleInfo
)
from foundation_service.repositories.user_repository import UserRepository
from foundation_service.repositories.organization_repository import OrganizationRepository
from foundation_service.repositories.organization_employee_repository import OrganizationEmployeeRepository
from foundation_service.models.user import User
from foundation_service.models.organization_employee import OrganizationEmployee
from foundation_service.models.user_role import UserRole
from foundation_service.utils.password import hash_password
from common.exceptions import UserNotFoundError, OrganizationNotFoundError, BusinessException


class UserService:
    """用户服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.org_repo = OrganizationRepository(db)
        self.employee_repo = OrganizationEmployeeRepository(db)
    
    async def create_user(self, request: UserCreateRequest) -> UserResponse:
        """创建用户"""
        # 验证组织是否存在
        organization = await self.org_repo.get_by_id(request.organization_id)
        if not organization:
            raise OrganizationNotFoundError()
        
        # 检查邮箱是否已存在
        if request.email:
            existing = await self.user_repo.get_by_email(request.email)
            if existing:
                raise BusinessException(detail="邮箱已存在")
        
        # 创建用户
        user = User(
            username=request.username,
            email=request.email,
            phone=request.phone,
            display_name=request.display_name,
            password_hash=hash_password(request.password),
            avatar_url=request.avatar_url,
            bio=request.bio,
            gender=request.gender,
            address=request.address,
            contact_phone=request.contact_phone,
            whatsapp=request.whatsapp,
            wechat=request.wechat,
            is_active=request.is_active
        )
        
        user = await self.user_repo.create(user)
        
        # 自动创建组织员工记录
        if request.auto_create_employee:
            employee = OrganizationEmployee(
                user_id=user.id,
                organization_id=request.organization_id,
                is_primary=True,
                is_active=True
            )
            await self.employee_repo.create(employee)
        
        # 分配角色
        if request.role_ids:
            for role_id in request.role_ids:
                user_role = UserRole(user_id=user.id, role_id=role_id)
                self.db.add(user_role)
            await self.db.flush()
        
        return await self._to_response(user)
    
    async def get_user_by_id(self, user_id: str) -> UserResponse:
        """查询用户详情"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        
        return await self._to_response(user)
    
    async def get_user_list(
        self,
        page: int = 1,
        size: int = 10,
        email: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> UserListResponse:
        """分页查询用户列表"""
        users, total = await self.user_repo.get_list(
            page=page,
            size=size,
            email=email,
            organization_id=organization_id
        )
        
        records = [await self._to_response(user) for user in users]
        
        return UserListResponse(
            records=records,
            total=total,
            size=size,
            current=page,
            pages=(total + size - 1) // size
        )
    
    async def update_user(self, user_id: str, request: UserUpdateRequest) -> UserResponse:
        """更新用户信息"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        
        # 更新字段
        if request.email is not None:
            if request.email != user.email:
                existing = await self.user_repo.get_by_email(request.email)
                if existing:
                    raise BusinessException(detail="邮箱已存在")
            user.email = request.email
        
        if request.phone is not None:
            user.phone = request.phone
        if request.display_name is not None:
            user.display_name = request.display_name
        if request.avatar_url is not None:
            user.avatar_url = request.avatar_url
        if request.bio is not None:
            user.bio = request.bio
        if request.gender is not None:
            user.gender = request.gender
        if request.address is not None:
            user.address = request.address
        if request.contact_phone is not None:
            user.contact_phone = request.contact_phone
        if request.whatsapp is not None:
            user.whatsapp = request.whatsapp
        if request.wechat is not None:
            user.wechat = request.wechat
        if request.is_active is not None:
            user.is_active = request.is_active
        
        # 更新角色
        if request.role_ids is not None:
            # 删除旧角色
            await self.db.execute(
                delete(UserRole).where(UserRole.user_id == user_id)
            )
            # 添加新角色
            for role_id in request.role_ids:
                user_role = UserRole(user_id=user_id, role_id=role_id)
                self.db.add(user_role)
        
        user = await self.user_repo.update(user)
        return await self._to_response(user)
    
    async def delete_user(self, user_id: str) -> None:
        """Block 用户（逻辑删除）"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        
        user.is_active = False
        await self.user_repo.update(user)
    
    async def _to_response(self, user: User) -> UserResponse:
        """转换为响应对象"""
        # 获取主要组织
        primary_employee = await self.employee_repo.get_primary_by_user_id(user.id)
        primary_org_id = primary_employee.organization_id if primary_employee else None
        primary_org_name = None
        if primary_org_id:
            org = await self.org_repo.get_by_id(primary_org_id)
            primary_org_name = org.name if org else None
        
        # 获取角色
        roles = await self.user_repo.get_user_roles(user.id)
        role_infos = [
            RoleInfo(id=role.id, code=role.code, name=role.name)
            for role in roles
        ]
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            phone=user.phone,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            bio=user.bio,
            gender=user.gender,
            address=user.address,
            contact_phone=user.contact_phone,
            whatsapp=user.whatsapp,
            wechat=user.wechat,
            primary_organization_id=primary_org_id,
            primary_organization_name=primary_org_name,
            is_active=user.is_active,
            last_login_at=user.last_login_at,
            roles=role_infos,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
