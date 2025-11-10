"""
组织服务
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from foundation_service.schemas.organization import (
    OrganizationCreateRequest, OrganizationUpdateRequest, OrganizationResponse
)
from foundation_service.repositories.organization_repository import OrganizationRepository
from foundation_service.models.organization import Organization
from common.exceptions import OrganizationNotFoundError, BusinessException


class OrganizationService:
    """组织服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.org_repo = OrganizationRepository(db)
    
    async def create_organization(self, request: OrganizationCreateRequest) -> OrganizationResponse:
        """创建组织"""
        # 检查编码是否已存在
        if request.code:
            existing = await self.org_repo.get_by_code(request.code)
            if existing:
                raise BusinessException(detail=f"组织编码 {request.code} 已存在")
        
        # 验证父组织
        if request.parent_id:
            parent = await self.org_repo.get_by_id(request.parent_id)
            if not parent:
                raise OrganizationNotFoundError()
        
        organization = Organization(
            name=request.name,
            code=request.code,
            organization_type=request.organization_type,
            parent_id=request.parent_id,
            email=request.email,
            phone=request.phone,
            website=request.website,
            logo_url=request.logo_url,
            description=request.description,
            street=request.street,
            city=request.city,
            state_province=request.state_province,
            postal_code=request.postal_code,
            country=request.country,
            country_code=request.country_code,
            company_size=request.company_size,
            company_nature=request.company_nature,
            company_type=request.company_type,
            industry=request.industry,
            industry_code=request.industry_code,
            sub_industry=request.sub_industry,
            business_scope=request.business_scope,
            registration_number=request.registration_number,
            tax_id=request.tax_id,
            legal_representative=request.legal_representative,
            established_date=request.established_date,
            registered_capital=request.registered_capital,
            registered_capital_currency=request.registered_capital_currency,
            company_status=request.company_status,
            annual_revenue=request.annual_revenue,
            annual_revenue_currency=request.annual_revenue_currency,
            employee_count=request.employee_count,
            revenue_year=request.revenue_year,
            certifications=request.certifications or [],
            business_license_url=request.business_license_url,
            tax_certificate_url=request.tax_certificate_url,
            is_active=request.is_active
        )
        
        organization = await self.org_repo.create(organization)
        return await self._to_response(organization)
    
    async def get_organization_by_id(self, organization_id: str) -> OrganizationResponse:
        """查询组织详情"""
        organization = await self.org_repo.get_by_id(organization_id)
        if not organization:
            raise OrganizationNotFoundError()
        
        return await self._to_response(organization)
    
    async def update_organization(
        self,
        organization_id: str,
        request: OrganizationUpdateRequest
    ) -> OrganizationResponse:
        """更新组织信息"""
        organization = await self.org_repo.get_by_id(organization_id)
        if not organization:
            raise OrganizationNotFoundError()
        
        # 更新字段（简化处理，实际应该逐个字段判断）
        if request.name is not None:
            organization.name = request.name
        if request.code is not None:
            if request.code != organization.code:
                existing = await self.org_repo.get_by_code(request.code)
                if existing:
                    raise BusinessException(detail=f"组织编码 {request.code} 已存在")
            organization.code = request.code
        if request.is_active is not None:
            organization.is_active = request.is_active
        if request.is_locked is not None:
            organization.is_locked = request.is_locked
        
        organization = await self.org_repo.update(organization)
        return await self._to_response(organization)
    
    async def delete_organization(self, organization_id: str) -> None:
        """Block 组织（逻辑删除）"""
        organization = await self.org_repo.get_by_id(organization_id)
        if not organization:
            raise OrganizationNotFoundError()
        
        organization.is_locked = True
        organization.is_active = False
        await self.org_repo.update(organization)
    
    async def get_organization_list(
        self,
        page: int = 1,
        size: int = 10,
        name: Optional[str] = None,
        code: Optional[str] = None,
        organization_type: Optional[str] = None,
        parent_id: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> dict:
        """分页查询组织列表"""
        organizations, total = await self.org_repo.get_list(
            page=page,
            size=size,
            name=name,
            code=code,
            organization_type=organization_type,
            parent_id=parent_id,
            is_active=is_active
        )
        
        # 转换为响应对象
        records = []
        for org in organizations:
            records.append(await self._to_response(org))
        
        return {
            "records": records,
            "total": total,
            "size": size,
            "current": page,
            "pages": (total + size - 1) // size if total > 0 else 0
        }
    
    async def _to_response(self, organization: Organization) -> OrganizationResponse:
        """转换为响应对象"""
        # 获取父组织名称
        parent_name = None
        if organization.parent_id:
            parent = await self.org_repo.get_by_id(organization.parent_id)
            parent_name = parent.name if parent else None
        
        # 获取统计信息
        children_count = await self.org_repo.get_children_count(organization.id)
        employees_count = await self.org_repo.get_employees_count(organization.id)
        
        return OrganizationResponse(
            id=organization.id,
            name=organization.name,
            code=organization.code,
            organization_type=organization.organization_type,
            parent_id=organization.parent_id,
            parent_name=parent_name,
            email=organization.email,
            phone=organization.phone,
            website=organization.website,
            logo_url=organization.logo_url,
            description=organization.description,
            is_active=organization.is_active,
            is_locked=organization.is_locked or False,
            is_verified=organization.is_verified or False,
            children_count=children_count,
            employees_count=employees_count,
            created_at=organization.created_at,
            updated_at=organization.updated_at
        )

