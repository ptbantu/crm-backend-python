-- ============================================================
-- 修改供应商产品表支持双价格（CNY和IDR）
-- ============================================================
-- 用途：将单一价格+货币字段改为双价格字段
-- 执行时间：需要根据实际情况调整
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 1. 检查并添加双价格字段（如果不存在）
-- 如果表已经有 cost_price_cny 和 cost_price_idr，则跳过
-- 如果表只有 cost_price + currency，则需要迁移

-- 检查是否存在 cost_price_cny 字段
SET @has_cny = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'vendor_products' 
    AND COLUMN_NAME = 'cost_price_cny'
);

-- 检查是否存在 cost_price 字段
SET @has_single_price = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'vendor_products' 
    AND COLUMN_NAME = 'cost_price'
);

-- 如果只有单一价格字段，需要迁移数据
SET @sql = IF(@has_single_price > 0 AND @has_cny = 0,
    CONCAT(
        'ALTER TABLE `vendor_products` ',
        'ADD COLUMN `cost_price_cny` DECIMAL(18, 2) NULL COMMENT ''成本价（人民币）'' AFTER `priority`, ',
        'ADD COLUMN `cost_price_idr` DECIMAL(18, 2) NULL COMMENT ''成本价（印尼盾）'' AFTER `cost_price_cny`;'
    ),
    'SELECT ''双价格字段已存在，跳过添加'' AS message;'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2. 迁移现有数据（如果存在 cost_price + currency）
SET @sql2 = IF(@has_single_price > 0 AND @has_cny = 0,
    'UPDATE `vendor_products`
    SET 
        `cost_price_cny` = CASE 
            WHEN `currency` = ''CNY'' THEN `cost_price`
            ELSE NULL
        END,
        `cost_price_idr` = CASE 
            WHEN `currency` = ''IDR'' OR `currency` IS NULL THEN `cost_price`
            ELSE NULL
        END
    WHERE `cost_price` IS NOT NULL;',
    'SELECT ''无需迁移数据'' AS message;'
);

PREPARE stmt2 FROM @sql2;
EXECUTE stmt2;
DEALLOCATE PREPARE stmt2;

-- 3. 删除旧字段（可选，建议先保留一段时间以便回滚）
-- 如果需要删除 cost_price 和 currency 字段，取消下面的注释
-- ALTER TABLE `vendor_products`
-- DROP COLUMN `cost_price`,
-- DROP COLUMN `currency`;

-- ============================================================
-- 修改供应商产品价格历史表支持双价格
-- ============================================================

-- 检查价格历史表是否存在双价格字段
SET @has_history_cny = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'vendor_product_price_history' 
    AND COLUMN_NAME = 'new_price_cny'
);

SET @has_history_single = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'vendor_product_price_history' 
    AND COLUMN_NAME = 'new_price'
);

-- 如果只有单一价格字段，需要迁移
SET @sql3 = IF(@has_history_single > 0 AND @has_history_cny = 0,
    CONCAT(
        'ALTER TABLE `vendor_product_price_history` ',
        'ADD COLUMN `old_price_cny` DECIMAL(18, 2) NULL COMMENT ''旧价格（人民币）'' AFTER `vendor_product_id`, ',
        'ADD COLUMN `old_price_idr` DECIMAL(18, 2) NULL COMMENT ''旧价格（印尼盾）'' AFTER `old_price_cny`, ',
        'ADD COLUMN `new_price_cny` DECIMAL(18, 2) NULL COMMENT ''新价格（人民币）'' AFTER `old_price_idr`, ',
        'ADD COLUMN `new_price_idr` DECIMAL(18, 2) NULL COMMENT ''新价格（印尼盾）'' AFTER `new_price_cny`;'
    ),
    'SELECT ''双价格历史字段已存在，跳过添加'' AS message;'
);

PREPARE stmt3 FROM @sql3;
EXECUTE stmt3;
DEALLOCATE PREPARE stmt3;

-- 迁移价格历史数据
SET @sql4 = IF(@has_history_single > 0 AND @has_history_cny = 0,
    'UPDATE `vendor_product_price_history`
    SET 
        `old_price_cny` = CASE 
            WHEN `currency` = ''CNY'' THEN `old_price`
            ELSE NULL
        END,
        `old_price_idr` = CASE 
            WHEN `currency` = ''IDR'' OR `currency` IS NULL THEN `old_price`
            ELSE NULL
        END,
        `new_price_cny` = CASE 
            WHEN `currency` = ''CNY'' THEN `new_price`
            ELSE NULL
        END,
        `new_price_idr` = CASE 
            WHEN `currency` = ''IDR'' OR `currency` IS NULL THEN `new_price`
            ELSE NULL
        END
    WHERE `new_price` IS NOT NULL;',
    'SELECT ''无需迁移历史数据'' AS message;'
);

PREPARE stmt4 FROM @sql4;
EXECUTE stmt4;
DEALLOCATE PREPARE stmt4;

-- 删除价格历史表的旧字段（可选）
-- ALTER TABLE `vendor_product_price_history`
-- DROP COLUMN `old_price`,
-- DROP COLUMN `new_price`,
-- DROP COLUMN `currency`;

-- 注意：建议在生产环境中先保留旧字段一段时间，确认新字段工作正常后再删除
