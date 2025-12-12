"""
行业管理 API
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from common.schemas.response import Result
from common.models.industry import Industry
from foundation_service.dependencies import get_db

router = APIRouter()


@router.get("", response_model=Result[List[dict]])
async def get_industries(
    lang: str = Query('zh', description="语言代码：'zh'（中文）或 'id'（印尼语）"),
    is_active: Optional[bool] = Query(None, description="是否激活"),
    db: AsyncSession = Depends(get_db)
):
    """获取行业列表（用于下拉选择）"""
    try:
        # 构建查询
        query = select(Industry)
        
        # 过滤激活状态
        if is_active is not None:
            query = query.where(Industry.is_active == is_active)
        else:
            # 默认只返回激活的
            query = query.where(Industry.is_active == True)
        
        # 按排序顺序排序
        query = query.order_by(Industry.sort_order, Industry.code)
        
        # 执行查询
        result = await db.execute(query)
        industries = result.scalars().all()
        
        # 打印查询结果用于调试
        from common.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info(f"查询到 {len(industries)} 条行业记录")
        for industry in industries:
            logger.info(f"行业数据: code={industry.code}, name_zh={industry.name_zh}, name_id={industry.name_id}, sort_order={industry.sort_order}")
        
        # 转换为响应格式
        industry_list = []
        for industry in industries:
            industry_dict = {
                "id": industry.id,
                "code": industry.code,
                "name_zh": industry.name_zh,
                "name_id": industry.name_id,
                "name": industry.name_zh if lang == 'zh' else industry.name_id,  # 根据语言返回对应名称
                "description_zh": industry.description_zh,
                "description_id": industry.description_id,
                "sort_order": industry.sort_order,
                "is_active": industry.is_active,
            }
            industry_list.append(industry_dict)
        
        # 打印最终返回的数据
        logger.info(f"返回的行业列表数据: {industry_list}")
        
        return Result.success(data=industry_list)
    except Exception as e:
        from common.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.error(f"获取行业列表失败: {str(e)}", exc_info=True)
        return Result.error(code=500, message=f"获取行业列表失败: {str(e)}")

