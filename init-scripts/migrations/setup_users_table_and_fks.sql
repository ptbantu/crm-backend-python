-- ============================================================
-- 迁移脚本：设置 users 表和重新创建外键约束
-- ============================================================
-- 说明：
-- 1. 在 order_workflow_service 中创建本地 users 表（简化版本）
-- 2. 删除旧的外键约束（如果存在，指向不存在的 users 表）
-- 3. 重新创建指向本地 users 表的外键约束
-- 4. 只处理 organizations 的跨服务外键约束删除
-- ============================================================

-- 禁用外键检查
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 步骤 1: 创建本地 users 表（如果不存在）
-- ============================================================
CREATE TABLE IF NOT EXISTS `users` (
  `id` char(36) NOT NULL COMMENT '用户ID：与 foundation_service 中的 users.id 保持一致',
  `username` varchar(255) NOT NULL COMMENT '用户名',
  `email` varchar(255) DEFAULT NULL COMMENT '邮箱（用于显示）',
  `display_name` varchar(255) DEFAULT NULL COMMENT '显示名称（用于显示）',
  `phone` varchar(50) DEFAULT NULL COMMENT '电话（用于显示）',
  `is_active` tinyint(1) NOT NULL DEFAULT '1' COMMENT '是否激活',
  `is_locked` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否锁定',
  `last_synced_at` datetime DEFAULT NULL COMMENT '最后同步时间（从 foundation_service 同步）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_users_username` (`username`),
  KEY `idx_users_email` (`email`),
  KEY `idx_users_display_name` (`display_name`),
  KEY `idx_users_is_active` (`is_active`),
  KEY `idx_users_is_locked` (`is_locked`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户表（本地引用，用于支持外键约束）';

-- ============================================================
-- 步骤 2: 删除旧的外键约束（如果存在）
-- ============================================================

-- 删除 leads.owner_user_id 的旧外键约束（如果存在）
SET @fk_name = (
    SELECT CONSTRAINT_NAME
    FROM information_schema.TABLE_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = DATABASE()
    AND TABLE_NAME = 'leads'
    AND CONSTRAINT_NAME LIKE '%owner_user_id%'
    AND CONSTRAINT_TYPE = 'FOREIGN KEY'
    LIMIT 1
);

SET @sql = IF(@fk_name IS NOT NULL,
    CONCAT('ALTER TABLE `leads` DROP FOREIGN KEY `', @fk_name, '`'),
    'SELECT "外键约束不存在，跳过删除" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 删除 leads.created_by 的旧外键约束（如果存在）
SET @fk_name = (
    SELECT CONSTRAINT_NAME
    FROM information_schema.TABLE_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = DATABASE()
    AND TABLE_NAME = 'leads'
    AND CONSTRAINT_NAME LIKE '%created_by%'
    AND CONSTRAINT_TYPE = 'FOREIGN KEY'
    LIMIT 1
);

SET @sql = IF(@fk_name IS NOT NULL,
    CONCAT('ALTER TABLE `leads` DROP FOREIGN KEY `', @fk_name, '`'),
    'SELECT "外键约束不存在，跳过删除" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 删除 leads.updated_by 的旧外键约束（如果存在）
SET @fk_name = (
    SELECT CONSTRAINT_NAME
    FROM information_schema.TABLE_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = DATABASE()
    AND TABLE_NAME = 'leads'
    AND CONSTRAINT_NAME LIKE '%updated_by%'
    AND CONSTRAINT_TYPE = 'FOREIGN KEY'
    LIMIT 1
);

SET @sql = IF(@fk_name IS NOT NULL,
    CONCAT('ALTER TABLE `leads` DROP FOREIGN KEY `', @fk_name, '`'),
    'SELECT "外键约束不存在，跳过删除" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ============================================================
-- 步骤 3: 重新创建指向本地 users 表的外键约束
-- ============================================================

-- 创建 leads.owner_user_id 的外键约束
SET @fk_exists = (
    SELECT COUNT(*)
    FROM information_schema.TABLE_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = DATABASE()
    AND TABLE_NAME = 'leads'
    AND CONSTRAINT_NAME = 'fk_leads_owner_user'
    AND CONSTRAINT_TYPE = 'FOREIGN KEY'
);

SET @sql = IF(@fk_exists = 0,
    'ALTER TABLE `leads` ADD CONSTRAINT `fk_leads_owner_user` FOREIGN KEY (`owner_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL',
    'SELECT "外键约束 fk_leads_owner_user 已存在，跳过创建" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 创建 leads.created_by 的外键约束
SET @fk_exists = (
    SELECT COUNT(*)
    FROM information_schema.TABLE_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = DATABASE()
    AND TABLE_NAME = 'leads'
    AND CONSTRAINT_NAME = 'fk_leads_created_by'
    AND CONSTRAINT_TYPE = 'FOREIGN KEY'
);

SET @sql = IF(@fk_exists = 0,
    'ALTER TABLE `leads` ADD CONSTRAINT `fk_leads_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL',
    'SELECT "外键约束 fk_leads_created_by 已存在，跳过创建" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 创建 leads.updated_by 的外键约束
SET @fk_exists = (
    SELECT COUNT(*)
    FROM information_schema.TABLE_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = DATABASE()
    AND TABLE_NAME = 'leads'
    AND CONSTRAINT_NAME = 'fk_leads_updated_by'
    AND CONSTRAINT_TYPE = 'FOREIGN KEY'
);

SET @sql = IF(@fk_exists = 0,
    'ALTER TABLE `leads` ADD CONSTRAINT `fk_leads_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL',
    'SELECT "外键约束 fk_leads_updated_by 已存在，跳过创建" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ============================================================
-- 步骤 4: 确保索引存在
-- ============================================================

-- 确保 leads.owner_user_id 索引存在
SET @idx_exists = (
    SELECT COUNT(*)
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'leads'
    AND INDEX_NAME = 'owner_user_id'
);

SET @sql = IF(@idx_exists = 0,
    'CREATE INDEX `owner_user_id` ON `leads` (`owner_user_id`)',
    'SELECT "索引 owner_user_id 已存在，跳过创建" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 确保 leads.created_by 索引存在
SET @idx_exists = (
    SELECT COUNT(*)
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'leads'
    AND INDEX_NAME = 'created_by'
);

SET @sql = IF(@idx_exists = 0,
    'CREATE INDEX `created_by` ON `leads` (`created_by`)',
    'SELECT "索引 created_by 已存在，跳过创建" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 确保 leads.updated_by 索引存在
SET @idx_exists = (
    SELECT COUNT(*)
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'leads'
    AND INDEX_NAME = 'updated_by'
);

SET @sql = IF(@idx_exists = 0,
    'CREATE INDEX `updated_by` ON `leads` (`updated_by`)',
    'SELECT "索引 updated_by 已存在，跳过创建" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 重新启用外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 验证结果
-- ============================================================
SELECT 
    TABLE_NAME,
    CONSTRAINT_NAME,
    CONSTRAINT_TYPE,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE CONSTRAINT_SCHEMA = DATABASE()
AND TABLE_NAME = 'leads'
AND REFERENCED_TABLE_NAME = 'users'
ORDER BY CONSTRAINT_NAME;

