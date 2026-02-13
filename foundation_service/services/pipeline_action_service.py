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
        阶段进入时初始化所有动作日志

        Args:
            opportunity_id: 商机ID
            pipeline_log_id: 流水线日志ID
            stage_id: 阶段ID
            current_user_id: 当前用户ID

        Returns:
            创建的动作日志列表
        """
        # 获取该阶段的所有动作配置
        stmt = select(PipelineActionConfig).where(
            PipelineActionConfig.stage_id == stage_id
        ).order_by(PipelineActionConfig.order)
        result = await self.db.execute(stmt)
        action_configs = result.scalars().all()

        if not action_configs:
            return []

        # 为每个动作配置创建执行日志
        action_logs = []
        for config in action_configs:
            # 检查是否已存在（避免重复初始化）
            stmt = select(OpportunityActionLog).where(
                and_(
                    OpportunityActionLog.opportunity_id == opportunity_id,
                    OpportunityActionLog.action_config_id == config.id
                )
            )
            result = await self.db.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                action_logs.append(existing)
                continue

            # 创建新的动作日志
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

        Args:
            opportunity_id: 商机ID
            stage_id: 阶段ID

        Returns:
            是否可以完成阶段
        """
        # 获取该阶段的所有动作配置
        stmt = select(PipelineActionConfig).where(
            PipelineActionConfig.stage_id == stage_id
        )
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
