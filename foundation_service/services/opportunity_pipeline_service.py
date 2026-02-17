"""
商机流水线服务
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import uuid

from common.models.pipeline_config import PipelineConfig, PipelineStage
from common.models.opportunity_pipeline_log import OpportunityPipelineLog, StageStatus
from common.models.opportunity import Opportunity
from common.exceptions import BusinessException
from common.utils.logger import get_logger
from foundation_service.schemas.opportunity_pipeline import (
    PipelineStageResponse,
    PipelineLogResponse,
    StartPipelineRequest,
    CompleteStageRequest,
    ApproveStageRequest,
    AssignStageRequest,
    PipelineProgressResponse,
    PipelineHistoryResponse,
)
from foundation_service.services.pipeline_action_service import PipelineActionService

logger = get_logger(__name__)


class OpportunityPipelineService:
    """商机流水线服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def start_pipeline(
        self,
        opportunity_id: str,
        request: StartPipelineRequest,
        current_user_id: str
    ) -> PipelineProgressResponse:
        """启动流水线"""
        logger.info(f"启动商机流水线: opportunity_id={opportunity_id}, pipeline_id={request.pipeline_id}")

        # --- 新增：启动流水线前计算 service_scope ---
        from foundation_service.services.opportunity_service import OpportunityService
        opp_service = OpportunityService(self.db)
        service_scope = await opp_service.compute_and_update_service_scope(opportunity_id)
        logger.info(f"商机 {opportunity_id} 的 service_scope 已更新为: {service_scope}")

        # 验证商机是否存在
        stmt = select(Opportunity).where(Opportunity.id == opportunity_id)
        result = await self.db.execute(stmt)
        opportunity = result.scalar_one_or_none()
        if not opportunity:
            raise BusinessException(detail="商机不存在", status_code=404)

        # 验证流水线是否存在
        stmt = select(PipelineConfig).where(
            and_(
                PipelineConfig.id == request.pipeline_id,
                PipelineConfig.is_active == True
            )
        )
        result = await self.db.execute(stmt)
        pipeline = result.scalar_one_or_none()
        if not pipeline:
            raise BusinessException(detail="流水线不存在或未启用", status_code=404)

        # 检查是否已启动流水线
        stmt = select(OpportunityPipelineLog).where(
            OpportunityPipelineLog.opportunity_id == opportunity_id
        )
        result = await self.db.execute(stmt)
        existing_logs = result.scalars().all()
        if existing_logs:
            raise BusinessException(detail="商机已启动流水线，不能重复启动")

        # 获取所有阶段
        stmt = select(PipelineStage).where(
            PipelineStage.pipeline_id == request.pipeline_id
        ).order_by(PipelineStage.order)
        result = await self.db.execute(stmt)
        stages = result.scalars().all()

        if not stages:
            raise BusinessException(detail="流水线没有配置阶段")

        # 找到第一个阶段（没有父阶段的阶段）
        first_stage = None
        for stage in stages:
            if stage.parent_id is None:
                first_stage = stage
                break

        if not first_stage:
            raise BusinessException(detail="流水线配置错误：找不到起始阶段")

        # 创建第一个阶段的日志
        log = OpportunityPipelineLog(
            id=str(uuid.uuid4()),
            opportunity_id=opportunity_id,
            pipeline_id=request.pipeline_id,
            stage_id=first_stage.id,
            stage_name=first_stage.name,
            stage_type=first_stage.stage_type.value,
            status=StageStatus.PROCESSING,
            parallel_group=first_stage.parallel_group,
            entered_at=func.now(),
            started_at=func.now(),
            notes=request.initial_notes,
            created_by=current_user_id,
            updated_by=current_user_id,
        )
        self.db.add(log)
        await self.db.flush()

        # 初始化第一个阶段的所有动作
        action_service = PipelineActionService(self.db)
        await action_service.initialize_stage_actions(
            opportunity_id=opportunity_id,
            pipeline_log_id=log.id,
            stage_id=first_stage.id,
            current_user_id=current_user_id
        )

        await self.db.commit()

        logger.info(f"流水线启动成功: opportunity_id={opportunity_id}, first_stage={first_stage.name}")

        return await self.get_pipeline_progress(opportunity_id)

    async def complete_stage(
        self,
        opportunity_id: str,
        stage_id: str,
        request: CompleteStageRequest,
        current_user_id: str
    ) -> PipelineProgressResponse:
        """完成阶段"""
        logger.info(f"完成阶段: opportunity_id={opportunity_id}, stage_id={stage_id}")

        # 获取当前阶段日志
        stmt = select(OpportunityPipelineLog).where(
            and_(
                OpportunityPipelineLog.opportunity_id == opportunity_id,
                OpportunityPipelineLog.stage_id == stage_id
            )
        )
        result = await self.db.execute(stmt)
        log = result.scalar_one_or_none()

        if not log:
            raise BusinessException(detail="阶段日志不存在", status_code=404)

        if log.status == StageStatus.COMPLETED:
            raise BusinessException(detail="阶段已完成，不能重复完成")

        # 检查所有必需动作是否已完成
        action_service = PipelineActionService(self.db)
        can_complete = await action_service.check_stage_completion(
            opportunity_id=opportunity_id,
            stage_id=stage_id
        )

        if not can_complete:
            raise BusinessException(detail="阶段还有未完成的必需动作，无法完成阶段")

        # 更新日志状态
        log.status = StageStatus.COMPLETED
        log.completed_at = func.now()
        if log.started_at:
            duration = (datetime.now() - log.started_at).total_seconds() / 60
            log.duration_minutes = int(duration)
        if request.notes:
            log.notes = request.notes
        if request.extra_data:
            log.extra_data = request.extra_data
        log.updated_by = current_user_id

        await self.db.commit()

        # 自动推进到下一阶段
        await self._auto_proceed_to_next_stage(opportunity_id, stage_id, current_user_id)

        logger.info(f"阶段完成成功: opportunity_id={opportunity_id}, stage_id={stage_id}")

        return await self.get_pipeline_progress(opportunity_id)

    async def approve_stage(
        self,
        opportunity_id: str,
        stage_id: str,
        request: ApproveStageRequest,
        current_user_id: str
    ) -> PipelineProgressResponse:
        """审批阶段"""
        logger.info(f"审批阶段: opportunity_id={opportunity_id}, stage_id={stage_id}, approved={request.approved}")

        # 获取当前阶段日志
        stmt = select(OpportunityPipelineLog).where(
            and_(
                OpportunityPipelineLog.opportunity_id == opportunity_id,
                OpportunityPipelineLog.stage_id == stage_id
            )
        )
        result = await self.db.execute(stmt)
        log = result.scalar_one_or_none()

        if not log:
            raise BusinessException(detail="阶段日志不存在", status_code=404)

        if log.status == StageStatus.COMPLETED:
            raise BusinessException(detail="阶段已完成，不能重复审批")

        # 更新审批信息
        log.approver_id = current_user_id
        log.approved_at = func.now()
        log.approval_notes = request.approval_notes

        if request.approved:
            log.status = StageStatus.COMPLETED
            log.completed_at = func.now()
            if log.started_at:
                duration = (datetime.now() - log.started_at).total_seconds() / 60
                log.duration_minutes = int(duration)
        else:
            log.status = StageStatus.REJECTED

        log.updated_by = current_user_id

        await self.db.commit()

        # 如果审批通过，自动推进到下一阶段
        if request.approved:
            await self._auto_proceed_to_next_stage(opportunity_id, stage_id, current_user_id)

        logger.info(f"阶段审批成功: opportunity_id={opportunity_id}, stage_id={stage_id}, approved={request.approved}")

        return await self.get_pipeline_progress(opportunity_id)

    async def assign_stage(
        self,
        opportunity_id: str,
        stage_id: str,
        request: AssignStageRequest,
        current_user_id: str
    ) -> PipelineProgressResponse:
        """分配阶段"""
        logger.info(f"分配阶段: opportunity_id={opportunity_id}, stage_id={stage_id}, assigned_to={request.assigned_to}")

        # 获取当前阶段日志
        stmt = select(OpportunityPipelineLog).where(
            and_(
                OpportunityPipelineLog.opportunity_id == opportunity_id,
                OpportunityPipelineLog.stage_id == stage_id
            )
        )
        result = await self.db.execute(stmt)
        log = result.scalar_one_or_none()

        if not log:
            raise BusinessException(detail="阶段日志不存在", status_code=404)

        # 更新分配信息
        log.assigned_to = request.assigned_to
        if request.notes:
            log.notes = request.notes
        log.updated_by = current_user_id

        await self.db.commit()

        logger.info(f"阶段分配成功: opportunity_id={opportunity_id}, stage_id={stage_id}")

        return await self.get_pipeline_progress(opportunity_id)

    async def get_pipeline_progress(self, opportunity_id: str) -> PipelineProgressResponse:
        """获取流水线进度"""
        logger.debug(f"获取流水线进度: opportunity_id={opportunity_id}")

        # 获取所有日志
        stmt = select(OpportunityPipelineLog).where(
            OpportunityPipelineLog.opportunity_id == opportunity_id
        ).order_by(OpportunityPipelineLog.entered_at)
        result = await self.db.execute(stmt)
        logs = result.scalars().all()

        if not logs:
            raise BusinessException(detail="商机未启动流水线", status_code=404)

        pipeline_id = logs[0].pipeline_id

        # 获取流水线配置
        stmt = select(PipelineConfig).where(PipelineConfig.id == pipeline_id)
        result = await self.db.execute(stmt)
        pipeline = result.scalar_one_or_none()

        if not pipeline:
            raise BusinessException(detail="流水线配置不存在", status_code=404)

        # 获取所有阶段
        stmt = select(PipelineStage).where(
            PipelineStage.pipeline_id == pipeline_id
        ).order_by(PipelineStage.order)
        result = await self.db.execute(stmt)
        all_stages = result.scalars().all()

        # 分类日志
        current_stages = []
        completed_stages = []
        for log in logs:
            log_response = PipelineLogResponse.model_validate(log)
            if log.status in [StageStatus.PROCESSING, StageStatus.PENDING]:
                current_stages.append(log_response)
            elif log.status == StageStatus.COMPLETED:
                completed_stages.append(log_response)

        # 找出待处理的阶段
        completed_stage_ids = {log.stage_id for log in logs if log.status == StageStatus.COMPLETED}
        pending_stages = []
        for stage in all_stages:
            if stage.id not in {log.stage_id for log in logs}:
                pending_stages.append(PipelineStageResponse.model_validate(stage))

        # 计算进度
        total_stages = len(all_stages)
        completed_count = len(completed_stages)
        progress_percentage = (completed_count / total_stages * 100) if total_stages > 0 else 0
        is_completed = completed_count == total_stages

        # 检查是否有并行阶段
        has_parallel_stages = any(stage.parallel_group for stage in all_stages)

        return PipelineProgressResponse(
            opportunity_id=opportunity_id,
            pipeline_id=pipeline_id,
            pipeline_name=pipeline.name,
            current_stages=current_stages,
            completed_stages=completed_stages,
            pending_stages=pending_stages,
            total_stages=total_stages,
            completed_count=completed_count,
            progress_percentage=round(progress_percentage, 2),
            is_completed=is_completed,
            has_parallel_stages=has_parallel_stages,
        )

    async def get_pipeline_history(
        self,
        opportunity_id: str,
        page: int = 1,
        size: int = 20
    ) -> PipelineHistoryResponse:
        """获取流水线历史"""
        logger.debug(f"获取流水线历史: opportunity_id={opportunity_id}, page={page}, size={size}")

        # 查询总数
        stmt = select(func.count()).select_from(OpportunityPipelineLog).where(
            OpportunityPipelineLog.opportunity_id == opportunity_id
        )
        result = await self.db.execute(stmt)
        total = result.scalar()

        # 查询日志
        stmt = select(OpportunityPipelineLog).where(
            OpportunityPipelineLog.opportunity_id == opportunity_id
        ).order_by(OpportunityPipelineLog.entered_at.desc()).offset((page - 1) * size).limit(size)
        result = await self.db.execute(stmt)
        logs = result.scalars().all()

        log_responses = [PipelineLogResponse.model_validate(log) for log in logs]

        return PipelineHistoryResponse(
            logs=log_responses,
            total=total,
        )

    async def _auto_proceed_to_next_stage(
        self,
        opportunity_id: str,
        completed_stage_id: str,
        current_user_id: str
    ):
        """自动推进到下一阶段"""
        logger.debug(f"自动推进到下一阶段: opportunity_id={opportunity_id}, completed_stage_id={completed_stage_id}")

        # 获取已完成的阶段
        stmt = select(PipelineStage).where(PipelineStage.id == completed_stage_id)
        result = await self.db.execute(stmt)
        completed_stage = result.scalar_one_or_none()

        if not completed_stage:
            logger.warning(f"已完成的阶段不存在: stage_id={completed_stage_id}")
            return

        # 获取所有阶段
        stmt = select(PipelineStage).where(
            PipelineStage.pipeline_id == completed_stage.pipeline_id
        ).order_by(PipelineStage.order)
        result = await self.db.execute(stmt)
        all_stages = result.scalars().all()

        # 找到下一个阶段（parent_id 指向当前阶段的阶段）
        next_stages = [stage for stage in all_stages if stage.parent_id == completed_stage_id]

        if not next_stages:
            logger.info(f"没有下一阶段，流水线结束: opportunity_id={opportunity_id}")
            return

        # 如果下一阶段是并行组，创建所有并行阶段的日志
        if next_stages[0].parallel_group:
            parallel_group = next_stages[0].parallel_group
            parallel_stages = [stage for stage in next_stages if stage.parallel_group == parallel_group]

            for stage in parallel_stages:
                # 检查是否已存在日志
                stmt = select(OpportunityPipelineLog).where(
                    and_(
                        OpportunityPipelineLog.opportunity_id == opportunity_id,
                        OpportunityPipelineLog.stage_id == stage.id
                    )
                )
                result = await self.db.execute(stmt)
                existing_log = result.scalar_one_or_none()

                if not existing_log:
                    log = OpportunityPipelineLog(
                        id=str(uuid.uuid4()),
                        opportunity_id=opportunity_id,
                        pipeline_id=completed_stage.pipeline_id,
                        stage_id=stage.id,
                        stage_name=stage.name,
                        stage_type=stage.stage_type.value,
                        status=StageStatus.PROCESSING,
                        parallel_group=stage.parallel_group,
                        entered_at=func.now(),
                        started_at=func.now(),
                        created_by=current_user_id,
                        updated_by=current_user_id,
                    )
                    self.db.add(log)
                    await self.db.flush()

                    # 初始化该阶段的所有动作
                    action_service = PipelineActionService(self.db)
                    await action_service.initialize_stage_actions(
                        opportunity_id=opportunity_id,
                        pipeline_log_id=log.id,
                        stage_id=stage.id,
                        current_user_id=current_user_id
                    )

            await self.db.commit()
            logger.info(f"创建并行阶段日志: opportunity_id={opportunity_id}, parallel_group={parallel_group}, count={len(parallel_stages)}")

        else:
            # 单个下一阶段
            next_stage = next_stages[0]

            # 检查是否已存在日志
            stmt = select(OpportunityPipelineLog).where(
                and_(
                    OpportunityPipelineLog.opportunity_id == opportunity_id,
                    OpportunityPipelineLog.stage_id == next_stage.id
                )
            )
            result = await self.db.execute(stmt)
            existing_log = result.scalar_one_or_none()

            if not existing_log:
                log = OpportunityPipelineLog(
                    id=str(uuid.uuid4()),
                    opportunity_id=opportunity_id,
                    pipeline_id=completed_stage.pipeline_id,
                    stage_id=next_stage.id,
                    stage_name=next_stage.name,
                    stage_type=next_stage.stage_type.value,
                    status=StageStatus.PROCESSING if not next_stage.auto_proceed else StageStatus.PENDING,
                    parallel_group=next_stage.parallel_group,
                    entered_at=func.now(),
                    started_at=func.now() if not next_stage.auto_proceed else None,
                    created_by=current_user_id,
                    updated_by=current_user_id,
                )
                self.db.add(log)
                await self.db.flush()

                # 初始化该阶段的所有动作
                action_service = PipelineActionService(self.db)
                await action_service.initialize_stage_actions(
                    opportunity_id=opportunity_id,
                    pipeline_log_id=log.id,
                    stage_id=next_stage.id,
                    current_user_id=current_user_id
                )

                await self.db.commit()

                logger.info(f"创建下一阶段日志: opportunity_id={opportunity_id}, next_stage={next_stage.name}")

                # 如果是自动推进的阶段，立即完成
                if next_stage.auto_proceed:
                    await self.complete_stage(
                        opportunity_id=opportunity_id,
                        stage_id=next_stage.id,
                        request=CompleteStageRequest(notes="系统自动完成"),
                        current_user_id=current_user_id
                    )
