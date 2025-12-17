-- ============================================================
-- 销售价格独立设计 - 数据迁移脚本
-- ============================================================
-- 用途：将 products 表中的销售价格字段迁移到 product_prices 表
-- 说明：此脚本将 products 表中的价格数据迁移到独立的 product_prices 表
--       迁移后，products 表中的价格字段保留（向后兼容），但新价格应使用 product_prices 表
-- ============================================================
-- 执行前请确保：
-- 1. product_prices 表已创建（通过 create_product_prices_table.sql）
-- 2. price_change_logs 表已创建（通过 create_price_and_exchange_rate_tables.sql）
-- 3. 已备份数据库
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 禁用外键检查（迁移数据时）
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 1. 检查表是否存在
-- ============================================================
SET @product_prices_exists = (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'product_prices'
);

SET @products_exists = (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'products'
);

-- 如果表不存在，提示错误
SELECT IF(
    @product_prices_exists = 0,
    'ERROR: product_prices table does not exist. Please run create_product_prices_table.sql first.',
    IF(
        @products_exists = 0,
        'ERROR: products table does not exist.',
        'Tables check passed. Starting migration...'
    )
) AS status;

-- ============================================================
-- 2. 创建临时表记录迁移状态
-- ============================================================
CREATE TABLE IF NOT EXISTS `_migration_product_prices_log` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `product_id` CHAR(36) NOT NULL,
    `price_type` VARCHAR(50) NOT NULL,
    `currency` VARCHAR(10) NOT NULL,
    `migrated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `migration_status` VARCHAR(50) NOT NULL DEFAULT 'success',
    `error_message` TEXT NULL,
    INDEX `idx_product_id` (`product_id`),
    INDEX `idx_migration_status` (`migration_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='产品价格迁移日志表';

-- ============================================================
-- 3. 迁移渠道价（Channel Price）
-- ============================================================
-- 迁移渠道价 IDR
INSERT INTO `product_prices` (
    `id`,
    `product_id`,
    `organization_id`,
    `price_type`,
    `currency`,
    `amount`,
    `exchange_rate`,
    `effective_from`,
    `effective_to`,
    `source`,
    `is_approved`,
    `change_reason`,
    `created_at`,
    `updated_at`
)
SELECT 
    UUID() AS `id`,
    products.`id` AS `product_id`,
    NULL AS `organization_id`,  -- 通用价格
    'channel' AS `price_type`,
    'IDR' AS `currency`,
    products.`price_channel_idr` AS `amount`,
    products.`exchange_rate`,
    COALESCE(products.`created_at`, NOW()) AS `effective_from`,
    NULL AS `effective_to`,  -- 当前有效
    'migration' AS `source`,
    TRUE AS `is_approved`,  -- 迁移的数据视为已审核
    '从 products 表迁移' AS `change_reason`,
    NOW() AS `created_at`,
    NOW() AS `updated_at`
FROM `products`
WHERE products.`price_channel_idr` IS NOT NULL
  AND products.`price_channel_idr` > 0
  AND NOT EXISTS (
      -- 避免重复迁移：检查是否已存在相同的价格记录
      SELECT 1 FROM `product_prices` pp
      WHERE pp.product_id = products.`id`
        AND pp.price_type = 'channel'
        AND pp.currency = 'IDR'
        AND pp.organization_id IS NULL
  );

-- 记录迁移日志
INSERT INTO `_migration_product_prices_log` (`product_id`, `price_type`, `currency`, `migration_status`)
SELECT products.`id`, 'channel', 'IDR', 'success'
FROM `products`
WHERE products.`price_channel_idr` IS NOT NULL AND products.`price_channel_idr` > 0;

-- 迁移渠道价 CNY
INSERT INTO `product_prices` (
    `id`,
    `product_id`,
    `organization_id`,
    `price_type`,
    `currency`,
    `amount`,
    `exchange_rate`,
    `effective_from`,
    `effective_to`,
    `source`,
    `is_approved`,
    `change_reason`,
    `created_at`,
    `updated_at`
)
SELECT 
    UUID() AS `id`,
    products.`id` AS `product_id`,
    NULL AS `organization_id`,
    'channel' AS `price_type`,
    'CNY' AS `currency`,
    products.`price_channel_cny` AS `amount`,
    products.`exchange_rate`,
    COALESCE(products.`created_at`, NOW()) AS `effective_from`,
    NULL AS `effective_to`,
    'migration' AS `source`,
    TRUE AS `is_approved`,
    '从 products 表迁移' AS `change_reason`,
    NOW() AS `created_at`,
    NOW() AS `updated_at`
