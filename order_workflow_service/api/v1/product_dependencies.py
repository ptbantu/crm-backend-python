"""
产品依赖关系 API 路由（ADMIN专用）
"""
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from order_workflow_service.dependencies import (
    get_database_session,
    get_current_user_id,
    get_current_user_roles,
)
from common.auth import (
    get_current_user_id_from_request as get_user_id_from_token,
    get_current_user_roles_from_request as get_user_roles_from_token,
)
from order_workflow_service.config import settings
from order_workflow_service.repositories.product_dependency_repository import ProductDependencyRepository
from order_workflow_service.services.product_dependency_service import ProductDependencyService
from order_workflow_service.schemas.product_dependency import (
    ProductDependencyResponse,
    ProductDependencyCreateRequest,
    ProductDependencyUpdateRequest,
    ProductDependencyListResponse,
)
from common.schemas.response import Result
from common.utils.logger import get_logger
from common.exceptions import BusinessException
import uuid

logger = get_logger(__name__)

router = APIRouter()


def require_admin(user_roles: Optional[List[str]]) -> None:
    """要求ADMIN角色"""
    if not user_roles or "ADMIN" not in user_roles:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="只有ADMIN用户可以管理产品依赖关系"
        )


@router.get("", response_model=Result[ProductDependencyListResponse])
async def get_product_dependency_list(
    request_obj: Request,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    product_id: Optional[str] = Query(None),
    depends_on_product_id: Optional[str] = Query(None),
    dependency_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_database_session),
):
    """获取产品依赖关系列表（ADMIN专用）"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    user_roles = get_user_roles_from_token(request_obj, settings)
    require_admin(user_roles)
    
    repository = ProductDependencyRepository(db)
    dependencies, total = await repository.get_list(
        page=page,
        size=size,
        product_id=product_id,
        depends_on_product_id=depends_on_product_id,
        dependency_type=dependency_type,
    )
    
    records = []
    for dep in dependencies:
        product_name = None
        product_code = None
        if dep.product:
            product_name = dep.product.name
            product_code = dep.product.code
        
        depends_on_name = None
        depends_on_code = None
        if dep.depends_on_product:
            depends_on_name = dep.depends_on_product.name
            depends_on_code = dep.depends_on_product.code
        
        records.append(ProductDependencyResponse(
            id=dep.id,
            product_id=dep.product_id,
            product_name=product_name,
            product_code=product_code,
            depends_on_product_id=dep.depends_on_product_id,
            depends_on_product_name=depends_on_name,
            depends_on_product_code=depends_on_code,
            dependency_type=dep.dependency_type,
            description=dep.description,
            created_at=dep.created_at,
            updated_at=dep.updated_at,
        ))
    
    return Result.success(data=ProductDependencyListResponse(
        records=records,
        total=total,
        size=size,
        current=page,
        pages=(total + size - 1) // size if size > 0 else 0,
    ))


@router.get("/{product_id}", response_model=Result[List[ProductDependencyResponse]])
async def get_product_dependencies(
    product_id: str,
    dependency_type: Optional[str] = Query(None),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_database_session),
):
    """获取产品的依赖关系（所有用户可查看）"""
    service = ProductDependencyService(db)
    dependencies = await service.get_product_dependencies(product_id, dependency_type)
    
    records = []
    for dep in dependencies:
        product_name = None
        product_code = None
        if dep.product:
            product_name = dep.product.name
            product_code = dep.product.code
        
        depends_on_name = None
        depends_on_code = None
        if dep.depends_on_product:
            depends_on_name = dep.depends_on_product.name
            depends_on_code = dep.depends_on_product.code
        
        records.append(ProductDependencyResponse(
            id=dep.id,
            product_id=dep.product_id,
            product_name=product_name,
            product_code=product_code,
            depends_on_product_id=dep.depends_on_product_id,
            depends_on_product_name=depends_on_name,
            depends_on_product_code=depends_on_code,
            dependency_type=dep.dependency_type,
            description=dep.description,
            created_at=dep.created_at,
            updated_at=dep.updated_at,
        ))
    
    return Result.success(data=records)


@router.get("/{product_id}/dependents", response_model=Result[List[ProductDependencyResponse]])
async def get_dependent_products(
    product_id: str,
    request_obj: Request = None,
    db: AsyncSession = Depends(get_database_session),
):
    """获取依赖该产品的产品列表（所有用户可查看）"""
    service = ProductDependencyService(db)
    dependencies = await service.get_dependent_products(product_id)
    
    records = []
    for dep in dependencies:
        product_name = None
        product_code = None
        if dep.product:
            product_name = dep.product.name
            product_code = dep.product.code
        
        depends_on_name = None
        depends_on_code = None
        if dep.depends_on_product:
            depends_on_name = dep.depends_on_product.name
            depends_on_code = dep.depends_on_product.code
        
        records.append(ProductDependencyResponse(
            id=dep.id,
            product_id=dep.product_id,
            product_name=product_name,
            product_code=product_code,
            depends_on_product_id=dep.depends_on_product_id,
            depends_on_product_name=depends_on_name,
            depends_on_product_code=depends_on_code,
            dependency_type=dep.dependency_type,
            description=dep.description,
            created_at=dep.created_at,
            updated_at=dep.updated_at,
        ))
    
    return Result.success(data=records)


@router.post("", response_model=Result[ProductDependencyResponse], status_code=201)
async def create_product_dependency(
    request: ProductDependencyCreateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_database_session),
):
    """创建产品依赖关系（ADMIN专用）"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    user_roles = get_user_roles_from_token(request_obj, settings)
    require_admin(user_roles)
    
    # 检查循环依赖
    service = ProductDependencyService(db)
    has_circular = await service.check_circular_dependency(
        request.product_id,
        request.depends_on_product_id
    )
    if has_circular:
        raise BusinessException(
            detail="存在循环依赖，无法创建",
            status_code=400
        )
    
    # 检查是否已存在
    repository = ProductDependencyRepository(db)
    existing = await repository.get_by_product_pair(
        request.product_id,
        request.depends_on_product_id
    )
    if existing:
        raise BusinessException(
            detail="该依赖关系已存在",
            status_code=400
        )
    
    # 创建依赖关系
    from common.models.product_dependency import ProductDependency
    dependency = ProductDependency(
        id=str(uuid.uuid4()),
        product_id=request.product_id,
        depends_on_product_id=request.depends_on_product_id,
        dependency_type=request.dependency_type,
        description=request.description,
    )
    
    await db.add(dependency)
    await db.commit()
    await db.refresh(dependency)
    
    # 加载关联产品
    await db.refresh(dependency, ["product", "depends_on_product"])
    
    product_name = None
    product_code = None
    if dependency.product:
        product_name = dependency.product.name
        product_code = dependency.product.code
    
    depends_on_name = None
    depends_on_code = None
    if dependency.depends_on_product:
        depends_on_name = dependency.depends_on_product.name
        depends_on_code = dependency.depends_on_product.code
    
    return Result.success(
        data=ProductDependencyResponse(
            id=dependency.id,
            product_id=dependency.product_id,
            product_name=product_name,
            product_code=product_code,
            depends_on_product_id=dependency.depends_on_product_id,
            depends_on_product_name=depends_on_name,
            depends_on_product_code=depends_on_code,
            dependency_type=dependency.dependency_type,
            description=dependency.description,
            created_at=dependency.created_at,
            updated_at=dependency.updated_at,
        ),
        message="产品依赖关系创建成功"
    )


