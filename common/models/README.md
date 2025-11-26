# 共享模型定义 (Common Models)

## 概述

`common/models/` 目录包含所有微服务共享的表结构定义，用于避免代码重复。

**重要原则**：
- ✅ 所有表结构定义统一放在 `common/models/` 中
- ✅ 每个微服务按需导入自己需要的模型
- ✅ 这些模型只用于代码层面的类型定义和 relationship
- ✅ **不实际创建表**（数据库表结构由 `init-scripts/schema.sql` 统一管理）
- ✅ 所有微服务共享同一个 `Base`（来自 `common.database`）
- ✅ 跨服务的外键约束已移除，只保留字段定义和索引

## 目录结构

```
common/models/
├── __init__.py                    # 导出所有共享模型
├── README.md                      # 本文档
│
├── Foundation Service Models
├── user.py                        # 用户模型
├── organization.py                # 组织模型
├── role.py                        # 角色模型
├── organization_employee.py      # 组织员工模型
├── user_role.py                   # 用户角色关联模型
├── organization_domain.py        # 组织领域模型
├── permission.py                  # 权限、菜单模型
│
├── Service Management Models
├── customer.py                    # 客户模型
├── customer_source.py            # 客户来源模型
├── customer_channel.py           # 客户渠道模型
├── contact.py                     # 联系人模型
├── product.py                     # 产品模型
├── product_category.py            # 产品分类模型
├── product_price.py               # 产品价格模型
├── product_price_history.py       # 产品价格历史模型
├── vendor_product.py              # 供应商产品模型
├── vendor_product_financial.py    # 供应商产品财务模型
├── service_record.py              # 服务记录模型
├── service_type.py                # 服务类型模型
│
└── Order Workflow Service Models
    ├── lead.py                    # 线索模型
    ├── lead_pool.py               # 线索池模型
    ├── lead_follow_up.py          # 线索跟进记录模型
    ├── lead_note.py               # 线索备注模型
    ├── order.py                   # 订单模型
    ├── order_item.py              # 订单项模型
    ├── order_comment.py           # 订单评论模型
    ├── order_file.py              # 订单文件模型
    ├── collection_task.py         # 催款任务模型
    ├── notification.py            # 通知模型
    ├── temporary_link.py          # 临时链接模型
    ├── workflow_definition.py     # 工作流定义模型
    ├── workflow_instance.py       # 工作流实例模型
    ├── workflow_task.py           # 工作流任务模型
    ├── workflow_transition.py     # 工作流流转记录模型
    ├── customer_level.py          # 客户等级配置模型
    └── follow_up_status.py        # 跟进状态配置模型
```

## 使用方法

### 1. 在微服务中导入共享模型

```python
# order_workflow_service/services/lead_service.py
from common.models import Lead, User, Customer

class LeadService:
    async def get_lead(self, lead_id: str):
        # 使用共享模型
        lead = await self.db.get(Lead, lead_id)
        return lead
```

### 2. 在微服务的 `__init__.py` 中重新导出（可选，保持向后兼容）

```python
# order_workflow_service/models/__init__.py
from common.models import (
    Lead,
    Order,
    User,
    Customer,
)

__all__ = [
    "Lead",
    "Order",
    "User",
    "Customer",
]
```

### 3. 在其他地方使用

```python
# order_workflow_service/repositories/lead_repository.py
from common.models import Lead, User, Customer

# 现在可以使用 relationship 进行查询
async def get_lead_with_owner(lead_id: str):
    lead = await session.get(Lead, lead_id)
    # 可以访问 lead.owner 和 lead.customer
    return lead
```

## 当前共享模型列表

### Foundation Service Models

#### User (用户)
- **表名**: `users`
- **服务**: `foundation_service`（主服务）
- **用途**: 所有微服务共享的用户表结构定义

#### Organization (组织)
- **表名**: `organizations`
- **服务**: `foundation_service`（主服务）
- **用途**: 所有微服务共享的组织表结构定义

#### Role (角色)
- **表名**: `roles`
- **服务**: `foundation_service`（主服务）
- **用途**: 角色表结构定义

#### OrganizationEmployee (组织员工)
- **表名**: `organization_employees`
- **服务**: `foundation_service`（主服务）
- **用途**: 组织员工关联表结构定义
- **注意**: 移除了跨服务的外键引用，只保留字段定义

#### UserRole (用户角色)
- **表名**: `user_roles`
- **服务**: `foundation_service`（主服务）
- **用途**: 用户角色关联表结构定义

