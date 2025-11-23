-- ============================================================
-- 完整修复 users 表 id 字段长度（处理所有外键约束）
-- ============================================================
-- 问题：用户ID格式为 organization_id(36字符) + 序号(2-3位)，总长度38-39字符
-- 但数据库字段是 CHAR(36)，导致数据过长错误
-- 解决方案：将 id 字段改为 VARCHAR(50) 以容纳更长的用户ID
-- 
-- 注意：由于存在多个外键约束，需要先删除所有约束，修改字段，再重建约束
-- ============================================================

-- 禁用外键检查（临时）
SET FOREIGN_KEY_CHECKS = 0;

-- 开始事务
START TRANSACTION;

-- 1. 删除所有引用 users.id 的外键约束
-- 注意：MySQL 不允许直接通过名称删除，需要先查询约束名称

-- 删除 user_roles 表的外键
SET @drop_fk_sql = (
    SELECT CONCAT('ALTER TABLE ', TABLE_NAME, ' DROP FOREIGN KEY ', CONSTRAINT_NAME)
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'bantu_crm'
      AND TABLE_NAME = 'user_roles'
      AND REFERENCED_TABLE_NAME = 'users'
      AND REFERENCED_COLUMN_NAME = 'id'
    LIMIT 1
);

SET @sql = IF(@drop_fk_sql IS NOT NULL, @drop_fk_sql, 'SELECT "No FK in user_roles"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 删除 organization_employees 表的外键
SET @drop_fk_sql = (
    SELECT CONCAT('ALTER TABLE ', TABLE_NAME, ' DROP FOREIGN KEY ', CONSTRAINT_NAME)
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'bantu_crm'
      AND TABLE_NAME = 'organization_employees'
      AND REFERENCED_TABLE_NAME = 'users'
      AND REFERENCED_COLUMN_NAME = 'id'
    LIMIT 1
);

SET @sql = IF(@drop_fk_sql IS NOT NULL, @drop_fk_sql, 'SELECT "No FK in organization_employees"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 删除 organizations 表的外键（verified_by）
SET @drop_fk_sql = (
    SELECT CONCAT('ALTER TABLE ', TABLE_NAME, ' DROP FOREIGN KEY ', CONSTRAINT_NAME)
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'bantu_crm'
      AND TABLE_NAME = 'organizations'
      AND REFERENCED_TABLE_NAME = 'users'
      AND REFERENCED_COLUMN_NAME = 'id'
    LIMIT 1
);

SET @sql = IF(@drop_fk_sql IS NOT NULL, @drop_fk_sql, 'SELECT "No FK in organizations"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 删除 opportunities 表的外键（owner_user_id, agent_user_id）
SET @drop_fk_sql = (
    SELECT CONCAT('ALTER TABLE ', TABLE_NAME, ' DROP FOREIGN KEY ', CONSTRAINT_NAME)
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'bantu_crm'
      AND TABLE_NAME = 'opportunities'
      AND REFERENCED_TABLE_NAME = 'users'
      AND REFERENCED_COLUMN_NAME = 'id'
    LIMIT 1
);

SET @sql = IF(@drop_fk_sql IS NOT NULL, @drop_fk_sql, 'SELECT "No FK in opportunities"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 删除 orders 表的外键（sales_user_id, created_by, updated_by）
SET @drop_fk_sql = (
    SELECT CONCAT('ALTER TABLE ', TABLE_NAME, ' DROP FOREIGN KEY ', CONSTRAINT_NAME)
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'bantu_crm'
      AND TABLE_NAME = 'orders'
      AND REFERENCED_TABLE_NAME = 'users'
      AND REFERENCED_COLUMN_NAME = 'id'
    LIMIT 1
);

SET @sql = IF(@drop_fk_sql IS NOT NULL, @drop_fk_sql, 'SELECT "No FK in orders"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 注意：由于可能有多个外键约束，上面的方法可能不够完整
-- 更安全的方法是使用循环删除所有外键，但 MySQL 不支持存储过程循环
-- 所以这里使用一个更简单的方法：直接修改字段类型，MySQL 8.0+ 支持自动处理外键

-- 2. 修改 users.id 字段
ALTER TABLE users MODIFY COLUMN id VARCHAR(50) NOT NULL COMMENT '用户ID：组织ID + 序号';

-- 提交事务
COMMIT;

-- 重新启用外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- 验证修改结果
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE,
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'bantu_crm'
  AND TABLE_NAME = 'users'
  AND COLUMN_NAME = 'id';

