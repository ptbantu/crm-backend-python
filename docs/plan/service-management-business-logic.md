# 服务管理业务逻辑梳理

## 一、核心业务需求

### 1.1 业务场景
- **一个服务可能由多个供应商提供**
- **每个供应商对同一个服务有不同的报价**
- **服务是共享的，修改服务名称时，所有供应商都能看到更新**
- **价格是供应商特定的，每个供应商可以设置自己的价格**

### 1.2 业务规则
1. 服务（Product）是全局共享的，所有供应商都可以提供
2. 供应商通过 `vendor_products` 表关联到服务
3. 每个供应商对同一服务可以设置不同的成本价
4. 价格类型包括：成本价、渠道价、直客价、列表价
5. 价格可以是供应商特定的，也可以是通用的（organization_id = NULL）

## 二、数据库表结构设计

### 2.1 四张核心表

#### 表1：供应商表（organizations）
**作用**：存储供应商/组织的基本信息

**关键字段**：
- `id` - 供应商ID
- `name` - 供应商名称
- `organization_type` - 组织类型（vendor/internal/agent）
- `is_active` - 是否激活

**说明**：
- 供应商可以是外部供应商（vendor）或内部组织（internal）
- 一个供应商可以提供多个服务

#### 表2：服务列表细则表（products）
**作用**：存储服务的通用信息，所有供应商共享

**关键字段**：
- `id` - 服务ID
- `name` - 服务名称（**共享**，修改后所有供应商都能看到）
- `code` - 服务编码（唯一）
- `category_id` - 分类ID
- `service_type` - 服务类型（visa, company_registration等）
- `service_subtype` - 服务子类型（B211, C211等）
- `description` - 服务描述
- `required_documents` - 所需资料
- `processing_days` - 处理天数（通用）
- `is_active` - 是否激活

**业务规则**：
- ✅ **服务是共享的**：所有供应商都看到相同的服务名称、描述等信息
- ✅ **修改服务名称**：只需要在 `products` 表中修改一次，所有供应商都能看到更新
- ✅ **服务可以有默认价格**：`products` 表中的价格字段可以作为默认价格或参考价格

**示例**：
```
服务：印尼工作签证 B211
- 名称：印尼工作签证 B211（所有供应商共享）
- 描述：适用于在印尼工作的外国人（所有供应商共享）
- 所需资料：护照、照片、申请表（所有供应商共享）
```

#### 表3：供应商提供服务表（vendor_products）
**作用**：关联供应商和服务，存储供应商特定的信息

**关键字段**：
- `id` - 关联ID
- `organization_id` - 供应商ID（FK -> organizations）
- `product_id` - 服务ID（FK -> products）
- `is_primary` - 是否主要供应商
- `priority` - 优先级
- `cost_price_idr` - 该供应商的成本价（IDR）
- `cost_price_cny` - 该供应商的成本价（CNY）
- `processing_days` - 该供应商处理该服务的天数（可能不同）
- `is_available` - 该供应商是否提供此服务
- `available_from` - 可用开始时间
- `available_to` - 可用结束时间

**业务规则**：
- ✅ **多对多关系**：一个供应商可以提供多个服务，一个服务可以由多个供应商提供
- ✅ **供应商特定信息**：每个供应商对同一服务可以有不同的成本价、处理天数等
- ✅ **唯一约束**：`(organization_id, product_id)` 唯一，确保一个供应商对同一服务只有一条记录

**示例**：
```
服务：印尼工作签证 B211
- 供应商A：成本价 2,000,000 IDR，处理天数 5天
- 供应商B：成本价 1,800,000 IDR，处理天数 7天
- 供应商C：成本价 2,200,000 IDR，处理天数 3天（加急）
```

#### 表4：服务价格表（product_prices）
**作用**：存储不同价格类型和货币的价格，支持供应商特定价格

