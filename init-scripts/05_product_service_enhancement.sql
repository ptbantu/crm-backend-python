-- ============================================================
-- 产品/服务管理增强
-- ============================================================
-- 支持多供应商、多货币价格、财务报账等功能
-- 
-- 执行顺序：
-- 1. 先执行 schema_unified.sql 创建基础表
-- 2. 再执行本文件增强产品/服务管理功能
-- ============================================================

-- =====================================
-- 1. 扩展产品分类表 (product_categories)
-- =====================================
-- 注意：MySQL 8.0.19+ 支持 IF NOT EXISTS，为了兼容性，先检查字段是否存在

ALTER TABLE product_categories 
ADD COLUMN IF NOT EXISTS parent_id CHAR(36) COMMENT '父分类ID（支持分类层级）',
ADD COLUMN IF NOT EXISTS description TEXT COMMENT '分类描述',
ADD COLUMN IF NOT EXISTS display_order INT DEFAULT 0 COMMENT '显示顺序',
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活';

-- 先删除可能存在的约束，然后添加外键约束
-- 注意：MySQL 不支持 IF EXISTS 用于约束，使用存储过程处理
-- 如果约束不存在，DROP 会报错，但可以通过存储过程忽略
DELIMITER $$

DROP PROCEDURE IF EXISTS add_product_categories_parent_fk$$
CREATE PROCEDURE add_product_categories_parent_fk()
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    -- 如果约束不存在，忽略错误
  END;
  
  ALTER TABLE product_categories 
  DROP FOREIGN KEY fk_product_categories_parent;
END$$

CALL add_product_categories_parent_fk()$$
DROP PROCEDURE IF EXISTS add_product_categories_parent_fk$$

DELIMITER ;

-- 添加外键约束
ALTER TABLE product_categories 
ADD CONSTRAINT fk_product_categories_parent 
  FOREIGN KEY (parent_id) REFERENCES product_categories(id) ON DELETE SET NULL;

-- 添加索引
CREATE INDEX IF NOT EXISTS ix_product_categories_parent ON product_categories(parent_id);
CREATE INDEX IF NOT EXISTS ix_product_categories_active ON product_categories(is_active);

-- =====================================
-- 2. 扩展产品表 (products) - 移除单一供应商关联，改为多对多
-- =====================================
-- 注意：vendor_id 字段保留用于向后兼容，但新设计使用 vendor_products 表

-- 添加多货币价格字段（分段添加，避免语法错误）
-- 注意：MySQL 8.0+ 支持 IF NOT EXISTS，但为了兼容性，先检查再添加

-- 多货币价格字段
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS price_cost_idr DECIMAL(18,2) COMMENT '成本价（IDR）- 对应 Excel "成本价格"',
ADD COLUMN IF NOT EXISTS price_cost_cny DECIMAL(18,2) COMMENT '成本价（CNY）- 计算得出',
ADD COLUMN IF NOT EXISTS price_channel_idr DECIMAL(18,2) COMMENT '渠道价（IDR）- 对应 Excel "渠道合作价(IDR)"',
ADD COLUMN IF NOT EXISTS price_channel_cny DECIMAL(18,2) COMMENT '渠道价（CNY）- 对应 Excel "渠道合作价(CNY)"',
ADD COLUMN IF NOT EXISTS price_direct_idr DECIMAL(18,2) COMMENT '直客价（IDR）- 对应 Excel "价格(IDR)"',
ADD COLUMN IF NOT EXISTS price_direct_cny DECIMAL(18,2) COMMENT '直客价（CNY）- 对应 Excel "价格(RMB)"',
ADD COLUMN IF NOT EXISTS price_list_idr DECIMAL(18,2) COMMENT '列表价（IDR）',
ADD COLUMN IF NOT EXISTS price_list_cny DECIMAL(18,2) COMMENT '列表价（CNY）';

-- 汇率相关
ALTER TABLE products
ADD COLUMN IF NOT EXISTS default_currency VARCHAR(10) DEFAULT 'IDR' COMMENT '默认货币',
ADD COLUMN IF NOT EXISTS exchange_rate DECIMAL(18,9) DEFAULT 2000 COMMENT '汇率（IDR/CNY），默认 2000';

