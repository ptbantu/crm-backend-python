# 客户结构分析与表关系设计

## 一、客户数据结构分析

### 1.1 从 Accounts.xlsx 提取的字段

根据 `Accounts.xlsx` 文件分析，客户数据包含以下字段：

| Excel列名 | 数据库字段 | 类型 | 说明 |
|---------|----------|------|------|
| 记录ID | id_external | VARCHAR(255) | 外部系统ID |
| 客户所有者.id | owner_id_external | VARCHAR(255) | 所有者外部ID |
| 客户所有者 | owner_name | VARCHAR(255) | 所有者名称 |
| 等级 | level | VARCHAR(50) | 客户等级（如：A 重点客户） |
| 客户名称 | name | VARCHAR(255) | 客户名称（必填） |
| 父客户.id | parent_id_external | VARCHAR(255) | 父客户外部ID |
| 父客户 | parent_name | VARCHAR(255) | 父客户名称 |
| 行业 | industry | VARCHAR(255) | 所属行业 |
| 创建者.id | created_by_external | VARCHAR(255) | 创建者外部ID |
| 创建者 | created_by_name | VARCHAR(255) | 创建者名称 |
| 修改者.id | updated_by_external | VARCHAR(255) | 修改者外部ID |
| 修改者 | updated_by_name | VARCHAR(255) | 修改者名称 |
| 创建时间 | created_at_src | DATETIME | 源系统创建时间 |
| 修改时间 | updated_at_src | DATETIME | 源系统修改时间 |
| 描述 | description | TEXT | 客户描述 |
| 最近操作时间 | last_action_at_src | DATETIME | 最近操作时间 |
| 标签 | tags | JSON | 标签数组 |
| 更改日志时间 | change_log_at_src | DATETIME | 更改日志时间 |
| Locked | is_locked | BOOLEAN | 是否锁定 |
| 最后充实时间 | last_enriched_at_src | DATETIME | 最后充实时间 |
| 充实状态 | enrich_status | VARCHAR(50) | 充实状态 |
| 渠道名称 | channel_name | VARCHAR(255) | 渠道名称 |
| 客户需求 | customer_requirements | TEXT | 客户需求（可能包含服务类型） |
| 客户来源 | source_name | VARCHAR(255) | 客户来源（如：客户转介绍、微信扫码、微信群） |
| Connected To.module | linked_module | VARCHAR(100) | 关联模块 |
| 连接到.id | linked_id_external | VARCHAR(255) | 关联外部ID |

### 1.2 客户类型识别

从数据样本分析：
- **个人客户**：如 "T0198C小白"、"刘立明"、"dyco" 等
- **组织客户**：如 "菲菲-斑兔企服"、"斑兔企服 Team Group"、"斑兔&李颖 双向合作" 等
- **渠道客户**：如 "[渠道]Yami"（通过名称前缀识别）

### 1.3 客户来源分析

常见来源：
- 客户转介绍
- 微信扫码
- 微信群
- 其他渠道

### 1.4 客户需求分析

`customer_requirements` 字段可能包含：
- 服务类型代码（如 "CompanyService"）
- 文本描述的需求
- 多个需求（可能需要解析）

## 二、表关系设计

### 2.1 核心表结构

#### 2.1.1 customers（客户表）

**客户类型区分**：
- `customer_type`: 'individual' | 'organization'
  - `individual`: 个人客户
  - `organization`: 组织客户

**客户来源区分**：
- `customer_source_type`: 'own' | 'agent'
  - `own`: 内部客户（直接客户）
  - `agent`: 渠道客户（通过代理/渠道获得）

**层级关系**：
- `parent_customer_id`: 支持组织客户下挂个人客户
  - 组织客户：`parent_customer_id = NULL`
  - 个人客户：可以关联到组织客户

**关联关系**：
- `owner_user_id` → `users.id` (内部客户的所有者，通常是 SALES 角色)
- `agent_id` → `organizations.id` (渠道客户的所有者，organization_type = 'agent')
- `source_id` → `customer_sources.id` (客户来源)
- `channel_id` → `customer_channels.id` (客户渠道)

#### 2.1.2 contacts（联系人表）

**用途**：组织客户下的联系人信息

**关联**：
- `customer_id` → `customers.id` (ON DELETE CASCADE)
- 每个组织客户可以有多个联系人
- `is_primary`: 主要联系人（每个客户唯一）

#### 2.1.3 customer_sources（客户来源表）

**用途**：定义客户来源类型

**字段**：
- `id`, `code`, `name`
- 示例：客户转介绍、微信扫码、微信群、官网、广告等

#### 2.1.4 customer_channels（客户渠道表）

**用途**：定义客户渠道

**字段**：
- `id`, `code`, `name`
- 示例：线上渠道、线下渠道、合作伙伴等

### 2.2 服务记录关联设计

#### 2.2.1 服务记录表（service_records）

**设计思路**：
每个客户可以有多条服务记录，每条服务记录对应一个具体的服务需求。

