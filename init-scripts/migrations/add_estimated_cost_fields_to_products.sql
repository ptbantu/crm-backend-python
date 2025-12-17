-- ============================================================
-- 添加预估成本字段到产品表
-- ============================================================
-- 作用：为产品添加预估成本字段（estimated_cost_idr, estimated_cost_cny）
--      这些字段用于供应商关联产品时的默认成本价，避免供应商每次都需要手动填写
-- 创建时间: 2025-12-16
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

USE bantu_crm;

-- 添加预估成本字段
ALTER TABLE `products` 
ADD COLUMN `estimated_cost_idr` DECIMAL(18, 2) NULL COMMENT '预估成本-IDR（供应商关联产品时的默认成本价）' AFTER `price_cost_cny`,
ADD COLUMN `estimated_cost_cny` DECIMAL(18, 2) NULL COMMENT '预估成本-CNY（供应商关联产品时的默认成本价）' AFTER `estimated_cost_idr`;

-- 添加索引（如果需要按预估成本查询）
-- ALTER TABLE `products` ADD INDEX `idx_estimated_cost_idr` (`estimated_cost_idr`);
-- ALTER TABLE `products` ADD INDEX `idx_estimated_cost_cny` (`estimated_cost_cny`);

-- 验证字段添加成功
SELECT 
    COLUMN_NAME,
    COLUMN_TYPE,
    IS_NULLABLE,
    COLUMN_COMMENT
FROM 
    INFORMATION_SCHEMA.COLUMNS
WHERE 
    TABLE_SCHEMA = 'bantu_crm'
    AND TABLE_NAME = 'products'
    AND COLUMN_NAME IN ('estimated_cost_idr', 'estimated_cost_cny');
