# 数据库结构 v1 文档

## 概述

本文档描述了 BANTU CRM 数据库结构 v1 版本，重点关注三个核心模块的优化：

1. **用户登录管理模块** - 用户认证、权限管理、组织架构
2. **销售-线索管理模块** - 线索管理、跟进、转换
3. **服务管理模块** - 客户管理、服务记录、订单管理

## 模块1：用户登录管理

### 核心表

#### users（用户表）
- **用途**: 存储用户登录账户信息
- **关键字段**:
  - `id`: UUID 主键
  - `username`: 用户名（唯一）
  - `email`: 邮箱（唯一）
  - `password_hash`: 密码哈希
  - `is_active`: 是否激活
  - `is_locked`: 是否锁定
- **索引优化**:
  - `ix_users_username`: 用户名索引
  - `ix_users_email`: 邮箱索引
  - `ix_users_active`: 激活状态索引
  - `ix_users_locked`: 锁定状态索引

#### organizations（组织表）
- **用途**: 存储组织信息
- **关键字段**:
  - `id`: UUID 主键
  - `name`: 组织名称
  - `code`: 组织编码（唯一）
  - `organization_type`: 组织类型（internal, vendor, agent）
  - `is_active`: 是否激活
- **索引优化**:
  - `ix_organizations_code`: 编码索引
  - `ix_organizations_type`: 类型索引
  - `ix_organizations_type_active`: 类型+激活状态复合索引

#### organization_employees（组织员工表）
- **用途**: 存储用户与组织的关联关系
- **关键字段**:
  - `id`: UUID 主键
  - `user_id`: 用户ID（外键）
  - `organization_id`: 组织ID（外键）
  - `is_primary`: 是否主要组织
  - `is_active`: 是否在职
- **索引优化**:
  - `ix_organization_employees_org`: 组织ID索引
  - `ix_organization_employees_user`: 用户ID索引
  - `ix_organization_employees_primary`: 用户+主要组织+激活状态复合索引

#### roles（角色表）
- **用途**: 存储角色定义
- **关键字段**:
  - `id`: UUID 主键
  - `code`: 角色代码（唯一）
  - `name`: 角色名称
  - `name_zh`: 中文名称
  - `name_id`: 印尼语名称

#### user_roles（用户角色关联表）
- **用途**: 用户与角色的多对多关联
- **关键字段**:
  - `user_id`: 用户ID（外键）
  - `role_id`: 角色ID（外键）
- **主键**: (`user_id`, `role_id`)

#### permissions（权限表）
- **用途**: 存储权限定义
- **关键字段**:
  - `id`: UUID 主键
  - `code`: 权限代码（唯一）
  - `resource_type`: 资源类型
  - `action`: 操作类型
  - `is_active`: 是否激活

#### role_permissions（角色权限关联表）
- **用途**: 角色与权限的多对多关联
- **关键字段**:
  - `role_id`: 角色ID（外键）
  - `permission_id`: 权限ID（外键）
- **主键**: (`role_id`, `permission_id`)

#### menus（菜单表）
- **用途**: 存储菜单定义
- **关键字段**:
  - `id`: UUID 主键
  - `code`: 菜单代码（唯一）
  - `name_zh`: 中文名称
  - `name_id`: 印尼语名称
  - `parent_id`: 父菜单ID
  - `path`: 路由路径
  - `is_active`: 是否激活
  - `is_visible`: 是否可见

#### menu_permissions（菜单权限关联表）
- **用途**: 菜单与权限的多对多关联
- **关键字段**:
  - `menu_id`: 菜单ID（外键）
  - `permission_id`: 权限ID（外键）
- **主键**: (`menu_id`, `permission_id`)

### 优化项

1. **统一审计字段**: 所有表都包含 `created_at`, `updated_at`, `created_by`, `updated_by`
2. **索引优化**: 为常用查询字段添加索引，包括复合索引
3. **外键约束**: 确保数据完整性，使用适当的 `ON DELETE` 策略

