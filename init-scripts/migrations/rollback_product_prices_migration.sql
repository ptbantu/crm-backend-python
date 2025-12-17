-- ============================================================
-- 销售价格独立设计 - 数据迁移回滚脚本
-- ============================================================
-- 用途：回滚产品价格迁移，删除从 products 表迁移到 product_prices 表的数据
-- 警告：此脚本会删除迁移过程中创建的价格记录，请谨慎使用
-- ============================================================
-- 注意：
-- 1. 此脚本只删除标记为 'migration' 来源的价格记录
-- 2. 不会删除 products 表中的价格字段（保持向后兼容）
-- 3. 不会删除手动创建的价格记录
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 禁用外键检查
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 1. 检查迁移日志表是否存在
-- ============================================================
SET @migration_log_exists = (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = '_migration_product_prices_log'
);

-- ============================================================
-- 2. 删除迁移过程中创建的价格记录
-- ============================================================
-- 只删除 source = 'migration' 的记录
DELETE FROM `product_prices`
WHERE `source` = 'migration'
  AND `change_reason` = '从 products 表迁移';

-- 显示删除的记录数
SELECT 
    'Rollback Summary' AS report_type,
    ROW_COUNT() AS deleted_price_records,
    'Price records with source=migration have been deleted' AS note;

-- ============================================================
-- 3. 删除迁移日志表（可选）
-- ============================================================
-- 如果需要保留迁移日志，可以注释掉下面的语句
-- DROP TABLE IF EXISTS `_migration_product_prices_log`;

-- ============================================================
-- 4. 删除验证视图（如果存在）
-- ============================================================
DROP VIEW IF EXISTS `v_product_prices_comparison`;

-- ============================================================
-- 5. 恢复外键检查
-- ============================================================
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 回滚完成
-- ============================================================
SELECT 
    'Rollback completed!' AS status,
    NOW() AS completed_at,
    'Note: Products table price fields are preserved for backward compatibility.' AS note;
