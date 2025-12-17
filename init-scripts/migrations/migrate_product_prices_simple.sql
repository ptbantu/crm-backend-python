-- ============================================================
-- 销售价格独立设计 - 数据迁移脚本（简化版）
-- ============================================================
-- 用途：将 products 表中的销售价格字段迁移到 product_prices 表
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 迁移渠道价 IDR
-- ============================================================
INSERT INTO product_prices (
    id, product_id, organization_id, price_type, currency, amount,
    exchange_rate, effective_from, source, is_approved, change_reason
)
SELECT 
    UUID(), p.id, NULL, 'channel', 'IDR', p.price_channel_idr,
    COALESCE(p.exchange_rate, 2000), NOW(), 'migration', TRUE, '从 products 表迁移'
FROM products p
LEFT JOIN product_prices pp ON pp.product_id = p.id 
    AND pp.price_type = 'channel' AND pp.currency = 'IDR' AND pp.organization_id IS NULL
WHERE p.price_channel_idr IS NOT NULL AND p.price_channel_idr > 0 AND pp.id IS NULL;

-- ============================================================
-- 迁移渠道价 CNY
-- ============================================================
INSERT INTO product_prices (
    id, product_id, organization_id, price_type, currency, amount,
    exchange_rate, effective_from, source, is_approved, change_reason
)
SELECT 
    UUID(), p.id, NULL, 'channel', 'CNY', p.price_channel_cny,
    COALESCE(p.exchange_rate, 2000), NOW(), 'migration', TRUE, '从 products 表迁移'
FROM products p
LEFT JOIN product_prices pp ON pp.product_id = p.id 
    AND pp.price_type = 'channel' AND pp.currency = 'CNY' AND pp.organization_id IS NULL
WHERE p.price_channel_cny IS NOT NULL AND p.price_channel_cny > 0 AND pp.id IS NULL;

-- ============================================================
-- 迁移列表价 IDR
-- ============================================================
INSERT INTO product_prices (
    id, product_id, organization_id, price_type, currency, amount,
    exchange_rate, effective_from, source, is_approved, change_reason
)
SELECT 
    UUID(), p.id, NULL, 'list', 'IDR', p.price_list_idr,
    COALESCE(p.exchange_rate, 2000), NOW(), 'migration', TRUE, '从 products 表迁移'
FROM products p
LEFT JOIN product_prices pp ON pp.product_id = p.id 
    AND pp.price_type = 'list' AND pp.currency = 'IDR' AND pp.organization_id IS NULL
WHERE p.price_list_idr IS NOT NULL AND p.price_list_idr > 0 AND pp.id IS NULL;

-- ============================================================
-- 迁移列表价 CNY
-- ============================================================
INSERT INTO product_prices (
    id, product_id, organization_id, price_type, currency, amount,
    exchange_rate, effective_from, source, is_approved, change_reason
)
SELECT 
    UUID(), p.id, NULL, 'list', 'CNY', p.price_list_cny,
    COALESCE(p.exchange_rate, 2000), NOW(), 'migration', TRUE, '从 products 表迁移'
FROM products p
LEFT JOIN product_prices pp ON pp.product_id = p.id 
    AND pp.price_type = 'list' AND pp.currency = 'CNY' AND pp.organization_id IS NULL
WHERE p.price_list_cny IS NOT NULL AND p.price_list_cny > 0 AND pp.id IS NULL;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 显示迁移结果
-- ============================================================
SELECT 
    '✅ Migration Complete!' as status,
    COUNT(DISTINCT product_id) as products_migrated,
    COUNT(*) as total_price_records,
    SUM(CASE WHEN price_type = 'channel' THEN 1 ELSE 0 END) as channel_prices,
    SUM(CASE WHEN price_type = 'list' THEN 1 ELSE 0 END) as list_prices,
    SUM(CASE WHEN currency = 'IDR' THEN 1 ELSE 0 END) as idr_prices,
    SUM(CASE WHEN currency = 'CNY' THEN 1 ELSE 0 END) as cny_prices
FROM product_prices WHERE source = 'migration';
