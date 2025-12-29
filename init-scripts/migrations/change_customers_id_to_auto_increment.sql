-- ============================================================
-- 迁移脚本：将customers表的id字段改为INT AUTO_INCREMENT
-- ============================================================
-- 说明：
-- 1. 客户ID改为数据库自增的5位数字（INT类型，自动递增）
-- 2. parent_customer_id字段也需要从CHAR(36)改为INT
-- 3. 所有引用customers.id的外键字段都需要从CHAR(36)改为INT
-- 4. ⚠️  警告：如果现有数据库中有客户数据（UUID格式），需要先备份并清空相关数据！
-- 5. 此脚本会先删除所有外键约束，修改字段类型，然后重新创建外键约束
-- 创建日期: 2025-12-28
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 步骤1: 删除所有引用customers.id的外键约束
-- ============================================================

-- 删除biz_expense_records表的外键约束（如果存在）
SET @fk_exists = (SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'biz_expense_records' 
    AND CONSTRAINT_NAME = 'fk_exp_customer');
SET @sql = IF(@fk_exists > 0, 
    'ALTER TABLE `biz_expense_records` DROP FOREIGN KEY `fk_exp_customer`', 
    'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 删除customer_documents表的外键约束（如果存在）
SET @fk_exists = (SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'customer_documents' 
    AND CONSTRAINT_NAME = 'customer_documents_ibfk_1');
SET @sql = IF(@fk_exists > 0, 
    'ALTER TABLE `customer_documents` DROP FOREIGN KEY `customer_documents_ibfk_1`', 
    'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 删除service_records表的外键约束（referral_customer_id，如果存在）
SET @fk_exists = (SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'service_records' 
    AND CONSTRAINT_NAME = 'service_records_ibfk_6');
SET @sql = IF(@fk_exists > 0, 
    'ALTER TABLE `service_records` DROP FOREIGN KEY `service_records_ibfk_6`', 
    'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 删除contacts表的外键约束（如果存在）
SET @fk_exists = (SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'contacts' 
    AND CONSTRAINT_NAME = 'contacts_ibfk_1');
SET @sql = IF(@fk_exists > 0, 
    'ALTER TABLE `contacts` DROP FOREIGN KEY `contacts_ibfk_1`', 
    'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 删除customer_follow_ups表的外键约束（如果存在）
SET @fk_exists = (SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'customer_follow_ups' 
    AND CONSTRAINT_NAME = 'customer_follow_ups_ibfk_1');
SET @sql = IF(@fk_exists > 0, 
    'ALTER TABLE `customer_follow_ups` DROP FOREIGN KEY `customer_follow_ups_ibfk_1`', 
    'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 删除customer_notes表的外键约束（如果存在）
SET @fk_exists = (SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'customer_notes' 
    AND CONSTRAINT_NAME = 'customer_notes_ibfk_1');
SET @sql = IF(@fk_exists > 0, 
    'ALTER TABLE `customer_notes` DROP FOREIGN KEY `customer_notes_ibfk_1`', 
    'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 删除leads表的外键约束（如果存在）
SET @fk_exists = (SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'leads' 
    AND CONSTRAINT_NAME = 'leads_ibfk_1');
SET @sql = IF(@fk_exists > 0, 
    'ALTER TABLE `leads` DROP FOREIGN KEY `leads_ibfk_1`', 
    'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 删除opportunities表的外键约束（如果存在）
SET @fk_exists = (SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'opportunities' 
    AND CONSTRAINT_NAME = 'opportunities_ibfk_1');
SET @sql = IF(@fk_exists > 0, 
    'ALTER TABLE `opportunities` DROP FOREIGN KEY `opportunities_ibfk_1`', 
    'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 删除orders表的外键约束（如果存在）
SET @fk_exists = (SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'orders' 
    AND CONSTRAINT_NAME = 'orders_ibfk_1');
SET @sql = IF(@fk_exists > 0, 
    'ALTER TABLE `orders` DROP FOREIGN KEY `orders_ibfk_1`', 
    'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 删除service_records表的外键约束（customer_id，如果存在）
SET @fk_exists = (SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'service_records' 
    AND CONSTRAINT_NAME = 'service_records_ibfk_1');
SET @sql = IF(@fk_exists > 0, 
    'ALTER TABLE `service_records` DROP FOREIGN KEY `service_records_ibfk_1`', 
    'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 删除customers表的parent_customer_id外键约束（如果存在）
SET @fk_exists = (SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'customers' 
    AND CONSTRAINT_NAME = 'customers_ibfk_1');
SET @sql = IF(@fk_exists > 0, 
    'ALTER TABLE `customers` DROP FOREIGN KEY `customers_ibfk_1`', 
    'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ============================================================
-- 步骤2: ⚠️  清空所有相关表的数据（因为UUID无法转换为INT）
-- ============================================================
-- 注意：如果现有数据很重要，请先备份！

TRUNCATE TABLE `biz_expense_records`;
TRUNCATE TABLE `customer_documents`;
TRUNCATE TABLE `service_records`;
TRUNCATE TABLE `contacts`;
TRUNCATE TABLE `customer_follow_ups`;
TRUNCATE TABLE `customer_notes`;
TRUNCATE TABLE `leads`;
TRUNCATE TABLE `opportunities`;
TRUNCATE TABLE `orders`;
TRUNCATE TABLE `customers`;

-- ============================================================
-- 步骤3: 修改所有表的customer_id字段类型
-- ============================================================

-- 修改customers表的主键和parent_customer_id
ALTER TABLE `customers` 
    MODIFY COLUMN `id` INT NOT NULL AUTO_INCREMENT COMMENT '客户ID：数据库自增，5位数字',
    MODIFY COLUMN `parent_customer_id` INT DEFAULT NULL COMMENT '父客户ID（外键 → customers.id）';

-- 设置AUTO_INCREMENT起始值为12000
ALTER TABLE `customers` AUTO_INCREMENT = 12000;

-- 修改所有引用customers.id的外键字段
-- contacts表
ALTER TABLE `contacts` 
    MODIFY COLUMN `customer_id` INT NOT NULL COMMENT '客户ID';

-- customer_follow_ups表
ALTER TABLE `customer_follow_ups` 
    MODIFY COLUMN `customer_id` INT NOT NULL COMMENT '客户ID';

-- customer_notes表
ALTER TABLE `customer_notes` 
    MODIFY COLUMN `customer_id` INT NOT NULL COMMENT '客户ID';

-- leads表
ALTER TABLE `leads` 
    MODIFY COLUMN `customer_id` INT DEFAULT NULL COMMENT '关联客户ID（可选）';

-- opportunities表
ALTER TABLE `opportunities` 
    MODIFY COLUMN `customer_id` INT NOT NULL COMMENT '客户ID';

-- orders表
ALTER TABLE `orders` 
    MODIFY COLUMN `customer_id` INT NOT NULL COMMENT '客户ID';

-- service_records表
ALTER TABLE `service_records` 
    MODIFY COLUMN `customer_id` INT NOT NULL COMMENT '客户ID',
    MODIFY COLUMN `referral_customer_id` INT DEFAULT NULL COMMENT '推荐客户ID';

-- biz_expense_records表（如果存在）
SET @table_exists = (SELECT COUNT(*) FROM information_schema.TABLES 
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'biz_expense_records');
SET @column_exists = (SELECT COUNT(*) FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'biz_expense_records' AND COLUMN_NAME = 'customer_id');
SET @sql = IF(@table_exists > 0 AND @column_exists > 0, 
    'ALTER TABLE `biz_expense_records` MODIFY COLUMN `customer_id` INT DEFAULT NULL COMMENT ''关联客户 (销售招待常用)''', 
    'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- customer_documents表（如果存在）
SET @table_exists = (SELECT COUNT(*) FROM information_schema.TABLES 
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'customer_documents');
SET @column_exists = (SELECT COUNT(*) FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'customer_documents' AND COLUMN_NAME = 'customer_id');
SET @sql = IF(@table_exists > 0 AND @column_exists > 0, 
    'ALTER TABLE `customer_documents` MODIFY COLUMN `customer_id` INT NOT NULL COMMENT ''客户ID''', 
    'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ============================================================
-- 步骤4: 重新创建外键约束
-- ============================================================

-- 重新创建customers表的parent_customer_id外键约束
ALTER TABLE `customers` 
    ADD CONSTRAINT `customers_ibfk_1` 
    FOREIGN KEY (`parent_customer_id`) REFERENCES `customers` (`id`) ON DELETE SET NULL;

-- 重新创建contacts表的外键约束
ALTER TABLE `contacts` 
    ADD CONSTRAINT `contacts_ibfk_1` 
    FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE CASCADE;

-- 重新创建customer_follow_ups表的外键约束
ALTER TABLE `customer_follow_ups` 
    ADD CONSTRAINT `customer_follow_ups_ibfk_1` 
    FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE CASCADE;

-- 重新创建customer_notes表的外键约束
ALTER TABLE `customer_notes` 
    ADD CONSTRAINT `customer_notes_ibfk_1` 
    FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE CASCADE;

-- 重新创建leads表的外键约束
ALTER TABLE `leads` 
    ADD CONSTRAINT `leads_ibfk_1` 
    FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE SET NULL;

-- 重新创建opportunities表的外键约束
ALTER TABLE `opportunities` 
    ADD CONSTRAINT `opportunities_ibfk_1` 
    FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE RESTRICT;

-- 重新创建orders表的外键约束
ALTER TABLE `orders` 
    ADD CONSTRAINT `orders_ibfk_1` 
    FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE RESTRICT;

-- 重新创建service_records表的外键约束
ALTER TABLE `service_records` 
    ADD CONSTRAINT `service_records_ibfk_1` 
    FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE CASCADE;

-- 重新创建service_records表的referral_customer_id外键约束
ALTER TABLE `service_records` 
    ADD CONSTRAINT `service_records_ibfk_6` 
    FOREIGN KEY (`referral_customer_id`) REFERENCES `customers` (`id`) ON DELETE SET NULL;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 验证修改结果
-- ============================================================
SELECT 
    COLUMN_NAME,
    COLUMN_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    EXTRA,
    COLUMN_COMMENT
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'customers'
AND COLUMN_NAME IN ('id', 'parent_customer_id')
ORDER BY COLUMN_NAME;
