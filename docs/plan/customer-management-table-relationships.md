# 客户管理表关系逻辑文档

## 一、概述

本文档详细说明客户管理模块中各个表之间的关系逻辑，包括客户、联系人、服务记录、订单、付款、文档等核心表的关系设计。

## 二、核心表结构

### 2.1 客户域（Customer Domain）

#### customers（客户表）

**用途**：客户主表，支持个人客户和组织客户

**关键字段**：
- `id`: 主键
- `name`: 客户名称（必填）
- `code`: 客户编码（唯一）
- `customer_type`: 客户类型
  - `'individual'`: 个人客户
  - `'organization'`: 组织客户
- `customer_source_type`: 客户来源类型
  - `'own'`: 内部客户（直接客户）
  - `'agent'`: 渠道客户（通过代理/渠道获得）
- `parent_customer_id`: 父客户ID（支持组织下挂个人客户）
- `owner_user_id`: 内部客户的所有者（SALES角色用户）
- `agent_id`: 渠道客户的所有者（agent组织）
- `source_id`: 客户来源ID
- `channel_id`: 客户渠道ID

**关联关系**：
- `parent_customer_id` → `customers.id` (ON DELETE SET NULL) - 自关联，支持层级结构
- `owner_user_id` → `users.id` (ON DELETE SET NULL) - 内部客户所有者
- `agent_id` → `organizations.id` (ON DELETE SET NULL) - 渠道客户所有者
- `source_id` → `customer_sources.id` (ON DELETE SET NULL) - 客户来源
- `channel_id` → `customer_channels.id` (ON DELETE SET NULL) - 客户渠道

**层级关系**：
```
组织客户 (parent_customer_id = NULL)
└── 个人客户1 (parent_customer_id = 组织客户.id)
└── 个人客户2 (parent_customer_id = 组织客户.id)
```

#### customer_sources（客户来源表）

**用途**：定义客户来源类型

**字段**：
- `id`, `code`, `name`

**示例数据**：
- 客户转介绍
- 微信扫码
- 微信群
- 官网
- 广告

#### customer_channels（客户渠道表）

**用途**：定义客户渠道

**字段**：
- `id`, `code`, `name`

**示例数据**：
- 线上渠道
- 线下渠道
- 合作伙伴

#### contacts（联系人表）

**用途**：联系人信息，同时代表接单人员（sales）

**关键字段**：
- `id`: 主键
- `customer_id`: 客户ID（必填）
- `first_name`, `last_name`: 姓名
- `email`, `phone`, `mobile`: 联系方式
- `is_primary`: 是否主要联系人（每个客户唯一）
- `is_decision_maker`: 是否决策人
- `is_active`: 是否激活

**关联关系**：
- `customer_id` → `customers.id` (ON DELETE CASCADE)
- `created_by` → `users.id` (ON DELETE SET NULL)
- `updated_by` → `users.id` (ON DELETE SET NULL)

**注意**：
- 对于组织客户，contacts 代表联系人
- 对于服务记录，contacts 代表接单人员（sales）

#### customer_documents（客户文档表）

**用途**：保存客户的护照、身份证、营业执照等文档信息

**关键字段**：
- `id`: 主键
- `customer_id`: 客户ID（必填）
- `document_type`: 文档类型
  - `'passport'`: 护照
  - `'id_card'`: 身份证
  - `'business_license'`: 营业执照
  - `'visa'`: 签证
  - `'other'`: 其他
- `document_number`: 文档编号（如护照号）
- `file_url`, `file_path`: 文件存储路径
- `full_name`, `date_of_birth`, `nationality`: 从文档提取的个人信息
- `is_primary`: 是否主要文档
- `is_verified`: 是否已验证

**关联关系**：
- `customer_id` → `customers.id` (ON DELETE CASCADE)
- `verified_by` → `users.id` (ON DELETE SET NULL)

**文档管理**：
- 一个客户可以有多个文档（护照、身份证等）
- 支持文档验证流程
- 支持文档过期提醒

### 2.2 服务域（Service Domain）

#### service_records（服务记录表）

**用途**：记录客户的服务需求/意向

**关键字段**：
- `id`: 主键
- `customer_id`: 客户ID（必填）
- `service_type_id`: 服务类型ID
- `product_id`: 产品/服务ID（可选）
- `contact_id`: 接单人员ID（关联 contacts 表，代表 sales）
- `sales_user_id`: 销售用户ID（冗余字段）
- `status`: 状态
  - `'pending'`: 待处理
  - `'in_progress'`: 进行中
  - `'completed'`: 已完成
  - `'cancelled'`: 已取消
  - `'on_hold'`: 暂停
