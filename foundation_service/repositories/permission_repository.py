"""
权限数据访问层
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from foundation_service.models.permission import Permission, RolePermission, Menu, MenuPermission
from common.utils.repository import BaseRepository


class PermissionRepository(BaseRepository[Permission]):
    """权限仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Permission)
    
    async def get_by_code(self, code: str) -> Optional[Permission]:
        """根据编码查询权限"""
        result = await self.db.execute(
            select(Permission).where(Permission.code == code)
        )
        return result.scalar_one_or_none()
    
    async def get_by_resource_type(self, resource_type: str) -> List[Permission]:
        """根据资源类型查询权限"""
        result = await self.db.execute(
            select(Permission)
            .where(
                and_(
                    Permission.resource_type == resource_type,
                    Permission.is_active == True
                )
            )
            .order_by(Permission.display_order)
        )
        return list(result.scalars().all())
    
    async def get_active_permissions(self) -> List[Permission]:
        """获取所有激活的权限"""
        result = await self.db.execute(
            select(Permission)
            .where(Permission.is_active == True)
            .order_by(Permission.resource_type, Permission.display_order)
        )
        return list(result.scalars().all())


class RolePermissionRepository:
    """角色权限关联仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_role_permissions(self, role_id: str) -> List[Permission]:
        """获取角色的权限列表"""
        result = await self.db.execute(
            select(Permission)
            .join(RolePermission, Permission.id == RolePermission.permission_id)
            .where(
                and_(
                    RolePermission.role_id == role_id,
                    Permission.is_active == True
                )
            )
            .order_by(Permission.resource_type, Permission.display_order)
        )
        return list(result.scalars().all())
    
    async def get_user_permissions(self, user_id: str) -> List[Permission]:
        """获取用户的所有权限（通过角色）"""
        from foundation_service.models.user_role import UserRole
        
        result = await self.db.execute(
            select(Permission)
            .join(RolePermission, Permission.id == RolePermission.permission_id)
            .join(UserRole, RolePermission.role_id == UserRole.role_id)
            .where(
                and_(
                    UserRole.user_id == user_id,
                    Permission.is_active == True
                )
            )
            .distinct()
            .order_by(Permission.resource_type, Permission.display_order)
        )
        return list(result.scalars().all())
    
    async def assign_permissions_to_role(self, role_id: str, permission_ids: List[str]) -> None:
        """为角色分配权限"""
        # 删除旧权限
        await self.db.execute(
            delete(RolePermission).where(RolePermission.role_id == role_id)
        )
        # 添加新权限
        for permission_id in permission_ids:
            role_permission = RolePermission(role_id=role_id, permission_id=permission_id)
            self.db.add(role_permission)
        await self.db.flush()
    
    async def has_permission(self, role_id: str, permission_code: str) -> bool:
        """检查角色是否拥有指定权限"""
        result = await self.db.execute(
            select(RolePermission)
            .join(Permission, RolePermission.permission_id == Permission.id)
            .where(
                and_(
                    RolePermission.role_id == role_id,
                    Permission.code == permission_code,
                    Permission.is_active == True
                )
            )
        )
        return result.scalar_one_or_none() is not None


class MenuRepository(BaseRepository[Menu]):
    """菜单仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Menu)
    
    async def get_by_code(self, code: str) -> Optional[Menu]:
        """根据编码查询菜单"""
        result = await self.db.execute(
            select(Menu).where(Menu.code == code)
        )
        return result.scalar_one_or_none()
    
    async def get_tree(self, parent_id: Optional[str] = None) -> List[Menu]:
        """获取菜单树（递归）"""
        result = await self.db.execute(
            select(Menu)
            .where(
                and_(
                    Menu.parent_id == parent_id,
                    Menu.is_active == True,
                    Menu.is_visible == True
                )
            )
            .order_by(Menu.display_order)
        )
        menus = list(result.scalars().all())
        # 注意：不在模型上设置 children，而是在 service 层构建树形结构
        return menus
    
    async def get_active_menus(self) -> List[Menu]:
        """获取所有激活的菜单"""
        result = await self.db.execute(
            select(Menu)
            .where(
                and_(
                    Menu.is_active == True,
                    Menu.is_visible == True
                )
            )
            .order_by(Menu.display_order)
        )
        return list(result.scalars().all())


class MenuPermissionRepository:
    """菜单权限关联仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_menu_permissions(self, menu_id: str) -> List[Permission]:
        """获取菜单关联的权限"""
        result = await self.db.execute(
            select(Permission)
            .join(MenuPermission, Permission.id == MenuPermission.permission_id)
            .where(
                and_(
                    MenuPermission.menu_id == menu_id,
                    Permission.is_active == True
                )
            )
        )
        return list(result.scalars().all())
    
    async def get_user_menus(self, user_id: str) -> List[Menu]:
        """获取用户可访问的菜单（根据权限过滤）"""
        from foundation_service.models.user_role import UserRole
        
        # 获取用户的所有权限
        result = await self.db.execute(
            select(Permission.id)
            .join(RolePermission, Permission.id == RolePermission.permission_id)
            .join(UserRole, RolePermission.role_id == UserRole.role_id)
            .where(
                and_(
                    UserRole.user_id == user_id,
                    Permission.is_active == True
                )
            )
            .distinct()
        )
        user_permission_ids = {row[0] for row in result.all()}
        
        # 获取所有激活的菜单
        all_menus_result = await self.db.execute(
            select(Menu)
            .where(
                and_(
                    Menu.is_active == True,
                    Menu.is_visible == True
                )
            )
            .order_by(Menu.display_order)
        )
        all_menus = list(all_menus_result.scalars().all())
        
        # 获取菜单权限关联
        menu_permissions_result = await self.db.execute(
            select(MenuPermission)
        )
        menu_permissions_map = {}
        for mp in menu_permissions_result.scalars().all():
            if mp.menu_id not in menu_permissions_map:
                menu_permissions_map[mp.menu_id] = []
            menu_permissions_map[mp.menu_id].append(mp.permission_id)
        
        # 过滤菜单：如果菜单没有关联权限，或者用户拥有任一关联权限，则显示
        accessible_menus = []
        for menu in all_menus:
            required_permissions = menu_permissions_map.get(menu.id, [])
            # 如果菜单没有关联权限，或者用户拥有任一关联权限，则显示
            if not required_permissions or any(pid in user_permission_ids for pid in required_permissions):
                accessible_menus.append(menu)
        
        # 构建菜单树（使用临时属性 _children）
        menu_map = {menu.id: menu for menu in accessible_menus}
        root_menus = []
        for menu in accessible_menus:
            if menu.parent_id and menu.parent_id in menu_map:
                parent = menu_map[menu.parent_id]
                if not hasattr(parent, '_children'):
                    parent._children = []
                parent._children.append(menu)
            else:
                root_menus.append(menu)
        
        return root_menus
    
    async def assign_permissions_to_menu(self, menu_id: str, permission_ids: List[str]) -> None:
        """为菜单分配权限"""
        # 删除旧权限
        await self.db.execute(
            delete(MenuPermission).where(MenuPermission.menu_id == menu_id)
        )
        # 添加新权限
        for permission_id in permission_ids:
            menu_permission = MenuPermission(menu_id=menu_id, permission_id=permission_id)
            self.db.add(menu_permission)
        await self.db.flush()

