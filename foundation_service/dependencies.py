"""
依赖注入
使用公共数据库模块
"""
from typing import Optional
from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from foundation_service.database import get_db
from foundation_service.repositories.organization_repository import OrganizationRepository
from foundation_service.repositories.user_repository import UserRepository
from foundation_service.repositories.organization_employee_repository import OrganizationEmployeeRepository


def get_current_user_id(request: Request) -> Optional[str]:
    """从请求中获取当前用户ID（由 Gateway Service 设置）"""
    return getattr(request.state, "user_id", None)


def get_current_user_roles(request: Request) -> list:
    """从请求中获取当前用户角色（由 Gateway Service 设置）"""
    return getattr(request.state, "roles", [])


async def require_bantu_admin(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> str:
    """要求当前用户是 BANTU 的 admin 用户"""
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要认证"
        )
    
    # 检查用户是否是 BANTU 的 admin
    org_repo = OrganizationRepository(db)
    user_repo = UserRepository(db)
    employee_repo = OrganizationEmployeeRepository(db)
    
    # 获取 BANTU 组织
    bantu_org = await org_repo.get_bantu_organization()
    if not bantu_org:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系统配置错误：BANTU 组织不存在"
        )
    
    # 检查用户是否属于 BANTU 组织
    bantu_employee = await employee_repo.get_primary_by_user_id(user_id)
    if not bantu_employee or bantu_employee.organization_id != bantu_org.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有 BANTU 的 admin 用户可以创建组织"
        )
    
    # 检查用户是否拥有 ADMIN 角色
    user_roles = await user_repo.get_user_roles(user_id)
    role_codes = [role.code for role in user_roles]
    if "ADMIN" not in role_codes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有 BANTU 的 admin 用户可以创建组织"
        )
    
    return user_id


async def require_organization_admin(
    request: Request,
    organization_id: str,
    db: AsyncSession = Depends(get_db)
) -> str:
    """要求当前用户是指定组织的 admin 用户"""
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要认证"
        )
    
    # 检查用户是否属于指定组织
    employee_repo = OrganizationEmployeeRepository(db)
    user_repo = UserRepository(db)
    
    # 检查用户是否属于该组织
    employee = await employee_repo.get_primary_by_user_id(user_id)
    if not employee or employee.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有该组织的 admin 用户可以创建用户"
        )
    
    # 检查用户是否拥有 ADMIN 角色
    user_roles = await user_repo.get_user_roles(user_id)
    role_codes = [role.code for role in user_roles]
    if "ADMIN" not in role_codes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有该组织的 admin 用户可以创建用户"
        )
    
    return user_id
