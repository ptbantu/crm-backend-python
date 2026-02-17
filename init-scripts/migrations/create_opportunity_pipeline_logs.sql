-- ============================================================
-- 商机流水线日志表
-- ============================================================

CREATE TABLE IF NOT EXISTS `opportunity_pipeline_logs` (
  `id` char(36) NOT NULL DEFAULT (uuid()) COMMENT '日志ID',
  `opportunity_id` char(36) NOT NULL COMMENT '商机ID（外键 → opportunities.id）',
  `pipeline_id` char(36) NOT NULL COMMENT '流水线ID（外键 → sys_pipeline_configs.id）',
  `stage_id` char(36) NOT NULL COMMENT '阶段ID（外键 → sys_pipeline_stages.id）',
  `stage_name` varchar(100) NOT NULL COMMENT '阶段名称（冗余，便于查询）',
  `stage_type` enum('TASK','APPROVAL','DECISION','NOTIFICATION') NOT NULL COMMENT '阶段类型',
  `status` enum('PENDING','PROCESSING','COMPLETED','SKIPPED','REJECTED') NOT NULL DEFAULT 'PENDING' COMMENT '状态',
  `parallel_group` varchar(50) DEFAULT NULL COMMENT '并行组标识（冗余）',

  -- 时间字段
  `entered_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '进入阶段时间',
  `started_at` datetime DEFAULT NULL COMMENT '开始处理时间',
  `completed_at` datetime DEFAULT NULL COMMENT '完成时间',
  `duration_minutes` int DEFAULT NULL COMMENT '耗时（分钟）',

  -- 审批字段
  `assigned_to` char(36) DEFAULT NULL COMMENT '分配给（外键 → users.id）',
  `approver_id` char(36) DEFAULT NULL COMMENT '审批人ID（外键 → users.id）',
  `approved_at` datetime DEFAULT NULL COMMENT '审批时间',
  `approval_notes` text COMMENT '审批意见',

  -- 元数据
  `notes` text COMMENT '备注',
  `metadata` json DEFAULT NULL COMMENT '扩展数据（JSON格式）',

  -- 审计字段
  `created_by` char(36) DEFAULT NULL COMMENT '创建人ID',
  `updated_by` char(36) DEFAULT NULL COMMENT '更新人ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_opp_stage` (`opportunity_id`, `stage_id`),
  KEY `idx_opportunity_id` (`opportunity_id`),
  KEY `idx_pipeline_id` (`pipeline_id`),
  KEY `idx_stage_id` (`stage_id`),
  KEY `idx_status` (`status`),
  KEY `idx_parallel_group` (`parallel_group`),
  KEY `idx_assigned_to` (`assigned_to`),
  KEY `idx_approver_id` (`approver_id`),
  KEY `idx_entered_at` (`entered_at`),
  KEY `idx_opp_status_entered` (`opportunity_id`, `status`, `entered_at`),
  KEY `idx_stage_status` (`stage_id`, `status`),

  CONSTRAINT `fk_opp_pipeline_logs_opportunity` FOREIGN KEY (`opportunity_id`) REFERENCES `opportunities` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_opp_pipeline_logs_pipeline` FOREIGN KEY (`pipeline_id`) REFERENCES `sys_pipeline_configs` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_opp_pipeline_logs_stage` FOREIGN KEY (`stage_id`) REFERENCES `sys_pipeline_stages` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_opp_pipeline_logs_assigned_to` FOREIGN KEY (`assigned_to`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_opp_pipeline_logs_approver` FOREIGN KEY (`approver_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_opp_pipeline_logs_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_opp_pipeline_logs_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='商机流水线执行日志表';
