"""
系统配置管理 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from common.utils.logger import get_logger
from foundation_service.schemas.system_config import (
    OSSConfigRequest, OSSConfigResponse,
    AIConfigRequest, AIConfigResponse,
    SMSConfigRequest, SMSConfigResponse,
    EmailConfigRequest, EmailConfigResponse,
    SystemStatusResponse, ConfigHistoryListResponse,
    TestConnectionResponse, ConfigType
)
from foundation_service.services.system_config_service import SystemConfigService
from foundation_service.dependencies import get_db, require_bantu_admin

logger = get_logger(__name__)

router = APIRouter()


@router.get("/{config_type}", response_model=Result[dict])
async def get_config(
    config_type: str,
    db: AsyncSession = Depends(get_db)
):
    """获取指定类型的配置"""
    service = SystemConfigService(db)
    
    if config_type == ConfigType.OSS:
        config = await service.get_oss_config()
        if config:
            return Result.success(data=config.model_dump())
    elif config_type == ConfigType.AI:
        config = await service.get_ai_config()
        if config:
            return Result.success(data=config.model_dump())
    elif config_type == ConfigType.SMS:
        config = await service.get_sms_config()
        if config:
            return Result.success(data=config.model_dump())
    elif config_type == ConfigType.EMAIL:
        config = await service.get_email_config()
        if config:
            return Result.success(data=config.model_dump())
    else:
        return Result.error(code=400, message=f"不支持的配置类型: {config_type}")
    
    return Result.success(data={})


@router.put("/{config_type}", response_model=Result[dict])
async def update_config(
    config_type: str,
    request: dict,
    request_obj: Request,
    db: AsyncSession = Depends(get_db)
):
    """更新指定类型的配置（仅管理员）"""
    # 权限检查：仅管理员可以修改配置
    current_user_id = await require_bantu_admin(request_obj, db)
    
    service = SystemConfigService(db)
    change_reason = request.pop("change_reason", None)
    
    try:
        if config_type == ConfigType.OSS:
            oss_request = OSSConfigRequest(**request)
            config = await service.update_oss_config(oss_request, current_user_id, change_reason)
            return Result.success(data=config.model_dump(), message="OSS配置更新成功")
        elif config_type == ConfigType.AI:
            ai_request = AIConfigRequest(**request)
            config = await service.update_ai_config(ai_request, current_user_id, change_reason)
            return Result.success(data=config.model_dump(), message="AI配置更新成功")
        elif config_type == ConfigType.SMS:
            sms_request = SMSConfigRequest(**request)
            config = await service.update_sms_config(sms_request, current_user_id, change_reason)
            return Result.success(data=config.model_dump(), message="短信配置更新成功")
        elif config_type == ConfigType.EMAIL:
            email_request = EmailConfigRequest(**request)
            config = await service.update_email_config(email_request, current_user_id, change_reason)
            return Result.success(data=config.model_dump(), message="邮箱配置更新成功")
        else:
            return Result.error(code=400, message=f"不支持的配置类型: {config_type}")
    except Exception as e:
        logger.error(f"更新配置失败: {str(e)}", exc_info=True)
        return Result.error(code=500, message=f"更新配置失败: {str(e)}")


@router.post("/{config_type}/test", response_model=Result[TestConnectionResponse])
async def test_connection(
    config_type: str,
    db: AsyncSession = Depends(get_db)
):
    """测试连接（仅管理员）"""
    service = SystemConfigService(db)
    result = await service.test_connection(config_type)
    return Result.success(data=result)


@router.get("/status/system", response_model=Result[SystemStatusResponse])
async def get_system_status(
    db: AsyncSession = Depends(get_db)
):
    """获取系统状态"""
    service = SystemConfigService(db)
    status = await service.get_system_status()
    return Result.success(data=status)


@router.get("/history", response_model=Result[ConfigHistoryListResponse])
async def get_config_history(
    config_id: Optional[str] = Query(None, description="配置ID（可选）"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """获取配置历史（仅管理员）"""
    service = SystemConfigService(db)
    records, total = await service.get_config_history(config_id, page, size)
    
    return Result.success(data=ConfigHistoryListResponse(
        records=records,
        total=total,
        page=page,
        size=size
    ))
