"""
天眼查 API 路由
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import Result
from common.utils.logger import get_logger
from foundation_service.schemas.tianyancha import (
    EnterpriseQueryRequest, 
    EnterpriseQueryResponse,
    EnterpriseSearchRequest,
    EnterpriseSearchResponse,
    EnterpriseDetailRequest,
    EnterpriseDetailResponse
)
from foundation_service.services.tianyancha_service import TianyanchaService
from foundation_service.dependencies import get_db

logger = get_logger(__name__)

router = APIRouter()


@router.post("/enterprise/query", response_model=Result[EnterpriseQueryResponse])
async def query_enterprise(
    request: EnterpriseQueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    查询企业信息
    
    支持通过企业名称、统一社会信用代码或注册号查询
    """
    try:
        service = TianyanchaService(db)
        result = await service.query_enterprise(request.keyword)
        
        if result.success:
            return Result.success(data=result, message=result.message or "查询成功")
        else:
            return Result.error(code=400, message=result.message or "查询失败", data=result)
            
    except Exception as e:
        logger.error(f"查询企业信息异常: {str(e)}", exc_info=True)
        return Result.error(code=500, message=f"查询异常: {str(e)}")


@router.post("/enterprise/search", response_model=Result[EnterpriseSearchResponse])
async def search_enterprises(
    request: EnterpriseSearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    搜索企业列表（816接口）
    
    支持通过企业名称、统一社会信用代码或注册号搜索，返回企业列表
    """
    try:
        service = TianyanchaService(db)
        result = await service.search_enterprises(
            keyword=request.keyword,
            page_num=request.page_num or 1,
            page_size=request.page_size or 10
        )
        
        if result.success:
            return Result.success(data=result, message=result.message or "搜索成功")
        else:
            return Result.error(code=400, message=result.message or "搜索失败", data=result)
            
    except Exception as e:
        logger.error(f"搜索企业列表异常: {str(e)}", exc_info=True)
        return Result.error(code=500, message=f"搜索异常: {str(e)}")


@router.post("/enterprise/detail", response_model=Result[EnterpriseDetailResponse])
async def get_enterprise_detail(
    request: EnterpriseDetailRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    获取企业详细信息（818接口）
    
    根据企业ID获取企业的详细信息
    """
    try:
        service = TianyanchaService(db)
        result = await service.get_enterprise_detail(request.enterprise_id)
        
        if result.success:
            return Result.success(data=result, message=result.message or "查询成功")
        else:
            return Result.error(code=400, message=result.message or "查询失败", data=result)
            
    except Exception as e:
        logger.error(f"查询企业详情异常: {str(e)}", exc_info=True)
        return Result.error(code=500, message=f"查询异常: {str(e)}")
