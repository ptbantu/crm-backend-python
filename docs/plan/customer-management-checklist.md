# 客户管理表结构检查清单

## 一、表结构完整性检查

### ✅ 1.1 客户域表（Customer Domain）

#### customers（客户表）
- ✅ 已存在（01_schema_unified.sql）
- ✅ 支持个人/组织客户（customer_type）
- ✅ 支持内部/渠道客户（customer_source_type）
- ✅ 支持层级关系（parent_customer_id）
- ✅ 关联客户来源（source_id）
- ✅ 关联客户渠道（channel_id）
- ✅ 关联所有者（owner_user_id, agent_id）

#### customer_sources（客户来源表）
- ✅ 已存在（01_schema_unified.sql）
- ✅ 基础字段：id, code, name
- ⚠️ **检查点**：是否需要添加 description, is_active 等字段？

#### customer_channels（客户渠道表）
- ✅ 已存在（01_schema_unified.sql）
- ✅ 基础字段：id, code, name
- ⚠️ **检查点**：是否需要添加 description, is_active 等字段？

#### contacts（联系人表）
- ✅ 已存在（01_schema_unified.sql）
- ✅ 支持联系人信息
- ✅ 支持接单人员角色（通过 service_records.contact_id 关联）
- ✅ 主要联系人约束（is_primary）

#### customer_documents（客户文档表）
- ✅ 新创建（09_customer_documents_and_payment_stages.sql）
- ✅ 支持多种文档类型（passport, id_card, business_license, visa, other）
- ✅ 文件存储字段（file_url, file_path, thumbnail_url）
- ✅ 个人信息提取字段（full_name, date_of_birth, nationality等）
- ✅ 文档验证流程（is_verified, verified_by, verified_at）
- ✅ 文档过期管理（expiry_date, is_valid）

### ✅ 1.2 服务域表（Service Domain）

#### service_records（服务记录表）
- ✅ 新创建（08_service_records.sql）
- ✅ 关联客户（customer_id）
- ✅ 关联服务类型（service_type_id）
- ✅ 关联产品（product_id，可选）
- ✅ 关联接单人员（contact_id，代表sales）
- ✅ 状态管理（status: pending, in_progress, completed, cancelled, on_hold）
- ✅ 优先级管理（priority: low, normal, high, urgent）
- ✅ 时间管理（expected_start_date, expected_completion_date等）
- ✅ 价格信息（estimated_price, final_price）
- ✅ 跟进信息（last_follow_up_at, next_follow_up_at）

### ✅ 1.3 订单域表（Order Domain）

#### orders（订单表）
- ✅ 已存在（01_schema_unified.sql）
- ✅ 关联客户（customer_id）
- ✅ 关联产品（product_id）
- ✅ 关联销售（sales_user_id）
- ⚠️ **检查点**：是否需要添加 service_record_id 字段？
  - ✅ 已在 08_service_records.sql 中添加

#### order_statuses（订单状态表）
- ✅ 已存在（01_schema_unified.sql）

### ✅ 1.4 付款域表（Payment Domain）

#### payment_stages（分阶段付款表）
- ✅ 新创建（09_customer_documents_and_payment_stages.sql）
- ✅ 关联订单（order_id）
- ✅ 关联服务记录（service_record_id，可选）
- ✅ 阶段管理（stage_number, stage_name）
- ✅ 金额管理（amount, paid_amount, remaining_amount）
- ✅ 付款触发条件（payment_trigger: manual, milestone, date, completion）
- ✅ 状态管理（status, payment_status）
- ✅ 财务系统关联（finance_record_id, finance_sync_status）
- ✅ 发票信息（invoice_number, invoice_date, invoice_url）

#### payments（收款记录表）
- ✅ 已存在（01_schema_unified.sql）
- ✅ 关联订单（order_id）
- ✅ **新增**：关联付款阶段（payment_stage_id）
- ✅ 付款信息（amount, payment_type, payment_method）
- ✅ 状态管理（status）
- ✅ 确认流程（confirmed_by, confirmed_at）

## 二、外键关系检查

### ✅ 2.1 customers 表外键
- ✅ parent_customer_id → customers.id (ON DELETE SET NULL)
- ✅ source_id → customer_sources.id (ON DELETE SET NULL)
- ✅ channel_id → customer_channels.id (ON DELETE SET NULL)
- ✅ owner_user_id → users.id (ON DELETE SET NULL)
- ✅ agent_user_id → users.id (ON DELETE SET NULL)
- ✅ agent_id → organizations.id (ON DELETE SET NULL)

