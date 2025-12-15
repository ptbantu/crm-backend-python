-- ============================================================
-- 创建供应商产品关联表 (vendor_products)
-- ============================================================
-- 用途：管理供应商提供的产品和服务，支持多供应商、价格管理
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 禁用外键检查（创建表时）
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS `vendor_products` (
    `id` CHAR(36) NOT NULL PRIMARY KEY,
    `organization_id` CHAR(36) NOT NULL COMMENT '供应商组织ID（跨服务，无外键）',
    `product_id` CHAR(36) NOT NULL COMMENT '产品ID',
    
    -- 供应商属性
    `is_primary` BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否主要供应商',
    `priority` INT NOT NULL DEFAULT 0 COMMENT '优先级（数字越小优先级越高）',
    
    -- 成本价（多货币）
    `cost_price_idr` DECIMAL(18, 2) NULL COMMENT '成本价（IDR）',
    `cost_price_cny` DECIMAL(18, 2) NULL COMMENT '成本价（CNY）',
    `exchange_rate` DECIMAL(18, 9) DEFAULT 2000 NULL COMMENT '汇率',
    
    -- 订购限制
    `min_quantity` INT NOT NULL DEFAULT 1 COMMENT '最小订购量',
    `max_quantity` INT NULL COMMENT '最大订购量',
    `lead_time_days` INT NULL COMMENT '交货期（天数）',
    `processing_days` INT NULL COMMENT '该组织处理该服务的天数',
    
    -- 可用性管理
    `is_available` BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否可用',
    `availability_notes` TEXT NULL COMMENT '可用性说明',
    `available_from` DATETIME NULL COMMENT '可用开始时间',
    `available_to` DATETIME NULL COMMENT '可用结束时间',
    
    -- 财务相关
    `account_code` VARCHAR(100) NULL COMMENT '会计科目代码',
    `cost_center` VARCHAR(100) NULL COMMENT '成本中心',
    `expense_category` VARCHAR(100) NULL COMMENT '费用类别',
    
    -- 元数据
    `notes` TEXT NULL COMMENT '备注',
    `created_by` CHAR(36) NULL COMMENT '创建人ID',
    `updated_by` CHAR(36) NULL COMMENT '更新人ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 索引
    INDEX `idx_organization_id` (`organization_id`),
    INDEX `idx_product_id` (`product_id`),
    INDEX `idx_is_primary` (`is_primary`),
    INDEX `idx_is_available` (`is_available`),
    
    -- 外键约束
    CONSTRAINT `fk_vendor_products_product_id` FOREIGN KEY (`product_id`) 
        REFERENCES `products` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_vendor_products_created_by` FOREIGN KEY (`created_by`) 
        REFERENCES `users` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_vendor_products_updated_by` FOREIGN KEY (`updated_by`) 
        REFERENCES `users` (`id`) ON DELETE SET NULL,
    
    -- 唯一约束：同一供应商不能重复添加同一产品
    UNIQUE KEY `uk_organization_product` (`organization_id`, `product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='供应商产品关联表';

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;
