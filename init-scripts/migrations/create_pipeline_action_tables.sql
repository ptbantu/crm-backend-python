-- ============================================================
-- 流水线原子动作系统表结构
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 1. 阶段原子动作配置表
CREATE TABLE IF NOT EXISTS `sys_pipeline_action_configs` (
  `id` char(36) NOT NULL DEFAULT (uuid()) COMMENT '动作配置ID',
  `stage_id` char(36) NOT NULL COMMENT '关联阶段ID（外键 → sys_pipeline_stages.id）',
  `action_code` varchar(50) NOT NULL COMMENT '动作编码（唯一标识）',
  `name` varchar(100) NOT NULL COMMENT '动作名称',
  `action_type` enum('FORM','FILE','APPROVAL','SUB_PIPELINE','API_CALL') NOT NULL COMMENT '动作类型',
  `is_required` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否必需（强制执行）',
  `order` int NOT NULL DEFAULT 1 COMMENT '执行顺序',
  `description` text COMMENT '动作描述',

  -- 配置字段
  `validation_rules` json DEFAULT NULL COMMENT '验证规则（JSON格式）',
  `trigger_config` json DEFAULT NULL COMMENT '触发配置（用于子流水线等）',
  `form_schema` json DEFAULT NULL COMMENT '表单结构定义（用于FORM类型）',

  -- 审计字段
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_stage_action_code` (`stage_id`, `action_code`),
  KEY `idx_stage_id` (`stage_id`),
  KEY `idx_action_type` (`action_type`),

  CONSTRAINT `fk_action_config_stage` FOREIGN KEY (`stage_id`)
    REFERENCES `sys_pipeline_stages` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='流水线阶段原子动作配置表';

-- 2. 商机动作执行日志表
CREATE TABLE IF NOT EXISTS `opportunity_action_logs` (
  `id` char(36) NOT NULL DEFAULT (uuid()) COMMENT '日志ID',
  `opportunity_id` char(36) NOT NULL COMMENT '商机ID（外键 → opportunities.id）',
  `pipeline_log_id` char(36) NOT NULL COMMENT '流水线日志ID（外键 → opportunity_pipeline_logs.id）',
  `action_config_id` char(36) NOT NULL COMMENT '动作配置ID（外键 → sys_pipeline_action_configs.id）',
  `action_code` varchar(50) NOT NULL COMMENT '动作编码（冗余，便于查询）',
  `action_name` varchar(100) NOT NULL COMMENT '动作名称（冗余）',
  `action_type` varchar(50) NOT NULL COMMENT '动作类型（冗余）',

  -- 执行状态
  `status` enum('TODO','PROCESSING','DONE','SKIPPED','FAILED') NOT NULL DEFAULT 'TODO' COMMENT '执行状态',
  `operator_id` char(36) DEFAULT NULL COMMENT '操作人ID（外键 → users.id）',
  `started_at` datetime DEFAULT NULL COMMENT '开始时间',
  `finished_at` datetime DEFAULT NULL COMMENT '完成时间',
  `duration_minutes` int DEFAULT NULL COMMENT '耗时（分钟）',

  -- 数据捕获
  `captured_data` json DEFAULT NULL COMMENT '捕获的数据（文件路径、表单数据、审批意见等）',
  `error_message` text COMMENT '错误信息（失败时记录）',
  `notes` text COMMENT '备注',

  -- 审计字段
  `created_by` char(36) DEFAULT NULL COMMENT '创建人ID',
  `updated_by` char(36) DEFAULT NULL COMMENT '更新人ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_opp_action` (`opportunity_id`, `action_config_id`),
  KEY `idx_opportunity_id` (`opportunity_id`),
  KEY `idx_pipeline_log_id` (`pipeline_log_id`),
  KEY `idx_action_config_id` (`action_config_id`),
  KEY `idx_status` (`status`),
  KEY `idx_operator_id` (`operator_id`),

  CONSTRAINT `fk_action_log_opportunity` FOREIGN KEY (`opportunity_id`)
    REFERENCES `opportunities` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_action_log_pipeline_log` FOREIGN KEY (`pipeline_log_id`)
    REFERENCES `opportunity_pipeline_logs` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_action_log_action_config` FOREIGN KEY (`action_config_id`)
    REFERENCES `sys_pipeline_action_configs` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_action_log_operator` FOREIGN KEY (`operator_id`)
    REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_action_log_created_by` FOREIGN KEY (`created_by`)
    REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_action_log_updated_by` FOREIGN KEY (`updated_by`)
    REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='商机流水线动作执行日志表';

SET FOREIGN_KEY_CHECKS = 1;
