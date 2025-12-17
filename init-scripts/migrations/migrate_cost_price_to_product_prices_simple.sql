-- ============================================================
-- 成本价格迁移到 product_prices 表（简化版）
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;
SET FOREIGN_KEY_CHECKS = 0;

-- 1. 添加成本价字段（如果不存在）
ALTER TABLE product_prices 
ADD COLUMN price_cost_idr DECIMAL(18, 2) NULL COMMENT '成本价-IDR' AFTER price_list_cny;

ALTER TABLE product_prices 
ADD COLUMN price_cost_cny DECIMAL(18, 2) NULL COMMENT '成本价-CNY' AFTER price_cost_idr;

-- 2. 添加检查约束
ALTER TABLE product_prices
ADD CONSTRAINT chk_product_prices_cost_idr_nonneg CHECK (price_cost_idr IS NULL OR price_cost_idr >= 0);

ALTER TABLE product_prices
ADD CONSTRAINT chk_product_prices_cost_cny_nonneg CHECK (price_cost_cny IS NULL OR price_cost_cny >= 0);

-- 3. 迁移数据：更新已有 product_prices 记录
UPDATE product_prices pp
INNER JOIN products p ON pp.product_id = p.id
SET 
    pp.price_cost_idr = p.price_cost_idr,
    pp.price_cost_cny = p.price_cost_cny
WHERE 
    (pp.effective_to IS NULL OR pp.effective_to >= NOW())
    AND pp.organization_id IS NULL
    AND (p.price_cost_idr IS NOT NULL OR p.price_cost_cny IS NOT NULL)
    AND (pp.price_cost_idr IS NULL AND pp.price_cost_cny IS NULL);

-- 4. 为没有 product_prices 记录的产品创建新记录
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
    NULL as organization_id,
    p.price_cost_idr,
    p.price_cost_cny,
    NOW() as effective_from,
    NULL as effective_to,
    'migration' as source,
    NOW() as created_at,
    NOW() as updated_at
FROM products p
WHERE 
    (p.price_cost_idr IS NOT NULL OR p.price_cost_cny IS NOT NULL)
    AND NOT EXISTS (
        SELECT 1 FROM product_prices pp 
        WHERE pp.product_id = p.id 
        AND pp.organization_id IS NULL
    );

SET FOREIGN_KEY_CHECKS = 1;

-- 5. 验证迁移结果
SELECT 
    'Migration Complete' as status,
    COUNT(DISTINCT pp.product_id) as products_with_cost_price,
    SUM(CASE WHEN pp.price_cost_idr IS NOT NULL THEN 1 ELSE 0 END) as has_cost_idr,
    SUM(CASE WHEN pp.price_cost_cny IS NOT NULL THEN 1 ELSE 0 END) as has_cost_cny
FROM product_prices pp
WHERE 
    pp.organization_id IS NULL
    AND (pp.price_cost_idr IS NOT NULL OR pp.price_cost_cny IS NOT NULL);
