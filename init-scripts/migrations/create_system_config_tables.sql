-- ============================================================
-- 系统配置管理表
-- 创建日期: 2024-12-20
-- 版本: v1.0
-- 说明: 创建系统配置表和配置历史表
-- ============================================================

-- 设置字符集
SET NAMES utf8mb4;
SET CHARACTER_SET_CLIENT = utf8mb4;
SET CHARACTER_SET_CONNECTION = utf8mb4;
SET CHARACTER_SET_RESULTS = utf8mb4;

-- ============================================================
-- 创建系统配置表 (system_config)
-- ============================================================

DROP TABLE IF EXISTS `system_config`;

CREATE TABLE `system_config` (
  `id` CHAR(36) NOT NULL DEFAULT (UUID()),
  
  -- 配置基本信息
  `config_key` VARCHAR(100) NOT NULL COMMENT '配置键（唯一索引）',
  `config_value` JSON NOT NULL COMMENT '配置值（JSON格式）',
  `config_type` VARCHAR(50) NOT NULL COMMENT '配置类型: oss/ai/sms/email/system',
  `description` VARCHAR(500) DEFAULT NULL COMMENT '配置描述',
  `is_enabled` BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否启用',
  
  -- 审计字段
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_by` CHAR(36) DEFAULT NULL COMMENT '创建人ID',
  `updated_by` CHAR(36) DEFAULT NULL COMMENT '更新人ID',
  
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_config_key` (`config_key`),
  KEY `ix_config_type` (`config_type`),
  KEY `ix_config_enabled` (`is_enabled`),
  CONSTRAINT `fk_config_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_config_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='系统配置表';

-- ============================================================
-- 创建系统配置历史表 (system_config_history)
-- ============================================================

DROP TABLE IF EXISTS `system_config_history`;

CREATE TABLE `system_config_history` (
  `id` CHAR(36) NOT NULL DEFAULT (UUID()),
  
  -- 关联配置
  `config_id` CHAR(36) NOT NULL COMMENT '配置ID',
  
  -- 变更信息
  `old_value` JSON DEFAULT NULL COMMENT '旧值（JSON格式）',
  `new_value` JSON NOT NULL COMMENT '新值（JSON格式）',
  `changed_by` CHAR(36) NOT NULL COMMENT '变更人ID',
  `changed_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '变更时间',
  `change_reason` VARCHAR(500) DEFAULT NULL COMMENT '变更原因',
  
  PRIMARY KEY (`id`),
  KEY `ix_history_config_id` (`config_id`),
  KEY `ix_history_changed_at` (`changed_at` DESC),
  KEY `ix_history_changed_by` (`changed_by`),
  CONSTRAINT `fk_history_config` FOREIGN KEY (`config_id`) REFERENCES `system_config` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_history_changed_by` FOREIGN KEY (`changed_by`) REFERENCES `users` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='系统配置历史表';

-- ============================================================
-- 完成
-- ============================================================

SELECT 'System config tables created successfully!' AS message;