- `priority`: 优先级
  - `'low'`: 低
  - `'normal'`: 普通
  - `'high'`: 高
  - `'urgent'`: 紧急

**关联关系**：
- `customer_id` → `customers.id` (ON DELETE CASCADE)
- `service_type_id` → `service_types.id` (ON DELETE SET NULL)
- `product_id` → `products.id` (ON DELETE SET NULL)
- `contact_id` → `contacts.id` (ON DELETE SET NULL) - **接单人员（sales）**
- `sales_user_id` → `users.id` (ON DELETE SET NULL)

**业务逻辑**：
- 一个客户可以有多条服务记录
- 每条服务记录对应一个服务需求/意向
- 服务记录可以关联到具体的产品
- 接单人员通过 `contact_id` 关联到 `contacts` 表

### 2.3 订单域（Order Domain）

#### orders（订单表）

**用途**：已确认的服务订单

**关键字段**：
- `id`: 主键
- `order_number`: 订单号（唯一）
- `customer_id`: 客户ID（必填）
- `product_id`: 产品ID
- `service_record_id`: 服务记录ID（可选）
- `sales_user_id`: 销售用户ID（必填）
- `total_amount`: 总金额
- `final_amount`: 最终金额
- `status_code`: 订单状态

**关联关系**：
- `customer_id` → `customers.id` (ON DELETE RESTRICT)
- `product_id` → `products.id` (ON DELETE SET NULL)
- `service_record_id` → `service_records.id` (ON DELETE SET NULL)
- `sales_user_id` → `users.id` (ON DELETE RESTRICT)

**业务逻辑**：
- 订单必须关联一个客户
- 订单可以关联一个服务记录（可选）
- 一个服务记录可以生成多个订单

### 2.4 付款域（Payment Domain）

#### payment_stages（分阶段付款表）

**用途**：管理订单的分阶段付款计划，与财务系统关联

**关键字段**：
- `id`: 主键
- `order_id`: 订单ID（必填）
- `service_record_id`: 服务记录ID（可选）
- `stage_number`: 阶段序号（1, 2, 3...）
- `stage_name`: 阶段名称（如：首付款、中期款、尾款）
- `amount`: 应付金额
- `paid_amount`: 已付金额
- `remaining_amount`: 剩余金额（计算字段：amount - paid_amount）
- `due_date`: 到期日期
- `status`: 状态
  - `'pending'`: 待付
  - `'partial'`: 部分付款
  - `'paid'`: 已付
  - `'overdue'`: 逾期
  - `'cancelled'`: 已取消
- `payment_status`: 付款状态
  - `'unpaid'`: 未付
  - `'partial'`: 部分付款
  - `'paid'`: 已付
  - `'refunded'`: 已退款
- `finance_record_id`: 财务系统记录ID
- `finance_sync_status`: 财务同步状态
  - `'pending'`: 待同步
  - `'synced'`: 已同步
  - `'failed'`: 同步失败

**关联关系**：
- `order_id` → `orders.id` (ON DELETE CASCADE)
- `service_record_id` → `service_records.id` (ON DELETE SET NULL)

**业务逻辑**：
- 一个订单可以有多个付款阶段
- 每个阶段有独立的付款金额和到期日期
- 支持与财务系统同步
- 自动计算已付金额和剩余金额

#### payments（收款记录表）

**用途**：记录实际的收款记录

**关键字段**：
- `id`: 主键
- `order_id`: 订单ID（必填）
- `payment_stage_id`: 付款阶段ID（新增字段）
- `payment_type`: 付款类型
- `amount`: 付款金额
- `status`: 状态
- `confirmed_by`: 确认人

**关联关系**：
- `order_id` → `orders.id` (ON DELETE RESTRICT)
- `payment_stage_id` → `payment_stages.id` (ON DELETE SET NULL) - **新增关联**
- `confirmed_by` → `users.id` (ON DELETE SET NULL)

**业务逻辑**：
- 每个付款记录可以关联到一个付款阶段
- 当付款记录状态为 `'confirmed'` 时，自动更新对应付款阶段的 `paid_amount`
- 支持一个阶段多次付款（部分付款）

## 三、表关系图

### 3.1 完整关系图