## 模块2：销售-线索管理

### 核心表

#### leads（线索表）
- **用途**: 存储销售线索信息
- **关键字段**:
  - `id`: UUID 主键
  - `name`: 线索名称
  - `company_name`: 公司名称
  - `contact_name`: 联系人姓名
  - `phone`: 联系电话
  - `email`: 邮箱
  - `organization_id`: 组织ID（**NOT NULL**，从创建用户的组织自动获取）
  - `owner_user_id`: 销售负责人ID
  - `status`: 状态（new, contacted, qualified, converted, lost）
  - `level`: 客户分级代码（外键关联到 customer_levels.code）
  - `is_in_public_pool`: 是否在公海池
  - `pool_id`: 线索池ID
- **业务规则**:
  - `organization_id` 必须为 NOT NULL，创建时从用户的 `organization_employees` 表自动获取
  - 如果用户有多个组织，使用 `is_primary = true` 的组织
  - 查询时使用 `organization_id` 进行数据隔离
- **索引优化**:
  - `ix_leads_organization`: 组织ID索引（数据隔离）
  - `ix_leads_owner`: 负责人ID索引
  - `ix_leads_status`: 状态索引
  - `ix_leads_public_pool`: 公海池索引
  - `ix_leads_created_at`: 创建时间索引（降序）

#### lead_follow_ups（线索跟进记录表）
- **用途**: 存储线索跟进记录
- **关键字段**:
  - `id`: UUID 主键
  - `lead_id`: 线索ID（外键）
  - `follow_up_type`: 跟进类型（call, meeting, email, note）
  - `content`: 跟进内容
  - `follow_up_date`: 跟进日期
  - `created_by`: 创建人ID
- **索引优化**:
  - `ix_lead_follow_ups_lead`: 线索ID索引
  - `ix_lead_follow_ups_date`: 跟进日期索引（降序）

#### lead_notes（线索备注表）
- **用途**: 存储线索备注
- **关键字段**:
  - `id`: UUID 主键
  - `lead_id`: 线索ID（外键）
  - `note_type`: 备注类型（comment, reminder, task）
  - `content`: 备注内容
  - `is_important`: 是否重要
  - `created_by`: 创建人ID
- **索引优化**:
  - `ix_lead_notes_lead`: 线索ID索引
  - `ix_lead_notes_important`: 重要性索引

#### lead_pools（线索池表）
- **用途**: 存储线索池定义
- **关键字段**:
  - `id`: UUID 主键
  - `name`: 线索池名称
  - `organization_id`: 组织ID（外键）
  - `is_active`: 是否激活
- **索引优化**:
  - `ix_lead_pools_organization`: 组织ID索引

#### customer_levels（客户分级表）
- **用途**: 存储客户分级配置
- **关键字段**:
  - `id`: UUID 主键
  - `code`: 等级代码（唯一）
  - `name_zh`: 中文名称
  - `name_id`: 印尼语名称
  - `sort_order`: 排序顺序
  - `is_active`: 是否激活

#### follow_up_statuses（跟进状态表）
- **用途**: 存储跟进状态配置
- **关键字段**:
  - `id`: UUID 主键
  - `code`: 状态代码（唯一）
  - `name_zh`: 中文名称
  - `name_id`: 印尼语名称
  - `sort_order`: 排序顺序
  - `is_active`: 是否激活

### 优化项

1. **数据隔离**: `leads.organization_id` 必须为 NOT NULL，确保数据隔离
2. **自动填充**: 创建线索时自动从用户的组织获取 `organization_id`
3. **索引优化**: 为查询性能优化索引，特别是组织ID和状态字段

## 模块3：服务管理

### 核心表

