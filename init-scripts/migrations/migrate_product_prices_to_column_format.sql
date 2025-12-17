-- ============================================================
-- 产品价格表结构改造 - 从行格式改为列格式
-- ============================================================
-- 用途：将 product_prices 表从行存储（每个价格类型+货币一条记录）
--       改为列存储（一条记录包含所有价格类型和货币）
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 1. 备份现有数据到临时表
-- ============================================================
CREATE TABLE IF NOT EXISTS `_product_prices_backup` AS
SELECT * FROM `product_prices`;

-- ============================================================
-- 2. 添加新列（如果不存在）
-- ============================================================
SET @dbname = DATABASE();
SET @tablename = 'product_prices';

-- 添加渠道价列
SET @columnname = 'price_channel_idr';
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
     WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
    'SELECT 1',
    CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' DECIMAL(18, 2) NULL COMMENT ''渠道价-IDR'' AFTER organization_id')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

SET @columnname = 'price_channel_cny';
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
     WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
    'SELECT 1',
    CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' DECIMAL(18, 2) NULL COMMENT ''渠道价-CNY'' AFTER price_channel_idr')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- 添加直客价列
SET @columnname = 'price_direct_idr';
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
     WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
    'SELECT 1',
    CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' DECIMAL(18, 2) NULL COMMENT ''直客价-IDR'' AFTER price_channel_cny')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

SET @columnname = 'price_direct_cny';
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
     WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
    'SELECT 1',
    CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' DECIMAL(18, 2) NULL COMMENT ''直客价-CNY'' AFTER price_direct_idr')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- 添加列表价列
SET @columnname = 'price_list_idr';
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
     WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
    'SELECT 1',
    CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' DECIMAL(18, 2) NULL COMMENT ''列表价-IDR'' AFTER price_direct_cny')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

SET @columnname = 'price_list_cny';
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
     WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
    'SELECT 1',
    CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' DECIMAL(18, 2) NULL COMMENT ''列表价-CNY'' AFTER price_list_idr')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- ============================================================
-- 3. 创建临时表存储转换后的数据
-- ============================================================
CREATE TEMPORARY TABLE temp_product_prices_new AS
SELECT 
    product_id,
    organization_id,
    MAX(CASE WHEN price_type = 'channel' AND currency = 'IDR' THEN amount END) AS price_channel_idr,
    MAX(CASE WHEN price_type = 'channel' AND currency = 'CNY' THEN amount END) AS price_channel_cny,
    MAX(CASE WHEN price_type = 'direct' AND currency = 'IDR' THEN amount END) AS price_direct_idr,
    MAX(CASE WHEN price_type = 'direct' AND currency = 'CNY' THEN amount END) AS price_direct_cny,
    MAX(CASE WHEN price_type = 'list' AND currency = 'IDR' THEN amount END) AS price_list_idr,
    MAX(CASE WHEN price_type = 'list' AND currency = 'CNY' THEN amount END) AS price_list_cny,
    MAX(exchange_rate) AS exchange_rate,
    MIN(effective_from) AS effective_from,
    MAX(effective_to) AS effective_to,
    MAX(source) AS source,
    MAX(is_approved) AS is_approved,
    MAX(approved_by) AS approved_by,
    MAX(approved_at) AS approved_at,
    MAX(change_reason) AS change_reason,
    MAX(changed_by) AS changed_by
FROM product_prices
WHERE source = 'migration' OR organization_id IS NULL
GROUP BY product_id, organization_id;

-- ============================================================
-- 4. 先修改 price_change_logs 表（如果存在 price_id 外键，需要先处理）
-- ============================================================
-- 注意：price_change_logs 表可能引用了 product_prices 表，但不会因为删除列而受影响
-- 因为 price_change_logs 表有自己的 price_type 和 currency 字段

-- ============================================================
-- 5. 清空 product_prices 表（保留表结构）
-- ============================================================
DELETE FROM product_prices;

-- ============================================================
-- 6. 将转换后的数据插入 product_prices 表
-- ============================================================
INSERT INTO product_prices (
    id, product_id, organization_id,
    price_channel_idr, price_channel_cny,
    price_direct_idr, price_direct_cny,
    price_list_idr, price_list_cny,
    exchange_rate, effective_from, effective_to,
    source, is_approved, approved_by, approved_at,
    change_reason, changed_by,
    price_type, currency, amount
)
SELECT 
    UUID(), product_id, organization_id,
    price_channel_idr, price_channel_cny,
    price_direct_idr, price_direct_cny,
    price_list_idr, price_list_cny,
    exchange_rate, effective_from, effective_to,
    COALESCE(source, 'migration'), is_approved, approved_by, approved_at,
    change_reason, changed_by,
    NULL, NULL, NULL
FROM temp_product_prices_new
WHERE price_channel_idr IS NOT NULL 
   OR price_channel_cny IS NOT NULL
   OR price_direct_idr IS NOT NULL
   OR price_direct_cny IS NOT NULL
   OR price_list_idr IS NOT NULL
   OR price_list_cny IS NOT NULL;
SELECT 
    UUID(), product_id, organization_id,
    price_channel_idr, price_channel_cny,
    price_direct_idr, price_direct_cny,
    price_list_idr, price_list_cny,
    exchange_rate, effective_from, effective_to,
    COALESCE(source, 'migration'), is_approved, approved_by, approved_at,
    change_reason, changed_by
FROM temp_product_prices_new
WHERE price_channel_idr IS NOT NULL 
   OR price_channel_cny IS NOT NULL
   OR price_direct_idr IS NOT NULL
   OR price_direct_cny IS NOT NULL
   OR price_list_idr IS NOT NULL
   OR price_list_cny IS NOT NULL;

