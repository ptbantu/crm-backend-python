"""
商机阶段管理服务
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import json
import uuid

from common.models.opportunity import Opportunity
from common.models.opportunity_stage_template import OpportunityStageTemplate
from common.models.opportunity_stage_history import OpportunityStageHistory
from foundation_service.repositories.opportunity_stage_template_repository import OpportunityStageTemplateRepository
from foundation_service.repositories.opportunity_stage_history_repository import OpportunityStageHistoryRepository
from foundation_service.repositories.opportunity_repository import OpportunityRepository
from foundation_service.schemas.opportunity_stage import (
    StageTemplateResponse,
    StageHistoryResponse,
    StageTransitionRequest,
    StageApprovalRequest,
)
from common.utils.logger import get_logger
from common.exceptions import BusinessException

logger = get_logger(__name__)


class OpportunityStageService:
    """商机阶段管理服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.stage_template_repo = OpportunityStageTemplateRepository(db)
        self.stage_history_repo = OpportunityStageHistoryRepository(db)
        self.opportunity_repo = OpportunityRepository(db)
    
    async def get_all_stage_templates(self) -> List[StageTemplateResponse]:
        """获取所有阶段模板"""
        templates = await self.stage_template_repo.get_all_active()
        return [
            StageTemplateResponse(
                id=template.id,
                code=template.code,
                name_zh=template.name_zh,
                name_id=template.name_id,
                description_zh=template.description_zh,
                description_id=template.description_id,
                stage_order=template.stage_order,
                requires_approval=template.requires_approval,
                approval_roles_json=template.approval_roles_json,
                conditions_json=template.conditions_json,
                is_active=template.is_active,
                created_at=template.created_at,
                updated_at=template.updated_at,
                created_by=template.created_by,
                updated_by=template.updated_by,
            )
            for template in templates
        ]
    
    async def get_stage_template_by_code(self, code: str) -> Optional[StageTemplateResponse]:
        """根据代码获取阶段模板"""
        template = await self.stage_template_repo.get_by_code(code)
        if not template:
            return None
        
        return StageTemplateResponse(
            id=template.id,
            code=template.code,
            name_zh=template.name_zh,
            name_id=template.name_id,
            description_zh=template.description_zh,
            description_id=template.description_id,
            stage_order=template.stage_order,
            requires_approval=template.requires_approval,
            approval_roles_json=template.approval_roles_json,
            conditions_json=template.conditions_json,
            is_active=template.is_active,
            created_at=template.created_at,
            updated_at=template.updated_at,
            created_by=template.created_by,
            updated_by=template.updated_by,
        )
    
    async def get_stage_history(
        self,
        opportunity_id: str,
        include_current: bool = True
    ) -> List[StageHistoryResponse]:
        """获取商机阶段历史"""
        histories = await self.stage_history_repo.get_by_opportunity_id(
            opportunity_id,
            include_current=include_current
        )
        
        return [
            StageHistoryResponse(
                id=history.id,
                opportunity_id=history.opportunity_id,
                stage_id=history.stage_id,
                stage_code=history.stage_template.code if history.stage_template else None,
                stage_name_zh=history.stage_template.name_zh if history.stage_template else None,
                entered_at=history.entered_at,
                exited_at=history.exited_at,
                duration_days=history.duration_days,
                conditions_met_json=history.conditions_met_json,
                requires_approval=history.requires_approval,
                approval_status=history.approval_status,
                approved_by=history.approved_by,
                approval_at=history.approval_at,
                approval_notes=history.approval_notes,
                created_at=history.created_at,
            )
            for history in histories
        ]
    
    async def get_current_stage(self, opportunity_id: str) -> Optional[StageHistoryResponse]:
        """获取当前阶段"""
        history = await self.stage_history_repo.get_current_stage(opportunity_id)
        if not history:
            return None
        
        return StageHistoryResponse(
            id=history.id,
            opportunity_id=history.opportunity_id,
            stage_id=history.stage_id,
            stage_code=history.stage_template.code if history.stage_template else None,
            stage_name_zh=history.stage_template.name_zh if history.stage_template else None,
            entered_at=history.entered_at,
            exited_at=history.exited_at,
            duration_days=history.duration_days,
            conditions_met_json=history.conditions_met_json,
            requires_approval=history.requires_approval,
            approval_status=history.approval_status,
            approved_by=history.approved_by,
            approval_at=history.approval_at,
            approval_notes=history.approval_notes,
            created_at=history.created_at,
        )
    
    async def check_transition_conditions(
        self,
        opportunity_id: str,
        target_stage_id: str
    ) -> tuple[bool, List[str]]:
        """检查推进条件是否满足"""
        opportunity = await self.opportunity_repo.get_by_id(opportunity_id)
        if not opportunity:
            raise BusinessException(detail="商机不存在", status_code=404)
        
        target_stage = await self.stage_template_repo.get_by_id(target_stage_id)
        if not target_stage:
            raise BusinessException(detail="目标阶段不存在", status_code=404)
        
        # 获取当前阶段
        current_stage = None
        if opportunity.current_stage_id:
            current_stage = await self.stage_template_repo.get_by_id(opportunity.current_stage_id)
        
        # 检查阶段顺序
        if current_stage:
            if target_stage.stage_order <= current_stage.stage_order:
                return False, ["不能回退到之前的阶段"]
        
        # 检查推进条件
        if target_stage.conditions_json:
            missing_conditions = []
            conditions = target_stage.conditions_json
            
            # 这里可以根据具体的条件进行验证
            # 例如：检查是否有报价单、合同等
            # 实际实现需要根据业务需求进行扩展
            
            if missing_conditions:
                return False, missing_conditions
        
        return True, []
    
    async def transition_stage(
        self,
        request: StageTransitionRequest,
        user_id: Optional[str] = None
    ) -> StageHistoryResponse:
        """推进阶段"""
        opportunity = await self.opportunity_repo.get_by_id(request.opportunity_id)
        if not opportunity:
            raise BusinessException(detail="商机不存在", status_code=404)
        
        # 确定目标阶段
        target_stage_id = request.target_stage_id
        if not target_stage_id:
            # 如果没有指定目标阶段，推进到下一阶段
            current_stage = None
            if opportunity.current_stage_id:
                current_stage = await self.stage_template_repo.get_by_id(opportunity.current_stage_id)
            
            if current_stage:
                next_stage = await self.stage_template_repo.get_next_stage(current_stage.stage_order)
                if not next_stage:
                    raise BusinessException(detail="已经是最后阶段，无法继续推进", status_code=400)
                target_stage_id = next_stage.id
            else:
                # 如果没有当前阶段，获取第一个阶段
                first_stage = await self.stage_template_repo.get_by_order(1)
                if not first_stage:
                    raise BusinessException(detail="没有可用的阶段模板", status_code=500)
                target_stage_id = first_stage.id
        
        # 检查推进条件
        can_transition, missing_conditions = await self.check_transition_conditions(
            request.opportunity_id,
            target_stage_id
        )
        if not can_transition:
            raise BusinessException(
                detail=f"推进条件不满足：{', '.join(missing_conditions)}",
                status_code=400
            )
        
        target_stage = await self.stage_template_repo.get_by_id(target_stage_id)
        if not target_stage:
            raise BusinessException(detail="目标阶段不存在", status_code=404)
        
        try:
            # 标记旧阶段退出
            current_history = await self.stage_history_repo.get_current_stage(request.opportunity_id)
            if current_history:
                current_history.exited_at = datetime.now()
                await self.db.flush()
            
            # 创建新阶段历史记录
            new_history = OpportunityStageHistory(
                id=str(uuid.uuid4()),
                opportunity_id=request.opportunity_id,
                stage_id=target_stage_id,
                conditions_met_json=request.conditions_met_json,
                requires_approval=target_stage.requires_approval,
                approval_status="pending" if target_stage.requires_approval else None,
            )
            await self.db.add(new_history)
            
            # 更新商机的当前阶段
            opportunity.current_stage_id = target_stage_id
            if not opportunity.workflow_status:
                opportunity.workflow_status = "active"
            
            await self.db.commit()
            await self.db.refresh(new_history)
            
            # 加载关联数据
            await self.db.refresh(new_history, ["stage_template"])
            
            return StageHistoryResponse(
                id=new_history.id,
                opportunity_id=new_history.opportunity_id,
                stage_id=new_history.stage_id,
                stage_code=new_history.stage_template.code if new_history.stage_template else None,
                stage_name_zh=new_history.stage_template.name_zh if new_history.stage_template else None,
                entered_at=new_history.entered_at,
                exited_at=new_history.exited_at,
                duration_days=new_history.duration_days,
                conditions_met_json=new_history.conditions_met_json,
                requires_approval=new_history.requires_approval,
                approval_status=new_history.approval_status,
                approved_by=new_history.approved_by,
                approval_at=new_history.approval_at,
                approval_notes=new_history.approval_notes,
                created_at=new_history.created_at,
            )
        except Exception as e:
            await self.db.rollback()
            logger.error(f"推进阶段失败: {e}", exc_info=True)
            raise BusinessException(detail=f"推进阶段失败: {str(e)}")
    
    async def approve_stage(
        self,
        request: StageApprovalRequest,
        approver_id: str
    ) -> StageHistoryResponse:
        """审批阶段"""
        history = await self.stage_history_repo.get_by_id(request.stage_history_id)
        if not history:
            raise BusinessException(detail="阶段历史记录不存在", status_code=404)
        
        if not history.requires_approval:
            raise BusinessException(detail="该阶段不需要审批", status_code=400)
        
        if history.approval_status != "pending":
            raise BusinessException(detail="该阶段已经审批过了", status_code=400)
        
        try:
            history.approval_status = request.approval_status
            history.approved_by = approver_id
            history.approval_at = datetime.now()
            history.approval_notes = request.approval_notes
            
            await self.db.commit()
            await self.db.refresh(history)
            
            # 加载关联数据
            await self.db.refresh(history, ["stage_template", "approver"])
            
            return StageHistoryResponse(
                id=history.id,
                opportunity_id=history.opportunity_id,
                stage_id=history.stage_id,
                stage_code=history.stage_template.code if history.stage_template else None,
                stage_name_zh=history.stage_template.name_zh if history.stage_template else None,
                entered_at=history.entered_at,
                exited_at=history.exited_at,
                duration_days=history.duration_days,
                conditions_met_json=history.conditions_met_json,
                requires_approval=history.requires_approval,
                approval_status=history.approval_status,
                approved_by=history.approved_by,
                approval_at=history.approval_at,
                approval_notes=history.approval_notes,
                created_at=history.created_at,
            )
        except Exception as e:
            await self.db.rollback()
            logger.error(f"审批阶段失败: {e}", exc_info=True)
            raise BusinessException(detail=f"审批阶段失败: {str(e)}")
    
    async def get_pending_approvals(
        self,
        opportunity_id: Optional[str] = None
    ) -> List[StageHistoryResponse]:
        """获取待审批的阶段历史记录"""
        histories = await self.stage_history_repo.get_pending_approvals(opportunity_id)
        
        return [
            StageHistoryResponse(
                id=history.id,
                opportunity_id=history.opportunity_id,
                stage_id=history.stage_id,
                stage_code=history.stage_template.code if history.stage_template else None,
                stage_name_zh=history.stage_template.name_zh if history.stage_template else None,
                entered_at=history.entered_at,
                exited_at=history.exited_at,
                duration_days=history.duration_days,
                conditions_met_json=history.conditions_met_json,
                requires_approval=history.requires_approval,
                approval_status=history.approval_status,
                approved_by=history.approved_by,
                approval_at=history.approval_at,
                approval_notes=history.approval_notes,
                created_at=history.created_at,
            )
            for history in histories
        ]