#### OrganizationDomain (组织领域)
- **表名**: `organization_domains`
- **服务**: `foundation_service`（主服务）
- **用途**: 组织领域表结构定义

#### Permission, Menu (权限、菜单)
- **表名**: `permissions`, `role_permissions`, `menus`, `menu_permissions`
- **服务**: `foundation_service`（主服务）
- **用途**: 权限和菜单表结构定义

### Service Management Models

#### Customer (客户)
- **表名**: `customers`
- **服务**: `service_management`（主服务）
- **用途**: 所有微服务共享的客户表结构定义
- **注意**: 移除了跨服务的外键引用（`customer_sources`、`customer_channels`、`organizations`），只保留本地可用的外键（`users`）

#### CustomerSource (客户来源)
- **表名**: `customer_sources`
- **服务**: `service_management`（主服务）
- **用途**: 客户来源表结构定义

#### CustomerChannel (客户渠道)
- **表名**: `customer_channels`
- **服务**: `service_management`（主服务）
- **用途**: 客户渠道表结构定义

#### Contact (联系人)
- **表名**: `contacts`
- **服务**: `service_management`（主服务）
- **用途**: 联系人表结构定义

#### Product (产品)
- **表名**: `products`
- **服务**: `service_management`（主服务）
- **用途**: 产品表结构定义

#### ProductCategory (产品分类)
- **表名**: `product_categories`
- **服务**: `service_management`（主服务）
- **用途**: 产品分类表结构定义

#### ProductPrice (产品价格)
- **表名**: `product_prices`
- **服务**: `service_management`（主服务）
- **用途**: 产品价格表结构定义

#### ProductPriceHistory (产品价格历史)
- **表名**: `product_price_history`
- **服务**: `service_management`（主服务）
- **用途**: 产品价格历史表结构定义

#### VendorProduct (供应商产品)
- **表名**: `vendor_products`
- **服务**: `service_management`（主服务）
- **用途**: 供应商产品表结构定义

#### VendorProductFinancial (供应商产品财务)
- **表名**: `vendor_product_financial`
- **服务**: `service_management`（主服务）
- **用途**: 供应商产品财务表结构定义

#### ServiceRecord (服务记录)
- **表名**: `service_records`
- **服务**: `service_management`（主服务）
- **用途**: 服务记录表结构定义

#### ServiceType (服务类型)
- **表名**: `service_types`
- **服务**: `service_management`（主服务）
- **用途**: 服务类型表结构定义

### Order Workflow Service Models

#### Lead (线索)
- **表名**: `leads`
- **服务**: `order_workflow_service`（主服务）
- **用途**: 线索表结构定义
- **注意**: 移除了跨服务的外键引用，只保留同服务内的外键（`lead_pools`, `customer_levels`）

#### LeadPool (线索池)
- **表名**: `lead_pools`
- **服务**: `order_workflow_service`（主服务）
- **用途**: 线索池表结构定义

#### LeadFollowUp (线索跟进记录)
- **表名**: `lead_follow_ups`
- **服务**: `order_workflow_service`（主服务）
- **用途**: 线索跟进记录表结构定义

#### LeadNote (线索备注)
- **表名**: `lead_notes`
- **服务**: `order_workflow_service`（主服务）
- **用途**: 线索备注表结构定义

#### Order (订单)
- **表名**: `orders`
- **服务**: `order_workflow_service`（主服务）
- **用途**: 订单表结构定义
- **注意**: 移除了跨服务的外键引用（`customers`, `products`, `service_records`, `users`, `order_statuses`），只保留同服务内的外键（`workflow_instances`）

#### OrderItem (订单项)
- **表名**: `order_items`
- **服务**: `order_workflow_service`（主服务）
- **用途**: 订单项表结构定义
- **注意**: 移除了跨服务的外键引用（`products`, `service_types`），只保留同服务内的外键（`orders`）

#### OrderComment (订单评论)
- **表名**: `order_comments`
- **服务**: `order_workflow_service`（主服务）
- **用途**: 订单评论表结构定义
- **注意**: 移除了跨服务的外键引用（`order_stages`），只保留同服务内的外键（`orders`）

#### OrderFile (订单文件)
- **表名**: `order_files`
- **服务**: `order_workflow_service`（主服务）
- **用途**: 订单文件表结构定义
- **注意**: 移除了跨服务的外键引用（`order_stages`），只保留同服务内的外键（`orders`, `order_items`）

