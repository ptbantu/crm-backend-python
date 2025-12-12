"""
组织服务
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from foundation_service.schemas.organization import (
    OrganizationCreateRequest, OrganizationUpdateRequest, OrganizationResponse
)
from foundation_service.repositories.organization_repository import OrganizationRepository
from foundation_service.repositories.user_repository import UserRepository
from foundation_service.repositories.role_repository import RoleRepository
from foundation_service.repositories.organization_employee_repository import OrganizationEmployeeRepository
from foundation_service.services.user_service import UserService
from foundation_service.repositories.organization_domain_repository import OrganizationDomainRepository
from common.models.organization import Organization
from common.models.user import User
from common.exceptions import OrganizationNotFoundError, BusinessException
from common.utils.logger import get_logger
from sqlalchemy import select

logger = get_logger(__name__)


class OrganizationService:
    """组织服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.org_repo = OrganizationRepository(db)
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)
        self.employee_repo = OrganizationEmployeeRepository(db)
        self.domain_repo = OrganizationDomainRepository(db)
        self.user_service = UserService(db)
    
    async def create_organization(
        self, 
        request: OrganizationCreateRequest,
        created_by_user_id: Optional[str] = None
    ) -> OrganizationResponse:
        """创建组织"""
        logger.info(f"开始创建组织: name={request.name}, code={request.code}, type={request.organization_type}, created_by={created_by_user_id}")
        
        # 1. 权限检查：只有 BANTU 的 admin 用户可以创建组织
        if created_by_user_id:
            # 检查用户是否是 BANTU 的 admin
            bantu_org = await self.org_repo.get_bantu_organization()
            if not bantu_org:
                logger.warning("BANTU 组织不存在，无法验证权限")
                raise BusinessException(detail="系统配置错误：BANTU 组织不存在")
            
            # 检查用户是否属于 BANTU 组织且拥有 ADMIN 角色
            user = await self.user_repo.get_by_id(created_by_user_id)
            if not user:
                raise BusinessException(detail="用户不存在")
            
            # 检查用户是否属于 BANTU 组织
            bantu_employee = await self.employee_repo.get_primary_by_user_id(created_by_user_id)
            if not bantu_employee or bantu_employee.organization_id != bantu_org.id:
                logger.warning(f"用户不属于 BANTU 组织: user_id={created_by_user_id}")
                raise BusinessException(detail="只有 BANTU 的 admin 用户可以创建组织")
            
            # 检查用户是否拥有 ADMIN 角色
            user_roles = await self.user_repo.get_user_roles(created_by_user_id)
            role_codes = [role.code for role in user_roles]
            if "ADMIN" not in role_codes:
                logger.warning(f"用户不是 ADMIN: user_id={created_by_user_id}, roles={role_codes}")
                raise BusinessException(detail="只有 BANTU 的 admin 用户可以创建组织")
        
        # 2. 生成组织 code（如果未提供）
        if not request.code:
            # 生成格式：type + 序列号(3位) + 年月日(8位)
            # 例如：internal00120241119, vendor00120241119, agent00120241119
            sequence = await self.org_repo.get_next_sequence_by_type(request.organization_type)
            today = datetime.now().strftime("%Y%m%d")
            request.code = f"{request.organization_type}{sequence:03d}{today}"
            logger.info(f"自动生成组织编码: code={request.code}")
        else:
            # 检查编码是否已存在
            existing = await self.org_repo.get_by_code(request.code)
            if existing:
                logger.warning(f"组织编码已存在: code={request.code}")
                raise BusinessException(detail=f"组织编码 {request.code} 已存在")
        
        # 3. 创建组织
        organization = Organization(
            name=request.name,
            code=request.code,
            organization_type=request.organization_type,
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
        logger.info(f"组织创建成功: id={organization.id}, name={organization.name}, code={organization.code}")
        
        # 4. 自动创建该组织的 admin 用户
        await self._create_organization_admin(organization)
        
        return await self._to_response(organization)
    
    async def _create_organization_admin(self, organization: Organization) -> User:
        """为组织自动创建 admin 用户（使用统一的用户创建函数）"""
        logger.info(f"开始为组织创建 admin 用户: organization_id={organization.id}, name={organization.name}")
        
        # 获取 ADMIN 角色
        all_roles = await self.role_repo.get_all()
        admin_role = next((r for r in all_roles if r.code == "ADMIN"), None)
        if not admin_role:
            logger.error("ADMIN 角色不存在，无法创建组织 admin 用户")
            raise BusinessException(detail="系统配置错误：ADMIN 角色不存在")
        
        # 生成默认邮箱和密码
        if organization.email:
            # 从组织邮箱提取域名：contact@example.com -> example.com
            email_parts = organization.email.split("@")
            if len(email_parts) == 2:
                email_domain = email_parts[1]
            else:
                email_domain = "bantu.sbs"
        else:
            email_domain = "bantu.sbs"
        
        admin_email = f"admin@{email_domain}"
        
        # 检查邮箱是否已存在（如果存在，添加组织code后缀）
        existing_email = await self.user_repo.get_by_email(admin_email)
        if existing_email:
            logger.warning(f"Admin 邮箱已存在，使用组织code后缀: email={admin_email}, organization_id={organization.id}")
            if organization.code:
                admin_email = f"admin{organization.code.lower()}@{email_domain}"
            else:
                admin_email = f"admin{organization.id[:8]}@{email_domain}"
        
        # 生成默认密码：admin + "bantu"
        default_password = "adminbantu"
        
        # 使用统一的用户创建函数
        admin_user = await self.user_service._create_user_internal(
            organization_id=organization.id,
            email=admin_email,
            password=default_password,
            role_ids=[admin_role.id],
            username="admin"  # 可选，提供默认用户名
        )
        
        # 更新显示名称和职位信息
        admin_user.display_name = f"{organization.name} 管理员"
        await self.user_repo.update(admin_user)
        
        # 更新员工记录，设置职位和管理员标记
        admin_employee = await self.employee_repo.get_primary_by_user_id(admin_user.id)
        if admin_employee:
            admin_employee.position = "管理员"
            admin_employee.is_manager = True
            await self.employee_repo.update(admin_employee)
        
        logger.info(f"组织 admin 用户创建成功: user_id={admin_user.id}, email={admin_user.email}, password={default_password}")
        return admin_user
    
    async def get_organization_by_id(self, organization_id: str) -> OrganizationResponse:
        """查询组织详情"""
        logger.debug(f"查询组织详情: organization_id={organization_id}")
        organization = await self.org_repo.get_by_id(organization_id)
        if not organization:
            logger.warning(f"组织不存在: organization_id={organization_id}")
            raise OrganizationNotFoundError()
        
        logger.debug(f"组织查询成功: id={organization.id}, name={organization.name}")
        return await self._to_response(organization)
    
    async def update_organization(
        self,
        organization_id: str,
        request: OrganizationUpdateRequest
    ) -> OrganizationResponse:
        """更新组织信息"""
        logger.info(f"开始更新组织: organization_id={organization_id}")
        organization = await self.org_repo.get_by_id(organization_id)
        if not organization:
            logger.warning(f"组织不存在: organization_id={organization_id}")
            raise OrganizationNotFoundError()
        
        # 更新字段（简化处理，实际应该逐个字段判断）
        if request.name is not None:
            organization.name = request.name
        if request.code is not None:
            if request.code != organization.code:
                existing = await self.org_repo.get_by_code(request.code)
                if existing:
                    logger.warning(f"组织编码已存在: code={request.code}, organization_id={organization_id}")
                    raise BusinessException(detail=f"组织编码 {request.code} 已存在")
                logger.debug(f"更新组织编码: organization_id={organization_id}, old_code={organization.code}, new_code={request.code}")
            organization.code = request.code
        
        if request.is_active is not None:
            organization.is_active = request.is_active
        if request.is_locked is not None:
            organization.is_locked = request.is_locked
        
        organization = await self.org_repo.update(organization)
        logger.info(f"组织更新成功: id={organization.id}, name={organization.name}")
        return await self._to_response(organization)
    
    async def lock_organization(self, organization_id: str) -> OrganizationResponse:
        """锁定组织（断开合作）"""
        logger.info(f"开始锁定组织: organization_id={organization_id}")
        organization = await self.org_repo.get_by_id(organization_id)
        if not organization:
            logger.warning(f"组织不存在: organization_id={organization_id}")
            raise OrganizationNotFoundError()
        
        # 不能锁定 BANTU 内部组织
        bantu_org = await self.org_repo.get_bantu_organization()
        if bantu_org and organization.id == bantu_org.id:
            logger.warning(f"不能锁定 BANTU 内部组织: organization_id={organization_id}")
            raise BusinessException(detail="不能锁定 BANTU 内部组织")
        
        # 设置 is_locked = True（锁定，断开合作）
        organization.is_locked = True
        await self.org_repo.update(organization)
        logger.info(f"组织锁定成功: id={organization.id}, name={organization.name}, is_locked=True")
        return await self._to_response(organization)
    
    async def unlock_organization(self, organization_id: str) -> OrganizationResponse:
        """解锁组织（恢复合作）"""
        logger.info(f"开始解锁组织: organization_id={organization_id}")
        organization = await self.org_repo.get_by_id(organization_id)
        if not organization:
            logger.warning(f"组织不存在: organization_id={organization_id}")
            raise OrganizationNotFoundError()
        
        # 设置 is_locked = False（合作，默认状态）
        organization.is_locked = False
        await self.org_repo.update(organization)
        logger.info(f"组织解锁成功: id={organization.id}, name={organization.name}, is_locked=False")
        return await self._to_response(organization)
    
    async def get_organization_list(
        self,
        page: int = 1,
        size: int = 10,
        name: Optional[str] = None,
        code: Optional[str] = None,
        organization_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_locked: Optional[bool] = None,
        current_user_id: Optional[str] = None
    ) -> dict:
        """
        分页查询组织列表
        
        权限逻辑：
        - 只有 internal 内部组织的 admin 用户才能看到所有组织列表
        - 其他组织用户查询时，默认只展示自己的组织
        """
        logger.debug(f"查询组织列表: page={page}, size={size}, name={name}, code={code}, type={organization_type}, is_locked={is_locked}, current_user_id={current_user_id}")
        
        # 如果提供了当前用户ID，检查权限
        if current_user_id:
            # 获取当前用户所属的组织
            current_employee = await self.employee_repo.get_primary_by_user_id(current_user_id)
            if current_employee:
                # 获取当前用户所属的组织信息
                current_org = await self.org_repo.get_by_id(current_employee.organization_id)
                
                # 获取当前用户的角色
                user_roles = await self.user_repo.get_user_roles(current_user_id)
                role_codes = [role.code for role in user_roles]
                is_admin = "ADMIN" in role_codes
                
                # 检查是否是 internal 内部组织的 admin
                # 使用 getattr 安全访问 organization_type，如果不存在则默认为 None
                # 注意：如果数据库表缺少 organization_type 字段，需要先执行数据库迁移
                org_type = getattr(current_org, 'organization_type', None) if current_org else None
                if current_org and org_type == "internal" and is_admin:
                    # 是 internal 组织的 admin，可以查看所有组织
                    logger.debug(f"Internal admin 用户查询所有组织: user_id={current_user_id}, organization_id={current_org.id}")
                    organizations, total = await self.org_repo.get_list(
                        page=page,
                        size=size,
                        name=name,
                        code=code,
                        organization_type=organization_type,
                        is_active=is_active,
                        is_locked=is_locked
                    )
                else:
                    # 其他用户，只能查看自己的组织
                    logger.debug(f"普通用户只查询自己的组织: user_id={current_user_id}, organization_id={current_employee.organization_id}")
                    # 只查询当前用户所属的组织
                    organizations, total = await self.org_repo.get_list(
                        page=page,
                        size=size,
                        name=name,
                        code=code,
                        organization_type=organization_type,
                        is_active=is_active,
                        is_locked=is_locked,
                        organization_id=current_employee.organization_id  # 添加组织ID过滤
                    )
            else:
                # 用户未关联到任何组织，返回空列表
                logger.warning(f"用户未关联到任何组织: user_id={current_user_id}")
                organizations, total = [], 0
        else:
            # 未提供用户ID，返回所有组织（兼容旧逻辑，但实际应该要求认证）
            logger.warning("未提供当前用户ID，返回所有组织（可能存在安全风险）")
            organizations, total = await self.org_repo.get_list(
                page=page,
                size=size,
                name=name,
                code=code,
                organization_type=organization_type,
                is_active=is_active,
                is_locked=is_locked
            )
        
        # 转换为响应对象
        records = []
        for org in organizations:
            try:
                records.append(await self._to_response(org))
            except Exception as e:
                logger.error(f"转换组织响应对象失败: organization_id={org.id}, error={str(e)}", exc_info=True)
                # 跳过有问题的记录，继续处理其他记录
                continue
        
        logger.debug(f"组织列表查询成功: total={total}, returned={len(records)}")
        return {
            "records": records,
            "total": total,
            "size": size,
            "current": page,
            "pages": (total + size - 1) // size if total > 0 else 0
        }
    
    async def _to_response(self, organization: Organization) -> OrganizationResponse:
        """转换为响应对象"""
        # 获取统计信息
        employees_count = await self.org_repo.get_employees_count(organization.id)
        
        # 获取组织领域
        domains = await self.domain_repo.get_by_organization_id(organization.id)
        domain_infos = []
        for domain in domains:
            # 获取关联关系以确定是否为主要领域
            from foundation_service.repositories.organization_domain_repository import OrganizationDomainRelationRepository
            relation_repo = OrganizationDomainRelationRepository(self.db)
            relations = await relation_repo.get_by_organization_id(organization.id)
            is_primary = any(r.domain_id == domain.id and r.is_primary for r in relations)
            
            domain_infos.append({
                "id": domain.id,
                "code": domain.code,
                "name_zh": domain.name_zh,
                "name_id": domain.name_id,
                "is_primary": is_primary
            })
        
        return OrganizationResponse(
            id=organization.id,
            name=organization.name,
            code=organization.code,
            organization_type=getattr(organization, 'organization_type', 'internal'),
            is_locked=getattr(organization, 'is_locked', False) or False,
            email=getattr(organization, 'email', None),
            phone=getattr(organization, 'phone', None),
            website=getattr(organization, 'website', None),
            logo_url=getattr(organization, 'logo_url', None),
            description=getattr(organization, 'description', None),
            is_active=getattr(organization, 'is_active', True),
            is_verified=getattr(organization, 'is_verified', False) or False,
            employees_count=employees_count,
            domains=domain_infos,
            created_at=organization.created_at,
            updated_at=organization.updated_at
        )
    

