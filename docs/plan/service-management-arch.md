# 服务管理架构设计文档

## 一、概述

服务管理模块负责管理由供应商提供的各种服务（如签证服务、公司注册服务等），包括服务分类、服务信息、定价体系、供应商关联等功能。同时，服务管理模块还包含客户管理功能，包括客户信息管理、联系人管理、服务记录管理等。

## 二、业务需求分析

### 2.1 从定价表分析的业务需求

基于 `副本斑兔标准定价 Quotation Company Price (1).xlsx` 分析：

#### 服务类型（基于 Excel 数据分析）

从定价表分析得出以下服务分类：

1. **签证服务** (VisaService_签证服务) - 40 个产品
   - 落地签（B1）- 新办、续签、加速、机场线下续签
   - 商务签（C2/C11/C12）- 单次、多次、续签
   - 工作签（C16/C17/C18/C20）- 90天、长期
   - 投资签（C12）
   - 续签服务
   - 加速服务
   - ITK 找回服务

2. **接送关服务** (Jemput&AntarService_接送关服务) - 1 个产品
   - 机场接送服务

3. **公司开办服务** (CompanyService_公司开办服务) - 13 个产品
   - 公司注册相关服务

4. **税务服务** (TaxService_税务服务) - 11 个产品
   - 税务申报、税务咨询等服务

5. **资质注册服务** (LicenseService_资质注册服务) - 10 个产品
   - 各类资质注册服务

#### 价格体系
1. **成本价格** (Cost Price) - 供应商提供的成本价
2. **渠道合作价** (Channel Price) - 给渠道代理的价格
   - IDR（印尼盾）
   - CNY（人民币）
3. **直客价格** (Direct Price) - 给最终客户的价格
   - IDR（印尼盾）
   - CNY（人民币）

#### 利润计算
- 渠道方利润 = 直客价格 - 渠道合作价
- 渠道客户利润 = 渠道合作价 - 成本价格
- 直客利润 = 直客价格 - 成本价格

#### 服务属性（基于 Excel 表头分析）

从定价表表头分析，服务包含以下属性：

**基本信息：**
- 服务项目（服务名称）
- 产品分类
- 产品编号（唯一标识）

**价格信息：**
- 成本价格
- 渠道合作价（IDR/CNY）
- 直客价格（IDR/RMB）
- 利润计算（渠道方利润、渠道客户利润、直客利润）
- 利润率

**服务属性：**
- 所需资料（Required Documents）
- 办理时长（Processing Time）
- 备注（Notes）
- SLA（服务级别协议）

**业务属性：**
- 提成比例（Commission Rate）
- 提成金额（Commission Amount）
- 等值人民币（Equivalent CNY）
- 每月单数（Monthly Orders）
- 合计（Total）

**状态管理：**
- 服务状态（激活/暂停/停用）

## 三、数据模型设计

### 3.1 数据库表结构（基于现有 schema）

#### 3.1.1 产品分类表 (product_categories)
```sql
CREATE TABLE IF NOT EXISTS product_categories (
  id                 CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  code               VARCHAR(100) NOT NULL UNIQUE,  -- 分类编码，如：VisaService_签证服务
  name               VARCHAR(255),                    -- 分类名称
  description        TEXT,                           -- 分类描述
  parent_id          CHAR(36),                       -- 父分类ID（支持分类层级）
  display_order      INT DEFAULT 0,                  -- 显示顺序
  is_active          BOOLEAN DEFAULT TRUE,           -- 是否激活
  created_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (parent_id) REFERENCES product_categories(id) ON DELETE SET NULL
);
```

#### 3.1.2 产品/服务表 (products) - 已存在，需要扩展
现有字段：
- `id`, `name`, `code`, `vendor_id` (供应商ID)
- `category_id` (分类ID)
- `price_list` (列表价)
- `price_channel` (渠道价)
- `price_cost` (成本价)
- `required_documents` (所需资料)
- `processing_time` (处理时间)
- `is_active`, `is_locked`