-- ============================================================
-- 7. 删除旧列（price_type, currency, amount）
-- ============================================================
-- 注意：先删除索引和外键约束
SET @indexname = 'idx_price_type';
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
     WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND INDEX_NAME = @indexname) > 0,
    CONCAT('DROP INDEX ', @indexname, ' ON ', @tablename),
    'SELECT 1'
));
PREPARE dropIndexIfExists FROM @preparedStatement;
EXECUTE dropIndexIfExists;
DEALLOCATE PREPARE dropIndexIfExists;

SET @indexname = 'idx_currency';
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
     WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND INDEX_NAME = @indexname) > 0,
    CONCAT('DROP INDEX ', @indexname, ' ON ', @tablename),
    'SELECT 1'
));
PREPARE dropIndexIfExists FROM @preparedStatement;
EXECUTE dropIndexIfExists;
DEALLOCATE PREPARE dropIndexIfExists;

-- 删除检查约束
SET @constraintname = 'chk_product_prices_price_type';
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
     WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND CONSTRAINT_NAME = @constraintname) > 0,
    CONCAT('ALTER TABLE ', @tablename, ' DROP CONSTRAINT ', @constraintname),
    'SELECT 1'
));
PREPARE dropConstraintIfExists FROM @preparedStatement;
EXECUTE dropConstraintIfExists;
DEALLOCATE PREPARE dropConstraintIfExists;

SET @constraintname = 'chk_product_prices_currency';
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
     WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND CONSTRAINT_NAME = @constraintname) > 0,
    CONCAT('ALTER TABLE ', @tablename, ' DROP CONSTRAINT ', @constraintname),
    'SELECT 1'
));
PREPARE dropConstraintIfExists FROM @preparedStatement;
EXECUTE dropConstraintIfExists;
DEALLOCATE PREPARE dropConstraintIfExists;

SET @constraintname = 'chk_product_prices_amount_nonneg';
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
     WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND CONSTRAINT_NAME = @constraintname) > 0,
    CONCAT('ALTER TABLE ', @tablename, ' DROP CONSTRAINT ', @constraintname),
    'SELECT 1'
));
PREPARE dropConstraintIfExists FROM @preparedStatement;
EXECUTE dropConstraintIfExists;
DEALLOCATE PREPARE dropConstraintIfExists;

-- 删除旧列
SET @columnname = 'price_type';
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
     WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
    CONCAT('ALTER TABLE ', @tablename, ' DROP COLUMN ', @columnname),
    'SELECT 1'
));
PREPARE dropColumnIfExists FROM @preparedStatement;
EXECUTE dropColumnIfExists;
DEALLOCATE PREPARE dropColumnIfExists;

SET @columnname = 'currency';
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
     WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
    CONCAT('ALTER TABLE ', @tablename, ' DROP COLUMN ', @columnname),
    'SELECT 1'
));
PREPARE dropColumnIfExists FROM @preparedStatement;
EXECUTE dropColumnIfExists;
DEALLOCATE PREPARE dropColumnIfExists;

SET @columnname = 'amount';
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
     WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
    CONCAT('ALTER TABLE ', @tablename, ' DROP COLUMN ', @columnname),
    'SELECT 1'
));
PREPARE dropColumnIfExists FROM @preparedStatement;
EXECUTE dropColumnIfExists;
DEALLOCATE PREPARE dropColumnIfExists;

-- ============================================================
-- 8. 添加新的检查约束
-- ============================================================
ALTER TABLE product_prices
ADD CONSTRAINT chk_product_prices_channel_idr_nonneg CHECK (price_channel_idr IS NULL OR price_channel_idr >= 0),
ADD CONSTRAINT chk_product_prices_channel_cny_nonneg CHECK (price_channel_cny IS NULL OR price_channel_cny >= 0),
ADD CONSTRAINT chk_product_prices_direct_idr_nonneg CHECK (price_direct_idr IS NULL OR price_direct_idr >= 0),
ADD CONSTRAINT chk_product_prices_direct_cny_nonneg CHECK (price_direct_cny IS NULL OR price_direct_cny >= 0),
ADD CONSTRAINT chk_product_prices_list_idr_nonneg CHECK (price_list_idr IS NULL OR price_list_idr >= 0),
ADD CONSTRAINT chk_product_prices_list_cny_nonneg CHECK (price_list_cny IS NULL OR price_list_cny >= 0);

-- ============================================================
-- 9. 显示迁移结果
-- ============================================================
SELECT 
    '✅ Migration Complete!' as status,
    COUNT(DISTINCT product_id) as products_migrated,
    COUNT(*) as total_price_records,
    SUM(CASE WHEN price_channel_idr IS NOT NULL THEN 1 ELSE 0 END) as has_channel_idr,
    SUM(CASE WHEN price_channel_cny IS NOT NULL THEN 1 ELSE 0 END) as has_channel_cny,
    SUM(CASE WHEN price_direct_idr IS NOT NULL THEN 1 ELSE 0 END) as has_direct_idr,
    SUM(CASE WHEN price_direct_cny IS NOT NULL THEN 1 ELSE 0 END) as has_direct_cny,
    SUM(CASE WHEN price_list_idr IS NOT NULL THEN 1 ELSE 0 END) as has_list_idr,
    SUM(CASE WHEN price_list_cny IS NOT NULL THEN 1 ELSE 0 END) as has_list_cny
FROM product_prices;

SET FOREIGN_KEY_CHECKS = 1;
