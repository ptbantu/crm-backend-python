-- 创建供应商产品价格历史表
-- 用于记录供应商产品价格的变更历史

CREATE TABLE IF NOT EXISTS `vendor_product_price_history` (
    `id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL PRIMARY KEY COMMENT '主键ID',
    `vendor_product_id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '供应商产品关联ID',
    `old_price` DECIMAL(18, 2) NULL COMMENT '旧价格',
    `new_price` DECIMAL(18, 2) NOT NULL COMMENT '新价格',
    `currency` VARCHAR(3) NOT NULL DEFAULT 'IDR' COMMENT '货币类型：IDR/CNY',
    `effective_from` DATETIME NOT NULL COMMENT '生效开始时间',
    `effective_to` DATETIME NULL COMMENT '生效结束时间（如果为NULL表示当前有效）',
    `change_reason` TEXT NULL COMMENT '变更原因',
    `changed_by` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '变更人ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_vendor_product_id` (`vendor_product_id`),
    INDEX `idx_effective_from` (`effective_from`),
    INDEX `idx_effective_to` (`effective_to`),
    CONSTRAINT `fk_vendor_product_price_history_vendor_product` 
        FOREIGN KEY (`vendor_product_id`) 
        REFERENCES `vendor_products` (`id`) 
        ON DELETE CASCADE,
    CONSTRAINT `fk_vendor_product_price_history_changed_by` 
        FOREIGN KEY (`changed_by`) 
        REFERENCES `users` (`id`) 
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='供应商产品价格历史表';