@router.put("/{dependency_id}", response_model=Result[ProductDependencyResponse])
async def update_product_dependency(
    dependency_id: str,
    request: ProductDependencyUpdateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_database_session),
):
    """更新产品依赖关系（ADMIN专用）"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    user_roles = get_user_roles_from_token(request_obj, settings)
    require_admin(user_roles)
    
    repository = ProductDependencyRepository(db)
    dependency = await repository.get_by_id(dependency_id)
    if not dependency:
        raise BusinessException(detail="产品依赖关系不存在", status_code=404)
    
    # 更新字段
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(dependency, key, value)
    
    await db.commit()
    await db.refresh(dependency)
    await db.refresh(dependency, ["product", "depends_on_product"])
    
    product_name = None
    product_code = None
    if dependency.product:
        product_name = dependency.product.name
        product_code = dependency.product.code
    
    depends_on_name = None
    depends_on_code = None
    if dependency.depends_on_product:
        depends_on_name = dependency.depends_on_product.name
        depends_on_code = dependency.depends_on_product.code
    
    return Result.success(
        data=ProductDependencyResponse(
            id=dependency.id,
            product_id=dependency.product_id,
            product_name=product_name,
            product_code=product_code,
            depends_on_product_id=dependency.depends_on_product_id,
            depends_on_product_name=depends_on_name,
            depends_on_product_code=depends_on_code,
            dependency_type=dependency.dependency_type,
            description=dependency.description,
            created_at=dependency.created_at,
            updated_at=dependency.updated_at,
        ),
        message="产品依赖关系更新成功"
    )


@router.delete("/{dependency_id}", response_model=Result[None])
async def delete_product_dependency(
    dependency_id: str,
    request_obj: Request,
    db: AsyncSession = Depends(get_database_session),
):
    """删除产品依赖关系（ADMIN专用）"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    user_roles = get_user_roles_from_token(request_obj, settings)
    require_admin(user_roles)
    
    repository = ProductDependencyRepository(db)
    dependency = await repository.get_by_id(dependency_id)
    if not dependency:
        raise BusinessException(detail="产品依赖关系不存在", status_code=404)
    
    await db.delete(dependency)
    await db.commit()
    
    return Result.success(message="产品依赖关系删除成功")

