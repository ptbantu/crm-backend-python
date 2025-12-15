-- ============================================================
-- 修改供应商产品表支持双价格（CNY和IDR）- 简化版本
-- ============================================================
-- 用途：直接添加双价格字段，如果字段已存在则忽略错误
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 1. 修改 vendor_products 表：添加双价格字段（如果不存在）
-- 注意：如果字段已存在，会报错但可以忽略

-- 添加 cost_price_cny 字段（如果不存在）
ALTER TABLE `vendor_products`
ADD COLUMN IF NOT EXISTS `cost_price_cny` DECIMAL(18, 2) NULL COMMENT '成本价（人民币）' AFTER `priority`;

-- 添加 cost_price_idr 字段（如果不存在）
ALTER TABLE `vendor_products`
ADD COLUMN IF NOT EXISTS `cost_price_idr` DECIMAL(18, 2) NULL COMMENT '成本价（印尼盾）' AFTER `cost_price_cny`;

-- 2. 迁移现有数据（如果存在 cost_price + currency 字段）
-- 注意：只有在存在这些字段时才执行
UPDATE `vendor_products`
SET 
    `cost_price_cny` = CASE 
        WHEN `currency` = 'CNY' THEN `cost_price`
        ELSE `cost_price_cny`
    END,
    `cost_price_idr` = CASE 
        WHEN `currency` = 'IDR' OR `currency` IS NULL THEN `cost_price`
        ELSE `cost_price_idr`
    END
WHERE EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'vendor_products' 
    AND COLUMN_NAME = 'cost_price'
)
AND EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'vendor_products' 
    AND COLUMN_NAME = 'currency'
)
AND `cost_price` IS NOT NULL;

-- ============================================================
-- 修改供应商产品价格历史表支持双价格
-- ============================================================

-- 添加 old_price_cny 字段（如果不存在）
ALTER TABLE `vendor_product_price_history`
ADD COLUMN IF NOT EXISTS `old_price_cny` DECIMAL(18, 2) NULL COMMENT '旧价格（人民币）' AFTER `vendor_product_id`;

-- 添加 old_price_idr 字段（如果不存在）
ALTER TABLE `vendor_product_price_history`
ADD COLUMN IF NOT EXISTS `old_price_idr` DECIMAL(18, 2) NULL COMMENT '旧价格（印尼盾）' AFTER `old_price_cny`;

-- 添加 new_price_cny 字段（如果不存在）
ALTER TABLE `vendor_product_price_history`
ADD COLUMN IF NOT EXISTS `new_price_cny` DECIMAL(18, 2) NULL COMMENT '新价格（人民币）' AFTER `old_price_idr`;

-- 添加 new_price_idr 字段（如果不存在）
ALTER TABLE `vendor_product_price_history`
ADD COLUMN IF NOT EXISTS `new_price_idr` DECIMAL(18, 2) NULL COMMENT '新价格（印尼盾）' AFTER `new_price_cny`;

-- 迁移价格历史数据（如果存在 old_price + new_price + currency 字段）
UPDATE `vendor_product_price_history`
SET 
    `old_price_cny` = CASE 
        WHEN `currency` = 'CNY' THEN `old_price`
        ELSE `old_price_cny`
    END,
    `old_price_idr` = CASE 
        WHEN `currency` = 'IDR' OR `currency` IS NULL THEN `old_price`
        ELSE `old_price_idr`
    END,
    `new_price_cny` = CASE 
        WHEN `currency` = 'CNY' THEN `new_price`
        ELSE `new_price_cny`
    END,
    `new_price_idr` = CASE 
        WHEN `currency` = 'IDR' OR `currency` IS NULL THEN `new_price`
        ELSE `new_price_idr`
    END
WHERE EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'vendor_product_price_history' 
    AND COLUMN_NAME = 'old_price'
)
AND EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'vendor_product_price_history' 
    AND COLUMN_NAME = 'new_price'
)
AND EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'vendor_product_price_history' 
    AND COLUMN_NAME = 'currency'
)
AND `new_price` IS NOT NULL;

-- 注意：
-- 1. MySQL 5.7+ 不支持 IF NOT EXISTS，如果字段已存在会报错，可以忽略
-- 2. 如果需要兼容 MySQL 5.7，请使用下面的版本（需要手动检查）