```
customers (客户表)
├── 1:N → contacts (联系人/接单人员)
├── 1:N → customer_documents (客户文档)
├── 1:N → service_records (服务记录)
└── 1:N → orders (订单)

service_records (服务记录)
├── N:1 → customers (客户)
├── N:1 → service_types (服务类型)
├── N:1 → products (产品)
├── N:1 → contacts (接单人员)
└── 1:N → orders (订单)

orders (订单)
├── N:1 → customers (客户)
├── N:1 → products (产品)
├── N:1 → service_records (服务记录)
├── N:1 → users (销售)
└── 1:N → payment_stages (付款阶段)

payment_stages (付款阶段)
├── N:1 → orders (订单)
├── N:1 → service_records (服务记录)
└── 1:N → payments (付款记录)

payments (付款记录)
├── N:1 → orders (订单)
└── N:1 → payment_stages (付款阶段)

customer_documents (客户文档)
└── N:1 → customers (客户)
```

### 3.2 数据流向

```
客户创建
  ↓
服务记录（需求/意向）
  ↓
订单（确认服务）
  ↓
付款阶段（分阶段付款计划）
  ↓
付款记录（实际收款）
  ↓
财务系统同步
```

## 四、关键业务逻辑

### 4.1 客户类型和来源

**个人客户 vs 组织客户**：
- `customer_type = 'individual'`: 个人客户
- `customer_type = 'organization'`: 组织客户
- 组织客户可以下挂个人客户（通过 `parent_customer_id`）

**内部客户 vs 渠道客户**：
- `customer_source_type = 'own'`: 内部客户，所有者是 `owner_user_id`（SALES角色）
- `customer_source_type = 'agent'`: 渠道客户，所有者是 `agent_id`（agent组织）

### 4.2 联系人 vs 接单人员

**contacts 表的双重角色**：
1. **联系人角色**：组织客户下的联系人信息
2. **接单人员角色**：在 `service_records` 中，`contact_id` 关联到 `contacts` 表，代表接单人员（sales）

**设计说明**：
- 一个联系人可以是多个服务记录的接单人员
- 接单人员信息存储在 `contacts` 表中，便于统一管理

### 4.3 服务记录到订单的转换

**流程**：
1. 客户创建服务记录（需求/意向）
2. 接单人员（contact）处理服务记录
3. 确认后创建订单（`service_record_id` 关联到服务记录）
4. 订单关联到具体的产品和价格

**关系**：
- 一个服务记录可以生成多个订单（同一服务可以多次下单）
- 一个订单必须关联一个客户，可以关联一个服务记录（可选）

### 4.4 分阶段付款逻辑

**付款阶段创建**：
- 订单创建后，可以创建多个付款阶段
- 每个阶段有独立的金额、到期日期和付款条件

**付款记录关联**：
- 每个付款记录可以关联到一个付款阶段（`payment_stage_id`）
- 当付款记录状态为 `'confirmed'` 时，自动更新对应阶段的 `paid_amount`

**自动计算**：
- `remaining_amount = amount - paid_amount`（计算字段）
- 根据 `paid_amount` 和 `amount` 自动更新 `payment_status` 和 `status`

**财务系统同步**：
- `finance_record_id`: 财务系统的记录ID
- `finance_sync_status`: 同步状态
- 支持同步失败重试

### 4.5 客户文档管理

**文档类型**：
- 护照（passport）
- 身份证（id_card）
- 营业执照（business_license）
- 签证（visa）
- 其他（other）

**文档验证**：
- `is_verified`: 是否已验证
- `verified_by`: 验证人
- `verified_at`: 验证时间

**个人信息提取**：
- 从文档中提取姓名、出生日期、国籍等信息
- 存储在 `customer_documents` 表中，便于后续使用

## 五、索引设计

### 5.1 客户表索引

- `ux_customers_code`: 客户编码唯一索引
- `ix_customers_source_type`: 客户来源类型索引
- `ix_customers_customer_type`: 客户类型索引
- `ix_customers_owner`: 所有者索引
- `ix_customers_agent`: 渠道索引
- `ix_customers_parent`: 父客户索引

### 5.2 服务记录表索引

- `ix_service_records_customer`: 客户索引
- `ix_service_records_service_type`: 服务类型索引
- `ix_service_records_contact`: 接单人员索引
- `ix_service_records_status`: 状态索引
- `ix_service_records_priority`: 优先级索引

### 5.3 付款阶段表索引

- `ix_payment_stages_order`: 订单索引
- `ix_payment_stages_stage_number`: 阶段序号索引（复合：order_id + stage_number）
- `ix_payment_stages_status`: 状态索引
- `ix_payment_stages_due_date`: 到期日期索引
- `ix_payment_stages_finance_sync`: 财务同步状态索引

## 六、数据完整性约束

### 6.1 外键约束