FROM `products`
WHERE products.`price_channel_cny` IS NOT NULL
  AND products.`price_channel_cny` > 0
  AND NOT EXISTS (
      SELECT 1 FROM `product_prices` pp
      WHERE pp.product_id = products.id
        AND pp.price_type = 'channel'
        AND pp.currency = 'CNY'
        AND pp.organization_id IS NULL
  )
ON DUPLICATE KEY UPDATE `id` = `id`;

INSERT INTO `_migration_product_prices_log` (`product_id`, `price_type`, `currency`, `migration_status`)
SELECT products.`id`, 'channel', 'CNY', 'success'
FROM `products`
WHERE products.`price_channel_cny` IS NOT NULL AND products.`price_channel_cny` > 0;

-- ============================================================
-- 4. 迁移直客价（Direct Price）
-- ============================================================
-- 迁移直客价 IDR
INSERT INTO `product_prices` (
    `id`,
    `product_id`,
    `organization_id`,
    `price_type`,
    `currency`,
    `amount`,
    `exchange_rate`,
    `effective_from`,
    `effective_to`,
    `source`,
    `is_approved`,
    `change_reason`,
    `created_at`,
    `updated_at`
)
SELECT 
    UUID() AS `id`,
    products.`id` AS `product_id`,
    NULL AS `organization_id`,
    'direct' AS `price_type`,
    'IDR' AS `currency`,
    products.`price_direct_idr` AS `amount`,
    `exchange_rate`,
    COALESCE(`created_at`, NOW()) AS `effective_from`,
    NULL AS `effective_to`,
    'migration' AS `source`,
    TRUE AS `is_approved`,
    '从 products 表迁移' AS `change_reason`,
    NOW() AS `created_at`,
    NOW() AS `updated_at`
FROM `products`
WHERE products.`price_direct_idr` IS NOT NULL
  AND products.`price_direct_idr` > 0
  AND NOT EXISTS (
      SELECT 1 FROM `product_prices` pp
      WHERE pp.product_id = products.id
        AND pp.price_type = 'direct'
        AND pp.currency = 'IDR'
        AND pp.organization_id IS NULL
  )
ON DUPLICATE KEY UPDATE `id` = `id`;

INSERT INTO `_migration_product_prices_log` (`product_id`, `price_type`, `currency`, `migration_status`)
SELECT products.`id`, 'direct', 'IDR', 'success'
FROM `products`
WHERE products.`price_direct_idr` IS NOT NULL AND products.`price_direct_idr` > 0;

-- 迁移直客价 CNY
INSERT INTO `product_prices` (
    `id`,
    `product_id`,
    `organization_id`,
    `price_type`,
    `currency`,
    `amount`,
    `exchange_rate`,
    `effective_from`,
    `effective_to`,
    `source`,
    `is_approved`,
    `change_reason`,
    `created_at`,
    `updated_at`
)
SELECT 
    UUID() AS `id`,
    products.`id` AS `product_id`,
    NULL AS `organization_id`,
    'direct' AS `price_type`,
    'CNY' AS `currency`,
    products.`price_direct_cny` AS `amount`,
    `exchange_rate`,
    COALESCE(`created_at`, NOW()) AS `effective_from`,
    NULL AS `effective_to`,
    'migration' AS `source`,
    TRUE AS `is_approved`,
    '从 products 表迁移' AS `change_reason`,
    NOW() AS `created_at`,
    NOW() AS `updated_at`
FROM `products`
WHERE products.`price_direct_cny` IS NOT NULL
  AND products.`price_direct_cny` > 0
  AND NOT EXISTS (
      SELECT 1 FROM `product_prices` pp
      WHERE pp.product_id = products.id
        AND pp.price_type = 'direct'
        AND pp.currency = 'CNY'
        AND pp.organization_id IS NULL
  )
