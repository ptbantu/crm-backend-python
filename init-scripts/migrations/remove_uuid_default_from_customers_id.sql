-- ============================================================
-- 迁移脚本：移除customers表id字段的DEFAULT (uuid())
-- ============================================================
-- 说明：
-- 1. 客户ID现在由应用层的ID生成器生成，格式为CUS{YYYYMMDD}{00001-99999}
-- 2. 移除数据库层的UUID默认值，确保ID完全由应用层控制
-- 3. 此迁移脚本用于更新现有数据库结构
-- 创建日期: 2025-12-28
-- ============================================================

SET NAMES utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
SET FOREIGN_KEY_CHECKS = 0;

-- 检查customers表是否存在
SET @table_exists = (
    SELECT COUNT(*) 
    FROM information_schema.TABLES 
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'customers'
);

-- 如果表存在，则修改id字段，移除DEFAULT (uuid())
SET @sql = IF(@table_exists > 0,
    'ALTER TABLE `customers` 
     MODIFY COLUMN `id` CHAR(36) NOT NULL COMMENT ''客户ID：由ID生成器生成，格式为CUS{YYYYMMDD}{00001-99999}''',
    'SELECT ''customers表不存在，跳过迁移'' AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET FOREIGN_KEY_CHECKS = 1;

-- 验证修改结果
SELECT 
    COLUMN_NAME,
    COLUMN_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    COLUMN_COMMENT
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'customers'
AND COLUMN_NAME = 'id';
