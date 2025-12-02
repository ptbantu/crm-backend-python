-- 迁移脚本：将 customers.industry 改为 customers.industry_id
-- 执行日期：2025-12-02

-- 1. 检查并创建临时列
ALTER TABLE `customers` 
ADD COLUMN `industry_id_temp` CHAR(36) DEFAULT NULL COMMENT '临时行业ID列' AFTER `industry`;

-- 2. 将现有的 industry 文本值迁移到 industries 表（如果不存在则创建）
-- 注意：这里假设 industries 表已经存在，如果不存在需要先执行 create_industries_table.sql

-- 2.1 为每个唯一的 industry 值在 industries 表中创建或查找记录
-- 使用存储过程或临时表来处理

-- 创建临时表存储唯一的 industry 值
-- 注意：MySQL 不支持 CREATE TEMPORARY TABLE IF NOT EXISTS，需要先删除
DROP TEMPORARY TABLE IF EXISTS `temp_industry_mapping`;

CREATE TEMPORARY TABLE `temp_industry_mapping` (
  `industry_name` VARCHAR(255) NOT NULL,
  `industry_id` CHAR(36) DEFAULT NULL,
  PRIMARY KEY (`industry_name`)
);

-- 插入所有唯一的 industry 值
INSERT INTO `temp_industry_mapping` (`industry_name`)
SELECT DISTINCT `industry` 
FROM `customers` 
WHERE `industry` IS NOT NULL AND `industry` != '';

-- 为每个 industry 值在 industries 表中创建记录（如果不存在）
-- 使用 LEFT JOIN 来避免子查询问题
INSERT INTO `industries` (`id`, `code`, `name_zh`, `name_id`, `sort_order`, `is_active`, `created_at`, `updated_at`)
SELECT 
  UUID() as `id`,
  CONCAT('IND_', UPPER(SUBSTRING(REPLACE(`industry_name`, ' ', '_'), 1, 50))) as `code`,
  `industry_name` as `name_zh`,
  `industry_name` as `name_id`,
  0 as `sort_order`,
  1 as `is_active`,
  NOW() as `created_at`,
  NOW() as `updated_at`
FROM `temp_industry_mapping` t
LEFT JOIN `industries` i1 ON i1.`name_zh` = t.`industry_name`
LEFT JOIN `industries` i2 ON i2.`name_id` = t.`industry_name`
WHERE i1.`id` IS NULL AND i2.`id` IS NULL;

-- 更新临时表，设置 industry_id
UPDATE `temp_industry_mapping` t
INNER JOIN `industries` i ON (i.`name_zh` = t.`industry_name` OR i.`name_id` = t.`industry_name`)
SET t.`industry_id` = i.`id`;

-- 3. 更新 customers 表的 industry_id_temp 列
UPDATE `customers` c
INNER JOIN `temp_industry_mapping` t ON c.`industry` = t.`industry_name`
SET c.`industry_id_temp` = t.`industry_id`
WHERE c.`industry` IS NOT NULL AND c.`industry` != '';

-- 4. 删除临时表
DROP TEMPORARY TABLE IF EXISTS `temp_industry_mapping`;

-- 5. 删除旧的 industry 列
ALTER TABLE `customers` DROP COLUMN `industry`;

-- 6. 重命名 industry_id_temp 为 industry_id
ALTER TABLE `customers` CHANGE COLUMN `industry_id_temp` `industry_id` CHAR(36) DEFAULT NULL COMMENT '行业ID（外键 → industries.id）';

-- 7. 添加外键约束和索引
ALTER TABLE `customers`
ADD CONSTRAINT `fk_customers_industry` 
FOREIGN KEY (`industry_id`) REFERENCES `industries` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;

-- 检查索引是否存在，如果不存在则创建
-- MySQL 5.7+ 支持 CREATE INDEX IF NOT EXISTS，但为了兼容性，先检查
SET @index_exists = (
  SELECT COUNT(*) 
  FROM INFORMATION_SCHEMA.STATISTICS 
  WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'customers' 
    AND INDEX_NAME = 'ix_customers_industry_id'
);

SET @sql = IF(@index_exists = 0,
  'CREATE INDEX `ix_customers_industry_id` ON `customers` (`industry_id`)',
  'SELECT "Index already exists"'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 完成

