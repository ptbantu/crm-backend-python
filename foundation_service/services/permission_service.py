"""
权限服务层
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from foundation_service.repositories.permission_repository import (
    PermissionRepository,
    RolePermissionRepository,
    MenuRepository,
    MenuPermissionRepository
)
from foundation_service.models.permission import Permission, Menu
from foundation_service.schemas.permission import (
    PermissionCreateRequest,
    PermissionUpdateRequest,
    PermissionResponse,
    PermissionInfo,
    RolePermissionAssignRequest,
    MenuCreateRequest,
    MenuUpdateRequest,
    MenuResponse,
    MenuPermissionAssignRequest,
    UserMenuResponse,
    UserPermissionResponse
)
from common.exceptions import BusinessException
import logging

logger = logging.getLogger(__name__)


class PermissionService:
    """权限服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.permission_repo = PermissionRepository(db)
        self.role_permission_repo = RolePermissionRepository(db)
        self.menu_repo = MenuRepository(db)
        self.menu_permission_repo = MenuPermissionRepository(db)
    
    # ==================== 权限管理 ====================
    
    async def create_permission(self, request: PermissionCreateRequest) -> PermissionResponse:
        """创建权限"""
        # 检查编码是否已存在
        existing = await self.permission_repo.get_by_code(request.code)
        if existing:
            raise BusinessException(detail=f"权限编码 {request.code} 已存在")
        
        permission = Permission(
            code=request.code,
            name_zh=request.name_zh,
            name_id=request.name_id,
            description_zh=request.description_zh,
            description_id=request.description_id,
            resource_type=request.resource_type,
            action=request.action,
            display_order=request.display_order or 0,
            is_active=request.is_active
        )
        permission = await self.permission_repo.create(permission)
        logger.info(f"权限创建成功: id={permission.id}, code={permission.code}")
        return await self._permission_to_response(permission)
    
    async def update_permission(self, permission_id: str, request: PermissionUpdateRequest) -> PermissionResponse:
        """更新权限"""
        permission = await self.permission_repo.get_by_id(permission_id)
        if not permission:
            raise BusinessException(detail="权限不存在")
        
        if request.name_zh is not None:
            permission.name_zh = request.name_zh
        if request.name_id is not None:
            permission.name_id = request.name_id
        if request.description_zh is not None:
            permission.description_zh = request.description_zh
        if request.description_id is not None:
            permission.description_id = request.description_id
        if request.resource_type is not None:
            permission.resource_type = request.resource_type
        if request.action is not None:
            permission.action = request.action
        if request.display_order is not None:
            permission.display_order = request.display_order
        if request.is_active is not None:
            permission.is_active = request.is_active
        
        permission = await self.permission_repo.update(permission)
        logger.info(f"权限更新成功: id={permission.id}, code={permission.code}")
        return await self._permission_to_response(permission)
    
    async def get_permission(self, permission_id: str) -> PermissionResponse:
        """获取权限详情"""
        permission = await self.permission_repo.get_by_id(permission_id)
        if not permission:
            raise BusinessException(detail="权限不存在")
        return await self._permission_to_response(permission)
    
    async def get_permission_list(
        self,
        resource_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[PermissionResponse]:
        """获取权限列表"""
        if resource_type:
            permissions = await self.permission_repo.get_by_resource_type(resource_type)
        else:
            permissions = await self.permission_repo.get_active_permissions()
        
        if is_active is not None:
            permissions = [p for p in permissions if p.is_active == is_active]
        
        return [await self._permission_to_response(p) for p in permissions]
    
    async def _permission_to_response(self, permission: Permission) -> PermissionResponse:
        """转换为响应对象"""
        return PermissionResponse(
            id=permission.id,
            code=permission.code,
            name_zh=permission.name_zh,
            name_id=permission.name_id,
            description_zh=permission.description_zh,
            description_id=permission.description_id,
            resource_type=permission.resource_type,
            action=permission.action,
            display_order=permission.display_order,
            is_active=permission.is_active,
            created_at=permission.created_at,
            updated_at=permission.updated_at
        )
    
    # ==================== 角色权限管理 ====================
    
    async def assign_permissions_to_role(self, role_id: str, request: RolePermissionAssignRequest) -> None:
        """为角色分配权限"""
        # 验证权限是否存在
        for permission_id in request.permission_ids:
            permission = await self.permission_repo.get_by_id(permission_id)
            if not permission:
                raise BusinessException(detail=f"权限不存在: permission_id={permission_id}")
        
        await self.role_permission_repo.assign_permissions_to_role(role_id, request.permission_ids)
        logger.info(f"角色权限分配成功: role_id={role_id}, permission_count={len(request.permission_ids)}")
    
    async def get_role_permissions(self, role_id: str) -> List[PermissionInfo]:
        """获取角色的权限列表"""
        permissions = await self.role_permission_repo.get_role_permissions(role_id)
        return [
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
    
    async def check_user_permission(self, user_id: str, permission_code: str) -> bool:
        """检查用户是否拥有指定权限"""
        permissions = await self.role_permission_repo.get_user_permissions(user_id)
        return any(p.code == permission_code for p in permissions)
    
    async def get_user_permissions(self, user_id: str) -> List[PermissionInfo]:
        """获取用户的所有权限"""
        permissions = await self.role_permission_repo.get_user_permissions(user_id)
        return [
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
    
    # ==================== 菜单管理 ====================
    
    async def create_menu(self, request: MenuCreateRequest) -> MenuResponse:
        """创建菜单"""
        # 检查编码是否已存在
        existing = await self.menu_repo.get_by_code(request.code)
        if existing:
            raise BusinessException(detail=f"菜单编码 {request.code} 已存在")
        
        # 验证父菜单是否存在
        if request.parent_id:
            parent = await self.menu_repo.get_by_id(request.parent_id)
            if not parent:
                raise BusinessException(detail="父菜单不存在")
        
        menu = Menu(
            code=request.code,
            name_zh=request.name_zh,
            name_id=request.name_id,
            description_zh=request.description_zh,
            description_id=request.description_id,
            parent_id=request.parent_id,
            path=request.path,
            component=request.component,
            icon=request.icon,
            display_order=request.display_order or 0,
            is_active=request.is_active,
            is_visible=request.is_visible
        )
        menu = await self.menu_repo.create(menu)
        logger.info(f"菜单创建成功: id={menu.id}, code={menu.code}")
        return await self._menu_to_response(menu)
    
    async def update_menu(self, menu_id: str, request: MenuUpdateRequest) -> MenuResponse:
        """更新菜单"""
        menu = await self.menu_repo.get_by_id(menu_id)
        if not menu:
            raise BusinessException(detail="菜单不存在")
        
        if request.name_zh is not None:
            menu.name_zh = request.name_zh
        if request.name_id is not None:
            menu.name_id = request.name_id
        if request.description_zh is not None:
            menu.description_zh = request.description_zh
        if request.description_id is not None:
            menu.description_id = request.description_id
        if request.parent_id is not None:
            # 验证父菜单是否存在
            if request.parent_id:
                parent = await self.menu_repo.get_by_id(request.parent_id)
                if not parent:
                    raise BusinessException(detail="父菜单不存在")
            menu.parent_id = request.parent_id
        if request.path is not None:
            menu.path = request.path
        if request.component is not None:
            menu.component = request.component
        if request.icon is not None:
            menu.icon = request.icon
        if request.display_order is not None:
            menu.display_order = request.display_order
        if request.is_active is not None:
            menu.is_active = request.is_active
        if request.is_visible is not None:
            menu.is_visible = request.is_visible
        
        menu = await self.menu_repo.update(menu)
        logger.info(f"菜单更新成功: id={menu.id}, code={menu.code}")
        return await self._menu_to_response(menu)
    
    async def get_menu(self, menu_id: str) -> MenuResponse:
        """获取菜单详情"""
        menu = await self.menu_repo.get_by_id(menu_id)
        if not menu:
            raise BusinessException(detail="菜单不存在")
        return await self._menu_to_response(menu)
    
    async def get_menu_tree(self) -> List[MenuResponse]:
        """获取菜单树"""
        # 获取所有菜单
        all_menus = await self.menu_repo.get_active_menus()
        # 构建菜单树
        menu_map = {menu.id: menu for menu in all_menus}
        root_menus = []
        for menu in all_menus:
            if menu.parent_id and menu.parent_id in menu_map:
                parent = menu_map[menu.parent_id]
                if not hasattr(parent, '_children'):
                    parent._children = []
                parent._children.append(menu)
            else:
                root_menus.append(menu)
        
        return [await self._menu_to_response_tree(menu) for menu in root_menus]
    
    async def _menu_to_response(self, menu: Menu) -> MenuResponse:
        """转换为响应对象（单个菜单）"""
        permissions = await self.menu_permission_repo.get_menu_permissions(menu.id)
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
        
        return MenuResponse(
            id=menu.id,
            code=menu.code,
            name_zh=menu.name_zh,
            name_id=menu.name_id,
            description_zh=menu.description_zh,
            description_id=menu.description_id,
            parent_id=menu.parent_id,
            path=menu.path,
            component=menu.component,
            icon=menu.icon,
            display_order=menu.display_order,
            is_active=menu.is_active,
            is_visible=menu.is_visible,
            children=[],
            permissions=permission_infos,
            created_at=menu.created_at,
            updated_at=menu.updated_at
        )
    
    async def _menu_to_response_tree(self, menu: Menu) -> MenuResponse:
        """转换为响应对象（树形结构）"""
        permissions = await self.menu_permission_repo.get_menu_permissions(menu.id)
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
        
        # 递归处理子菜单
        children = []
        if hasattr(menu, '_children'):
            children = [await self._menu_to_response_tree(child) for child in menu._children]
        
        return MenuResponse(
            id=menu.id,
            code=menu.code,
            name_zh=menu.name_zh,
            name_id=menu.name_id,
            description_zh=menu.description_zh,
            description_id=menu.description_id,
            parent_id=menu.parent_id,
            path=menu.path,
            component=menu.component,
            icon=menu.icon,
            display_order=menu.display_order,
            is_active=menu.is_active,
            is_visible=menu.is_visible,
            children=children,
            permissions=permission_infos,
            created_at=menu.created_at,
            updated_at=menu.updated_at
        )
    
    # ==================== 菜单权限管理 ====================
    
    async def assign_permissions_to_menu(self, menu_id: str, request: MenuPermissionAssignRequest) -> None:
        """为菜单分配权限"""
        # 验证权限是否存在
        for permission_id in request.permission_ids:
            permission = await self.permission_repo.get_by_id(permission_id)
            if not permission:
                raise BusinessException(detail=f"权限不存在: permission_id={permission_id}")
        
        await self.menu_permission_repo.assign_permissions_to_menu(menu_id, request.permission_ids)
        logger.info(f"菜单权限分配成功: menu_id={menu_id}, permission_count={len(request.permission_ids)}")
    
    # ==================== 用户菜单和权限 ====================
    
    async def get_user_menus(self, user_id: str) -> List[UserMenuResponse]:
        """获取用户可访问的菜单"""
        menus = await self.menu_permission_repo.get_user_menus(user_id)
        return [await self._menu_to_user_response(menu) for menu in menus]
    
    async def _menu_to_user_response(self, menu: Menu) -> UserMenuResponse:
        """转换为用户菜单响应"""
        children = []
        if hasattr(menu, '_children'):
            children = [await self._menu_to_user_response(child) for child in menu._children]
        
        return UserMenuResponse(
            id=menu.id,
            code=menu.code,
            name_zh=menu.name_zh,
            name_id=menu.name_id,
            path=menu.path,
            component=menu.component,
            icon=menu.icon,
            display_order=menu.display_order,
            children=children
        )
    
    async def get_user_permission_info(self, user_id: str) -> UserPermissionResponse:
        """获取用户的权限和菜单信息"""
        permissions = await self.get_user_permissions(user_id)
        menus = await self.get_user_menus(user_id)
        return UserPermissionResponse(
            permissions=permissions,
            menus=menus
        )