-- 服务属性（基于 Excel 分析）
ALTER TABLE products
ADD COLUMN IF NOT EXISTS service_type VARCHAR(50) COMMENT '服务类型：visa, company_registration, tax, license, etc.',
ADD COLUMN IF NOT EXISTS service_subtype VARCHAR(50) COMMENT '服务子类型：B1, C211, C212, etc.',
ADD COLUMN IF NOT EXISTS validity_period INT COMMENT '有效期（天数）',
ADD COLUMN IF NOT EXISTS processing_days INT COMMENT '处理天数 - 对应 Excel "办理时长"',
ADD COLUMN IF NOT EXISTS processing_time_text VARCHAR(255) COMMENT '处理时间文本描述（如：3个工作日）',
ADD COLUMN IF NOT EXISTS is_urgent_available BOOLEAN DEFAULT FALSE COMMENT '是否支持加急',
ADD COLUMN IF NOT EXISTS urgent_processing_days INT COMMENT '加急处理天数',
ADD COLUMN IF NOT EXISTS urgent_price_surcharge DECIMAL(18,2) COMMENT '加急附加费';

-- 利润计算（冗余字段，便于查询）- 对应 Excel 利润相关列
ALTER TABLE products
ADD COLUMN IF NOT EXISTS channel_profit DECIMAL(18,2) COMMENT '渠道方利润 = 直客价 - 渠道价',
ADD COLUMN IF NOT EXISTS channel_profit_rate DECIMAL(5,4) COMMENT '渠道方利润率',
ADD COLUMN IF NOT EXISTS channel_customer_profit DECIMAL(18,2) COMMENT '渠道客户利润 = 渠道价 - 成本价',
ADD COLUMN IF NOT EXISTS channel_customer_profit_rate DECIMAL(5,4) COMMENT '渠道客户利润率',
ADD COLUMN IF NOT EXISTS direct_profit DECIMAL(18,2) COMMENT '直客利润 = 直客价 - 成本价',
ADD COLUMN IF NOT EXISTS direct_profit_rate DECIMAL(5,4) COMMENT '直客利润率';

-- 业务属性（基于 Excel 分析）
ALTER TABLE products
ADD COLUMN IF NOT EXISTS commission_rate DECIMAL(5,4) COMMENT '提成比例 - 对应 Excel "提成比例"',
ADD COLUMN IF NOT EXISTS commission_amount DECIMAL(18,2) COMMENT '提成金额 - 对应 Excel "提成金额"',
ADD COLUMN IF NOT EXISTS equivalent_cny DECIMAL(18,2) COMMENT '等值人民币 - 对应 Excel "等值人民币"',
ADD COLUMN IF NOT EXISTS monthly_orders INT COMMENT '每月单数 - 对应 Excel "每月单数"',
ADD COLUMN IF NOT EXISTS total_amount DECIMAL(18,2) COMMENT '合计 - 对应 Excel "合计"';

-- SLA 和服务级别
ALTER TABLE products
ADD COLUMN IF NOT EXISTS sla_description TEXT COMMENT 'SLA 描述 - 对应 Excel "SLA"',
ADD COLUMN IF NOT EXISTS service_level VARCHAR(50) COMMENT '服务级别：standard, premium, vip';

-- 状态管理
ALTER TABLE products
ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'active' COMMENT '状态：active, suspended, discontinued',
ADD COLUMN IF NOT EXISTS suspended_reason TEXT COMMENT '暂停原因',
ADD COLUMN IF NOT EXISTS discontinued_at DATETIME COMMENT '停用时间';

-- 添加索引
CREATE INDEX IF NOT EXISTS ix_products_service_type ON products(service_type);
CREATE INDEX IF NOT EXISTS ix_products_service_subtype ON products(service_subtype);
CREATE INDEX IF NOT EXISTS ix_products_status ON products(status);
CREATE INDEX IF NOT EXISTS ix_products_category_id ON products(category_id);

