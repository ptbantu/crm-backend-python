"""
系统配置数据访问层
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from common.models.system_config import SystemConfig
from common.utils.repository import BaseRepository


class SystemConfigRepository(BaseRepository[SystemConfig]):
    """系统配置仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, SystemConfig)
    
    async def get_by_key(self, config_key: str) -> Optional[SystemConfig]:
        """根据配置键查询配置"""
        result = await self.db.execute(
            select(SystemConfig).where(SystemConfig.config_key == config_key)
        )
        return result.scalar_one_or_none()
    
    async def get_by_type(self, config_type: str) -> List[SystemConfig]:
        """根据配置类型查询配置列表"""
        result = await self.db.execute(
            select(SystemConfig).where(SystemConfig.config_type == config_type)
        )
        return list(result.scalars().all())
    
    async def get_enabled_by_type(self, config_type: str) -> List[SystemConfig]:
        """根据配置类型查询启用的配置列表"""
        result = await self.db.execute(
            select(SystemConfig).where(
                SystemConfig.config_type == config_type,
                SystemConfig.is_enabled == True
            )
        )
        return list(result.scalars().all())
