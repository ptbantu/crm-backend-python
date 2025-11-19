# 订单与工作流表关系文档

## 一、概述

本文档详细说明订单管理和工作流引擎模块中各个表之间的关系逻辑，包括订单、订单项、订单阶段、工作流定义、工作流实例、任务、评论、文件等核心表的关系设计。

## 二、核心表结构

### 2.1 订单域（Order Domain）

#### orders（订单表）

**用途**：订单主表，存储订单基本信息

**关键字段**：
- `id`: 主键
- `order_number`: 订单号（唯一）
- `title`: 订单标题
- `customer_id`: 客户ID（必填）
- `service_record_id`: 关联的服务记录ID（可选）
- `workflow_instance_id`: 关联的工作流实例ID（可选）
- `sales_user_id`: 销售用户ID（必填）
- `total_amount`: 订单总金额（从订单项汇总）
- `final_amount`: 最终金额（total_amount - discount_amount）
- `status_code`: 订单状态（submitted, approved, assigned, processing, completed, cancelled）
- `entry_city`: 入境城市（来自 EVOA）
- `passport_id`: 护照ID（来自 EVOA）
- `processor`: 处理器（来自 EVOA）

**关联关系**：
- `customer_id` → `customers.id` (ON DELETE RESTRICT)
- `service_record_id` → `service_records.id` (ON DELETE SET NULL)
- `workflow_instance_id` → `workflow_instances.id` (ON DELETE SET NULL)
- `sales_user_id` → `users.id` (ON DELETE RESTRICT)
- `product_id` → `products.id` (ON DELETE SET NULL) - 保留用于向后兼容

**业务逻辑**：
- 一个客户可以有多条服务记录
- 一个服务记录可以生成多个订单
- 一个订单可以包含多个订单项
- 订单总金额从订单项汇总计算

#### order_items（订单项表）

**用途**：订单项表，一个订单可以包含多个订单项

**关键字段**：
- `id`: 主键
- `order_id`: 订单ID（必填）
- `item_number`: 订单项序号（1, 2, 3...）
- `product_id`: 产品/服务ID
- `product_name_zh`: 产品名称（中文）
- `product_name_id`: 产品名称（印尼语）
- `service_type_id`: 服务类型ID
- `service_type_name_zh`: 服务类型名称（中文）
- `service_type_name_id`: 服务类型名称（印尼语）
- `quantity`: 数量
- `unit_price`: 单价
- `discount_amount`: 折扣金额
- `item_amount`: 订单项金额（quantity * unit_price - discount_amount）
- `status`: 订单项状态（pending, in_progress, completed, cancelled）

**关联关系**：
- `order_id` → `orders.id` (ON DELETE CASCADE)
- `product_id` → `products.id` (ON DELETE SET NULL)
- `service_type_id` → `service_types.id` (ON DELETE SET NULL)

**业务逻辑**：
- 一个订单可以包含多个订单项
- 每个订单项对应一个产品/服务
- 每个订单项可以独立管理状态
- 订单项金额 = quantity * unit_price - discount_amount

#### order_stages（订单阶段表）

**用途**：订单处理阶段，记录订单的处理进度

**关键字段**：
- `id`: 主键
- `order_id`: 订单ID（必填）
- `stage_name`: 阶段名称
- `stage_code`: 阶段代码
- `stage_order`: 阶段序号（1, 2, 3...）
- `status`: 阶段状态（pending, in_progress, completed, cancelled）
- `progress_percent`: 进度百分比（0-100）
- `assigned_to_user_id`: 分配给的用户ID

**关联关系**：
- `order_id` → `orders.id` (ON DELETE CASCADE)
- `assigned_to_user_id` → `users.id` (ON DELETE SET NULL)

**业务逻辑**：
- 一个订单可以有多个处理阶段
- 阶段按序号顺序执行
- 每个阶段可以分配给不同的用户

#### order_assignments（订单分配表）

**用途**：记录订单的分配情况

**关键字段**：
- `id`: 主键
- `order_id`: 订单ID（必填）
- `assigned_to_user_id`: 分配给的用户ID
- `assignment_type`: 分配类型（operation, sales等）
- `is_primary`: 是否主要分配

**关联关系**：
- `order_id` → `orders.id` (ON DELETE CASCADE)
- `assigned_to_user_id` → `users.id` (ON DELETE RESTRICT)

**业务逻辑**：
- 一个订单可以分配给多个用户
- 可以标记主要分配人

#### order_comments（订单评论表）

**用途**：订单评论和沟通记录

**关键字段**：
- `id`: 主键
- `order_id`: 订单ID（必填）
- `order_stage_id`: 关联的订单阶段ID（可选）
- `comment_type`: 评论类型（general, internal, customer, system）
- `content_zh`: 评论内容（中文）
- `content_id`: 评论内容（印尼语）
- `is_internal`: 是否内部评论（客户不可见）
- `is_pinned`: 是否置顶
- `replied_to_comment_id`: 回复的评论ID（支持回复）

