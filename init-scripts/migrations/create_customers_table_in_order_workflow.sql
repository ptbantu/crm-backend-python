-- ============================================================
-- 迁移脚本：在 order_workflow_service 数据库中创建 customers 表
-- ============================================================
-- 说明：
-- 1. 这是 service_management 中 customers 表的简化版本
-- 2. 主要用于支持外键约束和本地查询
-- 3. 数据应该通过同步机制或事件从 service_management 同步过来
-- 4. 只包含 order_workflow_service 需要的字段
-- ============================================================

-- 检查表是否已存在
SET @table_exists = (
    SELECT COUNT(*) 
    FROM information_schema.TABLES 
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'customers'
);

-- 如果表不存在，则创建
SET @sql = IF(@table_exists = 0,
    'CREATE TABLE IF NOT EXISTS `customers` (
      `id` char(36) NOT NULL COMMENT ''客户ID：与 service_management 中的 customers.id 保持一致'',
      `name` varchar(255) NOT NULL COMMENT ''客户名称'',
      `code` varchar(100) DEFAULT NULL COMMENT ''客户编码'',
      `customer_type` varchar(50) DEFAULT NULL COMMENT ''客户类型：individual(个人), organization(组织)'',
      `customer_source_type` varchar(50) DEFAULT NULL COMMENT ''客户来源类型：own(内部), agent(渠道)'',
      `parent_customer_id` char(36) DEFAULT NULL COMMENT ''父客户ID（支持层级关系）'',
      `owner_user_id` char(36) DEFAULT NULL COMMENT ''内部客户所有者ID'',
      `agent_id` char(36) DEFAULT NULL COMMENT ''渠道客户组织ID（跨服务引用）'',
      `level` varchar(50) DEFAULT NULL COMMENT ''客户等级'',
      `industry` varchar(255) DEFAULT NULL COMMENT ''行业'',
      `description` text COMMENT ''描述'',
      `tags` json DEFAULT NULL COMMENT ''标签（JSON数组）'',
      `is_locked` tinyint(1) NOT NULL DEFAULT ''0'' COMMENT ''是否锁定'',
      `last_synced_at` datetime DEFAULT NULL COMMENT ''最后同步时间（从 service_management 同步）'',
      `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT ''创建时间'',
      `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT ''更新时间'',
      PRIMARY KEY (`id`),
      UNIQUE KEY `code` (`code`),
      KEY `idx_customers_name` (`name`),
      KEY `idx_customers_type` (`customer_type`),
      KEY `idx_customers_source_type` (`customer_source_type`),
      KEY `idx_customers_parent` (`parent_customer_id`),
      KEY `idx_customers_owner` (`owner_user_id`),
      KEY `idx_customers_agent` (`agent_id`),
      KEY `idx_customers_locked` (`is_locked`),
      CONSTRAINT `fk_customers_parent` FOREIGN KEY (`parent_customer_id`) REFERENCES `customers` (`id`) ON DELETE SET NULL,
      CONSTRAINT `fk_customers_owner` FOREIGN KEY (`owner_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT=''客户表（本地引用，用于支持外键约束）''',
    'SELECT "customers 表已存在，跳过创建" AS message'
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
AND TABLE_NAME = 'customers';

-- 显示表结构
DESCRIBE `customers`;

