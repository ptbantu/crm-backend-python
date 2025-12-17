-- ============================================================
-- 删除 products 表中的成本价格和预估成本字段
-- ============================================================
-- 作用：删除 products 表中的以下字段：
--      - price_cost_idr, price_cost_cny（成本价，已迁移到 product_prices 表）
--      - estimated_cost_idr, estimated_cost_cny（预估成本，不再使用）
-- 创建时间: 2025-01-XX
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 1. 删除成本价字段
-- ============================================================
ALTER TABLE products DROP COLUMN IF EXISTS price_cost_idr;
ALTER TABLE products DROP COLUMN IF EXISTS price_cost_cny;

-- ============================================================
-- 2. 删除预估成本字段
-- ============================================================
ALTER TABLE products DROP COLUMN IF EXISTS estimated_cost_idr;
ALTER TABLE products DROP COLUMN IF EXISTS estimated_cost_cny;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 3. 验证删除结果
-- ============================================================
SELECT 
    'Deletion Complete' as status,
    COUNT(*) as remaining_cost_fields
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'bantu_crm'
AND TABLE_NAME = 'products'
AND COLUMN_NAME IN ('price_cost_idr', 'price_cost_cny', 'estimated_cost_idr', 'estimated_cost_cny');
