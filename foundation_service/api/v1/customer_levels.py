"""
客户等级和跟进状态选项 API
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from foundation_service.dependencies import get_database_session
from foundation_service.services.customer_level_service import CustomerLevelService
from foundation_service.services.follow_up_status_service import FollowUpStatusService
from common.schemas.response import Result

router = APIRouter()


@router.get("/customer-levels", response_model=Result[list])
async def get_customer_level_options(
    lang: str = Query("zh", description="语言代码：zh（中文）或 id（印尼语）"),
    db: AsyncSession = Depends(get_database_session),
):
    """获取客户等级选项列表（从数据库读取，支持双语）"""
    service = CustomerLevelService(db)
    options = await service.get_all_active(lang=lang)
    return Result.success(data=options)


@router.get("/follow-up-statuses", response_model=Result[list])
async def get_follow_up_status_options(
    lang: str = Query("zh", description="语言代码：zh（中文）或 id（印尼语）"),
    db: AsyncSession = Depends(get_database_session),
):
    """获取跟进状态选项列表（从数据库读取，支持双语）"""
    service = FollowUpStatusService(db)
    options = await service.get_all_active(lang=lang)
    return Result.success(data=options)