ON DUPLICATE KEY UPDATE `id` = `id`;

INSERT INTO `_migration_product_prices_log` (`product_id`, `price_type`, `currency`, `migration_status`)
SELECT products.`id`, 'direct', 'CNY', 'success'
FROM `products`
WHERE products.`price_direct_cny` IS NOT NULL AND products.`price_direct_cny` > 0;

-- ============================================================
-- 5. 迁移列表价（List Price）
-- ============================================================
-- 迁移列表价 IDR
INSERT INTO `product_prices` (
    `id`,
    `product_id`,
    `organization_id`,
    `price_type`,
    `currency`,
    `amount`,
    `exchange_rate`,
    `effective_from`,
    `effective_to`,
    `source`,
    `is_approved`,
    `change_reason`,
    `created_at`,
    `updated_at`
)
SELECT 
    UUID() AS `id`,
    products.`id` AS `product_id`,
    NULL AS `organization_id`,
    'list' AS `price_type`,
    'IDR' AS `currency`,
    products.`price_list_idr` AS `amount`,
    `exchange_rate`,
    COALESCE(`created_at`, NOW()) AS `effective_from`,
    NULL AS `effective_to`,
    'migration' AS `source`,
    TRUE AS `is_approved`,
    '从 products 表迁移' AS `change_reason`,
    NOW() AS `created_at`,
    NOW() AS `updated_at`
FROM `products`
WHERE products.`price_list_idr` IS NOT NULL
  AND products.`price_list_idr` > 0
  AND NOT EXISTS (
      SELECT 1 FROM `product_prices` pp
      WHERE pp.product_id = products.id
        AND pp.price_type = 'list'
        AND pp.currency = 'IDR'
        AND pp.organization_id IS NULL
  )
ON DUPLICATE KEY UPDATE `id` = `id`;

INSERT INTO `_migration_product_prices_log` (`product_id`, `price_type`, `currency`, `migration_status`)
SELECT products.`id`, 'list', 'IDR', 'success'
FROM `products`
WHERE products.`price_list_idr` IS NOT NULL AND products.`price_list_idr` > 0;

-- 迁移列表价 CNY
INSERT INTO `product_prices` (
    `id`,
    `product_id`,
    `organization_id`,
    `price_type`,
    `currency`,
    `amount`,
    `exchange_rate`,
    `effective_from`,
    `effective_to`,
    `source`,
    `is_approved`,
    `change_reason`,
    `created_at`,
    `updated_at`
)
SELECT 
    UUID() AS `id`,
    products.`id` AS `product_id`,
    NULL AS `organization_id`,
    'list' AS `price_type`,
    'CNY' AS `currency`,
    products.`price_list_cny` AS `amount`,
    `exchange_rate`,
    COALESCE(`created_at`, NOW()) AS `effective_from`,
    NULL AS `effective_to`,
    'migration' AS `source`,
    TRUE AS `is_approved`,
    '从 products 表迁移' AS `change_reason`,
    NOW() AS `created_at`,
    NOW() AS `updated_at`
FROM `products`
WHERE products.`price_list_cny` IS NOT NULL
  AND products.`price_list_cny` > 0
  AND NOT EXISTS (
      SELECT 1 FROM `product_prices` pp
      WHERE pp.product_id = products.id
        AND pp.price_type = 'list'
        AND pp.currency = 'CNY'
        AND pp.organization_id IS NULL
  )
ON DUPLICATE KEY UPDATE `id` = `id`;

INSERT INTO `_migration_product_prices_log` (`product_id`, `price_type`, `currency`, `migration_status`)
SELECT products.`id`, 'list', 'CNY', 'success'
FROM `products`
WHERE products.`price_list_cny` IS NOT NULL AND products.`price_list_cny` > 0;