**关联关系**：
- `order_id` → `orders.id` (ON DELETE CASCADE)
- `order_stage_id` → `order_stages.id` (ON DELETE SET NULL)
- `replied_to_comment_id` → `order_comments.id` (ON DELETE SET NULL)
- `created_by` → `users.id` (ON DELETE SET NULL)

**业务逻辑**：
- 一个订单可以有多个评论
- 评论可以关联到订单阶段
- 支持回复评论
- 支持置顶评论

#### order_files（订单文件表）

**用途**：订单相关文件（护照、签证、文档等）

**关键字段**：
- `id`: 主键
- `order_id`: 订单ID（必填）
- `order_item_id`: 关联的订单项ID（可选）
- `order_stage_id`: 关联的订单阶段ID（可选）
- `file_category`: 文件分类（passport, visa, document, other）
- `file_name_zh`: 文件名称（中文）
- `file_name_id`: 文件名称（印尼语）
- `file_path`: 文件存储路径
- `file_url`: 文件访问URL
- `file_size`: 文件大小
- `is_required`: 是否必需文件
- `is_verified`: 是否已验证

**关联关系**：
- `order_id` → `orders.id` (ON DELETE CASCADE)
- `order_item_id` → `order_items.id` (ON DELETE SET NULL)
- `order_stage_id` → `order_stages.id` (ON DELETE SET NULL)
- `uploaded_by` → `users.id` (ON DELETE SET NULL)
- `verified_by` → `users.id` (ON DELETE SET NULL)

**业务逻辑**：
- 文件可以关联到订单、订单项、订单阶段
- 不同订单项可以上传不同文件
- 不同阶段可以上传不同文件
- 文件存储使用 MinIO 对象存储

### 2.2 工作流域（Workflow Domain）

#### workflow_definitions（工作流定义表）

**用途**：工作流定义，存储工作流的配置信息

**关键字段**：
- `id`: 主键
- `name_zh`: 工作流名称（中文）
- `name_id`: 工作流名称（印尼语）
- `code`: 工作流代码（唯一）
- `description_zh`: 描述（中文）
- `description_id`: 描述（印尼语）
- `workflow_type`: 工作流类型（order_approval, delivery_review, payment_approval）
- `definition_json`: 工作流定义（JSON 格式，包含阶段和流转规则）
- `version`: 版本号
- `is_active`: 是否激活

**关联关系**：
- `created_by` → `users.id` (ON DELETE SET NULL)

**业务逻辑**：
- 工作流定义使用 JSON 格式存储
- 支持版本管理
- 可以激活/停用工作流定义

#### workflow_instances（工作流实例表）

**用途**：工作流实例，记录工作流的执行情况

**关键字段**：
- `id`: 主键
- `workflow_definition_id`: 工作流定义ID
- `business_type`: 业务类型（order, service_record）
- `business_id`: 业务对象ID（订单ID或服务记录ID）
- `current_stage`: 当前阶段
- `status`: 实例状态（running, completed, cancelled, suspended）
- `started_by`: 启动人ID
- `variables`: 流程变量（JSON）

**关联关系**：
- `workflow_definition_id` → `workflow_definitions.id` (ON DELETE SET NULL)
- `started_by` → `users.id` (ON DELETE SET NULL)

**业务逻辑**：
- 一个工作流定义可以创建多个实例
- 实例关联到业务对象（订单或服务记录）
- 实例根据定义自动流转

#### workflow_tasks（工作流任务表）

**用途**：工作流任务，记录需要处理的任务

**关键字段**：
- `id`: 主键
- `workflow_instance_id`: 工作流实例ID
- `task_name_zh`: 任务名称（中文）
- `task_name_id`: 任务名称（印尼语）
- `task_code`: 任务代码
- `task_type`: 任务类型（user_task, service_task, script_task）
- `assigned_to_user_id`: 分配给的用户ID
- `assigned_to_role_id`: 分配给的角色ID
- `status`: 任务状态（pending, in_progress, completed, cancelled）
- `due_date`: 到期日期

**关联关系**：
- `workflow_instance_id` → `workflow_instances.id` (ON DELETE CASCADE)
- `assigned_to_user_id` → `users.id` (ON DELETE SET NULL)
- `assigned_to_role_id` → `roles.id` (ON DELETE SET NULL)
- `completed_by` → `users.id` (ON DELETE SET NULL)

**业务逻辑**：
- 一个工作流实例可以有多个任务
- 任务可以分配给用户或角色
- 任务完成后，工作流自动流转

#### workflow_transitions（工作流流转记录表）

