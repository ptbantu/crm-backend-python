"""
客户来源管理 API
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from common.schemas.response import Result
from foundation_service.dependencies import get_db

router = APIRouter()


@router.get("", response_model=Result[List[dict]])
async def get_customer_sources(
    lang: str = Query('zh', description="语言代码：'zh'（中文）或 'id'（印尼语）"),
    db: AsyncSession = Depends(get_db)
):
    """获取客户来源列表（用于下拉选择）"""
    try:
        # 使用原始 SQL 查询，只查询表中实际存在的字段
        # 注意：数据库中的 customer_sources 表只有 name 字段，没有 name_zh 和 name_id
        sql = text("""
            SELECT 
                id,
                code,
                name,
                description,
                display_order
            FROM customer_sources
            WHERE is_active = 1
            ORDER BY display_order, code
        """)
        
        # 执行查询
        result = await db.execute(sql)
        rows = result.fetchall()
        
        # 转换为响应格式
        source_list = []
        for row in rows:
            # 数据库表只有 name 字段，使用 name 作为中文和印尼语名称
            source_name = row.name
            name_zh = source_name
            name_id = source_name
            name = source_name  # 当前只有 name 字段，所以都返回 name
            
            source_dict = {
                "id": row.id,
                "code": row.code,
                "name_zh": name_zh,
                "name_id": name_id,
                "name": name,  # 根据语言返回对应名称
                "description": row.description,
                "display_order": str(row.display_order) if row.display_order is not None else "0",
            }
            source_list.append(source_dict)
        
        return Result.success(data=source_list)
    except Exception as e:
        from common.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.error(f"获取客户来源列表失败: {str(e)}", exc_info=True)
        return Result.error(code=500, message=f"获取客户来源列表失败: {str(e)}")

