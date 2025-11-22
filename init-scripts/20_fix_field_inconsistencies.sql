-- ============================================================
-- 修复代码与数据库字段不一致问题
-- ============================================================
-- 修复日期: 2025-11-22
-- 
-- 修复内容:
-- 1. organizations.is_locked 字段：改为 NOT NULL, DEFAULT FALSE
-- 2. users.email 字段：改为 NOT NULL（根据业务需求）
-- ============================================================

-- ============================================================
-- 1. 修复 organizations.is_locked 字段
-- ============================================================
-- 代码要求：nullable=False, default=False
-- 数据库当前：nullable=YES, default=NULL
-- 修复：改为 NOT NULL, DEFAULT FALSE

-- 先更新现有 NULL 值为 FALSE
UPDATE organizations 
SET is_locked = FALSE 
WHERE is_locked IS NULL;

-- 修改字段定义
ALTER TABLE organizations 
MODIFY COLUMN is_locked BOOLEAN NOT NULL DEFAULT FALSE 
COMMENT '是否锁定：False=合作（默认），True=锁定（断开合作）';

-- ============================================================
-- 2. 修复 users.email 字段
-- ============================================================
-- 代码当前：nullable=True
-- 业务需求：email 应该是必填的（用于登录）
-- 修复：改为 NOT NULL

-- 注意：如果数据库中已有 email 为 NULL 的记录，需要先处理这些记录
-- 这里假设所有用户都有 email，如果有 NULL 值，需要先更新

-- 检查是否有 email 为 NULL 的记录
-- SELECT COUNT(*) FROM users WHERE email IS NULL;

-- 如果有 NULL 值，需要先更新（这里使用临时邮箱）
-- UPDATE users SET email = CONCAT('temp_', id, '@bantu.sbs') WHERE email IS NULL;

-- 修改字段定义
ALTER TABLE users 
MODIFY COLUMN email VARCHAR(255) NOT NULL;

-- 注意：如果执行失败，说明有 email 为 NULL 的记录，需要先处理这些记录


