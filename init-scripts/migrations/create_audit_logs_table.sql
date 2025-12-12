-- ============================================================
-- 创建审计日志表 (audit_logs)
-- ============================================================
-- 用途：记录所有用户操作和系统事件的审计日志
-- 支持：操作追踪、合规审计、安全监控
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 禁用外键检查（创建表时）
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS `audit_logs` (
  `id` char(36) NOT NULL DEFAULT (uuid()) COMMENT '审计日志ID',
  `organization_id` char(36) NOT NULL COMMENT '组织ID（数据隔离）',
  `user_id` char(36) DEFAULT NULL COMMENT '操作用户ID',
  `user_name` varchar(255) DEFAULT NULL COMMENT '操作用户名称（冗余字段，便于查询）',
  `action` varchar(50) NOT NULL COMMENT '操作类型：CREATE, UPDATE, DELETE, VIEW, LOGIN, LOGOUT 等',
  `resource_type` varchar(50) DEFAULT NULL COMMENT '资源类型：user, organization, order, lead, customer 等',
  `resource_id` char(36) DEFAULT NULL COMMENT '资源ID',
  `resource_name` varchar(255) DEFAULT NULL COMMENT '资源名称（冗余字段，便于查询）',
  `category` varchar(50) DEFAULT NULL COMMENT '操作分类：user_management, order_management, customer_management 等',
  `ip_address` varchar(50) DEFAULT NULL COMMENT 'IP地址',
  `user_agent` varchar(500) DEFAULT NULL COMMENT '用户代理',
  `request_method` varchar(10) DEFAULT NULL COMMENT 'HTTP方法：GET, POST, PUT, DELETE 等',
  `request_path` varchar(500) DEFAULT NULL COMMENT '请求路径',
  `request_params` json DEFAULT NULL COMMENT '请求参数（JSON格式）',
  `old_values` json DEFAULT NULL COMMENT '修改前的值（JSON格式，用于 UPDATE 操作）',
  `new_values` json DEFAULT NULL COMMENT '修改后的值（JSON格式，用于 UPDATE 操作）',
  `status` varchar(20) NOT NULL DEFAULT 'success' COMMENT '操作状态：success, failed',
  `error_message` text DEFAULT NULL COMMENT '错误信息（如果操作失败）',
  `duration_ms` int DEFAULT NULL COMMENT '操作耗时（毫秒）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间（用于分区和查询）',
  PRIMARY KEY (`id`),
  KEY `ix_audit_logs_organization` (`organization_id`),
  KEY `ix_audit_logs_user` (`user_id`),
  KEY `ix_audit_logs_action` (`action`),
  KEY `ix_audit_logs_resource_type` (`resource_type`),
  KEY `ix_audit_logs_resource_id` (`resource_id`),
  KEY `ix_audit_logs_category` (`category`),
  KEY `ix_audit_logs_created_at` (`created_at` DESC),
  -- 复合索引（用于优化查询性能）
  KEY `idx_org_created` (`organization_id`, `created_at`),
  KEY `idx_user_created` (`user_id`, `created_at`),
  KEY `idx_resource_created` (`resource_type`, `resource_id`, `created_at`),
  KEY `idx_category_created` (`category`, `created_at`),
  CONSTRAINT `chk_audit_logs_status` CHECK ((`status` in (_utf8mb4'success',_utf8mb4'failed')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='审计日志表';

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- 创建分区表（可选，如果数据量很大）
-- 注意：MySQL 8.0+ 支持分区表，可以按月或按年分区
-- 示例：按月分区（需要根据实际需求调整）
-- ALTER TABLE `audit_logs` PARTITION BY RANGE (YEAR(created_at) * 100 + MONTH(created_at)) (
--   PARTITION p202401 VALUES LESS THAN (202402),
--   PARTITION p202402 VALUES LESS THAN (202403),
--   PARTITION p202403 VALUES LESS THAN (202404),
--   -- ... 更多分区
--   PARTITION p_future VALUES LESS THAN MAXVALUE
-- );