#### CollectionTask (催款任务)
- **表名**: `collection_tasks`
- **服务**: `order_workflow_service`（主服务）
- **用途**: 催款任务表结构定义
- **注意**: 移除了跨服务的外键引用（`payment_stages`, `users`），只保留同服务内的外键（`orders`）

#### Notification (通知)
- **表名**: `notifications`
- **服务**: `order_workflow_service`（主服务）
- **用途**: 通知表结构定义
- **注意**: 移除了跨服务的外键引用（`users`），但保留了 relationship 定义

#### TemporaryLink (临时链接)
- **表名**: `temporary_links`
- **服务**: `order_workflow_service`（主服务）
- **用途**: 临时链接表结构定义
- **注意**: 移除了跨服务的外键引用（`users`）

#### WorkflowDefinition (工作流定义)
- **表名**: `workflow_definitions`
- **服务**: `order_workflow_service`（主服务）
- **用途**: 工作流定义表结构定义
- **注意**: 移除了跨服务的外键引用（`users`）

#### WorkflowInstance (工作流实例)
- **表名**: `workflow_instances`
- **服务**: `order_workflow_service`（主服务）
- **用途**: 工作流实例表结构定义
- **注意**: 移除了跨服务的外键引用（`users`），只保留同服务内的外键（`workflow_definitions`）

#### WorkflowTask (工作流任务)
- **表名**: `workflow_tasks`
- **服务**: `order_workflow_service`（主服务）
- **用途**: 工作流任务表结构定义
- **注意**: 移除了跨服务的外键引用（`users`, `roles`），只保留同服务内的外键（`workflow_instances`）

#### WorkflowTransition (工作流流转记录)
- **表名**: `workflow_transitions`
- **服务**: `order_workflow_service`（主服务）
- **用途**: 工作流流转记录表结构定义
- **注意**: 移除了跨服务的外键引用（`users`），只保留同服务内的外键（`workflow_instances`）

#### CustomerLevel (客户等级配置)
- **表名**: `customer_levels`
- **服务**: `order_workflow_service`（主服务）
- **用途**: 客户等级配置表结构定义

#### FollowUpStatus (跟进状态配置)
- **表名**: `follow_up_statuses`
- **服务**: `order_workflow_service`（主服务）
- **用途**: 跟进状态配置表结构定义

## 添加新的共享模型

1. 在 `common/models/` 中创建新的模型文件（如 `new_model.py`）
2. 使用 `common.database.Base` 作为基类
3. 移除跨服务的外键约束，只保留字段定义和索引
4. 在 `common/models/__init__.py` 中导出新模型
5. 各微服务按需导入使用

示例：

```python
# common/models/new_model.py
from sqlalchemy import Column, String, Text
from common.database import Base
import uuid

class NewModel(Base):
    __tablename__ = "new_models"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    # 跨服务引用不使用外键，只保留字段和索引
    organization_id = Column(String(36), nullable=True, index=True, comment="组织ID（跨服务引用）")
```

```python
# common/models/__init__.py
from common.models.new_model import NewModel

__all__ = [
    # ... existing models ...
    "NewModel",
]
```

## 注意事项

1. **不要重复定义**：如果模型已在 `common/models/` 中定义，不要在微服务中重复定义
2. **使用共享 Base**：所有模型必须使用 `common.database.Base`，确保共享元数据
3. **外键约束**：
   - 同服务内的表可以使用 `ForeignKey` 引用
   - **跨服务的外键应该移除**，只保留字段定义（无外键约束）和索引
   - 例如：`customers.organization_id` 引用 `foundation_service` 的 `organizations` 表，不应使用外键
4. **Relationship**：使用导入的类（而不是字符串）定义 relationship，以获得更好的类型支持
5. **导入顺序**：在 `__init__.py` 中导入时，注意循环依赖问题，必要时使用延迟导入

## 迁移指南

如果之前在各微服务中重复定义了模型，按以下步骤迁移：

1. 将模型定义移动到 `common/models/`
2. 移除跨服务的外键约束，只保留字段定义和索引
3. 更新微服务中的导入语句：`from common.models import ModelName`
4. 删除微服务中重复的模型文件（保留 `__init__.py`）
5. 更新 `__init__.py` 中的导入

示例：

```python
# 之前：order_workflow_service/models/lead.py
class Lead(Base):
    organization_id = Column(String(36), ForeignKey("organizations.id"), ...)
    # ...

# 之后：common/models/lead.py
class Lead(Base):
    organization_id = Column(String(36), nullable=True, index=True, comment="组织ID（跨服务引用）")
    # ...

# 使用：order_workflow_service/services/lead_service.py
from common.models import Lead
```