**需要扩展的字段：**
```sql
ALTER TABLE products ADD COLUMN IF NOT EXISTS (
  -- 多货币价格（基于 Excel 分析）
  price_cost_idr          DECIMAL(18,2),              -- 成本价（IDR）- 对应 Excel "成本价格"
  price_cost_cny          DECIMAL(18,2),              -- 成本价（CNY）- 计算得出
  price_channel_idr       DECIMAL(18,2),              -- 渠道价（IDR）- 对应 Excel "渠道合作价(IDR)"
  price_channel_cny       DECIMAL(18,2),              -- 渠道价（CNY）- 对应 Excel "渠道合作价(CNY)"
  price_direct_idr        DECIMAL(18,2),              -- 直客价（IDR）- 对应 Excel "价格(IDR)"
  price_direct_cny        DECIMAL(18,2),              -- 直客价（CNY）- 对应 Excel "价格(RMB)"
  price_list_idr          DECIMAL(18,2),              -- 列表价（IDR）
  price_list_cny          DECIMAL(18,2),              -- 列表价（CNY）
  
  -- 汇率相关
  default_currency        VARCHAR(10) DEFAULT 'IDR',  -- 默认货币
  exchange_rate           DECIMAL(18,9) DEFAULT 2000,  -- 汇率（IDR/CNY），默认 2000
  
  -- 服务属性（基于 Excel 分析）
  service_type            VARCHAR(50),                -- 服务类型：visa, company_registration, tax, license, etc.
  service_subtype         VARCHAR(50),                -- 服务子类型：B1, C211, C212, etc.
  validity_period         INT,                        -- 有效期（天数）
  processing_days         INT,                        -- 处理天数 - 对应 Excel "办理时长"
  processing_time_text    VARCHAR(255),               -- 处理时间文本描述（如：3个工作日）
  is_urgent_available     BOOLEAN DEFAULT FALSE,      -- 是否支持加急
  urgent_processing_days   INT,                        -- 加急处理天数
  urgent_price_surcharge  DECIMAL(18,2),              -- 加急附加费
  
  -- 利润计算（冗余字段，便于查询）- 对应 Excel 利润相关列
  channel_profit          DECIMAL(18,2),              -- 渠道方利润 = 直客价 - 渠道价
  channel_profit_rate     DECIMAL(5,4),              -- 渠道方利润率
  channel_customer_profit DECIMAL(18,2),              -- 渠道客户利润 = 渠道价 - 成本价
  channel_customer_profit_rate DECIMAL(5,4),         -- 渠道客户利润率
  direct_profit           DECIMAL(18,2),              -- 直客利润 = 直客价 - 成本价
  direct_profit_rate      DECIMAL(5,4),              -- 直客利润率
  
  -- 业务属性（基于 Excel 分析）
  commission_rate         DECIMAL(5,4),               -- 提成比例 - 对应 Excel "提成比例"
  commission_amount       DECIMAL(18,2),              -- 提成金额 - 对应 Excel "提成金额"
  equivalent_cny          DECIMAL(18,2),              -- 等值人民币 - 对应 Excel "等值人民币"
  monthly_orders          INT,                        -- 每月单数 - 对应 Excel "每月单数"
  total_amount            DECIMAL(18,2),              -- 合计 - 对应 Excel "合计"
  
  -- SLA 和服务级别
  sla_description         TEXT,                        -- SLA 描述 - 对应 Excel "SLA"
  service_level           VARCHAR(50),                -- 服务级别：standard, premium, vip
  
  -- 状态管理
  status                  VARCHAR(50) DEFAULT 'active', -- 状态：active, suspended, discontinued
  suspended_reason        TEXT,                        -- 暂停原因
  discontinued_at         DATETIME,                    -- 停用时间
  
  -- 元数据
  tags                    JSON DEFAULT (JSON_ARRAY()), -- 标签
  metadata                JSON,                        -- 扩展元数据（可存储 Excel 中的其他字段）
  notes                   TEXT,                        -- 备注 - 对应 Excel "备注"
);
```

