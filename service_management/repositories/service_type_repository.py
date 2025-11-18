"""
服务类型数据访问层
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
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
    
    async def get_list(
        self,
        page: int = 1,
        size: int = 10,
        code: Optional[str] = None,
        name: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[ServiceType], int]:
        """分页查询服务类型列表"""
        # 构建查询
        query = select(ServiceType)
        conditions = []
        
        if code:
            conditions.append(ServiceType.code.like(f"%{code}%"))
        if name:
            from sqlalchemy import case
            conditions.append(
                or_(
                    ServiceType.name.like(f"%{name}%"),
                    ServiceType.name_en.like(f"%{name}%")
                )
            )
        if is_active is not None:
            conditions.append(ServiceType.is_active == is_active)
        
        if conditions:
            query = query.where(*conditions)
        
        # 按显示顺序和创建时间排序
        query = query.order_by(
            ServiceType.display_order.asc(),
            ServiceType.created_at.asc()
        )
        
        # 获取总数
        count_query = select(func.count()).select_from(ServiceType)
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)
        
        # 执行查询
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return list(items), total

