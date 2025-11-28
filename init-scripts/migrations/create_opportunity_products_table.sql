-- ============================================================
-- 创建商机产品关联表 (opportunity_products)
-- ============================================================
-- 用途：管理商机关联的产品，包含执行顺序
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 禁用外键检查（创建表时）
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS `opportunity_products` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `opportunity_id` char(36) NOT NULL COMMENT '商机ID（外键 → opportunities.id）',
  `product_id` char(36) NOT NULL COMMENT '产品ID（外键 → products.id）',
  `quantity` int NOT NULL DEFAULT '1' COMMENT '数量',
  `unit_price` decimal(18,2) DEFAULT NULL COMMENT '单价',
  `total_amount` decimal(18,2) DEFAULT NULL COMMENT '总金额',
  `execution_order` int NOT NULL DEFAULT '1' COMMENT '执行顺序（1, 2, 3...）',
  `status` varchar(50) NOT NULL DEFAULT 'pending' COMMENT '状态（pending: 待执行, in_progress: 进行中, completed: 已完成, cancelled: 已取消）',
  `start_date` date DEFAULT NULL COMMENT '开始日期',
  `expected_completion_date` date DEFAULT NULL COMMENT '预期完成日期',
  `actual_completion_date` date DEFAULT NULL COMMENT '实际完成日期',
  `notes` text COMMENT '备注',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_opportunity_product` (`opportunity_id`, `product_id`),
  KEY `ix_opportunity_products_opportunity` (`opportunity_id`),
  KEY `ix_opportunity_products_product` (`product_id`),
  KEY `ix_opportunity_products_execution_order` (`opportunity_id`, `execution_order`),
  KEY `ix_opportunity_products_status` (`status`),
  CONSTRAINT `opportunity_products_ibfk_1` FOREIGN KEY (`opportunity_id`) REFERENCES `opportunities` (`id`) ON DELETE CASCADE,
  CONSTRAINT `opportunity_products_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `chk_opportunity_products_status` CHECK ((`status` in (_utf8mb4'pending',_utf8mb4'in_progress',_utf8mb4'completed',_utf8mb4'cancelled'))),
  CONSTRAINT `chk_opportunity_products_quantity` CHECK ((`quantity` > 0)),
  CONSTRAINT `chk_opportunity_products_execution_order` CHECK ((`execution_order` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='商机产品关联表';

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;