**关键字段**：
- `id` - 价格ID
- `product_id` - 服务ID（FK -> products）
- `organization_id` - 供应商ID（FK -> organizations，**NULL表示通用价格**）
- `price_type` - 价格类型（cost/channel/direct/list）
- `currency` - 货币（IDR/CNY）
- `amount` - 价格金额
- `effective_from` - 生效时间
- `effective_to` - 失效时间（NULL表示当前有效）

**业务规则**：
- ✅ **价格可以是供应商特定的**：`organization_id` 不为 NULL 时，表示该供应商的特定价格
- ✅ **价格可以是通用的**：`organization_id` 为 NULL 时，表示所有供应商的通用价格
- ✅ **支持多价格类型**：成本价、渠道价、直客价、列表价
- ✅ **支持多货币**：IDR、CNY
- ✅ **支持时间有效性**：价格可以设置生效和失效时间

**示例**：
```
服务：印尼工作签证 B211

通用价格（organization_id = NULL）：
- 列表价：3,500,000 IDR（所有供应商通用）

供应商A特定价格（organization_id = A）：
- 成本价：2,000,000 IDR
- 渠道价：2,500,000 IDR
- 直客价：3,000,000 IDR

供应商B特定价格（organization_id = B）：
- 成本价：1,800,000 IDR
- 渠道价：2,300,000 IDR
- 直客价：2,800,000 IDR
```

## 三、表关系图

```
┌─────────────────┐
│  organizations  │ (供应商表)
│  (供应商)       │
└────────┬────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────────────┐
│   vendor_products       │ (供应商提供服务表)
│   (供应商-服务关联)     │
│                         │
│ - organization_id (FK)  │
│ - product_id (FK)       │
│ - cost_price_idr        │ ← 供应商特定的成本价
│ - processing_days        │ ← 供应商特定的处理天数
│ - is_available          │ ← 供应商是否提供此服务
└────────┬────────────────┘
         │
         │ N:1
         │
         ▼
┌─────────────────┐
│    products     │ (服务列表细则表)
│    (服务)       │
│                 │
│ - name          │ ← 共享的服务名称
│ - description   │ ← 共享的服务描述
│ - code          │ ← 服务编码（唯一）
└────────┬────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────────────┐
│   product_prices        │ (服务价格表)
│   (服务价格)            │
│                         │
│ - product_id (FK)       │
│ - organization_id (FK)  │ ← NULL = 通用价格
│                         │   非NULL = 供应商特定价格
│ - price_type            │ ← cost/channel/direct/list
│ - currency              │ ← IDR/CNY
│ - amount                │
└─────────────────────────┘
```

## 四、业务逻辑示例

### 4.1 场景：多个供应商提供同一个服务

**服务信息**（products表）：
```json
{
  "id": "product-001",
  "name": "印尼工作签证 B211",
  "code": "VISA_B211",
  "description": "适用于在印尼工作的外国人",
  "required_documents": "护照、照片、申请表",
  "processing_days": 5,  // 通用处理天数（参考值）
  "is_active": true
}
```

**供应商关联**（vendor_products表）：
```json
// 供应商A
{
  "id": "vp-001",
  "organization_id": "vendor-A",
  "product_id": "product-001",
  "cost_price_idr": 2000000,
  "cost_price_cny": 1000,
  "processing_days": 5,  // 供应商A的处理天数
  "is_available": true,
  "is_primary": true
}

// 供应商B
{
  "id": "vp-002",
  "organization_id": "vendor-B",
  "product_id": "product-001",
  "cost_price_idr": 1800000,
  "cost_price_cny": 900,
  "processing_days": 7,  // 供应商B的处理天数（更慢）
  "is_available": true,
  "is_primary": false
}

// 供应商C
{
  "id": "vp-003",
  "organization_id": "vendor-C",
  "product_id": "product-001",
  "cost_price_idr": 2200000,
  "cost_price_cny": 1100,
  "processing_days": 3,  // 供应商C的处理天数（更快，但更贵）
  "is_available": true,
  "is_primary": false
}
```

