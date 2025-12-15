-- ============================================================
-- 修改供应商产品表支持双价格（CNY和IDR）- 可直接执行版本
-- ============================================================
-- 用途：使用存储过程安全地添加字段，如果字段已存在则跳过
-- 适用于 MySQL 5.7+
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

DELIMITER $$

-- 创建存储过程：安全添加列
DROP PROCEDURE IF EXISTS `add_column_if_not_exists`$$
CREATE PROCEDURE `add_column_if_not_exists`(
    IN table_name VARCHAR(255),
    IN column_name VARCHAR(255),
    IN column_definition TEXT
)
BEGIN
    DECLARE column_exists INT DEFAULT 0;
    
    SELECT COUNT(*) INTO column_exists
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = table_name
    AND COLUMN_NAME = column_name;
    
    IF column_exists = 0 THEN
        SET @sql = CONCAT('ALTER TABLE `', table_name, '` ADD COLUMN `', column_name, '` ', column_definition);
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END$$

DELIMITER ;

-- ============================================================
-- 修改 vendor_products 表
-- ============================================================

-- 添加双价格字段
CALL add_column_if_not_exists('vendor_products', 'cost_price_cny', 'DECIMAL(18, 2) NULL COMMENT ''成本价（人民币）'' AFTER `priority`');
CALL add_column_if_not_exists('vendor_products', 'cost_price_idr', 'DECIMAL(18, 2) NULL COMMENT ''成本价（印尼盾）'' AFTER `cost_price_cny`');

-- 迁移现有数据（如果存在 cost_price + currency 字段）
UPDATE `vendor_products`
SET 
    `cost_price_cny` = CASE 
        WHEN EXISTS (
            SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'vendor_products' 
            AND COLUMN_NAME = 'currency'
        ) AND `currency` = 'CNY' THEN `cost_price`
        WHEN EXISTS (
            SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'vendor_products' 
            AND COLUMN_NAME = 'cost_price'
        ) AND NOT EXISTS (
            SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'vendor_products' 
            AND COLUMN_NAME = 'currency'
        ) THEN NULL
        ELSE `cost_price_cny`
    END,
    `cost_price_idr` = CASE 
        WHEN EXISTS (
            SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'vendor_products' 
            AND COLUMN_NAME = 'currency'
        ) AND (`currency` = 'IDR' OR `currency` IS NULL) THEN `cost_price`
        WHEN EXISTS (
            SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'vendor_products' 
            AND COLUMN_NAME = 'cost_price'
        ) AND NOT EXISTS (
            SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'vendor_products' 
            AND COLUMN_NAME = 'currency'
        ) THEN `cost_price`
        ELSE `cost_price_idr`
    END
WHERE EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'vendor_products' 
    AND COLUMN_NAME = 'cost_price'
)
AND `cost_price` IS NOT NULL;

-- ============================================================
-- 修改 vendor_product_price_history 表
-- ============================================================

-- 添加双价格历史字段
CALL add_column_if_not_exists('vendor_product_price_history', 'old_price_cny', 'DECIMAL(18, 2) NULL COMMENT ''旧价格（人民币）'' AFTER `vendor_product_id`');
CALL add_column_if_not_exists('vendor_product_price_history', 'old_price_idr', 'DECIMAL(18, 2) NULL COMMENT ''旧价格（印尼盾）'' AFTER `old_price_cny`');
CALL add_column_if_not_exists('vendor_product_price_history', 'new_price_cny', 'DECIMAL(18, 2) NULL COMMENT ''新价格（人民币）'' AFTER `old_price_idr`');
CALL add_column_if_not_exists('vendor_product_price_history', 'new_price_idr', 'DECIMAL(18, 2) NULL COMMENT ''新价格（印尼盾）'' AFTER `new_price_cny`');

-- 迁移价格历史数据（如果存在 old_price + new_price + currency 字段）
UPDATE `vendor_product_price_history`
SET 
    `old_price_cny` = CASE 
        WHEN EXISTS (
            SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'vendor_product_price_history' 
            AND COLUMN_NAME = 'currency'
        ) AND `currency` = 'CNY' THEN `old_price`
        ELSE `old_price_cny`
    END,
    `old_price_idr` = CASE 
        WHEN EXISTS (
            SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'vendor_product_price_history' 
            AND COLUMN_NAME = 'currency'
        ) AND (`currency` = 'IDR' OR `currency` IS NULL) THEN `old_price`
        ELSE `old_price_idr`
    END,
    `new_price_cny` = CASE 
        WHEN EXISTS (
            SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'vendor_product_price_history' 
            AND COLUMN_NAME = 'currency'
        ) AND `currency` = 'CNY' THEN `new_price`
        ELSE `new_price_cny`
    END,
    `new_price_idr` = CASE 
        WHEN EXISTS (
            SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'vendor_product_price_history' 
            AND COLUMN_NAME = 'currency'
        ) AND (`currency` = 'IDR' OR `currency` IS NULL) THEN `new_price`
        ELSE `new_price_idr`
    END
WHERE EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'vendor_product_price_history' 
    AND COLUMN_NAME = 'new_price'
)
AND `new_price` IS NOT NULL;

-- 清理：删除临时存储过程
DROP PROCEDURE IF EXISTS `add_column_if_not_exists`;

DELIMITER ;