#### 3.1.3 供应商服务关联表 (vendor_products) - 新建
用于管理供应商提供的服务，支持一个服务由多个供应商提供，或一个供应商提供多个服务。

```sql
CREATE TABLE IF NOT EXISTS vendor_products (
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  vendor_id               CHAR(36) NOT NULL,          -- 供应商组织ID
  product_id              CHAR(36) NOT NULL,          -- 服务/产品ID
  is_primary              BOOLEAN DEFAULT FALSE,      -- 是否主要供应商
  priority                INT DEFAULT 0,               -- 优先级（数字越小优先级越高）
  cost_price_idr          DECIMAL(18,2),              -- 该供应商的成本价（IDR）
  cost_price_cny          DECIMAL(18,2),              -- 该供应商的成本价（CNY）
  min_quantity            INT DEFAULT 1,              -- 最小订购量
  max_quantity            INT,                        -- 最大订购量
  lead_time_days          INT,                        -- 交货期（天数）
  is_available             BOOLEAN DEFAULT TRUE,      -- 是否可用
  availability_notes      TEXT,                       -- 可用性说明
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (vendor_id) REFERENCES organizations(id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
  UNIQUE KEY uk_vendor_product (vendor_id, product_id)
);

CREATE INDEX ix_vendor_products_vendor ON vendor_products(vendor_id);
CREATE INDEX ix_vendor_products_product ON vendor_products(product_id);
CREATE INDEX ix_vendor_products_primary ON vendor_products(product_id, is_primary);
```

#### 3.1.4 服务价格历史表 (product_price_history) - 新建
记录价格变更历史，用于审计和价格趋势分析。

```sql
CREATE TABLE IF NOT EXISTS product_price_history (
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  product_id              CHAR(36) NOT NULL,
  vendor_id               CHAR(36),                   -- 如果是供应商特定价格
  price_type              VARCHAR(50) NOT NULL,       -- cost, channel, direct, list
  currency                VARCHAR(10) NOT NULL,        -- IDR, CNY
  old_price               DECIMAL(18,2),
  new_price               DECIMAL(18,2),
  change_reason            TEXT,                        -- 变更原因
  effective_from          DATETIME NOT NULL,           -- 生效时间
  effective_to            DATETIME,                    -- 失效时间（NULL表示当前有效）
  changed_by              CHAR(36),                    -- 变更人
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
  FOREIGN KEY (vendor_id) REFERENCES organizations(id) ON DELETE SET NULL,
  FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX ix_price_history_product ON product_price_history(product_id);
CREATE INDEX ix_price_history_vendor ON product_price_history(vendor_id);
CREATE INDEX ix_price_history_effective ON product_price_history(effective_from, effective_to);
```

## 四、服务架构设计

### 4.1 微服务划分

#### 4.1.1 Product Service（产品/服务管理服务）
**职责：**
- 服务/产品的 CRUD 操作
- 服务分类管理
- 服务搜索和筛选
- 服务状态管理

**主要功能模块：**
1. **Product Management（产品管理）**
   - 创建、更新、删除服务
   - 服务信息查询
   - 服务列表（支持分页、筛选、排序）
   - 服务详情查询

2. **Category Management（分类管理）**
   - 分类 CRUD
   - 分类树形结构管理
   - 分类下的服务查询

3. **Product Search（服务搜索）**
   - 全文搜索
   - 多条件筛选（分类、供应商、价格区间、状态等）
   - 排序（价格、创建时间、更新时间等）

#### 4.1.2 Pricing Service（定价管理服务）- 可选独立服务
**职责：**
- 价格计算和管理
- 价格历史记录
- 利润计算
- 汇率管理

**主要功能模块：**
1. **Price Management（价格管理）**
   - 设置/更新服务价格
   - 批量价格更新
   - 价格审核流程

2. **Price Calculation（价格计算）**
   - 根据客户类型计算价格（渠道/直客）
   - 利润计算
   - 汇率转换

3. **Price History（价格历史）**
   - 价格变更记录
   - 价格趋势分析
   - 价格审计

