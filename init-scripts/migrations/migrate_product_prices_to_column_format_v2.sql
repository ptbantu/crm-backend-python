-- ============================================================
-- 产品价格表结构改造 - 从行格式改为列格式（修复版）
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 1. 添加新列（如果不存在）
-- ============================================================
ALTER TABLE product_prices 
ADD COLUMN IF NOT EXISTS price_channel_idr DECIMAL(18, 2) NULL COMMENT '渠道价-IDR' AFTER organization_id,
ADD COLUMN IF NOT EXISTS price_channel_cny DECIMAL(18, 2) NULL COMMENT '渠道价-CNY' AFTER price_channel_idr,
ADD COLUMN IF NOT EXISTS price_direct_idr DECIMAL(18, 2) NULL COMMENT '直客价-IDR' AFTER price_channel_cny,
ADD COLUMN IF NOT EXISTS price_direct_cny DECIMAL(18, 2) NULL COMMENT '直客价-CNY' AFTER price_direct_idr,
ADD COLUMN IF NOT EXISTS price_list_idr DECIMAL(18, 2) NULL COMMENT '列表价-IDR' AFTER price_direct_cny,
ADD COLUMN IF NOT EXISTS price_list_cny DECIMAL(18, 2) NULL COMMENT '列表价-CNY' AFTER price_list_idr;

-- ============================================================
-- 2. 将现有行格式数据转换为列格式
-- ============================================================
-- 先更新现有记录，将对应价格类型的值填入新列
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
        MAX(exchange_rate) AS exchange_rate,
        MIN(effective_from) AS effective_from,
        MAX(effective_to) AS effective_to
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
DROP INDEX IF EXISTS idx_price_type ON product_prices;
DROP INDEX IF EXISTS idx_currency ON product_prices;

-- 删除检查约束
ALTER TABLE product_prices DROP CONSTRAINT IF EXISTS chk_product_prices_price_type;
ALTER TABLE product_prices DROP CONSTRAINT IF EXISTS chk_product_prices_currency;
ALTER TABLE product_prices DROP CONSTRAINT IF EXISTS chk_product_prices_amount_nonneg;

-- 删除列
ALTER TABLE product_prices DROP COLUMN IF EXISTS price_type;
ALTER TABLE product_prices DROP COLUMN IF EXISTS currency;
ALTER TABLE product_prices DROP COLUMN IF EXISTS amount;

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
