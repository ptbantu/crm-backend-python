"""
通用 Repository 基类
提供通用的 CRUD 操作方法
"""
from typing import Optional, List, TypeVar, Generic, Type, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import DeclarativeBase

ModelType = TypeVar("ModelType", bound=DeclarativeBase)


class BaseRepository(Generic[ModelType]):
    """通用仓库基类"""
    
    def __init__(self, db: AsyncSession, model: Type[ModelType]):
        """
        初始化仓库
        
        Args:
            db: 数据库会话
            model: SQLAlchemy 模型类
        """
        self.db = db
        self.model = model
    
    async def get_by_id(self, entity_id: str) -> Optional[ModelType]:
        """
        根据ID查询实体
        
        Args:
            entity_id: 实体ID
        
        Returns:
            实体对象或 None
        """
        result = await self.db.execute(
            select(self.model).where(self.model.id == entity_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_code(self, code: str) -> Optional[ModelType]:
        """
        根据编码查询实体（如果模型有 code 字段）
        
        Args:
            code: 编码
        
        Returns:
            实体对象或 None
        
        Raises:
            AttributeError: 如果模型没有 code 字段
        """
        if not hasattr(self.model, 'code'):
            raise AttributeError(f"Model {self.model.__name__} does not have 'code' attribute")
        
        result = await self.db.execute(
            select(self.model).where(self.model.code == code)
        )
        return result.scalar_one_or_none()
    
    async def create(self, entity: ModelType) -> ModelType:
        """
        创建实体
        
        Args:
            entity: 实体对象
        
        Returns:
            创建后的实体对象
        """
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity
    
    async def update(self, entity: ModelType) -> ModelType:
        """
        更新实体
        
        Args:
            entity: 实体对象
        
        Returns:
            更新后的实体对象
        """
        await self.db.flush()
        await self.db.refresh(entity)
        return entity
    
    async def delete(self, entity: ModelType) -> None:
        """
        删除实体
        
        Args:
            entity: 实体对象
        """
        await self.db.delete(entity)
        await self.db.flush()
    
    async def get_list(
        self,
        page: int = 1,
        size: int = 10,
        filters: Optional[List[Any]] = None,
        order_by: Optional[Any] = None,
    ) -> tuple[List[ModelType], int]:
        """
        分页查询实体列表
        
        Args:
            page: 页码（从1开始）
            size: 每页数量
            filters: 查询条件列表（SQLAlchemy 条件表达式）
            order_by: 排序字段（默认为 created_at 降序）
        
        Returns:
            (实体列表, 总数)
        """
        query = select(self.model)
        
        # 应用过滤条件
        if filters:
            query = query.where(or_(*filters))
        
        # 计算总数
        count_query = select(func.count()).select_from(self.model)
        if filters:
            count_query = count_query.where(or_(*filters))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 应用排序
        if order_by is not None:
            query = query.order_by(order_by)
        elif hasattr(self.model, 'created_at'):
            query = query.order_by(self.model.created_at.desc())
        
        # 分页
        query = query.offset((page - 1) * size).limit(size)
        
        # 执行查询
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return list(items), total
    
    async def get_all(
        self,
        filters: Optional[List[Any]] = None,
        order_by: Optional[Any] = None,
        limit: Optional[int] = None,
    ) -> List[ModelType]:
        """
        查询所有实体（不分页）
        
        Args:
            filters: 查询条件列表
            order_by: 排序字段
            limit: 限制返回数量
        
        Returns:
            实体列表
        """
        query = select(self.model)
        
        if filters:
            query = query.where(or_(*filters))
        
        if order_by is not None:
            query = query.order_by(order_by)
        elif hasattr(self.model, 'created_at'):
            query = query.order_by(self.model.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count(self, filters: Optional[List[Any]] = None) -> int:
        """
        统计实体数量
        
        Args:
            filters: 查询条件列表
        
        Returns:
            实体数量
        """
        query = select(func.count()).select_from(self.model)
        if filters:
            query = query.where(or_(*filters))
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def exists(self, entity_id: str) -> bool:
        """
        检查实体是否存在
        
        Args:
            entity_id: 实体ID
        
        Returns:
            是否存在
        """
        entity = await self.get_by_id(entity_id)
        return entity is not None