### ✅ 2.2 contacts 表外键
- ✅ customer_id → customers.id (ON DELETE CASCADE)
- ✅ created_by → users.id (ON DELETE SET NULL)
- ✅ updated_by → users.id (ON DELETE SET NULL)

### ✅ 2.3 customer_documents 表外键
- ✅ customer_id → customers.id (ON DELETE CASCADE)
- ✅ verified_by → users.id (ON DELETE SET NULL)
- ✅ created_by → users.id (ON DELETE SET NULL)
- ✅ updated_by → users.id (ON DELETE SET NULL)

### ✅ 2.4 service_records 表外键
- ✅ customer_id → customers.id (ON DELETE CASCADE)
- ✅ service_type_id → service_types.id (ON DELETE SET NULL)
- ✅ product_id → products.id (ON DELETE SET NULL)
- ✅ contact_id → contacts.id (ON DELETE SET NULL)
- ✅ sales_user_id → users.id (ON DELETE SET NULL)
- ✅ referral_customer_id → customers.id (ON DELETE SET NULL)
- ✅ created_by → users.id (ON DELETE SET NULL)
- ✅ updated_by → users.id (ON DELETE SET NULL)

### ✅ 2.5 orders 表外键
- ✅ customer_id → customers.id (ON DELETE RESTRICT)
- ✅ product_id → products.id (ON DELETE SET NULL)
- ✅ service_record_id → service_records.id (ON DELETE SET NULL) - **已添加**
- ✅ sales_user_id → users.id (ON DELETE RESTRICT)
- ✅ status_id → order_statuses.id (ON DELETE SET NULL)
- ✅ created_by → users.id (ON DELETE SET NULL)
- ✅ updated_by → users.id (ON DELETE SET NULL)

### ✅ 2.6 payment_stages 表外键
- ✅ order_id → orders.id (ON DELETE CASCADE)
- ✅ service_record_id → service_records.id (ON DELETE SET NULL)
- ✅ created_by → users.id (ON DELETE SET NULL)
- ✅ updated_by → users.id (ON DELETE SET NULL)

### ✅ 2.7 payments 表外键
- ✅ order_id → orders.id (ON DELETE RESTRICT)
- ✅ payment_stage_id → payment_stages.id (ON DELETE SET NULL) - **已添加**
- ✅ confirmed_by → users.id (ON DELETE SET NULL)
- ✅ created_by → users.id (ON DELETE SET NULL)

## 三、索引检查

### ✅ 3.1 customers 表索引
- ✅ ux_customers_code (唯一索引)
- ✅ ix_customers_source_type
- ✅ ix_customers_customer_type
- ✅ ix_customers_owner
- ✅ ix_customers_agent
- ✅ ix_customers_agent_id
- ✅ ix_customers_parent
- ✅ ix_customers_source

### ✅ 3.2 contacts 表索引
- ✅ ix_contacts_customer
- ✅ ix_contacts_email
- ✅ ix_contacts_phone
- ✅ ix_contacts_primary
- ✅ ux_contacts_one_primary_per_customer (唯一索引)

### ✅ 3.3 customer_documents 表索引
- ✅ ix_customer_documents_customer
- ✅ ix_customer_documents_type
- ✅ ix_customer_documents_number
- ✅ ix_customer_documents_status
- ✅ ix_customer_documents_expiry
- ✅ ix_customer_documents_is_primary
- ✅ ix_customer_documents_is_verified

### ✅ 3.4 service_records 表索引
- ✅ ix_service_records_customer
- ✅ ix_service_records_service_type
- ✅ ix_service_records_product
- ✅ ix_service_records_contact
- ✅ ix_service_records_status
- ✅ ix_service_records_priority
- ✅ ix_service_records_created_at
- ✅ 复合索引（customer_id + status, contact_id + status等）

### ✅ 3.5 payment_stages 表索引
- ✅ ix_payment_stages_order
- ✅ ix_payment_stages_service_record
- ✅ ix_payment_stages_stage_number (复合：order_id + stage_number)
- ✅ ix_payment_stages_status
- ✅ ix_payment_stages_payment_status
- ✅ ix_payment_stages_due_date
- ✅ ix_payment_stages_finance_sync
- ✅ ix_payment_stages_finance_record

### ✅ 3.6 payments 表索引
- ✅ ix_payments_order
- ✅ ix_payments_payment_stage - **已添加**
- ✅ ix_payments_status
- ✅ ix_payments_date

## 四、约束检查

### ✅ 4.1 检查约束（CHECK Constraints）

#### customers 表
- ✅ chk_customer_source_type: IN ('own', 'agent')
- ✅ chk_customer_type: IN ('individual', 'organization')