-- =====================================
-- 3. 供应商服务关联表 (vendor_products) - 多对多关系
-- =====================================
-- 支持：一个服务由多个组织（内部组织或供应商）提供
--      一个组织可以提供多个服务
CREATE TABLE IF NOT EXISTS vendor_products (
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  organization_id         CHAR(36) NOT NULL,          -- 组织ID（可以是 internal 或 vendor）
  product_id              CHAR(36) NOT NULL,          -- 服务/产品ID
  is_primary              BOOLEAN DEFAULT FALSE,      -- 是否主要供应商/组织
  priority                INT DEFAULT 0,               -- 优先级（数字越小优先级越高）
  
  -- 该组织提供该服务的成本价（多货币）
  cost_price_idr          DECIMAL(18,2),              -- 成本价（IDR）
  cost_price_cny          DECIMAL(18,2),              -- 成本价（CNY）
  exchange_rate           DECIMAL(18,9) DEFAULT 2000,  -- 汇率（IDR/CNY）
  
  -- 订购限制
  min_quantity            INT DEFAULT 1,              -- 最小订购量
  max_quantity            INT,                        -- 最大订购量
  lead_time_days          INT,                        -- 交货期（天数）
  processing_days         INT,                        -- 该组织处理该服务的天数
  
  -- 可用性管理
  is_available            BOOLEAN DEFAULT TRUE,      -- 是否可用
  availability_notes      TEXT,                       -- 可用性说明
  available_from          DATETIME,                    -- 可用开始时间
  available_to            DATETIME,                    -- 可用结束时间
  
  -- 财务相关（用于报账）
  account_code            VARCHAR(100),                -- 会计科目代码
  cost_center             VARCHAR(100),                -- 成本中心
  expense_category        VARCHAR(100),                -- 费用类别
  
  -- 元数据
  notes                   TEXT,                        -- 备注
  created_by              CHAR(36),                    -- 创建人
  updated_by              CHAR(36),                    -- 更新人
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
  UNIQUE KEY uk_vendor_product (organization_id, product_id),
  CONSTRAINT chk_vendor_products_prices_nonneg CHECK (
    COALESCE(cost_price_idr,0) >= 0 AND COALESCE(cost_price_cny,0) >= 0
  )
);

CREATE INDEX ix_vendor_products_org ON vendor_products(organization_id);
CREATE INDEX ix_vendor_products_product ON vendor_products(product_id);
CREATE INDEX ix_vendor_products_primary ON vendor_products(product_id, is_primary);
CREATE INDEX ix_vendor_products_available ON vendor_products(is_available, available_from, available_to);
CREATE INDEX ix_vendor_products_priority ON vendor_products(product_id, priority);

-- =====================================
-- 4. 产品价格表 (product_prices) - 支持多价格类型和多货币
-- =====================================
-- 用于管理产品的不同价格类型（成本价、渠道价、直客价等）
-- 每种价格类型都支持多货币（IDR、CNY）
CREATE TABLE IF NOT EXISTS product_prices (
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  product_id              CHAR(36) NOT NULL,          -- 产品ID
  organization_id         CHAR(36),                   -- 组织ID（如果是组织特定价格，NULL表示通用价格）
  price_type              VARCHAR(50) NOT NULL,       -- 价格类型：cost, channel, direct, list
  currency                VARCHAR(10) NOT NULL,        -- 货币：IDR, CNY
  amount                  DECIMAL(18,2) NOT NULL,      -- 价格金额
  exchange_rate           DECIMAL(18,9),              -- 汇率（用于计算）
  
  -- 价格生效时间
  effective_from          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 生效时间
  effective_to            DATETIME,                    -- 失效时间（NULL表示当前有效）
  
  -- 价格来源和审核
  source                  VARCHAR(50),                -- 价格来源：manual, import, contract
  is_approved             BOOLEAN DEFAULT FALSE,      -- 是否已审核
  approved_by             CHAR(36),                    -- 审核人
  approved_at             DATETIME,                    -- 审核时间
  
  -- 变更信息
  change_reason            TEXT,                        -- 变更原因
  changed_by              CHAR(36),                    -- 变更人
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
  FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE SET NULL,
  FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT chk_product_prices_amount_nonneg CHECK (amount >= 0),
  CONSTRAINT chk_product_prices_price_type CHECK (price_type IN ('cost', 'channel', 'direct', 'list')),
  CONSTRAINT chk_product_prices_currency CHECK (currency IN ('IDR', 'CNY', 'USD', 'EUR'))
);

