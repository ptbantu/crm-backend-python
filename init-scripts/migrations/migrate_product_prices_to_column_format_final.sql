-- ============================================================
-- 产品价格表结构改造 - 从行格式改为列格式
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 1. 添加新列（如果不存在）
-- ============================================================
SET @dbname = DATABASE();
SET @tablename = 'product_prices';

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
-- 2. 将现有行格式数据转换为列格式（更新现有记录）
-- ============================================================
UPDATE product_prices pp1
INNER JOIN (
    SELECT 
        product_id,
        organization_id,
        MAX(CASE WHEN price_type = 'channel' AND currency = 'IDR' THEN amount END) AS price_channel_idr,
        MAX(CASE WHEN price_type = 'channel' AND currency = 'CNY' THEN amount END) AS price_channel_cny,
        MAX(CASE WHEN price_type = 'direct' AND currency = 'IDR' THEN amount END) AS price_direct_idr,
        MAX(CASE WHEN price_type = 'direct' AND currency = 'CNY' THEN amount END) AS price_direct_cny,
        MAX(CASE WHEN price_type = 'list' AND currency = 'IDR' THEN amount END) AS price_list_idr,
        MAX(CASE WHEN price_type = 'list' AND currency = 'CNY' THEN amount END) AS price_list_cny,
        MAX(exchange_rate) AS exchange_rate
    FROM product_prices
    GROUP BY product_id, organization_id
) AS aggregated ON pp1.product_id = aggregated.product_id 
    AND (pp1.organization_id = aggregated.organization_id OR (pp1.organization_id IS NULL AND aggregated.organization_id IS NULL))
SET 
    pp1.price_channel_idr = aggregated.price_channel_idr,
    pp1.price_channel_cny = aggregated.price_channel_cny,
    pp1.price_direct_idr = aggregated.price_direct_idr,
    pp1.price_direct_cny = aggregated.price_direct_cny,
    pp1.price_list_idr = aggregated.price_list_idr,
    pp1.price_list_cny = aggregated.price_list_cny,
    pp1.exchange_rate = COALESCE(pp1.exchange_rate, aggregated.exchange_rate);

-- ============================================================
-- 3. 删除重复记录，每个产品+组织只保留一条记录
-- ============================================================
-- 创建临时表存储需要保留的记录ID
CREATE TEMPORARY TABLE temp_keep_ids AS
SELECT MIN(id) as id
FROM product_prices
GROUP BY product_id, organization_id;

-- 删除不在保留列表中的记录
DELETE FROM product_prices
WHERE id NOT IN (SELECT id FROM temp_keep_ids);

-- ============================================================
-- 4. 删除旧列（price_type, currency, amount）
-- ============================================================
-- 先删除索引
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

-- 删除列
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
-- 5. 添加新的检查约束
-- ============================================================
ALTER TABLE product_prices
ADD CONSTRAINT chk_product_prices_channel_idr_nonneg CHECK (price_channel_idr IS NULL OR price_channel_idr >= 0),
ADD CONSTRAINT chk_product_prices_channel_cny_nonneg CHECK (price_channel_cny IS NULL OR price_channel_cny >= 0),
ADD CONSTRAINT chk_product_prices_direct_idr_nonneg CHECK (price_direct_idr IS NULL OR price_direct_idr >= 0),
ADD CONSTRAINT chk_product_prices_direct_cny_nonneg CHECK (price_direct_cny IS NULL OR price_direct_cny >= 0),
ADD CONSTRAINT chk_product_prices_list_idr_nonneg CHECK (price_list_idr IS NULL OR price_list_idr >= 0),
ADD CONSTRAINT chk_product_prices_list_cny_nonneg CHECK (price_list_cny IS NULL OR price_list_cny >= 0);

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 6. 显示迁移结果
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
