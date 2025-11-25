"""
客户等级配置服务
"""
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from order_workflow_service.repositories.customer_level_repository import CustomerLevelRepository
from common.utils.logger import get_logger

logger = get_logger(__name__)


class CustomerLevelService:
    """客户等级配置服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = CustomerLevelRepository(db)
    
    async def get_by_code(self, code: str, lang: str = "zh") -> Optional[Dict]:
        """根据代码获取客户等级（支持双语）"""
        level = await self.repository.get_by_code(code)
        if not level:
            return None
        
        return {
            "code": level.code,
            "name_zh": level.name_zh,
            "name_id": level.name_id,
            "name": level.name_zh if lang == "zh" else level.name_id,
            "description_zh": level.description_zh,
            "description_id": level.description_id,
            "sort_order": level.sort_order,
        }
    
    async def get_all_active(self, lang: str = "zh") -> List[Dict]:
        """获取所有激活的客户等级（支持双语）"""
        levels = await self.repository.get_all_active()
        return [
            {
                "code": level.code,
                "name_zh": level.name_zh,
                "name_id": level.name_id,
                "name": level.name_zh if lang == "zh" else level.name_id,
                "description_zh": level.description_zh,
                "description_id": level.description_id,
                "sort_order": level.sort_order,
            }
            for level in levels
        ]
    
    async def validate_code(self, code: str) -> bool:
        """验证客户等级代码是否有效"""
        level = await self.repository.get_by_code(code)
        return level is not None