-- ============================================================
-- 6. 生成迁移统计报告
-- ============================================================
SELECT 
    'Migration Summary' AS report_type,
    COUNT(DISTINCT product_id) AS total_products_migrated,
    COUNT(*) AS total_price_records_migrated,
    SUM(CASE WHEN price_type = 'channel' THEN 1 ELSE 0 END) AS channel_prices,
    SUM(CASE WHEN price_type = 'direct' THEN 1 ELSE 0 END) AS direct_prices,
    SUM(CASE WHEN price_type = 'list' THEN 1 ELSE 0 END) AS list_prices,
    SUM(CASE WHEN currency = 'IDR' THEN 1 ELSE 0 END) AS idr_prices,
    SUM(CASE WHEN currency = 'CNY' THEN 1 ELSE 0 END) AS cny_prices
FROM `_migration_product_prices_log`
WHERE migration_status = 'success';

-- ============================================================
-- 7. 验证迁移结果
-- ============================================================
-- 检查是否有产品价格未迁移
SELECT 
    'Products with prices not migrated' AS check_type,
    COUNT(*) AS count
FROM `products` p
WHERE (
    (p.price_channel_idr IS NOT NULL AND p.price_channel_idr > 0)
    OR (p.price_channel_cny IS NOT NULL AND p.price_channel_cny > 0)
    OR (p.price_direct_idr IS NOT NULL AND p.price_direct_idr > 0)
    OR (p.price_direct_cny IS NOT NULL AND p.price_direct_cny > 0)
    OR (p.price_list_idr IS NOT NULL AND p.price_list_idr > 0)
    OR (p.price_list_cny IS NOT NULL AND p.price_list_cny > 0)
)
AND NOT EXISTS (
    SELECT 1 FROM `product_prices` pp
    WHERE pp.product_id = p.id
    AND pp.organization_id IS NULL
);

-- ============================================================
-- 8. 创建验证视图（可选）
-- ============================================================
-- 创建视图用于对比 products 表和 product_prices 表的价格
DROP VIEW IF EXISTS `v_product_prices_comparison`;
CREATE VIEW `v_product_prices_comparison` AS
SELECT 
    p.id AS product_id,
    p.code AS product_code,
    p.name AS product_name,
    -- products 表中的价格
    p.price_channel_idr AS products_channel_idr,
    p.price_channel_cny AS products_channel_cny,
    p.price_direct_idr AS products_direct_idr,
    p.price_direct_cny AS products_direct_cny,
    p.price_list_idr AS products_list_idr,
    p.price_list_cny AS products_list_cny,
    -- product_prices 表中的价格（当前有效）
    MAX(CASE WHEN pp.price_type = 'channel' AND pp.currency = 'IDR' AND pp.organization_id IS NULL THEN pp.amount END) AS product_prices_channel_idr,
    MAX(CASE WHEN pp.price_type = 'channel' AND pp.currency = 'CNY' AND pp.organization_id IS NULL THEN pp.amount END) AS product_prices_channel_cny,
    MAX(CASE WHEN pp.price_type = 'direct' AND pp.currency = 'IDR' AND pp.organization_id IS NULL THEN pp.amount END) AS product_prices_direct_idr,
    MAX(CASE WHEN pp.price_type = 'direct' AND pp.currency = 'CNY' AND pp.organization_id IS NULL THEN pp.amount END) AS product_prices_direct_cny,
    MAX(CASE WHEN pp.price_type = 'list' AND pp.currency = 'IDR' AND pp.organization_id IS NULL THEN pp.amount END) AS product_prices_list_idr,
    MAX(CASE WHEN pp.price_type = 'list' AND pp.currency = 'CNY' AND pp.organization_id IS NULL THEN pp.amount END) AS product_prices_list_cny
FROM products p
LEFT JOIN product_prices pp ON p.id = pp.product_id
    AND pp.organization_id IS NULL
    AND pp.effective_from <= NOW()
    AND (pp.effective_to IS NULL OR pp.effective_to > NOW())
GROUP BY p.id, p.code, p.name,
    p.price_channel_idr, p.price_channel_cny,
    p.price_direct_idr, p.price_direct_cny,
    p.price_list_idr, p.price_list_cny;

-- ============================================================
-- 9. 恢复外键检查
-- ============================================================
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 迁移完成
-- ============================================================
SELECT 
    'Migration completed successfully!' AS status,
    NOW() AS completed_at,
    'Please review the migration log table _migration_product_prices_log for details.' AS note;
