"""
认证 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from foundation_service.schemas.auth import LoginRequest, LoginResponse
from foundation_service.services.auth_service import AuthService
from foundation_service.dependencies import get_db

router = APIRouter()


@router.post("/login", response_model=Result[LoginResponse])
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """用户登录（邮箱+密码）"""
    service = AuthService(db)
    response = await service.login(request)
    return Result.success(data=response, message="登录成功")

