"""
临时链接服务
"""
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import secrets

from common.models import TemporaryLink
from order_workflow_service.repositories.temporary_link_repository import TemporaryLinkRepository
from common.utils.logger import get_logger
from common.exceptions import BusinessException
import uuid

logger = get_logger(__name__)


class TemporaryLinkService:
    """临时链接服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = TemporaryLinkRepository(db)
    
    def _generate_token(self) -> str:
        """生成唯一的链接令牌"""
        return secrets.token_urlsafe(32)
    
    async def create_temporary_link(
        self,
        resource_type: str,
        resource_id: str,
        expires_at: Optional[datetime] = None,
        max_access_count: int = 1,
        created_by: Optional[str] = None,
    ) -> TemporaryLink:
        """创建临时链接"""
        # 生成唯一令牌
        token = self._generate_token()
        while await self.repository.get_by_token(token):
            token = self._generate_token()
        
        link = TemporaryLink(
            id=str(uuid.uuid4()),
            link_token=token,
            resource_type=resource_type,
            resource_id=resource_id,
            expires_at=expires_at,
            max_access_count=max_access_count,
            current_access_count=0,
            is_active=True,
            created_by=created_by,
        )
        
        await self.repository.create(link)
        await self.db.commit()
        await self.db.refresh(link)
        
        return link
    
    async def access_temporary_link(
        self,
        link_token: str,
    ) -> Dict[str, Any]:
        """访问临时链接"""
        link = await self.repository.get_by_token(link_token)
        if not link:
            raise BusinessException(detail="链接不存在或已失效", status_code=404)
        
        # 检查是否过期
        if link.expires_at and link.expires_at < datetime.utcnow():
            raise BusinessException(detail="链接已过期", status_code=410)
        
        # 检查访问次数
        if link.current_access_count >= link.max_access_count:
            raise BusinessException(detail="链接访问次数已达上限", status_code=410)
        
        # 增加访问次数
        await self.repository.increment_access_count(link.id)
        
        # 根据资源类型获取资源数据
        resource_data = await self._get_resource_data(link.resource_type, link.resource_id)
        
        return {
            "link": link,
            "resource_data": resource_data,
        }
    
    async def _get_resource_data(
        self,
        resource_type: str,
        resource_id: str,
    ) -> Optional[Dict[str, Any]]:
        """根据资源类型获取资源数据"""
        # TODO: 根据不同的资源类型实现数据获取逻辑
        # 例如：service_account, order, customer
        logger.info(f"获取资源数据: resource_type={resource_type}, resource_id={resource_id}")
        return None

