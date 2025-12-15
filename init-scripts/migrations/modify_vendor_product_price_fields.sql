-- 修改供应商产品价格字段：将 cost_price_idr 和 cost_price_cny 合并为 cost_price + currency
-- 执行时间：需要根据实际情况调整

-- 1. 添加新字段
ALTER TABLE `vendor_products`
ADD COLUMN `cost_price` DECIMAL(18, 2) NULL COMMENT '成本价（统一价格）' AFTER `priority`,
ADD COLUMN `currency` VARCHAR(3) NULL DEFAULT 'IDR' COMMENT '货币类型：IDR/CNY' AFTER `cost_price`;

-- 2. 迁移现有数据
-- 优先使用 CNY，如果 CNY 为空则使用 IDR
UPDATE `vendor_products`
SET 
    `cost_price` = CASE 
        WHEN `cost_price_cny` IS NOT NULL THEN `cost_price_cny`
        WHEN `cost_price_idr` IS NOT NULL THEN `cost_price_idr`
        ELSE NULL
    END,
    `currency` = CASE 
        WHEN `cost_price_cny` IS NOT NULL THEN 'CNY'
        WHEN `cost_price_idr` IS NOT NULL THEN 'IDR'
        ELSE 'IDR'
    END
WHERE `cost_price_idr` IS NOT NULL OR `cost_price_cny` IS NOT NULL;

-- 3. 删除旧字段（可选，建议先保留一段时间以便回滚）
-- ALTER TABLE `vendor_products`
-- DROP COLUMN `cost_price_idr`,
-- DROP COLUMN `cost_price_cny`;

-- 注意：如果需要在删除旧字段前保留数据，可以先注释掉删除语句
-- 建议在生产环境中先保留旧字段一段时间，确认新字段工作正常后再删除
