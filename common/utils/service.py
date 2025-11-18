"""
通用 Service 基类
提供通用的服务层方法
"""
from typing import TypeVar, Generic, Optional, List, Type
from sqlalchemy.ext.asyncio import AsyncSession
from common.exceptions import BusinessException

RepositoryType = TypeVar("RepositoryType")


class BaseService(Generic[RepositoryType]):
    """通用服务基类"""
    
    def __init__(self, db: AsyncSession, repository: RepositoryType):
        """
        初始化服务
        
        Args:
            db: 数据库会话
            repository: 仓库实例
        """
        self.db = db
        self.repo = repository
    
    async def validate_not_exists(
        self,
        field_name: str,
        field_value: str,
        get_method: str = "get_by_code",
        error_message: Optional[str] = None,
    ) -> None:
        """
        验证字段值不存在（用于创建时检查唯一性）
        
        Args:
            field_name: 字段名称（用于错误消息）
            field_value: 字段值
            get_method: 仓库方法名（用于查询）
            error_message: 自定义错误消息
        
        Raises:
            BusinessException: 如果字段值已存在
        """
        if not field_value:
            return
        
        get_func = getattr(self.repo, get_method, None)
        if not get_func:
            raise ValueError(f"Repository does not have method '{get_method}'")
        
        existing = await get_func(field_value)
        if existing:
            if error_message:
                raise BusinessException(detail=error_message)
            raise BusinessException(detail=f"{field_name} {field_value} 已存在")
    
    async def validate_exists(
        self,
        entity_id: str,
        entity_name: str = "实体",
        error_message: Optional[str] = None,
    ) -> None:
        """
        验证实体存在
        
        Args:
            entity_id: 实体ID
            entity_name: 实体名称（用于错误消息）
            error_message: 自定义错误消息
        
        Raises:
            BusinessException: 如果实体不存在
        """
        exists = await self.repo.exists(entity_id)
        if not exists:
            if error_message:
                raise BusinessException(detail=error_message, status_code=404)
            raise BusinessException(detail=f"{entity_name}不存在", status_code=404)
    
    async def validate_active(
        self,
        entity_id: str,
        entity_name: str = "实体",
        error_message: Optional[str] = None,
    ) -> None:
        """
        验证实体处于激活状态
        
        Args:
            entity_id: 实体ID
            entity_name: 实体名称（用于错误消息）
            error_message: 自定义错误消息
        
        Raises:
            BusinessException: 如果实体未激活
        """
        entity = await self.repo.get_by_id(entity_id)
        if not entity:
            if error_message:
                raise BusinessException(detail=error_message, status_code=404)
            raise BusinessException(detail=f"{entity_name}不存在", status_code=404)
        
        if hasattr(entity, 'is_active') and not entity.is_active:
            if error_message:
                raise BusinessException(detail=error_message)
            raise BusinessException(detail=f"{entity_name}未激活")

