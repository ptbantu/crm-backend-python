"""
服务记录数据访问层
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from service_management.models.service_record import ServiceRecord
from common.utils.repository import BaseRepository


class ServiceRecordRepository(BaseRepository[ServiceRecord]):
    """服务记录仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ServiceRecord)
    
    async def get_list(
        self,
        page: int = 1,
        size: int = 10,
        customer_id: Optional[str] = None,
        service_type_id: Optional[str] = None,
        product_id: Optional[str] = None,
        contact_id: Optional[str] = None,
        sales_user_id: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        referral_customer_id: Optional[str] = None,
    ) -> Tuple[List[ServiceRecord], int]:
        """分页查询服务记录列表"""
        query = select(ServiceRecord)
        conditions = []
        
        if customer_id:
            conditions.append(ServiceRecord.customer_id == customer_id)
        if service_type_id:
            conditions.append(ServiceRecord.service_type_id == service_type_id)
        if product_id:
            conditions.append(ServiceRecord.product_id == product_id)
        if contact_id:
            conditions.append(ServiceRecord.contact_id == contact_id)
        if sales_user_id:
            conditions.append(ServiceRecord.sales_user_id == sales_user_id)
        if status:
            conditions.append(ServiceRecord.status == status)
        if priority:
            conditions.append(ServiceRecord.priority == priority)
        if referral_customer_id:
            conditions.append(ServiceRecord.referral_customer_id == referral_customer_id)
        
        if conditions:
            query = query.where(or_(*conditions))
        
        # 排序：优先级高的在前，然后按创建时间倒序
        priority_order = {
            'urgent': 1,
            'high': 2,
            'normal': 3,
            'low': 4,
        }
        # 使用 CASE WHEN 进行优先级排序
        from sqlalchemy import case
        query = query.order_by(
            case(
                (ServiceRecord.priority == 'urgent', 1),
                (ServiceRecord.priority == 'high', 2),
                (ServiceRecord.priority == 'normal', 3),
                (ServiceRecord.priority == 'low', 4),
                else_=5
            ),
            ServiceRecord.created_at.desc()
        )
        
        # 计算总数
        count_query = select(func.count()).select_from(ServiceRecord)
        if conditions:
            count_query = count_query.where(or_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页
        query = query.offset((page - 1) * size).limit(size)
        
        # 执行查询
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return list(items), total