#### customer_documents 表
- ✅ chk_customer_documents_type: IN ('passport', 'id_card', 'business_license', 'visa', 'other')
- ✅ chk_customer_documents_status: IN ('active', 'expired', 'cancelled')
- ✅ chk_customer_documents_gender: IN ('male', 'female', 'other') OR NULL

#### service_records 表
- ✅ chk_service_records_status: IN ('pending', 'in_progress', 'completed', 'cancelled', 'on_hold')
- ✅ chk_service_records_priority: IN ('low', 'normal', 'high', 'urgent')
- ✅ chk_service_records_quantity_nonneg: quantity >= 0
- ✅ chk_service_records_price_nonneg: estimated_price >= 0 AND final_price >= 0

#### payment_stages 表
- ✅ chk_payment_stages_amount_nonneg: amount >= 0 AND paid_amount >= 0
- ✅ chk_payment_stages_stage_number: stage_number > 0
- ✅ chk_payment_stages_status: IN ('pending', 'partial', 'paid', 'overdue', 'cancelled')
- ✅ chk_payment_stages_payment_status: IN ('unpaid', 'partial', 'paid', 'refunded')
- ✅ chk_payment_stages_trigger: IN ('manual', 'milestone', 'date', 'completion') OR NULL
- ✅ chk_payment_stages_finance_sync_status: IN ('pending', 'synced', 'failed')

#### orders 表
- ✅ chk_orders_amounts_nonneg: 所有金额字段 >= 0

### ✅ 4.2 唯一约束（UNIQUE Constraints）

- ✅ customers.code (唯一)
- ✅ orders.order_number (唯一)
- ✅ customer_documents.id_external (唯一，如果存在)
- ✅ service_records.id_external (唯一，如果存在)
- ✅ contacts: 每个客户的主要联系人唯一（is_primary = TRUE）

## 五、触发器检查

### ✅ 5.1 付款阶段金额自动更新触发器

- ✅ update_payment_stage_paid_amount (AFTER INSERT)
  - 当 payments 表插入新记录且 status = 'confirmed' 时
  - 自动更新 payment_stages.paid_amount
  - 自动更新 payment_status 和 status

- ✅ update_payment_stage_paid_amount_on_update (AFTER UPDATE)
  - 当 payments 表更新且 status 变化或 payment_stage_id 变化时
  - 更新旧阶段和新阶段的 paid_amount

### ⚠️ 5.2 其他可能的触发器

- ⚠️ **检查点**：是否需要触发器自动更新 orders.final_amount？
- ⚠️ **检查点**：是否需要触发器自动更新 customer_documents.is_valid（基于 expiry_date）？

## 六、计算字段检查

### ✅ 6.1 计算字段（Generated Columns）

- ✅ contacts.full_name: GENERATED ALWAYS AS (CONCAT(first_name, ' ', last_name)) STORED
- ✅ payment_stages.remaining_amount: GENERATED ALWAYS AS (amount - paid_amount) STORED

### ⚠️ 6.2 其他可能的计算字段

- ⚠️ **检查点**：orders 表是否需要计算字段 total_amount = quantity * unit_price？
  - 目前 orders 表有 total_amount 字段，但未设置为计算字段

## 七、业务逻辑检查

### ✅ 7.1 客户类型和来源逻辑

- ✅ 个人客户 vs 组织客户（customer_type）
- ✅ 内部客户 vs 渠道客户（customer_source_type）
- ✅ 组织下挂个人客户（parent_customer_id）

### ✅ 7.2 联系人双重角色

- ✅ 组织客户下的联系人（contacts.customer_id）
- ✅ 服务记录的接单人员（service_records.contact_id）

### ✅ 7.3 服务记录到订单转换

- ✅ 服务记录可以生成多个订单
- ✅ 订单可以关联服务记录（service_record_id）

### ✅ 7.4 分阶段付款逻辑

- ✅ 一个订单可以有多个付款阶段
- ✅ 每个阶段独立管理金额和状态
- ✅ 自动计算已付金额和剩余金额
- ✅ 支持财务系统同步

### ✅ 7.5 文档管理逻辑

- ✅ 支持多种文档类型
- ✅ 从文档提取个人信息
- ✅ 文档验证流程
- ✅ 文档过期管理

## 八、数据迁移检查

### ⚠️ 8.1 从 Accounts.xlsx 导入数据

- ⚠️ **待实现**：客户数据导入脚本
- ⚠️ **待实现**：客户来源数据导入（从 source_name 字段）
- ⚠️ **待实现**：客户渠道数据导入（从 channel_name 字段）
- ⚠️ **待实现**：服务记录创建（从 customer_requirements 字段）

