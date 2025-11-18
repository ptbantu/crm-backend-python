"""
服务类型数据访问层
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from service_management.models.service_type import ServiceType
from common.utils.repository import BaseRepository


class ServiceTypeRepository(BaseRepository[ServiceType]):
    """服务类型仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ServiceType)
    
    async def get_by_code(self, code: str) -> Optional[ServiceType]:
        """根据代码查询服务类型"""
        query = select(ServiceType).where(ServiceType.code == code)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

