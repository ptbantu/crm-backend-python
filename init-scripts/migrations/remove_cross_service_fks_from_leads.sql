-- ============================================================
-- 迁移脚本：移除 leads 表中跨服务的外键约束
-- ============================================================
-- 说明：
-- 1. 在微服务架构中，customers 表在 service_management 服务的数据库中
-- 2. organizations 表在 foundation_service 的数据库中
-- 3. leads 表在 order_workflow_service 的数据库中
-- 4. users 表现在在 order_workflow_service 中重新定义（本地引用），可以使用外键约束
-- 5. 跨服务的外键约束（customers, organizations）会导致数据库迁移失败
-- 6. 解决方案：移除 customers 和 organizations 的外键约束，保留索引，在应用层进行数据验证
-- ============================================================

-- 禁用外键检查
SET FOREIGN_KEY_CHECKS = 0;

-- 检查并移除 leads.customer_id 的外键约束 (leads_ibfk_1)
SET @fk_exists = (
    SELECT COUNT(*) 
    FROM information_schema.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = DATABASE()
    AND TABLE_NAME = 'leads'
    AND CONSTRAINT_NAME = 'leads_ibfk_1'
    AND CONSTRAINT_TYPE = 'FOREIGN KEY'
);

SET @sql = IF(@fk_exists > 0,
    'ALTER TABLE `leads` DROP FOREIGN KEY `leads_ibfk_1`',
    'SELECT "外键约束 leads_ibfk_1 不存在，跳过删除" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 检查并移除 leads.owner_user_id 的外键约束 (leads_ibfk_3)
SET @fk_exists = (
    SELECT COUNT(*) 
    FROM information_schema.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = DATABASE()
    AND TABLE_NAME = 'leads'
    AND CONSTRAINT_NAME = 'leads_ibfk_3'
    AND CONSTRAINT_TYPE = 'FOREIGN KEY'
);

SET @sql = IF(@fk_exists > 0,
    'ALTER TABLE `leads` DROP FOREIGN KEY `leads_ibfk_3`',
    'SELECT "外键约束 leads_ibfk_3 不存在，跳过删除" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 检查并移除 leads.organization_id 的外键约束 (leads_ibfk_2)
SET @fk_exists = (
    SELECT COUNT(*) 
    FROM information_schema.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = DATABASE()
    AND TABLE_NAME = 'leads'
    AND CONSTRAINT_NAME = 'leads_ibfk_2'
    AND CONSTRAINT_TYPE = 'FOREIGN KEY'
);

SET @sql = IF(@fk_exists > 0,
    'ALTER TABLE `leads` DROP FOREIGN KEY `leads_ibfk_2`',
    'SELECT "外键约束 leads_ibfk_2 不存在，跳过删除" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 检查并移除 leads.created_by 的外键约束 (leads_ibfk_5)
SET @fk_exists = (
    SELECT COUNT(*) 
    FROM information_schema.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = DATABASE()
    AND TABLE_NAME = 'leads'
    AND CONSTRAINT_NAME = 'leads_ibfk_5'
    AND CONSTRAINT_TYPE = 'FOREIGN KEY'
);

SET @sql = IF(@fk_exists > 0,
    'ALTER TABLE `leads` DROP FOREIGN KEY `leads_ibfk_5`',
    'SELECT "外键约束 leads_ibfk_5 不存在，跳过删除" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 检查并移除 leads.updated_by 的外键约束 (leads_ibfk_6)
SET @fk_exists = (
    SELECT COUNT(*) 
    FROM information_schema.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = DATABASE()
    AND TABLE_NAME = 'leads'
    AND CONSTRAINT_NAME = 'leads_ibfk_6'
    AND CONSTRAINT_TYPE = 'FOREIGN KEY'
);

SET @sql = IF(@fk_exists > 0,
    'ALTER TABLE `leads` DROP FOREIGN KEY `leads_ibfk_6`',
    'SELECT "外键约束 leads_ibfk_6 不存在，跳过删除" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 检查并移除 lead_pools.organization_id 的外键约束 (lead_pools_ibfk_1)
SET @fk_exists = (
    SELECT COUNT(*) 
    FROM information_schema.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = DATABASE()
    AND TABLE_NAME = 'lead_pools'
    AND CONSTRAINT_NAME = 'lead_pools_ibfk_1'
    AND CONSTRAINT_TYPE = 'FOREIGN KEY'
);

SET @sql = IF(@fk_exists > 0,
    'ALTER TABLE `lead_pools` DROP FOREIGN KEY `lead_pools_ibfk_1`',
    'SELECT "外键约束 lead_pools_ibfk_1 不存在，跳过删除" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 确保索引存在（外键约束移除后，索引可能被移除，需要重新创建）
-- 检查并创建 leads.customer_id 索引（如果不存在）
SET @idx_exists = (
    SELECT COUNT(*) 
    FROM information_schema.STATISTICS 
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'leads'
    AND INDEX_NAME = 'customer_id'
);

SET @sql = IF(@idx_exists = 0,
    'CREATE INDEX `customer_id` ON `leads` (`customer_id`)',
    'SELECT "索引 customer_id 已存在，跳过创建" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 检查并创建 leads.owner_user_id 索引（如果不存在）
SET @idx_exists = (
    SELECT COUNT(*) 
    FROM information_schema.STATISTICS 
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'leads'
    AND INDEX_NAME = 'owner_user_id'
);

SET @sql = IF(@idx_exists = 0,
    'CREATE INDEX `owner_user_id` ON `leads` (`owner_user_id`)',
    'SELECT "索引已存在，跳过创建" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 检查并创建 leads.created_by 索引（如果不存在）
SET @idx_exists = (
    SELECT COUNT(*) 
    FROM information_schema.STATISTICS 
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'leads'
    AND INDEX_NAME = 'created_by'
);

SET @sql = IF(@idx_exists = 0,
    'CREATE INDEX `created_by` ON `leads` (`created_by`)',
    'SELECT "索引已存在，跳过创建" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 检查并创建 leads.updated_by 索引（如果不存在）
SET @idx_exists = (
    SELECT COUNT(*) 
    FROM information_schema.STATISTICS 
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'leads'
    AND INDEX_NAME = 'updated_by'
);

SET @sql = IF(@idx_exists = 0,
    'CREATE INDEX `updated_by` ON `leads` (`updated_by`)',
    'SELECT "索引已存在，跳过创建" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 重新启用外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- 验证结果
SELECT 
    TABLE_NAME,
    CONSTRAINT_NAME,
    CONSTRAINT_TYPE,
    REFERENCED_TABLE_NAME
FROM information_schema.TABLE_CONSTRAINTS
WHERE CONSTRAINT_SCHEMA = DATABASE()
AND TABLE_NAME IN ('leads', 'lead_pools')
AND CONSTRAINT_TYPE = 'FOREIGN KEY'
AND (
    CONSTRAINT_NAME LIKE '%customer%'
    OR CONSTRAINT_NAME LIKE '%organization%'
);

