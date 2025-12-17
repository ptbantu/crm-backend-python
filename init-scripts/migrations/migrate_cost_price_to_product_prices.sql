-- ============================================================
-- 成本价格迁移到 product_prices 表
-- ============================================================
-- 作用：将 products 表中的成本价格字段（price_cost_idr, price_cost_cny）
--      迁移到 product_prices 表，实现所有价格统一管理
-- 创建时间: 2025-01-XX
-- ============================================================
-- 注意事项：
-- 1. estimated_cost_idr 和 estimated_cost_cny 保留在 products 表中（作为供应商关联时的默认值）
-- 2. vendor_products 表中的 cost_price_idr 和 cost_price_cny 保持不变（供应商特定成本价）
-- 3. 迁移时需要处理已有 product_prices 记录的情况（更新 vs 创建新记录）
-- 4. 确保价格生效时间逻辑正确（成本价也应该有生效时间管理）
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 1. 更新 product_prices 表结构：添加成本价字段
-- ============================================================
SET @dbname = DATABASE();
SET @tablename = 'product_prices';

-- 添加 price_cost_idr 字段
SET @columnname = 'price_cost_idr';
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
     WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
    'SELECT 1',
    CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' DECIMAL(18, 2) NULL COMMENT ''成本价-IDR'' AFTER price_list_cny')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- 添加 price_cost_cny 字段
SET @columnname = 'price_cost_cny';
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
     WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
    'SELECT 1',
    CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' DECIMAL(18, 2) NULL COMMENT ''成本价-CNY'' AFTER price_cost_idr')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- ============================================================
-- 2. 添加检查约束确保价格非负
-- ============================================================
-- 删除已存在的约束（如果存在）
SET @constraintname = 'chk_product_prices_cost_idr_nonneg';
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
     WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND CONSTRAINT_NAME = @constraintname) > 0,
    CONCAT('ALTER TABLE ', @tablename, ' DROP CONSTRAINT ', @constraintname),
    'SELECT 1'
));
PREPARE dropConstraintIfExists FROM @preparedStatement;
EXECUTE dropConstraintIfExists;
DEALLOCATE PREPARE dropConstraintIfExists;

SET @constraintname = 'chk_product_prices_cost_cny_nonneg';
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
     WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND CONSTRAINT_NAME = @constraintname) > 0,
    CONCAT('ALTER TABLE ', @tablename, ' DROP CONSTRAINT ', @constraintname),
    'SELECT 1'
));
PREPARE dropConstraintIfExists FROM @preparedStatement;
EXECUTE dropConstraintIfExists;
DEALLOCATE PREPARE dropConstraintIfExists;

-- 添加新的检查约束
ALTER TABLE product_prices
ADD CONSTRAINT chk_product_prices_cost_idr_nonneg CHECK (price_cost_idr IS NULL OR price_cost_idr >= 0),
ADD CONSTRAINT chk_product_prices_cost_cny_nonneg CHECK (price_cost_cny IS NULL OR price_cost_cny >= 0);

-- ============================================================
-- 3. 数据迁移：将 products 表中的成本价迁移到 product_prices 表
-- ============================================================
-- 策略：
-- - 对于已有 product_prices 记录的产品，更新现有记录（只更新成本价字段，不影响其他价格）
-- - 对于没有 product_prices 记录的产品，创建新记录（只包含成本价，其他价格字段为 NULL）

-- 3.1 更新已有 product_prices 记录的产品（只更新当前有效的价格记录）
UPDATE product_prices pp
INNER JOIN products p ON pp.product_id = p.id
SET 
    pp.price_cost_idr = p.price_cost_idr,
    pp.price_cost_cny = p.price_cost_cny
WHERE 
    -- 只更新当前有效的价格记录（effective_to 为 NULL 或 >= 当前时间）
    (pp.effective_to IS NULL OR pp.effective_to >= NOW())
    -- 只更新通用价格（organization_id 为 NULL）
    AND pp.organization_id IS NULL
    -- 只迁移非空的成本价
    AND (p.price_cost_idr IS NOT NULL OR p.price_cost_cny IS NOT NULL)
    -- 如果 product_prices 中成本价已存在，则不覆盖（保留已有值）
    AND (pp.price_cost_idr IS NULL AND pp.price_cost_cny IS NULL);

-- 3.2 为没有 product_prices 记录的产品创建新记录（只包含成本价）
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_cost_cny,
    effective_from,
    effective_to,
    source,
    created_at,
    updated_at
)
SELECT 
    UUID() as id,
    p.id as product_id,
    NULL as organization_id,  -- 通用价格
    p.price_cost_idr,
    p.price_cost_cny,
    NOW() as effective_from,
    NULL as effective_to,  -- 当前有效
    'migration' as source,
    NOW() as created_at,
    NOW() as updated_at
FROM products p
WHERE 
    -- 产品有成本价
    (p.price_cost_idr IS NOT NULL OR p.price_cost_cny IS NOT NULL)
    -- 且没有 product_prices 记录
    AND NOT EXISTS (
        SELECT 1 FROM product_prices pp 
        WHERE pp.product_id = p.id 
        AND pp.organization_id IS NULL
    );

-- ============================================================
-- 4. 删除 products 表中的成本价字段
-- ============================================================
-- 注意：estimated_cost_idr 和 estimated_cost_cny 保留在 products 表中

-- 删除 price_cost_idr 字段
SET @columnname = 'price_cost_idr';
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
     WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = 'products' AND COLUMN_NAME = @columnname) > 0,
    CONCAT('ALTER TABLE products DROP COLUMN ', @columnname),
    'SELECT 1'
));
PREPARE dropColumnIfExists FROM @preparedStatement;
EXECUTE dropColumnIfExists;
DEALLOCATE PREPARE dropColumnIfExists;

-- 删除 price_cost_cny 字段
SET @columnname = 'price_cost_cny';
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
     WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = 'products' AND COLUMN_NAME = @columnname) > 0,
    CONCAT('ALTER TABLE products DROP COLUMN ', @columnname),
    'SELECT 1'
));
PREPARE dropColumnIfExists FROM @preparedStatement;
EXECUTE dropColumnIfExists;
DEALLOCATE PREPARE dropColumnIfExists;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 5. 验证迁移结果
-- ============================================================
SELECT 
    '✅ Migration Complete!' as status,
    COUNT(DISTINCT pp.product_id) as products_with_cost_price,
    SUM(CASE WHEN pp.price_cost_idr IS NOT NULL THEN 1 ELSE 0 END) as has_cost_idr,
    SUM(CASE WHEN pp.price_cost_cny IS NOT NULL THEN 1 ELSE 0 END) as has_cost_cny,
    COUNT(DISTINCT p.id) as total_products_with_estimated_cost
FROM product_prices pp
RIGHT JOIN products p ON pp.product_id = p.id
WHERE 
    pp.organization_id IS NULL
    AND (pp.price_cost_idr IS NOT NULL OR pp.price_cost_cny IS NOT NULL 
         OR p.estimated_cost_idr IS NOT NULL OR p.estimated_cost_cny IS NOT NULL);

-- 显示迁移统计
SELECT 
    'Migration Statistics' as info,
    (SELECT COUNT(*) FROM products WHERE estimated_cost_idr IS NOT NULL OR estimated_cost_cny IS NOT NULL) as products_with_estimated_cost,
    (SELECT COUNT(*) FROM product_prices WHERE organization_id IS NULL AND (price_cost_idr IS NOT NULL OR price_cost_cny IS NOT NULL)) as product_prices_with_cost_price;