**用途**：工作流流转记录，记录工作流的流转历史

**关键字段**：
- `id`: 主键
- `workflow_instance_id`: 工作流实例ID
- `from_stage`: 源阶段
- `to_stage`: 目标阶段
- `transition_condition`: 流转条件
- `triggered_by`: 触发人ID
- `triggered_at`: 触发时间
- `notes`: 备注

**关联关系**：
- `workflow_instance_id` → `workflow_instances.id` (ON DELETE CASCADE)
- `triggered_by` → `users.id` (ON DELETE SET NULL)

**业务逻辑**：
- 记录每次工作流流转
- 可以查看工作流流转历史

## 三、表关系图

### 3.1 订单域关系

```
customers (客户)
    │
    ├── service_records (服务记录)
    │       │
    │       └── orders (订单)
    │               │
    │               ├── order_items (订单项)
    │               │       └── products (产品)
    │               │
    │               ├── order_stages (订单阶段)
    │               │
    │               ├── order_assignments (订单分配)
    │               │       └── users (用户)
    │               │
    │               ├── order_comments (订单评论)
    │               │       └── order_stages (订单阶段)
    │               │
    │               └── order_files (订单文件)
    │                       ├── order_items (订单项)
    │                       └── order_stages (订单阶段)
    │
    └── orders (订单) [直接关联]
```

### 3.2 工作流域关系

```
workflow_definitions (工作流定义)
    │
    └── workflow_instances (工作流实例)
            │
            ├── orders (订单) [business_type='order']
            │
            ├── service_records (服务记录) [business_type='service_record']
            │
            ├── workflow_tasks (工作流任务)
            │       ├── users (用户)
            │       └── roles (角色)
            │
            └── workflow_transitions (工作流流转记录)
```

### 3.3 完整关系图

```
customers
    │
    ├── service_records
    │       │
    │       └── orders ──┐
    │                     │
    └── orders ───────────┼── workflow_instances ─── workflow_definitions
                          │
                          ├── order_items ─── products
                          │
                          ├── order_stages
                          │
                          ├── order_assignments ─── users
                          │
                          ├── order_comments
                          │       └── order_stages
                          │
                          └── order_files
                                  ├── order_items
                                  └── order_stages
```

## 四、外键约束说明

### 4.1 级联删除规则

- `orders` → `order_items`: CASCADE（删除订单时，级联删除订单项）
- `orders` → `order_stages`: CASCADE（删除订单时，级联删除订单阶段）
- `orders` → `order_assignments`: CASCADE（删除订单时，级联删除订单分配）
- `orders` → `order_comments`: CASCADE（删除订单时，级联删除订单评论）
- `orders` → `order_files`: CASCADE（删除订单时，级联删除订单文件）
- `workflow_instances` → `workflow_tasks`: CASCADE（删除工作流实例时，级联删除任务）
- `workflow_instances` → `workflow_transitions`: CASCADE（删除工作流实例时，级联删除流转记录）

### 4.2 限制删除规则

- `customers` → `orders`: RESTRICT（有订单的客户不能删除）
- `users` → `orders`: RESTRICT（有订单的销售用户不能删除）

### 4.3 置空删除规则

- `products` → `order_items`: SET NULL（删除产品时，订单项的产品ID置空）
- `service_types` → `order_items`: SET NULL（删除服务类型时，订单项的服务类型ID置空）
- `order_stages` → `order_comments`: SET NULL（删除订单阶段时，评论的阶段ID置空）
- `order_items` → `order_files`: SET NULL（删除订单项时，文件的订单项ID置空）
- `order_stages` → `order_files`: SET NULL（删除订单阶段时，文件的阶段ID置空）

## 五、索引设计

### 5.1 订单表索引
- `ux_orders_number`: 订单号唯一索引
- `ix_orders_customer`: 客户ID索引
- `ix_orders_service_record`: 服务记录ID索引
- `ix_orders_status`: 订单状态索引
- `ix_orders_created`: 创建时间索引（DESC）

### 5.2 订单项表索引
- `ix_order_items_order`: 订单ID索引
- `ix_order_items_product`: 产品ID索引
- `ix_order_items_service_type`: 服务类型ID索引
- `ix_order_items_status`: 订单项状态索引
- `ix_order_items_item_number`: 订单ID + 订单项序号复合索引

### 5.3 订单阶段表索引
- `ix_order_stages_order`: 订单ID索引
- `ix_order_stages_assigned`: 分配用户ID索引
- `ix_order_stages_status`: 阶段状态索引

### 5.4 订单评论表索引
- `ix_order_comments_order`: 订单ID索引
- `ix_order_comments_stage`: 订单阶段ID索引
- `ix_order_comments_created_by`: 创建人ID索引
- `ix_order_comments_created_at`: 创建时间索引（DESC）

