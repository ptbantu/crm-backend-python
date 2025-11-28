-- ============================================================
-- 创建商机表 (opportunities)
-- ============================================================
-- 用途：管理商机信息，从线索转化或直接创建
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 禁用外键检查（创建表时）
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS `opportunities` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `customer_id` char(36) NOT NULL COMMENT '客户ID',
  `lead_id` char(36) DEFAULT NULL COMMENT '来源线索ID（可选，用于追溯）',
  `name` varchar(255) NOT NULL COMMENT '商机名称',
  `amount` decimal(18,2) DEFAULT NULL COMMENT '商机金额',
  `probability` int DEFAULT NULL COMMENT '成交概率（0-100）',
  `stage` varchar(50) NOT NULL DEFAULT 'initial_contact' COMMENT '商机阶段（initial_contact, needs_analysis, proposal, negotiation, closed_won, closed_lost）',
  `status` varchar(50) NOT NULL DEFAULT 'active' COMMENT '状态（active, won, lost, cancelled）',
  `owner_user_id` char(36) DEFAULT NULL COMMENT '负责人（外键 → users.id）',
  `expected_close_date` date DEFAULT NULL COMMENT '预期成交日期',
  `actual_close_date` date DEFAULT NULL COMMENT '实际成交日期',
  `description` text COMMENT '描述',
  `organization_id` char(36) NOT NULL COMMENT '组织ID（数据隔离）',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人ID',
  `updated_by` char(36) DEFAULT NULL COMMENT '更新人ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `ix_opportunities_customer` (`customer_id`),
  KEY `ix_opportunities_lead` (`lead_id`),
  KEY `ix_opportunities_owner` (`owner_user_id`),
  KEY `ix_opportunities_organization` (`organization_id`),
  KEY `ix_opportunities_stage` (`stage`),
  KEY `ix_opportunities_status` (`status`),
  KEY `ix_opportunities_created` (`created_at` DESC),
  KEY `created_by` (`created_by`),
  KEY `updated_by` (`updated_by`),
  CONSTRAINT `opportunities_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `opportunities_ibfk_2` FOREIGN KEY (`lead_id`) REFERENCES `leads` (`id`) ON DELETE SET NULL,
  CONSTRAINT `opportunities_ibfk_3` FOREIGN KEY (`owner_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `opportunities_ibfk_4` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `opportunities_ibfk_5` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_opportunities_stage` CHECK ((`stage` in (_utf8mb4'initial_contact',_utf8mb4'needs_analysis',_utf8mb4'proposal',_utf8mb4'negotiation',_utf8mb4'closed_won',_utf8mb4'closed_lost'))),
  CONSTRAINT `chk_opportunities_status` CHECK ((`status` in (_utf8mb4'active',_utf8mb4'won',_utf8mb4'lost',_utf8mb4'cancelled'))),
  CONSTRAINT `chk_opportunities_probability` CHECK (((`probability` >= 0) and (`probability` <= 100)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='商机表';

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;