**表结构**：
```sql
CREATE TABLE IF NOT EXISTS service_records (
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  customer_id             CHAR(36) NOT NULL,
  service_type_id         CHAR(36),  -- 关联服务类型
  product_id              CHAR(36),  -- 关联具体产品/服务（可选）
  service_name            VARCHAR(255),  -- 服务名称（冗余字段，便于查询）
  service_description     TEXT,  -- 服务描述/需求
  status                  VARCHAR(50) DEFAULT 'pending',  -- 状态：pending, in_progress, completed, cancelled
  priority                VARCHAR(20) DEFAULT 'normal',  -- 优先级：low, normal, high, urgent
  expected_start_date     DATE,  -- 预期开始日期
  expected_completion_date DATE,  -- 预期完成日期
  actual_start_date       DATE,  -- 实际开始日期
  actual_completion_date  DATE,  -- 实际完成日期
  contact_id              CHAR(36),  -- 关联联系人（如果是组织客户）
  notes                   TEXT,  -- 备注
  created_by              CHAR(36),  -- 创建人
  updated_by              CHAR(36),  -- 更新人
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
  FOREIGN KEY (service_type_id) REFERENCES service_types(id) ON DELETE SET NULL,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL,
  FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
);
```

**索引**：
```sql
CREATE INDEX ix_service_records_customer ON service_records(customer_id);
CREATE INDEX ix_service_records_service_type ON service_records(service_type_id);
CREATE INDEX ix_service_records_status ON service_records(status);
CREATE INDEX ix_service_records_created_at ON service_records(created_at);
```

#### 2.2.2 服务记录与订单的关系

**设计思路**：
- 服务记录（service_records）：客户的服务需求/意向
- 订单（orders）：已确认的服务订单，关联到具体的产品和价格

**关系**：
- 一个服务记录可以生成多个订单（同一服务可以多次下单）
- 一个订单必须关联一个客户，可以关联一个服务记录（可选）

**订单表扩展**（如果需要关联服务记录）：
```sql
ALTER TABLE orders ADD COLUMN service_record_id CHAR(36);
ALTER TABLE orders ADD CONSTRAINT fk_orders_service_record 
  FOREIGN KEY (service_record_id) REFERENCES service_records(id) ON DELETE SET NULL;
CREATE INDEX ix_orders_service_record ON orders(service_record_id);
```

### 2.3 完整表关系图

```
customers (客户表)
├── customer_type: 'individual' | 'organization'
├── customer_source_type: 'own' | 'agent'
├── parent_customer_id → customers.id (组织层级)
├── owner_user_id → users.id (内部客户所有者)
├── agent_id → organizations.id (渠道客户所有者)
├── source_id → customer_sources.id (客户来源)
└── channel_id → customer_channels.id (客户渠道)

contacts (联系人表)
└── customer_id → customers.id (组织客户联系人)

service_records (服务记录表)
├── customer_id → customers.id (客户)
├── service_type_id → service_types.id (服务类型)
├── product_id → products.id (具体产品，可选)
└── contact_id → contacts.id (联系人，可选)

orders (订单表)
├── customer_id → customers.id (客户)
├── product_id → products.id (产品)
├── service_record_id → service_records.id (服务记录，可选)
└── sales_user_id → users.id (销售)
```

## 三、数据迁移建议

### 3.1 从 Accounts.xlsx 导入客户数据

1. **客户基本信息**：直接映射到 `customers` 表
2. **客户来源**：根据 `source_name` 字段，创建或关联 `customer_sources` 记录
3. **客户渠道**：根据 `channel_name` 字段，创建或关联 `customer_channels` 记录
4. **客户需求**：解析 `customer_requirements` 字段，创建 `service_records` 记录
5. **客户类型判断**：
   - 如果名称包含 "[渠道]"，设置为 `customer_source_type = 'agent'`
   - 根据名称和描述判断是个人还是组织客户

### 3.2 服务记录创建规则

从 `customer_requirements` 字段创建服务记录：
- 如果包含服务类型代码（如 "CompanyService"），关联到对应的 `service_types`
- 如果包含产品代码，关联到对应的 `products`
- 创建初始状态为 'pending' 的服务记录

## 四、API 设计建议

### 4.1 客户管理 API

- `GET /api/service-management/customers` - 获取客户列表
- `GET /api/service-management/customers/{id}` - 获取客户详情
- `POST /api/service-management/customers` - 创建客户
- `PUT /api/service-management/customers/{id}` - 更新客户
- `DELETE /api/service-management/customers/{id}` - 删除客户

### 4.2 服务记录 API

- `GET /api/service-management/customers/{customer_id}/service-records` - 获取客户的服务记录
- `POST /api/service-management/customers/{customer_id}/service-records` - 创建服务记录
- `PUT /api/service-management/service-records/{id}` - 更新服务记录
- `DELETE /api/service-management/service-records/{id}` - 删除服务记录

### 4.3 联系人 API

- `GET /api/service-management/customers/{customer_id}/contacts` - 获取客户联系人
- `POST /api/service-management/customers/{customer_id}/contacts` - 创建联系人
- `PUT /api/service-management/contacts/{id}` - 更新联系人
- `DELETE /api/service-management/contacts/{id}` - 删除联系人

## 五、实现优先级

1. **Phase 1**: 客户基础 CRUD（customers 表）
2. **Phase 2**: 联系人管理（contacts 表）
3. **Phase 3**: 服务记录管理（service_records 表）
4. **Phase 4**: 客户来源和渠道管理（customer_sources, customer_channels）
5. **Phase 5**: 数据导入（从 Accounts.xlsx）

