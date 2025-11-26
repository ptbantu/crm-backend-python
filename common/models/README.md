# 共享模型定义 (Common Models)

## 概述

`common/models/` 目录包含所有微服务共享的表结构定义，用于避免代码重复。

**重要原则**：
- ✅ 所有表结构定义统一放在 `common/models/` 中
- ✅ 每个微服务按需导入自己需要的模型
- ✅ 这些模型只用于代码层面的类型定义和 relationship
- ✅ **不实际创建表**（数据库表结构由 `init-scripts/schema.sql` 统一管理）
- ✅ 所有微服务共享同一个 `Base`（来自 `common.database`）

## 目录结构

```
common/models/
├── __init__.py          # 导出所有共享模型
├── user.py              # 用户模型
├── organization.py      # 组织模型
├── customer.py          # 客户模型
└── README.md            # 本文档
```

## 使用方法

### 1. 在微服务中导入共享模型

```python
# order_workflow_service/models/lead.py
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from order_workflow_service.database import Base
# 从共享模型导入 User 和 Customer
from common.models import User, Customer

class Lead(Base):
    __tablename__ = "leads"
    
    # 使用外键引用共享模型
    owner_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=True)
    
    # 使用 relationship（直接使用导入的类，而不是字符串）
    owner = relationship(User, foreign_keys=[owner_user_id], backref="owned_leads")
    customer = relationship(Customer, foreign_keys=[customer_id], backref="leads")
```

### 2. 在微服务的 `__init__.py` 中重新导出

```python
# order_workflow_service/models/__init__.py
from order_workflow_service.models.lead import Lead
# 从共享模型导入并重新导出
from common.models import User, Customer

__all__ = [
    "Lead",
    "User",      # 从 common.models 导入
    "Customer",  # 从 common.models 导入
]
```

### 3. 在其他地方使用

```python
# order_workflow_service/repositories/lead_repository.py
from order_workflow_service.models import Lead, User, Customer

# 现在可以使用 relationship 进行查询
async def get_lead_with_owner(lead_id: str):
    lead = await session.get(Lead, lead_id)
    # 可以访问 lead.owner 和 lead.customer
    return lead
```

## 当前共享模型列表

### User (用户)
- **表名**: `users`
- **服务**: `foundation_service`（主服务）
- **用途**: 所有微服务共享的用户表结构定义

### Organization (组织)
- **表名**: `organizations`
- **服务**: `foundation_service`（主服务）
- **用途**: 所有微服务共享的组织表结构定义

### Customer (客户)
- **表名**: `customers`
- **服务**: `service_management`（主服务）
- **用途**: 所有微服务共享的客户表结构定义

## 添加新的共享模型

1. 在 `common/models/` 中创建新的模型文件（如 `product.py`）
2. 在 `common/models/__init__.py` 中导出新模型
3. 各微服务按需导入使用

示例：

```python
# common/models/product.py
from sqlalchemy import Column, String
from common.database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    # ...
```

```python
# common/models/__init__.py
from common.models.user import User
from common.models.product import Product  # 新增

__all__ = [
    "User",
    "Product",  # 新增
]
```

## 注意事项

1. **不要重复定义**：如果模型已在 `common/models/` 中定义，不要在微服务中重复定义
2. **使用共享 Base**：所有模型必须使用 `common.database.Base`，确保共享元数据
3. **外键约束**：可以使用 `ForeignKey` 引用共享模型，但要注意跨服务的情况
4. **Relationship**：使用导入的类（而不是字符串）定义 relationship，以获得更好的类型支持

## 迁移指南

如果之前在各微服务中重复定义了模型，按以下步骤迁移：

1. 将模型定义移动到 `common/models/`
2. 更新微服务中的导入语句：`from common.models import User, Customer`
3. 删除微服务中重复的模型文件
4. 更新 `__init__.py` 中的导入

示例：

```python
# 之前：order_workflow_service/models/user.py
class User(Base):
    # ...

# 之后：删除该文件，改为从 common.models 导入
from common.models import User
```

