-- ============================================================
-- 创建产品价格表 (product_prices)
-- ============================================================
-- 用途：管理产品的多种价格类型（成本价、渠道价、直客价、列表价）和多货币支持
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 禁用外键检查（创建表时）
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS `product_prices` (
  `id` CHAR(36) NOT NULL PRIMARY KEY,
  `product_id` CHAR(36) NOT NULL COMMENT '产品ID（外键 → products.id）',
  `organization_id` CHAR(36) NULL COMMENT '组织ID（NULL表示通用价格，跨服务无外键）',
  
  -- 价格信息
  `price_type` VARCHAR(50) NOT NULL COMMENT '价格类型：cost, channel, direct, list',
  `currency` VARCHAR(10) NOT NULL COMMENT '货币：IDR, CNY, USD, EUR',
  `amount` DECIMAL(18, 2) NOT NULL COMMENT '价格金额',
  `exchange_rate` DECIMAL(18, 9) NULL COMMENT '汇率（用于计算）',
  
  -- 价格生效时间
  `effective_from` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '生效时间',
  `effective_to` DATETIME NULL COMMENT '失效时间（NULL表示当前有效）',
  
  -- 价格来源和审核
  `source` VARCHAR(50) NULL COMMENT '价格来源：manual, import, contract',
  `is_approved` BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否已审核',
  `approved_by` CHAR(36) NULL COMMENT '审核人ID',
  `approved_at` DATETIME NULL COMMENT '审核时间',
  
  -- 变更信息
  `change_reason` TEXT NULL COMMENT '变更原因',
  `changed_by` CHAR(36) NULL COMMENT '变更人ID',
  
  -- 时间戳
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  -- 索引
  INDEX `idx_product_id` (`product_id`),
  INDEX `idx_organization_id` (`organization_id`),
  INDEX `idx_price_type` (`price_type`),
  INDEX `idx_currency` (`currency`),
  INDEX `idx_effective_from` (`effective_from`),
  INDEX `idx_effective_to` (`effective_to`),
  
  -- 外键约束
  CONSTRAINT `fk_product_prices_product_id` FOREIGN KEY (`product_id`) 
    REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_product_prices_approved_by` FOREIGN KEY (`approved_by`) 
    REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_product_prices_changed_by` FOREIGN KEY (`changed_by`) 
    REFERENCES `users` (`id`) ON DELETE SET NULL,
  
  -- 检查约束
  CONSTRAINT `chk_product_prices_amount_nonneg` CHECK (`amount` >= 0),
  CONSTRAINT `chk_product_prices_price_type` CHECK (`price_type` IN ('cost', 'channel', 'direct', 'list')),
  CONSTRAINT `chk_product_prices_currency` CHECK (`currency` IN ('IDR', 'CNY', 'USD', 'EUR'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='产品价格表';

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;
