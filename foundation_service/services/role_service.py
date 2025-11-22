"""
角色服务
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from foundation_service.schemas.role import RoleCreateRequest, RoleUpdateRequest, RoleResponse
from foundation_service.repositories.role_repository import RoleRepository
from foundation_service.repositories.permission_repository import RolePermissionRepository
from foundation_service.models.role import Role
from common.exceptions import RoleNotFoundError, BusinessException
from common.utils.logger import get_logger

logger = get_logger(__name__)


class RoleService:
    """角色服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.role_repo = RoleRepository(db)
        self.role_permission_repo = RolePermissionRepository(db)
    
    async def get_role_list(self) -> List[RoleResponse]:
        """查询角色列表"""
        logger.debug("查询角色列表")
        roles = await self.role_repo.get_all()
        logger.debug(f"角色列表查询成功: total={len(roles)}")
        
        result = []
        for role in roles:
            # 获取角色的权限列表
            permissions = await self.role_permission_repo.get_role_permissions(role.id)
            from foundation_service.schemas.permission import PermissionInfo
            permission_infos = [
                PermissionInfo(
                    id=p.id,
                    code=p.code,
                    name_zh=p.name_zh,
                    name_id=p.name_id,
                    resource_type=p.resource_type,
                    action=p.action
                )
                for p in permissions
            ]
            
            result.append(RoleResponse(
                id=role.id,
                code=role.code,
                name=role.name,
                name_zh=role.name_zh,
                name_id=role.name_id,
                description=role.description,
                description_zh=role.description_zh,
                description_id=role.description_id,
                permissions=permission_infos,
                created_at=role.created_at,
                updated_at=role.updated_at
            ))
        
        return result
    
    async def create_role(self, request: RoleCreateRequest) -> RoleResponse:
        """创建角色"""
        # 检查角色编码是否已存在
        existing = await self.role_repo.get_by_code(request.code)
        if existing:
            raise BusinessException(detail=f"角色编码 {request.code} 已存在")
        
        role = Role(
            code=request.code,
            name=request.name or request.name_zh or request.name_id or request.code,
            name_zh=request.name_zh,
            name_id=request.name_id,
            description=request.description,
            description_zh=request.description_zh,
            description_id=request.description_id
        )
        
        role = await self.role_repo.create(role)
        
        return RoleResponse(
            id=role.id,
            code=role.code,
            name=role.name,
            name_zh=role.name_zh,
            name_id=role.name_id,
            description=role.description,
            description_zh=role.description_zh,
            description_id=role.description_id,
            permissions=[],
            created_at=role.created_at,
            updated_at=role.updated_at
        )
    
    async def update_role(self, role_id: str, request: RoleUpdateRequest) -> RoleResponse:
        """更新角色"""
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise RoleNotFoundError()
        
        # 预设角色的 code 不可修改（这里简化处理）
        if request.name is not None:
            role.name = request.name
        if request.name_zh is not None:
            role.name_zh = request.name_zh
        if request.name_id is not None:
            role.name_id = request.name_id
        if request.description is not None:
            role.description = request.description
        if request.description_zh is not None:
            role.description_zh = request.description_zh
        if request.description_id is not None:
            role.description_id = request.description_id
        
        role = await self.role_repo.update(role)
        
        # 获取角色的权限列表
        permissions = await self.role_permission_repo.get_role_permissions(role.id)
        from foundation_service.schemas.permission import PermissionInfo
        permission_infos = [
            PermissionInfo(
                id=p.id,
                code=p.code,
                name_zh=p.name_zh,
                name_id=p.name_id,
                resource_type=p.resource_type,
                action=p.action
            )
            for p in permissions
        ]
        
        return RoleResponse(
            id=role.id,
            code=role.code,
            name=role.name,
            name_zh=role.name_zh,
            name_id=role.name_id,
            description=role.description,
            description_zh=role.description_zh,
            description_id=role.description_id,
            permissions=permission_infos,
            created_at=role.created_at,
            updated_at=role.updated_at
        )
    
    async def get_role(self, role_id: str) -> RoleResponse:
        """获取角色详情"""
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise RoleNotFoundError()
        
        # 获取角色的权限列表
        permissions = await self.role_permission_repo.get_role_permissions(role.id)
        from foundation_service.schemas.permission import PermissionInfo
        permission_infos = [
            PermissionInfo(
                id=p.id,
                code=p.code,
                name_zh=p.name_zh,
                name_id=p.name_id,
                resource_type=p.resource_type,
                action=p.action
            )
            for p in permissions
        ]
        
        return RoleResponse(
            id=role.id,
            code=role.code,
            name=role.name,
            name_zh=role.name_zh,
            name_id=role.name_id,
            description=role.description,
            description_zh=role.description_zh,
            description_id=role.description_id,
            permissions=permission_infos,
            created_at=role.created_at,
            updated_at=role.updated_at
        )
    
    async def delete_role(self, role_id: str) -> None:
        """删除角色"""
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise RoleNotFoundError()
        
        # 预设角色不可删除
        preset_roles = ["ADMIN", "SALES", "AGENT", "OPERATION", "FINANCE"]
        if role.code in preset_roles:
            raise BusinessException(detail=f"预设角色 {role.code} 不可删除")
        
        await self.role_repo.delete(role)