**价格信息**（product_prices表）：
```json
// 供应商A的价格
{
  "product_id": "product-001",
  "organization_id": "vendor-A",  // 供应商特定
  "price_type": "cost",
  "currency": "IDR",
  "amount": 2000000
},
{
  "product_id": "product-001",
  "organization_id": "vendor-A",
  "price_type": "channel",
  "currency": "IDR",
  "amount": 2500000
},
{
  "product_id": "product-001",
  "organization_id": "vendor-A",
  "price_type": "direct",
  "currency": "IDR",
  "amount": 3000000
}

// 供应商B的价格
{
  "product_id": "product-001",
  "organization_id": "vendor-B",  // 供应商特定
  "price_type": "cost",
  "currency": "IDR",
  "amount": 1800000
},
{
  "product_id": "product-001",
  "organization_id": "vendor-B",
  "price_type": "channel",
  "currency": "IDR",
  "amount": 2300000
},
{
  "product_id": "product-001",
  "organization_id": "vendor-B",
  "price_type": "direct",
  "currency": "IDR",
  "amount": 2800000
}

// 通用价格（所有供应商共享）
{
  "product_id": "product-001",
  "organization_id": null,  // NULL = 通用价格
  "price_type": "list",
  "currency": "IDR",
  "amount": 3500000
}
```

### 4.2 场景：修改服务名称

**操作**：修改 `products` 表中的服务名称

**影响**：
- ✅ 所有供应商都能看到新的服务名称
- ✅ 不需要在每个供应商的记录中修改
- ✅ `vendor_products` 和 `product_prices` 表不需要修改

**示例**：
```sql
-- 修改服务名称
UPDATE products 
SET name = '印尼工作签证 B211（更新版）'
WHERE id = 'product-001';

-- 所有供应商关联的服务名称都会自动更新（通过 JOIN 查询）
```

### 4.3 场景：供应商添加新服务

**操作流程**：
1. 检查服务是否已存在（`products` 表）
2. 如果不存在，创建新服务
3. 在 `vendor_products` 表中创建关联记录
4. 在 `product_prices` 表中设置该供应商的价格

**示例**：
```sql
-- 1. 检查服务是否存在
SELECT * FROM products WHERE code = 'VISA_B211';

-- 2. 如果不存在，创建服务（只需要创建一次）
INSERT INTO products (name, code, ...) VALUES (...);

-- 3. 供应商A关联此服务
INSERT INTO vendor_products (organization_id, product_id, cost_price_idr, ...) 
VALUES ('vendor-A', 'product-001', 2000000, ...);

-- 4. 设置供应商A的价格
INSERT INTO product_prices (product_id, organization_id, price_type, currency, amount)
VALUES 
  ('product-001', 'vendor-A', 'cost', 'IDR', 2000000),
  ('product-001', 'vendor-A', 'channel', 'IDR', 2500000),
  ('product-001', 'vendor-A', 'direct', 'IDR', 3000000);
```

### 4.4 场景：其他供应商也提供相同服务

**操作**：只需要在 `vendor_products` 表中添加关联，不需要重新创建服务

**示例**：
```sql
-- 供应商B也提供相同的服务
INSERT INTO vendor_products (organization_id, product_id, cost_price_idr, ...) 
VALUES ('vendor-B', 'product-001', 1800000, ...);  -- 使用相同的 product_id

-- 设置供应商B的价格
INSERT INTO product_prices (product_id, organization_id, price_type, currency, amount)
VALUES 
  ('product-001', 'vendor-B', 'cost', 'IDR', 1800000),
  ('product-001', 'vendor-B', 'channel', 'IDR', 2300000),
  ('product-001', 'vendor-B', 'direct', 'IDR', 2800000);
```

## 五、查询示例

### 5.1 查询某个服务的所有供应商