#### 4.1.3 Vendor Service（供应商服务管理）- 可选独立服务
**职责：**
- 供应商服务关联管理
- 供应商服务可用性管理
- 供应商服务优先级管理

**主要功能模块：**
1. **Vendor Product Association（供应商服务关联）**
   - 关联供应商和服务
   - 设置供应商优先级
   - 供应商服务成本价管理

2. **Vendor Availability（供应商可用性）**
   - 管理供应商服务可用性
   - 供应商服务库存/容量管理

#### 4.1.4 Customer Service（客户管理服务）
**职责：**
- 客户信息管理
- 联系人管理
- 服务记录管理

**主要功能模块：**
1. **Customer Management（客户管理）**
   - 客户创建、更新、删除、查询
   - 支持个人客户和组织客户
   - 支持内部客户和渠道客户
   - 支持客户层级关系（组织下挂个人）

2. **Contact Management（联系人管理）**
   - 联系人创建、更新、删除、查询
   - 主要联系人自动管理
   - 联系人作为接单人员（sales）

3. **Service Record Management（服务记录管理）**
   - 服务记录创建、更新、删除、查询
   - 服务记录状态流转
   - 优先级管理
   - 接单人员关联

### 4.2 推荐架构方案

**方案一：单一服务（推荐初期使用）**
- 将所有功能整合到 **Service Management Service** 中
- 包括：产品管理、客户管理、联系人管理、服务记录管理
- 优点：开发简单，部署方便，减少服务间通信
- 缺点：服务职责较多，后续拆分成本高

**方案二：拆分服务（推荐后期使用）**
- Product Service：产品管理
- Pricing Service：定价管理
- Vendor Service：供应商管理
- Customer Service：客户管理
- 优点：职责清晰，易于扩展和维护
- 缺点：服务间通信复杂，部署成本高

**建议：** 初期采用方案一，后续根据业务复杂度逐步拆分。

## 五、API 设计

### 5.1 Product Service API

#### 5.1.1 产品分类 API

```
GET    /api/products/categories              # 获取分类列表（树形结构）
GET    /api/products/categories/{id}         # 获取分类详情
POST   /api/products/categories              # 创建分类
PUT    /api/products/categories/{id}         # 更新分类
DELETE /api/products/categories/{id}         # 删除分类
GET    /api/products/categories/{id}/products # 获取分类下的服务
```

#### 5.1.2 产品/服务 API

```
GET    /api/products                         # 获取服务列表（支持分页、筛选、排序）
GET    /api/products/{id}                    # 获取服务详情
POST   /api/products                         # 创建服务
PUT    /api/products/{id}                    # 更新服务
DELETE /api/products/{id}                    # 删除服务
PATCH  /api/products/{id}/status             # 更新服务状态（激活/暂停/停用）
GET    /api/products/{id}/prices             # 获取服务价格信息
PUT    /api/products/{id}/prices             # 更新服务价格
GET    /api/products/search                  # 搜索服务（全文搜索）
GET    /api/products/{id}/vendors            # 获取服务的供应商列表
POST   /api/products/{id}/vendors            # 关联供应商到服务
DELETE /api/products/{id}/vendors/{vendor_id} # 取消供应商关联
```

#### 5.1.3 价格计算 API

```
POST   /api/products/calculate-price         # 计算价格（根据客户类型、数量等）
GET    /api/products/{id}/price-history     # 获取价格历史
```

#### 5.1.4 客户管理 API

```
# 客户管理
POST   /api/service-management/customers              # 创建客户
GET    /api/service-management/customers               # 获取客户列表
GET    /api/service-management/customers/{id}         # 获取客户详情
PUT    /api/service-management/customers/{id}         # 更新客户
DELETE /api/service-management/customers/{id}         # 删除客户

# 联系人管理
POST   /api/service-management/contacts                # 创建联系人
GET    /api/service-management/contacts/{id}          # 获取联系人详情
GET    /api/service-management/contacts/customers/{customer_id}/contacts  # 获取客户的联系人列表
PUT    /api/service-management/contacts/{id}          # 更新联系人
DELETE /api/service-management/contacts/{id}         # 删除联系人

# 服务记录管理
POST   /api/service-management/service-records         # 创建服务记录
GET    /api/service-management/service-records         # 获取服务记录列表
GET    /api/service-management/service-records/{id}    # 获取服务记录详情
GET    /api/service-management/service-records/customers/{customer_id}/service-records  # 获取客户的服务记录列表
PUT    /api/service-management/service-records/{id}     # 更新服务记录
DELETE /api/service-management/service-records/{id}   # 删除服务记录
```

