"""
流水线动作服务
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from common.models.pipeline_action_config import PipelineActionConfig, ActionType
from common.models.opportunity_action_log import OpportunityActionLog, ActionStatus
from common.models.opportunity_pipeline_log import OpportunityPipelineLog
from common.models.pipeline_config import PipelineStage
from common.models.opportunity import Opportunity
from common.models.opp_execution_summary import OppExecutionSummary
from foundation_service.schemas.pipeline_action import (
    ActionLogResponse,
    StageActionsResponse,
    ExecuteActionRequest,
    ApproveActionRequest,
    SkipActionRequest
)
from common.exceptions import BusinessException


class PipelineActionService:
    """流水线动作服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def initialize_stage_actions(
        self,
        opportunity_id: str,
        pipeline_log_id: str,
        stage_id: str,
        current_user_id: str
    ) -> List[OpportunityActionLog]:
        """
        阶段进入时初始化动作日志（按 service_scope 过滤）

        Args:
            opportunity_id: 商机ID
            pipeline_log_id: 流水线日志ID
            stage_id: 阶段ID
            current_user_id: 当前用户ID

        Returns:
            创建的动作日志列表
        """
        # 1. 获取商机的 service_scope
        opp_stmt = select(Opportunity).where(Opportunity.id == opportunity_id)
        opp = (await self.db.execute(opp_stmt)).scalar_one_or_none()
        service_scope = opp.service_scope or [] if opp else []

        # 2. 获取该阶段所有 action configs
        stmt = select(PipelineActionConfig).where(
            PipelineActionConfig.stage_id == stage_id
        ).order_by(PipelineActionConfig.order)
        action_configs = (await self.db.execute(stmt)).scalars().all()

        if not action_configs:
            return []

        # 3. 按 service_scope 过滤 (trigger_condition="DEFAULT" 始终包含)
        filtered_configs = [
            c for c in action_configs
            if c.trigger_condition == "DEFAULT" or c.trigger_condition in service_scope
        ]

        # 4. 为过滤后的 configs 创建 action logs（幂等检查保留）
        action_logs = []
        for config in filtered_configs:
            existing_stmt = select(OpportunityActionLog).where(
                and_(
                    OpportunityActionLog.opportunity_id == opportunity_id,
                    OpportunityActionLog.action_config_id == config.id
                )
            )
            existing = (await self.db.execute(existing_stmt)).scalar_one_or_none()

            if existing:
                action_logs.append(existing)
                continue

            action_log = OpportunityActionLog(
                id=str(uuid.uuid4()),
                opportunity_id=opportunity_id,
                pipeline_log_id=pipeline_log_id,
                action_config_id=config.id,
                action_code=config.action_code,
                action_name=config.name,
                action_type=config.action_type.value,
                status=ActionStatus.TODO,
                created_by=current_user_id
            )
            self.db.add(action_log)
            action_logs.append(action_log)

        await self.db.flush()

        # 5. 同步快照表
        await self._sync_execution_summary(opportunity_id, stage_id, filtered_configs, action_logs)
        return action_logs

    async def get_stage_actions(
        self,
        opportunity_id: str,
        stage_id: str
    ) -> StageActionsResponse:
        """
        获取阶段的所有动作及其状态

        Args:
            opportunity_id: 商机ID
            stage_id: 阶段ID

        Returns:
            阶段动作列表响应
        """
        # 获取阶段信息
        stmt = select(PipelineStage).where(PipelineStage.id == stage_id)
        result = await self.db.execute(stmt)
        stage = result.scalar_one_or_none()

        if not stage:
            raise BusinessException(detail="阶段不存在")

        # 获取该阶段的所有动作配置
        stmt = select(PipelineActionConfig).where(
            PipelineActionConfig.stage_id == stage_id
        ).order_by(PipelineActionConfig.order)
        result = await self.db.execute(stmt)
        action_configs = result.scalars().all()

        # 获取动作执行日志
        action_logs = []
        for config in action_configs:
            stmt = select(OpportunityActionLog).where(
                and_(
                    OpportunityActionLog.opportunity_id == opportunity_id,
                    OpportunityActionLog.action_config_id == config.id
                )
            )
            result = await self.db.execute(stmt)
            log = result.scalar_one_or_none()

            if log:
                action_logs.append(log)

        # 统计信息
        total_actions = len(action_configs)
        completed_actions = sum(1 for log in action_logs if log.status == ActionStatus.DONE)
        required_actions = sum(1 for config in action_configs if config.is_required)

        # 检查是否可以完成阶段
        can_complete = await self._check_can_complete_stage(action_configs, action_logs)

        return StageActionsResponse(
            stage_id=stage_id,
            stage_name=stage.name,
            actions=[ActionLogResponse.model_validate(log) for log in action_logs],
            total_actions=total_actions,
            completed_actions=completed_actions,
            required_actions=required_actions,
            can_complete_stage=can_complete
        )

    async def execute_action(
        self,
        action_id: str,
        request: ExecuteActionRequest,
        current_user_id: str
    ) -> ActionLogResponse:
        """
        执行动作（FILE/FORM类型）

        Args:
            action_id: 动作日志ID
            request: 执行请求
            current_user_id: 当前用户ID

        Returns:
            更新后的动作日志
        """
        stmt = select(OpportunityActionLog).where(OpportunityActionLog.id == action_id)
        result = await self.db.execute(stmt)
        action_log = result.scalar_one_or_none()

        if not action_log:
            raise BusinessException(detail="动作不存在")

        if action_log.status == ActionStatus.DONE:
            raise BusinessException(detail="动作已完成，无法重复执行")

        # 获取动作配置
        stmt = select(PipelineActionConfig).where(
            PipelineActionConfig.id == action_log.action_config_id
        )
        result = await self.db.execute(stmt)
        config = result.scalar_one_or_none()

        # 验证动作类型
        if config.action_type not in [ActionType.FILE, ActionType.FORM]:
            raise BusinessException(detail=f"动作类型 {config.action_type} 不支持此操作")

        # 验证规则检查
        if config.validation_rules:
            await self._validate_action_data(config.validation_rules, request.captured_data)

        # 更新动作状态
        if not action_log.started_at:
            action_log.started_at = datetime.now()

        action_log.status = ActionStatus.DONE
        action_log.finished_at = datetime.now()
        action_log.operator_id = current_user_id
        action_log.captured_data = request.captured_data
        action_log.notes = request.notes
        action_log.updated_by = current_user_id

        # 计算耗时
        if action_log.started_at and action_log.finished_at:
            duration = (action_log.finished_at - action_log.started_at).total_seconds() / 60
            action_log.duration_minutes = int(duration)

        await self.db.flush()

        # 同步快照表
        await self._sync_after_action_update(action_log, f"完成动作: {action_log.action_name}")

        await self.db.commit()
        await self.db.refresh(action_log)

        return ActionLogResponse.model_validate(action_log)

    async def approve_action(
        self,
        action_id: str,
        request: ApproveActionRequest,
        current_user_id: str
    ) -> ActionLogResponse:
        """
        审批动作（APPROVAL类型）

        Args:
            action_id: 动作日志ID
            request: 审批请求
            current_user_id: 当前用户ID

        Returns:
            更新后的动作日志
        """
        stmt = select(OpportunityActionLog).where(OpportunityActionLog.id == action_id)
        result = await self.db.execute(stmt)
        action_log = result.scalar_one_or_none()

        if not action_log:
            raise BusinessException(detail="动作不存在")

        if action_log.status == ActionStatus.DONE:
            raise BusinessException(detail="动作已完成，无法重复审批")

        # 获取动作配置
        stmt = select(PipelineActionConfig).where(
            PipelineActionConfig.id == action_log.action_config_id
        )
        result = await self.db.execute(stmt)
        config = result.scalar_one_or_none()

        # 验证动作类型
        if config.action_type != ActionType.APPROVAL:
            raise BusinessException(detail=f"动作类型 {config.action_type} 不支持审批操作")

        # 更新动作状态
        if not action_log.started_at:
            action_log.started_at = datetime.now()

        action_log.status = ActionStatus.DONE if request.approved else ActionStatus.FAILED
        action_log.finished_at = datetime.now()
        action_log.operator_id = current_user_id
        action_log.notes = request.approval_notes
        action_log.updated_by = current_user_id

        # 合并捕获数据
        captured_data = request.captured_data or {}
        captured_data["approved"] = request.approved
        captured_data["approval_notes"] = request.approval_notes
        action_log.captured_data = captured_data

        # 计算耗时
        if action_log.started_at and action_log.finished_at:
            duration = (action_log.finished_at - action_log.started_at).total_seconds() / 60
            action_log.duration_minutes = int(duration)

        await self.db.flush()

        # 同步快照表
        status_desc = "批准" if request.approved else "拒绝"
        await self._sync_after_action_update(action_log, f"{status_desc}动作: {action_log.action_name}")

        await self.db.commit()
        await self.db.refresh(action_log)

        return ActionLogResponse.model_validate(action_log)

    async def skip_action(
        self,
        action_id: str,
        request: SkipActionRequest,
        current_user_id: str
    ) -> ActionLogResponse:
        """
        跳过动作

        Args:
            action_id: 动作日志ID
            request: 跳过请求
            current_user_id: 当前用户ID

        Returns:
            更新后的动作日志
        """
        stmt = select(OpportunityActionLog).where(OpportunityActionLog.id == action_id)
        result = await self.db.execute(stmt)
        action_log = result.scalar_one_or_none()

        if not action_log:
            raise BusinessException(detail="动作不存在")

        if action_log.status in [ActionStatus.DONE, ActionStatus.SKIPPED]:
            raise BusinessException(detail="动作已完成或已跳过")

        # 获取动作配置
        stmt = select(PipelineActionConfig).where(
            PipelineActionConfig.id == action_log.action_config_id
        )
        result = await self.db.execute(stmt)
        config = result.scalar_one_or_none()

        # 检查是否为必需动作
        if config.is_required:
            raise BusinessException(detail="必需动作不能跳过")

        # 更新动作状态
        action_log.status = ActionStatus.SKIPPED
        action_log.finished_at = datetime.now()
        action_log.operator_id = current_user_id
        action_log.notes = request.reason
        action_log.updated_by = current_user_id

        await self.db.flush()

        # 同步快照表
        await self._sync_after_action_update(action_log, f"跳过动作: {action_log.action_name}")

        await self.db.commit()
        await self.db.refresh(action_log)

        return ActionLogResponse.model_validate(action_log)

    async def check_stage_completion(
        self,
        opportunity_id: str,
        stage_id: str
    ) -> bool:
        """
        检查阶段是否可以完成（所有必需动作已完成）
        优先使用快照表，fallback 到全量扫描

        Args:
            opportunity_id: 商机ID
            stage_id: 阶段ID

        Returns:
            是否可以完成阶段
        """
        # 优先从快照表读取
        summary_stmt = select(OppExecutionSummary).where(
            OppExecutionSummary.opportunity_id == opportunity_id,
            OppExecutionSummary.current_stage_id == stage_id
        )
        summary = (await self.db.execute(summary_stmt)).scalar_one_or_none()
        if summary:
            return summary.pending_required_count == 0

        # fallback: 全量扫描
        return await self._full_scan_check(opportunity_id, stage_id)

    async def _full_scan_check(self, opportunity_id: str, stage_id: str) -> bool:
        """全量扫描检查阶段完成状态（fallback）"""
        stmt = select(PipelineActionConfig).where(
            PipelineActionConfig.stage_id == stage_id
        )
        result = await self.db.execute(stmt)
        action_configs = result.scalars().all()

        action_logs = []
        for config in action_configs:
            stmt = select(OpportunityActionLog).where(
                and_(
                    OpportunityActionLog.opportunity_id == opportunity_id,
                    OpportunityActionLog.action_config_id == config.id
                )
            )
            result = await self.db.execute(stmt)
            log = result.scalar_one_or_none()
            if log:
                action_logs.append(log)

        return await self._check_can_complete_stage(action_configs, action_logs)

    async def get_action_detail(self, action_id: str) -> ActionLogResponse:
        """
        获取动作详情

        Args:
            action_id: 动作日志ID

        Returns:
            动作日志详情
        """
        stmt = select(OpportunityActionLog).where(OpportunityActionLog.id == action_id)
        result = await self.db.execute(stmt)
        action_log = result.scalar_one_or_none()

        if not action_log:
            raise BusinessException(detail="动作不存在")

        return ActionLogResponse.model_validate(action_log)

    async def get_opportunity_actions(
        self,
        opportunity_id: str
    ) -> List[ActionLogResponse]:
        """
        获取商机的所有动作

        Args:
            opportunity_id: 商机ID

        Returns:
            动作日志列表
        """
        stmt = select(OpportunityActionLog).where(
            OpportunityActionLog.opportunity_id == opportunity_id
        ).order_by(OpportunityActionLog.created_at)
        result = await self.db.execute(stmt)
        action_logs = result.scalars().all()

        return [ActionLogResponse.model_validate(log) for log in action_logs]

    async def trigger_sub_pipeline(
        self,
        action_id: str,
        current_user_id: str
    ) -> ActionLogResponse:
        """
        触发子流水线（SUB_PIPELINE类型）

        Args:
            action_id: 动作日志ID
            current_user_id: 当前用户ID

        Returns:
            更新后的动作日志
        """
        stmt = select(OpportunityActionLog).where(OpportunityActionLog.id == action_id)
        result = await self.db.execute(stmt)
        action_log = result.scalar_one_or_none()

        if not action_log:
            raise BusinessException(detail="动作不存在")

        # 获取动作配置
        stmt = select(PipelineActionConfig).where(
            PipelineActionConfig.id == action_log.action_config_id
        )
        result = await self.db.execute(stmt)
        config = result.scalar_one_or_none()

        # 验证动作类型
        if config.action_type != ActionType.SUB_PIPELINE:
            raise BusinessException(detail=f"动作类型 {config.action_type} 不支持子流水线触发")

        # TODO: 实现子流水线触发逻辑
        # 这里需要根据 trigger_config 中的配置启动子流水线
        # 暂时标记为完成

        action_log.status = ActionStatus.DONE
        action_log.finished_at = datetime.now()
        action_log.operator_id = current_user_id
        action_log.updated_by = current_user_id
        action_log.captured_data = {
            "sub_pipeline_triggered": True,
            "trigger_config": config.trigger_config
        }

        await self.db.commit()
        await self.db.refresh(action_log)

        return ActionLogResponse.model_validate(action_log)

    # 私有方法

    async def _sync_execution_summary(
        self,
        opportunity_id: str,
        stage_id: str,
        action_configs: list,
        action_logs: list,
        last_action_desc: str = None
    ):
        """
        同步执行快照表 crm_opp_execution_summary

        Args:
            opportunity_id: 商机ID
            stage_id: 阶段ID
            action_configs: 当前阶段的 PipelineActionConfig 列表（已过滤）
            action_logs: 当前商机的 OpportunityActionLog 列表
            last_action_desc: 最后一次操作摘要
        """
        # 计算 pending_required_count
        required_configs = [c for c in action_configs if c.is_required]
        log_map = {log.action_config_id: log for log in action_logs}
        pending = sum(
            1 for c in required_configs
            if c.id not in log_map or log_map[c.id].status != ActionStatus.DONE
        )

        # 获取阶段信息（stage code/name/order）用于计算进度
        stage_stmt = select(PipelineStage).where(PipelineStage.id == stage_id)
        stage = (await self.db.execute(stage_stmt)).scalar_one_or_none()
        total_stages = 9  # 固定9个阶段
        progress = round((stage.order / total_stages) * 100, 2) if stage else 0.0

        # Upsert crm_opp_execution_summary
        summary_stmt = select(OppExecutionSummary).where(
            OppExecutionSummary.opportunity_id == opportunity_id
        )
        summary = (await self.db.execute(summary_stmt)).scalar_one_or_none()

        if summary:
            summary.current_stage_id = stage_id
            summary.current_stage_code = getattr(stage, 'stage_code', stage.id) if stage else None
            summary.current_stage_name = stage.name if stage else None
            summary.total_progress = progress
            summary.pending_required_count = pending
            summary.total_required_count = len(required_configs)
            summary.health_status = "RED" if pending > 3 else "YELLOW" if pending > 0 else "GREEN"
            if last_action_desc:
                summary.last_action_desc = last_action_desc
                summary.last_action_at = datetime.now()
        else:
            self.db.add(OppExecutionSummary(
                opportunity_id=opportunity_id,
                current_stage_id=stage_id,
                current_stage_code=getattr(stage, 'stage_code', stage.id) if stage else None,
                current_stage_name=stage.name if stage else None,
                total_progress=progress,
                pending_required_count=pending,
                total_required_count=len(required_configs),
                health_status="GREEN",
                last_action_desc=last_action_desc,
                last_action_at=datetime.now() if last_action_desc else None,
            ))
        await self.db.flush()

    async def _sync_after_action_update(
        self,
        action_log: OpportunityActionLog,
        last_action_desc: str
    ):
        """
        在 action 状态更新后同步快照表（内部辅助方法）

        Args:
            action_log: 已更新的动作日志
            last_action_desc: 最后操作摘要
        """
        # 1. 获取 stage_id（从 action_config）
        config_stmt = select(PipelineActionConfig).where(
            PipelineActionConfig.id == action_log.action_config_id
        )
        config = (await self.db.execute(config_stmt)).scalar_one_or_none()
        if not config:
            return
        stage_id = config.stage_id

        # 2. 获取商机的 service_scope
        opp_stmt = select(Opportunity).where(Opportunity.id == action_log.opportunity_id)
        opp = (await self.db.execute(opp_stmt)).scalar_one_or_none()
        service_scope = opp.service_scope or [] if opp else []

        # 3. 获取该阶段所有过滤后的 configs
        all_configs_stmt = select(PipelineActionConfig).where(
            PipelineActionConfig.stage_id == stage_id
        )
        all_configs = (await self.db.execute(all_configs_stmt)).scalars().all()
        filtered_configs = [
            c for c in all_configs
            if c.trigger_condition == "DEFAULT" or c.trigger_condition in service_scope
        ]

        # 4. 获取当前 pipeline_log 中该商机的所有 action logs
        logs_stmt = select(OpportunityActionLog).where(
            and_(
                OpportunityActionLog.opportunity_id == action_log.opportunity_id,
                OpportunityActionLog.pipeline_log_id == action_log.pipeline_log_id
            )
        )
        action_logs = (await self.db.execute(logs_stmt)).scalars().all()

        # 5. 同步快照
        await self._sync_execution_summary(
            opportunity_id=action_log.opportunity_id,
            stage_id=stage_id,
            action_configs=filtered_configs,
            action_logs=list(action_logs),
            last_action_desc=last_action_desc
        )

    async def _check_can_complete_stage(
        self,
        action_configs: List[PipelineActionConfig],
        action_logs: List[OpportunityActionLog]
    ) -> bool:
        """
        检查是否可以完成阶段

        Args:
            action_configs: 动作配置列表
            action_logs: 动作日志列表

        Returns:
            是否可以完成阶段
        """
        # 创建日志映射
        log_map = {log.action_config_id: log for log in action_logs}

        # 检查所有必需动作是否已完成
        for config in action_configs:
            if config.is_required:
                log = log_map.get(config.id)
                if not log or log.status != ActionStatus.DONE:
                    return False

        return True

    async def _validate_action_data(
        self,
        validation_rules: Dict[str, Any],
        captured_data: Optional[Dict[str, Any]]
    ) -> None:
        """
        验证动作数据

        Args:
            validation_rules: 验证规则
            captured_data: 捕获的数据

        Raises:
            BusinessException: 验证失败
        """
        if not captured_data and validation_rules.get("required"):
            raise BusinessException(detail="缺少必需的数据")

        # 文件类型验证
        if "file_types" in validation_rules and captured_data:
            file_path = captured_data.get("file_path", "")
            allowed_types = validation_rules["file_types"]
            file_ext = file_path.split(".")[-1].lower() if "." in file_path else ""

            if file_ext and file_ext not in allowed_types:
                raise BusinessException(
                    detail=f"不支持的文件类型，允许的类型: {', '.join(allowed_types)}"
                )

        # 文件大小验证
        if "max_size_mb" in validation_rules and captured_data:
            file_size = captured_data.get("file_size", 0)
            max_size_bytes = validation_rules["max_size_mb"] * 1024 * 1024

            if file_size > max_size_bytes:
                raise BusinessException(
                    detail=f"文件大小超过限制 ({validation_rules['max_size_mb']}MB)"
                )

        # 必填字段验证
        if "required_fields" in validation_rules and captured_data:
            required_fields = validation_rules["required_fields"]
            missing_fields = [field for field in required_fields if field not in captured_data]

            if missing_fields:
                raise BusinessException(
                    detail=f"缺少必填字段: {', '.join(missing_fields)}"
                )
