"""
角色服务
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from foundation_service.schemas.role import RoleCreateRequest, RoleUpdateRequest, RoleResponse
from foundation_service.repositories.role_repository import RoleRepository
from foundation_service.models.role import Role
from common.exceptions import RoleNotFoundError, BusinessException
from common.utils.logger import get_logger

logger = get_logger(__name__)


class RoleService:
    """角色服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.role_repo = RoleRepository(db)
    
    async def get_role_list(self) -> List[RoleResponse]:
        """查询角色列表"""
        logger.debug("查询角色列表")
        roles = await self.role_repo.get_all()
        logger.debug(f"角色列表查询成功: total={len(roles)}")
        return [RoleResponse(
            id=role.id,
            code=role.code,
            name=role.name,
            description=role.description,
            created_at=role.created_at,
            updated_at=role.updated_at
        ) for role in roles]
    
    async def create_role(self, request: RoleCreateRequest) -> RoleResponse:
        """创建角色"""
        # 检查角色编码是否已存在
        existing = await self.role_repo.get_by_code(request.code)
        if existing:
            raise BusinessException(detail=f"角色编码 {request.code} 已存在")
        
        role = Role(
            code=request.code,
            name=request.name,
            description=request.description
        )
        
        role = await self.role_repo.create(role)
        
        return RoleResponse(
            id=role.id,
            code=role.code,
            name=role.name,
            description=role.description,
            created_at=role.created_at,
            updated_at=role.updated_at
        )
    
    async def update_role(self, role_id: str, request: RoleUpdateRequest) -> RoleResponse:
        """更新角色"""
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise RoleNotFoundError()
        
        # 预设角色的 code 不可修改（这里简化处理）
        role.name = request.name
        role.description = request.description
        
        role = await self.role_repo.update(role)
        
        return RoleResponse(
            id=role.id,
            code=role.code,
            name=role.name,
            description=role.description,
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

