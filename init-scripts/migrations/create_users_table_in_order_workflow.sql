-- ============================================================
-- 迁移脚本：在 order_workflow_service 数据库中创建 users 表
-- ============================================================
-- 说明：
-- 1. 这是 foundation_service 中 users 表的简化版本
-- 2. 主要用于支持外键约束和本地查询
-- 3. 数据应该通过同步机制或事件从 foundation_service 同步过来
-- 4. 只包含 order_workflow_service 需要的字段
-- ============================================================

-- 检查表是否已存在
SET @table_exists = (
    SELECT COUNT(*) 
    FROM information_schema.TABLES 
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'users'
);

-- 如果表不存在，则创建
SET @sql = IF(@table_exists = 0,
    'CREATE TABLE IF NOT EXISTS `users` (
      `id` char(36) NOT NULL COMMENT ''用户ID：与 foundation_service 中的 users.id 保持一致'',
      `username` varchar(255) NOT NULL COMMENT ''用户名'',
      `email` varchar(255) DEFAULT NULL COMMENT ''邮箱（用于显示）'',
      `display_name` varchar(255) DEFAULT NULL COMMENT ''显示名称（用于显示）'',
      `phone` varchar(50) DEFAULT NULL COMMENT ''电话（用于显示）'',
      `is_active` tinyint(1) NOT NULL DEFAULT ''1'' COMMENT ''是否激活'',
      `is_locked` tinyint(1) NOT NULL DEFAULT ''0'' COMMENT ''是否锁定'',
      `last_synced_at` datetime DEFAULT NULL COMMENT ''最后同步时间（从 foundation_service 同步）'',
      `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT ''创建时间'',
      `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT ''更新时间'',
      PRIMARY KEY (`id`),
      KEY `idx_users_username` (`username`),
      KEY `idx_users_email` (`email`),
      KEY `idx_users_display_name` (`display_name`),
      KEY `idx_users_is_active` (`is_active`),
      KEY `idx_users_is_locked` (`is_locked`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT=''用户表（本地引用，用于支持外键约束）''',
    'SELECT "users 表已存在，跳过创建" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 验证表是否创建成功
SELECT 
    TABLE_NAME,
    TABLE_COMMENT,
    TABLE_ROWS
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'users';

-- 显示表结构
DESCRIBE `users`;

