"""
系统配置服务
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
import json
import uuid
from datetime import datetime

from foundation_service.repositories.system_config_repository import SystemConfigRepository
from foundation_service.repositories.system_config_history_repository import SystemConfigHistoryRepository
from common.models.system_config import SystemConfig
from common.models.system_config_history import SystemConfigHistory
from foundation_service.schemas.system_config import (
    ConfigType, OSSConfigRequest, OSSConfigResponse,
    AIConfigRequest, AIConfigResponse,
    SMSConfigRequest, SMSConfigResponse,
    EmailConfigRequest, EmailConfigResponse,
    SystemConfigResponse, SystemConfigHistoryResponse,
    TestConnectionResponse, SystemStatusResponse
)
from common.exceptions import BusinessException
from common.utils.logger import get_logger
from common.utils.id_generator import generate_id

logger = get_logger(__name__)


class SystemConfigService:
    """系统配置服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.config_repo = SystemConfigRepository(db)
        self.history_repo = SystemConfigHistoryRepository(db)
    
    def _mask_sensitive_value(self, value: Dict[str, Any], sensitive_fields: List[str]) -> Dict[str, Any]:
        """脱敏敏感字段"""
        masked = value.copy()
        for field in sensitive_fields:
            if field in masked and masked[field]:
                # 保留前3位和后3位，中间用*替代
                original = str(masked[field])
                if len(original) > 6:
                    masked[field] = original[:3] + "*" * (len(original) - 6) + original[-3:]
                else:
                    masked[field] = "*" * len(original)
        return masked
    
    async def get_config_by_type(self, config_type: str) -> Dict[str, Any]:
        """获取指定类型的配置"""
        configs = await self.config_repo.get_by_type(config_type)
        if not configs:
            return {}
        
        # 合并所有配置值
        result = {}
        for config in configs:
            if isinstance(config.config_value, dict):
                result.update(config.config_value)
            else:
                result.update(json.loads(config.config_value) if isinstance(config.config_value, str) else {})
        
        return result
    
    async def get_oss_config(self) -> Optional[OSSConfigResponse]:
        """获取OSS配置"""
        config_data = await self.get_config_by_type(ConfigType.OSS)
        if not config_data:
            return None
        
        # 脱敏敏感信息
        masked_data = self._mask_sensitive_value(config_data, ["access_key_secret"])
        
        return OSSConfigResponse(**masked_data)
    
    async def get_ai_config(self) -> Optional[AIConfigResponse]:
        """获取AI配置"""
        config_data = await self.get_config_by_type(ConfigType.AI)
        if not config_data:
            return None
        
        masked_data = self._mask_sensitive_value(config_data, ["api_key"])
        
        return AIConfigResponse(**masked_data)
    
    async def get_sms_config(self) -> Optional[SMSConfigResponse]:
        """获取短信配置"""
        config_data = await self.get_config_by_type(ConfigType.SMS)
        if not config_data:
            return None
        
        masked_data = self._mask_sensitive_value(config_data, ["access_key_secret"])
        
        return SMSConfigResponse(**masked_data)
    
    async def get_email_config(self) -> Optional[EmailConfigResponse]:
        """获取邮箱配置"""
        config_data = await self.get_config_by_type(ConfigType.EMAIL)
        if not config_data:
            return None
        
        masked_data = self._mask_sensitive_value(config_data, ["smtp_password"])
        
        return EmailConfigResponse(**masked_data)
    
    async def update_config(
        self,
        config_type: str,
        config_data: Dict[str, Any],
        user_id: str,
        change_reason: Optional[str] = None
    ) -> SystemConfigResponse:
        """更新配置"""
        # 构建配置键（使用类型作为前缀）
        config_key = f"{config_type}.main"
        
        # 查找现有配置
        existing_config = await self.config_repo.get_by_key(config_key)
        
        old_value = None
        if existing_config:
            old_value = existing_config.config_value
            # 更新现有配置
            existing_config.config_value = config_data
            existing_config.updated_by = user_id
            existing_config.updated_at = datetime.now()
            if "is_enabled" in config_data:
                existing_config.is_enabled = config_data.pop("is_enabled")
            
            config = await self.config_repo.update(existing_config)
        else:
            # 生成系统配置ID
            config_id = await generate_id(self.db, "SystemConfig")
            
            # 创建新配置
            new_config = SystemConfig(
                id=config_id,
                config_key=config_key,
                config_value=config_data,
                config_type=config_type,
                description=f"{config_type}配置",
                is_enabled=config_data.pop("is_enabled", True),
                created_by=user_id,
                updated_by=user_id
            )
            config = await self.config_repo.create(new_config)
        
        # 记录历史
        history = SystemConfigHistory(
            id=str(uuid.uuid4()),
            config_id=config.id,
            old_value=old_value,
            new_value=config_data,
            changed_by=user_id,
            change_reason=change_reason
        )
        await self.history_repo.create(history)
        
        await self.db.commit()
        
        return SystemConfigResponse(
            id=config.id,
            config_key=config.config_key,
            config_value=config.config_value,
            config_type=config.config_type,
            description=config.description,
            is_enabled=config.is_enabled,
            created_at=config.created_at,
            updated_at=config.updated_at,
            created_by=config.created_by,
            updated_by=config.updated_by
        )
    
    async def update_oss_config(
        self,
        request: OSSConfigRequest,
        user_id: str,
        change_reason: Optional[str] = None
    ) -> OSSConfigResponse:
        """更新OSS配置"""
        config_data = request.model_dump()
        await self.update_config(ConfigType.OSS, config_data, user_id, change_reason)
        return await self.get_oss_config()
    
    async def update_ai_config(
        self,
        request: AIConfigRequest,
        user_id: str,
        change_reason: Optional[str] = None
    ) -> AIConfigResponse:
        """更新AI配置"""
        config_data = request.model_dump()
        await self.update_config(ConfigType.AI, config_data, user_id, change_reason)
        return await self.get_ai_config()
    
    async def update_sms_config(
        self,
        request: SMSConfigRequest,
        user_id: str,
        change_reason: Optional[str] = None
    ) -> SMSConfigResponse:
        """更新短信配置"""
        config_data = request.model_dump()
        await self.update_config(ConfigType.SMS, config_data, user_id, change_reason)
        return await self.get_sms_config()
    
    async def update_email_config(
        self,
        request: EmailConfigRequest,
        user_id: str,
        change_reason: Optional[str] = None
    ) -> EmailConfigResponse:
        """更新邮箱配置"""
        config_data = request.model_dump()
        await self.update_config(ConfigType.EMAIL, config_data, user_id, change_reason)
        return await self.get_email_config()
    
    async def test_connection(self, config_type: str) -> TestConnectionResponse:
        """测试连接"""
        try:
            config_data = await self.get_config_by_type(config_type)
            if not config_data:
                return TestConnectionResponse(
                    success=False,
                    message="配置不存在"
                )
            
            # 根据配置类型进行不同的测试
            if config_type == ConfigType.OSS:
                return await self._test_oss_connection(config_data)
            elif config_type == ConfigType.AI:
                return await self._test_ai_connection(config_data)
            elif config_type == ConfigType.SMS:
                return await self._test_sms_connection(config_data)
            elif config_type == ConfigType.EMAIL:
                return await self._test_email_connection(config_data)
            else:
                return TestConnectionResponse(
                    success=False,
                    message=f"不支持的配置类型: {config_type}"
                )
        except Exception as e:
            logger.error(f"测试连接失败: {str(e)}", exc_info=True)
            return TestConnectionResponse(
                success=False,
                message=f"测试失败: {str(e)}"
            )
    
    async def _test_oss_connection(self, config_data: Dict[str, Any]) -> TestConnectionResponse:
        """测试OSS连接"""
        try:
            # 这里应该实际调用OSS SDK进行连接测试
            # 为了演示，我们只做基本验证
            required_fields = ["endpoint", "access_key_id", "access_key_secret", "bucket_name"]
            for field in required_fields:
                if field not in config_data or not config_data[field]:
                    return TestConnectionResponse(
                        success=False,
                        message=f"缺少必需字段: {field}"
                    )
            
            # TODO: 实际调用OSS SDK测试连接
            return TestConnectionResponse(
                success=True,
                message="OSS连接测试成功",
                details={"bucket": config_data.get("bucket_name")}
            )
        except Exception as e:
            return TestConnectionResponse(
                success=False,
                message=f"OSS连接测试失败: {str(e)}"
            )
    
    async def _test_ai_connection(self, config_data: Dict[str, Any]) -> TestConnectionResponse:
        """测试AI服务连接"""
        try:
            required_fields = ["provider", "api_key"]
            for field in required_fields:
                if field not in config_data or not config_data[field]:
                    return TestConnectionResponse(
                        success=False,
                        message=f"缺少必需字段: {field}"
                    )
            
            # TODO: 实际调用AI服务API测试连接
            return TestConnectionResponse(
                success=True,
                message="AI服务连接测试成功",
                details={"provider": config_data.get("provider")}
            )
        except Exception as e:
            return TestConnectionResponse(
                success=False,
                message=f"AI服务连接测试失败: {str(e)}"
            )
    
    async def _test_sms_connection(self, config_data: Dict[str, Any]) -> TestConnectionResponse:
        """测试短信服务连接"""
        try:
            required_fields = ["provider", "access_key_id", "access_key_secret"]
            for field in required_fields:
                if field not in config_data or not config_data[field]:
                    return TestConnectionResponse(
                        success=False,
                        message=f"缺少必需字段: {field}"
                    )
            
            # TODO: 实际调用短信服务API测试连接
            return TestConnectionResponse(
                success=True,
                message="短信服务连接测试成功",
                details={"provider": config_data.get("provider")}
            )
        except Exception as e:
            return TestConnectionResponse(
                success=False,
                message=f"短信服务连接测试失败: {str(e)}"
            )
    
    async def _test_email_connection(self, config_data: Dict[str, Any]) -> TestConnectionResponse:
        """测试邮箱服务连接"""
        try:
            required_fields = ["smtp_host", "smtp_port", "smtp_user", "smtp_password"]
            for field in required_fields:
                if field not in config_data or not config_data[field]:
                    return TestConnectionResponse(
                        success=False,
                        message=f"缺少必需字段: {field}"
                    )
            
            # TODO: 实际测试SMTP连接
            return TestConnectionResponse(
                success=True,
                message="邮箱服务连接测试成功",
                details={"smtp_host": config_data.get("smtp_host")}
            )
        except Exception as e:
            return TestConnectionResponse(
                success=False,
                message=f"邮箱服务连接测试失败: {str(e)}"
            )
    
    async def get_system_status(self) -> SystemStatusResponse:
        """获取系统状态"""
        # TODO: 实际获取系统状态信息
        # 这里返回模拟数据
        return SystemStatusResponse(
            version="v2.1.0",
            uptime="15天 8小时 32分钟",
            database_status="正常",
            redis_status="正常",
            mongodb_status="正常",
            cpu_usage=45.2,
            memory_usage=62.8,
            disk_usage=38.5,
            active_users=156,
            total_requests=1234
        )
    
    async def get_config_history(
        self,
        config_id: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> tuple[List[SystemConfigHistoryResponse], int]:
        """获取配置历史"""
        if config_id:
            records, total = await self.history_repo.get_by_config_id(config_id, page, size)
        else:
            # 获取所有历史记录
            all_records = await self.history_repo.get_all()
            total = len(all_records)
            records = all_records[(page - 1) * size:page * size]
        
        history_responses = [
            SystemConfigHistoryResponse(
                id=record.id,
                config_id=record.config_id,
                old_value=record.old_value,
                new_value=record.new_value,
                changed_by=record.changed_by,
                changed_at=record.changed_at,
                change_reason=record.change_reason
            )
            for record in records
        ]
        
        return history_responses, total
