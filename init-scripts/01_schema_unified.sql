-- ============================================================
-- BANTU CRM Database Schema (Unified MySQL Version)
-- ============================================================
-- Complete database schema for BANTU Enterprise Services CRM
-- Unified schema with all tables, constraints, indexes, and triggers
-- 
-- Usage: mysql -u user -p database < sql/schema_unified.sql
-- 
-- Changes:
-- - Users table: username is NOT unique, only email is unique
-- - Users table: Added avatar_url, bio, gender, address, contact_phone, whatsapp, wechat
-- - All field names use snake_case convention
-- ============================================================

-- ============================================================
-- Triggers will be created after all tables are created
-- ============================================================

-- ============================================================
-- 1. Core Tables: Users, Roles, Organizations
-- ============================================================
-- 注意：必须先创建 users 表，因为 organizations 表有外键引用 users

-- =====================================
-- Roles (角色表)
-- =====================================
CREATE TABLE IF NOT EXISTS roles (
  id              CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  code            VARCHAR(50) NOT NULL UNIQUE,
  name            VARCHAR(255) NOT NULL,
  description     TEXT,
  created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Seed core roles
INSERT INTO roles (id, code, name, description)
SELECT UUID(), v.code, v.name, v.description
FROM (
  SELECT 'ADMIN' as code, 'Administrator' as name, 'System administrator with full access' as description
  UNION ALL SELECT 'SALES', 'Sales', 'Internal sales representative'
  UNION ALL SELECT 'AGENT', 'Channel Agent', 'External channel agent sales'
  UNION ALL SELECT 'OPERATION', 'Operation', 'Order processing staff'
  UNION ALL SELECT 'FINANCE', 'Finance', 'Finance staff for AR/AP and reports'
) AS v
WHERE NOT EXISTS (SELECT 1 FROM roles r WHERE r.code = v.code);

-- =====================================
-- Users (用户表) - 系统登录账户
-- =====================================
-- 职责：管理可以登录系统的用户账户信息
-- 注意：每个用户必须至少有一个 organization_employees 记录
CREATE TABLE IF NOT EXISTS users (
  id                CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  username          VARCHAR(255) NOT NULL,                    -- 用户名（用于登录，不唯一）
  email             VARCHAR(255) UNIQUE,                      -- 全局唯一邮箱（用于登录，可空）
  phone             VARCHAR(50),                              -- 手机号（用于登录验证，可空）
  display_name      VARCHAR(255),                             -- 显示名称
  password_hash     VARCHAR(255),                             -- 密码哈希（登录凭证）
  avatar_url        VARCHAR(500),                             -- 头像地址
  bio               TEXT,                                     -- 个人简介
  gender            VARCHAR(10),                              -- 性别：male, female, other
  address           TEXT,                                     -- 住址
  contact_phone     VARCHAR(50),                              -- 联系电话
  whatsapp          VARCHAR(50),                              -- WhatsApp 号码
  wechat            VARCHAR(100),                             -- 微信号
  is_active         BOOLEAN NOT NULL DEFAULT TRUE,          -- 是否激活（控制登录权限）
  last_login_at     DATETIME,                                 -- 最后登录时间
  created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 邮箱用于登录，需要唯一性索引（用户名不唯一）
CREATE UNIQUE INDEX ux_users_email ON users(email);
CREATE INDEX ix_users_username ON users(username);
CREATE INDEX ix_users_phone ON users(phone);
CREATE INDEX ix_users_active ON users(is_active);
CREATE INDEX ix_users_wechat ON users(wechat);

-- =====================================
-- Organizations (统一组织表)
-- =====================================
-- Supports: 'internal' (内部组织), 'vendor' (供应商), 'agent' (渠道代理)
-- 扩展字段：公司规模、性质、类型、领域、国别、logo等
CREATE TABLE IF NOT EXISTS organizations (
  id                 CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  name               TEXT NOT NULL,
  code               VARCHAR(255) UNIQUE,
  external_id        VARCHAR(255) UNIQUE,
  organization_type  VARCHAR(50) NOT NULL,                     -- 'internal' | 'vendor' | 'agent'
  parent_id          CHAR(36),
  
  -- 基本信息
  email              VARCHAR(255),
  phone              VARCHAR(50),
  website            VARCHAR(255),
  logo_url           VARCHAR(500),                              -- 公司logo地址
  description        TEXT,
  
  -- 地址信息
  street             TEXT,
  city               VARCHAR(100),
  state_province      VARCHAR(100),
  postal_code        VARCHAR(20),
  country_region      VARCHAR(100),                             -- 国家/地区（保留兼容）
  country            VARCHAR(100),                              -- 国别（ISO 3166-1 alpha-2 或完整国家名）
  country_code       VARCHAR(10),                              -- 国家代码（如：CN, US, GB）
  
  -- 公司属性
  company_size       VARCHAR(50),                              -- 公司规模：micro, small, medium, large, enterprise
  company_nature     VARCHAR(50),                              -- 公司性质：state_owned, private, foreign, joint_venture, collective, individual
  company_type       VARCHAR(50),                              -- 公司类型：limited, unlimited, partnership, sole_proprietorship, other
  industry           VARCHAR(100),                              -- 行业领域（主行业）
  industry_code      VARCHAR(50),                               -- 行业代码（如：GB/T 4754-2017）
  sub_industry       VARCHAR(100),                              -- 细分行业
  business_scope     TEXT,                                      -- 经营范围
  
  -- 工商信息
  registration_number VARCHAR(100),                            -- 注册号/统一社会信用代码
  tax_id             VARCHAR(100),                             -- 税号/纳税人识别号
  legal_representative VARCHAR(255),                           -- 法定代表人
  established_date   DATE,                                      -- 成立日期
  registered_capital DECIMAL(18,2),                            -- 注册资本（单位：元）
  registered_capital_currency VARCHAR(10) DEFAULT 'CNY',      -- 注册资本币种
  company_status     VARCHAR(50),                             -- 公司状态：normal, cancelled, revoked, liquidated, other
  
  -- 财务信息
  annual_revenue     DECIMAL(18,2),                            -- 年营业额（单位：元）
  annual_revenue_currency VARCHAR(10) DEFAULT 'CNY',          -- 营业额币种
  employee_count     INT,                                       -- 员工数量
  revenue_year       INT,                                       -- 营业额年份
  
  -- 认证信息
  certifications     JSON DEFAULT (JSON_ARRAY()),              -- 认证信息（如：ISO9001, ISO14001等）
  business_license_url VARCHAR(500),                            -- 营业执照URL
  tax_certificate_url VARCHAR(500),                            -- 税务登记证URL
  
  -- 状态控制
  is_active          BOOLEAN NOT NULL DEFAULT TRUE,
  is_locked          BOOLEAN,
  is_verified        BOOLEAN DEFAULT FALSE,                    -- 是否已认证/审核
  verified_at        DATETIME,                                  -- 认证时间
  verified_by        CHAR(36),                                 -- 认证人
  
  -- 外部系统关联
  owner_id_external  VARCHAR(255),
  owner_name         VARCHAR(255),
  created_by_external VARCHAR(255),
  created_by_name    VARCHAR(255),
  updated_by_external VARCHAR(255),
  updated_by_name    VARCHAR(255),
  created_at_src     DATETIME,
  updated_at_src      DATETIME,
  last_action_at_src  DATETIME,
  linked_module       VARCHAR(100),
  linked_id_external  VARCHAR(255),
  tags                JSON DEFAULT (JSON_ARRAY()),
  
  -- 营销相关
  do_not_email       BOOLEAN,
  unsubscribe_method VARCHAR(50),
  unsubscribe_date_src TEXT,
  
  -- 审计字段
  created_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  FOREIGN KEY (parent_id) REFERENCES organizations(id) ON DELETE SET NULL,
  FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT chk_organizations_type CHECK (organization_type IN ('internal', 'vendor', 'agent')),
  CONSTRAINT chk_organizations_size CHECK (company_size IS NULL OR company_size IN ('micro', 'small', 'medium', 'large', 'enterprise')),
  CONSTRAINT chk_organizations_nature CHECK (company_nature IS NULL OR company_nature IN ('state_owned', 'private', 'foreign', 'joint_venture', 'collective', 'individual', 'other')),
  CONSTRAINT chk_organizations_company_type CHECK (company_type IS NULL OR company_type IN ('limited', 'unlimited', 'partnership', 'sole_proprietorship', 'other')),
  CONSTRAINT chk_organizations_status CHECK (company_status IS NULL OR company_status IN ('normal', 'cancelled', 'revoked', 'liquidated', 'other')),
  CONSTRAINT chk_organizations_capital_nonneg CHECK (COALESCE(registered_capital, 0) >= 0),
  CONSTRAINT chk_organizations_revenue_nonneg CHECK (COALESCE(annual_revenue, 0) >= 0),
  CONSTRAINT chk_organizations_employee_nonneg CHECK (COALESCE(employee_count, 0) >= 0)
);

-- 基础索引
CREATE INDEX ix_organizations_code ON organizations(code);
CREATE INDEX ix_organizations_type ON organizations(organization_type);
CREATE INDEX ix_organizations_type_active ON organizations(organization_type, is_active);
CREATE INDEX ix_organizations_email ON organizations(email);
CREATE INDEX ix_organizations_phone ON organizations(phone);
CREATE INDEX ix_organizations_parent ON organizations(parent_id);

-- 新增字段索引
CREATE INDEX ix_organizations_country ON organizations(country);
CREATE INDEX ix_organizations_country_code ON organizations(country_code);
CREATE INDEX ix_organizations_size ON organizations(company_size);
CREATE INDEX ix_organizations_nature ON organizations(company_nature);
CREATE INDEX ix_organizations_industry ON organizations(industry);
CREATE INDEX ix_organizations_registration ON organizations(registration_number);
CREATE INDEX ix_organizations_tax_id ON organizations(tax_id);
CREATE INDEX ix_organizations_status ON organizations(company_status);
CREATE INDEX ix_organizations_verified ON organizations(is_verified);
CREATE INDEX ix_organizations_employee_count ON organizations(employee_count);

-- =====================================
-- Vendor Extensions (供应商扩展表)
-- =====================================
CREATE TABLE IF NOT EXISTS vendor_extensions (
  organization_id    CHAR(36) PRIMARY KEY,
  account_group      VARCHAR(255),
  category_name      VARCHAR(255),
  created_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
);

-- =====================================
-- Agent Extensions (渠道代理扩展表)
-- =====================================
CREATE TABLE IF NOT EXISTS agent_extensions (
  organization_id    CHAR(36) PRIMARY KEY,
  account_group      VARCHAR(255),
  category_name      VARCHAR(255),
  created_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
);

-- =====================================
-- User Roles (用户角色关联表)
-- =====================================
CREATE TABLE IF NOT EXISTS user_roles (
  user_id   CHAR(36) NOT NULL,
  role_id   CHAR(36) NOT NULL,
  PRIMARY KEY (user_id, role_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

-- =====================================
-- Organization Employees (组织员工表) - 用户表的扩展
-- =====================================
-- 职责：作为用户表的扩展，记录用户在组织中的详细信息
-- 约束：每个用户必须至少有一个 organization_employees 记录（业务逻辑约束）
-- 注意：所有组织成员信息（职位、部门、联系方式等）都在此表中
CREATE TABLE IF NOT EXISTS organization_employees (
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  user_id                 CHAR(36) NOT NULL,                  -- 必须关联用户（每个成员必须是组织成员）
  organization_id         CHAR(36) NOT NULL,                  -- 所属组织
  first_name              VARCHAR(255),                     -- 名字（可选，可从 users.display_name 派生）
  last_name               VARCHAR(255),                     -- 姓氏（可选）
  full_name               VARCHAR(510) GENERATED ALWAYS AS (CONCAT(IFNULL(first_name, ''), ' ', IFNULL(last_name, ''))) STORED,
  email                   VARCHAR(255),                     -- 工作邮箱（可与 users.email 不同）
  phone                   VARCHAR(50),                      -- 工作电话（可与 users.phone 不同）
  position                VARCHAR(255),                     -- 职位
  department              VARCHAR(255),                    -- 部门
  employee_number         VARCHAR(100),                    -- 工号
  is_primary              BOOLEAN DEFAULT FALSE,           -- 是否用户的主要组织
  is_manager              BOOLEAN DEFAULT FALSE,           -- 是否管理者
  is_decision_maker       BOOLEAN DEFAULT FALSE,           -- 是否决策人（vendor/agent）
  is_active               BOOLEAN NOT NULL DEFAULT TRUE,  -- 是否在职
  joined_at               DATE,                            -- 入职日期
  left_at                 DATE,                            -- 离职日期
  id_external             VARCHAR(255),                    -- 外部系统ID
  external_user_id        VARCHAR(255),                    -- 外部用户ID
  notes                   TEXT,                             -- 备注
  created_by              CHAR(36),                        -- 创建人
  updated_by              CHAR(36),                       -- 更新人
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,  -- 删除用户时级联删除员工记录
  FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
);

-- 索引：组织查询
CREATE INDEX ix_organization_employees_org ON organization_employees(organization_id);
CREATE INDEX ix_organization_employees_org_active ON organization_employees(organization_id, is_active);

-- 索引：用户查询
CREATE INDEX ix_organization_employees_user ON organization_employees(user_id);
CREATE INDEX ix_organization_employees_user_active ON organization_employees(user_id, is_active);

-- 索引：主要组织查询
CREATE INDEX ix_organization_employees_primary ON organization_employees(user_id, is_primary, is_active);

-- 索引：联系方式查询
CREATE INDEX ix_organization_employees_email ON organization_employees(email);
CREATE INDEX ix_organization_employees_phone ON organization_employees(phone);

-- 唯一约束：每个用户只能有一个主要组织（通过应用层或触发器保证，MySQL 不支持部分唯一索引）
-- 注意：需要在应用层或触发器中确保 is_primary=TRUE AND is_active=TRUE 时，每个用户只有一条记录

-- 唯一约束：同一用户在同一组织只能有一条激活的员工记录（通过应用层保证）
-- 注意：需要在应用层确保 is_active=TRUE 时，同一用户在同一组织只有一条记录

-- ============================================================
-- 2. Product Domain
-- ============================================================

-- =====================================
-- Product Categories (产品分类表)
-- =====================================
CREATE TABLE IF NOT EXISTS product_categories (
  id                 CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  code               VARCHAR(100) NOT NULL UNIQUE,
  name               VARCHAR(255),
  created_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =====================================
-- Products (产品表)
-- =====================================
CREATE TABLE IF NOT EXISTS products (
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  id_external             VARCHAR(255) UNIQUE,
  owner_id_external       VARCHAR(255),
  owner_name              VARCHAR(255),
  created_by_external     VARCHAR(255),
  created_by_name         VARCHAR(255),
  updated_by_external     VARCHAR(255),
  updated_by_name         VARCHAR(255),
  created_at_src          DATETIME,
  updated_at_src          DATETIME,
  last_action_at_src      DATETIME,
  linked_module           VARCHAR(100),
  linked_id_external      VARCHAR(255),
  name                    VARCHAR(255) NOT NULL,
  code                    VARCHAR(100),
  vendor_id               CHAR(36),
  vendor_id_external      VARCHAR(255),
  vendor_name             VARCHAR(255),
  is_active               BOOLEAN NOT NULL DEFAULT TRUE,
  category_code           VARCHAR(100),
  unit                    VARCHAR(50),
  is_taxable              BOOLEAN,
  tax_rate                DECIMAL(5,2),
  tax_code                VARCHAR(50),
  price_list              DECIMAL(18,2),
  price_channel           DECIMAL(18,2),
  price_cost              DECIMAL(18,2),
  tags                    JSON DEFAULT (JSON_ARRAY()),
  is_locked               BOOLEAN,
  notes                   TEXT,
  required_documents      TEXT,
  processing_time         VARCHAR(255),
  category_id             CHAR(36),
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (vendor_id) REFERENCES organizations(id) ON DELETE SET NULL,
  FOREIGN KEY (category_id) REFERENCES product_categories(id) ON DELETE SET NULL,
  CONSTRAINT chk_products_prices_nonneg CHECK (
    COALESCE(price_list,0) >= 0 AND COALESCE(price_channel,0) >= 0 AND COALESCE(price_cost,0) >= 0
  )
);

CREATE UNIQUE INDEX ux_products_code ON products(code);
CREATE INDEX ix_products_active ON products(is_active);

-- ============================================================
-- 3. Customer Domain
-- ============================================================

-- =====================================
-- Customer Sources (客户来源表)
-- =====================================
CREATE TABLE IF NOT EXISTS customer_sources (
  id            CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  code          VARCHAR(100) UNIQUE,
  name          VARCHAR(255) NOT NULL,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =====================================
-- Customer Channels (客户渠道表)
-- =====================================
CREATE TABLE IF NOT EXISTS customer_channels (
  id            CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  code          VARCHAR(100) UNIQUE,
  name          VARCHAR(255) NOT NULL,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =====================================
-- Customers (客户表)
-- =====================================
CREATE TABLE IF NOT EXISTS customers (
  id                        CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  id_external               VARCHAR(255) UNIQUE,
  owner_id_external         VARCHAR(255),
  owner_name                VARCHAR(255),
  created_by_external       VARCHAR(255),
  created_by_name           VARCHAR(255),
  updated_by_external       VARCHAR(255),
  updated_by_name           VARCHAR(255),
  created_at_src            DATETIME,
  updated_at_src            DATETIME,
  last_action_at_src        DATETIME,
  change_log_at_src         DATETIME,
  linked_module             VARCHAR(100),
  linked_id_external        VARCHAR(255),
  name                      VARCHAR(255) NOT NULL,
  code                      VARCHAR(100),
  level                     VARCHAR(50),
  parent_id_external       VARCHAR(255),
  parent_customer_id        CHAR(36),
  parent_name               VARCHAR(255),
  industry                  VARCHAR(255),
  description               TEXT,
  tags                      JSON DEFAULT (JSON_ARRAY()),
  is_locked                 BOOLEAN,
  last_enriched_at_src      DATETIME,
  enrich_status             VARCHAR(50),
  channel_name              VARCHAR(255),
  source_name               VARCHAR(255),
  customer_requirements     TEXT,
  source_id                 CHAR(36),
  channel_id                CHAR(36),
  customer_source_type      VARCHAR(50) DEFAULT 'own',
  customer_type             VARCHAR(50) DEFAULT 'individual',
  owner_user_id             CHAR(36),
  agent_user_id             CHAR(36),
  agent_id                  CHAR(36),
  created_at                DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at                DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (parent_customer_id) REFERENCES customers(id) ON DELETE SET NULL,
  FOREIGN KEY (source_id) REFERENCES customer_sources(id) ON DELETE SET NULL,
  FOREIGN KEY (channel_id) REFERENCES customer_channels(id) ON DELETE SET NULL,
  FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (agent_user_id) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (agent_id) REFERENCES organizations(id) ON DELETE SET NULL,
  CONSTRAINT chk_customer_source_type CHECK (customer_source_type IN ('own', 'agent')),
  CONSTRAINT chk_customer_type CHECK (customer_type IN ('individual', 'organization'))
);

CREATE UNIQUE INDEX ux_customers_code ON customers(code);
CREATE INDEX ix_customers_source_type ON customers(customer_source_type);
CREATE INDEX ix_customers_customer_type ON customers(customer_type);
CREATE INDEX ix_customers_owner ON customers(owner_user_id);
CREATE INDEX ix_customers_agent ON customers(agent_user_id);
CREATE INDEX ix_customers_agent_id ON customers(agent_id);
CREATE INDEX ix_customers_parent ON customers(parent_customer_id);
CREATE INDEX ix_customers_source ON customers(customer_source_type);

-- =====================================
-- Contacts (联系人表)
-- =====================================
CREATE TABLE IF NOT EXISTS contacts (
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  customer_id             CHAR(36) NOT NULL,
  first_name              VARCHAR(255) NOT NULL,
  last_name               VARCHAR(255) NOT NULL,
  full_name               VARCHAR(510) GENERATED ALWAYS AS (CONCAT(first_name, ' ', last_name)) STORED,
  email                   VARCHAR(255),
  phone                   VARCHAR(50),
  mobile                  VARCHAR(50),
  position                VARCHAR(255),
  department              VARCHAR(255),
  is_primary              BOOLEAN DEFAULT FALSE,
  is_decision_maker        BOOLEAN DEFAULT FALSE,
  contact_role            VARCHAR(100),
  address                 TEXT,
  city                    VARCHAR(100),
  province                VARCHAR(100),
  country                 VARCHAR(100),
  postal_code             VARCHAR(20),
  preferred_contact_method VARCHAR(50),
  wechat_id               VARCHAR(100),
  notes                   TEXT,
  is_active               BOOLEAN DEFAULT TRUE,
  created_by              CHAR(36),
  updated_by              CHAR(36),
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX ix_contacts_customer ON contacts(customer_id);
CREATE INDEX ix_contacts_email ON contacts(email);
CREATE INDEX ix_contacts_phone ON contacts(phone);
CREATE INDEX ix_contacts_primary ON contacts(customer_id, is_primary);

CREATE UNIQUE INDEX ux_contacts_one_primary_per_customer 
  ON contacts(customer_id, is_primary);

-- =====================================
-- Visa Records (签证记录表)
-- =====================================
CREATE TABLE IF NOT EXISTS visa_records (
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  id_external             VARCHAR(255) UNIQUE,
  owner_id_external       VARCHAR(255),
  owner_name              VARCHAR(255),
  created_by_external     VARCHAR(255),
  created_by_name         VARCHAR(255),
  updated_by_external     VARCHAR(255),
  updated_by_name         VARCHAR(255),
  created_at_src          DATETIME,
  updated_at_src          DATETIME,
  last_action_at_src      DATETIME,
  linked_module           VARCHAR(100),
  linked_id_external      VARCHAR(255),
  customer_name           VARCHAR(255) NOT NULL,
  customer_id             CHAR(36),
  passport_id             VARCHAR(100),
  entry_city              VARCHAR(100),
  currency_code           VARCHAR(10),
  fx_rate                 DECIMAL(18,9),
  payment_amount          DECIMAL(18,2),
  cancel_method           VARCHAR(50),
  cancel_date_src          TEXT,
  is_locked               BOOLEAN,
  tags                    JSON,
  processor_name          VARCHAR(255),
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
  CONSTRAINT chk_visa_fx_rate_nonneg CHECK (COALESCE(fx_rate,0) >= 0),
  CONSTRAINT chk_visa_payment_nonneg CHECK (COALESCE(payment_amount,0) >= 0)
);

-- ============================================================
-- 4. Order Domain
-- ============================================================

-- =====================================
-- Order Statuses (订单状态表)
-- =====================================
CREATE TABLE IF NOT EXISTS order_statuses (
  id            CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  code          VARCHAR(50) NOT NULL UNIQUE,
  name          VARCHAR(255) NOT NULL,
  description   TEXT,
  display_order INT,
  is_active     BOOLEAN NOT NULL DEFAULT TRUE,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Seed order statuses
INSERT INTO order_statuses (id, code, name, description, display_order)
SELECT UUID(), v.code, v.name, v.description, v.display_order
FROM (
  SELECT 'draft' as code, '草稿' as name, '订单草稿，未提交' as description, 1 as display_order
  UNION ALL SELECT 'submitted', '已提交', '订单已提交，待接单', 2
  UNION ALL SELECT 'assigned', '已分配', '已分配给做单人员', 3
  UNION ALL SELECT 'in_progress', '进行中', '做单进行中', 4
  UNION ALL SELECT 'pending_review', '待审核', '待审核交付物', 5
  UNION ALL SELECT 'completed', '已完成', '订单已完成', 6
  UNION ALL SELECT 'cancelled', '已取消', '订单已取消', 7
  UNION ALL SELECT 'on_hold', '暂停', '订单暂停', 8
) AS v
WHERE NOT EXISTS (SELECT 1 FROM order_statuses os WHERE os.code = v.code);

-- =====================================
-- Orders (订单表)
-- =====================================
CREATE TABLE IF NOT EXISTS orders (
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  order_number            VARCHAR(100) NOT NULL,
  title                   VARCHAR(255) NOT NULL,
  customer_id             CHAR(36) NOT NULL,
  product_id              CHAR(36),
  product_name            VARCHAR(255),
  sales_user_id           CHAR(36) NOT NULL,
  sales_username          VARCHAR(255),
  quantity                INT DEFAULT 1,
  unit_price              DECIMAL(18,2),
  total_amount            DECIMAL(18,2),
  currency_code           VARCHAR(10) DEFAULT 'CNY',
  discount_amount         DECIMAL(18,2) DEFAULT 0,
  final_amount            DECIMAL(18,2),
  status_id               CHAR(36),
  status_code             VARCHAR(50),
  expected_start_date     DATE,
  expected_completion_date DATE,
  actual_start_date       DATE,
  actual_completion_date  DATE,
  customer_notes          TEXT,
  internal_notes          TEXT,
  requirements            TEXT,
  created_by              CHAR(36),
  updated_by              CHAR(36),
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL,
  FOREIGN KEY (sales_user_id) REFERENCES users(id) ON DELETE RESTRICT,
  FOREIGN KEY (status_id) REFERENCES order_statuses(id) ON DELETE SET NULL,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT chk_orders_amounts_nonneg CHECK (
    COALESCE(quantity, 0) >= 0 
    AND COALESCE(unit_price, 0) >= 0 
    AND COALESCE(total_amount, 0) >= 0 
    AND COALESCE(discount_amount, 0) >= 0 
    AND COALESCE(final_amount, 0) >= 0
  )
);

CREATE UNIQUE INDEX ux_orders_number ON orders(order_number);
CREATE INDEX ix_orders_customer ON orders(customer_id);
CREATE INDEX ix_orders_product ON orders(product_id);
CREATE INDEX ix_orders_sales ON orders(sales_user_id);
CREATE INDEX ix_orders_status ON orders(status_code);
CREATE INDEX ix_orders_status_id ON orders(status_id);
CREATE INDEX ix_orders_created ON orders(created_at DESC);

-- =====================================
-- Order Assignments (订单分配表)
-- =====================================
CREATE TABLE IF NOT EXISTS order_assignments (
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  order_id                CHAR(36) NOT NULL,
  assigned_to_user_id     CHAR(36) NOT NULL,
  assigned_by_user_id     CHAR(36),
  assignment_type         VARCHAR(50) DEFAULT 'operation',
  is_primary              BOOLEAN DEFAULT TRUE,
  vendor_id               CHAR(36),
  organization_employee_id CHAR(36),
  vendor_employee_id       CHAR(36),
  assigned_at             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  unassigned_at           DATETIME,
  notes                   TEXT,
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (assigned_to_user_id) REFERENCES users(id) ON DELETE RESTRICT,
  FOREIGN KEY (assigned_by_user_id) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (vendor_id) REFERENCES organizations(id) ON DELETE SET NULL,
  FOREIGN KEY (organization_employee_id) REFERENCES organization_employees(id) ON DELETE SET NULL,
  FOREIGN KEY (vendor_employee_id) REFERENCES organization_employees(id) ON DELETE SET NULL
);

CREATE INDEX ix_order_assignments_order ON order_assignments(order_id);
CREATE INDEX ix_order_assignments_user ON order_assignments(assigned_to_user_id);
CREATE INDEX ix_order_assignments_active ON order_assignments(order_id, assigned_to_user_id);
CREATE INDEX ix_order_assignments_org_employee ON order_assignments(organization_employee_id);

-- =====================================
-- Order Stages (订单阶段表)
-- =====================================
CREATE TABLE IF NOT EXISTS order_stages (
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  order_id                CHAR(36) NOT NULL,
  stage_name              VARCHAR(255) NOT NULL,
  stage_code              VARCHAR(100),
  stage_order             INT NOT NULL,
  status                  VARCHAR(50) DEFAULT 'pending',
  started_at              DATETIME,
  completed_at            DATETIME,
  progress_percent        INT DEFAULT 0,
  notes                   TEXT,
  assigned_to_user_id     CHAR(36),
  created_by              CHAR(36),
  updated_by              CHAR(36),
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (assigned_to_user_id) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT chk_order_stages_progress_range CHECK (progress_percent >= 0 AND progress_percent <= 100)
);

CREATE INDEX ix_order_stages_order ON order_stages(order_id);
CREATE INDEX ix_order_stages_assigned ON order_stages(assigned_to_user_id);
CREATE INDEX ix_order_stages_status ON order_stages(status);

-- =====================================
-- Deliverables (交付物表)
-- =====================================
CREATE TABLE IF NOT EXISTS deliverables (
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  order_id                CHAR(36),
  order_stage_id          CHAR(36),
  deliverable_type        VARCHAR(100) NOT NULL,
  name                    VARCHAR(255) NOT NULL,
  description             TEXT,
  file_path               TEXT,
  file_url                TEXT,
  file_size               BIGINT,
  mime_type               VARCHAR(100),
  is_verified             BOOLEAN DEFAULT FALSE,
  verified_by             CHAR(36),
  verified_at             DATETIME,
  uploaded_by             CHAR(36),
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (order_stage_id) REFERENCES order_stages(id) ON DELETE SET NULL,
  FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT chk_deliverables_file_size_nonneg CHECK (COALESCE(file_size, 0) >= 0)
);

CREATE INDEX ix_deliverables_order ON deliverables(order_id);
CREATE INDEX ix_deliverables_stage ON deliverables(order_stage_id);
CREATE INDEX ix_deliverables_uploaded ON deliverables(uploaded_by);

-- =====================================
-- Payments (收款记录表)
-- =====================================
CREATE TABLE IF NOT EXISTS payments (
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  order_id                CHAR(36) NOT NULL,
  payment_type            VARCHAR(50) NOT NULL,
  amount                  DECIMAL(18,2) NOT NULL,
  currency_code           VARCHAR(10) DEFAULT 'CNY',
  payment_method          VARCHAR(50),
  payment_date            DATE,
  received_at             DATETIME,
  transaction_id          VARCHAR(255),
  bank_account            VARCHAR(255),
  payer_name              VARCHAR(255),
  payer_account           VARCHAR(255),
  status                  VARCHAR(50) DEFAULT 'pending',
  confirmed_by            CHAR(36),
  confirmed_at            DATETIME,
  notes                   TEXT,
  created_by              CHAR(36),
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE RESTRICT,
  FOREIGN KEY (confirmed_by) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX ix_payments_order ON payments(order_id);
CREATE INDEX ix_payments_status ON payments(status);
CREATE INDEX ix_payments_date ON payments(payment_date DESC);

-- ============================================================
-- Triggers (created after all tables)
-- ============================================================

DELIMITER $$

DROP TRIGGER IF EXISTS organizations_updated_at$$
CREATE TRIGGER organizations_updated_at
BEFORE UPDATE ON organizations
FOR EACH ROW
BEGIN
  SET NEW.updated_at = NOW();
END$$

DROP TRIGGER IF EXISTS vendor_extensions_updated_at$$
CREATE TRIGGER vendor_extensions_updated_at
BEFORE UPDATE ON vendor_extensions
FOR EACH ROW
BEGIN
  SET NEW.updated_at = NOW();
END$$

DROP TRIGGER IF EXISTS agent_extensions_updated_at$$
CREATE TRIGGER agent_extensions_updated_at
BEFORE UPDATE ON agent_extensions
FOR EACH ROW
BEGIN
  SET NEW.updated_at = NOW();
END$$

DROP TRIGGER IF EXISTS users_updated_at$$
CREATE TRIGGER users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
  SET NEW.updated_at = NOW();
END$$

DROP TRIGGER IF EXISTS roles_updated_at$$
CREATE TRIGGER roles_updated_at
BEFORE UPDATE ON roles
FOR EACH ROW
BEGIN
  SET NEW.updated_at = NOW();
END$$

DROP TRIGGER IF EXISTS organization_employees_updated_at$$
CREATE TRIGGER organization_employees_updated_at
BEFORE UPDATE ON organization_employees
FOR EACH ROW
BEGIN
  SET NEW.updated_at = NOW();
END$$

DROP TRIGGER IF EXISTS products_updated_at$$
CREATE TRIGGER products_updated_at
BEFORE UPDATE ON products
FOR EACH ROW
BEGIN
  SET NEW.updated_at = NOW();
END$$

DROP TRIGGER IF EXISTS product_categories_updated_at$$
CREATE TRIGGER product_categories_updated_at
BEFORE UPDATE ON product_categories
FOR EACH ROW
BEGIN
  SET NEW.updated_at = NOW();
END$$

DROP TRIGGER IF EXISTS customers_updated_at$$
CREATE TRIGGER customers_updated_at
BEFORE UPDATE ON customers
FOR EACH ROW
BEGIN
  SET NEW.updated_at = NOW();
END$$

DROP TRIGGER IF EXISTS customer_sources_updated_at$$
CREATE TRIGGER customer_sources_updated_at
BEFORE UPDATE ON customer_sources
FOR EACH ROW
BEGIN
  SET NEW.updated_at = NOW();
END$$

DROP TRIGGER IF EXISTS customer_channels_updated_at$$
CREATE TRIGGER customer_channels_updated_at
BEFORE UPDATE ON customer_channels
FOR EACH ROW
BEGIN
  SET NEW.updated_at = NOW();
END$$

DROP TRIGGER IF EXISTS contacts_updated_at$$
CREATE TRIGGER contacts_updated_at
BEFORE UPDATE ON contacts
FOR EACH ROW
BEGIN
  SET NEW.updated_at = NOW();
END$$

DROP TRIGGER IF EXISTS visa_records_updated_at$$
CREATE TRIGGER visa_records_updated_at
BEFORE UPDATE ON visa_records
FOR EACH ROW
BEGIN
  SET NEW.updated_at = NOW();
END$$

DROP TRIGGER IF EXISTS orders_updated_at$$
CREATE TRIGGER orders_updated_at
BEFORE UPDATE ON orders
FOR EACH ROW
BEGIN
  SET NEW.updated_at = NOW();
END$$

DROP TRIGGER IF EXISTS order_statuses_updated_at$$
CREATE TRIGGER order_statuses_updated_at
BEFORE UPDATE ON order_statuses
FOR EACH ROW
BEGIN
  SET NEW.updated_at = NOW();
END$$

DROP TRIGGER IF EXISTS order_stages_updated_at$$
CREATE TRIGGER order_stages_updated_at
BEFORE UPDATE ON order_stages
FOR EACH ROW
BEGIN
  SET NEW.updated_at = NOW();
END$$

DROP TRIGGER IF EXISTS deliverables_updated_at$$
CREATE TRIGGER deliverables_updated_at
BEFORE UPDATE ON deliverables
FOR EACH ROW
BEGIN
  SET NEW.updated_at = NOW();
END$$

DROP TRIGGER IF EXISTS payments_updated_at$$
CREATE TRIGGER payments_updated_at
BEFORE UPDATE ON payments
FOR EACH ROW
BEGIN
  SET NEW.updated_at = NOW();
END$$

DELIMITER ;

-- ============================================================
-- Views
-- ============================================================

-- Customer with owner/agent info
CREATE OR REPLACE VIEW customer_ownership_view AS
SELECT 
  c.id,
  c.name,
  c.code,
  c.customer_source_type,
  c.customer_type,
  c.owner_user_id,
  owner.display_name as owner_name,
  owner.username as owner_username,
  c.agent_user_id,
  agent.display_name as agent_name,
  agent.username as agent_username,
  c.agent_id,
  agent_org.name as agent_organization_name,
  agent_org.code as agent_organization_code,
  c.parent_customer_id,
  parent.name as parent_customer_name,
  c.created_at
FROM customers c
LEFT JOIN users owner ON owner.id = c.owner_user_id
LEFT JOIN users agent ON agent.id = c.agent_user_id
LEFT JOIN organizations agent_org ON agent_org.id = c.agent_id
LEFT JOIN customers parent ON parent.id = c.parent_customer_id;

-- Organization with contacts count
CREATE OR REPLACE VIEW organization_contacts_view AS
SELECT 
  c.id as customer_id,
  c.name as organization_name,
  c.customer_source_type,
  c.owner_user_id,
  c.agent_user_id,
  c.agent_id,
  COUNT(ct.id) as contacts_count,
  SUM(CASE WHEN ct.is_primary = TRUE THEN 1 ELSE 0 END) as primary_contacts_count
FROM customers c
LEFT JOIN contacts ct ON ct.customer_id = c.id AND ct.is_active = TRUE
WHERE c.customer_type = 'organization'
GROUP BY c.id, c.name, c.customer_source_type, c.owner_user_id, c.agent_user_id, c.agent_id;

-- ============================================================
-- Schema Complete
-- ============================================================

