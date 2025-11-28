-- ============================================================
-- 更新 orders 表：添加 opportunity_id 字段
-- ============================================================
-- 用途：用于追溯订单来源的商机
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 禁用外键检查（修改表时）
SET FOREIGN_KEY_CHECKS = 0;

-- 检查字段是否已存在
SET @column_exists = (
  SELECT COUNT(*) 
  FROM INFORMATION_SCHEMA.COLUMNS 
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'orders'
    AND COLUMN_NAME = 'opportunity_id'
);

-- 如果字段不存在，则添加
SET @sql = IF(
  @column_exists = 0,
  'ALTER TABLE `orders` ADD COLUMN `opportunity_id` char(36) DEFAULT NULL COMMENT ''商机ID（可选，用于追溯）'' AFTER `service_record_id`',
  'SELECT ''Column opportunity_id already exists'' AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加索引（如果字段已存在，索引可能已存在，但不会报错）
ALTER TABLE `orders` ADD INDEX `ix_orders_opportunity` (`opportunity_id`);

-- 添加外键约束（如果字段已存在，外键可能已存在，但不会报错）
-- 注意：如果外键已存在，此语句会失败，但不影响功能
SET @fk_exists = (
  SELECT COUNT(*) 
  FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'orders'
    AND CONSTRAINT_NAME = 'orders_ibfk_opportunity'
    AND COLUMN_NAME = 'opportunity_id'
);

SET @sql_fk = IF(
  @fk_exists = 0,
  'ALTER TABLE `orders` ADD CONSTRAINT `orders_ibfk_opportunity` FOREIGN KEY (`opportunity_id`) REFERENCES `opportunities` (`id`) ON DELETE SET NULL',
  'SELECT ''Foreign key already exists'' AS message'
);

PREPARE stmt_fk FROM @sql_fk;
EXECUTE stmt_fk;
DEALLOCATE PREPARE stmt_fk;

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;

