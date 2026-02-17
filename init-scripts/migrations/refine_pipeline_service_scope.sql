-- =========================================================
-- Migration: 流水线服务范围细化
-- Purpose: 添加 service_scope 到 opportunities，
--          trigger_condition 到 sys_pipeline_action_configs，
--          创建 crm_opp_execution_summary 快照表
-- =========================================================

-- 1.1 修改 opportunities 表，增加 service_scope
ALTER TABLE `opportunities`
ADD COLUMN `service_scope` JSON DEFAULT NULL
COMMENT '商机服务范围标签，如 ["VISA","REG","SITE"]'
AFTER `service_type`;

-- 1.2 修改 sys_pipeline_action_configs，增加 trigger_condition
ALTER TABLE `sys_pipeline_action_configs`
ADD COLUMN `trigger_condition` VARCHAR(50) NOT NULL DEFAULT 'DEFAULT'
COMMENT '触发条件标签: DEFAULT=始终触发, VISA/REG/SITE=仅在 service_scope 包含该标签时触发'
AFTER `is_required`;

-- 1.3 创建 crm_opp_execution_summary 快照表
CREATE TABLE `crm_opp_execution_summary` (
  `opportunity_id`        CHAR(36)        NOT NULL COMMENT '商机ID',
  `current_stage_id`      CHAR(36)        DEFAULT NULL COMMENT '当前阶段ID（外键 → sys_pipeline_stages.id）',
  `current_stage_code`    VARCHAR(50)     DEFAULT NULL COMMENT '阶段编码，如 ST_OPP_05',
  `current_stage_name`    VARCHAR(100)    DEFAULT NULL COMMENT '阶段名称',
  `total_progress`        DECIMAL(5,2)    NOT NULL DEFAULT 0.00 COMMENT '整体进度 0-100%',
  `pending_required_count` INT            NOT NULL DEFAULT 0 COMMENT '当前阶段剩余未完成必需 Action 数',
  `total_required_count`  INT             NOT NULL DEFAULT 0 COMMENT '当前阶段必需 Action 总数',
  `health_status`         ENUM('GREEN','YELLOW','RED') NOT NULL DEFAULT 'GREEN' COMMENT '健康状态',
  `last_action_at`        DATETIME        DEFAULT NULL COMMENT '最后一次 Action 操作时间',
  `last_action_desc`      VARCHAR(255)    DEFAULT NULL COMMENT '最后一次操作摘要',
  `created_at`            DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`            DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`opportunity_id`),
  KEY `idx_health_status` (`health_status`),
  KEY `idx_current_stage` (`current_stage_id`),
  CONSTRAINT `fk_exec_summary_opp` FOREIGN KEY (`opportunity_id`)
    REFERENCES `opportunities` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_exec_summary_stage` FOREIGN KEY (`current_stage_id`)
    REFERENCES `sys_pipeline_stages` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='商机流转执行快照表（实时对齐）';
