"""
跟进状态配置服务
"""
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from order_workflow_service.repositories.follow_up_status_repository import FollowUpStatusRepository
from common.utils.logger import get_logger

logger = get_logger(__name__)


class FollowUpStatusService:
    """跟进状态配置服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = FollowUpStatusRepository(db)
    
    async def get_by_code(self, code: str, lang: str = "zh") -> Optional[Dict]:
        """根据代码获取跟进状态（支持双语）"""
        status = await self.repository.get_by_code(code)
        if not status:
            return None
        
        return {
            "code": status.code,
            "name_zh": status.name_zh,
            "name_id": status.name_id,
            "name": status.name_zh if lang == "zh" else status.name_id,
            "description_zh": status.description_zh,
            "description_id": status.description_id,
            "sort_order": status.sort_order,
        }
    
    async def get_all_active(self, lang: str = "zh") -> List[Dict]:
        """获取所有激活的跟进状态（支持双语）"""
        statuses = await self.repository.get_all_active()
        return [
            {
                "code": status.code,
                "name_zh": status.name_zh,
                "name_id": status.name_id,
                "name": status.name_zh if lang == "zh" else status.name_id,
                "description_zh": status.description_zh,
                "description_id": status.description_id,
                "sort_order": status.sort_order,
            }
            for status in statuses
        ]
    
    async def validate_code(self, code: str) -> bool:
        """验证跟进状态代码是否有效"""
        status = await self.repository.get_by_code(code)
        return status is not None