```sql
SELECT 
  p.name as service_name,
  o.name as vendor_name,
  vp.cost_price_idr,
  vp.cost_price_cny,
  vp.processing_days,
  vp.is_available
FROM products p
JOIN vendor_products vp ON vp.product_id = p.id
JOIN organizations o ON o.id = vp.organization_id
WHERE p.id = 'product-001'
  AND vp.is_available = true
ORDER BY vp.priority, vp.cost_price_idr;
```

### 5.2 查询某个供应商提供的所有服务

```sql
SELECT 
  p.name as service_name,
  p.code as service_code,
  vp.cost_price_idr,
  vp.is_available
FROM organizations o
JOIN vendor_products vp ON vp.organization_id = o.id
JOIN products p ON p.id = vp.product_id
WHERE o.id = 'vendor-A'
  AND p.is_active = true
ORDER BY p.name;
```

### 5.3 查询某个服务的价格（包括通用价格和供应商特定价格）

```sql
SELECT 
  p.name as service_name,
  o.name as vendor_name,
  pp.price_type,
  pp.currency,
  pp.amount,
  pp.effective_from,
  pp.effective_to
FROM products p
LEFT JOIN product_prices pp ON pp.product_id = p.id
LEFT JOIN organizations o ON o.id = pp.organization_id
WHERE p.id = 'product-001'
  AND (pp.effective_to IS NULL OR pp.effective_to > NOW())
ORDER BY 
  CASE WHEN pp.organization_id IS NULL THEN 0 ELSE 1 END,  -- 通用价格在前
  o.name,
  pp.price_type,
  pp.currency;
```

## 六、设计优势

### 6.1 数据一致性
- ✅ **服务信息统一管理**：所有供应商看到相同的服务名称、描述等信息
- ✅ **避免数据冗余**：不需要在每个供应商记录中重复存储服务信息
- ✅ **易于维护**：修改服务信息只需要更新 `products` 表

### 6.2 灵活性
- ✅ **多供应商支持**：一个服务可以由多个供应商提供
- ✅ **价格差异化**：每个供应商可以设置不同的价格
- ✅ **通用价格支持**：可以设置所有供应商共享的通用价格
- ✅ **时间有效性**：价格可以设置生效和失效时间

### 6.3 扩展性
- ✅ **易于添加新供应商**：只需要在 `vendor_products` 表中添加关联
- ✅ **易于添加新服务**：创建服务后，多个供应商可以关联
- ✅ **支持价格历史**：`product_price_history` 表记录价格变更历史

## 七、总结

### 7.1 表职责划分

| 表名 | 职责 | 数据特点 |
|------|------|----------|
| `organizations` | 存储供应商信息 | 供应商基本信息 |
| `products` | 存储服务通用信息 | **共享数据**，所有供应商共享 |
| `vendor_products` | 关联供应商和服务 | 供应商特定的服务信息（成本价、处理天数等） |
| `product_prices` | 存储价格信息 | 支持通用价格和供应商特定价格 |

### 7.2 核心业务规则

1. **服务是共享的**：`products` 表中的服务信息是所有供应商共享的
2. **价格是供应商特定的**：每个供应商可以设置自己的价格
3. **支持通用价格**：可以设置所有供应商共享的通用价格
4. **多对多关系**：一个供应商可以提供多个服务，一个服务可以由多个供应商提供

### 7.3 数据修改影响

| 操作 | 影响的表 | 影响范围 |
|------|----------|----------|
| 修改服务名称 | `products` | 所有供应商都能看到更新 |
| 添加供应商关联 | `vendor_products` | 只影响该供应商 |
| 设置供应商价格 | `product_prices` | 只影响该供应商的价格 |
| 设置通用价格 | `product_prices` (organization_id = NULL) | 所有供应商共享 |

---

**设计符合业务需求**：✅
- 服务是共享的，修改服务名称时所有供应商都能看到
- 价格是供应商特定的，每个供应商可以设置不同的报价
- 支持多供应商提供同一服务
- 数据结构清晰，易于维护和扩展

