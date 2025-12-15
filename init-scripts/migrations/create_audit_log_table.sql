-- ============================================================
-- 操作审计日志表
-- 创建日期: 2024-12-13
-- 版本: v1.0
-- 说明: 记录所有关键操作的审计日志
-- ============================================================

-- 设置字符集
SET NAMES utf8mb4;
SET CHARACTER_SET_CLIENT = utf8mb4;
SET CHARACTER_SET_CONNECTION = utf8mb4;
SET CHARACTER_SET_RESULTS = utf8mb4;

-- ============================================================
-- 创建操作审计日志表 (operation_audit_logs)
-- ============================================================

DROP TABLE IF EXISTS `operation_audit_logs`;

CREATE TABLE `operation_audit_logs` (
  `id` CHAR(36) NOT NULL DEFAULT (UUID()),
  
  -- 操作基本信息
  `operation_type` VARCHAR(50) NOT NULL COMMENT '操作类型: CREATE, UPDATE, DELETE, VIEW, LOGIN, LOGOUT, PRICE_CHANGE, STATUS_CHANGE等',
  `entity_type` VARCHAR(100) NOT NULL COMMENT '实体类型（表名）: products, orders, customers等',
  `entity_id` CHAR(36) DEFAULT NULL COMMENT '实体ID（记录ID）',
  
  -- 操作人信息
  `user_id` CHAR(36) NOT NULL COMMENT '操作人ID',
  `username` VARCHAR(255) DEFAULT NULL COMMENT '操作人用户名（冗余字段，便于查询）',
  `organization_id` CHAR(36) DEFAULT NULL COMMENT '操作人所属组织ID',
  
  -- 操作时间
  `operated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  
  -- 数据变更
  `data_before` JSON DEFAULT NULL COMMENT '操作前的数据（JSON格式）',
  `data_after` JSON DEFAULT NULL COMMENT '操作后的数据（JSON格式）',
  `changed_fields` JSON DEFAULT NULL COMMENT '变更字段列表（JSON数组，如：["name", "price"])',
  
  -- 操作上下文
  `ip_address` VARCHAR(50) DEFAULT NULL COMMENT 'IP地址',
  `user_agent` VARCHAR(500) DEFAULT NULL COMMENT '用户代理',
  `request_path` VARCHAR(500) DEFAULT NULL COMMENT '请求路径',
  `request_method` VARCHAR(10) DEFAULT NULL COMMENT '请求方法（GET/POST/PUT/DELETE）',
  `request_params` JSON DEFAULT NULL COMMENT '请求参数（JSON格式，敏感信息需脱敏）',
  
  -- 操作结果
  `status` VARCHAR(20) NOT NULL DEFAULT 'SUCCESS' COMMENT '操作状态: SUCCESS, FAILURE',
  `error_message` TEXT DEFAULT NULL COMMENT '错误信息（如果失败）',
  `error_code` VARCHAR(50) DEFAULT NULL COMMENT '错误码',
  
  -- 其他信息
  `operation_source` VARCHAR(50) DEFAULT 'API' COMMENT '操作来源: API, ADMIN, IMPORT, BATCH等',
  `batch_id` CHAR(36) DEFAULT NULL COMMENT '批次ID（用于关联多个操作，如批量导入）',
  `duration_ms` INT DEFAULT NULL COMMENT '操作耗时（毫秒）',
  `notes` TEXT DEFAULT NULL COMMENT '备注说明',
  
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id`),
  KEY `ix_audit_operation_type` (`operation_type`),
  KEY `ix_audit_entity` (`entity_type`, `entity_id`),
  KEY `ix_audit_user` (`user_id`),
  KEY `ix_audit_organization` (`organization_id`),
  KEY `ix_audit_operated_at` (`operated_at` DESC),
  KEY `ix_audit_status` (`status`),
  KEY `ix_audit_batch` (`batch_id`),
  CONSTRAINT `fk_audit_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_audit_organization` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='操作审计日志表';

-- ============================================================
-- 完成
-- ============================================================

SELECT 'Operation audit log table created successfully!' AS message;
