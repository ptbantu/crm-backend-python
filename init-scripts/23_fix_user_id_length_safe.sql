-- ============================================================
-- 安全修复 users 表 id 字段长度（处理外键约束）
-- ============================================================
-- 问题：用户ID格式为 organization_id(36字符) + 序号(2-3位)，总长度38-39字符
-- 但数据库字段是 CHAR(36)，导致数据过长错误
-- 解决方案：将 id 字段改为 VARCHAR(50) 以容纳更长的用户ID
-- 
-- 注意：由于存在外键约束，需要先删除约束，修改字段，再重建约束
-- ============================================================

-- 禁用外键检查（临时）
SET FOREIGN_KEY_CHECKS = 0;

-- 开始事务
START TRANSACTION;

-- 1. 删除所有引用 users.id 的外键约束
-- 查找并删除 user_roles 表的外键
SET @fk_user_roles = (
    SELECT CONSTRAINT_NAME 
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
    WHERE TABLE_SCHEMA = 'bantu_crm' 
      AND TABLE_NAME = 'user_roles' 
      AND REFERENCED_TABLE_NAME = 'users' 
      AND REFERENCED_COLUMN_NAME = 'id'
    LIMIT 1
);

SET @sql = IF(@fk_user_roles IS NOT NULL, 
    CONCAT('ALTER TABLE user_roles DROP FOREIGN KEY ', @fk_user_roles), 
    'SELECT "No foreign key found in user_roles"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 查找并删除 organization_employees 表的外键（如果存在）
SET @fk_org_employees = (
    SELECT CONSTRAINT_NAME 
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
    WHERE TABLE_SCHEMA = 'bantu_crm' 
      AND TABLE_NAME = 'organization_employees' 
      AND REFERENCED_TABLE_NAME = 'users' 
      AND REFERENCED_COLUMN_NAME = 'id'
    LIMIT 1
);

SET @sql = IF(@fk_org_employees IS NOT NULL, 
    CONCAT('ALTER TABLE organization_employees DROP FOREIGN KEY ', @fk_org_employees), 
    'SELECT "No foreign key found in organization_employees"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 查找并删除其他可能引用 users.id 的外键
-- 注意：这里需要根据实际的外键约束名称进行调整

-- 2. 修改 users.id 字段
ALTER TABLE users MODIFY COLUMN id VARCHAR(50) NOT NULL COMMENT '用户ID：组织ID + 序号';

-- 3. 重新创建外键约束
-- 重新创建 user_roles 表的外键（如果之前存在）
-- 注意：这里假设外键约束的名称和定义，需要根据实际情况调整
-- ALTER TABLE user_roles 
-- ADD CONSTRAINT user_roles_ibfk_1 
-- FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

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

