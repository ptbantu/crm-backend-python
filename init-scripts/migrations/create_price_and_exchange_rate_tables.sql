-- ============================================================
-- 价格和汇率管理系统数据库迁移脚本
-- ============================================================
-- 用途：创建价格历史、订单价格快照、汇率历史、价格变更日志、客户等级价格等表
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 禁用外键检查（创建表时）
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 1. 创建订单价格快照表 (order_price_snapshots)
-- ============================================================
CREATE TABLE IF NOT EXISTS `order_price_snapshots` (
  `id` CHAR(36) NOT NULL PRIMARY KEY,
  `order_id` CHAR(36) NOT NULL COMMENT '订单ID（外键 → orders.id）',
  `order_item_id` CHAR(36) NULL COMMENT '订单项ID（外键 → order_items.id）',
  `product_id` CHAR(36) NOT NULL COMMENT '产品ID（外键 → products.id）',
  
  -- 价格快照信息
  `price_type` VARCHAR(50) NOT NULL COMMENT '价格类型：cost, channel, direct, list',
  `currency` VARCHAR(10) NOT NULL COMMENT '货币：IDR, CNY, USD, EUR',
  `unit_price` DECIMAL(18, 2) NOT NULL COMMENT '单价快照',
  `quantity` INTEGER NOT NULL DEFAULT 1 COMMENT '数量',
  `subtotal` DECIMAL(18, 2) NOT NULL COMMENT '小计',
  `discount_amount` DECIMAL(18, 2) NOT NULL DEFAULT 0 COMMENT '折扣金额',
  `final_amount` DECIMAL(18, 2) NOT NULL COMMENT '最终金额',
  
  -- 汇率快照
  `exchange_rate` DECIMAL(18, 9) NULL COMMENT '汇率快照',
  `base_currency` VARCHAR(10) NOT NULL COMMENT '基准货币',
  `converted_currency` VARCHAR(10) NOT NULL COMMENT '转换后货币',
  
  -- 客户等级价格快照
  `customer_level_code` VARCHAR(50) NULL COMMENT '客户等级代码',
  `customer_level_price` DECIMAL(18, 2) NULL COMMENT '客户等级价格',
  
  -- 时间戳
  `snapshot_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '快照时间',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  
  -- 索引
  INDEX `idx_order_id` (`order_id`),
  INDEX `idx_order_item_id` (`order_item_id`),
  INDEX `idx_product_id` (`product_id`),
  INDEX `idx_snapshot_at` (`snapshot_at`),
  
  -- 外键约束
  CONSTRAINT `fk_order_price_snapshots_order_id` FOREIGN KEY (`order_id`) 
    REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_order_price_snapshots_order_item_id` FOREIGN KEY (`order_item_id`) 
    REFERENCES `order_items` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_order_price_snapshots_product_id` FOREIGN KEY (`product_id`) 
    REFERENCES `products` (`id`) ON DELETE RESTRICT,
  
  -- 检查约束
  CONSTRAINT `chk_order_price_snapshots_amount_nonneg` CHECK (`unit_price` >= 0 AND `subtotal` >= 0 AND `final_amount` >= 0),
  CONSTRAINT `chk_order_price_snapshots_price_type` CHECK (`price_type` IN ('cost', 'channel', 'direct', 'list')),
  CONSTRAINT `chk_order_price_snapshots_currency` CHECK (`currency` IN ('IDR', 'CNY', 'USD', 'EUR'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='订单价格快照表';

-- ============================================================
-- 2. 创建汇率历史表 (exchange_rate_history)
-- ============================================================
CREATE TABLE IF NOT EXISTS `exchange_rate_history` (
  `id` CHAR(36) NOT NULL PRIMARY KEY,
  
  -- 汇率信息
  `from_currency` VARCHAR(10) NOT NULL COMMENT '源货币：IDR, CNY, USD, EUR',
  `to_currency` VARCHAR(10) NOT NULL COMMENT '目标货币：IDR, CNY, USD, EUR',
  `rate` DECIMAL(18, 9) NOT NULL COMMENT '汇率',
  
  -- 生效时间
  `effective_from` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '生效时间',
  `effective_to` DATETIME NULL COMMENT '失效时间（NULL表示当前有效）',
  
  -- 汇率来源和审核
  `source` VARCHAR(50) NULL COMMENT '汇率来源：manual, api, import',
  `source_reference` VARCHAR(255) NULL COMMENT '来源参考（如API提供商）',
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
  INDEX `idx_from_currency` (`from_currency`),
  INDEX `idx_to_currency` (`to_currency`),
  INDEX `idx_effective_from` (`effective_from`),
  INDEX `idx_effective_to` (`effective_to`),
  INDEX `idx_currency_pair` (`from_currency`, `to_currency`),
  
  -- 外键约束
  CONSTRAINT `fk_exchange_rate_history_approved_by` FOREIGN KEY (`approved_by`) 
    REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_exchange_rate_history_changed_by` FOREIGN KEY (`changed_by`) 
    REFERENCES `users` (`id`) ON DELETE SET NULL,
  
  -- 检查约束
  CONSTRAINT `chk_exchange_rate_history_rate_positive` CHECK (`rate` > 0),
  CONSTRAINT `chk_exchange_rate_history_currencies_different` CHECK (`from_currency` != `to_currency`),
  CONSTRAINT `chk_exchange_rate_history_from_currency` CHECK (`from_currency` IN ('IDR', 'CNY', 'USD', 'EUR')),
  CONSTRAINT `chk_exchange_rate_history_to_currency` CHECK (`to_currency` IN ('IDR', 'CNY', 'USD', 'EUR'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='汇率历史表';

-- ============================================================
-- 3. 创建价格变更日志表 (price_change_logs)
-- ============================================================
CREATE TABLE IF NOT EXISTS `price_change_logs` (
  `id` CHAR(36) NOT NULL PRIMARY KEY,
  `product_id` CHAR(36) NOT NULL COMMENT '产品ID（外键 → products.id）',
  `price_id` CHAR(36) NULL COMMENT '价格ID（外键 → product_prices.id）',
  
  -- 变更信息
  `change_type` VARCHAR(50) NOT NULL COMMENT '变更类型：create, update, delete, activate, deactivate',
  `price_type` VARCHAR(50) NOT NULL COMMENT '价格类型：cost, channel, direct, list',
  `currency` VARCHAR(10) NOT NULL COMMENT '货币：IDR, CNY, USD, EUR',
  
  -- 价格变更前后
  `old_price` DECIMAL(18, 2) NULL COMMENT '变更前价格',
  `new_price` DECIMAL(18, 2) NULL COMMENT '变更后价格',
  `price_change_amount` DECIMAL(18, 2) NULL COMMENT '价格变动金额',
  `price_change_percentage` DECIMAL(5, 2) NULL COMMENT '价格变动百分比',
  
  -- 生效时间变更
  `old_effective_from` DATETIME NULL COMMENT '变更前生效时间',
  `new_effective_from` DATETIME NULL COMMENT '变更后生效时间',
  `old_effective_to` DATETIME NULL COMMENT '变更前失效时间',
  `new_effective_to` DATETIME NULL COMMENT '变更后失效时间',
  
  -- 变更原因和操作人
  `change_reason` TEXT NULL COMMENT '变更原因',
  `changed_by` CHAR(36) NULL COMMENT '变更人ID',
  `changed_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '变更时间',
  
  -- 影响分析
  `affected_orders_count` INTEGER NULL COMMENT '受影响订单数量（预估）',
  `impact_analysis` JSON NULL COMMENT '影响分析（JSON格式）',
  
  -- 时间戳
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  
  -- 索引
  INDEX `idx_product_id` (`product_id`),
  INDEX `idx_price_id` (`price_id`),
  INDEX `idx_change_type` (`change_type`),
  INDEX `idx_price_type` (`price_type`),
  INDEX `idx_changed_at` (`changed_at`),
  INDEX `idx_changed_by` (`changed_by`),
  
  -- 外键约束
  CONSTRAINT `fk_price_change_logs_product_id` FOREIGN KEY (`product_id`) 
    REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_price_change_logs_price_id` FOREIGN KEY (`price_id`) 
    REFERENCES `product_prices` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_price_change_logs_changed_by` FOREIGN KEY (`changed_by`) 
    REFERENCES `users` (`id`) ON DELETE SET NULL,
  
  -- 检查约束
  CONSTRAINT `chk_price_change_logs_change_type` CHECK (`change_type` IN ('create', 'update', 'delete', 'activate', 'deactivate')),
  CONSTRAINT `chk_price_change_logs_price_type` CHECK (`price_type` IN ('cost', 'channel', 'direct', 'list')),
  CONSTRAINT `chk_price_change_logs_currency` CHECK (`currency` IN ('IDR', 'CNY', 'USD', 'EUR'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='价格变更日志表';

-- ============================================================
-- 4. 创建客户等级价格表 (customer_level_prices)
-- ============================================================
CREATE TABLE IF NOT EXISTS `customer_level_prices` (
  `id` CHAR(36) NOT NULL PRIMARY KEY,
  `product_id` CHAR(36) NOT NULL COMMENT '产品ID（外键 → products.id）',
  `customer_level_code` VARCHAR(50) NOT NULL COMMENT '客户等级代码（外键 → customer_levels.code）',
  
  -- 价格信息
  `currency` VARCHAR(10) NOT NULL COMMENT '货币：IDR, CNY, USD, EUR',
  `amount` DECIMAL(18, 2) NOT NULL COMMENT '价格金额',
  
  -- 生效时间
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
  INDEX `idx_customer_level_code` (`customer_level_code`),
  INDEX `idx_currency` (`currency`),
  INDEX `idx_effective_from` (`effective_from`),
  INDEX `idx_effective_to` (`effective_to`),
  INDEX `idx_product_level_currency` (`product_id`, `customer_level_code`, `currency`),
  
  -- 外键约束
  CONSTRAINT `fk_customer_level_prices_product_id` FOREIGN KEY (`product_id`) 
    REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_customer_level_prices_customer_level_code` FOREIGN KEY (`customer_level_code`) 
    REFERENCES `customer_levels` (`code`) ON DELETE RESTRICT,
  CONSTRAINT `fk_customer_level_prices_approved_by` FOREIGN KEY (`approved_by`) 
    REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_customer_level_prices_changed_by` FOREIGN KEY (`changed_by`) 
    REFERENCES `users` (`id`) ON DELETE SET NULL,
  
  -- 检查约束
  CONSTRAINT `chk_customer_level_prices_amount_nonneg` CHECK (`amount` >= 0),
  CONSTRAINT `chk_customer_level_prices_currency` CHECK (`currency` IN ('IDR', 'CNY', 'USD', 'EUR'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='客户等级价格表';

-- ============================================================
-- 5. 更新 products 表，添加价格状态控制字段
-- ============================================================
-- 检查并添加 price_status 字段
SET @dbname = DATABASE();
SET @tablename = 'products';
SET @columnname = 'price_status';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (TABLE_SCHEMA = @dbname)
      AND (TABLE_NAME = @tablename)
      AND (COLUMN_NAME = @columnname)
  ) > 0,
  'SELECT 1',
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' VARCHAR(50) NULL DEFAULT ''active'' COMMENT ''价格状态：active（生效中）, pending（待生效）, suspended（已暂停）'' AFTER `status`')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- 检查并添加 price_locked 字段
SET @columnname = 'price_locked';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (TABLE_SCHEMA = @dbname)
      AND (TABLE_NAME = @tablename)
      AND (COLUMN_NAME = @columnname)
  ) > 0,
  'SELECT 1',
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' BOOLEAN NOT NULL DEFAULT FALSE COMMENT ''价格是否锁定（锁定后不允许修改）'' AFTER `price_status`')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- 检查并添加 price_locked_by 字段
SET @columnname = 'price_locked_by';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (TABLE_SCHEMA = @dbname)
      AND (TABLE_NAME = @tablename)
      AND (COLUMN_NAME = @columnname)
  ) > 0,
  'SELECT 1',
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' CHAR(36) NULL COMMENT ''价格锁定人ID'' AFTER `price_locked`')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- 检查并添加 price_locked_at 字段
SET @columnname = 'price_locked_at';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (TABLE_SCHEMA = @dbname)
      AND (TABLE_NAME = @tablename)
      AND (COLUMN_NAME = @columnname)
  ) > 0,
  'SELECT 1',
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' DATETIME NULL COMMENT ''价格锁定时间'' AFTER `price_locked_by`')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- 添加索引（如果不存在）
SET @indexname = 'idx_products_price_status';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE
      (TABLE_SCHEMA = @dbname)
      AND (TABLE_NAME = @tablename)
      AND (INDEX_NAME = @indexname)
  ) > 0,
  'SELECT 1',
  CONCAT('CREATE INDEX ', @indexname, ' ON ', @tablename, ' (`price_status`)')
));
PREPARE createIndexIfNotExists FROM @preparedStatement;
EXECUTE createIndexIfNotExists;
DEALLOCATE PREPARE createIndexIfNotExists;

SET @indexname = 'idx_products_price_locked';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE
      (TABLE_SCHEMA = @dbname)
      AND (TABLE_NAME = @tablename)
      AND (INDEX_NAME = @indexname)
  ) > 0,
  'SELECT 1',
  CONCAT('CREATE INDEX ', @indexname, ' ON ', @tablename, ' (`price_locked`)')
));
PREPARE createIndexIfNotExists FROM @preparedStatement;
EXECUTE createIndexIfNotExists;
DEALLOCATE PREPARE createIndexIfNotExists;

-- 添加外键约束（如果不存在）
SET @constraintname = 'fk_products_price_locked_by';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE
      (TABLE_SCHEMA = @dbname)
      AND (TABLE_NAME = @tablename)
      AND (CONSTRAINT_NAME = @constraintname)
  ) > 0,
  'SELECT 1',
  CONCAT('ALTER TABLE ', @tablename, ' ADD CONSTRAINT ', @constraintname, ' FOREIGN KEY (`price_locked_by`) REFERENCES `users` (`id`) ON DELETE SET NULL')
));
PREPARE addConstraintIfNotExists FROM @preparedStatement;
EXECUTE addConstraintIfNotExists;
DEALLOCATE PREPARE addConstraintIfNotExists;

-- ============================================================
-- 6. 创建视图：当前有效价格 (v_current_product_prices)
-- ============================================================
DROP VIEW IF EXISTS `v_current_product_prices`;
CREATE VIEW `v_current_product_prices` AS
SELECT 
  pp.id,
  pp.product_id,
  pp.organization_id,
  pp.price_type,
  pp.currency,
  pp.amount,
  pp.exchange_rate,
  pp.effective_from,
  pp.effective_to,
  pp.source,
  pp.is_approved,
  pp.approved_by,
  pp.approved_at,
  pp.change_reason,
  pp.changed_by,
  pp.created_at,
  pp.updated_at,
  p.name AS product_name,
  p.code AS product_code
FROM product_prices pp
INNER JOIN products p ON pp.product_id = p.id
WHERE pp.effective_from <= NOW()
  AND (pp.effective_to IS NULL OR pp.effective_to > NOW())
  AND p.is_active = TRUE
  AND p.price_status = 'active';

-- ============================================================
-- 7. 创建视图：即将生效的价格 (v_upcoming_product_prices)
-- ============================================================
DROP VIEW IF EXISTS `v_upcoming_product_prices`;
CREATE VIEW `v_upcoming_product_prices` AS
SELECT 
  pp.id,
  pp.product_id,
  pp.organization_id,
  pp.price_type,
  pp.currency,
  pp.amount,
  pp.exchange_rate,
  pp.effective_from,
  pp.effective_to,
  pp.source,
  pp.is_approved,
  pp.approved_by,
  pp.approved_at,
  pp.change_reason,
  pp.changed_by,
  pp.created_at,
  pp.updated_at,
  p.name AS product_name,
  p.code AS product_code,
  TIMESTAMPDIFF(HOUR, NOW(), pp.effective_from) AS hours_until_effective
FROM product_prices pp
INNER JOIN products p ON pp.product_id = p.id
WHERE pp.effective_from > NOW()
  AND p.is_active = TRUE
ORDER BY pp.effective_from ASC;

-- ============================================================
-- 8. 创建视图：当前有效汇率 (v_current_exchange_rates)
-- ============================================================
DROP VIEW IF EXISTS `v_current_exchange_rates`;
CREATE VIEW `v_current_exchange_rates` AS
SELECT 
  er.id,
  er.from_currency,
  er.to_currency,
  er.rate,
  er.effective_from,
  er.effective_to,
  er.source,
  er.source_reference,
  er.is_approved,
  er.approved_by,
  er.approved_at,
  er.change_reason,
  er.changed_by,
  er.created_at,
  er.updated_at
FROM exchange_rate_history er
WHERE er.effective_from <= NOW()
  AND (er.effective_to IS NULL OR er.effective_to > NOW())
  AND er.is_approved = TRUE
ORDER BY er.from_currency, er.to_currency;

-- ============================================================
-- 9. 创建触发器：价格变更时自动记录日志
-- ============================================================
-- 删除已存在的触发器（如果存在）
DROP TRIGGER IF EXISTS `trg_product_prices_after_insert`;
DROP TRIGGER IF EXISTS `trg_product_prices_after_update`;

DELIMITER $$

CREATE TRIGGER `trg_product_prices_after_insert`
AFTER INSERT ON `product_prices`
FOR EACH ROW
BEGIN
  INSERT INTO price_change_logs (
    id, product_id, price_id, change_type, price_type, currency,
    old_price, new_price, price_change_amount,
    old_effective_from, new_effective_from,
    old_effective_to, new_effective_to,
    change_reason, changed_by, changed_at
  ) VALUES (
    UUID(), NEW.product_id, NEW.id, 'create', NEW.price_type, NEW.currency,
    NULL, NEW.amount, NULL,
    NULL, NEW.effective_from,
    NULL, NEW.effective_to,
    NEW.change_reason, NEW.changed_by, NOW()
  );
END$$

CREATE TRIGGER `trg_product_prices_after_update`
AFTER UPDATE ON `product_prices`
FOR EACH ROW
BEGIN
  DECLARE v_price_change_amount DECIMAL(18, 2);
  DECLARE v_price_change_percentage DECIMAL(5, 2);
  
  -- 计算价格变动
  IF OLD.amount != NEW.amount THEN
    SET v_price_change_amount = NEW.amount - OLD.amount;
    IF OLD.amount > 0 THEN
      SET v_price_change_percentage = (v_price_change_amount / OLD.amount) * 100;
    ELSE
      SET v_price_change_percentage = NULL;
    END IF;
  ELSE
    SET v_price_change_amount = NULL;
    SET v_price_change_percentage = NULL;
  END IF;
  
  INSERT INTO price_change_logs (
    id, product_id, price_id, change_type, price_type, currency,
    old_price, new_price, price_change_amount, price_change_percentage,
    old_effective_from, new_effective_from,
    old_effective_to, new_effective_to,
    change_reason, changed_by, changed_at
  ) VALUES (
    UUID(), NEW.product_id, NEW.id, 'update', NEW.price_type, NEW.currency,
    OLD.amount, NEW.amount, v_price_change_amount, v_price_change_percentage,
    OLD.effective_from, NEW.effective_from,
    OLD.effective_to, NEW.effective_to,
    NEW.change_reason, NEW.changed_by, NOW()
  );
END$$

DELIMITER ;

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;