### 5.5 订单文件表索引
- `ix_order_files_order`: 订单ID索引
- `ix_order_files_item`: 订单项ID索引
- `ix_order_files_stage`: 订单阶段ID索引
- `ix_order_files_category`: 文件分类索引
- `ix_order_files_uploaded_by`: 上传人ID索引
- `ix_order_files_created_at`: 创建时间索引（DESC）

### 5.6 工作流表索引
- `ux_workflow_definitions_code`: 工作流定义代码唯一索引
- `ix_workflow_instances_definition`: 工作流定义ID索引
- `ix_workflow_instances_business`: 业务类型 + 业务ID复合索引
- `ix_workflow_instances_status`: 实例状态索引
- `ix_workflow_tasks_instance`: 工作流实例ID索引
- `ix_workflow_tasks_assigned_user`: 分配用户ID索引
- `ix_workflow_tasks_assigned_role`: 分配角色ID索引
- `ix_workflow_tasks_status`: 任务状态索引

## 六、数据完整性约束

### 6.1 检查约束

#### orders 表
- `chk_orders_amounts_nonneg`: 金额字段必须 >= 0
  - quantity >= 0
  - unit_price >= 0
  - total_amount >= 0
  - discount_amount >= 0
  - final_amount >= 0

#### order_items 表
- `chk_order_items_amounts_nonneg`: 金额字段必须 >= 0
  - quantity >= 0
  - unit_price >= 0
  - discount_amount >= 0
  - item_amount >= 0

#### order_stages 表
- `chk_order_stages_progress_range`: 进度百分比必须在 0-100 之间

#### order_files 表
- `chk_order_files_file_size_nonneg`: 文件大小必须 >= 0

### 6.2 唯一约束

- `orders.order_number`: 订单号唯一
- `workflow_definitions.code`: 工作流定义代码唯一
- `order_items(order_id, item_number)`: 同一订单内，订单项序号唯一

## 七、数据冗余设计

### 7.1 冗余字段说明

为了提升查询性能，以下字段采用冗余设计：

#### orders 表
- `product_name`: 产品名称（冗余，从 products 表同步）
- `sales_username`: 销售用户名（冗余，从 users 表同步）

#### order_items 表
- `product_name_zh`, `product_name_id`: 产品名称（冗余，从 products 表同步）
- `service_type_name_zh`, `service_type_name_id`: 服务类型名称（冗余，从 service_types 表同步）

#### order_comments 表
- `content_zh`, `content_id`: 评论内容（双语，冗余存储）

#### order_files 表
- `file_name_zh`, `file_name_id`: 文件名称（双语，冗余存储）

### 7.2 冗余字段更新策略

- 创建时：从关联表同步冗余字段
- 更新时：如果关联表字段更新，需要同步更新冗余字段
- 查询时：优先使用冗余字段，减少 JOIN 查询

## 八、业务关系总结

### 8.1 一对多关系

1. **客户 → 服务记录**：一个客户可以有多条服务记录
2. **客户 → 订单**：一个客户可以有多个订单
3. **服务记录 → 订单**：一个服务记录可以生成多个订单
4. **订单 → 订单项**：一个订单可以包含多个订单项
5. **订单 → 订单阶段**：一个订单可以有多个处理阶段
6. **订单 → 订单分配**：一个订单可以分配给多个用户
7. **订单 → 订单评论**：一个订单可以有多个评论
8. **订单 → 订单文件**：一个订单可以有多个文件
9. **工作流定义 → 工作流实例**：一个工作流定义可以创建多个实例
10. **工作流实例 → 工作流任务**：一个工作流实例可以有多个任务
11. **工作流实例 → 工作流流转记录**：一个工作流实例可以有多个流转记录

### 8.2 多对一关系

1. **订单项 → 订单**：多个订单项属于一个订单
2. **订单阶段 → 订单**：多个订单阶段属于一个订单
3. **订单分配 → 订单**：多个订单分配属于一个订单
4. **订单评论 → 订单**：多个订单评论属于一个订单
5. **订单文件 → 订单**：多个订单文件属于一个订单
6. **订单文件 → 订单项**：多个订单文件可以属于一个订单项
7. **订单文件 → 订单阶段**：多个订单文件可以属于一个订单阶段
8. **工作流实例 → 工作流定义**：多个工作流实例属于一个工作流定义
9. **工作流任务 → 工作流实例**：多个工作流任务属于一个工作流实例

### 8.3 多对多关系

通过中间表实现：
- **订单 ↔ 用户**：通过 `order_assignments` 表
- **工作流任务 ↔ 用户**：通过 `workflow_tasks.assigned_to_user_id`
- **工作流任务 ↔ 角色**：通过 `workflow_tasks.assigned_to_role_id`


