-- ============================================================
-- 创建商机付款阶段表 (opportunity_payment_stages)
-- ============================================================
-- 用途：管理商机的付款计划
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 禁用外键检查（创建表时）
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS `opportunity_payment_stages` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `opportunity_id` char(36) NOT NULL COMMENT '商机ID（外键 → opportunities.id）',
  `stage_number` int NOT NULL COMMENT '阶段序号（1, 2, 3...）',
  `stage_name` varchar(255) NOT NULL COMMENT '阶段名称（如：首付款、中期款、尾款）',
  `amount` decimal(18,2) NOT NULL COMMENT '应付金额',
  `due_date` date DEFAULT NULL COMMENT '到期日期',
  `payment_trigger` varchar(50) DEFAULT 'manual' COMMENT '付款触发条件（manual, milestone, date, completion）',
  `status` varchar(50) NOT NULL DEFAULT 'pending' COMMENT '状态（pending, paid, overdue, cancelled）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `ix_opportunity_payment_stages_opportunity` (`opportunity_id`),
  KEY `ix_opportunity_payment_stages_stage_number` (`opportunity_id`, `stage_number`),
  KEY `ix_opportunity_payment_stages_status` (`status`),
  KEY `ix_opportunity_payment_stages_due_date` (`due_date`),
  CONSTRAINT `opportunity_payment_stages_ibfk_1` FOREIGN KEY (`opportunity_id`) REFERENCES `opportunities` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_opportunity_payment_stages_trigger` CHECK ((`payment_trigger` in (_utf8mb4'manual',_utf8mb4'milestone',_utf8mb4'date',_utf8mb4'completion'))),
  CONSTRAINT `chk_opportunity_payment_stages_status` CHECK ((`status` in (_utf8mb4'pending',_utf8mb4'paid',_utf8mb4'overdue',_utf8mb4'cancelled'))),
  CONSTRAINT `chk_opportunity_payment_stages_stage_number` CHECK ((`stage_number` > 0)),
  CONSTRAINT `chk_opportunity_payment_stages_amount` CHECK ((`amount` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='商机付款阶段表';

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;

