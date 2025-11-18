# BaseRepository - 通用仓库基类

`BaseRepository` 提供了通用的 CRUD 操作方法，减少代码重复。

## 功能

### 基础 CRUD 操作

- `get_by_id(entity_id: str)` - 根据ID查询实体
- `get_by_code(code: str)` - 根据编码查询实体（如果模型有 code 字段）
- `create(entity: ModelType)` - 创建实体
- `update(entity: ModelType)` - 更新实体
- `delete(entity: ModelType)` - 删除实体

### 查询操作

- `get_list(page, size, filters, order_by)` - 分页查询列表
- `get_all(filters, order_by, limit)` - 查询所有实体（不分页）
- `count(filters)` - 统计实体数量
- `exists(entity_id)` - 检查实体是否存在

## 使用示例

### 基础用法

```python
from common.utils.repository import BaseRepository
from service_management.models.product import Product
from sqlalchemy.ext.asyncio import AsyncSession

class ProductRepository(BaseRepository[Product]):
    """产品仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Product)
    
    # 继承的方法：
    # - get_by_id()
    # - get_by_code()
    # - create()
    # - update()
    # - delete()
    # - get_list()
    # - get_all()
    # - count()
    # - exists()
    
    # 可以添加自定义方法
    async def get_by_name(self, name: str):
        """根据名称查询产品"""
        result = await self.db.execute(
            select(Product).where(Product.name == name)
        )
        return result.scalar_one_or_none()
```

### 自定义查询列表

```python
class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Product)
    
    async def get_list(
        self,
        page: int = 1,
        size: int = 10,
        name: Optional[str] = None,
        category_id: Optional[str] = None,
    ) -> tuple[List[Product], int]:
        """分页查询产品列表（自定义）"""
        conditions = []
        if name:
            conditions.append(Product.name.ilike(f"%{name}%"))
        if category_id:
            conditions.append(Product.category_id == category_id)
        
        # 使用基类的 get_list 方法
        return await super().get_list(
            page=page,
            size=size,
            filters=conditions if conditions else None,
            order_by=Product.created_at.desc()
        )
```

## 优势

1. **代码复用**：避免在每个 Repository 中重复实现相同的 CRUD 操作
2. **类型安全**：使用泛型确保类型安全
3. **灵活性**：可以覆盖基类方法或添加自定义方法
4. **一致性**：所有 Repository 使用相同的接口和实现

## 注意事项

1. **code 字段**：`get_by_code()` 方法要求模型必须有 `code` 字段，否则会抛出 `AttributeError`
2. **created_at 字段**：`get_list()` 的默认排序使用 `created_at` 字段，如果模型没有此字段，需要显式指定 `order_by`
3. **自定义方法**：可以添加任何自定义的查询方法，不受基类限制

