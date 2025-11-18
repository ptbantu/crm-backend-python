# BaseService - 通用服务基类

`BaseService` 提供了通用的服务层验证方法，减少代码重复。

## 功能

### 验证方法

- `validate_not_exists()` - 验证字段值不存在（用于创建时检查唯一性）
- `validate_exists()` - 验证实体存在
- `validate_active()` - 验证实体处于激活状态

## 使用示例

### 基础用法

```python
from common.utils.service import BaseService
from service_management.repositories.product_repository import ProductRepository
from sqlalchemy.ext.asyncio import AsyncSession

class ProductService(BaseService[ProductRepository]):
    """产品服务"""
    
    def __init__(self, db: AsyncSession):
        repository = ProductRepository(db)
        super().__init__(db, repository)
    
    async def create_product(self, request: ProductCreateRequest):
        """创建产品"""
        # 使用基类的验证方法
        await self.validate_not_exists(
            field_name="产品编码",
            field_value=request.code,
            get_method="get_by_code",
            error_message=f"产品编码 {request.code} 已存在"
        )
        
        # 创建产品...
        product = Product(...)
        return await self.repo.create(product)
```

### 验证实体存在和激活状态

```python
class ProductService(BaseService[ProductRepository]):
    async def update_product(self, product_id: str, request: ProductUpdateRequest):
        """更新产品"""
        # 验证产品存在
        await self.validate_exists(
            entity_id=product_id,
            entity_name="产品"
        )
        
        # 验证产品激活状态
        await self.validate_active(
            entity_id=product_id,
            entity_name="产品"
        )
        
        # 更新产品...
        product = await self.repo.get_by_id(product_id)
        # ...
```

## 优势

1. **代码复用**：避免在每个 Service 中重复实现相同的验证逻辑
2. **一致性**：所有 Service 使用相同的验证方法和错误消息格式
3. **灵活性**：可以覆盖基类方法或添加自定义验证方法

## 注意事项

1. **Repository 方法**：`validate_not_exists()` 需要 Repository 有对应的方法（如 `get_by_code`）
2. **is_active 字段**：`validate_active()` 要求模型有 `is_active` 字段
3. **自定义验证**：可以添加任何自定义的验证方法，不受基类限制

