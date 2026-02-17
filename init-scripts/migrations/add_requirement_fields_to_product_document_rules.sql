-- ============================================================
-- 扩展 product_document_rules 表，添加资料依赖管理相关字段
-- ============================================================
-- 用途：支持多文件、ZIP文件、文件数量限制等功能
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 禁用外键检查（修改表时）
SET FOREIGN_KEY_CHECKS = 0;

-- 扩展 product_document_rules 表
-- 检查并添加字段（兼容 MySQL 5.7）
SET @dbname = DATABASE();
SET @tablename = 'product_document_rules';
SET @preparedStatement = (SELECT IF(
    (
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = @dbname
        AND TABLE_NAME = @tablename
        AND COLUMN_NAME = 'min_file_count'
    ) > 0,
    'SELECT 1',
    CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN `min_file_count` INT NOT NULL DEFAULT 1 COMMENT ''最小文件数（必填）'' AFTER `is_required`')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

SET @preparedStatement = (SELECT IF(
    (
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = @dbname
        AND TABLE_NAME = @tablename
        AND COLUMN_NAME = 'max_file_count'
    ) > 0,
    'SELECT 1',
    CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN `max_file_count` INT NULL COMMENT ''最大文件数（NULL表示不限制）'' AFTER `min_file_count`')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

SET @preparedStatement = (SELECT IF(
    (
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = @dbname
        AND TABLE_NAME = @tablename
        AND COLUMN_NAME = 'support_zip'
    ) > 0,
    'SELECT 1',
    CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN `support_zip` BOOLEAN NOT NULL DEFAULT FALSE COMMENT ''是否支持ZIP文件'' AFTER `max_file_count`')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

SET @preparedStatement = (SELECT IF(
    (
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = @dbname
        AND TABLE_NAME = @tablename
        AND COLUMN_NAME = 'zip_extract_mode'
    ) > 0,
    'SELECT 1',
    CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN `zip_extract_mode` VARCHAR(50) NULL COMMENT ''ZIP解压模式：none(不解压), extract(解压后单独校验), both(同时保留ZIP和解压文件)'' AFTER `support_zip`')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

SET @preparedStatement = (SELECT IF(
    (
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = @dbname
        AND TABLE_NAME = @tablename
        AND COLUMN_NAME = 'file_type'
    ) > 0,
    'SELECT 1',
    CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN `file_type` VARCHAR(50) NULL COMMENT ''文件类型：text, pdf, zip, image, file（兼容现有document_type）'' AFTER `zip_extract_mode`')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- 添加约束（如果不存在）
SET @preparedStatement = (SELECT IF(
    (
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
        WHERE TABLE_SCHEMA = @dbname
        AND TABLE_NAME = @tablename
        AND CONSTRAINT_NAME = 'chk_min_file_count'
    ) > 0,
    'SELECT 1',
    CONCAT('ALTER TABLE ', @tablename, ' ADD CONSTRAINT `chk_min_file_count` CHECK (`min_file_count` > 0)')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

SET @preparedStatement = (SELECT IF(
    (
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
        WHERE TABLE_SCHEMA = @dbname
        AND TABLE_NAME = @tablename
        AND CONSTRAINT_NAME = 'chk_max_file_count'
    ) > 0,
    'SELECT 1',
    CONCAT('ALTER TABLE ', @tablename, ' ADD CONSTRAINT `chk_max_file_count` CHECK (`max_file_count` IS NULL OR `max_file_count` >= `min_file_count`)')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

SET @preparedStatement = (SELECT IF(
    (
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
        WHERE TABLE_SCHEMA = @dbname
        AND TABLE_NAME = @tablename
        AND CONSTRAINT_NAME = 'chk_zip_extract_mode'
    ) > 0,
    'SELECT 1',
    CONCAT('ALTER TABLE ', @tablename, ' ADD CONSTRAINT `chk_zip_extract_mode` CHECK (`zip_extract_mode` IS NULL OR `zip_extract_mode` IN (''none'', ''extract'', ''both''))')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;
