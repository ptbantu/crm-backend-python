-- ============================================================
-- 修复 users 表 id 字段长度
-- ============================================================
-- 问题：用户ID格式为 organization_id(36字符) + 序号(2-3位)，总长度38-39字符
-- 但数据库字段是 CHAR(36)，导致数据过长错误
-- 解决方案：将 id 字段改为 VARCHAR(50) 以容纳更长的用户ID
-- ============================================================

-- 修改 users 表 id 字段长度
ALTER TABLE users MODIFY COLUMN id VARCHAR(50) NOT NULL COMMENT '用户ID：组织ID + 序号';

-- 检查修改结果
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE,
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'users'
  AND COLUMN_NAME = 'id';
