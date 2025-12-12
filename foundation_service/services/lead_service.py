"""
线索服务
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from common.models.lead import Lead
from foundation_service.repositories.lead_repository import LeadRepository
from foundation_service.repositories.lead_follow_up_repository import LeadFollowUpRepository
from foundation_service.repositories.lead_note_repository import LeadNoteRepository
from foundation_service.services.customer_level_service import CustomerLevelService
from foundation_service.utils.organization_helper import get_user_organization_id
from foundation_service.schemas.lead import (
    LeadCreateRequest,
    LeadUpdateRequest,
    LeadResponse,
    LeadListResponse,
)
from common.utils.logger import get_logger
from common.exceptions import BusinessException
import uuid

logger = get_logger(__name__)


class LeadService:
    """线索服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = LeadRepository(db)
        self.follow_up_repository = LeadFollowUpRepository(db)
        self.note_repository = LeadNoteRepository(db)
        self.customer_level_service = CustomerLevelService(db)
    
    async def create_lead(
        self,
        request: LeadCreateRequest,
        organization_id: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> LeadResponse:
        """创建线索"""
        # 验证：线索不能关联客户，customer_id 必须为 NULL
        if request.customer_id:
            raise BusinessException(
                detail="线索不能关联客户，线索默认是未知的客户。只有转换时才会创建客户并关联。",
                status_code=400
            )
        
        # 验证客户等级代码
        if request.level:
            is_valid = await self.customer_level_service.validate_code(request.level)
            if not is_valid:
                raise BusinessException(detail=f"无效的客户等级代码: {request.level}", status_code=400)
        
        # 如果没有提供 organization_id，从创建用户的组织获取
        if not organization_id and created_by:
            organization_id = await get_user_organization_id(self.db, created_by)
            if not organization_id:
                raise BusinessException(
                    detail=f"无法获取用户 {created_by} 的组织ID，请确保用户已关联组织",
                    status_code=400
                )
        elif not organization_id:
            raise BusinessException(
                detail="缺少组织ID，且无法从用户获取",
                status_code=400
            )
        
        try:
            # 如果没有提供 owner_user_id，则默认设置为创建人（线索与用户绑定）
            owner_user_id = request.owner_user_id or created_by
            
            lead = Lead(
                id=str(uuid.uuid4()),
                name=request.name,
                company_name=request.company_name,
                contact_name=request.contact_name,
                phone=request.phone,
                email=request.email,
                address=request.address,
                customer_id=None,  # 线索不能关联客户，必须为 NULL
                organization_id=organization_id,  # 现在确保不为 None
                owner_user_id=owner_user_id,  # 使用默认值或请求值
                status=request.status,
                level=request.level,
                next_follow_up_at=request.next_follow_up_at,
                created_by=created_by,
            )
            
            await self.repository.create(lead)
            await self.db.commit()
            await self.db.refresh(lead)
            
            # 填充客户等级双语名称
            response = LeadResponse.model_validate(lead)
            if lead.level:
                level_info = await self.customer_level_service.get_by_code(lead.level)
                if level_info:
                    response.level_name_zh = level_info["name_zh"]
                    response.level_name_id = level_info["name_id"]
            
            return response
        except Exception as e:
            await self.db.rollback()
            logger.error(f"创建线索失败: {e}", exc_info=True)
            raise BusinessException(detail=f"创建线索失败: {str(e)}")
    
    async def get_lead(
        self,
        lead_id: str,
        organization_id: Optional[str] = None,
        current_user_id: Optional[str] = None,
        current_user_roles: Optional[List[str]] = None,
    ) -> LeadResponse:
        """获取线索详情（organization_id可选）"""
        lead = await self.repository.get_by_id(lead_id, organization_id)
        if not lead:
            raise BusinessException(detail="线索不存在", status_code=404)
        
        # 数据隔离检查：非admin用户只能看自己的线索
        if current_user_roles and "ADMIN" not in current_user_roles:
            if lead.owner_user_id != current_user_id:
                raise BusinessException(detail="无权访问该线索", status_code=403)
        
        # 填充客户等级双语名称和负责人用户名
        response = LeadResponse.model_validate(lead)
        if lead.level:
            level_info = await self.customer_level_service.get_by_code(lead.level)
            if level_info:
                response.level_name_zh = level_info["name_zh"]
                response.level_name_id = level_info["name_id"]
        # 填充负责人用户名
        if lead.owner_user_id and lead.owner:
            # 优先使用 display_name，如果没有则使用 username
            response.owner_username = lead.owner.display_name or lead.owner.username
        
        return response
    
    async def get_lead_list(
        self,
        organization_id: Optional[str] = None,
        page: int = 1,
        size: int = 20,
        owner_user_id: Optional[str] = None,
        status: Optional[str] = None,
        is_in_public_pool: Optional[bool] = None,
        customer_id: Optional[str] = None,
        company_name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        current_user_id: Optional[str] = None,
        current_user_roles: Optional[List[str]] = None,
    ) -> LeadListResponse:
        """获取线索列表（organization_id可选，如果没有则只根据用户ID查询）"""
        leads, total = await self.repository.get_list(
            organization_id=organization_id,
            page=page,
            size=size,
            owner_user_id=owner_user_id,
            status=status,
            is_in_public_pool=is_in_public_pool,
            customer_id=customer_id,
            company_name=company_name,
            phone=phone,
            email=email,
            current_user_id=current_user_id,
            current_user_roles=current_user_roles,
        )
        
        # 填充客户等级双语名称和负责人用户名
        items = []
        for lead in leads:
            response = LeadResponse.model_validate(lead)
            if lead.level:
                level_info = await self.customer_level_service.get_by_code(lead.level)
                if level_info:
                    response.level_name_zh = level_info["name_zh"]
                    response.level_name_id = level_info["name_id"]
            # 填充负责人用户名
            if lead.owner_user_id and lead.owner:
                # 优先使用 display_name，如果没有则使用 username
                response.owner_username = lead.owner.display_name or lead.owner.username
            items.append(response)
        
        return LeadListResponse(
            items=items,
            total=total,
            page=page,
            size=size,
        )
    
    async def update_lead(
        self,
        lead_id: str,
        request: LeadUpdateRequest,
        organization_id: Optional[str] = None,
        updated_by: Optional[str] = None,
        current_user_id: Optional[str] = None,
        current_user_roles: Optional[List[str]] = None,
    ) -> LeadResponse:
        """更新线索（organization_id可选）"""
        lead = await self.repository.get_by_id(lead_id, organization_id)
        if not lead:
            raise BusinessException(detail="线索不存在", status_code=404)
        
        # 权限检查：非admin用户只能更新自己的线索
        if current_user_roles and "ADMIN" not in current_user_roles:
            if lead.owner_user_id != current_user_id:
                raise BusinessException(detail="无权更新该线索", status_code=403)
        
        # 验证：更新线索时不允许设置 customer_id（除非通过转换API）
        if request.customer_id is not None:
            raise BusinessException(
                detail="更新线索时不允许设置 customer_id。线索不能关联客户，只有通过转换API才能设置 customer_id。",
                status_code=400
            )
        
        # 验证客户等级代码（如果更新了level字段）
        if request.level is not None:
            is_valid = await self.customer_level_service.validate_code(request.level)
            if not is_valid:
                raise BusinessException(detail=f"无效的客户等级代码: {request.level}", status_code=400)
        
        # 更新字段（排除 customer_id）
        update_data = request.model_dump(exclude_unset=True, exclude={'customer_id'})
        for key, value in update_data.items():
            setattr(lead, key, value)
        
        lead.updated_by = updated_by
        await self.db.commit()
        await self.db.refresh(lead)
        
        # 填充客户等级双语名称
        response = LeadResponse.model_validate(lead)
        if lead.level:
            level_info = await self.customer_level_service.get_by_code(lead.level)
            if level_info:
                response.level_name_zh = level_info["name_zh"]
                response.level_name_id = level_info["name_id"]
        
        return response
    
    async def delete_lead(
        self,
        lead_id: str,
        organization_id: Optional[str] = None,
        current_user_id: Optional[str] = None,
        current_user_roles: Optional[List[str]] = None,
    ) -> None:
        """删除线索
        
        权限控制：
        1. 管理员可以删除任何线索
        2. 非管理员可以删除：
           - 自己负责的线索（owner_user_id == current_user_id）
           - 自己创建的线索（created_by == current_user_id）
        """
        # 查询线索
        lead = await self.repository.get_by_id(lead_id, organization_id)
        if not lead:
            raise BusinessException(detail="线索不存在", status_code=404)
        
        # 权限检查
        is_admin = current_user_roles and "ADMIN" in current_user_roles
        
        if not is_admin:
            # 非管理员：只能删除自己负责的或自己创建的线索
            if not current_user_id:
                raise BusinessException(detail="需要认证", status_code=401)
            
            can_delete = False
            if lead.owner_user_id == current_user_id:
                # 自己负责的线索
                can_delete = True
            elif lead.created_by == current_user_id:
                # 自己创建的线索
                can_delete = True
            
            if not can_delete:
                raise BusinessException(
                    detail="无权删除该线索，只能删除自己负责的或自己创建的线索",
                    status_code=403
                )
        
        # 执行删除
        await self.repository.delete(lead)
        await self.db.commit()
    
    async def move_to_pool(
        self,
        lead_id: str,
        pool_id: Optional[str],
        organization_id: str,
        current_user_id: Optional[str] = None,
        current_user_roles: Optional[List[str]] = None,
    ) -> LeadResponse:
        """移入公海池"""
        lead = await self.repository.get_by_id(lead_id, organization_id)
        if not lead:
            raise BusinessException(detail="线索不存在", status_code=404)
        
        # 权限检查：只有负责人或admin可以移入公海池
        if current_user_roles and "ADMIN" not in current_user_roles:
            if lead.owner_user_id != current_user_id:
                raise BusinessException(detail="无权操作该线索", status_code=403)
        
        updated_lead = await self.repository.move_to_pool(lead_id, organization_id, pool_id)
        if not updated_lead:
            raise BusinessException(detail="移入公海池失败", status_code=500)
        
        # 填充客户等级双语名称
        response = LeadResponse.model_validate(updated_lead)
        if updated_lead.level:
            level_info = await self.customer_level_service.get_by_code(updated_lead.level)
            if level_info:
                response.level_name_zh = level_info["name_zh"]
                response.level_name_id = level_info["name_id"]
        
        return response
    
    async def assign_lead(
        self,
        lead_id: str,
        owner_user_id: str,
        organization_id: str,
        current_user_id: Optional[str] = None,
        current_user_roles: Optional[List[str]] = None,
    ) -> LeadResponse:
        """分配线索"""
        lead = await self.repository.get_by_id(lead_id, organization_id)
        if not lead:
            raise BusinessException(detail="线索不存在", status_code=404)
        
        # 权限检查：
        # 1. ADMIN 可以分配线索给任何人
        # 2. 普通用户可以将线索分配给自己（从公海转化线索）
        is_admin = current_user_roles and "ADMIN" in current_user_roles
        is_self_assignment = current_user_id and owner_user_id == current_user_id
        
        if not is_admin and not is_self_assignment:
            raise BusinessException(detail="只有管理员可以分配线索给他人，或可以将线索分配给自己", status_code=403)
        
        updated_lead = await self.repository.assign(lead_id, organization_id, owner_user_id)
        if not updated_lead:
            raise BusinessException(detail="分配线索失败", status_code=500)
        
        # 填充客户等级双语名称
        response = LeadResponse.model_validate(updated_lead)
        if updated_lead.level:
            level_info = await self.customer_level_service.get_by_code(updated_lead.level)
            if level_info:
                response.level_name_zh = level_info["name_zh"]
                response.level_name_id = level_info["name_id"]
        
        return response

