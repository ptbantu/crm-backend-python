-- ============================================================
-- 创建供应商产品财务记录表 (vendor_product_financials)
-- ============================================================
-- 用途：管理供应商产品的财务记录，用于报账
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 禁用外键检查（创建表时）
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS `vendor_product_financials` (
    `id` CHAR(36) NOT NULL PRIMARY KEY,
    `vendor_product_id` CHAR(36) NOT NULL COMMENT '供应商产品关联ID',
    `order_id` CHAR(36) NULL COMMENT '关联订单ID（如果有）（跨服务，无外键）',
    
    -- 财务信息
    `cost_amount_idr` DECIMAL(18, 2) NULL COMMENT '成本金额（IDR）',
    `cost_amount_cny` DECIMAL(18, 2) NULL COMMENT '成本金额（CNY）',
    `exchange_rate` DECIMAL(18, 9) NULL COMMENT '汇率',
    
    -- 会计信息
    `account_code` VARCHAR(100) NULL COMMENT '会计科目代码',
    `cost_center` VARCHAR(100) NULL COMMENT '成本中心',
    `expense_category` VARCHAR(100) NULL COMMENT '费用类别',
    `department` VARCHAR(100) NULL COMMENT '部门',
    
    -- 报账信息
    `invoice_number` VARCHAR(255) NULL COMMENT '发票号',
    `invoice_date` DATE NULL COMMENT '发票日期',
    `payment_status` VARCHAR(50) NOT NULL DEFAULT 'pending' COMMENT '付款状态：pending, paid, cancelled, refunded',
    `payment_id` CHAR(36) NULL COMMENT '关联付款记录ID（跨服务，无外键）',
    
    -- 审核信息
    `is_approved` BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否已审核',
    `approved_by` CHAR(36) NULL COMMENT '审核人ID',
    `approved_at` DATETIME NULL COMMENT '审核时间',
    `approval_notes` TEXT NULL COMMENT '审核备注',
    
    -- 元数据
    `notes` TEXT NULL COMMENT '备注',
    `created_by` CHAR(36) NULL COMMENT '创建人ID',
    `updated_by` CHAR(36) NULL COMMENT '更新人ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 索引
    INDEX `idx_vendor_product_id` (`vendor_product_id`),
    INDEX `idx_order_id` (`order_id`),
    INDEX `idx_invoice_number` (`invoice_number`),
    INDEX `idx_payment_status` (`payment_status`),
    INDEX `idx_payment_id` (`payment_id`),
    INDEX `idx_is_approved` (`is_approved`),
    
    -- 外键约束
    CONSTRAINT `fk_vendor_product_financials_vendor_product` FOREIGN KEY (`vendor_product_id`) 
        REFERENCES `vendor_products` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_vendor_product_financials_approved_by` FOREIGN KEY (`approved_by`) 
        REFERENCES `users` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_vendor_product_financials_created_by` FOREIGN KEY (`created_by`) 
        REFERENCES `users` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_vendor_product_financials_updated_by` FOREIGN KEY (`updated_by`) 
        REFERENCES `users` (`id`) ON DELETE SET NULL,
    
    -- 检查约束
    CONSTRAINT `chk_vendor_product_financials_amount_nonneg` 
        CHECK (COALESCE(`cost_amount_idr`,0) >= 0 AND COALESCE(`cost_amount_cny`,0) >= 0),
    CONSTRAINT `chk_vendor_product_financials_payment_status` 
        CHECK (`payment_status` IN ('pending', 'paid', 'cancelled', 'refunded'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='供应商产品财务记录表';

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;
