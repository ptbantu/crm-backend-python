-- ============================================================
-- 用户锁定字段迁移脚本
-- 添加 is_locked 字段，用于用户锁定管理
-- False = 正常（默认）
-- True = 锁定（禁用登录）
-- ============================================================

-- 检查并添加 is_locked 字段（如果不存在）
SET @dbname = DATABASE();
SET @tablename = 'users';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (TABLE_SCHEMA = @dbname)
      AND (TABLE_NAME = @tablename)
      AND (COLUMN_NAME = 'is_locked')
  ) > 0,
  'SELECT 1',
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN is_locked BOOLEAN NOT NULL DEFAULT FALSE COMMENT ''是否锁定：False=正常（默认），True=锁定（禁用登录）'' AFTER is_active;')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- 创建索引（如果不存在）
SET @indexname = 'ix_users_locked';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND INDEX_NAME = @indexname) > 0,
  'SELECT 1',
  CONCAT('CREATE INDEX ', @indexname, ' ON ', @tablename, '(is_locked);')
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 迁移现有数据：如果 is_active=FALSE，则设置 is_locked=TRUE（保持兼容）
UPDATE users 
SET is_locked = TRUE 
WHERE is_active = FALSE AND (is_locked IS NULL OR is_locked = FALSE);

