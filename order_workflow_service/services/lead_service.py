"""
线索服务
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from order_workflow_service.models.lead import Lead
from order_workflow_service.repositories.lead_repository import LeadRepository
from order_workflow_service.repositories.lead_follow_up_repository import LeadFollowUpRepository
from order_workflow_service.repositories.lead_note_repository import LeadNoteRepository
from order_workflow_service.services.customer_level_service import CustomerLevelService
from order_workflow_service.schemas.lead import (
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
        # 验证客户等级代码
        if request.level:
            is_valid = await self.customer_level_service.validate_code(request.level)
            if not is_valid:
                raise BusinessException(detail=f"无效的客户等级代码: {request.level}", status_code=400)
        
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
                customer_id=request.customer_id,
                organization_id=organization_id,
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
        
        # 填充客户等级双语名称
        response = LeadResponse.model_validate(lead)
        if lead.level:
            level_info = await self.customer_level_service.get_by_code(lead.level)
            if level_info:
                response.level_name_zh = level_info["name_zh"]
                response.level_name_id = level_info["name_id"]
        
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
        
        # 填充客户等级双语名称
        items = []
        for lead in leads:
            response = LeadResponse.model_validate(lead)
            if lead.level:
                level_info = await self.customer_level_service.get_by_code(lead.level)
                if level_info:
                    response.level_name_zh = level_info["name_zh"]
                    response.level_name_id = level_info["name_id"]
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
        
        # 验证客户等级代码（如果更新了level字段）
        if request.level is not None:
            is_valid = await self.customer_level_service.validate_code(request.level)
            if not is_valid:
                raise BusinessException(detail=f"无效的客户等级代码: {request.level}", status_code=400)
        
        # 更新字段
        update_data = request.model_dump(exclude_unset=True)
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
        organization_id: str,
        current_user_id: Optional[str] = None,
        current_user_roles: Optional[List[str]] = None,
    ) -> None:
        """删除线索（仅admin）"""
        if not current_user_roles or "ADMIN" not in current_user_roles:
            raise BusinessException(detail="只有管理员可以删除线索", status_code=403)
        
        lead = await self.repository.get_by_id(lead_id, organization_id)
        if not lead:
            raise BusinessException(detail="线索不存在", status_code=404)
        
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
        
        # 权限检查：只有admin可以分配线索
        if not current_user_roles or "ADMIN" not in current_user_roles:
            raise BusinessException(detail="只有管理员可以分配线索", status_code=403)
        
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