### ⚠️ 8.2 数据同步

- ⚠️ **检查点**：是否需要同步 customer_sources 和 customer_channels 的种子数据？

## 九、API 设计检查

### ⚠️ 9.1 待实现的 API

- ⚠️ 客户管理 API（CRUD）
- ⚠️ 客户文档 API（上传、查看、验证）
- ⚠️ 服务记录 API（CRUD）
- ⚠️ 付款阶段 API（CRUD、财务同步）
- ⚠️ 联系人 API（CRUD）

### ⚠️ 9.2 API 文档

- ⚠️ **待更新**：API_DOCUMENTATION.md 需要添加客户管理相关接口

## 十、潜在遗漏检查

### ⚠️ 10.1 可能遗漏的字段

#### customers 表
- ⚠️ **检查点**：是否需要添加 address 相关字段？
  - 目前 customers 表没有地址字段，但 customer_documents 有
  - 建议：如果需要，可以在 customers 表添加地址字段

#### customer_sources 和 customer_channels 表
- ⚠️ **检查点**：是否需要添加 description, is_active, display_order 等字段？
  - 建议：为了统一管理，可以添加这些字段

#### service_records 表
- ✅ 字段已完整

#### payment_stages 表
- ✅ 字段已完整

### ⚠️ 10.2 可能遗漏的表

- ⚠️ **检查点**：是否需要客户跟进记录表（customer_follow_ups）？
  - 目前 service_records 有 follow_up 相关字段
  - 如果需要独立的跟进记录表，可以创建

- ⚠️ **检查点**：是否需要客户标签表（customer_tags）？
  - 目前 customers 表有 tags 字段（JSON）
  - 如果需要规范化标签管理，可以创建独立的标签表

- ⚠️ **检查点**：是否需要客户附件表（customer_attachments）？
  - 目前 customer_documents 表可以存储文档
  - 如果需要存储其他附件，可以创建独立的附件表

### ⚠️ 10.3 可能遗漏的关系

- ⚠️ **检查点**：是否需要客户与组织的直接关联？
  - 目前通过 owner_user_id 和 agent_id 间接关联
  - 如果需要，可以添加 organization_id 字段

- ⚠️ **检查点**：是否需要客户与产品的关注/收藏关系？
  - 如果需要，可以创建 customer_product_interests 表

## 十一、SQL 脚本执行顺序检查

### ✅ 11.1 脚本执行顺序

1. ✅ 01_schema_unified.sql - 基础表结构（包含 customers, contacts, customer_sources, customer_channels, orders, payments）
2. ✅ 07_sync_database_fields.sql - 字段同步（包含基础 service_records 表）
3. ✅ 08_service_records.sql - 完整的 service_records 表（可选，如果需要完整字段）
4. ✅ 09_customer_documents_and_payment_stages.sql - customer_documents 和 payment_stages 表
5. ✅ 02_all_seed_data.sql - 种子数据

### ⚠️ 11.2 脚本依赖关系

- ✅ 08_service_records.sql 依赖 01_schema_unified.sql（customers, service_types, products, contacts, users）
- ✅ 09_customer_documents_and_payment_stages.sql 依赖 01_schema_unified.sql（customers, users, orders）
- ✅ 09_customer_documents_and_payment_stages.sql 依赖 08_service_records.sql（service_records）

## 十二、文档完整性检查

### ✅ 12.1 已创建的文档

- ✅ customer-structure-analysis.md - 客户结构分析
- ✅ customer-management-table-relationships.md - 表关系逻辑文档
- ✅ customer-management-checklist.md - 本检查清单

### ⚠️ 12.2 待创建的文档

- ⚠️ **待创建**：客户管理 API 设计文档
- ⚠️ **待创建**：数据导入脚本说明文档

## 十三、总结

### ✅ 已完成

1. ✅ 所有核心表结构已创建
2. ✅ 所有外键关系已设置
3. ✅ 所有索引已创建
4. ✅ 所有约束已设置
5. ✅ 触发器已创建（付款阶段金额自动更新）
6. ✅ 表关系文档已创建

### ⚠️ 待完善

1. ⚠️ customer_sources 和 customer_channels 表可能需要添加更多字段（description, is_active等）
2. ⚠️ 需要创建数据导入脚本（从 Accounts.xlsx）
3. ⚠️ 需要实现客户管理相关的 API
4. ⚠️ 需要更新 API 文档

### ✅ 建议

1. ✅ 表结构设计完整，可以开始实现业务逻辑
2. ✅ 建议先实现基础 CRUD，再实现高级功能
3. ✅ 建议创建数据导入脚本，便于从 Excel 导入历史数据

