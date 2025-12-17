/**
 * 删除 products 表中重复的价格字段
 * 
 * 背景：
 * - 销售价格（渠道价、直客价、列表价）已迁移到 product_prices 表（列格式）
 * - products 表中仍保留这些字段，造成数据冗余
 * - 成本价（price_cost_idr, price_cost_cny）和预估成本（estimated_cost_idr, estimated_cost_cny）保留在 products 表中
 * 
 * 删除的字段：
 * 1. 旧的价格字段（单货币，已废弃）：
 *    - price_list
 *    - price_channel
 *    - price_cost
 * 
 * 2. 销售价格字段（多货币，已迁移到 product_prices 表）：
 *    - price_channel_idr
 *    - price_channel_cny
 *    - price_direct_idr
 *    - price_direct_cny
 *    - price_list_idr
 *    - price_list_cny
 * 
 * 3. 汇率相关字段（product_prices 表中也有）：
 *    - exchange_rate
 *    - default_currency（可选，如果不再需要）
 * 
 * 保留的字段：
 * - price_cost_idr, price_cost_cny（成本价，供应商价格）
 * - estimated_cost_idr, estimated_cost_cny（预估成本）
 */

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================
-- 1. 备份数据（可选，如果需要保留历史数据）
-- ============================================
DROP TABLE IF EXISTS `_products_price_fields_backup`;

CREATE TABLE `_products_price_fields_backup` AS
SELECT 
    id,
    price_list,
    price_channel,
    price_cost,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    price_list_idr,
    price_list_cny,
    exchange_rate,
    default_currency,
    created_at
FROM products;

SELECT CONCAT('备份完成，共 ', COUNT(*), ' 条记录') AS backup_status FROM _products_price_fields_backup;

-- ============================================
-- 2. 删除检查约束（如果存在）
-- ============================================
SET @constraint_name = (
    SELECT CONSTRAINT_NAME 
    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'products' 
    AND CONSTRAINT_NAME = 'chk_products_prices_nonneg'
    LIMIT 1
);

SET @sql = IF(@constraint_name IS NOT NULL, 
    CONCAT('ALTER TABLE products DROP CONSTRAINT ', @constraint_name),
    'SELECT "约束不存在，跳过" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ============================================
-- 3. 删除字段的函数（动态检查列是否存在）
-- ============================================

-- 删除旧的价格字段（单货币）
SET @col_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'products' 
    AND COLUMN_NAME = 'price_list'
);

SET @sql = IF(@col_exists > 0, 'ALTER TABLE products DROP COLUMN price_list', 'SELECT "price_list 列不存在，跳过" AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'products' 
    AND COLUMN_NAME = 'price_channel'
);

SET @sql = IF(@col_exists > 0, 'ALTER TABLE products DROP COLUMN price_channel', 'SELECT "price_channel 列不存在，跳过" AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'products' 
    AND COLUMN_NAME = 'price_cost'
);

SET @sql = IF(@col_exists > 0, 'ALTER TABLE products DROP COLUMN price_cost', 'SELECT "price_cost 列不存在，跳过" AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 删除销售价格字段（多货币）
SET @col_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'products' 
    AND COLUMN_NAME = 'price_channel_idr'
);

SET @sql = IF(@col_exists > 0, 'ALTER TABLE products DROP COLUMN price_channel_idr', 'SELECT "price_channel_idr 列不存在，跳过" AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'products' 
    AND COLUMN_NAME = 'price_channel_cny'
);

SET @sql = IF(@col_exists > 0, 'ALTER TABLE products DROP COLUMN price_channel_cny', 'SELECT "price_channel_cny 列不存在，跳过" AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'products' 
    AND COLUMN_NAME = 'price_direct_idr'
);

SET @sql = IF(@col_exists > 0, 'ALTER TABLE products DROP COLUMN price_direct_idr', 'SELECT "price_direct_idr 列不存在，跳过" AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'products' 
    AND COLUMN_NAME = 'price_direct_cny'
);

SET @sql = IF(@col_exists > 0, 'ALTER TABLE products DROP COLUMN price_direct_cny', 'SELECT "price_direct_cny 列不存在，跳过" AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'products' 
    AND COLUMN_NAME = 'price_list_idr'
);

SET @sql = IF(@col_exists > 0, 'ALTER TABLE products DROP COLUMN price_list_idr', 'SELECT "price_list_idr 列不存在，跳过" AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'products' 
    AND COLUMN_NAME = 'price_list_cny'
);

SET @sql = IF(@col_exists > 0, 'ALTER TABLE products DROP COLUMN price_list_cny', 'SELECT "price_list_cny 列不存在，跳过" AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 删除汇率相关字段
SET @col_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'products' 
    AND COLUMN_NAME = 'exchange_rate'
);

SET @sql = IF(@col_exists > 0, 'ALTER TABLE products DROP COLUMN exchange_rate', 'SELECT "exchange_rate 列不存在，跳过" AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'products' 
    AND COLUMN_NAME = 'default_currency'
);

SET @sql = IF(@col_exists > 0, 'ALTER TABLE products DROP COLUMN default_currency', 'SELECT "default_currency 列不存在，跳过" AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- 4. 验证删除结果
-- ============================================
SELECT 
    '已删除的字段检查' AS check_type,
    COLUMN_NAME,
    '应该为空' AS expected_result
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'products'
AND COLUMN_NAME IN (
    'price_list', 'price_channel', 'price_cost',
    'price_channel_idr', 'price_channel_cny',
    'price_direct_idr', 'price_direct_cny',
    'price_list_idr', 'price_list_cny',
    'exchange_rate', 'default_currency'
)
ORDER BY COLUMN_NAME;

-- 应该返回空结果（所有字段都已删除）

-- ============================================
-- 5. 确认保留的字段
-- ============================================
SELECT 
    '保留的字段检查' AS check_type,
    COLUMN_NAME,
    DATA_TYPE,
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'products'
AND COLUMN_NAME IN (
    'price_cost_idr', 'price_cost_cny',
    'estimated_cost_idr', 'estimated_cost_cny'
)
ORDER BY COLUMN_NAME;

-- 应该返回4个字段（成本价和预估成本）

-- ============================================
-- 完成
-- ============================================
SELECT '迁移完成：已删除 products 表中的重复价格字段' AS message,
       '备份表：_products_price_fields_backup' AS backup_table;
