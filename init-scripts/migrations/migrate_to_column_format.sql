-- ============================================================
-- 产品价格表数据迁移 - 从行格式转换为列格式
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;
SET FOREIGN_KEY_CHECKS = 0;

-- 清空 product_prices 表
TRUNCATE TABLE product_prices;

-- 插入转换后的数据
INSERT INTO product_prices (
    id, product_id, organization_id,
    price_channel_idr, price_channel_cny,
    price_direct_idr, price_direct_cny,
    price_list_idr, price_list_cny,
    exchange_rate, effective_from, effective_to,
    source, is_approved, approved_by, approved_at,
    change_reason, changed_by, created_at, updated_at
)
SELECT 
    UUID(), 
    product_id,
    organization_id,
    MAX(CASE WHEN price_type = 'channel' AND currency = 'IDR' THEN amount END),
    MAX(CASE WHEN price_type = 'channel' AND currency = 'CNY' THEN amount END),
    MAX(CASE WHEN price_type = 'direct' AND currency = 'IDR' THEN amount END),
    MAX(CASE WHEN price_type = 'direct' AND currency = 'CNY' THEN amount END),
    MAX(CASE WHEN price_type = 'list' AND currency = 'IDR' THEN amount END),
    MAX(CASE WHEN price_type = 'list' AND currency = 'CNY' THEN amount END),
    MAX(exchange_rate),
    MIN(effective_from),
    MAX(effective_to),
    COALESCE(MAX(source), 'migration'),
    MAX(is_approved),
    MAX(approved_by),
    MAX(approved_at),
    MAX(change_reason),
    MAX(changed_by),
    MIN(created_at),
    MAX(updated_at)
FROM _product_prices_backup
GROUP BY product_id, organization_id;

-- 显示迁移结果
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
