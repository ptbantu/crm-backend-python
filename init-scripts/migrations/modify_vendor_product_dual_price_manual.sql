-- ============================================================
-- 修改供应商产品表支持双价格（CNY和IDR）- 手动执行版本
-- ============================================================
-- 用途：手动执行，适用于 MySQL 5.7 或需要更精确控制的场景
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- ============================================================
-- 第一部分：修改 vendor_products 表
-- ============================================================

-- 1. 检查并添加 cost_price_cny 字段
-- 如果字段不存在，执行下面的语句
ALTER TABLE `vendor_products`
ADD COLUMN `cost_price_cny` DECIMAL(18, 2) NULL COMMENT '成本价（人民币）' AFTER `priority`;

-- 2. 检查并添加 cost_price_idr 字段
-- 如果字段不存在，执行下面的语句
ALTER TABLE `vendor_products`
ADD COLUMN `cost_price_idr` DECIMAL(18, 2) NULL COMMENT '成本价（印尼盾）' AFTER `cost_price_cny`;

-- 3. 迁移现有数据（如果存在 cost_price + currency 字段）
-- 执行前请确认 vendor_products 表中有 cost_price 和 currency 字段
UPDATE `vendor_products`
SET 
    `cost_price_cny` = CASE 
        WHEN `currency` = 'CNY' THEN `cost_price`
        ELSE NULL
    END,
    `cost_price_idr` = CASE 
        WHEN `currency` = 'IDR' OR `currency` IS NULL THEN `cost_price`
        ELSE NULL
    END
WHERE `cost_price` IS NOT NULL;

-- ============================================================
-- 第二部分：修改 vendor_product_price_history 表
-- ============================================================

-- 1. 检查并添加 old_price_cny 字段
-- 如果字段不存在，执行下面的语句
ALTER TABLE `vendor_product_price_history`
ADD COLUMN `old_price_cny` DECIMAL(18, 2) NULL COMMENT '旧价格（人民币）' AFTER `vendor_product_id`;

-- 2. 检查并添加 old_price_idr 字段
-- 如果字段不存在，执行下面的语句
ALTER TABLE `vendor_product_price_history`
ADD COLUMN `old_price_idr` DECIMAL(18, 2) NULL COMMENT '旧价格（印尼盾）' AFTER `old_price_cny`;

-- 3. 检查并添加 new_price_cny 字段
-- 如果字段不存在，执行下面的语句
ALTER TABLE `vendor_product_price_history`
ADD COLUMN `new_price_cny` DECIMAL(18, 2) NULL COMMENT '新价格（人民币）' AFTER `old_price_idr`;

-- 4. 检查并添加 new_price_idr 字段
-- 如果字段不存在，执行下面的语句
ALTER TABLE `vendor_product_price_history`
ADD COLUMN `new_price_idr` DECIMAL(18, 2) NULL COMMENT '新价格（印尼盾）' AFTER `new_price_cny`;

-- 5. 迁移价格历史数据（如果存在 old_price + new_price + currency 字段）
-- 执行前请确认 vendor_product_price_history 表中有这些字段
UPDATE `vendor_product_price_history`
SET 
    `old_price_cny` = CASE 
        WHEN `currency` = 'CNY' THEN `old_price`
        ELSE NULL
    END,
    `old_price_idr` = CASE 
        WHEN `currency` = 'IDR' OR `currency` IS NULL THEN `old_price`
        ELSE NULL
    END,
    `new_price_cny` = CASE 
        WHEN `currency` = 'CNY' THEN `new_price`
        ELSE NULL
    END,
    `new_price_idr` = CASE 
        WHEN `currency` = 'IDR' OR `currency` IS NULL THEN `new_price`
        ELSE NULL
    END
WHERE `new_price` IS NOT NULL;

-- ============================================================
-- 执行说明：
-- ============================================================
-- 1. 如果字段已存在，ALTER TABLE 语句会报错，可以忽略
-- 2. 建议先检查字段是否存在：
--    SELECT COLUMN_NAME 
--    FROM INFORMATION_SCHEMA.COLUMNS 
--    WHERE TABLE_SCHEMA = DATABASE() 
--    AND TABLE_NAME = 'vendor_products' 
--    AND COLUMN_NAME IN ('cost_price_cny', 'cost_price_idr');
--
--    SELECT COLUMN_NAME 
--    FROM INFORMATION_SCHEMA.COLUMNS 
--    WHERE TABLE_SCHEMA = DATABASE() 
--    AND TABLE_NAME = 'vendor_product_price_history' 
--    AND COLUMN_NAME IN ('old_price_cny', 'old_price_idr', 'new_price_cny', 'new_price_idr');
-- ============================================================
