"""
数据库模型
"""
from foundation_service.models.user import User
from foundation_service.models.organization import Organization
from foundation_service.models.role import Role
from foundation_service.models.organization_employee import OrganizationEmployee
from foundation_service.models.user_role import UserRole
from foundation_service.models.organization_domain import OrganizationDomain, OrganizationDomainRelation
from foundation_service.models.permission import Permission, RolePermission, Menu, MenuPermission

__all__ = [
    "User",
    "Organization",
    "Role",
    "OrganizationEmployee",
    "UserRole",
    "OrganizationDomain",
    "OrganizationDomainRelation",
    "Permission",
    "RolePermission",
    "Menu",
    "MenuPermission",
]