#### customers（客户表）
- **用途**: 存储客户信息
- **关键字段**:
  - `id`: UUID 主键
  - `name`: 客户名称
  - `code`: 客户编码（唯一）
  - `customer_type`: 客户类型（individual, organization）
  - `customer_source_type`: 客户来源类型（own, agent）
  - `owner_user_id`: 内部客户所有者ID
  - `agent_id`: 渠道客户组织ID
  - `level`: 客户等级
- **索引优化**:
  - `ix_customers_source_type`: 来源类型索引
  - `ix_customers_customer_type`: 客户类型索引
  - `ix_customers_owner`: 所有者索引
  - `ix_customers_agent`: 渠道索引

#### contacts（联系人表）
- **用途**: 存储客户联系人信息
- **关键字段**:
  - `id`: UUID 主键
  - `customer_id`: 客户ID（外键）
  - `first_name`: 名
  - `last_name`: 姓
  - `full_name`: 全名（生成列）
  - `email`: 邮箱
  - `phone`: 电话
  - `is_primary`: 是否主要联系人
- **索引优化**:
  - `ix_contacts_customer`: 客户ID索引
  - `ix_contacts_primary`: 客户+主要联系人复合索引

#### service_records（服务记录表）
- **用途**: 存储客户服务需求/意向
- **关键字段**:
  - `id`: UUID 主键
  - `customer_id`: 客户ID（外键）
  - `service_type_id`: 服务类型ID（外键）
  - `product_id`: 产品/服务ID（外键）
  - `status`: 状态（pending, in_progress, completed, cancelled, on_hold）
  - `priority`: 优先级（low, normal, high, urgent）
  - `expected_start_date`: 预期开始日期
  - `expected_completion_date`: 预期完成日期
  - `actual_start_date`: 实际开始日期
  - `actual_completion_date`: 实际完成日期
- **索引优化**:
  - `ix_service_records_customer`: 客户ID索引
  - `ix_service_records_status`: 状态索引
  - `ix_service_records_priority`: 优先级索引
  - `ix_service_records_customer_status`: 客户+状态复合索引

#### service_types（服务类型表）
- **用途**: 存储服务类型定义
- **关键字段**:
  - `id`: UUID 主键
  - `code`: 服务类型代码（唯一）
  - `name`: 服务类型名称
  - `display_order`: 显示顺序
  - `is_active`: 是否激活

#### orders（订单表）
- **用途**: 存储订单信息
- **关键字段**:
  - `id`: UUID 主键
  - `order_number`: 订单号（唯一）
  - `title`: 订单标题
  - `customer_id`: 客户ID（外键）
  - `service_record_id`: 服务记录ID（外键）
  - `sales_user_id`: 销售用户ID（外键）
  - `status_code`: 状态代码
  - `total_amount`: 订单总金额
  - `final_amount`: 最终金额
  - `currency_code`: 货币代码
- **索引优化**:
  - `ix_orders_customer`: 客户ID索引
  - `ix_orders_sales`: 销售用户ID索引
  - `ix_orders_status`: 状态代码索引
  - `ix_orders_created`: 创建时间索引（降序）

#### order_items（订单项表）
- **用途**: 存储订单项信息
- **关键字段**:
  - `id`: UUID 主键
  - `order_id`: 订单ID（外键）
  - `item_number`: 订单项序号
  - `product_id`: 产品ID（外键）
  - `service_type_id`: 服务类型ID（外键）
  - `quantity`: 数量
  - `unit_price`: 单价
  - `item_amount`: 订单项金额
- **索引优化**:
  - `ix_order_items_order`: 订单ID索引
  - `ix_order_items_item_number`: 订单+序号复合索引

#### order_stages（订单阶段表）
- **用途**: 存储订单阶段信息
- **关键字段**:
  - `id`: UUID 主键
  - `order_id`: 订单ID（外键）
  - `stage_name`: 阶段名称
  - `stage_code`: 阶段代码
  - `stage_order`: 阶段顺序
  - `status`: 状态
  - `progress_percent`: 进度百分比
- **索引优化**:
  - `ix_order_stages_order`: 订单ID索引
  - `ix_order_stages_status`: 状态索引

