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
from common.exceptions import (
    UserNotFoundError, OrganizationNotFoundError, OrganizationInactiveError, 
    BusinessException
)
from common.utils.logger import get_logger

logger = get_logger(__name__)


class UserService:
    """用户服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.org_repo = OrganizationRepository(db)
        self.employee_repo = OrganizationEmployeeRepository(db)
    
    async def create_user(self, request: UserCreateRequest) -> UserResponse:
        """创建用户"""
        logger.info(f"开始创建用户: username={request.username}, email={request.email}, organization_id={request.organization_id}")
        
        # 验证组织是否存在
        organization = await self.org_repo.get_by_id(request.organization_id)
        if not organization:
            logger.warning(f"组织不存在: organization_id={request.organization_id}")
            raise OrganizationNotFoundError()
        
        # 检查组织是否激活
        if not organization.is_active:
            logger.warning(f"组织未激活: organization_id={request.organization_id}, name={organization.name}")
            raise OrganizationInactiveError()
        
        # 检查组织内用户名是否已存在（用户名在组织内唯一）
        existing_user = await self.user_repo.get_by_username_in_organization(
            request.username, 
            request.organization_id
        )
        if existing_user:
            logger.warning(f"组织内用户名已存在: username={request.username}, organization_id={request.organization_id}")
            raise BusinessException(detail=f"用户名 {request.username} 在该组织内已存在")
        
        # 检查邮箱是否已存在（邮箱全局唯一）
        if request.email:
            existing = await self.user_repo.get_by_email(request.email)
            if existing:
                logger.warning(f"邮箱已存在: email={request.email}")
                raise BusinessException(detail="邮箱已存在")
        
        # 验证密码强度（至少8位，包含字母和数字）
        if len(request.password) < 8:
            logger.warning(f"密码长度不足: username={request.username}")
            raise BusinessException(detail="密码长度至少8位")
        
        # 检查密码是否包含字母和数字（可选，可根据需求调整）
        has_letter = any(c.isalpha() for c in request.password)
        has_digit = any(c.isdigit() for c in request.password)
        if not (has_letter and has_digit):
            logger.warning(f"密码强度不足: username={request.username}")
            raise BusinessException(detail="密码必须包含字母和数字")
        
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
        
        # 必须创建组织员工记录（业务规则：每个用户必须至少有一个组织员工记录）
        logger.debug(f"创建组织员工记录: user_id={user.id}, organization_id={request.organization_id}")
        
        # 检查用户是否已有主要组织，如果没有则设置为主要组织
        existing_primary = await self.employee_repo.get_primary_by_user_id(user.id)
        is_primary = existing_primary is None  # 如果没有主要组织，则设为主要组织
        
        employee = OrganizationEmployee(
            user_id=user.id,
            organization_id=request.organization_id,
            is_primary=is_primary,
            is_active=True
        )
        await self.employee_repo.create(employee)
        
        # 分配角色
        if request.role_ids:
            logger.debug(f"分配角色: user_id={user.id}, role_ids={request.role_ids}")
            for role_id in request.role_ids:
                user_role = UserRole(user_id=user.id, role_id=role_id)
                self.db.add(user_role)
            await self.db.flush()
        
        logger.info(f"用户创建成功: id={user.id}, username={user.username}, email={user.email}")
        return await self._to_response(user)
    
    async def get_user_by_id(self, user_id: str) -> UserResponse:
        """查询用户详情"""
        logger.debug(f"查询用户详情: user_id={user_id}")
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            logger.warning(f"用户不存在: user_id={user_id}")
            raise UserNotFoundError()
        
        logger.debug(f"用户查询成功: id={user.id}, username={user.username}")
        return await self._to_response(user)
    
    async def get_user_list(
        self,
        page: int = 1,
        size: int = 10,
        email: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> UserListResponse:
        """分页查询用户列表"""
        logger.debug(f"查询用户列表: page={page}, size={size}, email={email}, organization_id={organization_id}")
        users, total = await self.user_repo.get_list(
            page=page,
            size=size,
            email=email,
            organization_id=organization_id
        )
        
        records = [await self._to_response(user) for user in users]
        
        logger.debug(f"用户列表查询成功: total={total}, returned={len(records)}")
        return UserListResponse(
            records=records,
            total=total,
            size=size,
            current=page,
            pages=(total + size - 1) // size
        )
    
    async def update_user(self, user_id: str, request: UserUpdateRequest) -> UserResponse:
        """更新用户信息"""
        logger.info(f"开始更新用户: user_id={user_id}")
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            logger.warning(f"用户不存在: user_id={user_id}")
            raise UserNotFoundError()
        
        # 更新字段
        if request.email is not None:
            if request.email != user.email:
                existing = await self.user_repo.get_by_email(request.email)
                if existing:
                    logger.warning(f"邮箱已存在: email={request.email}, user_id={user_id}")
                    raise BusinessException(detail="邮箱已存在")
                logger.debug(f"更新邮箱: user_id={user_id}, old_email={user.email}, new_email={request.email}")
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
            logger.debug(f"更新用户角色: user_id={user_id}, role_ids={request.role_ids}")
            # 删除旧角色
            await self.db.execute(
                delete(UserRole).where(UserRole.user_id == user_id)
            )
            # 添加新角色
            for role_id in request.role_ids:
                user_role = UserRole(user_id=user_id, role_id=role_id)
                self.db.add(user_role)
        
        user = await self.user_repo.update(user)
        logger.info(f"用户更新成功: id={user.id}, username={user.username}")
        return await self._to_response(user)
    
    async def delete_user(self, user_id: str) -> None:
        """Block 用户（逻辑删除）"""
        logger.info(f"开始删除用户: user_id={user_id}")
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            logger.warning(f"用户不存在: user_id={user_id}")
            raise UserNotFoundError()
        
        user.is_active = False
        await self.user_repo.update(user)
        logger.info(f"用户删除成功: id={user.id}, username={user.username}")
    
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
