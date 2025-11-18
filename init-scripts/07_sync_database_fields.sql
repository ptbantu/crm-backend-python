-- ============================================================
-- 同步数据库字段脚本
-- ============================================================
-- 确保 products 表包含所有新增字段
-- 
-- 执行顺序：
-- 1. 先执行 01_schema_unified.sql 创建基础表
-- 2. 执行本文件同步所有字段
-- 3. 执行 06_products_seed_data.sql 导入数据
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- ============================================================
-- 1. 扩展产品分类表 (product_categories)
-- ============================================================

ALTER TABLE product_categories 
ADD COLUMN IF NOT EXISTS parent_id CHAR(36) COMMENT '父分类ID（支持分类层级）',
ADD COLUMN IF NOT EXISTS description TEXT COMMENT '分类描述',
ADD COLUMN IF NOT EXISTS display_order INT DEFAULT 0 COMMENT '显示顺序',
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活';

-- 添加索引
CREATE INDEX IF NOT EXISTS ix_product_categories_parent ON product_categories(parent_id);
CREATE INDEX IF NOT EXISTS ix_product_categories_active ON product_categories(is_active);

-- ============================================================
-- 2. 确保执行了 05_product_service_enhancement.sql 的所有字段
-- ============================================================

-- 多货币价格字段
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS price_cost_idr DECIMAL(18,2) COMMENT '成本价（IDR）',
ADD COLUMN IF NOT EXISTS price_cost_cny DECIMAL(18,2) COMMENT '成本价（CNY）',
ADD COLUMN IF NOT EXISTS price_channel_idr DECIMAL(18,2) COMMENT '渠道价（IDR）',
ADD COLUMN IF NOT EXISTS price_channel_cny DECIMAL(18,2) COMMENT '渠道价（CNY）',
ADD COLUMN IF NOT EXISTS price_direct_idr DECIMAL(18,2) COMMENT '直客价（IDR）',
ADD COLUMN IF NOT EXISTS price_direct_cny DECIMAL(18,2) COMMENT '直客价（CNY）',
ADD COLUMN IF NOT EXISTS price_list_idr DECIMAL(18,2) COMMENT '列表价（IDR）',
ADD COLUMN IF NOT EXISTS price_list_cny DECIMAL(18,2) COMMENT '列表价（CNY）';

-- 汇率相关
ALTER TABLE products
ADD COLUMN IF NOT EXISTS default_currency VARCHAR(10) DEFAULT 'IDR' COMMENT '默认货币',
ADD COLUMN IF NOT EXISTS exchange_rate DECIMAL(18,9) DEFAULT 2000 COMMENT '汇率（IDR/CNY）';

-- 服务属性
ALTER TABLE products
ADD COLUMN IF NOT EXISTS service_type VARCHAR(50) COMMENT '服务类型',
ADD COLUMN IF NOT EXISTS service_subtype VARCHAR(50) COMMENT '服务子类型',
ADD COLUMN IF NOT EXISTS validity_period INT COMMENT '有效期（天数）',
ADD COLUMN IF NOT EXISTS processing_days INT COMMENT '处理天数',
ADD COLUMN IF NOT EXISTS processing_time_text VARCHAR(255) COMMENT '处理时间文本描述',
ADD COLUMN IF NOT EXISTS is_urgent_available BOOLEAN DEFAULT FALSE COMMENT '是否支持加急',
ADD COLUMN IF NOT EXISTS urgent_processing_days INT COMMENT '加急处理天数',
ADD COLUMN IF NOT EXISTS urgent_price_surcharge DECIMAL(18,2) COMMENT '加急附加费';