#### order_statuses（订单状态表）
- **用途**: 存储订单状态定义
- **关键字段**:
  - `id`: UUID 主键
  - `code`: 状态代码（唯一）
  - `name`: 状态名称
  - `display_order`: 显示顺序
  - `is_active`: 是否激活

#### order_comments（订单评论表）
- **用途**: 存储订单评论和沟通记录
- **关键字段**:
  - `id`: UUID 主键
  - `order_id`: 订单ID（外键）
  - `order_stage_id`: 订单阶段ID（外键）
  - `comment_type`: 评论类型（general, internal, customer, system）
  - `content_zh`: 评论内容（中文）
  - `content_id`: 评论内容（印尼语）
  - `is_internal`: 是否内部评论
  - `created_by`: 创建人ID
- **索引优化**:
  - `ix_order_comments_order`: 订单ID索引
  - `ix_order_comments_created_at`: 创建时间索引（降序）

#### order_files（订单文件表）
- **用途**: 存储订单相关文件
- **关键字段**:
  - `id`: UUID 主键
  - `order_id`: 订单ID（外键）
  - `order_item_id`: 订单项ID（外键）
  - `order_stage_id`: 订单阶段ID（外键）
  - `file_category`: 文件分类（passport, visa, document, other）
  - `file_path`: 文件存储路径
  - `file_url`: 文件访问URL
  - `uploaded_by`: 上传人ID
- **索引优化**:
  - `ix_order_files_order`: 订单ID索引
  - `ix_order_files_category`: 文件分类索引

#### order_assignments（订单分配表）
- **用途**: 存储订单分配信息
- **关键字段**:
  - `id`: UUID 主键
  - `order_id`: 订单ID（外键）
  - `assigned_to_user_id`: 分配给的用户ID（外键）
  - `assigned_by_user_id`: 分配人ID（外键）
  - `assignment_type`: 分配类型（operation）
  - `is_primary`: 是否主要分配
- **索引优化**:
  - `ix_order_assignments_order`: 订单ID索引
  - `ix_order_assignments_user`: 用户ID索引
  - `ix_order_assignments_active`: 订单+用户复合索引

### 优化项

1. **关联关系**: 确保服务记录与订单的关联关系正确
2. **索引优化**: 为订单查询相关索引优化
3. **状态流转**: 确保状态流转逻辑清晰

## 关键业务规则

### 数据隔离

1. **线索数据隔离**: 
   - `leads.organization_id` 必须为 NOT NULL
   - 创建线索时自动从用户的 `organization_employees` 表获取组织ID
   - 查询时使用 `organization_id` 进行数据隔离

2. **用户组织关联**:
   - 每个用户必须至少有一个 `organization_employees` 记录
   - 用户可以有多个组织，但只有一个主要组织（`is_primary = true`）
   - 创建线索时使用用户的主要组织

### 审计字段

所有表都包含以下审计字段：
- `created_at`: 创建时间（自动设置）
- `updated_at`: 更新时间（自动更新）
- `created_by`: 创建人ID（可选）
- `updated_by`: 更新人ID（可选）

### 外键约束

- 使用适当的 `ON DELETE` 策略：
  - `CASCADE`: 删除父记录时自动删除子记录
  - `SET NULL`: 删除父记录时将子记录的外键设置为 NULL
  - `RESTRICT`: 如果存在子记录，禁止删除父记录

## 迁移说明

从当前 schema 迁移到 v1 的步骤：

1. 确保 `leads.organization_id` 为 NOT NULL
2. 为现有线索数据填充 `organization_id`（从创建用户的组织获取）
3. 优化索引（添加缺失的索引，删除冗余索引）
4. 统一审计字段（确保所有表都有 `created_at`, `updated_at`, `created_by`, `updated_by`）

详细的迁移脚本请参考 `init-scripts/migrations/migrate_to_v1.sql`。