所有外键都设置了适当的 `ON DELETE` 行为：
- `CASCADE`: 删除主记录时，同时删除关联记录（如：客户删除时删除文档）
- `SET NULL`: 删除主记录时，将外键设置为 NULL（如：删除服务类型时，服务记录的 service_type_id 设为 NULL）
- `RESTRICT`: 如果有关联记录，禁止删除主记录（如：有订单的客户不能删除）

### 6.2 检查约束

- 客户类型：`customer_type IN ('individual', 'organization')`
- 客户来源类型：`customer_source_type IN ('own', 'agent')`
- 服务记录状态：`status IN ('pending', 'in_progress', 'completed', 'cancelled', 'on_hold')`
- 付款阶段状态：`status IN ('pending', 'partial', 'paid', 'overdue', 'cancelled')`
- 金额非负：所有金额字段都有 `>= 0` 的检查约束

### 6.3 唯一约束

- `customers.code`: 客户编码唯一
- `orders.order_number`: 订单号唯一
- `customer_documents`: 每个客户的主要文档唯一（通过 `is_primary` 约束）

## 七、触发器设计

### 7.1 付款阶段金额自动更新

**触发器**：`update_payment_stage_paid_amount`

**功能**：
- 当 `payments` 表插入新记录且状态为 `'confirmed'` 时
- 自动更新对应 `payment_stages` 的 `paid_amount`
- 自动更新 `payment_status` 和 `status`

**逻辑**：
```sql
paid_amount = SUM(payments.amount WHERE payment_stage_id = ? AND status = 'confirmed')
payment_status = CASE
  WHEN paid_amount >= amount THEN 'paid'
  WHEN paid_amount > 0 THEN 'partial'
  ELSE 'unpaid'
END
```

## 八、API 设计建议

### 8.1 客户管理 API

- `GET /api/service-management/customers` - 获取客户列表
- `GET /api/service-management/customers/{id}` - 获取客户详情
- `POST /api/service-management/customers` - 创建客户
- `PUT /api/service-management/customers/{id}` - 更新客户
- `DELETE /api/service-management/customers/{id}` - 删除客户

### 8.2 客户文档 API

- `GET /api/service-management/customers/{customer_id}/documents` - 获取客户文档列表
- `POST /api/service-management/customers/{customer_id}/documents` - 上传客户文档
- `PUT /api/service-management/documents/{id}` - 更新文档信息
- `DELETE /api/service-management/documents/{id}` - 删除文档
- `POST /api/service-management/documents/{id}/verify` - 验证文档

### 8.3 服务记录 API

- `GET /api/service-management/customers/{customer_id}/service-records` - 获取客户的服务记录
- `POST /api/service-management/customers/{customer_id}/service-records` - 创建服务记录
- `PUT /api/service-management/service-records/{id}` - 更新服务记录
- `DELETE /api/service-management/service-records/{id}` - 删除服务记录

### 8.4 付款阶段 API

- `GET /api/service-management/orders/{order_id}/payment-stages` - 获取订单的付款阶段
- `POST /api/service-management/orders/{order_id}/payment-stages` - 创建付款阶段
- `PUT /api/service-management/payment-stages/{id}` - 更新付款阶段
- `DELETE /api/service-management/payment-stages/{id}` - 删除付款阶段
- `POST /api/service-management/payment-stages/{id}/sync-finance` - 同步到财务系统

## 九、实施优先级

### Phase 1: 基础功能
1. 客户基础 CRUD（customers 表）
2. 联系人管理（contacts 表）
3. 客户文档管理（customer_documents 表）

### Phase 2: 服务管理
4. 服务记录管理（service_records 表）
5. 服务记录到订单的转换

### Phase 3: 付款管理
6. 分阶段付款计划（payment_stages 表）
7. 付款记录关联（payments.payment_stage_id）
8. 财务系统同步

### Phase 4: 高级功能
9. 文档验证流程
10. 付款阶段自动计算和状态更新
11. 数据导入（从 Accounts.xlsx）

## 十、注意事项

1. **数据一致性**：
   - 删除客户时，会级联删除文档和服务记录
   - 删除订单时，会级联删除付款阶段
   - 删除付款阶段时，不会删除付款记录，但会将 `payment_stage_id` 设为 NULL

2. **性能优化**：
   - 大量使用冗余字段（如 customer_name, product_name）减少 JOIN 查询
   - 合理使用索引提高查询性能
   - 付款阶段金额使用计算字段，避免实时计算

3. **财务系统集成**：
   - `finance_record_id` 存储财务系统的记录ID
   - `finance_sync_status` 跟踪同步状态
   - 支持同步失败重试机制

4. **文档管理**：
   - 支持多种文档类型
   - 支持文档验证流程
   - 支持文档过期提醒