CREATE INDEX ix_product_prices_product ON product_prices(product_id);
CREATE INDEX ix_product_prices_org ON product_prices(organization_id);
CREATE INDEX ix_product_prices_type ON product_prices(price_type);
CREATE INDEX ix_product_prices_currency ON product_prices(currency);
CREATE INDEX ix_product_prices_effective ON product_prices(effective_from, effective_to);
CREATE INDEX ix_product_prices_current ON product_prices(product_id, price_type, currency, effective_from, effective_to);

-- 注意：MySQL 不支持部分唯一索引（WHERE 子句），需要在应用层保证唯一性
-- 或者使用触发器来确保同一产品、同一组织、同一价格类型、同一货币在同一时间只有一个有效价格

-- =====================================
-- 5. 产品价格历史表 (product_price_history) - 审计和趋势分析
-- =====================================
CREATE TABLE IF NOT EXISTS product_price_history (
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  product_id              CHAR(36) NOT NULL,
  organization_id         CHAR(36),                   -- 如果是组织特定价格
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
  FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE SET NULL,
  FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX ix_price_history_product ON product_price_history(product_id);
CREATE INDEX ix_price_history_org ON product_price_history(organization_id);
CREATE INDEX ix_price_history_effective ON product_price_history(effective_from, effective_to);
CREATE INDEX ix_price_history_type ON product_price_history(price_type, currency);

-- =====================================
-- 6. 供应商服务财务记录表 (vendor_product_financials) - 用于报账
-- =====================================
-- 记录供应商提供服务的财务信息，用于财务报账和成本核算
CREATE TABLE IF NOT EXISTS vendor_product_financials (
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  vendor_product_id       CHAR(36) NOT NULL,          -- 供应商服务关联ID
  order_id                CHAR(36),                   -- 关联订单ID（如果有）
  
  -- 财务信息
  cost_amount_idr         DECIMAL(18,2),              -- 成本金额（IDR）
  cost_amount_cny         DECIMAL(18,2),              -- 成本金额（CNY）
  exchange_rate           DECIMAL(18,9),              -- 汇率
  
  -- 会计信息
  account_code            VARCHAR(100),                -- 会计科目代码
  cost_center             VARCHAR(100),                -- 成本中心
  expense_category        VARCHAR(100),                -- 费用类别
  department              VARCHAR(100),                -- 部门
  
  -- 报账信息
  invoice_number          VARCHAR(255),                -- 发票号
  invoice_date            DATE,                        -- 发票日期
  payment_status          VARCHAR(50) DEFAULT 'pending', -- 付款状态：pending, paid, cancelled
  payment_id              CHAR(36),                    -- 关联付款记录ID
  
  -- 审核信息
  is_approved             BOOLEAN DEFAULT FALSE,      -- 是否已审核
  approved_by             CHAR(36),                    -- 审核人
  approved_at             DATETIME,                    -- 审核时间
  approval_notes          TEXT,                        -- 审核备注
  
  -- 元数据
  notes                   TEXT,                        -- 备注
  created_by              CHAR(36),                    -- 创建人
  updated_by              CHAR(36),                    -- 更新人
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  FOREIGN KEY (vendor_product_id) REFERENCES vendor_products(id) ON DELETE CASCADE,
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL,
  FOREIGN KEY (payment_id) REFERENCES payments(id) ON DELETE SET NULL,
  FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT chk_vendor_product_financials_amount_nonneg CHECK (
    COALESCE(cost_amount_idr,0) >= 0 AND COALESCE(cost_amount_cny,0) >= 0
  ),
  CONSTRAINT chk_vendor_product_financials_payment_status CHECK (
    payment_status IN ('pending', 'paid', 'cancelled', 'refunded')
  )
);

CREATE INDEX ix_vendor_product_financials_vendor_product ON vendor_product_financials(vendor_product_id);
CREATE INDEX ix_vendor_product_financials_order ON vendor_product_financials(order_id);
CREATE INDEX ix_vendor_product_financials_payment ON vendor_product_financials(payment_id);
CREATE INDEX ix_vendor_product_financials_payment_status ON vendor_product_financials(payment_status);
CREATE INDEX ix_vendor_product_financials_approved ON vendor_product_financials(is_approved);
CREATE INDEX ix_vendor_product_financials_invoice ON vendor_product_financials(invoice_number);

-- =====================================
-- 7. 更新现有约束和索引
-- =====================================

-- 更新 products 表的约束，支持多货币价格
ALTER TABLE products 
DROP CONSTRAINT IF EXISTS chk_products_prices_nonneg;

ALTER TABLE products 
ADD CONSTRAINT chk_products_prices_nonneg CHECK (
  COALESCE(price_list,0) >= 0 
  AND COALESCE(price_channel,0) >= 0 
  AND COALESCE(price_cost,0) >= 0
  AND COALESCE(price_cost_idr,0) >= 0 
  AND COALESCE(price_cost_cny,0) >= 0
  AND COALESCE(price_channel_idr,0) >= 0 
  AND COALESCE(price_channel_cny,0) >= 0
  AND COALESCE(price_direct_idr,0) >= 0 
  AND COALESCE(price_direct_cny,0) >= 0
  AND COALESCE(price_list_idr,0) >= 0 
  AND COALESCE(price_list_cny,0) >= 0
  AND (exchange_rate IS NULL OR exchange_rate > 0)  -- 允许 NULL，如果不为 NULL 则必须 > 0
  AND COALESCE(processing_days,0) >= 0
  AND COALESCE(validity_period,0) >= 0
  AND COALESCE(urgent_processing_days,0) >= 0
  AND COALESCE(urgent_price_surcharge,0) >= 0
  AND COALESCE(commission_rate,0) >= 0 
  AND COALESCE(commission_rate,0) <= 1
  AND COALESCE(monthly_orders,0) >= 0
);

-- 添加状态约束
ALTER TABLE products
ADD CONSTRAINT chk_products_status CHECK (
  status IN ('active', 'suspended', 'discontinued')
);

-- =====================================
-- 8. 触发器 - 自动更新利润字段
-- =====================================
DELIMITER $$

-- 触发器：当价格更新时，自动计算利润
DROP TRIGGER IF EXISTS products_calculate_profit$$
CREATE TRIGGER products_calculate_profit
BEFORE UPDATE ON products
FOR EACH ROW
BEGIN
  -- 计算渠道方利润（使用默认货币）
  IF NEW.price_direct_idr IS NOT NULL AND NEW.price_channel_idr IS NOT NULL THEN
    SET NEW.channel_profit = NEW.price_direct_idr - NEW.price_channel_idr;
    IF NEW.price_channel_idr > 0 THEN
      SET NEW.channel_profit_rate = NEW.channel_profit / NEW.price_channel_idr;
    END IF;
  END IF;
  
  -- 计算渠道客户利润
  IF NEW.price_channel_idr IS NOT NULL AND NEW.price_cost_idr IS NOT NULL THEN
    SET NEW.channel_customer_profit = NEW.price_channel_idr - NEW.price_cost_idr;
    IF NEW.price_cost_idr > 0 THEN
      SET NEW.channel_customer_profit_rate = NEW.channel_customer_profit / NEW.price_cost_idr;
    END IF;
  END IF;
  
  -- 计算直客利润
  IF NEW.price_direct_idr IS NOT NULL AND NEW.price_cost_idr IS NOT NULL THEN
    SET NEW.direct_profit = NEW.price_direct_idr - NEW.price_cost_idr;
    IF NEW.price_cost_idr > 0 THEN
      SET NEW.direct_profit_rate = NEW.direct_profit / NEW.price_cost_idr;
    END IF;
  END IF;
  
  -- 自动计算 CNY 价格（如果汇率和 IDR 价格存在）
  IF NEW.exchange_rate IS NOT NULL AND NEW.exchange_rate > 0 THEN
    IF NEW.price_cost_idr IS NOT NULL AND NEW.price_cost_cny IS NULL THEN
      SET NEW.price_cost_cny = NEW.price_cost_idr / NEW.exchange_rate;
    END IF;
    IF NEW.price_channel_idr IS NOT NULL AND NEW.price_channel_cny IS NULL THEN
      SET NEW.price_channel_cny = NEW.price_channel_idr / NEW.exchange_rate;
    END IF;
    IF NEW.price_direct_idr IS NOT NULL AND NEW.price_direct_cny IS NULL THEN
      SET NEW.price_direct_cny = NEW.price_direct_idr / NEW.exchange_rate;
    END IF;
  END IF;
END$$

DELIMITER ;

-- =====================================
-- 9. 视图 - 产品服务综合视图
-- =====================================

-- 产品与供应商关联视图
CREATE OR REPLACE VIEW product_vendor_view AS
SELECT 
  p.id as product_id,
  p.name as product_name,
  p.code as product_code,
  p.service_type,
  p.service_subtype,
  p.status as product_status,
  pc.id as category_id,
  pc.code as category_code,
  pc.name as category_name,
  vp.id as vendor_product_id,
  vp.organization_id,
  org.name as organization_name,
  org.organization_type,
  vp.is_primary,
  vp.priority,
  vp.cost_price_idr,
  vp.cost_price_cny,
  vp.is_available,
  vp.processing_days as vendor_processing_days,
  vp.lead_time_days,
  p.price_cost_idr,
  p.price_cost_cny,
  p.price_channel_idr,
  p.price_channel_cny,
  p.price_direct_idr,
  p.price_direct_cny,
  p.processing_days as product_processing_days,
  p.processing_time_text,
  p.created_at as product_created_at,
  vp.created_at as vendor_product_created_at
FROM products p
LEFT JOIN product_categories pc ON pc.id = p.category_id
LEFT JOIN vendor_products vp ON vp.product_id = p.id
LEFT JOIN organizations org ON org.id = vp.organization_id
WHERE p.is_active = TRUE;

-- 产品价格汇总视图
CREATE OR REPLACE VIEW product_price_summary_view AS
SELECT 
  p.id as product_id,
  p.name as product_name,
  p.code as product_code,
  p.service_type,
  p.service_subtype,
  -- 成本价
  p.price_cost_idr,
  p.price_cost_cny,
  -- 渠道价
  p.price_channel_idr,
  p.price_channel_cny,
  -- 直客价
  p.price_direct_idr,
  p.price_direct_cny,
  -- 利润
  p.channel_profit,
  p.channel_profit_rate,
  p.channel_customer_profit,
  p.channel_customer_profit_rate,
  p.direct_profit,
  p.direct_profit_rate,
  -- 汇率
  p.exchange_rate,
  p.default_currency,
  -- 供应商数量
  COUNT(DISTINCT vp.organization_id) as vendor_count,
  -- 主要供应商（使用子查询确保准确性）
  (SELECT org2.name 
   FROM vendor_products vp2 
   JOIN organizations org2 ON org2.id = vp2.organization_id 
   WHERE vp2.product_id = p.id 
     AND vp2.is_primary = TRUE 
     AND vp2.is_available = TRUE
   LIMIT 1) as primary_vendor_name,
  p.status,
  p.is_active,
  p.created_at,
  p.updated_at
FROM products p
LEFT JOIN vendor_products vp ON vp.product_id = p.id AND vp.is_available = TRUE
GROUP BY p.id, p.name, p.code, p.service_type, p.service_subtype,
         p.price_cost_idr, p.price_cost_cny,
         p.price_channel_idr, p.price_channel_cny,
         p.price_direct_idr, p.price_direct_cny,
         p.channel_profit, p.channel_profit_rate,
         p.channel_customer_profit, p.channel_customer_profit_rate,
         p.direct_profit, p.direct_profit_rate,
         p.exchange_rate, p.default_currency,
         p.status, p.is_active, p.created_at, p.updated_at;

-- 供应商服务财务汇总视图
CREATE OR REPLACE VIEW vendor_product_financial_summary_view AS
SELECT 
  vp.id as vendor_product_id,
  vp.organization_id,
  org.name as organization_name,
  org.organization_type,
  vp.product_id,
  p.name as product_name,
  p.code as product_code,
  -- 成本汇总
  SUM(COALESCE(vpf.cost_amount_idr, 0)) as total_cost_idr,
  SUM(COALESCE(vpf.cost_amount_cny, 0)) as total_cost_cny,
  -- 订单数量
  COUNT(DISTINCT vpf.order_id) as order_count,
  -- 付款状态汇总
  SUM(CASE WHEN vpf.payment_status = 'paid' THEN 1 ELSE 0 END) as paid_count,
  SUM(CASE WHEN vpf.payment_status = 'pending' THEN 1 ELSE 0 END) as pending_count,
  SUM(CASE WHEN vpf.payment_status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_count,
  -- 已付款金额
  SUM(CASE WHEN vpf.payment_status = 'paid' THEN COALESCE(vpf.cost_amount_cny, 0) ELSE 0 END) as paid_amount_cny,
  SUM(CASE WHEN vpf.payment_status = 'paid' THEN COALESCE(vpf.cost_amount_idr, 0) ELSE 0 END) as paid_amount_idr,
  -- 待付款金额
  SUM(CASE WHEN vpf.payment_status = 'pending' THEN COALESCE(vpf.cost_amount_cny, 0) ELSE 0 END) as pending_amount_cny,
  SUM(CASE WHEN vpf.payment_status = 'pending' THEN COALESCE(vpf.cost_amount_idr, 0) ELSE 0 END) as pending_amount_idr
FROM vendor_products vp
LEFT JOIN organizations org ON org.id = vp.organization_id
LEFT JOIN products p ON p.id = vp.product_id
LEFT JOIN vendor_product_financials vpf ON vpf.vendor_product_id = vp.id
GROUP BY vp.id, vp.organization_id, org.name, org.organization_type, 
         vp.product_id, p.name, p.code;

-- =====================================
-- 10. 表关系说明
-- =====================================
-- 
-- 核心关系：
-- 1. products (产品/服务) <---> vendor_products (供应商服务关联) <---> organizations (组织)
--    - 多对多关系：一个服务可以由多个组织提供，一个组织可以提供多个服务
--    - organizations.organization_type 可以是 'internal' 或 'vendor'
--
-- 2. products (产品) <---> product_categories (产品分类)
--    - 多对一关系：一个产品属于一个分类，一个分类可以有多个产品
--    - 支持分类层级（parent_id）
--
-- 3. products (产品) <---> product_prices (产品价格)
--    - 一对多关系：一个产品可以有多个价格记录（不同时间、不同组织）
--    - 支持多价格类型（cost, channel, direct, list）
--    - 支持多货币（IDR, CNY, USD, EUR）
--
-- 4. vendor_products (供应商服务关联) <---> vendor_product_financials (财务记录)
--    - 一对多关系：一个供应商服务关联可以有多个财务记录（用于报账）
--    - 关联到 orders (订单) 和 payments (付款)
--
-- 5. products (产品) <---> orders (订单)
--    - 一对多关系：一个产品可以出现在多个订单中
--    - 通过 orders.product_id 关联
--
-- 财务流程：
-- 1. 订单创建 (orders) -> 关联产品 (products) -> 关联供应商服务 (vendor_products)
-- 2. 服务完成后 -> 创建财务记录 (vendor_product_financials)
-- 3. 财务审核 -> 创建付款记录 (payments) -> 更新财务记录状态
--
-- =====================================
-- 11. 索引优化
-- =====================================

-- 复合索引：用于常用查询
CREATE INDEX IF NOT EXISTS ix_products_category_status 
ON products(category_id, status, is_active);

CREATE INDEX IF NOT EXISTS ix_products_service_type_subtype 
ON products(service_type, service_subtype);

CREATE INDEX IF NOT EXISTS ix_vendor_products_org_available 
ON vendor_products(organization_id, is_available, priority);

CREATE INDEX IF NOT EXISTS ix_product_prices_product_type_currency 
ON product_prices(product_id, price_type, currency, effective_from DESC);

-- =====================================
-- 12. 数据完整性约束和触发器
-- =====================================

-- 触发器：确保主要供应商的唯一性（每个产品只能有一个主要供应商）
DELIMITER $$

DROP TRIGGER IF EXISTS vendor_products_ensure_single_primary$$
CREATE TRIGGER vendor_products_ensure_single_primary
BEFORE INSERT ON vendor_products
FOR EACH ROW
BEGIN
  -- 如果设置为主要供应商，将其他供应商的主要标志设为 FALSE
  -- 注意：INSERT 时 NEW.id 可能还未生成，所以不需要检查 id != NEW.id
  IF NEW.is_primary = TRUE THEN
    UPDATE vendor_products 
    SET is_primary = FALSE 
    WHERE product_id = NEW.product_id 
      AND is_primary = TRUE;
  END IF;
END$$

DROP TRIGGER IF EXISTS vendor_products_ensure_single_primary_update$$
CREATE TRIGGER vendor_products_ensure_single_primary_update
BEFORE UPDATE ON vendor_products
FOR EACH ROW
BEGIN
  -- 如果设置为主要供应商，将其他供应商的主要标志设为 FALSE
  IF NEW.is_primary = TRUE AND OLD.is_primary = FALSE THEN
    UPDATE vendor_products 
    SET is_primary = FALSE 
    WHERE product_id = NEW.product_id 
      AND id != NEW.id 
      AND is_primary = TRUE;
  END IF;
END$$

-- 注意：以下触发器用于自动更新 updated_at 字段
-- 由于表定义中已有 ON UPDATE CURRENT_TIMESTAMP，这些触发器是冗余的
-- 如果将来需要在这些表的更新时执行其他逻辑（如日志记录），可以取消注释
-- 
-- DROP TRIGGER IF EXISTS vendor_products_updated_at$$
-- CREATE TRIGGER vendor_products_updated_at
-- BEFORE UPDATE ON vendor_products
-- FOR EACH ROW
-- BEGIN
--   SET NEW.updated_at = NOW();
--   -- 可以在这里添加其他逻辑，如审计日志
-- END$$
--
-- DROP TRIGGER IF EXISTS product_prices_updated_at$$
-- CREATE TRIGGER product_prices_updated_at
-- BEFORE UPDATE ON product_prices
-- FOR EACH ROW
-- BEGIN
--   SET NEW.updated_at = NOW();
--   -- 可以在这里添加其他逻辑，如审计日志
-- END$$
--
-- DROP TRIGGER IF EXISTS vendor_product_financials_updated_at$$
-- CREATE TRIGGER vendor_product_financials_updated_at
-- BEFORE UPDATE ON vendor_product_financials
-- FOR EACH ROW
-- BEGIN
--   SET NEW.updated_at = NOW();
--   -- 可以在这里添加其他逻辑，如审计日志
-- END$$

DELIMITER ;

-- =====================================
-- 13. 业务逻辑说明
-- =====================================
--
-- 数据完整性约束（需要在应用层实现）：
-- 1. 确保每个产品至少有一个供应商/组织（通过应用层验证）
-- 2. 确保主要供应商的唯一性（通过触发器实现）
-- 3. 价格历史记录：当价格更新时，自动创建历史记录（通过应用层实现）
--
-- 财务报账流程：
-- 1. 订单创建 -> 选择产品和供应商 -> 创建 vendor_product_financials 记录
-- 2. 服务完成后 -> 更新财务记录状态为待审核
-- 3. 财务审核 -> 更新 is_approved = TRUE，approved_by, approved_at
-- 4. 创建付款记录 -> 关联到 payments 表，更新 payment_status = 'paid'
--
-- 价格管理：
-- 1. 产品基础价格存储在 products 表（冗余字段，便于快速查询）
-- 2. 详细价格历史存储在 product_prices 表（支持时间序列）
-- 3. 供应商特定成本价存储在 vendor_products 表
-- 4. 价格变更历史存储在 product_price_history 表
--
-- 多对多关系说明：
-- - products <---> vendor_products <---> organizations
-- - 一个服务可以由多个组织（internal 或 vendor）提供
-- - 一个组织可以提供多个服务
-- - 通过 vendor_products.is_primary 标识主要供应商
-- - 通过 vendor_products.priority 设置优先级
--
-- =====================================
-- 完成
-- =====================================