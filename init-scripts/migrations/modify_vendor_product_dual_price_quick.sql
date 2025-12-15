-- ============================================================
-- 修改供应商产品表支持双价格（CNY和IDR）- 快速执行版本
-- ============================================================
-- 用途：直接执行 ALTER TABLE，如果字段已存在会报错但可以忽略
-- 这是最快的执行方式
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- ============================================================
-- 第一部分：修改 vendor_products 表
-- ============================================================

-- 添加 cost_price_cny 字段
-- 如果字段已存在，会报错：Duplicate column name 'cost_price_cny'，可以忽略
ALTER TABLE `vendor_products`
ADD COLUMN `cost_price_cny` DECIMAL(18, 2) NULL COMMENT '成本价（人民币）' AFTER `priority`;

-- 添加 cost_price_idr 字段
-- 如果字段已存在，会报错：Duplicate column name 'cost_price_idr'，可以忽略
ALTER TABLE `vendor_products`
ADD COLUMN `cost_price_idr` DECIMAL(18, 2) NULL COMMENT '成本价（印尼盾）' AFTER `cost_price_cny`;

-- ============================================================
-- 第二部分：修改 vendor_product_price_history 表
-- ============================================================

-- 添加 old_price_cny 字段
-- 如果字段已存在，会报错：Duplicate column name 'old_price_cny'，可以忽略
ALTER TABLE `vendor_product_price_history`
ADD COLUMN `old_price_cny` DECIMAL(18, 2) NULL COMMENT '旧价格（人民币）' AFTER `vendor_product_id`;

-- 添加 old_price_idr 字段
-- 如果字段已存在，会报错：Duplicate column name 'old_price_idr'，可以忽略
ALTER TABLE `vendor_product_price_history`
ADD COLUMN `old_price_idr` DECIMAL(18, 2) NULL COMMENT '旧价格（印尼盾）' AFTER `old_price_cny`;

-- 添加 new_price_cny 字段
-- 如果字段已存在，会报错：Duplicate column name 'new_price_cny'，可以忽略
ALTER TABLE `vendor_product_price_history`
ADD COLUMN `new_price_cny` DECIMAL(18, 2) NULL COMMENT '新价格（人民币）' AFTER `old_price_idr`;

-- 添加 new_price_idr 字段
-- 如果字段已存在，会报错：Duplicate column name 'new_price_idr'，可以忽略
ALTER TABLE `vendor_product_price_history`
ADD COLUMN `new_price_idr` DECIMAL(18, 2) NULL COMMENT '新价格（印尼盾）' AFTER `new_price_cny`;

-- ============================================================
-- 执行说明：
-- ============================================================
-- 1. 直接执行上面的 ALTER TABLE 语句
-- 2. 如果字段已存在，MySQL 会报错 "Duplicate column name"，可以安全忽略
-- 3. 如果需要在脚本中忽略错误，可以使用：
--    mysql -u user -p database < modify_vendor_product_dual_price_quick.sql 2>/dev/null
-- ============================================================
