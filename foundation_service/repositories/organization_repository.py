"""
组织数据访问层
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from common.models.organization import Organization
from common.models.organization_employee import OrganizationEmployee
from common.utils.repository import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    """组织仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Organization)
    
    async def get_by_code(self, code: str) -> Optional[Organization]:
        """根据编码查询组织"""
        result = await self.db.execute(
            select(Organization).where(Organization.code == code)
        )
        return result.scalar_one_or_none()
    
    async def get_employees_count(self, organization_id: str) -> int:
        """获取员工数量"""
        result = await self.db.execute(
            select(func.count(OrganizationEmployee.id))
            .where(
                OrganizationEmployee.organization_id == organization_id,
                OrganizationEmployee.is_active == True
            )
        )
        return result.scalar() or 0
    
    async def get_list(
        self,
        page: int = 1,
        size: int = 10,
        name: Optional[str] = None,
        code: Optional[str] = None,
        organization_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_locked: Optional[bool] = None,
        organization_id: Optional[str] = None
    ) -> tuple[List[Organization], int]:
        """分页查询组织列表"""
        query = select(Organization)
        
        if name:
            query = query.where(Organization.name.like(f"%{name}%"))
        if code:
            query = query.where(Organization.code == code)
        if organization_type:
            query = query.where(Organization.organization_type == organization_type)
        if is_locked is not None:
            query = query.where(Organization.is_locked == is_locked)
        if is_active is not None:
            query = query.where(Organization.is_active == is_active)
        if organization_id:
            query = query.where(Organization.id == organization_id)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页查询
        query = query.order_by(Organization.organization_type, Organization.code)
        query = query.offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        organizations = result.scalars().all()
        
        return list(organizations), total
    
    async def get_next_sequence_by_type(self, organization_type: str) -> int:
        """获取指定组织类型的下一个序列号"""
        # 查询该类型组织的最大序列号（从 code 中提取）
        # code 格式：type + 序列号 + 年月日，例如：internal00120241119
        from datetime import datetime
        today = datetime.now().strftime("%Y%m%d")
        
        # 查询所有该类型的组织，code 以 type + 数字 + today 开头
        query = select(Organization).where(
            Organization.organization_type == organization_type
        )
        result = await self.db.execute(query)
        all_orgs = list(result.scalars().all())
        
        # 提取序列号
        max_seq = 0
        prefix = f"{organization_type}"
        for org in all_orgs:
            if org.code and org.code.startswith(prefix):
                try:
                    # 尝试从 code 中提取序列号
                    # code 格式：type + 序列号 + 年月日
                    # 例如：internal00120241119 -> 提取 001
                    code_without_prefix = org.code[len(prefix):]
                    if len(code_without_prefix) >= 8:  # 至少包含序列号(3位) + 日期(8位)
                        seq_str = code_without_prefix[:-8]  # 去掉最后8位日期
                        if seq_str.isdigit():
                            seq = int(seq_str)
                            max_seq = max(max_seq, seq)
                except (ValueError, IndexError):
                    continue
        
        return max_seq + 1
    
    async def get_bantu_organization(self) -> Optional[Organization]:
        """获取 BANTU 内部组织（code 为 'BANTU' 或 name 包含 'BANTU'）"""
        # 先尝试通过 code 查找
        bantu = await self.get_by_code("BANTU")
        if bantu:
            return bantu
        
        # 如果 code 不存在，通过 name 查找
        result = await self.db.execute(
            select(Organization)
            .where(
                Organization.organization_type == "internal",
                Organization.name.like("%BANTU%")
            )
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_organization_user_count(self, organization_id: str) -> int:
        """获取组织的用户数量（用于生成用户ID序号）"""
        from common.models.organization_employee import OrganizationEmployee
        result = await self.db.execute(
            select(func.count(OrganizationEmployee.id))
            .where(
                OrganizationEmployee.organization_id == organization_id,
                OrganizationEmployee.is_active == True
            )
        )
        return result.scalar() or 0

