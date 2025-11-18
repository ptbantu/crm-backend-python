"""
联系人数据访问层
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from service_management.models.contact import Contact
from common.utils.repository import BaseRepository


class ContactRepository(BaseRepository[Contact]):
    """联系人仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Contact)
    
    async def get_by_customer_id(
        self,
        customer_id: str,
        page: int = 1,
        size: int = 10,
        is_primary: Optional[bool] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[Contact], int]:
        """根据客户ID查询联系人列表"""
        query = select(Contact).where(Contact.customer_id == customer_id)
        conditions = [Contact.customer_id == customer_id]
        
        if is_primary is not None:
            conditions.append(Contact.is_primary == is_primary)
        if is_active is not None:
            conditions.append(Contact.is_active == is_active)
        
        query = query.where(or_(*conditions))
        
        # 排序：主要联系人优先
        query = query.order_by(Contact.is_primary.desc(), Contact.created_at.desc())
        
        # 计算总数
        count_query = select(func.count()).select_from(Contact)
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
    
    async def get_primary_contact(self, customer_id: str) -> Optional[Contact]:
        """获取客户的主要联系人"""
        query = select(Contact).where(
            Contact.customer_id == customer_id,
            Contact.is_primary == True,
            Contact.is_active == True
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def set_primary_contact(self, contact_id: str, customer_id: str) -> None:
        """设置主要联系人（取消其他主要联系人）"""
        # 先取消该客户的所有主要联系人
        query = select(Contact).where(
            Contact.customer_id == customer_id,
            Contact.is_primary == True
        )
        result = await self.db.execute(query)
        existing_primary = result.scalars().all()
        for contact in existing_primary:
            contact.is_primary = False
        
        # 设置新的主要联系人
        contact = await self.get_by_id(contact_id)
        if contact and contact.customer_id == customer_id:
            contact.is_primary = True
            await self.db.flush()

