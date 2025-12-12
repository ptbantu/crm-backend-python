"""
认证服务
"""
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from foundation_service.schemas.auth import LoginRequest, LoginResponse, UserInfo
from foundation_service.repositories.user_repository import UserRepository
from foundation_service.repositories.organization_repository import OrganizationRepository
from foundation_service.repositories.organization_employee_repository import OrganizationEmployeeRepository
from foundation_service.repositories.role_repository import RoleRepository
from foundation_service.utils.password import verify_password
from foundation_service.utils.jwt import create_access_token, create_refresh_token
from common.models.user_role import UserRole
from common.exceptions import (
    UserNotFoundError, PasswordIncorrectError, OrganizationNotFoundError,
    OrganizationLockedError, OrganizationInactiveError, UserInactiveError
)
from common.utils.logger import get_logger

logger = get_logger(__name__)


class AuthService:
    """认证服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.org_repo = OrganizationRepository(db)
        self.employee_repo = OrganizationEmployeeRepository(db)
        self.role_repo = RoleRepository(db)
    
    async def login(self, request: LoginRequest) -> LoginResponse:
        """用户登录（邮箱+密码）"""
        # 1. 查询用户（仅支持邮箱登录）
        user = await self.user_repo.get_by_email(request.email)
        if not user:
            raise UserNotFoundError()
        
        # 2. 验证密码
        if not user.password_hash or not verify_password(request.password, user.password_hash):
            raise PasswordIncorrectError()
        
        # 3. 查询用户的主要组织
        primary_employee = await self.employee_repo.get_primary_by_user_id(user.id)
        if not primary_employee:
            raise OrganizationNotFoundError()
        
        # 4. 检查组织状态
        organization = await self.org_repo.get_by_id(primary_employee.organization_id)
        if not organization:
            raise OrganizationNotFoundError()
        
        # 检查组织是否锁定：is_locked=True 表示锁定（断开合作），该组织所有用户不能登录
        if organization.is_locked:
            logger.warning(f"组织已锁定，用户无法登录: user_id={user.id}, organization_id={organization.id}, organization_name={organization.name}")
            raise OrganizationLockedError()
        
        # 检查组织是否激活
        if not organization.is_active:
            raise OrganizationInactiveError()
        
        # 5. 查询用户的所有激活的组织（用于前端缓存）
        all_employees = await self.employee_repo.get_all_by_user_id(user.id)
        organization_ids = [emp.organization_id for emp in all_employees]
        
        # 6. 检查用户是否被锁定
        if user.is_locked:
            logger.warning(f"用户已锁定，无法登录: user_id={user.id}, email={request.email}")
            raise UserInactiveError()
        
        # 7. 检查用户是否激活
        if not user.is_active:
            raise UserInactiveError()
        
        # 8. 查询用户角色
        roles = await self.user_repo.get_user_roles(user.id)
        role_codes = [role.code for role in roles]
        
        # 9. 查询权限列表（简化处理，从配置获取）
        permissions = self._get_permissions_by_roles(role_codes)
        
        # 10. 生成 JWT Token（包含主要组织ID，用于快速访问）
        token_data = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "primary_organization_id": organization.id,
            "organization_id": organization.id,  # 兼容字段，与 get_current_organization_id 保持一致
            "roles": role_codes,
            "permissions": permissions
        }
        token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # 11. 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        await self.user_repo.update(user)
        
        # 12. 构建响应（包含所有组织ID，供前端缓存）
        user_info = UserInfo(
            id=user.id,
            username=user.username,
            email=user.email,
            display_name=user.display_name,
            primary_organization_id=organization.id,
            primary_organization_name=organization.name,
            organization_ids=organization_ids,  # 所有组织ID列表
            roles=role_codes,
            permissions=permissions
        )
        
        return LoginResponse(
            token=token,
            refresh_token=refresh_token,
            user=user_info,
            expires_in=86400000  # 24小时
        )
    
    def _get_permissions_by_roles(self, role_codes: list[str]) -> list[str]:
        """根据角色获取权限（简化实现）"""
        # TODO: 从配置或权限表获取
        permissions_map = {
            "ADMIN": ["*:*"],
            "SALES": ["customer:read", "customer:write", "order:read", "order:write"],
            "AGENT": ["customer:read", "order:read"],
            "OPERATION": ["order:read", "order:write", "order:process"],
            "FINANCE": ["order:read", "finance:read", "finance:write"]
        }
        
        permissions = []
        for role_code in role_codes:
            if role_code in permissions_map:
                permissions.extend(permissions_map[role_code])
        
        return list(set(permissions))  # 去重