-- 利润计算字段
ALTER TABLE products
ADD COLUMN IF NOT EXISTS channel_profit DECIMAL(18,2) COMMENT '渠道方利润',
ADD COLUMN IF NOT EXISTS channel_profit_rate DECIMAL(5,4) COMMENT '渠道方利润率',
ADD COLUMN IF NOT EXISTS channel_customer_profit DECIMAL(18,2) COMMENT '渠道客户利润',
ADD COLUMN IF NOT EXISTS channel_customer_profit_rate DECIMAL(5,4) COMMENT '渠道客户利润率',
ADD COLUMN IF NOT EXISTS direct_profit DECIMAL(18,2) COMMENT '直客利润',
ADD COLUMN IF NOT EXISTS direct_profit_rate DECIMAL(5,4) COMMENT '直客利润率';

-- 业务属性
ALTER TABLE products
ADD COLUMN IF NOT EXISTS commission_rate DECIMAL(5,4) COMMENT '提成比例',
ADD COLUMN IF NOT EXISTS commission_amount DECIMAL(18,2) COMMENT '提成金额',
ADD COLUMN IF NOT EXISTS equivalent_cny DECIMAL(18,2) COMMENT '等值人民币',
ADD COLUMN IF NOT EXISTS monthly_orders INT COMMENT '每月单数',
ADD COLUMN IF NOT EXISTS total_amount DECIMAL(18,2) COMMENT '合计';

-- SLA 和服务级别
ALTER TABLE products
ADD COLUMN IF NOT EXISTS sla_description TEXT COMMENT 'SLA 描述',
ADD COLUMN IF NOT EXISTS service_level VARCHAR(50) COMMENT '服务级别';

-- 状态管理
ALTER TABLE products
ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'active' COMMENT '状态',
ADD COLUMN IF NOT EXISTS suspended_reason TEXT COMMENT '暂停原因',
ADD COLUMN IF NOT EXISTS discontinued_at DATETIME COMMENT '停用时间';

-- 添加索引
CREATE INDEX IF NOT EXISTS ix_products_service_type ON products(service_type);
CREATE INDEX IF NOT EXISTS ix_products_service_subtype ON products(service_subtype);
CREATE INDEX IF NOT EXISTS ix_products_status ON products(status);

-- ============================================================
-- 2. 更新现有数据：将基础价格字段同步到多货币字段
-- ============================================================

-- 将 price_list 同步到 price_list_idr（如果 price_list_idr 为空）
UPDATE products 
SET price_list_idr = price_list 
WHERE price_list IS NOT NULL AND price_list_idr IS NULL;

-- 将 price_channel 同步到 price_channel_idr（如果 price_channel_idr 为空）
UPDATE products 
SET price_channel_idr = price_channel 
WHERE price_channel IS NOT NULL AND price_channel_idr IS NULL;

-- 将 price_cost 同步到 price_cost_idr（如果 price_cost_idr 为空）
UPDATE products 
SET price_cost_idr = price_cost 
WHERE price_cost IS NOT NULL AND price_cost_idr IS NULL;

-- 根据汇率计算 CNY 价格（如果 IDR 价格存在但 CNY 价格为空）
UPDATE products 
SET price_cost_cny = price_cost_idr / exchange_rate 
WHERE price_cost_idr IS NOT NULL AND price_cost_cny IS NULL AND exchange_rate > 0;

UPDATE products 
SET price_channel_cny = price_channel_idr / exchange_rate 
WHERE price_channel_idr IS NOT NULL AND price_channel_cny IS NULL AND exchange_rate > 0;

UPDATE products 
SET price_list_cny = price_list_idr / exchange_rate 
WHERE price_list_idr IS NOT NULL AND price_list_cny IS NULL AND exchange_rate > 0;

-- ============================================================
-- 3. 验证字段同步
-- ============================================================

-- 检查字段是否存在
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'products'
  AND COLUMN_NAME IN (
    'price_cost_idr', 'price_cost_cny',
    'price_channel_idr', 'price_channel_cny',
    'price_direct_idr', 'price_direct_cny',
    'price_list_idr', 'price_list_cny',
    'default_currency', 'exchange_rate',
    'service_type', 'service_subtype',
    'status', 'processing_days', 'processing_time_text'
  )
ORDER BY COLUMN_NAME;

