-- ============================================================
-- 迁移脚本：为 leads 表的 level 字段添加外键约束
-- 关联到 customer_levels 表的 code 字段
-- 同时修改 organization_id 字段允许 NULL
-- ============================================================
-- 说明：
-- 1. leads.level 字段存储客户分级代码（如：'2', '3', '4', '5', '6'）
-- 2. customer_levels.code 字段有唯一约束，可以作为外键引用
-- 3. 添加外键约束后，确保数据一致性
-- 4. organization_id 字段改为允许 NULL，支持线索与用户直接绑定
-- ============================================================

-- 步骤1: 删除 organization_id 的外键约束（如果存在）
SET @fk_org_exists = (
    SELECT COUNT(*) 
    FROM information_schema.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = DATABASE()
    AND TABLE_NAME = 'leads'
    AND CONSTRAINT_NAME = 'leads_ibfk_2'
    AND CONSTRAINT_TYPE = 'FOREIGN KEY'
);

SET @sql_drop_fk = IF(@fk_org_exists > 0,
    'ALTER TABLE `leads` DROP FOREIGN KEY `leads_ibfk_2`',
    'SELECT "外键 leads_ibfk_2 不存在，跳过删除" AS message'
);

PREPARE stmt_drop FROM @sql_drop_fk;
EXECUTE stmt_drop;
DEALLOCATE PREPARE stmt_drop;

-- 步骤2: 修改 organization_id 字段允许 NULL
ALTER TABLE `leads` MODIFY COLUMN `organization_id` VARCHAR(36) NULL;

-- 步骤3: 重新添加 organization_id 的外键约束（允许 NULL，删除时设置为 NULL）
SET @sql_add_fk_org = IF(@fk_org_exists > 0,
    'ALTER TABLE `leads` 
     ADD CONSTRAINT `leads_ibfk_2` 
     FOREIGN KEY (`organization_id`) 
     REFERENCES `organizations` (`id`) 
     ON DELETE SET NULL 
     ON UPDATE CASCADE',
    'SELECT "跳过添加外键约束" AS message'
);

PREPARE stmt_add_fk_org FROM @sql_add_fk_org;
EXECUTE stmt_add_fk_org;
DEALLOCATE PREPARE stmt_add_fk_org; 

-- 检查外键是否已存在
SET @fk_exists = (
    SELECT COUNT(*) 
    FROM information_schema.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = DATABASE()
    AND TABLE_NAME = 'leads'
    AND CONSTRAINT_NAME = 'fk_leads_customer_level'
    AND CONSTRAINT_TYPE = 'FOREIGN KEY'
);

-- 如果外键不存在，则添加
SET @sql = IF(@fk_exists = 0,
    'ALTER TABLE `leads` 
     ADD CONSTRAINT `fk_leads_customer_level` 
     FOREIGN KEY (`level`) 
     REFERENCES `customer_levels` (`code`) 
     ON DELETE SET NULL 
     ON UPDATE CASCADE',
    'SELECT "外键 fk_leads_customer_level 已存在，跳过创建" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 验证外键是否创建成功
SELECT 
    CONSTRAINT_NAME,
    TABLE_NAME,
    COLUMN_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE CONSTRAINT_SCHEMA = DATABASE()
AND TABLE_NAME = 'leads'
AND CONSTRAINT_NAME = 'fk_leads_customer_level';