### 5.2 数据模型（Pydantic Schemas）

#### 5.2.1 ProductCategory（产品分类）

```python
class ProductCategoryCreateRequest(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    display_order: int = 0

class ProductCategoryResponse(BaseModel):
    id: str
    code: str
    name: str
    description: Optional[str]
    parent_id: Optional[str]
    parent_name: Optional[str]
    display_order: int
    is_active: bool
    children_count: int
    products_count: int
    created_at: datetime
    updated_at: datetime
```

#### 5.2.2 Product（产品/服务）

```python
class ProductCreateRequest(BaseModel):
    name: str
    code: str
    category_id: str
    vendor_id: Optional[str] = None
    service_type: Optional[str] = None
    service_subtype: Optional[str] = None
    
    # 价格信息
    price_cost_idr: Optional[Decimal] = None
    price_cost_cny: Optional[Decimal] = None
    price_channel_idr: Optional[Decimal] = None
    price_channel_cny: Optional[Decimal] = None
    price_direct_idr: Optional[Decimal] = None
    price_direct_cny: Optional[Decimal] = None
    default_currency: str = "IDR"
    exchange_rate: Optional[Decimal] = None
    
    # 服务属性
```

#### 5.2.3 Customer（客户）

```python
class CustomerCreateRequest(BaseModel):
    name: str
    code: Optional[str] = None
    customer_type: str = "individual"  # individual/organization
    customer_source_type: str = "own"  # own/agent
    parent_customer_id: Optional[str] = None
    owner_user_id: Optional[str] = None
    agent_id: Optional[str] = None
    source_id: Optional[str] = None
    channel_id: Optional[str] = None
    level: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class CustomerResponse(BaseModel):
    id: str
    name: str
    code: Optional[str]
    customer_type: str
    customer_source_type: str
    parent_customer_id: Optional[str]
    owner_user_id: Optional[str]
    level: Optional[str]
    industry: Optional[str]
    created_at: datetime
    updated_at: datetime
```

#### 5.2.4 Contact（联系人）

```python
class ContactCreateRequest(BaseModel):
    customer_id: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    position: Optional[str] = None
    is_primary: bool = False
    is_decision_maker: bool = False

class ContactResponse(BaseModel):
    id: str
    customer_id: str
    customer_name: Optional[str]
    first_name: str
    last_name: str
    full_name: Optional[str]
    email: Optional[str]
    mobile: Optional[str]
    position: Optional[str]
    is_primary: bool
    is_decision_maker: bool
    created_at: datetime
    updated_at: datetime
```

#### 5.2.5 ServiceRecord（服务记录）

```python
class ServiceRecordCreateRequest(BaseModel):
    customer_id: str
    service_type_id: Optional[str] = None
    product_id: Optional[str] = None
    service_name: Optional[str] = None
    contact_id: Optional[str] = None  # 接单人员
    sales_user_id: Optional[str] = None
    status: str = "pending"
    priority: str = "normal"
    expected_start_date: Optional[date] = None
    expected_completion_date: Optional[date] = None
    estimated_price: Optional[Decimal] = None
    currency_code: str = "CNY"

class ServiceRecordResponse(BaseModel):
    id: str
    customer_id: str
    customer_name: Optional[str]
    service_name: Optional[str]
    service_type_id: Optional[str]
    product_id: Optional[str]
    contact_id: Optional[str]
    contact_name: Optional[str]
    status: str
    priority: str
    estimated_price: Optional[Decimal]
    final_price: Optional[Decimal]
    created_at: datetime
    updated_at: datetime
```
    required_documents: Opti