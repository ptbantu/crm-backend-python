/**
 * 删除 products 表中重复的价格字段（直接删除版本）
 * 
 * 注意：此脚本会直接删除字段，如果字段不存在会报错，但可以忽略
 */

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================
-- 1. 备份数据
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
-- 2. 删除检查约束（必须先删除约束才能删除字段）
-- ============================================
ALTER TABLE products DROP CONSTRAINT IF EXISTS chk_products_prices_nonneg;

-- ============================================
-- 3. 删除字段（直接删除）
-- ============================================

-- 删除旧的价格字段（单货币）
ALTER TABLE products DROP COLUMN price_list;
ALTER TABLE products DROP COLUMN price_channel;
ALTER TABLE products DROP COLUMN price_cost;

-- 删除销售价格字段（多货币）
ALTER TABLE products DROP COLUMN price_channel_idr;
ALTER TABLE products DROP COLUMN price_channel_cny;
ALTER TABLE products DROP COLUMN price_direct_idr;
ALTER TABLE products DROP COLUMN price_direct_cny;
ALTER TABLE products DROP COLUMN price_list_idr;
ALTER TABLE products DROP COLUMN price_list_cny;

-- 删除汇率相关字段
ALTER TABLE products DROP COLUMN exchange_rate;
ALTER TABLE products DROP COLUMN default_currency;

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

-- ============================================
-- 5. 确认保留的字段
-- ============================================
SELECT 
    '保留的字段检查' AS check_type,
    COLUMN_NAME,
    DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'products'
AND COLUMN_NAME IN (
    'price_cost_idr', 'price_cost_cny',
    'estimated_cost_idr', 'estimated_cost_cny'
)
ORDER BY COLUMN_NAME;

-- ============================================
-- 完成
-- ============================================
SELECT '迁移完成：已删除 products 表中的重复价格字段' AS message,
       '备份表：_products_price_fields_backup' AS backup_table;
